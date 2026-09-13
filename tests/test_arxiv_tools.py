"""arXiv 三工具的离线单测（httpx MockTransport，不联网）。"""

from __future__ import annotations

import httpx
import pymupdf
import pytest

from novelty_agent_framework.tools.database_search.providers import arxiv as arxiv_module
from novelty_agent_framework.tools.database_search.providers.arxiv import (
    ArxivFullTextTool,
    ArxivMetadataTool,
    ArxivSearchTool,
)


@pytest.fixture(autouse=True)
def _reset_arxiv_throttle(monkeypatch):
    """节流时间戳是模块级共享的，测试之间必须重置，否则会相互影响。"""

    monkeypatch.setattr(arxiv_module, "_LAST_REQUEST_AT", 0.0)

ATOM_ENTRY = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2305.12345v2</id>
    <title>Graph Summarization for Temporal Graph Learning</title>
    <summary>We propose a graph summarization method for dynamic graphs.</summary>
    <published>2023-05-19T00:00:00Z</published>
    <author><name>Alice Zhang</name></author>
    <author><name>Bob Li</name></author>
    <arxiv:doi>10.48550/arXiv.2305.12345</arxiv:doi>
  </entry>
</feed>
"""

HTML_BODY = """<html><head><title>Graph Summarization for Temporal Graph Learning</title></head>
<body><section><p>Paragraph one of the paper.</p><p>Paragraph two with <b>bold</b>.</p></section></body></html>"""


def make_client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def _pdf_bytes() -> bytes:
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Full text from PDF fallback.")
    data = document.tobytes()
    document.close()
    return data


def test_search_parses_atom_and_strips_version():
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        return httpx.Response(200, text=ATOM_ENTRY)

    tool = ArxivSearchTool(client=make_client(handler), min_interval=0.0)
    hits = tool.search('abs:"graph summarization"', limit=5)

    assert len(hits) == 1
    hit = hits[0]
    assert hit.document_id == "2305.12345"
    assert hit.external_id == "2305.12345v2"
    assert hit.source_id == "arxiv"
    assert hit.full_text_url == "https://arxiv.org/pdf/2305.12345"
    assert hit.title == "Graph Summarization for Temporal Graph Learning"
    assert hit.authors == ("Alice Zhang", "Bob Li")
    assert hit.year == 2023
    assert hit.doi == "10.48550/arXiv.2305.12345"
    assert hit.url == "https://arxiv.org/abs/2305.12345"
    assert "search_query=" in seen[0]
    assert "max_results=5" in seen[0]


def test_search_follows_redirects():
    redirected = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        redirected["count"] += 1
        if redirected["count"] == 1:
            return httpx.Response(301, headers={"Location": str(request.url).replace("http://", "https://", 1)})
        return httpx.Response(200, text=ATOM_ENTRY)

    client = httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)
    tool = ArxivSearchTool(client=client, min_interval=0.0)
    hits = tool.search("q")

    assert len(hits) == 1
    assert redirected["count"] == 2


def test_search_throttles_requests(monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr(
        "novelty_agent_framework.tools.database_search.providers.arxiv.time.sleep",
        lambda seconds: sleeps.append(seconds),
    )
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, text=ATOM_ENTRY)

    tool = ArxivSearchTool(client=make_client(handler), min_interval=0.5)
    tool.search("q1")
    tool.search("q2")

    assert calls["n"] == 2
    assert len(sleeps) == 1
    assert sleeps[0] == pytest.approx(0.5, abs=0.25)


def test_search_retries_on_5xx_then_succeeds():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(500)
        return httpx.Response(200, text=ATOM_ENTRY)

    tool = ArxivSearchTool(client=make_client(handler), min_interval=0.0)
    hits = tool.search("q")

    assert calls["n"] == 3
    assert len(hits) == 1


def test_search_retries_on_429_and_honours_retry_after(monkeypatch):
    """429 是限流而非请求错误，必须重试。

    实测线上就是在这里挂的：429 直接抛出，一次检索执行就此失败，
    整篇论文的 arXiv 召回全部落空。
    """

    sleeps: list[float] = []
    monkeypatch.setattr(
        "novelty_agent_framework.tools.database_search.providers.arxiv.time.sleep",
        lambda seconds: sleeps.append(seconds),
    )
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "7"}, text="slow down")
        return httpx.Response(200, text=ATOM_ENTRY)

    tool = ArxivSearchTool(client=make_client(handler), min_interval=0.0, max_retries=2)
    hits = tool.search("q")

    assert calls["n"] == 2
    assert len(hits) == 1
    assert 7.0 in sleeps, "应当遵守 Retry-After"


def test_throttle_is_shared_across_tool_instances(monkeypatch):
    """节流状态是模块级共享的。

    工作流、bootstrap CLI、多来源各自构建 ArxivSearchTool；若各自计时，
    叠加速率就会超过 arXiv 的单来源限制并触发 429。
    """

    sleeps: list[float] = []
    monkeypatch.setattr(
        "novelty_agent_framework.tools.database_search.providers.arxiv.time.sleep",
        lambda seconds: sleeps.append(seconds),
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=ATOM_ENTRY)

    first = ArxivSearchTool(client=make_client(handler), min_interval=5.0)
    second = ArxivSearchTool(client=make_client(handler), min_interval=5.0)
    first.search("q1")
    second.search("q2")

    assert len(sleeps) == 1, "第二个实例必须等待第一个实例让出的间隔"
    assert sleeps[0] == pytest.approx(5.0, abs=0.25)


def test_search_raises_on_4xx_without_retry():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(404)

    tool = ArxivSearchTool(client=make_client(handler), min_interval=0.0)
    with pytest.raises(httpx.HTTPStatusError):
        tool.search("q")
    assert calls["n"] == 1


def test_fulltext_html_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert "/html/" in str(request.url)
        return httpx.Response(200, text=HTML_BODY)

    tool = ArxivFullTextTool(client=make_client(handler))
    result = tool.fetch("2305.12345v2")

    assert result is not None
    assert result.document_id == "2305.12345"
    assert "Paragraph one" in result.text
    assert result.title == "Graph Summarization for Temporal Graph Learning"
    assert result.source.url == "https://arxiv.org/abs/2305.12345"


def test_fulltext_falls_back_to_pdf():
    def handler(request: httpx.Request) -> httpx.Response:
        if "/html/" in str(request.url):
            return httpx.Response(404)
        return httpx.Response(200, content=_pdf_bytes())

    tool = ArxivFullTextTool(client=make_client(handler))
    result = tool.fetch("2305.12345")

    assert result is not None
    assert "PDF fallback" in result.text


def test_fulltext_missing_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    tool = ArxivFullTextTool(client=make_client(handler))
    assert tool.fetch("0000.00000") is None


def test_fulltext_truncates_to_max_chars():
    html = "<html><body>" + "<p>word</p>" * 2000 + "</body></html>"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=html)

    tool = ArxivFullTextTool(client=make_client(handler), max_chars=100)
    result = tool.fetch("2305.12345")

    assert result is not None
    assert len(result.text) <= 100
    assert result.content_extent == "partial"


def test_fulltext_caches_across_versions():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, text=HTML_BODY)

    tool = ArxivFullTextTool(client=make_client(handler))
    tool.fetch("2305.12345")
    tool.fetch("2305.12345v2")

    assert calls["n"] == 1


def test_metadata_resolves_entry():
    def handler(request: httpx.Request) -> httpx.Response:
        assert "id_list=2305.12345" in str(request.url)
        return httpx.Response(200, text=ATOM_ENTRY)

    tool = ArxivMetadataTool(client=make_client(handler))
    source = tool.resolve("2305.12345v2")

    assert source is not None
    assert source.title == "Graph Summarization for Temporal Graph Learning"
    assert source.doi == "10.48550/arXiv.2305.12345"
    assert source.url == "https://arxiv.org/abs/2305.12345"


def test_metadata_missing_returns_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<feed xmlns='http://www.w3.org/2005/Atom'/>")

    tool = ArxivMetadataTool(client=make_client(handler))
    assert tool.resolve("0000.00000") is None
