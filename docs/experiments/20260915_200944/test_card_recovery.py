"""Regressions for real candidate-to-card loss paths, with the real Builder."""
import asyncio
import json

import pytest
from backend.env import ModelResponse, ModelToolCall
from novelty_agent_framework.core.tool_call_harness import ToolCallHarnessEvent
from novelty_agent_framework.schemas import ResearcherToolObservation, ResearchFinishDraft, StrictModel
from novelty_agent_framework.tools import EvidenceCardBuilder, ResearcherToolRegistry
from novelty_agent_framework.workflows import TaskResearcherConfig, TaskResearcherWorkflow
from novelty_agent_framework.workflows.candidate_audit import build_candidate_audit
from test_evidence_card_builder import prepare_store, scope, read, card, quote, TEXT_A, TEXT_B
from test_tool_call_harness import ScriptedModelClient


class ReadArgs(StrictModel):
    artifact_id: str
    max_chars: int = 100


class Reader:
    name, description, args_schema = "reader", "read persisted text", ReadArgs

    def __init__(self, reads):
        self.reads = {r.artifact_id: r for r in reads}
        self.calls = []

    async def ainvoke(self, args, *, scope):
        self.calls.append(args)
        return ResearcherToolObservation(tool_name=self.name, succeeded=True,
            payload={"read_result": self.reads[args.artifact_id].model_dump(mode="json")})


def call(id, artifact="art_a", max_chars=100):
    return ModelResponse(content=None, tool_calls=[ModelToolCall(id, "reader", {
        "artifact_id": artifact, "max_chars": max_chars,
    })])


def finish(*cards):
    return ModelResponse(content=ResearchFinishDraft(cards=list(cards)).model_dump_json())


def workflow(tmp_path, model, reader, **config):
    return TaskResearcherWorkflow(model, ResearcherToolRegistry([reader]),
        EvidenceCardBuilder(prepare_store(tmp_path)), config=TaskResearcherConfig(**config))


@pytest.mark.parametrize("boundary", ["turn", "total", "per_tool", "read_chars"])
def test_budget_finalization_builds_card_from_existing_read(tmp_path, boundary):
    reader = Reader([read()])
    config = {"max_steps": 5, "max_tool_calls": 5, "per_tool_limits": {}}
    responses = [call("first", max_chars=len(TEXT_A))]
    if boundary == "turn":
        config["max_steps"] = 1
    else:
        responses.append(call("rejected", max_chars=len(TEXT_A)))
        if boundary == "total": config["max_tool_calls"] = 1
        if boundary == "per_tool": config["per_tool_limits"] = {"reader": 1}
        if boundary == "read_chars": config["max_total_read_chars"] = len(TEXT_A)
    responses.append(finish(card(quote("Alpha unique quote."))))
    model = ScriptedModelClient(*responses)
    result = asyncio.run(workflow(tmp_path, model, reader, **config).ainvoke(scope()))
    assert len(reader.calls) == 1
    assert result.status.value == "partial"  # Coverage remains explicitly degraded.
    assert len(result.evidence_cards) == len(result.evidence) == 1
    assert result.evidence[0].quote == "Alpha unique quote."
    assert result.candidate_audit[0].status == "card_produced"
    assert result.steps_used == len(responses)
    messages, options = model.calls[-1]
    assert not options.tools and options.tool_choice == "none"
    # The aborted tool call has a matching rejection before the final user message.
    if boundary != "turn":
        assert any(m.role == "tool" and m.tool_call_id == "rejected" for m in messages)
    assert any("finalization completed" in w for w in result.warnings)


@pytest.mark.parametrize("last", [ModelResponse(content="invalid JSON"), call("forbidden")])
def test_invalid_finalization_is_bounded_and_retains_reads(tmp_path, last):
    reader = Reader([read()])
    model = ScriptedModelClient(call("first"), last)
    result = asyncio.run(workflow(tmp_path, model, reader, max_steps=1).ainvoke(scope()))
    assert len(model.calls) == 2 and len(reader.calls) == 1
    assert result.status.value == "partial" and not result.evidence_cards
    assert len(result.read_results) == 1
    assert result.candidate_audit[0].status == "read_task_interrupted"


