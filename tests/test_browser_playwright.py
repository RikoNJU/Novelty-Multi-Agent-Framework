"""Local Playwright backend behavior without live network navigation."""

from __future__ import annotations

import asyncio

import pytest

from novelty_agent_framework.tools import PlaywrightBrowserBackend
from novelty_agent_framework.tools.browser_backend import _validate_public_url


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "data:text/plain,no",
        "javascript:alert(1)",
        "ftp://example.com/file",
        "http://localhost/test",
        "http://sub.localhost/test",
        "http://127.0.0.1/test",
        "http://[::1]/test",
        "http://10.0.0.1/test",
        "http://172.16.0.1/test",
        "http://192.168.1.1/test",
        "http://169.254.169.254/latest/meta-data",
        "https://user:password@example.com/",
    ],
)
def test_rejects_unsafe_urls(url) -> None:
    with pytest.raises(ValueError):
        _validate_public_url(url)


def test_accepts_public_http_urls() -> None:
    assert _validate_public_url("https://example.com/page") == (
        "https://example.com/page"
    )
    assert _validate_public_url("http://93.184.216.34/") == (
        "http://93.184.216.34/"
    )


def test_configuration_requires_positive_limits() -> None:
    with pytest.raises(ValueError, match="navigation_timeout"):
        PlaywrightBrowserBackend(navigation_timeout_ms=0)
    with pytest.raises(ValueError, match="content limits"):
        PlaywrightBrowserBackend(max_text_chars=0)


class _Response:
    status = 200

    async def all_headers(self):
        return {"content-type": "text/html; charset=utf-8"}


class _Body:
    async def inner_text(self, *, timeout):
        return "rendered body is deliberately long"


class _Page:
    url = "https://example.com/final"

    def set_default_navigation_timeout(self, timeout):
        self.default_timeout = timeout

    async def goto(self, url, *, wait_until, timeout):
        self.goto_call = (url, wait_until, timeout)
        return _Response()

    async def title(self):
        return " Rendered Title "

    async def content(self):
        return "<html><body>rendered body is deliberately long</body></html>"

    def locator(self, selector):
        assert selector == "body"
        return _Body()


class _Context:
    def __init__(self):
        self.page = _Page()
        self.closed = False

    async def new_page(self):
        return self.page

    async def close(self):
        self.closed = True


class _Browser:
    def __init__(self):
        self.context = _Context()
        self.closed = False

    async def new_context(self):
        return self.context

    async def close(self):
        self.closed = True


class _Chromium:
    def __init__(self):
        self.browser = _Browser()

    async def launch(self, *, headless):
        assert headless is True
        return self.browser


class _Playwright:
    def __init__(self):
        self.chromium = _Chromium()


class _Manager:
    def __init__(self):
        self.playwright = _Playwright()

    async def __aenter__(self):
        return self.playwright

    async def __aexit__(self, *args):
        return None


def test_fetch_collects_rendered_content_and_applies_limits(monkeypatch) -> None:
    manager = _Manager()
    monkeypatch.setattr(
        "novelty_agent_framework.tools.browser_backend._load_async_playwright",
        lambda: lambda: manager,
    )
    backend = PlaywrightBrowserBackend(max_html_chars=20, max_text_chars=13)

    result = asyncio.run(backend.fetch("https://example.com/requested"))

    assert result.requested_url == "https://example.com/requested"
    assert result.final_url == "https://example.com/final"
    assert result.title == "Rendered Title"
    assert len(result.html) == 20
    assert result.text == "rendered body"
    assert result.content_type == "text/html; charset=utf-8"
    assert len(result.warnings) == 2
    browser = manager.playwright.chromium.browser
    assert browser.context.closed and browser.closed
