from __future__ import annotations

import httpx
import pytest

from novelty_agent_framework.schemas import SearchConcept, SearchPlan, SearchStrategy
from novelty_agent_framework.tools.database_search import compile_search_plan
from novelty_agent_framework.tools.database_search.factory import build_source_registry
from novelty_agent_framework.tools.database_search.providers.common import (
    HttpRequestPolicy,
    MissingProviderCredentialError,
    ProviderRequestError,
    ResilientHttpClient,
)
from novelty_agent_framework.tools.database_search.providers.springer import (
    SpringerNatureArticleClient,
    SpringerNatureFullTextTool,
    SpringerNatureQueryAdapter,
    SpringerNatureSearchTool,
    build_springer_source,
)

BASE_URL = "https://springer.test"


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


def test_query_adapter_compiles_springer_query() -> None:
    query = SpringerNatureQueryAdapter().compile(_plan(use_alias=True))[0]

    assert query.database == "springer"
    assert query.query == (
        '("graph neural network" OR "GNN" OR "graph network") NOT "survey"'
    )


def test_public_compiler_and_registry_lazily_load_springer() -> None:
    query = compile_search_plan(_plan(), database="springer")[0]
    source = build_source_registry().build("springer", {"enabled": False})

    assert query.database == "springer"
    assert isinstance(source.query_adapter, SpringerNatureQueryAdapter)
    assert source.search_tool is None


def test_search_maps_meta_v2_record_and_does_not_leak_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/meta/v2/json"
        assert request.url.params["q"] == '"graph neural network"'
        assert request.url.params["api_key"] == "secret-key"
        assert request.url.params["p"] == "8"
        return httpx.Response(
            200,
            json={
                "records": [
                    {
                        "identifier": "doi:10.1007/example",
                        "doi": "10.1007/example",
                        "title": "A Springer Paper",
                        "abstract": "Structured abstract.",
                        "creators": [{"creator": "Zhang, Alice"}],
                        "publicationDate": "2025-03-04",
                        "openaccess": "true",
                        "url": [
                            {
                                "format": "html",
                                "platform": "web",
                                "value": "https://link.springer.com/article/example",
                            },
                            {
                                "format": "pdf",
                                "platform": "web",
                                "value": "https://link.springer.com/content/pdf/example.pdf",
                            },
                        ],
                    }
                ]
            },
        )

    transport = _transport(handler)
    article_client = SpringerNatureArticleClient(
        transport,
        base_url=BASE_URL,
        api_key="secret-key",
        full_text_mode="openaccess",
    )
    tool = SpringerNatureSearchTool(
        transport,
        article_client,
        base_url=BASE_URL,
        api_key="secret-key",
    )

    hits = tool.search('"graph neural network"', limit=8)

    assert len(hits) == 1
    assert hits[0].document_id == "10.1007/example"
    assert hits[0].authors == ("Zhang, Alice",)
    assert hits[0].year == 2025
    assert hits[0].abstract == "Structured abstract."
    assert hits[0].full_text_url == (
        "https://link.springer.com/content/pdf/example.pdf"
    )


def test_open_access_full_text_parses_jats_and_truncates() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/openaccess/jats"
        assert request.url.params["q"] == "doi:10.1007/example"
        assert request.url.params["api_key"] == "secret-key"
        return httpx.Response(
            200,
            text="""<response><records><article>
              <front><article-meta><title-group><article-title>JATS Paper</article-title>
              </title-group><abstract><p>Abstract text.</p></abstract></article-meta></front>
              <body><sec><title>Methods</title><p>Method details.</p></sec></body>
            </article></records></response>""",
            headers={"Content-Type": "application/xml; charset=utf-8"},
        )

    transport = _transport(handler)
    article_client = SpringerNatureArticleClient(
        transport,
        base_url=BASE_URL,
        api_key="secret-key",
        full_text_mode="openaccess",
    )
    article_client.remember(
        "10.1007/example",
        {
            "doi": "10.1007/example",
            "title": "Cached title",
            "openaccess": "true",
            "url": [
                {
                    "format": "html",
                    "value": "https://link.springer.com/article/example",
                }
            ],
        },
    )

    result = SpringerNatureFullTextTool(article_client, max_chars=24).fetch(
        "10.1007/example"
    )

    assert result is not None
    assert result.title == "JATS Paper"
    assert result.text == "Abstract\n\nAbstract text."
    assert result.content_extent == "partial"
    assert result.sections["Methods"] == "Method details."
    assert result.source_url == "https://link.springer.com/article/example"


def test_open_access_full_text_skips_known_closed_record() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(500)

    article_client = SpringerNatureArticleClient(
        _transport(handler),
        base_url=BASE_URL,
        api_key="secret-key",
        full_text_mode="openaccess",
    )
    article_client.remember(
        "10.1007/closed", {"doi": "10.1007/closed", "openaccess": "false"}
    )

    assert SpringerNatureFullTextTool(article_client).fetch("10.1007/closed") is None
    assert calls["count"] == 0


def test_tdm_mode_uses_metric_and_new_xmldata_endpoint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/xmldata/jats"
        assert request.url.params["api_key"] == "secret-key/metric"
        return httpx.Response(404)

    article_client = SpringerNatureArticleClient(
        _transport(handler),
        base_url=BASE_URL,
        api_key="secret-key",
        full_text_mode="tdm",
        tdm_api_metric="metric",
    )

    assert article_client.fetch_full_text("doi:10.1007/example") is None


def test_springer_http_error_does_not_expose_query_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401)

    transport = _transport(handler)
    article_client = SpringerNatureArticleClient(
        transport,
        base_url=BASE_URL,
        api_key="secret-key",
        full_text_mode="disabled",
    )
    tool = SpringerNatureSearchTool(
        transport,
        article_client,
        base_url=BASE_URL,
        api_key="secret-key",
    )

    with pytest.raises(ProviderRequestError) as exc_info:
        tool.search("graph")

    assert "secret-key" not in str(exc_info.value)


def test_builder_uses_environment_credentials(monkeypatch) -> None:
    monkeypatch.setenv("SPRINGER_TEST_KEY", "test-key")
    source = build_springer_source(
        {
            "enabled": True,
            "api_key_env": "SPRINGER_TEST_KEY",
            "timeout_seconds": 1,
            "min_interval_seconds": 0,
            "full_text_mode": "openaccess",
        }
    )

    assert source.source_id == "springer"
    assert source.search_tool is not None
    assert source.full_text_tool is not None
    source.search_tool.transport.client.close()


def test_tdm_builder_requires_metric(monkeypatch) -> None:
    monkeypatch.setenv("SPRINGER_TEST_KEY", "test-key")
    monkeypatch.delenv("SPRINGER_MISSING_METRIC", raising=False)

    with pytest.raises(MissingProviderCredentialError, match="SPRINGER_MISSING_METRIC"):
        build_springer_source(
            {
                "enabled": True,
                "api_key_env": "SPRINGER_TEST_KEY",
                "full_text_mode": "tdm",
                "tdm_api_metric_env": "SPRINGER_MISSING_METRIC",
            }
        )