@pytest.mark.parametrize("repair_ok", [True, False])
def test_single_quote_correction_preserves_already_valid_card(tmp_path, repair_ok):
    reader = Reader([read(), read("wrk_b", "art_b", TEXT_B)])
    original = finish(card(quote("Alpha unique quote.")), card(quote("Beta invented quote.")))
    correction = finish(card(quote("Beta unique quote." if repair_ok else "Still invented.")))
    model = ScriptedModelClient(call("a"), call("b", "art_b"), original, correction)
    result = asyncio.run(workflow(tmp_path, model, reader).ainvoke(scope()))
    assert len(model.calls) == 4 and len(reader.calls) == 2
    assert result.steps_used == 4
    assert len(result.evidence_cards) == (2 if repair_ok else 1)
    assert any(e.quote == "Alpha unique quote." for e in result.evidence)
    assert not model.calls[-1][1].tools and model.calls[-1][1].tool_choice == "none"
    assert len(json.loads(model.calls[-1][0][-1].content)["rejected_cards"]) == 1
    assert all(e.quote in TEXT_A or e.quote in TEXT_B for e in result.evidence)


def test_real_latex_quote_loss_can_be_repaired_without_loosening_matching(tmp_path):
    text = 'the "graph partitioning $$ + $$ + local learning" framework splits the global graph'
    reader = Reader([read(text=text)])
    model = ScriptedModelClient(call("a"),
        finish(card(quote(text.replace("$$ + $$ +", "+ +")))), finish(card(quote(text))))
    result = asyncio.run(workflow(tmp_path, model, reader).ainvoke(scope()))
    assert len(result.evidence_cards) == 1 and result.evidence[0].quote == text
    assert any("ungrounded quote" in w for w in result.warnings)
    assert any("recovered 1" in w for w in result.warnings)


def event(name, payload, succeeded=True):
    return ToolCallHarnessEvent(kind="tool_result", observation=ResearcherToolObservation(
        tool_name=name, succeeded=succeeded, payload=payload))


def test_candidates_record_unread_read_and_unacquired_without_claiming_irrelevance():
    trace = [event("database_search", {"database_search_result": {"results": [
        {"work_id": "wrk_a", "title": "Read", "artifact_ids": ["art_a"]},
        {"work_id": "wrk_b", "title": "Unread", "artifact_ids": ["art_b"]},
    ]}}), event("web_search", {"search_result": {"results": [
        {"source_record_id": "web_1", "title": "Discovery only"},
    ]}})]
    rows = build_candidate_audit(trace, [read()], [], [])
    assert {r.status for r in rows} == {"read_without_card", "not_read", "acquisition_unavailable"}
    assert len(rows) == 3 and all(not r.card_ids for r in rows)


def test_browser_binding_merges_discovery_row_and_keeps_namespace_separate():
    trace = [event("web_search", {"source_records": [{"source_record_id": "web_1", "title": "Page"}]}),
             event("browser", {"browser_result": {"source_record_id": "web_1", "work_id": "wrk_a",
                "artifacts": [{"artifact_id": "art_a"}]}})]
    rows = build_candidate_audit(trace, [read(), read(namespace="subject_reference")], [], [])
    assert len(rows) == 2
    web = next(r for r in rows if r.namespace == "research_reference")
    assert web.source_record_id == "web_1" and web.title == "Page" and web.read_ids


def test_web_without_browser_prompt_is_explicit_and_budget_is_visible(tmp_path):
    reader = Reader([read()])
    model = ScriptedModelClient(call("a"), finish(card(quote("Alpha unique quote."))))
    asyncio.run(workflow(tmp_path, model, reader).ainvoke(scope()))
    first = model.calls[0][0]
    assert "browser is unavailable" in first[1].content
    assert "source_record_id" in first[1].content
    assert '"remaining_tool_calls"' in first[0].content


def test_malformed_discovery_does_not_discard_valid_reader_evidence():
    rows = build_candidate_audit([
        event("database_search", {"database_search_result": None, "research_bundle": "invalid"}, False),
        event("web_search", {"source_records": [None, {"work_id": 42}], "search_result": []}),
    ], [read()], [], [])
    assert len(rows) == 1 and rows[0].status == "read_without_card"
