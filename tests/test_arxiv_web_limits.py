"""Offline acceptance: failures, circuit, budgets and concurrent task dispatch."""
import asyncio
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest

from novelty_agent_framework.core.runtime_artifacts import RuntimeArtifactManager, RuntimeDebugConfig
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.schemas import DatabaseSearchArguments, TaskResearchRequest
from novelty_agent_framework.tools.database_search import DatabaseSearchTool, RetrievalSource, StructuredSourceRetrievalTool
from novelty_agent_framework.tools.database_search.providers.arxiv import ArxivQueryAdapter
from novelty_agent_framework.tools.database_search.providers import arxiv_web as web
from test_structured_retrieval_tool import request


@pytest.fixture(autouse=True)
def isolated_gate():
    web.reset_shared_arxiv_web_gate()
    yield
    web.reset_shared_arxiv_web_gate()


def session(handler, **options):
    return web.ArxivWebSession(client=httpx.Client(transport=httpx.MockTransport(handler)),
        **{"min_interval": 0, "max_retries": 0, **options})


def database(handler, tmp_path):
    transport = session(handler)
    store = ReferenceStore(tmp_path)
    retrieval = StructuredSourceRetrievalTool(source=RetrievalSource(
        source_id="arxiv", query_adapter=ArxivQueryAdapter(),
        search_tool=web.ArxivWebSearchTool(session=transport)), reference_store=store, full_text_limit=0)
    return DatabaseSearchTool({"arxiv": retrieval}, store), transport


def invoke(tool):
    req = request(source_id="arxiv")
    scope = TaskResearchRequest(**req.model_dump(exclude={"source_id"}))
    return asyncio.run(tool.ainvoke(DatabaseSearchArguments(source_id="arxiv"), scope=scope))


def test_web_http_200_zero_hits_is_success(tmp_path):
    tool, transport = database(lambda r: httpx.Response(200, text="No results"), tmp_path)
    result = invoke(tool)
    assert result.succeeded
    assert tool.project_model_context(result)["retrieval_status"] == "ZERO_RESULT"
    assert transport.stats()["requests"] >= 2  # zero hit continues fallback
    assert all(e["status"] == "succeeded" for e in result.payload["search_executions"])


@pytest.mark.parametrize("status", [403, 429, 503], ids=["403", "429", "503"])
def test_web_http_is_failed(status, tmp_path):
    tool, transport = database(lambda r: httpx.Response(status), tmp_path)
    result = invoke(tool)
    assert not result.succeeded
    assert tool.project_model_context(result)["retrieval_status"] == "PROVIDER_FAILED"
    assert result.payload["execution_summary"]["provider_failed"]
    assert len(result.payload["search_executions"]) == transport.stats()["requests"] == 1
    assert str(status) in result.payload["search_executions"][0]["error"]


@pytest.mark.parametrize("error", [httpx.ReadTimeout, httpx.ConnectError])
def test_web_timeout_or_connection_is_failed(error, tmp_path):
    def handler(req):
        raise error("offline failure", request=req)
    tool, transport = database(handler, tmp_path)
    result = invoke(tool)
    assert not result.succeeded
    assert transport.stats()["requests"] == 1
    assert error.__name__ in result.payload["search_executions"][0]["error"]


def test_structured_retrieval_does_not_treat_provider_failure_as_empty(tmp_path):
    tool, transport = database(lambda r: httpx.Response(503), tmp_path)
    manager = RuntimeArtifactManager("web-failure", config=RuntimeDebugConfig(
        output_root=tmp_path / "runtime", archive_root=tmp_path / "archive"), diagnostics=())
    with manager:
        handle = manager.start_tool_call("database_search", agent_arguments={}, resolved_arguments={})
        result = invoke(tool)
        projected = tool.project_model_context(result)
        manager.finish_tool_call(handle, raw_result=result.model_dump(), normalized_result=projected, succeeded=result.succeeded)
    summary_path, _ = manager.finish_run("FAILED")
    summary = json.loads(summary_path.read_text())
    assert summary["provider_requests"]["physical_web_requests"] == 1
    assert summary["provider_requests"]["physical_api_requests"] == 0
    record = json.loads(next((manager.run_dir / "tools").glob("*.json")).read_text())
    assert record["business_status"] == "PROVIDER_FAILED"
    assert record["execution_status"] == "FAILED"
    assert transport.stats()["events"][-1]["task_id"] == "T-1"


@pytest.mark.parametrize("probe_status", [200, 503])
def test_circuit_open_cooldown_single_probe(probe_status):
    codes = iter([503, probe_status])
    transport = session(lambda r: httpx.Response(next(codes)), max_consecutive_failures=1,
                        circuit_cooldown_seconds=0.03)
    with pytest.raises(web.ArxivWebChannelError):
        transport.get(web.ARXIV_WEB_SEARCH_URL)
    with pytest.raises(web.ArxivWebCircuitOpenError):
        transport.get(web.ARXIV_WEB_SEARCH_URL)
    assert transport.stats()["requests"] == 1
    # Isolate circuit cooldown from local backoff in this state-machine test.
    transport._gate.blocked_until = 0
    time.sleep(0.04)
    transport._max_retries = 3
    if probe_status == 200:
        transport.get(web.ARXIV_WEB_SEARCH_URL)
        assert transport.stats()["circuit_state"] == "CLOSED"
    else:
        with pytest.raises(web.ArxivWebChannelError):
            transport.get(web.ARXIV_WEB_SEARCH_URL)
        assert transport.stats()["circuit_state"] == "OPEN"
    assert transport.stats()["requests"] == 2


