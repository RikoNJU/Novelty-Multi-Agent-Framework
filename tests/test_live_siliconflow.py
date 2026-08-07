"""调用硅基流动真实模型的集成测试。

默认跳过；显式执行：
    pytest -m live tests/test_live_siliconflow.py -s
需要本机存在 SILICONFLOW_API_KEY（backend/.env 或环境变量）。
"""

from __future__ import annotations

import os

import pytest

from backend.env import (
    ChatMessage,
    ModelCallOptions,
    ModelProfile,
    OpenAICompatibleChatClient,
)

pytestmark = pytest.mark.live

MODEL_NAME = "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"
BASE_URL = "https://api.siliconflow.cn/v1"


@pytest.mark.skipif(
    not os.getenv("SILICONFLOW_API_KEY"),
    reason="需要 SILICONFLOW_API_KEY（backend/.env 或环境变量）",
)
def test_siliconflow_deepseek_hello() -> None:
    profile = ModelProfile(
        alias="deepseek-r1-qwen3-8b",
        model=MODEL_NAME,
        base_url=BASE_URL,
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        supported_params=frozenset({"enable_thinking", "thinking_budget"}),
        defaults={"temperature": 0.7, "timeout_seconds": 120.0},
    )
    client = OpenAICompatibleChatClient(profile)

    response = client.complete(
        [ChatMessage(role="user", content="你好")],
        options=ModelCallOptions(temperature=0.7),
    )

    print(f"\n模型回复：{response.content}")
    print(f"响应模型：{response.raw.get('model')}")
    print(f"用量：{response.usage}")
    assert response.content.strip(), "模型返回内容为空"
