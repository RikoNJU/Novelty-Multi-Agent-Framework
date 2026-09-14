"""arXiv 限速策略：共享时隙、429 长退避、配置贯通到每条链路。

背景：arXiv 官方要求不超过每 3 秒 1 次请求；实测贴着该上限仍会拿到 429，
而 bootstrap 曾使用构造默认值（比工作流更激进），两条链路叠加更容易被限流。
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

from novelty_agent_framework.tools.database_search.providers.arxiv import (
    DEFAULT_MIN_INTERVAL_SECONDS,
    DEFAULT_RATE_LIMIT_WAIT_SECONDS,
    ArxivMetadataTool,
    build_arxiv_search_tool,
    _wait_for_request_slot,
)

CONFIG_PATH = Path(
    "backend/src/novelty_agent_framework/config/agents/researcher.example.json"
)


def _arxiv_options() -> dict:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return config["tools"]["database_search"]["providers"]["arxiv"]


def test_configured_arxiv_limits_reach_the_tool() -> None:
    options = _arxiv_options()
    tool = build_arxiv_search_tool(options)

    assert tool._min_interval == float(options["min_interval_seconds"])
    assert tool._circuit_failure_threshold == int(
        options["circuit_failure_threshold"]
    )
    assert tool._circuit_cooldown_seconds == float(
        options["circuit_cooldown_seconds"]
    )
    assert tool._rate_limit_wait == float(options["rate_limit_wait_seconds"])


def test_configured_interval_respects_the_code_floor() -> None:
    """配置值不得低于代码下限，否则等于没有留出限流余量。"""

    assert _arxiv_options()["min_interval_seconds"] >= DEFAULT_MIN_INTERVAL_SECONDS


def test_defaults_are_stricter_than_the_documented_three_seconds() -> None:
    tool = build_arxiv_search_tool({})

    assert tool._min_interval >= 5.0
    assert tool._rate_limit_wait >= 30.0


def test_rate_limit_wait_takes_the_longer_of_header_and_floor() -> None:
    tool = build_arxiv_search_tool({"rate_limit_wait_seconds": 30})
    request = httpx.Request("GET", "https://export.arxiv.org/api/query")

    assert tool._rate_limit_wait_for(httpx.Response(429, request=request)) == 30.0
    assert (
        tool._rate_limit_wait_for(
            httpx.Response(
                429, headers={"Retry-After": "120"}, request=request
            )
        )
        == 120.0
    )


def test_request_slot_is_shared_between_instances() -> None:
    """两个实例共用一个模块级时隙，各自计时叠加就会超限。"""

    first = build_arxiv_search_tool({"min_interval_seconds": 0.3})
    second = build_arxiv_search_tool({"min_interval_seconds": 0.3})
    deadline = time.monotonic() + 5.0

    assert _wait_for_request_slot(first._min_interval, deadline=deadline)
    started = time.monotonic()
    assert _wait_for_request_slot(second._min_interval, deadline=deadline)
    assert time.monotonic() - started >= 0.25


def test_metadata_tool_shares_the_same_interval() -> None:
    """元数据核验也打 export API，必须带同一套限速参数。"""

    assert ArxivMetadataTool()._min_interval >= DEFAULT_MIN_INTERVAL_SECONDS
    assert (
        ArxivMetadataTool(min_interval=9.0)._min_interval == 9.0
    )
    assert DEFAULT_RATE_LIMIT_WAIT_SECONDS >= 30.0
