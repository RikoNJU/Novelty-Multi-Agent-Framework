from __future__ import annotations

import asyncio
import json
from pathlib import Path

from backend.env import (ChatMessage, ModelProfile, ModelResponse, ModelToolCall,
                         OpenAICompatibleChatClient)
from novelty_agent_framework.core import (
    RuntimeArtifactManager,
    RuntimeDebugConfig,
    ToolCallHarness,
)
from novelty_agent_framework.core.runtime_artifacts import _infer_result_count
from novelty_agent_framework.schemas import (
    NoveltyPoint,
    ResearcherToolObservation,
    ResearchTask,
    StrictModel,
    TaskResearchRequest,
)
from novelty_agent_framework.tools import ResearcherToolRegistry
from conftest import minimal_search_plan


def _config(tmp_path: Path, *, enabled: bool = True, max_inline_bytes: int = 256_000):
    return RuntimeDebugConfig(
        enabled=enabled,
        output_root=tmp_path / "outputs",
        archive_root=tmp_path / "docs" / "experiments" / "runtime",
        max_inline_bytes=max_inline_bytes,
    )


def test_diagnostic_sidecar_is_archived_and_rejects_unsafe_name(tmp_path: Path) -> None:
    manager = RuntimeArtifactManager("paper-1", config=_config(tmp_path), run_id="trace-1")
    manager.record_diagnostic_artifact("point_extraction_trace.json", {"stage": "dedup"})
    assert json.loads((manager.run_dir / "diagnostics" / "point_extraction_trace.json").read_text()) == {"stage": "dedup"}
    _, archive = manager.finish_run("SUCCESS")
    assert archive is not None
    assert (archive / "diagnostics" / "point_extraction_trace.json").is_file()


