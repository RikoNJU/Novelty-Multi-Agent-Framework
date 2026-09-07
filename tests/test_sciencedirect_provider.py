from __future__ import annotations

import json

import httpx
import pytest

from novelty_agent_framework.schemas import SearchConcept, SearchPlan, SearchStrategy
from novelty_agent_framework.tools.database_search.factory import build_source_registry
from novelty_agent_framework.tools.database_search import compile_search_plan
from novelty_agent_framework.tools.database_search.providers.common import (
    HttpRequestPolicy,
    ResilientHttpClient,
)
from novelty_agent_framework.tools.database_search.providers.sciencedirect import (
    ScienceDirectArticleClient,
    ScienceDirectFullTextTool,
    ScienceDirectQueryAdapter,
    ScienceDirectSearchTool,
    build_sciencedirect_source,
)

BASE_URL = "https://api.elsevier.test"
HEADERS = {"X-ELS-APIKey": "test-key"}


def _transport(handler) -> ResilientHttpClient:
    return ResilientHttpClient(
        httpx.Client(transport=httpx.MockTransport(handler)),
        policy=HttpRequestPolicy(min_interval_seconds=0, max_retries=0),
    )


def _plan(*, use_alias: bool = False) -> SearchPlan:
    return SearchPlan(
        task_id="T1",
        novelty_point_id="NP1",
        concepts=[
            SearchConcept(
                concept_id="C1",
                name="graph model",
                terms=["graph neural network", "GNN"],
                alias=["graph network"],
                exclude=["survey"],
            )
        ],
        strategies=[
            SearchStrategy(
                strategy_id="S1",
                level="strict",
                expression="C1",
                use_alias=use_alias,
            )
        ],
    )


def test_query_adapter_compiles_sciencedirect_qs() -> None:
    query = ScienceDirectQueryAdapter().compile(_plan(use_alias=True))[0]

    assert query.database == "sciencedirect"
    assert query.query == (
        '("graph neural network" OR "GNN" OR "graph network") '
        'AND NOT ("survey")'
    )


def test_public_compiler_lazily_loads_sciencedirect_adapter() -> None:
    query = compile_search_plan(_plan(), database="sciencedirect")[0]

    assert query.database == "sciencedirect"


def test_query_adapter_rejects_provider_limit() -> None:
    with pytest.raises(ValueError, match="exceeds 20 characters"):
        ScienceDirectQueryAdapter(max_query_chars=20).compile(_plan())


def test_search_maps_results_and_enriches_abstract() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        assert request.headers["X-ELS-APIKey"] == "test-key"
        if request.method == "PUT":
            body = json.loads(request.content)
            assert body["display"]["show"] == 10
            assert body["qs"] == '"graph neural network"'
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "pii": "S123456789",
                            "title": "A Graph Paper",
                            "authors": [{"order": 0, "name": "Alice Zhang"}],
                            "doi": "10.1016/example",
                            "publicationDate": "2025-02-03",
                            "uri": "https://www.sciencedirect.com/science/article/pii/S123456789",
                        }
                    ]
                },
            )
        assert request.url.params["view"] == "META_ABS"
        return httpx.Response(
            200,
            json={
                "full-text-retrieval-response": {
                    "coredata": {
                        "dc:title": "A Graph Paper",
                        "dc:description": "Complete abstract text.",
                        "prism:doi": "10.1016/example",
                    }
                }
            },
        )

    search_transport = _transport(handler)
    article_transport = _transport(handler)
    article_client = ScienceDirectArticleClient(
        article_transport, base_url=BASE_URL, headers=HEADERS
    )
    tool = ScienceDirectSearchTool(
        search_transport,
        article_client,
        base_url=BASE_URL,
        headers=HEADERS,
        abstract_enrichment_limit=1,
    )

    hits = tool.search('"graph neural network"', limit=8)

    assert len(hits) == 1
    assert hits[0].document_id == "S123456789"
    assert hits[0].authors == ("Alice Zhang",)
    assert hits[0].year == 2025
    assert hits[0].abstract == "Complete abstract text."
    assert hits[0].full_text_url == (
        "https://api.elsevier.test/content/article/pii/S123456789"
    )
    assert [request.method for request in requests] == ["PUT", "GET"]


def test_full_text_returns_none_when_not_entitled() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["view"] == "FULL"
        return httpx.Response(403)

    article_client = ScienceDirectArticleClient(
        _transport(handler), base_url=BASE_URL, headers=HEADERS
    )

    assert ScienceDirectFullTextTool(article_client).fetch("S123") is None


def test_full_text_is_returned_and_truncated() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.params["view"] == "FULL":
            return httpx.Response(
                200,
                text="abcdefghij",
                headers={"Content-Type": "text/plain; charset=utf-8"},
            )
        return httpx.Response(
            200,
            json={
                "full-text-retrieval-response": {
                    "coredata": {
                        "dc:title": "Entitled Paper",
                        "prism:doi": "10.1016/entitled",
                    }
                }
            },
        )

    article_client = ScienceDirectArticleClient(
        _transport(handler), base_url=BASE_URL, headers=HEADERS
    )
    article_client.fetch_metadata("S123")
    result = ScienceDirectFullTextTool(article_client, max_chars=5).fetch("S123")

    assert result is not None
    assert result.title == "Entitled Paper"
    assert result.text == "abcde"
    assert result.content_extent == "partial"


def test_builder_uses_environment_credentials(monkeypatch) -> None:
    monkeypatch.setenv("ELSEVIER_TEST_KEY", "test-key")
    source = build_sciencedirect_source(
        {
            "enabled": True,
            "api_key_env": "ELSEVIER_TEST_KEY",
            "timeout_seconds": 1,
            "search_min_interval_seconds": 0,
            "article_min_interval_seconds": 0,
        }
    )

    assert source.source_id == "sciencedirect"
    assert source.search_tool is not None
    assert source.metadata_tool is None
    assert source.full_text_tool is not None
    source.search_tool.transport.client.close()


def test_default_registry_exposes_adapter_without_credentials() -> None:
    source = build_source_registry().build("sciencedirect", {"enabled": False})

    assert isinstance(source.query_adapter, ScienceDirectQueryAdapter)
    assert source.search_tool is None
