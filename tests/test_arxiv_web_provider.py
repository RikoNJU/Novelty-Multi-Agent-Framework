"""arXiv 主站通道（``search_transport="web"``）：查询翻译、解析与开关行为。

离线测试：HTTP 全部用 ``httpx.MockTransport`` 或本地夹具（``tests/fixtures/arxiv_web``
来自 2026-09-15 真实页面抓取），不触网。
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from novelty_agent_framework.schemas import ExternalIdentifier, ParsedCitation
from novelty_agent_framework.tools.database_search.providers.arxiv import (
    DEFAULT_SEARCH_TRANSPORT,
    SEARCH_TRANSPORTS,
    ArxivMetadataTool,
    ArxivSearchTool,
    build_arxiv_search_tool,
    build_arxiv_source,
    resolve_search_transport,
)
from novelty_agent_framework.tools.database_search.providers.arxiv_web import (
    ALLOWED_PAGE_SIZES,
    ARXIV_WEB_ADVANCED_URL,
    MAX_QUERY_SLOTS,
    ArxivWebChannelError,
    ArxivWebMetadataTool,
    ArxivWebSearchTool,
    ArxivWebSession,
    build_arxiv_web_search_tool,
    parse_abs_page,
    parse_search_page,
    translate_arxiv_query,
)

FIXTURES = Path("tests/fixtures/arxiv_web")
SEARCH_FIXTURE = FIXTURES / "search_advanced.html"
ABS_FIXTURE = FIXTURES / "abs_page.html"
ABS_DOC_ID = "2607.05736"


def _fixture(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _session(handler, **overrides) -> ArxivWebSession:
    options = {"min_interval": 0.0, "max_retries": 0, "timeout": 5.0}
    options.update(overrides)
    return ArxivWebSession(
        client=httpx.Client(transport=httpx.MockTransport(handler)), **options
    )


def _search_tool(handler, **overrides) -> ArxivWebSearchTool:
    return ArxivWebSearchTool(session=_session(handler, **overrides))


# ---- 查询翻译 --------------------------------------------------------------


def test_translate_maps_api_fields_to_advanced_form() -> None:
    plan = translate_arxiv_query(
        '(ti:"dynamic graph" OR ti:"temporal graph") AND abs:"graph summarization"'
    )

    assert plan.params["terms-0-field"] == "title"
    assert plan.params["terms-0-term"] == '"dynamic graph" OR "temporal graph"'
    assert plan.params["terms-1-field"] == "abstract"
    assert plan.params["terms-1-term"] == '"graph summarization"'
    assert plan.params["abstracts"] == "show"
    assert plan.excludes == ()
    assert plan.notes == ()


def test_translate_extracts_andnot_clauses_as_local_excludes() -> None:
    """主站不支持 ANDNOT（实测 0 结果），排除项必须由调用方本地过滤。"""

    plan = translate_arxiv_query(
        '(abs:"fine-grained attention") ANDNOT (all:"image super resolution")'
    )

    assert plan.excludes == ("image super resolution",)
    assert all("ANDNOT" not in str(value) for value in plan.params.values())
    assert not any(
        key.endswith("-term") for key in plan.params if key != "terms-0-term"
    )


def test_translate_keeps_word_level_terms_unquoted() -> None:
    """render_v2 的长术语是词级 AND（``all:w1 AND all:w2``），不能加上引号。"""

    plan = translate_arxiv_query("all:graph AND all:neural")

    assert plan.params["terms-0-term"] == "graph"
    assert plan.params["terms-1-term"] == "neural"
    assert plan.params["terms-0-field"] == "all"


def test_translate_merges_real_world_or_group() -> None:
    """真实编译查询：一个概念里 6 个 OR 术语必须落进同一个槽位。"""

    plan = translate_arxiv_query(
        '(ti:"music generation" OR ti:"music generation model" OR ti:"Museformer") '
        'AND abs:"fine-grained attention"'
    )

    assert '"music generation" OR "music generation model" OR "Museformer"' == (
        plan.params["terms-0-term"]
    )
    assert plan.params["terms-1-term"] == '"fine-grained attention"'


def test_translate_compacts_same_field_clauses_before_dropping() -> None:
    """同字段的单术语子句先用 AND 并进同一槽位（实测槽位内 AND 有效）。"""

    clauses = " AND ".join(
        f'all:"term {index}"' for index in range(MAX_QUERY_SLOTS + 4)
    )
    plan = translate_arxiv_query(clauses)

    slots = [key for key in plan.params if key.endswith("-term")]
    assert len(slots) == (MAX_QUERY_SLOTS + 4) // 2
    assert " AND " in plan.params["terms-0-term"]
    assert plan.notes == ()


def test_translate_drops_beyond_slot_limit_when_compaction_cannot_help() -> None:
    """字段交替时无法合并，超出上限只能丢弃（结果更宽，且必须留痕）。"""

    clauses = " AND ".join(
        f'{"ti" if index % 2 else "abs"}:"term {index}"'
        for index in range(MAX_QUERY_SLOTS + 4)
    )
    plan = translate_arxiv_query(clauses)

    slots = [key for key in plan.params if key.endswith("-term")]
    assert len(slots) == MAX_QUERY_SLOTS
    assert any("丢弃" in note for note in plan.notes)


def test_translate_rejects_unparsable_fragment() -> None:
    with pytest.raises(ValueError):
        translate_arxiv_query('all:"graph" XOR all:"neural"')


def test_translate_rejects_unbalanced_parenthesis() -> None:
    with pytest.raises(ValueError):
        translate_arxiv_query('(all:"graph" AND all:"neural"')


def test_translate_preserves_real_adapter_grouping() -> None:
    """真实 ArxivQueryAdapter 输出：OR 组 + 组内词级 AND 链必须落进同一个槽位。

    回归保护：早期实现把这些项拍平成独立槽位（``"graph neural network" OR message``
    / ``passing`` / ``neural`` / ``network``…），结果集被收窄到 0 条。
    """

    plan = translate_arxiv_query(
        '(ti:"graph neural network" OR ti:message AND ti:passing AND ti:neural '
        'AND ti:network) AND abs:"molecular property prediction" AND all:"survey" '
        'ANDNOT (all:"survey" OR all:"review")'
    )

    assert [
        (plan.params[f"terms-{index}-field"], plan.params[f"terms-{index}-term"])
        for index in range(3)
    ] == [
        ("title", '"graph neural network" OR message AND passing AND neural AND network'),
        ("abstract", '"molecular property prediction"'),
        ("all", '"survey"'),
    ]
    assert not any(key == "terms-3-term" for key in plan.params)
    assert plan.excludes == ("survey", "review")
    assert any("ANDNOT 降级为本地过滤" in note for note in plan.notes)


def test_translate_top_level_or_becomes_single_slot() -> None:
    """broad 策略是概念间的 OR（``C1 OR C2 OR C3``），整体占一个槽位。"""

    plan = translate_arxiv_query('(ti:"a" OR ti:"b") OR ti:"c" OR ti:"d"')

    assert plan.params["terms-0-term"] == '"a" OR "b" OR "c" OR "d"'
    assert plan.params["terms-0-field"] == "title"
    assert not any(key == "terms-1-term" for key in plan.params)


def test_translate_degrades_cross_field_group_to_all() -> None:
    """跨字段 OR 组无法用单一槽位表达，降级为 all 并留痕（宁宽勿错）。"""

    plan = translate_arxiv_query('all:"query" AND (ti:"title term" OR abs:"abs term")')

    assert plan.params["terms-1-field"] == "all"
    assert plan.params["terms-1-term"] == '"title term" OR "abs term"'
    assert any("跨字段分组" in note for note in plan.notes)


def test_translate_splits_transparent_parentheses_without_extra_syntax() -> None:
    """``(a AND (b OR c))`` 的外层括号是透明的：拆成两个槽位，不需要括号语法。"""

    plan = translate_arxiv_query('(all:"a" AND (all:"b" OR all:"c"))')

    assert plan.params["terms-0-term"] == '"a"'
    assert plan.params["terms-1-term"] == '"b" OR "c"'
    assert plan.notes == ()


def test_translate_adds_parentheses_only_for_nested_or_inside_and() -> None:
    """AND 里嵌 OR 且整体又在别的分组内时才需要括号，并且必须留痕。"""

    plan = translate_arxiv_query('all:"x" OR (all:"a" AND (all:"b" OR all:"c"))')

    assert plan.params["terms-0-term"] == '"x" OR "a" AND ("b" OR "c")'
    assert any("括号" in note for note in plan.notes)


def test_translate_strips_negation_attached_to_a_group() -> None:
    """``(a OR b) ANDNOT (x)``：OR 组保留，ANDNOT 完全剥离。"""

    plan = translate_arxiv_query('(ti:"a" OR ti:"b") ANDNOT (all:"x" OR all:"y")')

    assert plan.params["terms-0-term"] == '"a" OR "b"'
    assert plan.excludes == ("x", "y")
    assert not any("ANDNOT" in str(value) for value in plan.params.values())


# ---- HTML 解析 -------------------------------------------------------------


def test_parse_search_page_reads_real_fixture() -> None:
    hits = parse_search_page(_fixture(SEARCH_FIXTURE), limit=5)

    assert len(hits) == 3
    first = hits[0]
    assert first.document_id == ABS_DOC_ID
    assert first.title and "Graph Neural" in first.title
    assert first.source_id == "arxiv"
    assert first.url == f"https://arxiv.org/abs/{ABS_DOC_ID}"
    assert first.full_text_url == f"https://arxiv.org/pdf/{ABS_DOC_ID}"
    assert first.year and 2000 < first.year < 2100
    assert first.authors
    assert "<span" not in first.abstract


def test_parse_search_page_keeps_full_abstract_when_highlighted() -> None:
    """回归：摘要里嵌 ``search-hit`` span 时，按嵌套深度取内容而不是提前截断。"""

    hits = parse_search_page(_fixture(SEARCH_FIXTURE), limit=5)

    assert all(len(hit.abstract) > 500 for hit in hits)


def test_parse_search_page_drops_abstract_collapse_toggle() -> None:
    """回归：``abstract-full`` 末尾的折叠开关 ``△ Less`` 不得混进摘要正文。

    它是被取的 span 内部的一个 ``<a>``，``_clean`` 只剥标签不剥文字。实测主站
    落库的 9/9 篇摘要都以 ``△ Less`` 结尾（API 通道没有），该文字会进
    ``SourceRecord.abstract`` 与候选清单。夹具里三个结果全部带这个标记。
    """

    hits = parse_search_page(_fixture(SEARCH_FIXTURE), limit=5)

    assert hits
    for hit in hits:
        assert "△ Less" not in hit.abstract
        assert "▽ More" not in hit.abstract
        assert not hit.abstract.endswith("Less")


def test_parse_abs_page_drops_abstract_collapse_toggle() -> None:
    hit = parse_abs_page(
        '<h1 class="title mathjax">Title: A Paper</h1>'
        '<div class="authors">Authors: A. Author</div>'
        '<blockquote class="abstract mathjax">'
        "<span>Abstract:</span> Body text of the paper."
        '<a href="#" class="is-size-7"'
        ' onclick="toggle();">&#9661; More</a>'
        "</blockquote>",
        "1234.5678",
    )

    assert hit is not None
    assert hit.abstract == "Body text of the paper."


def test_parse_abs_page_reads_real_fixture() -> None:
    hit = parse_abs_page(_fixture(ABS_FIXTURE), ABS_DOC_ID)

    assert hit is not None
    assert hit.document_id == ABS_DOC_ID
    assert hit.title.startswith("Multimodal")
    assert len(hit.abstract) > 500
    assert hit.authors
    assert hit.year == 2026


def test_parse_abs_page_returns_none_without_title() -> None:
    assert parse_abs_page("<html><body>not a paper</body></html>", "1234.5678") is None


def test_parse_search_page_records_observed_version() -> None:
    """``external_id`` 带观测版本、``document_id`` 不带——与 API 通道同形。

    两处分开不是洁癖：``document_id`` 是下游解析标识的入口（必须无版本），而
    ``external_id`` 决定 ``source_record_id``。主站若把它填成无版本形态，同一篇
    论文在 API 通道下已有一条记录、切到主站会再算出一条（实测清单里 124 个 work
    对应 125 条记录），并且 ``adapt_hit`` 的 ``has no observed version`` 警告会对
    每一篇候选触发。
    """

    hits = parse_search_page(_fixture(SEARCH_FIXTURE), limit=5)

    assert hits
    for hit in hits:
        assert "v" not in hit.document_id
        assert hit.external_id == f"{hit.document_id}v1"


def test_parse_abs_page_records_observed_version() -> None:
    hit = parse_abs_page(_fixture(ABS_FIXTURE), ABS_DOC_ID)

    assert hit is not None
    assert hit.document_id == ABS_DOC_ID
    assert hit.external_id == f"{ABS_DOC_ID}v1"


def test_parse_search_page_does_not_invent_version() -> None:
    """页面没给出版本 id 时不臆造 v1，退回无版本形态（沿用 API 通道的既有约定）。"""

    html = (
        '<li class="arxiv-result">'
        '<p class="title is-5 mathjax">A. Title</p>'
        '<p class="authors"><a>B. Author</a></p>'
        '<p class="abstract mathjax">Abstract: Some abstract text long enough.</p>'
        '<a href="https://arxiv.org/abs/1234.5678">arXiv:1234.5678</a>'
        "</li>"
    )

    hits = parse_search_page(html, limit=5)

    assert len(hits) == 1
    assert hits[0].document_id == "1234.5678"
    assert hits[0].external_id == "1234.5678"


# ---- 工具行为 --------------------------------------------------------------


def test_search_applies_local_excludes() -> None:
    html = _fixture(SEARCH_FIXTURE)
    tool = _search_tool(lambda request: httpx.Response(200, text=html))

    hits = tool.search('ti:"graph neural network" ANDNOT (all:"quantum")')

    assert len(hits) == 2  # 排除前 3 条
    assert all("quantum" not in hit.abstract.casefold() for hit in hits)
    assert all("quantum" not in hit.title.casefold() for hit in hits)


def test_search_excludes_can_empty_the_page() -> None:
    """三条夹具都含 molecular：排除生效时结果可以为空，而不是退回未过滤结果。"""

    html = _fixture(SEARCH_FIXTURE)
    tool = _search_tool(lambda request: httpx.Response(200, text=html))

    assert tool.search('ti:"graph neural network" ANDNOT (all:"molecular")') == ()


def test_search_requests_advanced_form_and_show_abstracts() -> None:
    html = _fixture(SEARCH_FIXTURE)
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(dict(request.url.params))
        return httpx.Response(200, text=html)

    tool = _search_tool(handler)
    tool.search('ti:"graph neural network"', limit=5)

    assert captured["abstracts"] == "show"
    assert captured["terms-0-field"] == "title"
    assert captured["terms-0-term"] == '"graph neural network"'
    assert captured["size"] == "25"


def test_search_returns_empty_tuple_on_channel_failure() -> None:
    """通道故障必须返回空结果：抛异常会打断整条检索放宽链。"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    tool = _search_tool(handler)
    hits = tool.search('ti:"graph neural network"')

    assert tuple(hits) == ()
    assert tool.last_error and "500" in tool.last_error


