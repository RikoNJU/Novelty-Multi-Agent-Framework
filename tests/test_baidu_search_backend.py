"""Offline HTTP contract tests for BaiduSearchBackend v1."""

from __future__ import annotations

import asyncio

import httpx
import pytest

from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.schemas import NoveltyPoint, ResearchTask, TaskResearchRequest
from novelty_agent_framework.tools import (
    BaiduSearchBackend,
    BaiduSearchError,
    ResearcherToolRegistry,
    WebSearchTool,
)
import novelty_agent_framework.tools.web_search_backend as backend_module
from conftest import minimal_search_plan


class FakeAsyncClient:
    response: httpx.Response | None = None
    error: Exception | None = None
    calls = []

    def __init__(self, *, timeout) -> None:
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def post(self, url, *, headers, json):
        type(self).calls.append(
            {"url": url, "headers": headers, "json": json, "timeout": self.timeout}
        )
        if type(self).error is not None:
            raise type(self).error
        assert type(self).response is not None
        return type(self).response


@pytest.fixture(autouse=True)
def fake_http(monkeypatch):
    FakeAsyncClient.response = None
    FakeAsyncClient.error = None
    FakeAsyncClient.calls = []
    monkeypatch.setattr(backend_module.httpx, "AsyncClient", FakeAsyncClient)


def response(status=200, payload=None, *, text=None) -> httpx.Response:
    request = httpx.Request("POST", "https://qianfan.test/search")
    if text is not None:
        return httpx.Response(status, text=text, request=request)
    return httpx.Response(status, json=payload or {}, request=request)


def search(payload=None, *, query="多智能体 科技查新", max_results=7):
    FakeAsyncClient.response = response(payload=payload)
    return asyncio.run(
        BaiduSearchBackend(api_key="test-key").search(
            query,
            max_results=max_results,
        )
    )


def reference(**updates):
    item = {
        "id": 1,
        "title": "多智能体科技查新",
        "url": "https://example.test/paper",
        "website": "示例网站",
        "snippet": "候选来源摘要",
        "content": "搜索阶段相关内容",
        "date": "2026-08-20 10:00:00",
        "type": "web",
        "web_anchor": "anchor-1",
    }
    item.update(updates)
    return item


def scope() -> TaskResearchRequest:
    return TaskResearchRequest(
        subject_paper_id="EXP_BAIDU_WEBSEARCH",
        run_id="run-baidu-test",
        novelty_point=NoveltyPoint(
            point_id="NP-1", claim="一种方法", technical_features=["特征"]
        ),
        research_task=ResearchTask(
            task_id="TASK-1",
            novelty_point_id="NP-1",
            task_type="search",
            language="zh",
        ),
        search_plan=minimal_search_plan("TASK-1", "NP-1"),
    )


def test_request_and_normal_reference_mapping() -> None:
    result = search(
        {
            "request_id": "req-1",
            "references": [reference(), reference(id=2, url="https://example.test/2")],
        }
    )

    assert BaiduSearchBackend.name == "baidu"
    assert result.query == "多智能体 科技查新"
    assert len(result.hits) == 2
    hit = result.hits[0]
    assert hit.title == "多智能体科技查新"
    assert hit.url == "https://example.test/paper"
    assert hit.snippet == "候选来源摘要"
    assert hit.published_at.isoformat() == "2026-08-20T10:00:00"
    assert hit.source_name == "示例网站"
    assert hit.external_id == "1"
    assert hit.score is None
    assert hit.raw_metadata == {
        "request_id": "req-1",
        "web_anchor": "anchor-1",
        "content": "搜索阶段相关内容",
    }
    call = FakeAsyncClient.calls[0]
    assert call["json"] == {
        "messages": [{"role": "user", "content": "多智能体 科技查新"}],
        "search_source": "baidu_search_v2",
        "resource_type_filter": [{"type": "web", "top_k": 7}],
    }
    assert call["headers"]["Content-Type"] == "application/json"
    assert call["headers"]["Authorization"].startswith("Bearer ")


@pytest.mark.parametrize("payload", [{}, {"references": []}, {"references": None}])
def test_missing_or_empty_references_return_empty_result(payload) -> None:
    assert list(search(payload).hits) == []


def test_optional_fields_title_fallback_and_invalid_date() -> None:
    item = reference()
    for key in ("title", "snippet", "date", "website", "id"):
        item.pop(key)
    first = search({"references": [item]}).hits[0]
    assert first.title == first.url
    assert first.snippet is None
    assert first.published_at is None
    assert first.source_name is None
    assert first.external_id is None

    invalid_date = search(
        {"references": [reference(date="not-a-date")]}
    ).hits[0]
    assert invalid_date.published_at is None


