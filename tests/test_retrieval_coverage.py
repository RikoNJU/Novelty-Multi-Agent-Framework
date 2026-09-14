"""检索覆盖判定：只有完整覆盖才允许基于"未检索到"的结论。

回归要点（Run D 场景）：arXiv 执行失败、模型改用 null_catalog 得到"成功但零命中"，
既不能算完整覆盖，也不能让 Reviewer 的 novel 裁定成立。
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

import pytest

from novelty_agent_framework.agents import DemoCoordinator
from novelty_agent_framework.core import (
    RuntimeArtifactManager,
    RuntimeDebugConfig,
    apply_coverage_policy,
    assess_coverage,
    assess_point_coverage,
    coverage_limitations,
    required_retrieval_sources,
    testing_only_retrieval_sources as non_evidentiary_sources,
    zero_card_reason,
)
from novelty_agent_framework.core.retrieval_coverage import (
    CoverageState,
    SourceState,
)
from novelty_agent_framework.schemas import (
    NoveltyPoint,
    NoveltyPointReview,
    NoveltyBrief,
    PaperInput,
    SupplementRequest,
    NoveltyVerdict,
    RelevantWork,
    ReviewStatus,
    SearchExecution,
    SearchExecutionStatus,
    SearchResultRef,
    TaskResearchResult,
    TaskResearchStatus,
)
from novelty_agent_framework.workflows import NoveltyWorkflow, NoveltyWorkflowServices

NOW = datetime(2026, 9, 14, tzinfo=timezone.utc)

#: 与线上一致的来源配置：arxiv 是必要来源，null_catalog 只是测试桩。
RUN_D_CONFIG = {
    "researcher": {
        "tools": {
            "database_search": {
                "providers": {
                    "arxiv": {"enabled": True},
                    "null_catalog": {"enabled": True, "testing_only": True},
                }
            }
        }
    }
}


def _execution(
    source_id: str,
    status: SearchExecutionStatus,
    *,
    hits: int = 0,
    suffix: str = "",
) -> SearchExecution:
    return SearchExecution(
        execution_id=f"exec-{source_id}-{status.value}{suffix}",
        tool_name="database_search",
        source_id=source_id,
        query="query",
        status=status,
        started_at=NOW,
        completed_at=NOW,
        results=[
            SearchResultRef(source_record_id=f"record-{index}", rank=index + 1)
            for index in range(hits)
        ],
    )


def _result(point_id: str, executions) -> TaskResearchResult:
    return TaskResearchResult(
        task_id=f"T-{point_id}",
        novelty_point_id=point_id,
        status=TaskResearchStatus.COMPLETED,
        retrieval_executions=list(executions),
        steps_used=1,
    )


def _coverage(executions):
    return assess_point_coverage(
        novelty_point_id="NP-1",
        executions=executions,
        required_sources=required_retrieval_sources(RUN_D_CONFIG),
        testing_only_sources=non_evidentiary_sources(RUN_D_CONFIG),
    )


def _review(verdict: NoveltyVerdict) -> NoveltyPointReview:
    return NoveltyPointReview(
        novelty_point_id="NP-1",
        status=ReviewStatus.REVIEWED,
        verdict=verdict,
        verdict_reason="reviewer reason",
        confidence=0.8,
        highly_relevant_works=[
            RelevantWork(
                work_id="work-1",
                card_ids=["card-1"],
                evidence_ids=["evidence-1"],
                relevance_reason="overlap",
            )
        ],
    )


def _insufficient_review(point_id: str = "NP-1") -> NoveltyPointReview:
    """复现真实 Reviewer 在 0 卡时的短路结果（同一句固定 reason）。"""

    return NoveltyPointReview(
        novelty_point_id=point_id,
        status=ReviewStatus.INSUFFICIENT_EVIDENCE,
        supplement_request=SupplementRequest(
            reason="当前查新点没有可供可靠判定的已绑定证据。"
        ),
    )


class _StaticReviewer:
    """返回固定裁定的 Reviewer，用于验证工作流侧的强制降级。"""

    def __init__(self, review: NoveltyPointReview) -> None:
        self._review_value = review

    def review(self, request):
        return self._review_value


def test_required_sources_exclude_testing_only_providers() -> None:
    assert required_retrieval_sources(RUN_D_CONFIG) == ("arxiv",)
    assert non_evidentiary_sources(RUN_D_CONFIG) == ("null_catalog",)


def test_contract_absent_is_empty() -> None:
    assert required_retrieval_sources(None) == ()
    assert required_retrieval_sources({}) == ()


def test_zero_hit_with_complete_coverage_permits_absence_conclusion() -> None:
    coverage = _coverage(
        [_execution("arxiv", SearchExecutionStatus.SUCCEEDED, hits=0)]
    )

    assert coverage.state is CoverageState.COMPLETE
    assert coverage.zero_hit_sources == ["arxiv"]
    assert coverage.permits_absence_conclusion is True
    assert coverage.sources[0].state is SourceState.OK
    assert coverage.sources[0].empty == 1


def test_succeeded_with_hits_is_complete_coverage() -> None:
    coverage = _coverage(
        [_execution("arxiv", SearchExecutionStatus.SUCCEEDED, hits=2)]
    )

    assert coverage.state is CoverageState.COMPLETE
    assert coverage.zero_hit_sources == []


def test_single_failed_execution_degrades_coverage() -> None:
    coverage = _coverage(
        [
            _execution("arxiv", SearchExecutionStatus.SUCCEEDED, hits=1, suffix="-a"),
            _execution("arxiv", SearchExecutionStatus.FAILED, suffix="-b"),
        ]
    )

    assert coverage.state is CoverageState.PARTIAL
    assert coverage.permits_absence_conclusion is False
    assert coverage.degraded_sources == ["arxiv"]
    assert coverage.failed_sources == []


def test_all_failed_is_failed_state() -> None:
    coverage = _coverage([_execution("arxiv", SearchExecutionStatus.FAILED)])

    assert coverage.state is CoverageState.FAILED
    assert coverage.permits_absence_conclusion is False


def test_run_d_shape_failure_is_not_zero_hit() -> None:
    """arXiv 失败 + null_catalog 成功但为空，不得读作"检索成功零命中"。"""

    coverage = _coverage(
        [
            _execution("arxiv", SearchExecutionStatus.FAILED, suffix="-1"),
            _execution("arxiv", SearchExecutionStatus.FAILED, suffix="-2"),
            _execution("null_catalog", SearchExecutionStatus.SUCCEEDED, hits=0),
        ]
    )

    assert coverage.state is CoverageState.FAILED
    assert coverage.failed_sources == ["arxiv"]
    # null_catalog 是测试桩，它的"零命中"永远不能成为无文献的证据。
    assert coverage.zero_hit_sources == []
    assert coverage.permits_absence_conclusion is False
    non_evidentiary = [
        item.source_id
        for item in coverage.sources
        if item.state is SourceState.NON_EVIDENTIARY
    ]
    assert non_evidentiary == ["null_catalog"]


def test_no_execution_is_not_attempted() -> None:
    coverage = _coverage([])

    assert coverage.state is CoverageState.NOT_ATTEMPTED
    assert coverage.not_attempted_sources == ["arxiv"]
    assert coverage.permits_absence_conclusion is False


def test_missing_contract_blocks_absence_conclusion() -> None:
    coverage = assess_point_coverage(
        novelty_point_id="NP-1",
        executions=[_execution("arxiv", SearchExecutionStatus.SUCCEEDED)],
        required_sources=(),
    )

    assert coverage.state is CoverageState.UNCONFIGURED
    assert coverage.permits_absence_conclusion is False


def test_assess_coverage_groups_executions_by_point() -> None:
    coverages = assess_coverage(
        point_ids=["NP-1", "NP-2"],
        task_results=[
            _result("NP-1", [_execution("arxiv", SearchExecutionStatus.SUCCEEDED)]),
            _result("NP-2", [_execution("arxiv", SearchExecutionStatus.FAILED)]),
        ],
        required_sources=("arxiv",),
    )

    assert [item.state for item in coverages] == [
        CoverageState.COMPLETE,
        CoverageState.FAILED,
    ]


@pytest.mark.parametrize(
    "verdict", [NoveltyVerdict.NOVEL, NoveltyVerdict.PARTIALLY_NOVEL]
)
def test_policy_downgrades_absence_verdicts_without_complete_coverage(
    verdict: NoveltyVerdict,
) -> None:
    coverage = _coverage([_execution("arxiv", SearchExecutionStatus.FAILED)])
    enforced, downgrades = apply_coverage_policy([_review(verdict)], [coverage])

    assert enforced[0].status.value == "insufficient_evidence"
    assert enforced[0].verdict is None
    assert enforced[0].verdict_reason is None
    assert enforced[0].confidence is None
    # 已检索到的高相关工作是事实，降级时保留。
    assert enforced[0].highly_relevant_works == _review(verdict).highly_relevant_works
    assert enforced[0].supplement_request is not None
    assert downgrades[0].previous_verdict is verdict
    assert downgrades[0].coverage_state is CoverageState.FAILED


def test_policy_keeps_absence_verdict_when_coverage_is_complete() -> None:
    coverage = _coverage([_execution("arxiv", SearchExecutionStatus.SUCCEEDED)])
    review = _review(NoveltyVerdict.NOVEL)
    enforced, downgrades = apply_coverage_policy([review], [coverage])

    assert enforced == [review]
    assert downgrades == []


def test_policy_keeps_positive_findings_under_failed_coverage() -> None:
    """找到高度重合的文献是正面证据，不因检索覆盖不完整而撤销。"""

    coverage = _coverage([_execution("arxiv", SearchExecutionStatus.FAILED)])
    review = _review(NoveltyVerdict.NOT_NOVEL)
    enforced, downgrades = apply_coverage_policy([review], [coverage])

    assert enforced == [review]
    assert downgrades == []


def _workflow(tmp_path, reviewer) -> NoveltyWorkflow:
    default = NoveltyWorkflow.default()
    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=DemoCoordinator(),
            task_researcher=default.services.task_researcher,
            search_planner=default.services.search_planner,
            reviewer=reviewer,
        ),
        runtime_config=RUN_D_CONFIG,
        output_root=tmp_path / "outputs",
    )


def _review_state(executions):
    point = NoveltyPoint(point_id="NP-1", claim="claim")
    return {
        "paper": PaperInput(
            paper_id="paper-1", title="Paper", full_text="body"
        ),
        "novelty_points": [point],
        "all_research_tasks": [],
        "raw_evidence": [],
        "raw_evidence_cards": [],
        "evidence_cards": [],
        "validator_accepted_cards": [],
        "rejected_evidence": [],
        "review_decisions": [],
        "task_research_results": [_result("NP-1", executions)],
    }


def test_workflow_downgrades_novel_verdict_when_coverage_incomplete(tmp_path) -> None:
    workflow = _workflow(tmp_path, _StaticReviewer(_review(NoveltyVerdict.NOVEL)))
    state = _review_state(
        [_execution("arxiv", SearchExecutionStatus.FAILED)]
    )

    output = asyncio.run(workflow._review_evidence(state))

    review = output["novelty_reviews"][0]
    assert review.status.value == "insufficient_evidence"
    assert review.verdict is None
    assert output["retrieval_coverage"][0].state is CoverageState.FAILED
    assert [issue.code for issue in output["issues"]] == [
        "retrieval_coverage_insufficient"
    ]


def test_workflow_keeps_novel_verdict_when_coverage_complete(tmp_path) -> None:
    workflow = _workflow(tmp_path, _StaticReviewer(_review(NoveltyVerdict.NOVEL)))
    state = _review_state(
        [_execution("arxiv", SearchExecutionStatus.SUCCEEDED)]
    )

    output = asyncio.run(workflow._review_evidence(state))

    review = output["novelty_reviews"][0]
    assert review.verdict is NoveltyVerdict.NOVEL
    assert output["retrieval_coverage"][0].state is CoverageState.COMPLETE
    assert output["issues"] == []


def test_runtime_summary_records_retrieval_coverage(tmp_path) -> None:
    """覆盖事实必须进 runtime 审计：报告之外还要能查到“为什么只给了证据不足”。"""

    workflow = _workflow(tmp_path, _StaticReviewer(_review(NoveltyVerdict.NOVEL)))
    state = _review_state([_execution("arxiv", SearchExecutionStatus.FAILED)])
    manager = RuntimeArtifactManager(
        "paper-1",
        config=RuntimeDebugConfig(
            output_root=tmp_path / "outputs",
            archive_root=tmp_path / "archive",
        ),
        run_id="run-coverage",
        runtime_config=RUN_D_CONFIG,
        enabled_tools=["database_search"],
    )
    manager.activate()
    try:
        asyncio.run(
            workflow._record_stage(
                "review_evidence", workflow._review_evidence
            )(state)
        )
    finally:
        manager.deactivate()
    manager.finish_run("SUCCESS")

    summary = json.loads(
        (manager.run_dir / "summary.json").read_text(encoding="utf-8")
    )
    checks = summary["retrieval_coverage_checks"]
    assert len(checks) == 1
    coverage = checks[0]["coverages"][0]
    assert coverage["state"] == "failed"
    assert coverage["failed_sources"] == ["arxiv"]
    assert coverage["zero_hit_sources"] == []

    rendered = (manager.run_dir / "summary.md").read_text(encoding="utf-8")
    assert "## Retrieval Coverage" in rendered


def test_zero_card_reason_differs_by_cause() -> None:
    reasons = {
        "failed": zero_card_reason(
            _coverage([_execution("arxiv", SearchExecutionStatus.FAILED)])
        ),
        "zero_hit": zero_card_reason(
            _coverage([_execution("arxiv", SearchExecutionStatus.SUCCEEDED)])
        ),
        "not_attempted": zero_card_reason(_coverage([])),
    }

    assert len(set(reasons.values())) == 3
    assert "检索执行失败" in reasons["failed"]
    assert "零命中" in reasons["zero_hit"]
    assert "没有检索执行记录" in reasons["not_attempted"]
    assert "在本次检索范围内未见相同报道" in reasons["zero_hit"]
    assert "未见相同报道" not in reasons["failed"]
    # 不得退回 Reviewer 的固定兜底句。
    assert all(
        "没有可供可靠判定的已绑定证据" not in item
        for item in reasons.values()
    )


def test_coverage_limitations_scope() -> None:
    complete = _coverage([_execution("arxiv", SearchExecutionStatus.SUCCEEDED)])
    failed = _coverage([_execution("arxiv", SearchExecutionStatus.FAILED)])

    # 完整覆盖且有卡片不写；完整覆盖但 0 卡写零命中；覆盖不完整无论有无卡片都写。
    assert coverage_limitations([complete], zero_card_points=[]) == []
    assert len(coverage_limitations([complete], zero_card_points=["NP-1"])) == 1
    assert len(coverage_limitations([failed], zero_card_points=[])) == 1


@pytest.mark.parametrize(
    ("executions", "expected"),
    [
        ([_execution("arxiv", SearchExecutionStatus.FAILED)], "检索执行失败"),
        ([
            _execution("arxiv", SearchExecutionStatus.SUCCEEDED)
        ], "检索完整执行但零命中"),
        ([], "没有检索执行记录"),
    ],
)
def test_workflow_replaces_generic_zero_card_reason(
    tmp_path, executions, expected
) -> None:
    workflow = _workflow(tmp_path, _StaticReviewer(_insufficient_review()))
    output = asyncio.run(workflow._review_evidence(_review_state(executions)))

    reason = output["novelty_reviews"][0].supplement_request.reason
    assert reason.startswith(expected)
    assert "没有可供可靠判定的已绑定证据" not in reason


def test_synthesize_report_appends_deterministic_coverage_limitations(
    tmp_path,
) -> None:
    workflow = _workflow(tmp_path, _StaticReviewer(_insufficient_review()))
    point = NoveltyPoint(point_id="NP-1", claim="claim")
    state = {
        "paper": PaperInput(
            paper_id="paper-1", title="Paper", full_text="body"
        ),
        "novelty_points": [point],
        "brief": NoveltyBrief(
            paper_summary="summary", novelty_points=[point], research_tasks=[]
        ),
        "evidence_cards": [],
        "novelty_reviews": [_insufficient_review()],
        "rejected_evidence": [],
        "insufficient_final_evidence_points": [],
        "retrieval_coverage": [
            _coverage([_execution("arxiv", SearchExecutionStatus.FAILED)])
        ],
    }

    report = asyncio.run(workflow._synthesize_report(state))["report"]

    assert any(
        item.startswith("NP-1：检索执行失败") for item in report.limitations
    )


class _Observation:
    def __init__(self, payload) -> None:
        self.payload = payload


class _Event:
    def __init__(self, payload) -> None:
        self.kind = "tool_result"
        self.observation = _Observation(payload)


def test_retrieval_executions_deduplicate_repeated_ids() -> None:
    """共享 request gate 会把旧执行在后续 bundle 里重复带回。

    重复计数会把“arxiv 失败 1 次”放大成“失败 3 次”，进而污染覆盖统计与报告
    措辞，因此必须按 execution_id 去重。
    """

    from novelty_agent_framework.workflows.research_task import (
        _retrieval_executions,
    )

    execution = _execution("arxiv", SearchExecutionStatus.FAILED)
    payload = {"search_executions": [execution.model_dump(mode="json")]}
    trace = [_Event(payload), _Event(payload), _Event(payload)]

    collected = _retrieval_executions(trace)

    assert len(collected) == 1
    assert collected[0].execution_id == execution.execution_id
