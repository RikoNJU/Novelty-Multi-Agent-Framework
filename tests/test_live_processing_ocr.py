"""真实 DeepSeek-OCR 冒烟测试（默认跳过，需 -m live）。"""

from __future__ import annotations

import base64
import os
from pathlib import Path

import pymupdf
import pytest

from backend.env import (
    ChatMessage,
    ImageContentPart,
    ModelProfile,
    OpenAICompatibleChatClient,
)
from novelty_agent_framework.processing.textify import OCR_PROMPT

pytestmark = pytest.mark.live

PDF = Path("examples/MF2033k6lC.pdf")


@pytest.mark.skipif(
    not os.getenv("SILICONFLOW_API_KEY"),
    reason="需要 SILICONFLOW_API_KEY（backend/.env 或环境变量）",
)
def test_live_deepseek_ocr_page5() -> None:
    doc = pymupdf.open(PDF)
    try:
        png = doc[4].get_pixmap(dpi=200).tobytes("png")
    finally:
        doc.close()
    data_url = "data:image/png;base64," + base64.b64encode(png).decode("ascii")

    profile = ModelProfile(
        alias="deepseek-ocr",
        model="deepseek-ai/DeepSeek-OCR",
        base_url="https://api.siliconflow.cn/v1",
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        defaults={"timeout_seconds": 180},
    )
    client = OpenAICompatibleChatClient(profile)
    response = client.complete(
        [
            ChatMessage(
                role="user",
                content=[ImageContentPart(image_url=data_url), OCR_PROMPT],
            )
        ]
    )

    assert response.content.strip()
    assert "GSAERU" in response.content or "图表示学习" in response.content
