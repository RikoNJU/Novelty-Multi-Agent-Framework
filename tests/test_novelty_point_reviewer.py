"""查新点级 Reviewer、Reader scope 与输出引用契约。"""

from __future__ import annotations

import asyncio
import hashlib
import json

import pytest
from pydantic import ValidationError
from backend.env import ModelResponse, ModelToolCall
from novelty_agent_framework.agents import NoveltyEvidenceReviewer
from novelty_agent_framework.agents import (
    DemoCoordinator,
    DemoSearchPlanner,
    DemoTaskResearcher,
)
from novelty_agent_framework.schemas import (
    ArtifactRole,
    ArtifactNamespace,
    Evidence,
    EvidenceCard,
    NoveltyPoint,
    NoveltyPointReviewRequest,
    NoveltyPointReview,
    PaperInput,
    ReferenceReadResult,
    ResearchTask,
)
from novelty_agent_framework.tools import ReviewerReaderTool, ResearcherToolRegistry
from novelty_agent_framework.workflows import (
    NoveltyWorkflow,
    NoveltyWorkflowServices,
)


class ScriptedClient:
    def __init__(self, *responses: ModelResponse):
        self.responses = list(responses)
        self.calls = []

    async def acomplete(self, messages, *, options=None):
        self.calls.append((list(messages), options))
        return self.responses.pop(0)


class RecordingReader:
    max_chars_per_read = 16_000

    def __init__(self):
        self.requests = []

    async def ainvoke(self, request):
        self.requests.append(request)
        return ReferenceReadResult(
            namespace=request.namespace,
            read_id="read-1",
            work_id="work-1",
            artifact_id=request.artifact_id,
            role=ArtifactRole.EXTRACTED_TEXT,
            char_start=request.char_start,
            char_end=request.char_start + len("source text"),
            text="source text",
            has_more=False,
            sha256=hashlib.sha256(b"source text").hexdigest(),
        )


def _request() -> NoveltyPointReviewRequest:
    point = NoveltyPoint(point_id="NP-1", claim="组合技术特征")
    task = ResearchTask(
        task_id="T-1",
        novelty_point_id="NP-1",
        task_type="prior-art",
        language="zh",
    )
    evidence = Evidence(
        evidence_id="E-1",
        work_id="work-1",
        artifact_id="artifact-1",
        novelty_point_id="NP-1",
        task_id="T-1",
        quote="source text",
        interpretation="与查新点部分重合",
        confidence=0.9,
    )
    card = EvidenceCard(
        card_id="C-1",
        task_id="T-1",
        novelty_point_id="NP-1",
        document_title="Prior Work",
        main_contribution="prior contribution",
        relevance=0.9,
        confidence=0.9,
        evidence_ids=["E-1"],
    )
    return NoveltyPointReviewRequest(
        subject_paper_id="paper-1",
        novelty_point=point,
        tasks=[task],
        cards=[card],
        evidence=[evidence],
    )


def _review_json(status="reviewed") -> str:
    if status == "insufficient_evidence":
        return json.dumps(
            {
                "novelty_point_id": "NP-1",
                "status": status,
                "supplement_request": {
                    "reason": "缺少实现细节",
                    "missing_aspects": ["实现细节"],
                },
            }
        )
    return json.dumps(
        {
            "novelty_point_id": "NP-1",
            "status": status,
            "verdict": "partially_novel",
            "verdict_reason": "既有工作覆盖部分特征，但未覆盖完整组合。",
            "confidence": 0.84,
            "highly_relevant_works": [
                {
                    "work_id": "work-1",
                    "card_ids": ["C-1"],
                    "evidence_ids": ["E-1"],
                    "relevance_reason": "直接覆盖一个核心特征。",
                }
            ],
        },
        ensure_ascii=False,
    )


def _reviewer(client, reader):
    return NoveltyEvidenceReviewer(
        client,
        tool_registry=ResearcherToolRegistry([ReviewerReaderTool(reader)]),
    )


