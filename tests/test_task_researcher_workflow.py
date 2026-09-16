import asyncio
import json

import pytest
from pydantic import ValidationError

from backend.env import ModelResponse, ModelToolCall
from novelty_agent_framework.schemas import (EvidenceCardBuilderResult, NoveltyPoint,
    ResearcherToolObservation, ResearchTask, StrictModel, TaskResearchRequest)
from novelty_agent_framework.tools import ResearcherToolRegistry
from novelty_agent_framework.workflows import TaskResearcherConfig, TaskResearcherWorkflow
from conftest import minimal_search_plan


def scope():
    return TaskResearchRequest(subject_paper_id="paper-1", run_id="run-1",
        novelty_point=NoveltyPoint(point_id="NP-1", claim="claim", technical_features=[]),
        research_task=ResearchTask(task_id="T-1", novelty_point_id="NP-1",
                                   task_type="search", language="en"),
        search_plan=minimal_search_plan("T-1", "NP-1"))


class ReaderArgs(StrictModel):
    max_chars: int


class FakeReader:
    name, description, args_schema = "reader", "reader", ReaderArgs

    def __init__(self): self.max_chars = None

    async def ainvoke(self, arguments, *, scope):
        self.max_chars = arguments.max_chars
        read = {"namespace": "research_reference", "read_id": "read-1",
                "work_id": "work-1", "artifact_id": "artifact-1",
                "role": "extracted_text", "char_start": 0, "char_end": 5,
                "text": "quote", "has_more": False, "sha256": "abc"}
        return ResearcherToolObservation(tool_name="reader",
            arguments=arguments.model_dump(), succeeded=True, payload={"read_result": read})


class FakeModel:
    def __init__(self, responses): self.responses, self.messages = list(responses), []
    async def acomplete(self, messages, *, options=None):
        self.messages.append(messages)
        return self.responses.pop(0)


class FakeBuilder:
    def __init__(self, *, fail=False): self.calls, self.fail = [], fail
    def build(self, draft, *, scope, read_results):
        if self.fail: raise ValueError("broken provenance")
        self.calls.append((draft, scope, list(read_results)))
        return EvidenceCardBuilderResult(
            warnings=["no evidence: empty"] if not draft.cards else [])


def finish(reason="empty"):
    return ModelResponse(content=json.dumps({"cards": [], "no_evidence_reason": reason}))


def test_request_requires_a_bound_search_plan():
    payload = scope().model_dump(mode="python")
    payload.pop("search_plan")
    with pytest.raises(ValidationError):
        TaskResearchRequest.model_validate(payload)

    payload = scope().model_dump(mode="python")
    payload["search_plan"]["task_id"] = "wrong-task"
    with pytest.raises(ValidationError, match="search_plan must belong"):
        TaskResearchRequest.model_validate(payload)


def test_native_reader_trace_is_trusted_and_arguments_are_not_clamped():
    reader = FakeReader()
    model = FakeModel([ModelResponse(content=None, tool_calls=[
        ModelToolCall("call-1", "reader", {"max_chars": 12000})]), finish()])
    builder = FakeBuilder()
    workflow = TaskResearcherWorkflow(model, ResearcherToolRegistry([reader]), builder,
        config=TaskResearcherConfig(max_steps=4, max_tool_calls=2, max_chars_per_read=10))
    result = asyncio.run(workflow.ainvoke(scope()))
    assert result.status.value == "completed" and result.steps_used == 2
    assert reader.max_chars == 12000
    assert len(result.read_results) == 1
    assert builder.calls[0][2] == result.read_results


def test_invalid_finish_is_partial_and_builder_is_not_called():
    builder = FakeBuilder()
    result = asyncio.run(TaskResearcherWorkflow(FakeModel([ModelResponse(content="not json")]),
        ResearcherToolRegistry(), builder).ainvoke(scope()))
    assert result.status.value == "partial" and not builder.calls
    assert any("invalid ResearchFinishDraft" in item for item in result.warnings)


def test_builder_failure_is_partial():
    result = asyncio.run(TaskResearcherWorkflow(FakeModel([finish()]),
        ResearcherToolRegistry(), FakeBuilder(fail=True)).ainvoke(scope()))
    assert result.status.value == "partial"
    assert any("evidence builder failed" in item for item in result.warnings)


