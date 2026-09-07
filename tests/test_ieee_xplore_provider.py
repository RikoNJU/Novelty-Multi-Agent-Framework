from __future__ import annotations

import httpx
import pytest

from novelty_agent_framework.schemas import SearchConcept, SearchPlan, SearchStrategy
from novelty_agent_framework.tools.database_search import compile_search_plan
from novelty_agent_framework.tools.database_search.factory import build_source_registry
from novelty_agent_framework.tools.database_search.providers.common import (
    HttpRequestPolicy,
    ProviderConfigurationError,
    ProviderRequestError,
    ResilientHttpClient,
)
from novelty_agent_framework.tools.database_search.providers.ieee_xplore import (
    IEEEXploreArticleClient,
    IEEEXploreFullTextTool,
    IEEEXploreQueryAdapter,
    IEEEXploreSearchTool,
    build_ieee_xplore_source,
)

BASE_URL = "https://ieee.test/api/v1"


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


def test_query_adapter_compiles_ieee_querytext() -> None:
    query = IEEEXploreQueryAdapter().compile(_plan(use_alias=True))[0]

    assert query.database == "ieee_xplore"
    assert query.query == (
        '("graph neural network" OR "GNN" OR "graph network") NOT "survey"'
    )


def test_public_compiler_and_registry_lazily_load_ieee() -> None:
    query = compile_search_plan(_plan(), database="ieee_xplore")[0]
    source = build_source_registry().build("ieee_xplore", {"enabled": False})

    assert query.database == "ieee_xplore"
    assert isinstance(source.query_adapter, IEEEXploreQueryAdapter)
    assert source.search_tool is None


def test_search_maps_ieee_metadata_and_abstract() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/search/articles"
        assert request.url.params["querytext"] == '"graph neural network"'
        assert request.url.params["apikey"] == "secret-key"
        assert request.url.params["max_records"] == "8"
        return httpx.Response(
            200,
            json={
                "total_records": 1,
                "articles": [
                    {
                        "article_number": "12345678",
                        "title": "An <b>IEEE</b> Paper",
                        "abstract": "<p>Structured abstract.</p>",
                        "authors": {"authors": [{"full_name": "Alice Zhang"}]},
                        "publication_year": "2025",
                        "doi": "10.1109/example",
                        "html_url": "https://ieeexplore.ieee.org/document/12345678",
                        "pdf_url": "https://ieeexplore.ieee.org/document/12345678.pdf",
                        "access_type": "OPEN_ACCESS",
                    }
                ],
            },
        )

    transport = _transport(handler)
    article_client = IEEEXploreArticleClient(
        transport,
        base_url=BASE_URL,
        api_key="secret-key",
        full_text_mode="openaccess",
    )
    tool = IEEEXploreSearchTool(
        transport,
        article_client,
        base_url=BASE_URL,
        api_key="secret-key",
    )

    hits = tool.search('"graph neural network"', limit=8)

    assert len(hits) == 1
    assert hits[0].document_id == "12345678"
    assert hits[0].title == "An IEEE Paper"
    assert hits[0].abstract == "Structured abstract."
    assert hits[0].authors == ("Alice Zhang",)
    assert hits[0].year == 2025
    assert hits[0].full_text_url.endswith("12345678.pdf")


def test_open_access_full_text_uses_article_number_and_parses_xml() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/search/document/12345678/fulltext"
        assert request.url.params["apikey"] == "secret-key"
        assert request.url.params["format"] == "xml"
        return httpx.Response(
            200,
            text="""<document><article><front><article-meta><title-group>
              <article-title>IEEE Full Text</article-title></title-group>
              <abstract><p>Abstract text.</p></abstract></article-meta></front>
              <body><sec><title>Results</title><p>Result details.</p></sec></body>
            </article></document>""",
            headers={"Content-Type": "application/xml"},
        )

    article_client = IEEEXploreArticleClient(
        _transport(handler),
        base_url=BASE_URL,
        api_key="secret-key",
        full_text_mode="openaccess",
    )
    article_client.remember(
        "12345678",
        {
            "title": "Cached title",
            "doi": "10.1109/example",
            "html_url": "https://ieeexplore.ieee.org/document/12345678",
            "access_type": "OPEN_ACCESS",
        },
    )

    result = IEEEXploreFullTextTool(article_client).fetch("12345678")

    assert result is not None
    assert result.title == "IEEE Full Text"
    assert "Result details." in result.text
    assert result.sections["Results"] == "Result details."
    assert result.content_extent == "full"
    assert result.source is not None
    assert result.source.doi == "10.1109/example"


def test_open_access_full_text_skips_known_subscription_record() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(500)

    article_client = IEEEXploreArticleClient(
        _transport(handler),
        base_url=BASE_URL,
        api_key="secret-key",
        full_text_mode="openaccess",
    )
    article_client.remember("12345678", {"access_type": "SUBSCRIPTION"})

    assert IEEEXploreFullTextTool(article_client).fetch("12345678") is None
    assert calls["count"] == 0


def test_non_available_open_access_response_degrades_to_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400)

    article_client = IEEEXploreArticleClient(
        _transport(handler),
        base_url=BASE_URL,
        api_key="secret-key",
        full_text_mode="openaccess",
    )

    assert IEEEXploreFullTextTool(article_client).fetch("12345678") is None


def test_ieee_http_error_does_not_expose_query_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401)

    transport = _transport(handler)
    article_client = IEEEXploreArticleClient(
        transport,
        base_url=BASE_URL,
        api_key="secret-key",
        full_text_mode="disabled",
    )
    tool = IEEEXploreSearchTool(
        transport,
        article_client,
        base_url=BASE_URL,
        api_key="secret-key",
    )

    with pytest.raises(ProviderRequestError) as exc_info:
        tool.search("graph")

    assert "secret-key" not in str(exc_info.value)


def test_builder_uses_environment_credentials(monkeypatch) -> None:
    monkeypatch.setenv("IEEE_TEST_KEY", "test-key")
    source = build_ieee_xplore_source(
        {
            "enabled": True,
            "api_key_env": "IEEE_TEST_KEY",
            "timeout_seconds": 1,
            "min_interval_seconds": 0,
            "full_text_mode": "openaccess",
        }
    )

    assert source.source_id == "ieee_xplore"
    assert source.search_tool is not None
    assert source.full_text_tool is not None
    source.search_tool.transport.client.close()


def test_builder_rejects_unimplemented_chargeable_mode(monkeypatch) -> None:
    monkeypatch.setenv("IEEE_TEST_KEY", "test-key")

    with pytest.raises(ProviderConfigurationError, match="separately contracted"):
        build_ieee_xplore_source(
            {
                "enabled": True,
                "api_key_env": "IEEE_TEST_KEY",
                "full_text_mode": "chargeable",
            }
        )