def test_review_request_rejects_unresolved_card_evidence_ids():
    request = _request()
    with pytest.raises(ValidationError, match="absent from request evidence"):
        NoveltyPointReviewRequest(
            subject_paper_id=request.subject_paper_id,
            novelty_point=request.novelty_point,
            tasks=request.tasks,
            cards=request.cards,
            evidence=[],
        )


def test_point_review_can_finish_with_traceable_relevant_work():
    result = asyncio.run(
        _reviewer(ScriptedClient(ModelResponse(content=_review_json())), RecordingReader())
        .review(_request())
    )
    assert result.status.value == "reviewed"
    assert result.verdict.value == "partially_novel"
    assert result.highly_relevant_works[0].evidence_ids == ["E-1"]


def test_reviewer_reader_call_is_returned_to_model():
    reader = RecordingReader()
    client = ScriptedClient(
        ModelResponse(
            content=None,
            tool_calls=(
                ModelToolCall(
                    id="call-1",
                    name="reader",
                    arguments={"artifact_id": "artifact-1", "max_chars": 100},
                ),
            ),
        ),
        ModelResponse(content=_review_json()),
    )
    result = asyncio.run(_reviewer(client, reader).review(_request()))
    assert result.status.value == "reviewed"
    assert reader.requests[0].artifact_id == "artifact-1"
    observation = json.loads(client.calls[1][0][-1].content)
    assert observation["succeeded"] is True
    assert observation["read_result"]["text"] == "source text"


def test_reviewer_reader_rejects_artifact_outside_point_scope():
    reader = RecordingReader()
    client = ScriptedClient(
        ModelResponse(
            content=None,
            tool_calls=(
                ModelToolCall(
                    id="call-bad",
                    name="reader",
                    arguments={"artifact_id": "artifact-other"},
                ),
            ),
        ),
        ModelResponse(content=_review_json("insufficient_evidence")),
    )
    result = asyncio.run(_reviewer(client, reader).review(_request()))
    assert result.status.value == "insufficient_evidence"
    assert reader.requests == []
    observation = json.loads(client.calls[1][0][-1].content)
    assert observation["succeeded"] is False
    assert "outside reviewer scope" in observation["error"]


def test_insufficient_evidence_does_not_require_a_verdict():
    result = asyncio.run(
        _reviewer(
            ScriptedClient(ModelResponse(content=_review_json("insufficient_evidence"))),
            RecordingReader(),
        ).review(_request())
    )
    assert result.verdict is None
    assert result.confidence is None
    assert result.supplement_request is not None


class PointReviewer:
    def __init__(self):
        self.requests = []

    async def review(self, request):
        self.requests.append(request)
        return NoveltyPointReview.model_validate_json(_review_json())


def _workflow(reviewer):
    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=DemoCoordinator(),
            task_researcher=DemoTaskResearcher(),
            search_planner=DemoSearchPlanner(),
            reviewer=reviewer,
        )
    )


def test_workflow_persists_point_reviews_without_filtering_or_routing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    request = _request()
    reviewer = PointReviewer()
    workflow = _workflow(reviewer)
    state = {
        "paper": PaperInput(paper_id="paper-1", title="Paper", full_text="body"),
        "novelty_points": [request.novelty_point],
        "all_research_tasks": request.tasks,
        "raw_evidence": request.evidence,
        "raw_evidence_cards": request.cards,
        "validator_accepted_cards": request.cards,
        "evidence_cards": request.cards,
        "rejected_evidence": [],
    }
    reviewed = asyncio.run(workflow._review_evidence(state))
    assert reviewed["evidence_cards"] == request.cards
    payload = json.loads(
        (tmp_path / "outputs/paper-1/novelty-reviews.json").read_text(encoding="utf-8")
    )
    assert payload["reviews"][0]["novelty_point_id"] == "NP-1"
    assert asyncio.run(
        workflow._route_after_evidence_sufficiency_check(
            {**state, **reviewed, "insufficient_final_evidence_points": []}
        )
    ) == "synthesize"