def test_no_evidence_finish_is_completed_with_warning():
    model = FakeModel([finish("nothing relevant")])
    result = asyncio.run(TaskResearcherWorkflow(model,
        ResearcherToolRegistry(), FakeBuilder()).ainvoke(scope()))
    assert result.status.value == "completed"
    assert result.evidence == result.evidence_cards == []
    assert result.warnings == ["no evidence: empty"]
    assert "search_plan_json:" in model.messages[0][1].content
    assert '"task_id": "T-1"' in model.messages[0][1].content


CARD = {
    "main_contribution": "same idea",
    "overlaps": ["overlap"],
    "differences": ["difference"],
    "quotes": [{"quote": "quote", "interpretation": "same wording", "confidence": 0.7}],
    "possible_baseline": True,
    "relevance": 0.8,
    "confidence": 0.7,
}


def card_finish():
    return ModelResponse(content=json.dumps({"cards": [CARD]}))


def reader_call(call_id="call-1"):
    return ModelResponse(
        content=None,
        tool_calls=[ModelToolCall(call_id, "reader", {"max_chars": 5})],
    )


def test_harness_budget_failure_salvages_cards_from_recovered_reads() -> None:
    """预算耗尽后必须用已读内容抢救出卡，而不是把读到的证据全丢。

    回归背景（2026-09-16，MF2033k6lC run 0010/0011）：harness 抛
    ``ToolCallHarnessError`` 后 ``_partial()`` 不构建卡片 —— 两轮读了 25 万字符却 0 卡。
    """

    reader = FakeReader()
    model = FakeModel([reader_call(), reader_call("call-2"), card_finish()])
    builder = FakeBuilder()
    workflow = TaskResearcherWorkflow(
        model,
        ResearcherToolRegistry([reader]),
        builder,
        config=TaskResearcherConfig(max_steps=4, max_tool_calls=1, max_chars_per_read=10),
    )

    result = asyncio.run(workflow.ainvoke(scope()))

    assert result.status.value == "completed"
    assert result.steps_used == 2
    assert len(result.read_results) == 1
    assert any("salvaged finish draft" in item for item in result.warnings)
    # 抢救调用复用了同一批读取结果，引文绑定才有依据。
    assert len(builder.calls) == 1
    draft, _scope, reads = builder.calls[0]
    assert [card.main_contribution for card in draft.cards] == ["same idea"]
    assert reads == result.read_results
    # 抢救调用无工具，且把已读片段喂给了模型。
    salvage_user = model.messages[2][1].content
    assert "read_excerpts" in salvage_user
    assert '"artifact_id": "artifact-1"' in salvage_user


def test_salvage_is_skipped_when_nothing_was_read() -> None:
    """读取为空时不白花一次模型调用。"""

    model = FakeModel([ModelResponse(content="not json")])
    result = asyncio.run(
        TaskResearcherWorkflow(
            model, ResearcherToolRegistry(), FakeBuilder()
        ).ainvoke(scope())
    )

    assert result.status.value == "partial"
    assert len(model.messages) == 1


def test_salvage_failure_still_falls_back_to_partial() -> None:
    reader = FakeReader()
    model = FakeModel([reader_call(), reader_call("call-2"), ModelResponse(content="still broken")])
    workflow = TaskResearcherWorkflow(
        model,
        ResearcherToolRegistry([reader]),
        FakeBuilder(),
        config=TaskResearcherConfig(max_steps=4, max_tool_calls=1, max_chars_per_read=10),
    )

    result = asyncio.run(workflow.ainvoke(scope()))

    assert result.status.value == "partial"
    assert any("salvage attempt failed" in item for item in result.warnings)


def test_salvage_can_be_disabled() -> None:
    reader = FakeReader()
    model = FakeModel([reader_call(), reader_call("call-2"), card_finish()])
    workflow = TaskResearcherWorkflow(
        model,
        ResearcherToolRegistry([reader]),
        FakeBuilder(),
        config=TaskResearcherConfig(
            max_steps=4,
            max_tool_calls=1,
            max_chars_per_read=10,
            salvage_enabled=False,
        ),
    )

    result = asyncio.run(workflow.ainvoke(scope()))

    assert result.status.value == "partial"
    assert len(model.messages) == 2
