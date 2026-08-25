import asyncio
import json

from backend.env import ModelResponse, ModelToolCall
from novelty_agent_framework.schemas import (EvidenceCardBuilderResult, NoveltyPoint,
    ResearcherToolObservation, ResearchTask, StrictModel, TaskResearchRequest)
from novelty_agent_framework.tools import ResearcherToolRegistry
from novelty_agent_framework.workflows import TaskResearcherConfig, TaskResearcherWorkflow


def scope():
    return TaskResearchRequest(subject_paper_id="paper-1", run_id="run-1",
        novelty_point=NoveltyPoint(point_id="NP-1", claim="claim", technical_features=[]),
        research_task=ResearchTask(task_id="T-1", novelty_point_id="NP-1",
                                   task_type="search", language="en"))


class ReaderArgs(StrictModel):
    max_chars: int


class FakeReader:
    name, description, args_schema = "reader", "reader", ReaderArgs

    def __init__(self): self.max_chars = None

    async def ainvoke(self, arguments, *, scope):
        self.max_chars = arguments.max_chars
        read = {"read_id": "read-1", "work_id": "work-1", "artifact_id": "artifact-1",
                "role": "extracted_text", "char_start": 0, "char_end": 5,
                "text": "quote", "has_more": False, "sha256": "abc"}
        return ResearcherToolObservation(tool_name="reader",
            arguments=arguments.model_dump(), succeeded=True, payload={"read_result": read})


class FakeModel:
    def __init__(self, responses): self.responses = list(responses)
    async def acomplete(self, messages, *, options=None): return self.responses.pop(0)


class FakeBuilder:
    def __init__(self, *, fail=False): self.calls, self.fail = [], fail
    def build(self, draft, *, scope, read_results):
        if self.fail: raise ValueError("broken provenance")
        self.calls.append((draft, scope, list(read_results)))
        return EvidenceCardBuilderResult(
            warnings=["no evidence: empty"] if not draft.cards else [])


def finish(reason="empty"):
    return ModelResponse(content=json.dumps({"cards": [], "no_evidence_reason": reason}))


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
    result = asyncio.run(TaskResearcherWorkflow(FakeModel([finish("nothing relevant")]),
        ResearcherToolRegistry(), FakeBuilder()).ainvoke(scope()))
    assert result.status.value == "completed"
    assert result.evidence == result.evidence_cards == []
    assert result.warnings == ["no evidence: empty"]