def test_filters_non_web_and_missing_url() -> None:
    FakeAsyncClient.response = response(
        payload={
            "request_id": "req-diagnostics",
            "references": [
                reference(type="image"),
                reference(type="video"),
                reference(url=""),
                reference(id=4),
            ],
        }
    )
    backend = BaiduSearchBackend(api_key="test-key")
    result = asyncio.run(
        backend.search("多智能体 科技查新", max_results=7)
    )
    assert [hit.external_id for hit in result.hits] == ["4"]
    assert backend.last_diagnostics == {
        "request_id": "req-diagnostics",
        "raw_reference_count": 4,
        "normalized_hit_count": 1,
        "skipped_non_web_count": 2,
        "skipped_missing_url_count": 1,
        "missing_snippet_count": 0,
        "missing_date_count": 0,
        "missing_website_count": 0,
        "duplicate_url_count": 0,
    }


@pytest.mark.parametrize("max_results", [0, 51])
def test_max_results_bounds(max_results: int) -> None:
    with pytest.raises(BaiduSearchError, match="1..50"):
        asyncio.run(
            BaiduSearchBackend(api_key="test-key").search(
                "query", max_results=max_results
            )
        )
    assert FakeAsyncClient.calls == []


@pytest.mark.parametrize("query", ["", "   ", "中" * 37, "a" * 73])
def test_empty_or_overlong_query_is_rejected(query: str) -> None:
    with pytest.raises(BaiduSearchError, match="query"):
        asyncio.run(
            BaiduSearchBackend(api_key="test-key").search(query, max_results=1)
        )
    assert FakeAsyncClient.calls == []


@pytest.mark.parametrize("status", [401, 403, 429, 500, 503])
def test_http_errors_preserve_status_and_request_id(status: int) -> None:
    FakeAsyncClient.response = response(
        status,
        {"request_id": "req-error", "message": "provider detail"},
    )
    with pytest.raises(BaiduSearchError, match=f"HTTP {status}") as exc:
        asyncio.run(
            BaiduSearchBackend(api_key="test-key").search("query", max_results=1)
        )
    assert exc.value.status_code == status
    assert exc.value.request_id == "req-error"


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (httpx.ReadTimeout("slow"), "timed out"),
        (httpx.ConnectError("offline"), "network request failed"),
    ],
)
def test_timeout_and_network_errors(error: Exception, message: str) -> None:
    FakeAsyncClient.error = error
    with pytest.raises(BaiduSearchError, match=message):
        asyncio.run(
            BaiduSearchBackend(api_key="test-key").search("query", max_results=1)
        )


def test_invalid_json_and_business_error() -> None:
    FakeAsyncClient.response = response(text="not-json")
    with pytest.raises(BaiduSearchError, match="invalid JSON"):
        asyncio.run(
            BaiduSearchBackend(api_key="test-key").search("query", max_results=1)
        )

    FakeAsyncClient.response = response(
        payload={"code": 18, "message": "quota exceeded", "request_id": "req-18"}
    )
    with pytest.raises(BaiduSearchError, match="quota exceeded") as exc:
        asyncio.run(
            BaiduSearchBackend(api_key="test-key").search("query", max_results=1)
        )
    assert exc.value.request_id == "req-18"


def test_missing_key_fails_before_http(monkeypatch) -> None:
    monkeypatch.delenv("BAIDU_QIANFAN_API_KEY", raising=False)
    with pytest.raises(BaiduSearchError, match="not configured"):
        asyncio.run(BaiduSearchBackend().search("query", max_results=1))
    assert FakeAsyncClient.calls == []


def test_baidu_backend_injects_into_unchanged_web_search_tool(tmp_path) -> None:
    FakeAsyncClient.response = response(
        payload={"request_id": "req-live-shape", "references": [reference()]}
    )
    store = ReferenceStore(output_root=tmp_path)
    registry = ResearcherToolRegistry(
        [WebSearchTool(BaiduSearchBackend(api_key="test-key"), store)]
    )
    observation = asyncio.run(
        registry.execute(
            "web_search",
            {"query": "多智能体 科技查新", "max_results": 3},
            scope=scope(),
        )
    )

    assert observation.succeeded is True
    result = observation.payload["search_result"]
    source_record_id = result["results"][0]["source_record_id"]
    manifest = store.load_manifest("EXP_BAIDU_WEBSEARCH")
    record = manifest.source_records[0]
    assert record.source_record_id == source_record_id
    assert record.source_id == "baidu"
    assert record.landing_url == "https://example.test/paper"
    assert record.raw_metadata["content"] == "搜索阶段相关内容"
    assert manifest.artifacts == []
