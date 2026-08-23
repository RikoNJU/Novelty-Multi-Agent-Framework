"""证据 Reviewer 离线单元测试。

使用 Fake Model / Mock Client，不访问真实网络，不消耗 Token。
覆盖 Evidence_Reviewer.md 列出的离线测试场景。
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.env import ModelResponse, PromptLibrary
from novelty_agent_framework.agents import (
    DemoEvidenceReviewer,
    EvidenceReviewerConfig,
    NoveltyEvidenceReviewer,
)
from novelty_agent_framework.schemas import (
    EvidenceCard,
    EvidenceReviewDecision,
    EvidenceReviewIssue,
    EvidenceSource,
    IssueSeverity,
    NoveltyPoint,
    ResearchTask,
    ReviewVerdict,
)

PROMPTS_ROOT = Path("backend/src/novelty_agent_framework/prompts")


# ---------------------------------------------------------------------------
# 测试夹具
# ---------------------------------------------------------------------------


def make_point(point_id: str = "NP-1") -> NoveltyPoint:
    return NoveltyPoint(
        point_id=point_id,
        claim="提出一种基于图摘要的时序图表示学习方法",
        technical_features=["图摘要压缩", "循环神经网络时序建模"],
        source_locations=["abstract"],
    )


def make_task(
    task_id: str = "T-1",
    point_id: str = "NP-1",
    language: str = "zh",
) -> ResearchTask:
    return ResearchTask(
        task_id=task_id,
        novelty_point_id=point_id,
        task_type="literature_search",
        language=language,
        description="针对该查新点执行文献检索",
        attempt=1,
    )


def make_card(
    card_id: str = "C1",
    *,
    task_id: str = "T-1",
    point_id: str = "NP-1",
    main_contribution: str = "候选文献提出了基于图摘要的图压缩方法",
    overlaps: list[str] | None = None,
    differences: list[str] | None = None,
    quote: str | None = "本文提出一种基于图摘要的图压缩方法",
    confidence: float = 0.85,
    relevance: float = 0.8,
) -> EvidenceCard:
    return EvidenceCard(
        card_id=card_id,
        task_id=task_id,
        novelty_point_id=point_id,
        document_title="Related Work",
        main_contribution=main_contribution,
        overlaps=overlaps if overlaps is not None else ["图摘要压缩技术存在重合"],
        differences=differences if differences is not None else ["适用范围不同"],
        sources=[
            EvidenceSource(
                title="Related Work",
                quote=quote,
                location="Section 3, paragraph 1",
                url="https://example.test/c1",
            )
        ],
        relevance=relevance,
        confidence=confidence,
    )


class ScriptedClient:
    """按调用顺序返回预设 JSON 的假模型客户端。"""

    def __init__(self, outputs: Sequence[str]) -> None:
        self.outputs = list(outputs)
        self.calls: list = []

    def complete(self, messages, *, options=None):  # type: ignore[no-untyped-def]
        self.calls.append((list(messages), options))
        index = min(len(self.calls) - 1, len(self.outputs) - 1)
        return ModelResponse(content=self.outputs[index])


def make_reviewer(
    client: ScriptedClient,
    *,
    config: EvidenceReviewerConfig | None = None,
) -> NoveltyEvidenceReviewer:
    return NoveltyEvidenceReviewer(
        model_client=client,
        prompts=PromptLibrary(PROMPTS_ROOT),
        config=config or EvidenceReviewerConfig(enabled=True),
    )


def accept_decision(card_id: str, confidence: float = 0.85) -> dict:
    return {
        "card_id": card_id,
        "verdict": "accept",
        "issues": [],
        "reviewed_confidence": confidence,
    }


def reject_decision(
    card_id: str, code: str, message: str, field: str | None = None
) -> dict:
    return {
        "card_id": card_id,
        "verdict": "reject",
        "issues": [
            {
                "code": code,
                "message": message,
                "severity": "warning",
                "field": field,
                "source_index": None,
            }
        ],
        "reviewed_confidence": 0.2,
    }


def needs_more_decision(card_id: str, message: str = "证据不足以判断") -> dict:
    return {
        "card_id": card_id,
        "verdict": "needs_more_evidence",
        "issues": [
            {
                "code": "missing_evidence_detail",
                "message": message,
                "severity": "warning",
            }
        ],
        "reviewed_confidence": 0.3,
    }


# ---------------------------------------------------------------------------
# 1. 合法 Evidence Card 通过审查
# ---------------------------------------------------------------------------


def test_valid_card_passes_review() -> None:
    card = make_card()
    client = ScriptedClient(
        [json.dumps({"decisions": [accept_decision("C1", 0.85)]})]
    )
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    assert [c.card_id for c in result.accepted] == ["C1"]
    assert result.rejected == ()
    assert result.needs_more == ()
    assert len(result.decisions) == 1
    assert result.decisions[0].verdict is ReviewVerdict.ACCEPT


# ---------------------------------------------------------------------------
# 2. card_id 不存在时拒绝 Reviewer 输出（防幻觉）
# ---------------------------------------------------------------------------


def test_decision_with_unknown_card_id_is_dropped() -> None:
    card = make_card(card_id="C1")
    client = ScriptedClient(
        [
            json.dumps(
                {
                    "decisions": [
                        accept_decision("C1", 0.9),
                        accept_decision("HALLUCINATED", 0.99),  # 不在输入里
                    ]
                }
            )
        ]
    )
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    # 幻觉决定被丢弃，C1 仍按其决定 accept
    assert [d.card_id for d in result.decisions] == ["C1"]
    assert [c.card_id for c in result.accepted] == ["C1"]


# ---------------------------------------------------------------------------
# 3. Reviewer 返回额外字段时 Schema 校验失败（extra=forbid）
# ---------------------------------------------------------------------------


def test_extra_field_in_decision_is_rejected() -> None:
    card = make_card(card_id="C1")
    bad_decision = accept_decision("C1", 0.9)
    bad_decision["modified_main_contribution"] = "Reviewer 想改写贡献"  # 额外字段
    client = ScriptedClient([json.dumps({"decisions": [bad_decision]})])

    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    # 非法 decision 被丢弃；卡片无决定，按 fail_closed 默认拒绝
    assert result.decisions == ()
    assert [c.card_id for c in result.accepted] == []
    assert result.rejected == (("C1", "review_missing_decision"),)


# ---------------------------------------------------------------------------
# 4. Reviewer 尝试修改 Evidence Card 时不被采纳
# ---------------------------------------------------------------------------


def test_reviewer_cannot_modify_evidence_card() -> None:
    original = make_card(card_id="C1", main_contribution="原始贡献描述")
    # 模型尝试塞入修改后的 card 字段（应被 extra=forbid 拒绝）
    bad_decision = accept_decision("C1", 0.9)
    bad_decision["main_contribution"] = "Reviewer 改写的贡献"
    client = ScriptedClient([json.dumps({"decisions": [bad_decision]})])

    result = make_reviewer(client).review(
        [original], points=[make_point()], tasks=[make_task()]
    )

    # accept 时原样透传，main_contribution 不变
    assert len(result.accepted) == 0  # 因为 decision 被丢弃，fail_closed 拒绝
    # 改成 fail_open 验证原样透传
    client2 = ScriptedClient([json.dumps({"decisions": [bad_decision]})])
    reviewer = make_reviewer(
        client2, config=EvidenceReviewerConfig(enabled=True, fail_closed=False)
    )
    result2 = reviewer.review(
        [original], points=[make_point()], tasks=[make_task()]
    )
    # fail_open 模式下非法 decision 仍被丢弃，但卡片无决定时进入 accepted
    assert [c.card_id for c in result2.accepted] == ["C1"]
    assert result2.accepted[0].main_contribution == "原始贡献描述"


# ---------------------------------------------------------------------------
# 5. main contribution 缺乏支撑
# ---------------------------------------------------------------------------


def test_unsupported_main_contribution_is_rejected() -> None:
    card = make_card(main_contribution="该文献实现了端到端自动驾驶")
    client = ScriptedClient(
        [
            json.dumps(
                {
                    "decisions": [
                        reject_decision(
                            "C1",
                            "unsupported_main_contribution",
                            "quote 仅描述图压缩，未提及自动驾驶",
                            "main_contribution",
                        )
                    ]
                }
            )
        ]
    )
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    assert result.accepted == ()
    assert result.rejected[0][0] == "C1"
    assert "unsupported_main_contribution" in result.rejected[0][1]


# ---------------------------------------------------------------------------
# 6. overlap 缺乏支撑
# ---------------------------------------------------------------------------


def test_unsupported_overlap_is_rejected() -> None:
    card = make_card(overlaps=["与目标论文共享 Transformer 架构"])
    client = ScriptedClient(
        [
            json.dumps(
                {
                    "decisions": [
                        reject_decision(
                            "C1",
                            "unsupported_overlap",
                            "quote 未提及 Transformer",
                            "overlaps[0]",
                        )
                    ]
                }
            )
        ]
    )
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    assert result.rejected[0][0] == "C1"
    assert "unsupported_overlap" in result.rejected[0][1]


# ---------------------------------------------------------------------------
# 7. difference 缺乏支撑
# ---------------------------------------------------------------------------


def test_unsupported_difference_is_rejected() -> None:
    card = make_card(differences=["适用范围完全不同"])
    client = ScriptedClient(
        [
            json.dumps(
                {
                    "decisions": [
                        reject_decision(
                            "C1",
                            "unsupported_difference",
                            "quote 未说明适用范围差异",
                            "differences[0]",
                        )
                    ]
                }
            )
        ]
    )
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    assert result.rejected[0][0] == "C1"
    assert "unsupported_difference" in result.rejected[0][1]


# ---------------------------------------------------------------------------
# 8. 引文与判断不一致
# ---------------------------------------------------------------------------


def test_quote_not_supporting_claim_is_rejected() -> None:
    card = make_card(
        main_contribution="文献实现了端到端自动驾驶",
        quote="本文研究了图像分类任务",
    )
    client = ScriptedClient(
        [
            json.dumps(
                {
                    "decisions": [
                        reject_decision(
                            "C1",
                            "quote_not_supporting_claim",
                            "quote 描述图像分类，与自动驾驶结论无关",
                            "sources[0].quote",
                        )
                    ]
                }
            )
        ]
    )
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    assert result.rejected[0][0] == "C1"
    assert "quote_not_supporting_claim" in result.rejected[0][1]


# ---------------------------------------------------------------------------
# 9. 摘要证据被夸大成全文结论
# ---------------------------------------------------------------------------


def test_abstract_only_overclaim_is_rejected() -> None:
    card = make_card(main_contribution="全文实验证明该方法优于所有基线")
    client = ScriptedClient(
        [
            json.dumps(
                {
                    "decisions": [
                        reject_decision(
                            "C1",
                            "abstract_only_overclaim",
                            "仅摘要级证据，不能下全文级实验结论",
                            "main_contribution",
                        )
                    ]
                }
            )
        ]
    )
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    assert "abstract_only_overclaim" in result.rejected[0][1]


# ---------------------------------------------------------------------------
# 10. 查新点与 Evidence Card 不一致
# ---------------------------------------------------------------------------


def test_novelty_point_mismatch_is_rejected() -> None:
    card = make_card(point_id="NP-1")
    # 模型识别到卡片语义和查新点不符
    client = ScriptedClient(
        [
            json.dumps(
                {
                    "decisions": [
                        reject_decision(
                            "C1",
                            "novelty_point_mismatch",
                            "卡片描述的是图像分类，与图摘要时序建模无关",
                            "novelty_point_id",
                        )
                    ]
                }
            )
        ]
    )
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    assert "novelty_point_mismatch" in result.rejected[0][1]


# ---------------------------------------------------------------------------
# 11. task 绑定错误
# ---------------------------------------------------------------------------


def test_task_mismatch_is_rejected() -> None:
    card = make_card(task_id="T-1")
    client = ScriptedClient(
        [
            json.dumps(
                {
                    "decisions": [
                        reject_decision(
                            "C1",
                            "task_mismatch",
                            "卡片语义与 T-1 任务目标不一致",
                            "task_id",
                        )
                    ]
                }
            )
        ]
    )
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    assert "task_mismatch" in result.rejected[0][1]


# ---------------------------------------------------------------------------
# 12. confidence 明显虚高
# ---------------------------------------------------------------------------


def test_confidence_overstated_is_flagged() -> None:
    card = make_card(confidence=0.95)
    # Reviewer 仍 accept 但标记 confidence_overstated
    decision = accept_decision("C1", 0.4)
    decision["issues"] = [
        {
            "code": "confidence_overstated",
            "message": "quote 支撑弱，0.95 明显虚高",
            "severity": "warning",
            "field": "confidence",
        }
    ]
    client = ScriptedClient([json.dumps({"decisions": [decision]})])
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    # accept 但 issues 里有 confidence_overstated；原 confidence 未被覆盖
    assert [c.card_id for c in result.accepted] == ["C1"]
    assert result.decisions[0].reviewed_confidence == 0.4
    assert result.accepted[0].confidence == 0.95  # 原始字段不动


# ---------------------------------------------------------------------------
# 13. Reviewer 返回 needs_more_evidence
# ---------------------------------------------------------------------------


def test_needs_more_evidence_is_captured() -> None:
    card = make_card()
    client = ScriptedClient(
        [json.dumps({"decisions": [needs_more_decision("C1")]})]
    )
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    assert result.accepted == ()
    assert result.rejected == ()
    assert result.needs_more == ("C1",)
    assert result.decisions[0].verdict is ReviewVerdict.NEEDS_MORE_EVIDENCE


# ---------------------------------------------------------------------------
# 14. 单张卡片审查失败不导致全流程崩溃
# ---------------------------------------------------------------------------


def test_single_batch_failure_does_not_crash_others() -> None:
    # 第一批触发异常（非 JSON），第二批正常
    cards = [make_card(card_id=f"C{i}") for i in range(1, 3)]
    client = ScriptedClient(
        [
            "not-json",
            json.dumps({"decisions": [accept_decision("C2", 0.8)]}),
        ]
    )
    # max_cards_per_call=1 让每张卡独立成批
    reviewer = make_reviewer(
        client,
        config=EvidenceReviewerConfig(
            enabled=True, max_cards_per_call=1, fail_closed=False
        ),
    )
    result = reviewer.review(
        cards, points=[make_point()], tasks=[make_task()]
    )

    # C1 批失败，fail_open 模式下进入 accepted（无决定）
    # C2 正常 accept
    assert {c.card_id for c in result.accepted} == {"C1", "C2"}


def test_single_batch_failure_fail_closed_rejects() -> None:
    cards = [make_card(card_id=f"C{i}") for i in range(1, 3)]
    client = ScriptedClient(
        [
            "not-json",
            json.dumps({"decisions": [accept_decision("C2", 0.8)]}),
        ]
    )
    reviewer = make_reviewer(
        client,
        config=EvidenceReviewerConfig(
            enabled=True, max_cards_per_call=1, fail_closed=True
        ),
    )
    result = reviewer.review(
        cards, points=[make_point()], tasks=[make_task()]
    )

    assert [c.card_id for c in result.accepted] == ["C2"]
    assert result.rejected[0][0] == "C1"


# ---------------------------------------------------------------------------
# 15. Reviewer 禁用时维持兼容行为
# ---------------------------------------------------------------------------


def test_demo_reviewer_accepts_all() -> None:
    cards = [make_card(card_id="C1"), make_card(card_id="C2")]
    result = DemoEvidenceReviewer().review(
        cards, points=[make_point()], tasks=[make_task()]
    )

    assert [c.card_id for c in result.accepted] == ["C1", "C2"]
    assert result.rejected == ()
    assert result.needs_more == ()
    # Demo 给每张卡都生成 ACCEPT decision
    assert [d.verdict for d in result.decisions] == [
        ReviewVerdict.ACCEPT,
        ReviewVerdict.ACCEPT,
    ]


def test_empty_cards_returns_empty_result() -> None:
    result = DemoEvidenceReviewer().review(
        [], points=[make_point()], tasks=[make_task()]
    )
    assert result.accepted == ()
    assert result.decisions == ()


# ---------------------------------------------------------------------------
# 16. fail-closed 与 fail-open 配置行为
# ---------------------------------------------------------------------------


def test_fail_closed_rejects_missing_decision() -> None:
    # 模型只返回 C1 的决定，C2 缺失
    card1 = make_card(card_id="C1")
    card2 = make_card(card_id="C2")
    client = ScriptedClient(
        [json.dumps({"decisions": [accept_decision("C1", 0.8)]})]
    )
    reviewer = make_reviewer(
        client,
        config=EvidenceReviewerConfig(enabled=True, fail_closed=True),
    )
    result = reviewer.review(
        [card1, card2], points=[make_point()], tasks=[make_task()]
    )

    assert [c.card_id for c in result.accepted] == ["C1"]
    assert result.rejected[0] == ("C2", "review_missing_decision")


def test_fail_open_accepts_missing_decision() -> None:
    card1 = make_card(card_id="C1")
    card2 = make_card(card_id="C2")
    client = ScriptedClient(
        [json.dumps({"decisions": [accept_decision("C1", 0.8)]})]
    )
    reviewer = make_reviewer(
        client,
        config=EvidenceReviewerConfig(enabled=True, fail_closed=False),
    )
    result = reviewer.review(
        [card1, card2], points=[make_point()], tasks=[make_task()]
    )

    assert {c.card_id for c in result.accepted} == {"C1", "C2"}


# ---------------------------------------------------------------------------
# 17. 确定性 Validator 拒绝的卡片不调用 LLM
#   （由工作流层保证，这里验证 Reviewer 接口本身只看输入的卡）
# ---------------------------------------------------------------------------


def test_reviewer_only_processes_input_cards() -> None:
    # Validator 已拒绝的卡不会出现在输入里，Reviewer 自然不会处理
    accepted_card = make_card(card_id="C1")
    client = ScriptedClient(
        [json.dumps({"decisions": [accept_decision("C1", 0.8)]})]
    )
    reviewer = make_reviewer(client)
    result = reviewer.review(
        [accepted_card], points=[make_point()], tasks=[make_task()]
    )

    assert len(client.calls) == 1  # 只调用一次 LLM
    assert [c.card_id for c in result.accepted] == ["C1"]


# ---------------------------------------------------------------------------
# 18. 审查结果写入 evidence-cards.json（持久化层覆盖在 test_persistence）
#   这里只验证 ReviewResult 携带的 decisions 可序列化
# ---------------------------------------------------------------------------


def test_decisions_are_serializable() -> None:
    card = make_card()
    client = ScriptedClient(
        [json.dumps({"decisions": [accept_decision("C1", 0.85)]})]
    )
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    serialized = json.dumps(
        [d.model_dump(mode="json") for d in result.decisions],
        ensure_ascii=False,
    )
    assert "C1" in serialized
    assert "accept" in serialized


# ---------------------------------------------------------------------------
# 19. Coordinator 只接收最终通过的证据
#   （工作流层覆盖，这里验证 ReviewResult.accepted 即为透传后的卡）
# ---------------------------------------------------------------------------


def test_accepted_cards_are_original_objects() -> None:
    original = make_card(card_id="C1", main_contribution="原始贡献")
    client = ScriptedClient(
        [json.dumps({"decisions": [accept_decision("C1", 0.85)]})]
    )
    result = make_reviewer(client).review(
        [original], points=[make_point()], tasks=[make_task()]
    )

    assert result.accepted[0] is original  # 原对象透传，未被复制或修改


# ---------------------------------------------------------------------------
# 20. 严格 Schema 校验：reviewed_confidence 超范围
# ---------------------------------------------------------------------------


def test_reviewed_confidence_out_of_range_is_dropped() -> None:
    card = make_card()
    bad = accept_decision("C1", 0.85)
    bad["reviewed_confidence"] = 1.5  # 超出 [0, 1]
    client = ScriptedClient([json.dumps({"decisions": [bad]})])
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    # 非法 decision 被丢弃，fail_closed 拒绝
    assert result.accepted == ()
    assert result.rejected[0] == ("C1", "review_missing_decision")


def test_unknown_issue_code_is_replaced() -> None:
    """模型返回未知 issue.code 时替换为 missing_evidence_detail，不丢弃整个决定。"""

    card = make_card()
    decision = accept_decision("C1", 0.85)
    decision["issues"] = [
        {
            "code": "made_up_code",  # 不在白名单
            "message": "随便说点",
            "severity": "warning",
        }
    ]
    client = ScriptedClient([json.dumps({"decisions": [decision]})])
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    assert [c.card_id for c in result.accepted] == ["C1"]
    assert result.decisions[0].issues[0].code == "missing_evidence_detail"


def test_config_validates_temperature() -> None:
    with pytest.raises(ValueError, match="temperature"):
        EvidenceReviewerConfig(enabled=True, temperature=3.0)


def test_config_validates_max_cards() -> None:
    with pytest.raises(ValueError, match="max_cards_per_call"):
        EvidenceReviewerConfig(enabled=True, max_cards_per_call=0)


def test_reviewer_without_client_raises() -> None:
    reviewer = NoveltyEvidenceReviewer(
        config=EvidenceReviewerConfig(enabled=True)
    )
    with pytest.raises(NotImplementedError, match="ModelClient"):
        reviewer.review(
            [make_card()], points=[make_point()], tasks=[make_task()]
        )


def test_reviewer_handles_list_response_without_wrapper() -> None:
    """模型直接返回 list 而非 {"decisions": [...]} 时也能解析。"""

    card = make_card()
    client = ScriptedClient([json.dumps([accept_decision("C1", 0.85)])])
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    assert [c.card_id for c in result.accepted] == ["C1"]


def test_reviewer_does_not_generate_new_dois() -> None:
    """Reviewer 输出 schema 不包含 sources 字段，无法塞入新 DOI/URL。"""

    card = make_card()
    decision = accept_decision("C1", 0.85)
    decision["sources"] = [  # 尝试塞入新引用
        {
            "title": "Fabricated Paper",
            "doi": "10.9999/fabricated",
            "url": "https://example.test/fake",
        }
    ]
    client = ScriptedClient([json.dumps({"decisions": [decision]})])
    result = make_reviewer(client).review(
        [card], points=[make_point()], tasks=[make_task()]
    )

    # extra=forbid 拒绝 sources 字段，整个 decision 被丢弃
    assert result.decisions == ()
    # 原 card 的 sources 不变
    if result.accepted:
        assert result.accepted[0].sources[0].doi is None