def test_search_skips_request_when_all_conditions_are_negated() -> None:
    """全是 ANDNOT 的查询没有服务端条件：不能裸打主站（那等于全库检索）。"""

    requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        return httpx.Response(200, text=_fixture(SEARCH_FIXTURE))

    tool = _search_tool(handler)

    assert tool.search('ANDNOT (all:"survey")') == ()
    assert requests == []
    assert tool.last_error and "正向条件" in tool.last_error


def test_size_for_snaps_to_page_sizes_the_site_accepts() -> None:
    """主站只认 25/50/100/200；任意条数必须向上取整，否则 400 被吞成空结果。"""

    tool = _search_tool(lambda request: httpx.Response(200, text=""))

    assert [tool._size_for(limit) for limit in (1, 5, 25, 26, 30, 50, 51, 120, 999)] == [
        25,
        25,
        25,
        50,
        50,
        50,
        100,
        200,
        200,
    ]
    assert all(value in ALLOWED_PAGE_SIZES for value in (tool._size_for(n) for n in range(1, 300)))


def test_search_sends_a_page_size_the_site_accepts() -> None:
    """回归保护：limit=30 曾直接透传成 size=30 → HTTP 400 → 静默空结果。"""

    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(dict(request.url.params))
        return httpx.Response(200, text=_fixture(SEARCH_FIXTURE))

    hits = _search_tool(handler).search('ti:"graph neural network"', limit=30)

    assert captured["size"] == "50"
    assert len(hits) == 3  # 夹具只有 3 条，取实际返回