def test_retry_after_is_honored_without_exceeding_budget():
    transport = session(lambda r: httpx.Response(429, headers={"Retry-After": "120"}),
                        max_retries=5, retry_budget_seconds=0.2, max_consecutive_failures=1)
    started = time.monotonic()
    with pytest.raises(web.ArxivWebRetryBudgetExceeded):
        transport.get(web.ARXIV_WEB_SEARCH_URL)
    assert time.monotonic() - started < 0.2
    assert transport.stats()["requests"] == 1
    assert transport._gate.blocked_until > started + 119
    assert transport.stats()["circuit_state"] == "OPEN"


@pytest.mark.parametrize("status", [429, 503])
def test_retry_after_zero_takes_priority_over_backoff(status):
    codes = iter([status, 200])
    transport = session(lambda r: httpx.Response(next(codes), headers={"Retry-After": "0"}), max_retries=1)
    transport.get(web.ARXIV_WEB_SEARCH_URL)
    assert transport.stats()["retry_count"] == 1
    assert transport.stats()["events"][1]["backoff_ms"] == 0


def test_four_concurrent_research_tasks_share_dispatch_gate(tmp_path):
    # Independent provider instances must still share process-wide state.
    from novelty_agent_framework.tools.database_search.providers.arxiv_scheduler import provider_task_id
    barrier = threading.Barrier(4)
    dispatches = []
    def handler(req):
        dispatches.append(time.monotonic())
        return httpx.Response(200, text="No results")
    transports = [session(handler, min_interval=0.03) for _ in range(4)]
    starts = []
    def run(i):
        token = provider_task_id.set(f"T-{i}")
        try:
            starts.append(time.monotonic())
            barrier.wait(timeout=2)
            return transports[i].get(web.ARXIV_WEB_SEARCH_URL)
        finally:
            provider_task_id.reset(token)
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert all(r.status_code == 200 for r in pool.map(run, range(4)))
    assert max(starts) - min(starts) < 0.1
    assert all(b - a >= 0.029 for a, b in zip(dispatches, dispatches[1:]))
    physical = [e for t in transports for e in t.stats()["events"] if e["event_type"] == "physical_request"]
    assert {e["task_id"] for e in physical} == {"T-0", "T-1", "T-2", "T-3"}
    assert all(not e["interval_violation"] for e in physical)


def test_retry_limit_and_timeout_budget():
    calls = []
    def handler(req):
        calls.append(req.extensions["timeout"]["read"])
        raise httpx.ReadTimeout("timeout", request=req)
    transport = session(handler, max_retries=2, max_retry_delay=0, retry_budget_seconds=0.5)
    with pytest.raises(web.ArxivWebChannelError):
        transport.get(web.ARXIV_WEB_SEARCH_URL)
    assert len(calls) == 3
    assert all(0 < value <= 0.5 for value in calls)
    assert transport.stats()["timeout_count"] == 3


def test_circuit_failure_is_shared_between_independent_sessions():
    calls = []
    def handler(req):
        calls.append(req)
        return httpx.Response(403)
    first = session(handler, max_consecutive_failures=1)
    second = session(handler)
    with pytest.raises(web.ArxivWebChannelError):
        first.get(web.ARXIV_WEB_SEARCH_URL)
    with pytest.raises(web.ArxivWebCircuitOpenError):
        second.get(web.ARXIV_WEB_SEARCH_URL)
    assert len(calls) == 1


def test_fulltext_uses_same_web_gate():
    from novelty_agent_framework.tools.database_search.providers.arxiv import ArxivFullTextTool
    transport = session(lambda req: httpx.Response(200, text='<p>Readable body</p>'), min_interval=0.02)
    transport.get(web.ARXIV_WEB_SEARCH_URL)
    assert ArxivFullTextTool(client=transport).fetch('1706.03762') is not None
    physical = [e for e in transport.stats()['events'] if e['event_type'] == 'physical_request']
    assert [e['operation'] for e in physical] == ['search', 'full_text']
    assert physical[1]['previous_request_interval_ms'] >= 19


def test_web_circuit_half_open_serializes_concurrent_probes():
    calls = []
    started = threading.Event()
    release = threading.Event()
    def handler(req):
        calls.append(req)
        if len(calls) == 1:
            return httpx.Response(403)
        started.set()
        assert release.wait(timeout=2)
        return httpx.Response(200)
    transport = session(handler, max_consecutive_failures=1, circuit_cooldown_seconds=0)
    with pytest.raises(web.ArxivWebChannelError):
        transport.get(web.ARXIV_WEB_SEARCH_URL)
    with ThreadPoolExecutor(max_workers=2) as pool:
        probe = pool.submit(transport.get, web.ARXIV_WEB_SEARCH_URL)
        assert started.wait(timeout=2)
        other = pool.submit(transport.get, web.ARXIV_WEB_SEARCH_URL)
        assert len(calls) == 2
        assert transport.stats()['circuit_state'] == 'HALF_OPEN'
        release.set()
        assert probe.result().status_code == other.result().status_code == 200
    assert transport.stats()['circuit_state'] == 'CLOSED'


def test_redirect_hops_use_gate_and_one_logical_budget():
    def handler(req):
        if req.url.path == '/html/1706.03762':
            return httpx.Response(302, headers={'Location': '/html/1706.03762v7'})
        return httpx.Response(200, text='<p>body</p>')
    transport = session(handler, min_interval=0.02)
    assert transport.get('https://arxiv.org/html/1706.03762').status_code == 200
    stats = transport.stats()
    assert stats['logical_web_requests'] == 1
    assert stats['physical_web_requests'] == 2
    assert stats['retry_count'] == 0
    assert stats['interval_violation_count'] == 0
    assert stats['events'][-1]['previous_request_interval_ms'] >= 19
