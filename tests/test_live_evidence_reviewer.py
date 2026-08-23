"""证据 Reviewer 真实模型测试（live）。

默认跳过；通过 ``pytest -m live`` 显式运行。使用仓库内人工构造的小型
EvidenceCard，不依赖真实网页访问。

运行方式：
    pytest -m live tests/test_live_evidence_reviewer.py -s
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import pytest

from backend.env import ModelRegistry, ModelProfile, PromptLibrary
from novelty_agent_framework.agents import (
    EvidenceReviewerConfig,
    NoveltyEvidenceReviewer,
)
from novelty_agent_framework.schemas import (
    EvidenceCard,
    EvidenceSource,
    NoveltyPoint,
    ResearchTask,
    ReviewVerdict,
)

pytestmark = pytest.mark.live

PROMPTS_ROOT = Path("backend/src/novelty_agent_framework/prompts")


def _build_registry() -> ModelRegistry:
    """从环境变量构建 ModelRegistry，要求 SILICONFLOW_API_KEY。"""

    import os

    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        pytest.skip("未设置 SILICONFLOW_API_KEY，跳过 live Reviewer 测试")

    profile = ModelProfile(
        alias="reviewer",
        provider="openai_compatible",
        model="deepseek-ai/DeepSeek-V4-Flash",
        base_url="https://api.siliconflow.cn/v1",
        api_key=api_key,
        context_window=128_000,
        supported_params=frozenset({"enable_thinking", "reasoning_effort"}),
        defaults={"temperature": 0.0, "max_tokens": 4096},
    )
    return ModelRegistry({"reviewer": profile})


def _make_inputs() -> tuple[Sequence[EvidenceCard], NoveltyPoint, ResearchTask]:
    point = NoveltyPoint(
        point_id="NP-1",
        claim="提出一种基于图摘要的时序图表示学习方法",
        technical_features=["图摘要压缩", "循环神经网络时序建模"],
        source_locations=["abstract"],
    )
    task = ResearchTask(
        task_id="T-1",
        novelty_point_id="NP-1",
        task_type="literature_search",
        language="zh",
        description="针对该查新点执行文献检索",
        attempt=1,
    )

    # 一张明显夸大的卡：quote 是图像分类，main_contribution 却写自动驾驶
    bad_card = EvidenceCard(
        card_id="C-BAD",
        task_id="T-1",
        novelty_point_id="NP-1",
        document_title="Image Classification Paper",
        main_contribution="该文献实现了端到端自动驾驶系统",
        overlaps=["与目标论文共享 Transformer 架构"],
        differences=["适用范围完全不同"],
        sources=[
            EvidenceSource(
                title="Image Classification Paper",
                quote="本文研究了图像分类任务的迁移学习方法",
                location="abstract",
                url="https://example.test/bad",
            )
        ],
        relevance=0.95,
        confidence=0.95,
    )
    # 一张合法卡：quote 与贡献一致
    good_card = EvidenceCard(
        card_id="C-GOOD",
        task_id="T-1",
        novelty_point_id="NP-1",
        document_title="Graph Summarization Paper",
        main_contribution="候选文献提出了基于图摘要的图压缩方法",
        overlaps=["图摘要压缩技术存在重合"],
        differences=["时序建模部分不同"],
        sources=[
            EvidenceSource(
                title="Graph Summarization Paper",
                quote="本文提出一种基于图摘要的图压缩方法",
                location="Section 3, paragraph 1",
                url="https://example.test/good",
            )
        ],
        relevance=0.85,
        confidence=0.85,
    )
    return [bad_card, good_card], point, task


def test_live_reviewer_returns_valid_schema() -> None:
    registry = _build_registry()
    reviewer = NoveltyEvidenceReviewer(
        prompts=PromptLibrary(PROMPTS_ROOT),
        models=registry,
        config=EvidenceReviewerConfig(enabled=True, model_alias="reviewer"),
    )
    cards, point, task = _make_inputs()

    result = reviewer.review(cards, points=[point], tasks=[task])

    # 验证：每张卡都有决定，card_id 都在输入里
    assert len(result.decisions) == 2
    valid_ids = {"C-BAD", "C-GOOD"}
    assert {d.card_id for d in result.decisions} <= valid_ids
    # reviewed_confidence 在 [0, 1]
    for decision in result.decisions:
        assert 0.0 <= decision.reviewed_confidence <= 1.0
        assert decision.verdict in (
            ReviewVerdict.ACCEPT,
            ReviewVerdict.REJECT,
            ReviewVerdict.NEEDS_MORE_EVIDENCE,
        )


def test_live_reviewer_rejects_unsupported_evidence() -> None:
    """明显缺乏支撑的证据应被拒绝或标记 needs_more。"""

    registry = _build_registry()
    reviewer = NoveltyEvidenceReviewer(
        prompts=PromptLibrary(PROMPTS_ROOT),
        models=registry,
        config=EvidenceReviewerConfig(enabled=True, model_alias="reviewer"),
    )
    cards, point, task = _make_inputs()

    result = reviewer.review(cards, points=[point], tasks=[task])

    bad_decision = next(
        (d for d in result.decisions if d.card_id == "C-BAD"), None
    )
    assert bad_decision is not None
    # C-BAD quote 与 main_contribution 明显不一致，应被拒绝或标记需要更多证据
    assert bad_decision.verdict in (
        ReviewVerdict.REJECT,
        ReviewVerdict.NEEDS_MORE_EVIDENCE,
    )
    if bad_decision.issues:
        codes = {issue.code for issue in bad_decision.issues}
        # 至少有一个相关的问题代码
        assert codes & {
            "unsupported_main_contribution",
            "quote_not_supporting_claim",
            "abstract_only_overclaim",
            "scope_overstatement",
            "confidence_overstated",
        }


def test_live_reviewer_does_not_fabricate_dois() -> None:
    """Reviewer 输出的 decisions 不应包含新的 DOI/URL/quote 字段。"""

    registry = _build_registry()
    reviewer = NoveltyEvidenceReviewer(
        prompts=PromptLibrary(PROMPTS_ROOT),
        models=registry,
        config=EvidenceReviewerConfig(enabled=True, model_alias="reviewer"),
    )
    cards, point, task = _make_inputs()

    result = reviewer.review(cards, points=[point], tasks=[task])

    for decision in result.decisions:
        # EvidenceReviewDecision 严格 schema 没有 sources/doi/url/quote 字段
        dumped = decision.model_dump(mode="json")
        forbidden = {"sources", "doi", "url", "quote", "location", "page"}
        assert not (set(dumped.keys()) & forbidden)