def test_search_seeds_abs_cache_for_metadata_enrichment() -> None:
    """检索链拿到候选后必然做元数据核验：结果页数据要预热，避免重复打主站。"""

    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(200, text=_fixture(SEARCH_FIXTURE))

    search = _search_tool(handler)
    metadata = ArxivWebMetadataTool(session=search._session, search=search)

    hits = search.search('ti:"graph neural network"')
    assert hits
    resolved = metadata.resolve(hits[0].document_id)

    assert resolved is not None
    assert resolved.title == hits[0].title
    assert calls == ["/search/advanced"]  # 富化没有再产生请求


def test_search_does_not_overwrite_real_abs_fetch_with_page_data() -> None:
    """预热是 setdefault：真抓过 /abs/ 的条目更权威，不能被结果页覆盖。"""

    abs_html = _fixture(ABS_FIXTURE)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.startswith("/abs/"):
            return httpx.Response(200, text=abs_html)
        return httpx.Response(200, text=_fixture(SEARCH_FIXTURE))

    tool = _search_tool(handler)
    identifier = ExternalIdentifier(namespace="arxiv", value=ABS_DOC_ID)
    fetched = tool.resolve_identifier(identifier)
    assert fetched is not None

    tool.search('ti:"graph neural network"')

    assert tool.abs_hit(ABS_DOC_ID) is fetched


