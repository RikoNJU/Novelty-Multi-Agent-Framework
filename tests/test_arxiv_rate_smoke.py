from __future__ import annotations

import httpx
import pytest

from novelty_agent_framework.experiments.arxiv_rate_smoke import (
    DEFAULT_CASES,
    run_smoke,
)
from novelty_agent_framework.tools.database_search.providers import arxiv as arxiv_module
from novelty_agent_framework.tools.database_search.providers.arxiv import ArxivSearchTool


@pytest.fixture(autouse=True)
def _reset_scheduler():
    arxiv_module.reset_shared_arxiv_scheduler()
    yield
    arxiv_module.reset_shared_arxiv_scheduler()


def _feed(*, with_entry: bool = True) -> str:
    entry = """
      <entry>
        <id>http://arxiv.org/abs/1706.03762v7</id>
        <title>Attention Is All You Need</title>
        <summary>Transformer architecture.</summary>
        <published>2017-06-12T00:00:00Z</published>
        <author><name>Ashish Vaswani</name></author>
      </entry>
    """ if with_entry else ""
    return f'<feed xmlns="http://www.w3.org/2005/Atom">{entry}</feed>'


def test_smoke_measures_c_empty_only_after_a_and_b_pass(monkeypatch):
    monkeypatch.setattr(arxiv_module, "_LAST_REQUEST_AT", 0.0)
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, text=_feed(with_entry=calls < 3))

    tool = ArxivSearchTool(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        min_interval=0.0,
    )
    result = run_smoke(tool=tool)

    assert [item["classification"] for item in result["cases"]] == [
        "VALID_HIT",
        "VALID_HIT",
        "VALID_EMPTY",
    ]
    assert result["provider_access"] == "PASS"
    assert result["structured_query_recall"] == "EMPTY"
    assert result["query_layer_decision_allowed"] is True


def test_case_a_uses_id_list_instead_of_search_query(monkeypatch):
    monkeypatch.setattr(arxiv_module, "_LAST_REQUEST_AT", 0.0)
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, text=_feed())

    tool = ArxivSearchTool(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        min_interval=0.0,
    )
    result = run_smoke(tool=tool)

    first = requests[0]
    assert first.url.params["id_list"] == "1706.03762"
    assert first.url.params["max_results"] == "1"
    assert "start" not in first.url.params
    assert "search_query" not in first.url.params
    assert result["cases"][0]["request_parameter"] == "id_list"


def test_smoke_stops_after_provider_access_failure(monkeypatch):
    monkeypatch.setattr(arxiv_module, "_LAST_REQUEST_AT", 0.0)
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(429)

    tool = ArxivSearchTool(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        min_interval=0.0,
        max_retries=0,
        circuit_failure_threshold=10,
    )
    result = run_smoke(tool=tool)

    assert calls == 1
    assert result["cases"][0]["classification"] == "HTTP_NON_200"
    assert result["cases"][1]["classification"] == "SKIPPED_UPSTREAM_GATE"
    assert result["cases"][2]["classification"] == "SKIPPED_UPSTREAM_GATE"
    assert result["provider_access"] == "FAIL"
    assert result["structured_query_recall"] == "NOT_MEASURED"
    assert result["query_layer_decision_allowed"] is False


def test_smoke_reports_atom_parse_failure_and_stops(monkeypatch):
    monkeypatch.setattr(arxiv_module, "_LAST_REQUEST_AT", 0.0)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not xml")

    tool = ArxivSearchTool(
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        min_interval=0.0,
    )
    result = run_smoke(tool=tool)

    first = result["cases"][0]
    assert first["http_200"] is True
    assert first["atom_parsed"] is False
    assert first["classification"] == "ATOM_PARSE_FAILURE"
    assert result["provider_access"] == "FAIL"
    assert tuple(item["query"] for item in result["cases"]) == tuple(
        case.query for case in DEFAULT_CASES
    )
