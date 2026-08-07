"""pytest 全局配置：默认跳过需要真实模型/网络的 live 测试。"""

from __future__ import annotations

import os

import pytest


def pytest_collection_modifyitems(config, items) -> None:
    """默认跳过 live 测试，除非显式 ``-m live`` 或设置 ``RUN_LIVE_TESTS=1``。"""

    markexpr = config.getoption("markexpr") or ""
    if "live" in markexpr or os.getenv("RUN_LIVE_TESTS"):
        return
    skip_live = pytest.mark.skip(
        reason="live 测试：需要显式执行 pytest -m live 或设置 RUN_LIVE_TESTS=1"
    )
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