def test_resolve_identifier_returns_none_on_404() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="no such paper")

    tool = _search_tool(handler)
    identifier = ExternalIdentifier(namespace="arxiv", value="2607.05736v2")

    assert tool.resolve_identifier(identifier) is None


def test_resolve_identifier_reads_abs_page_and_caches() -> None:
    calls: list[str] = []
    html = _fixture(ABS_FIXTURE)

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(200, text=html)

    tool = _search_tool(handler)
    identifier = ExternalIdentifier(namespace="arxiv", value="2607.05736")

    first = tool.resolve_identifier(identifier)
    second = tool.resolve_identifier(identifier)

    assert first is not None and second is not None
    assert first.title == second.title
    assert calls == [f"/abs/{ABS_DOC_ID}"]
    assert tool.resolve_identifier(
        ExternalIdentifier(namespace="doi", value="10.1/x")
    ) is None


def test_resolve_identifier_raises_on_channel_failure() -> None:
    """bootstrap 需要区分「通道故障」(FAILED) 与「查无此条」(not_found)。"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="unavailable")

    tool = _search_tool(handler)

    with pytest.raises(ArxivWebChannelError):
        tool.resolve_identifier(
            ExternalIdentifier(namespace="arxiv", value=ABS_DOC_ID)
        )


def test_search_known_item_raises_on_channel_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="unavailable")

    tool = _search_tool(handler)
    citation = ParsedCitation(title="Multimodal Molecular Representation")

    with pytest.raises(ArxivWebChannelError):
        tool.search_known_item(citation)


def test_search_known_item_uses_title_phrase_on_simple_search() -> None:
    html = _fixture(SEARCH_FIXTURE)
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(dict(request.url.params))
        captured["path"] = request.url.path
        return httpx.Response(200, text=html)

    tool = _search_tool(handler)
    hits = tool.search_known_item(
        ParsedCitation(title='A "quoted" title'), limit=5
    )

    assert captured["path"] == "/search/"
    assert captured["searchtype"] == "all"
    assert captured["query"] == '"A  quoted  title"'
    assert len(hits) == 3


def test_metadata_tool_returns_source_from_abs_page() -> None:
    html = _fixture(ABS_FIXTURE)
    tool = ArxivWebMetadataTool(
        session=_session(lambda request: httpx.Response(200, text=html))
    )

    source = tool.resolve(ABS_DOC_ID)

    assert source is not None
    assert source.url == f"https://arxiv.org/abs/{ABS_DOC_ID}"
    assert source.title.startswith("Multimodal")


def test_metadata_tool_returns_none_on_channel_failure() -> None:
    """与 ArxivMetadataTool 在 API 无响应时返回 None 的契约一致。"""

    tool = ArxivWebMetadataTool(
        session=_session(lambda request: httpx.Response(500, text="boom"))
    )

    assert tool.resolve(ABS_DOC_ID) is None
    assert tool.last_error


def test_metadata_tool_reuses_search_abs_cache() -> None:
    """检索链先解析过的 ID，元数据核验必须直接命中缓存（主站单次 5~25 秒）。"""

    calls: list[str] = []
    html = _fixture(ABS_FIXTURE)

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(200, text=html)

    search = _search_tool(handler)
    metadata = ArxivWebMetadataTool(session=search._session, search=search)

    assert search.resolve_identifier(
        ExternalIdentifier(namespace="arxiv", value=ABS_DOC_ID)
    ) is not None
    assert metadata.resolve(ABS_DOC_ID) is not None
    assert calls == [f"/abs/{ABS_DOC_ID}"]  # 只打了一次主站


def test_session_throttles_consecutive_requests() -> None:
    import time

    html = _fixture(SEARCH_FIXTURE)
    tool = _search_tool(
        lambda request: httpx.Response(200, text=html), min_interval=0.2
    )

    started = time.monotonic()
    tool.search('ti:"a"')
    tool.search('ti:"b"')
    assert time.monotonic() - started >= 0.18


# ---- 开关 ------------------------------------------------------------------


def test_transport_defaults_to_api_and_rejects_unknown_values() -> None:
    assert DEFAULT_SEARCH_TRANSPORT == "api"
    assert SEARCH_TRANSPORTS == ("api", "web")
    assert resolve_search_transport({}) == "api"
    assert resolve_search_transport({"search_transport": " WEB "}) == "web"
    with pytest.raises(ValueError):
        resolve_search_transport({"search_transport": "main_site"})


def test_build_search_tool_switches_channel() -> None:
    web_tool = build_arxiv_search_tool({"search_transport": "web"})
    api_tool = build_arxiv_search_tool({"min_interval_seconds": 6})

    assert isinstance(web_tool, ArxivWebSearchTool)
    assert isinstance(api_tool, ArxivSearchTool)
    assert web_tool.source_id == api_tool.source_id == "arxiv"


def test_build_source_uses_web_channel_without_api_scheduler() -> None:
    config = {
        "enabled": True,
        "search_transport": "web",
        "min_interval_seconds": 6,
        "timeout_seconds": 20,
        "full_text_max_chars": 100000,
        "web_min_interval_seconds": 1.5,
    }
    source = build_arxiv_source(config)

    assert isinstance(source.search_tool, ArxivWebSearchTool)
    assert isinstance(source.metadata_tool, ArxivWebMetadataTool)
    assert source.search_tool._session._min_interval == 1.5
    assert source.search_tool._session is source.metadata_tool._session
    assert source.full_text_tool is not None


def test_build_source_keeps_api_channel_by_default() -> None:
    config = {
        "enabled": True,
        "min_interval_seconds": 6,
        "scheduler_enabled": False,
        "timeout_seconds": 20,
        "max_retries": 2,
        "full_text_max_chars": 100000,
    }
    source = build_arxiv_source(config)

    assert isinstance(source.search_tool, ArxivSearchTool)
    assert isinstance(source.metadata_tool, ArxivMetadataTool)


def test_web_search_tool_reads_config_options() -> None:
    tool = build_arxiv_web_search_tool(
        {"web_min_interval_seconds": 4, "web_timeout_seconds": 90, "web_page_size": 10}
    )

    assert tool._session._min_interval == 4
    assert tool._session._client.timeout.connect == 90
    assert tool._page_size == 10


def test_researcher_example_config_carries_the_switch() -> None:
    config = json.loads(
        Path(
            "backend/src/novelty_agent_framework/config/agents/researcher.example.json"
        ).read_text(encoding="utf-8")
    )
    arxiv = config["tools"]["database_search"]["providers"]["arxiv"]

    assert arxiv["search_transport"] in SEARCH_TRANSPORTS
    assert arxiv["enabled"] is True
    assert arxiv["web_min_interval_seconds"] > 0
    assert arxiv["web_timeout_seconds"] >= 30


def test_legacy_retrieval_config_inherits_provider_transport() -> None:
    """legacy 路径过去只认 tools.arxiv；provider 段的开关必须能带到检索来源。"""

    from novelty_agent_framework.config.factory import _normalized_retrieval_config

    raw = {
        "workflow": {"max_concurrency": 4},
        "researcher": {
            "tools": {
                "database_search": {
                    "providers": {
                        "arxiv": {
                            "enabled": True,
                            "search_transport": "web",
                            "web_timeout_seconds": 45,
                            "min_interval_seconds": 6,
                            "timeout_seconds": 20,
                        }
                    }
                }
            }
        },
    }
    source = _normalized_retrieval_config(raw)["sources"]["arxiv"]

    assert source["search_transport"] == "web"
    assert source["web_timeout_seconds"] == 45


def test_legacy_retrieval_config_defaults_to_api() -> None:
    from novelty_agent_framework.config.factory import _normalized_retrieval_config

    source = _normalized_retrieval_config({"workflow": {}})["sources"]["arxiv"]

    assert source["search_transport"] == "api"


def test_arp_web_tool_feeds_structured_retrieval_contract() -> None:
    """检索链按鸭子类型调用 search(query, limit=...)；返回值必须是 SearchHit。"""

    from novelty_agent_framework.ports import SearchHit

    html = _fixture(SEARCH_FIXTURE)
    tool = _search_tool(lambda request: httpx.Response(200, text=html))
    hits = tool.search('ti:"graph neural network"', limit=2)

    assert len(hits) == 2
    assert all(isinstance(hit, SearchHit) for hit in hits)
    assert ARXIV_WEB_ADVANCED_URL.endswith("/search/advanced")