def test_incremental_run_stage_tool_and_archived_summary(tmp_path: Path) -> None:
    manager = RuntimeArtifactManager(
        "paper/unsafe",
        config=_config(tmp_path),
        run_id="run-1",
        enabled_tools=["web_search"],
        stage_names=["researcher", "writer"],
    )
    assert manager.run_dir is not None
    manifest = json.loads((manager.run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "RUNNING"

    manager.activate()
    stage = manager.start_stage("researcher", {"query": "novelty"})
    tool = manager.start_tool_call(
        "web_search",
        agent_arguments={"query": "novelty"},
        resolved_arguments={"query": "novelty", "max_results": 10},
        agent_tool_call_id="model-call-7",
    )
    running = json.loads(tool.path.read_text(encoding="utf-8"))
    assert running["execution_status"] == "RUNNING"
    manager.finish_tool_call(
        tool,
        raw_result={"http_status": 200, "hits": []},
        normalized_result={"results": []},
    )
    manager.finish_stage(stage, {"evidence_cards": []})
    manager.deactivate()
    _, archive = manager.finish_run("SUCCESS")

    recorded = json.loads(tool.path.read_text(encoding="utf-8"))
    stage_meta = json.loads((stage.directory / "meta.json").read_text(encoding="utf-8"))
    assert "debug_details" not in stage_meta
    assert recorded["tool_call_id"] == "tool_0001"
    assert recorded["agent_tool_call_id"] == "model-call-7"
    assert recorded["execution_status"] == "SUCCESS"
    assert recorded["business_status"] == "EMPTY"
    assert recorded["agent_arguments"] == {"query": "novelty"}
    assert recorded["resolved_arguments"]["max_results"] == 10
    assert recorded["raw_result"]["http_status"] == 200
    assert recorded["normalized_result"] == {"results": []}
    summary = json.loads((manager.run_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["run"]["status"] == "SUCCESS"
    assert any(item["stage_name"] == "writer" and item["status"] == "NOT_RUN"
               for item in summary["stages"])
    not_run_meta = json.loads(
        (manager.run_dir / "stages" / "not_run_writer" / "meta.json").read_text(encoding="utf-8")
    )
    assert not_run_meta["status"] == "NOT_RUN"
    assert summary["tool_calls"] == [{
        "calls": 1, "empty": 1, "failed": 0, "success": 1,
        "tool_name": "web_search",
    }]
    assert archive is not None
    assert (archive / "summary.json").is_file()
    assert (archive / "summary.md").is_file()
    diagnostic = manager.run_dir / "diagnostics" / "reader.json"
    assert json.loads(diagnostic.read_text(encoding="utf-8"))["status"] == "INCOMPLETE"
    assert (archive / "diagnostics" / "reader.json").is_file()
    assert (archive / "diagnostics" / "reference_namespace.json").is_file()
    assert (archive / "diagnostics" / "reviewer.json").is_file()
    namespace_detail = json.loads(
        (manager.run_dir / "diagnostics" / "reference_namespace.json").read_text(
            encoding="utf-8"
        )
    )
    reviewer_detail = json.loads(
        (manager.run_dir / "diagnostics" / "reviewer.json").read_text(
            encoding="utf-8"
        )
    )
    assert namespace_detail["scope"]["run_id"] == "run-1"
    assert namespace_detail["report"]["run_id"] == "run-1"
    assert reviewer_detail["scope"]["run_id"] == "run-1"
    assert reviewer_detail["report"]["run_id"] == "run-1"
    assert summary["diagnostics"][0]["artifact"] == "diagnostics/reader.json"
    assert "## Runtime Diagnostics" in (manager.run_dir / "summary.md").read_text(
        encoding="utf-8"
    )


def test_run_identity_is_written_to_manifest_and_summary(tmp_path: Path) -> None:
    identity = {
        "entrypoint": "paper_input",
        "input_identity": {
            "paper_json": "fixtures/experiments/case/paper.json",
            "paper_sha256": "a" * 64,
            "novelty_point_id": None,
            "task_id": None,
            "search_plan_id": None,
        },
    }
    manager = RuntimeArtifactManager(
        "paper", config=_config(tmp_path), run_id="identity-run", run_identity=identity
    )
    _, archive = manager.finish_run("SUCCESS")

    manifest = json.loads((manager.run_dir / "manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((manager.run_dir / "summary.json").read_text(encoding="utf-8"))
    assert manifest["entrypoint"] == "paper_input"
    assert manifest["input_identity"] == identity["input_identity"]
    assert summary["run"]["entrypoint"] == "paper_input"
    assert summary["run"]["input_identity"] == identity["input_identity"]


def test_failures_preserve_raw_result_error_and_traceback(tmp_path: Path) -> None:
    manager = RuntimeArtifactManager("paper", config=_config(tmp_path))
    manager.activate()
    stage = manager.start_stage("researcher", {"input": True})
    call = manager.start_tool_call(
        "browser", agent_arguments={"url": "x"}, resolved_arguments={"url": "x"}
    )
    try:
        raise TimeoutError("browser timed out")
    except TimeoutError as exc:
        manager.fail_tool_call(call, exc, raw_result={"status": 200})
        manager.fail_stage(stage, exc)
        manager.deactivate()
        manager.finish_run("FAILED", error=exc)

    payload = json.loads(call.path.read_text(encoding="utf-8"))
    assert payload["execution_status"] == "FAILED"
    assert payload["business_status"] == "INVALID"
    assert payload["raw_result"] == {"status": 200}
    assert payload["normalized_result"] is None
    assert payload["error"]["type"] == "TimeoutError"
    assert "Traceback" in payload["error"]["traceback"]
    assert list((manager.run_dir / "errors").glob("*.json"))


def test_recursive_redaction_and_large_value_reference(tmp_path: Path) -> None:
    secret = "do-not-persist-this"
    manager = RuntimeArtifactManager(
        "paper",
        config=_config(tmp_path, max_inline_bytes=20),
        runtime_config={
            "apiKey": secret,
            "nested": {"Authorization": secret, "safe": f"token={secret}"},
        },
    )
    stage = manager.start_stage("reader", {"password": secret, "text": "x" * 100})
    manager.finish_stage(stage, {"cookie": secret})
    _, archive = manager.finish_run("SUCCESS")

    all_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in tmp_path.rglob("*")
        if path.is_file()
    )
    assert secret not in all_text
    stage_input = json.loads((stage.directory / "input.json").read_text(encoding="utf-8"))
    assert stage_input["password"] == "***REDACTED***"
    assert stage_input["text"]["type"] == "content_reference"
    blob = manager.run_dir / stage_input["text"]["path"]
    assert blob.is_file()
    assert len(blob.read_bytes()) == stage_input["text"]["size"]
    assert (archive / stage_input["text"]["path"]).read_bytes() == blob.read_bytes()
    assert stage_input["text"]["size"] == 100


def test_concurrent_points_keep_distinct_task_scope(tmp_path: Path) -> None:
    manager = RuntimeArtifactManager("paper", config=_config(tmp_path), run_id="two-points")
    client = OpenAICompatibleChatClient(ModelProfile(
        alias="local", model="local", api_key="stub"))
    client._complete = lambda _messages, *, options=None: ModelResponse(
        content="ok", tool_calls=(ModelToolCall(id="same-call", name="search", arguments={}),))

    async def worker(point_id: str) -> None:
        stage = manager.start_stage("run_research_task", {
            "current_point": {"point_id": point_id},
            "current_task": {"task_id": "T-1", "novelty_point_id": point_id,
                             "attempt": 1},
        })
        await asyncio.sleep(0)
        client.complete([ChatMessage(role="user", content=point_id)])
        handle = manager.start_tool_call("search", agent_arguments={},
                                         resolved_arguments={}, agent_tool_call_id="same-call")
        manager.finish_tool_call(handle, raw_result=[], normalized_result=[])
        manager.finish_stage(stage, {})

    manager.activate()
    async def run_both() -> None:
        await asyncio.gather(worker("NP-1"), worker("NP-2"))
    asyncio.run(run_both())
    manager.deactivate()
    records = [json.loads(path.read_text()) for path in
               (manager.run_dir / "tools").glob("*.json")]
    assert {item["scope"]["point_id"] for item in records} == {"NP-1", "NP-2"}
    assert {item["scope"]["task_id"] for item in records} == {"T-1"}
    assert all(item["parent_stage_id"] for item in records)
    model_records = [json.loads(path.read_text()) for path in
                     (manager.run_dir / "llm_calls").glob("*.json")]
    assert {item["scope"]["point_id"] for item in model_records} == {"NP-1", "NP-2"}
    assert all(item["parent_stage_id"] for item in model_records)
    models_by_point = {item["scope"]["point_id"]: item["llm_call_id"]
                       for item in model_records}
    assert all(item["parent_llm_call_id"] == models_by_point[item["scope"]["point_id"]]
               for item in records)


def test_disabled_recorder_has_no_filesystem_side_effect(tmp_path: Path) -> None:
    manager = RuntimeArtifactManager("paper", config=_config(tmp_path, enabled=False))
    manager.activate()
    stage = manager.start_stage("researcher", {"input": True})
    call = manager.start_tool_call(
        "web_search", agent_arguments={}, resolved_arguments={}
    )
    manager.finish_tool_call(call, raw_result=[], normalized_result=[])
    manager.finish_stage(stage, {})
    manager.deactivate()
    assert manager.finish_run("SUCCESS") == (None, None)
    assert not (tmp_path / "outputs").exists()
    assert not (tmp_path / "docs").exists()


class _BrokenDiagnostic:
    name = "broken"
    schema_version = "1.0"

    def inspect(self, context):
        raise RuntimeError("diagnostic exploded")


def test_diagnostic_failure_does_not_change_success_business_status(tmp_path: Path) -> None:
    manager = RuntimeArtifactManager(
        "paper",
        config=_config(tmp_path),
        run_id="success-run",
        diagnostics=[_BrokenDiagnostic()],
    )
    manager.record_outcome({"task_status": "partial"})
    manager.finish_run("SUCCESS")

    manifest = json.loads((manager.run_dir / "manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((manager.run_dir / "summary.json").read_text(encoding="utf-8"))
    detail = json.loads(
        (manager.run_dir / "diagnostics" / "broken.json").read_text(encoding="utf-8")
    )
    assert manifest["status"] == "SUCCESS"
    assert manifest["runtime_diagnostics"] == [
        {"diagnostic_name": "broken", "schema_version": "1.0"}
    ]
    assert summary["run"]["status"] == "SUCCESS"
    assert summary["outcome"] == {"task_status": "partial"}
    assert summary["diagnostics"][0]["status"] == "ERROR"
    assert detail["status"] == "ERROR"


def test_finish_run_automatically_classifies_current_reader_failure(tmp_path: Path) -> None:
    manager = RuntimeArtifactManager("paper", config=_config(tmp_path), run_id="reader-run")
    call = manager.start_tool_call(
        "reader",
        agent_arguments={"artifact_id": "art_missing"},
        resolved_arguments={"artifact_id": "art_missing", "char_start": 0, "max_chars": 10},
        agent_tool_call_id="agent-call-1",
    )
    manager.fail_tool_call(call, ValueError("unknown artifact_id 'art_missing'"))
    manager.finish_run("SUCCESS")

    detail = json.loads(
        (manager.run_dir / "diagnostics" / "reader.json").read_text(
            encoding="utf-8"
        )
    )
    summary = json.loads((manager.run_dir / "summary.json").read_text(encoding="utf-8"))
    assert detail["status"] == "WARNING"
    assert detail["classification_counts"] == {"NEVER_PERSISTED": 1}
    assert detail["findings"][0]["agent_tool_call_id"] == "agent-call-1"
    assert summary["diagnostics"][0]["primary_code"] == "NEVER_PERSISTED"


class _DefaultArguments(StrictModel):
    query: str
    max_results: int = 10


class _SearchTool:
    name = "web_search"
    description = "test"
    args_schema = _DefaultArguments

    async def ainvoke(self, arguments, *, scope):
        return ResearcherToolObservation(
            tool_name=self.name,
            arguments=arguments.model_dump(),
            succeeded=True,
            payload={"search_result": {"results": []}},
        )

    def project_model_context(self, observation):
        return observation.payload["search_result"]


class _Model:
    def __init__(self):
        self.responses = [
            ModelResponse(content=None, tool_calls=(ModelToolCall(
                id="agent-1", name="web_search", arguments={"query": "q"}
            ),)),
            ModelResponse(content="done"),
        ]

    async def acomplete(self, messages, *, options=None):
        return self.responses.pop(0)


def test_harness_records_agent_and_schema_resolved_arguments(tmp_path: Path) -> None:
    request = TaskResearchRequest(
        subject_paper_id="paper",
        run_id="run",
        novelty_point=NoveltyPoint(
            point_id="NP-1", claim="claim", technical_features=["feature"]
        ),
        research_task=ResearchTask(
            task_id="T-1", novelty_point_id="NP-1", task_type="search", language="en"
        ),
        search_plan=minimal_search_plan("T-1", "NP-1"),
    )
    manager = RuntimeArtifactManager("paper", config=_config(tmp_path))
    manager.activate()
    asyncio.run(ToolCallHarness(
        _Model(), ResearcherToolRegistry([_SearchTool()])
    ).run(system_prompt="system", initial_user_message="task", scope=request))
    manager.deactivate()
    manager.finish_run("SUCCESS")

    payload = json.loads(next((manager.run_dir / "tools").glob("*.json")).read_text(encoding="utf-8"))
    assert payload["agent_arguments"] == {"query": "q"}
    assert payload["resolved_arguments"] == {"query": "q", "max_results": 10}
    assert payload["execution_status"] == "SUCCESS"
    assert payload["business_status"] == "EMPTY"


def test_final_evidence_sufficiency_facts_are_in_stage_and_summary(
    tmp_path: Path,
) -> None:
    manager = RuntimeArtifactManager(
        "paper",
        config=_config(tmp_path),
        runtime_config={
            "project": {
                "workflow": {
                    "max_rounds": 2,
                    "min_final_evidence_cards_per_point": 2,
                }
            }
        },
        stage_names=[
            "check_final_evidence_sufficiency",
            "plan_supplement",
        ],
    )
    manager.activate()
    stage = manager.start_stage(
        "check_final_evidence_sufficiency",
        {
            "brief": {
                "novelty_points": [
                    {"point_id": "NP-1"},
                    {"point_id": "NP-2"},
                ]
            },
            "evidence_cards": [
                {"novelty_point_id": "NP-1"},
                {"novelty_point_id": "NP-1"},
                {"novelty_point_id": "NP-2"},
            ],
            "rounds": 1,
        },
    )
    manager.finish_stage(
        stage,
        {
            "insufficient_final_evidence_points": [
                {
                    "novelty_point_id": "NP-2",
                    "valid_card_count": 1,
                    "required_card_count": 2,
                    "reason": "insufficient_final_evidence",
                }
            ]
        },
    )
    supplement = manager.start_stage("plan_supplement", {"rounds": 1})
    manager.finish_stage(supplement, {"rounds": 2})
    manager.deactivate()
    manager.finish_run("SUCCESS")

    meta = json.loads((stage.directory / "meta.json").read_text(encoding="utf-8"))
    details = meta["debug_details"]["final_evidence_sufficiency"]
    assert details["configured_cut"] == 2
    assert details["check_status"] == "INSUFFICIENT"
    assert details["input_final_valid_card_count"] == 3
    assert details["point_results"] == [
        {
            "novelty_point_id": "NP-1",
            "required_card_count": 2,
            "status": "PASS",
            "valid_card_count": 2,
        },
        {
            "novelty_point_id": "NP-2",
            "required_card_count": 2,
            "status": "INSUFFICIENT",
            "valid_card_count": 1,
        },
    ]
    assert details["output_matches_calculation"] is True
    assert details["round_limit_allows_supplement"] is True

    summary = json.loads((manager.run_dir / "summary.json").read_text(encoding="utf-8"))
    check = summary["final_evidence_sufficiency_checks"][0]
    assert check["stage_status"] == "SUCCESS"
    assert check["actual_next_stage"] == "plan_supplement"
    assert check["reported_insufficient_final_evidence_points"][0][
        "reason"
    ] == "insufficient_final_evidence"
    markdown = (manager.run_dir / "summary.md").read_text(encoding="utf-8")
    assert "## Final Evidence Sufficiency Checks" in markdown
    assert "| NP-2 | 1 | 2 | INSUFFICIENT |" in markdown


def test_reviewer_scope_and_output_facts_are_in_stage_and_summary(
    tmp_path: Path,
) -> None:
    manager = RuntimeArtifactManager(
        "paper",
        config=_config(tmp_path),
        stage_names=["review_evidence", "validate_synthesis_input"],
    )
    manager.activate()
    stage = manager.start_stage(
        "review_evidence",
        {
            "novelty_points": [{"point_id": "NP-1"}, {"point_id": "NP-2"}],
            "validator_accepted_cards": [
                {
                    "card_id": "C-1",
                    "novelty_point_id": "NP-1",
                    "evidence_ids": ["E-1", "E-missing"],
                }
            ],
            "raw_evidence": [
                {
                    "evidence_id": "E-1",
                    "novelty_point_id": "NP-1",
                    "artifact_id": "A-1",
                }
            ],
        },
    )
    manager.finish_stage(
        stage,
        {
            "evidence_cards": [
                {
                    "card_id": "C-1",
                    "novelty_point_id": "NP-1",
                    "evidence_ids": ["E-1", "E-missing"],
                }
            ],
            "novelty_reviews": [
                {
                    "novelty_point_id": "NP-1",
                    "status": "insufficient_evidence",
                    "verdict": None,
                    "confidence": None,
                    "highly_relevant_works": [],
                    "supplement_request": {"reason": "missing detail"},
                }
            ],
        },
    )
    next_stage = manager.start_stage("validate_synthesis_input", {})
    manager.finish_stage(next_stage, {})
    manager.deactivate()
    manager.finish_run("SUCCESS")

    meta = json.loads((stage.directory / "meta.json").read_text(encoding="utf-8"))
    details = meta["debug_details"]["reviewer_information_adjudication"]
    assert details["cards_preserved"] is True
    assert details["missing_review_point_ids"] == ["NP-2"]
    assert details["unresolved_evidence_ids"] == ["E-missing"]
    assert details["point_scopes"][0]["allowed_artifact_ids"] == ["A-1"]
    assert details["supplement_requests_control_route"] is False

    summary = json.loads((manager.run_dir / "summary.json").read_text(encoding="utf-8"))
    check = summary["reviewer_information_adjudication_checks"][0]
    assert check["actual_next_stage"] == "validate_synthesis_input"
    markdown = (manager.run_dir / "summary.md").read_text(encoding="utf-8")
    assert "## Reviewer Information Adjudication" in markdown
    assert "| NP-1 | insufficient_evidence | - | 0 | True |" in markdown


def test_reader_content_count_precedes_empty_material_catalog() -> None:
    assert _infer_result_count({"material_catalog": [], "read_result": {
        "char_start": 0, "char_end": 100, "text": "x" * 100}}) == 1
    assert _infer_result_count({"material_catalog": [], "read_result": {
        "char_start": 100, "char_end": 100, "text": ""}}) == 0
    assert _infer_result_count({"read_results": [
        {"char_start": 0, "char_end": 10}, {"char_start": 10, "char_end": 10}]}) == 1
