"""证据 Reviewer 工作流集成测试。

验证 Reviewer 接入工作流后的端到端行为，使用 Fake Model，不消耗 Token。
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import pytest

from novelty_agent_framework.agents import (
    DemoCoordinator,
    DemoEvidenceReviewer,
    DemoPointExtractor,
    DemoQueryAdapter,
    DemoResearchAgent,
    DemoSearchTool,
    NoveltyEvidenceReviewer,
    EvidenceReviewerConfig,
)
from novelty_agent_framework.persistence import persist_evidence_cards
from novelty_agent_framework.ports import EvidenceReviewer, ReviewResult, SearchHit
from novelty_agent_framework.schemas import (
    EvidenceCard,
    EvidenceReviewDecision,
    EvidenceSource,
    NoveltyPoint,
    PaperInput,
    ResearchTask,
    ReviewVerdict,
    WorkflowIssue,
)
from novelty_agent_framework.workflows import (
    NoveltyWorkflow,
    NoveltyWorkflowConfig,
    NoveltyWorkflowServices,
)


@pytest.fixture(autouse=True)
def _isolated_outputs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def make_paper() -> PaperInput:
    return PaperInput(
        paper_id="paper-reviewer-test",
        title="证据驱动论文查新",
        abstract="测试论文摘要",
        full_text="测试论文正文",
        claimed_contributions=["创新声明"],
    )


class StaticResearchAgent:
    """返回固定 EvidenceCard 的 Research Agent。"""

    def __init__(self, cards: Sequence[EvidenceCard]) -> None:
        self._cards = list(cards)

    async def research(
        self,
        task: ResearchTask,
        point: NoveltyPoint,
        candidates: Sequence[SearchHit],
        **_: object,
    ) -> Sequence[EvidenceCard]:
        return list(self._cards)


class ScriptedReviewer:
    """按预设 decisions 返回 ReviewResult 的 Reviewer。"""

    def __init__(self, decisions: Sequence[EvidenceReviewDecision]) -> None:
        self._decisions = list(decisions)
        self.calls: list = []

    def review(
        self,
        cards: Sequence[EvidenceCard],
        *,
        points: Sequence[NoveltyPoint],
        tasks: Sequence[ResearchTask],
    ) -> ReviewResult:
        self.calls.append(list(cards))
        decision_by_id = {d.card_id: d for d in self._decisions}
        accepted: list[EvidenceCard] = []
        rejected: list[tuple[str, str]] = []
        needs_more: list[str] = []

        for card in cards:
            decision = decision_by_id.get(card.card_id)
            if decision is None:
                rejected.append((card.card_id, "review_missing_decision"))
                continue
            if decision.verdict is ReviewVerdict.ACCEPT:
                accepted.append(card)
            elif decision.verdict is ReviewVerdict.REJECT:
                rejected.append((card.card_id, "rejected by reviewer"))
            else:
                needs_more.append(card.card_id)

        return ReviewResult(
            accepted=tuple(accepted),
            rejected=tuple(rejected),
            needs_more=tuple(needs_more),
            decisions=tuple(self._decisions),
        )


def make_card(
    card_id: str = "C1",
    point_id: str = "NP-1",
    document_title: str = "Related Work",
) -> EvidenceCard:
    return EvidenceCard(
        card_id=card_id,
        task_id="T-1",
        novelty_point_id=point_id,
        document_title=document_title,
        main_contribution="候选文献提出了基于图摘要的图压缩方法",
        overlaps=["图摘要压缩技术存在重合"],
        differences=["适用范围不同"],
        sources=[
            EvidenceSource(
                title=document_title,
                quote="本文提出一种基于图摘要的图压缩方法",
                location="Section 3",
                url=f"https://example.test/{card_id.lower()}",
            )
        ],
        relevance=0.85,
        confidence=0.85,
    )


def build_workflow(
    *,
    researcher_cards: Sequence[EvidenceCard],
    reviewer: EvidenceReviewer | None,
) -> NoveltyWorkflow:
    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=DemoCoordinator(),
            research_agent=StaticResearchAgent(researcher_cards),
            search_planner=DemoQueryAdapter(),
            query_adapter=DemoQueryAdapter(),
            point_extractor=DemoPointExtractor(),
            search_tool=DemoSearchTool(),
            reviewer=reviewer,
        ),
        NoveltyWorkflowConfig(max_rounds=1, minimum_evidence_per_point=1),
    )


# ---------------------------------------------------------------------------
# Reviewer 接入 Validator 之后、coverage assessment 之前
# ---------------------------------------------------------------------------


def test_reviewer_runs_after_validator_and_before_coverage() -> None:
    card = make_card("C1")
    decision = EvidenceReviewDecision(
        card_id="C1",
        verdict=ReviewVerdict.ACCEPT,
        issues=[],
        reviewed_confidence=0.85,
    )
    reviewer = ScriptedReviewer([decision])
    workflow = build_workflow(researcher_cards=[card], reviewer=reviewer)

    result = workflow.run(make_paper())

    # Reviewer 被调用过一次，传入的卡是 Validator 通过的
    assert len(reviewer.calls) == 1
    assert [c.card_id for c in reviewer.calls[0]] == ["C1"]
    # Coordinator 拿到的最终证据是 Reviewer accept 的卡
    assert [c.card_id for c in result.evidence_cards] == ["C1"]
    # 决定出现在结果中
    assert result.issues  # 至少有 coverage_gaps 等节点产生的 issues


# ---------------------------------------------------------------------------
# Coordinator 只接收最终通过的证据
# ---------------------------------------------------------------------------


def test_coordinator_only_receives_reviewer_accepted() -> None:
    # 两张卡：C1 accept，C2 reject；使用不同 title 避免 Validator 去重
    card1 = make_card("C1", document_title="Related Work A")
    card2 = make_card("C2", document_title="Related Work B")
    decisions = [
        EvidenceReviewDecision(
            card_id="C1",
            verdict=ReviewVerdict.ACCEPT,
            issues=[],
            reviewed_confidence=0.85,
        ),
        EvidenceReviewDecision(
            card_id="C2",
            verdict=ReviewVerdict.REJECT,
            issues=[],
            reviewed_confidence=0.2,
        ),
    ]
    reviewer = ScriptedReviewer(decisions)
    workflow = build_workflow(researcher_cards=[card1, card2], reviewer=reviewer)

    result = workflow.run(make_paper())

    # 只有 C1 进入最终证据
    assert [c.card_id for c in result.evidence_cards] == ["C1"]
    # C2 出现在 rejected_evidence
    rejected_ids = {item.card_id for item in result.rejected_evidence}
    assert "C2" in rejected_ids


# ---------------------------------------------------------------------------
# 审查决定写入 evidence-cards.json
# ---------------------------------------------------------------------------


def test_review_decisions_persisted_to_evidence_cards_json() -> None:
    card = make_card("C1")
    decision = EvidenceReviewDecision(
        card_id="C1",
        verdict=ReviewVerdict.ACCEPT,
        issues=[],
        reviewed_confidence=0.85,
    )
    reviewer = ScriptedReviewer([decision])
    workflow = build_workflow(researcher_cards=[card], reviewer=reviewer)

    workflow.run(make_paper())

    data = json.loads(
        Path("outputs/paper-reviewer-test/evidence-cards.json").read_text(
            encoding="utf-8"
        )
    )
    assert data["paper_id"] == "paper-reviewer-test"
    # raw_evidence_cards 使用 add reducer，zh/en 两个任务各返回 [C1]，所以会有重复
    assert any(c["card_id"] == "C1" for c in data["raw_evidence_cards"])
    # Validator 去重后只保留 1 张
    assert len(data["validator_accepted_cards"]) == 1
    assert len(data["review_decisions"]) == 1
    assert data["review_decisions"][0]["card_id"] == "C1"
    assert data["review_decisions"][0]["verdict"] == "accept"
    assert len(data["accepted_evidence_cards"]) == 1


# ---------------------------------------------------------------------------
# Reviewer 禁用时维持兼容行为
# ---------------------------------------------------------------------------


def test_reviewer_disabled_maintains_compatibility() -> None:
    card = make_card("C1")
    workflow = build_workflow(researcher_cards=[card], reviewer=None)

    result = workflow.run(make_paper())

    # Reviewer 未注入，行为与原工作流一致
    assert [c.card_id for c in result.evidence_cards] == ["C1"]
    # evidence-cards.json 不应包含 review_decisions（兼容旧 Reader）
    data = json.loads(
        Path("outputs/paper-reviewer-test/evidence-cards.json").read_text(
            encoding="utf-8"
        )
    )
    assert "review_decisions" not in data
    assert "validator_accepted_cards" not in data
    assert data["accepted_evidence_cards"][0]["card_id"] == "C1"


# ---------------------------------------------------------------------------
# DemoEvidenceReviewer 默认全 accept
# ---------------------------------------------------------------------------


def test_demo_reviewer_accepts_all_in_workflow() -> None:
    # 两张卡使用不同 document_title，避免被 Validator 按 (point_id, title) 去重
    card1 = make_card("C1", document_title="Related Work A")
    card2 = make_card("C2", document_title="Related Work B")
    workflow = build_workflow(
        researcher_cards=[card1, card2],
        reviewer=DemoEvidenceReviewer(),
    )

    result = workflow.run(make_paper())

    assert {c.card_id for c in result.evidence_cards} == {"C1", "C2"}


# ---------------------------------------------------------------------------
# needs_more_evidence 进入 coverage gap 提示
# ---------------------------------------------------------------------------


def test_needs_more_evidence_generates_workflow_issue() -> None:
    card = make_card("C1")
    decision = EvidenceReviewDecision(
        card_id="C1",
        verdict=ReviewVerdict.NEEDS_MORE_EVIDENCE,
        issues=[],
        reviewed_confidence=0.3,
    )
    reviewer = ScriptedReviewer([decision])
    workflow = build_workflow(researcher_cards=[card], reviewer=reviewer)

    result = workflow.run(make_paper())

    # C1 被标记 needs_more，不进入最终证据
    assert result.evidence_cards == []
    # 产生 needs_more_evidence workflow issue
    assert any(
        issue.code == "needs_more_evidence" for issue in result.issues
    )


# ---------------------------------------------------------------------------
# 单张卡片审查失败不导致全流程崩溃
# ---------------------------------------------------------------------------


class CrashingReviewer:
    """整批崩溃的 Reviewer，用于验证 fail_closed 兜底。"""

    def review(
        self,
        cards: Sequence[EvidenceCard],
        *,
        points: Sequence[NoveltyPoint],
        tasks: Sequence[ResearchTask],
    ) -> ReviewResult:
        raise RuntimeError("model service unavailable")


def test_reviewer_crash_does_not_crash_workflow() -> None:
    card = make_card("C1")
    workflow = build_workflow(
        researcher_cards=[card], reviewer=CrashingReviewer()
    )

    result = workflow.run(make_paper())

    # 工作流没有崩溃；最终证据为空
    assert result.evidence_cards == []
    # 产生 review_failed issue
    assert any(issue.code == "review_failed" for issue in result.issues)
    # 被拒卡进入 rejected_evidence
    assert any(
        item.card_id == "C1" for item in result.rejected_evidence
    )


# ---------------------------------------------------------------------------
# 确定性 Validator 拒绝的卡片不调用 Reviewer
# ---------------------------------------------------------------------------


def test_validator_rejected_cards_skip_reviewer() -> None:
    # 这张卡的 confidence=0.1，低于 Validator 默认门槛 0.3
    bad_card = EvidenceCard(
        card_id="C-BAD",
        task_id="T-1",
        novelty_point_id="NP-1",
        document_title="Bad Card",
        main_contribution="贡献",
        sources=[
            EvidenceSource(
                title="Bad",
                quote="quote",
                location="loc",
                url="https://example.test/bad",
            )
        ],
        relevance=0.1,
        confidence=0.1,
    )
    # 还有一张合规卡
    good_card = make_card("C-GOOD")
    reviewer = ScriptedReviewer(
        [
            EvidenceReviewDecision(
                card_id="C-GOOD",
                verdict=ReviewVerdict.ACCEPT,
                issues=[],
                reviewed_confidence=0.85,
            )
        ]
    )
    workflow = build_workflow(
        researcher_cards=[bad_card, good_card], reviewer=reviewer
    )

    workflow.run(make_paper())

    # Reviewer 只收到 C-GOOD，没收到 C-BAD
    assert len(reviewer.calls) == 1
    assert [c.card_id for c in reviewer.calls[0]] == ["C-GOOD"]


# ---------------------------------------------------------------------------
# 持久化层兼容：persist_evidence_cards 不传新字段时仍可写
# ---------------------------------------------------------------------------


def test_persist_evidence_cards_backward_compatible(tmp_path: Path) -> None:
    from novelty_agent_framework.schemas import RejectedEvidence

    paper = make_paper()
    card = make_card()
    path = persist_evidence_cards(
        paper,
        raw_cards=[card],
        accepted_cards=[card],
        rejected_evidence=[RejectedEvidence(card_id="X", reason="r")],
        output_root=tmp_path,
    )
    data = json.loads(path.read_text(encoding="utf-8"))

    # 旧调用方不传 validator_accepted_cards / review_decisions，对应键不存在
    assert "validator_accepted_cards" not in data
    assert "review_decisions" not in data
    assert data["raw_evidence_cards"][0]["card_id"] == "C1"
    assert data["accepted_evidence_cards"][0]["card_id"] == "C1"


# ---------------------------------------------------------------------------
# Renderer 读取不被破坏（间接验证：existing test_renderer.py 仍通过）
# 这里只验证 evidence-cards.json 的核心字段仍存在
# ---------------------------------------------------------------------------


def test_evidence_cards_json_keeps_renderer_required_fields() -> None:
    card = make_card("C1")
    decision = EvidenceReviewDecision(
        card_id="C1",
        verdict=ReviewVerdict.ACCEPT,
        issues=[],
        reviewed_confidence=0.85,
    )
    reviewer = ScriptedReviewer([decision])
    workflow = build_workflow(researcher_cards=[card], reviewer=reviewer)

    workflow.run(make_paper())

    data = json.loads(
        Path("outputs/paper-reviewer-test/evidence-cards.json").read_text(
            encoding="utf-8"
        )
    )
    # Renderer 依赖这三个字段，必须保留
    assert "raw_evidence_cards" in data
    assert "accepted_evidence_cards" in data
    assert "rejected_evidence" in data


# ---------------------------------------------------------------------------
# NoveltyEvidenceReviewer 也能跑通工作流（端到端）
# ---------------------------------------------------------------------------


class FakeModelClient:
    """返回固定 JSON 的假模型客户端。"""

    def __init__(self, content: str) -> None:
        self.content = content

    def complete(self, messages, *, options=None):  # type: ignore[no-untyped-def]
        return type(
            "Resp",
            (),
            {"content": self.content},
        )()


def test_llm_reviewer_runs_end_to_end_in_workflow() -> None:
    from backend.env import ModelResponse

    class _Client:
        def complete(self, messages, *, options=None):  # type: ignore[no-untyped-def]
            return ModelResponse(
                content=json.dumps(
                    {
                        "decisions": [
                            {
                                "card_id": "C1",
                                "verdict": "accept",
                                "issues": [],
                                "reviewed_confidence": 0.85,
                            }
                        ]
                    }
                )
            )

    card = make_card("C1")
    reviewer = NoveltyEvidenceReviewer(
        model_client=_Client(),
        config=EvidenceReviewerConfig(enabled=True),
    )
    workflow = build_workflow(researcher_cards=[card], reviewer=reviewer)

    result = workflow.run(make_paper())

    assert [c.card_id for c in result.evidence_cards] == ["C1"]
