"""基于 LangGraph 的论文查新总分总工作流。"""

from __future__ import annotations

import asyncio
import inspect
import json
import re
import uuid
from collections.abc import Awaitable
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Mapping, TypeVar, cast

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from pydantic import ValidationError

from novelty_agent_framework.core.errors import WorkflowExecutionError
from novelty_agent_framework.core.integrity_gates import (
    validate_report_integrity,
    validate_synthesis_input,
)
from novelty_agent_framework.core.report_binding import bind_reviews_to_report
from novelty_agent_framework.core.retrieval_coverage import (
    RetrievalCoverage,
    apply_coverage_policy,
    assess_coverage,
    coverage_limitations,
    required_retrieval_sources,
    testing_only_retrieval_sources,
    zero_card_reason,
)
from novelty_agent_framework.core.runtime_artifacts import (
    RuntimeArtifactManager,
    current_runtime_artifacts,
)
from novelty_agent_framework.persistence import (
    ReferenceStore,
    persist_evidence_cards,
    persist_novelty_points,
    persist_novelty_reviews,
    persist_report,
    persist_retrieval_plans,
    persist_task_research_result,
    persist_task_retrieval_audit,
    persist_workflow_input,
)
from novelty_agent_framework.tools.renderer import render_report

from ..agents import (
    DefaultEvidenceValidator,
    DemoCoordinator,
    DemoPointExtractor,
    DemoSearchPlanner,
    DemoTaskResearcher,
    build_paper_digest,
)
from ..schemas import (
    EvidenceCard,
    InsufficientFinalEvidence,
    IssueSeverity,
    NoveltyBrief,
    NoveltyPoint,
    NoveltyPointReview,
    NoveltyPointReviewRequest,
    ReviewStatus,
    SupplementRequest,
    NoveltyReport,
    NoveltyRunResult,
    PaperInput,
    RejectedEvidence,
    ResearchTask,
    SearchPlan,
    TaskResearchRequest,
    TaskResearchResult,
    TaskResearchStatus,
    WorkflowIssue,
)
from .state import NoveltyState, NoveltyWorkflowConfig, NoveltyWorkflowServices

T = TypeVar("T")

_STAGE_NAMES = (
    "extract_points",
    "resolve_subject_references",
    "plan",
    "dispatch_planning_tasks",
    "plan_research_task",
    "dispatch_research_tasks",
    "run_research_task",
    "validate_evidence",
    "review_evidence",
    "validate_synthesis_input",
    "check_final_evidence_sufficiency",
    "plan_supplement",
    "synthesize_report",
    "validate_report_integrity",
    "persist_report",
    "render_report",
)


async def _resolve(value: T | Awaitable[T]) -> T:
    """兼容同步实现和异步实现，便于接入不同模型 SDK。"""

    if inspect.isawaitable(value):
        return await cast(Awaitable[T], value)
    return value


def _safe_error(exc: Exception) -> str:
    message = re.sub(
        r"(?i)(api[_-]?key|authorization|cookie)\s*[:=]\s*\S+",
        r"\1=<redacted>",
        str(exc),
    )
    message = re.sub(r"(?:/[\w. -]+){2,}", "<path>", message)
    return f"{type(exc).__name__}: {message}"[:1000]


def _insufficient_point_review(
    point_id: str, reason: str
) -> NoveltyPointReview:
    return NoveltyPointReview(
        novelty_point_id=point_id,
        status=ReviewStatus.INSUFFICIENT_EVIDENCE,
        supplement_request=SupplementRequest(reason=reason),
    )


class NoveltyWorkflow:
    """把规划、并行调研、证据门控和汇总组织成可运行闭环。"""

    @classmethod
    def default(cls) -> "NoveltyWorkflow":
        """构造默认查新工作流。

        当前项目采用固定 Agent 组合，因此默认装配逻辑直接放在工作流类中。
        """

        return cls(
            NoveltyWorkflowServices(
                coordinator=DemoCoordinator(),
                task_researcher=DemoTaskResearcher(),
                search_planner=DemoSearchPlanner(),
                point_extractor=DemoPointExtractor(),
            )
        )

    def __init__(
        self,
        services: NoveltyWorkflowServices,
        config: NoveltyWorkflowConfig | None = None,
        *,
        runtime_config: Mapping[str, Any] | None = None,
        output_root: str | Path | None = None,
    ) -> None:
        self.services = services
        self.config = config or NoveltyWorkflowConfig()
        self.output_root = Path(
            output_root
            if output_root is not None
            else self.config.runtime_debug.output_root
        )
        if Path(self.config.runtime_debug.output_root) != self.output_root:
            self.config = replace(
                self.config,
                runtime_debug=replace(
                    self.config.runtime_debug, output_root=self.output_root
                ),
            )
        self.validator = services.validator or DefaultEvidenceValidator()
        self.point_extractor = services.point_extractor or DemoPointExtractor()
        evidence_builder = getattr(services.task_researcher, "evidence_builder", None)
        self.reference_store = (
            getattr(evidence_builder, "reference_store", None)
            or getattr(services.task_researcher, "reference_store", None)
            or ReferenceStore(self.output_root)
        )
        self.runtime_config = dict(runtime_config or {})
        self.last_runtime_run_id: str | None = None
        self.last_rendered_report_path: str | None = None
        self.graph = self._build_graph()

    def _build_graph(self) -> Any:
        builder = StateGraph(NoveltyState)
        builder.add_node(
            "extract_points", self._record_stage("extract_points", self._extract_points)
        )
        builder.add_node(
            "resolve_subject_references",
            self._record_stage(
                "resolve_subject_references",
                self._resolve_subject_references,
            ),
        )
        builder.add_node("plan", self._record_stage("plan", self._plan))
        builder.add_node(
            "dispatch_planning_tasks",
            self._record_stage("dispatch_planning_tasks", self._dispatch_node),
        )
        builder.add_node(
            "plan_research_task",
            self._record_stage("plan_research_task", self._plan_research_task),
        )
        builder.add_node(
            "dispatch_research_tasks",
            self._record_stage("dispatch_research_tasks", self._dispatch_node),
        )
        builder.add_node(
            "run_research_task",
            self._record_stage("run_research_task", self._run_research_task),
        )
        builder.add_node(
            "validate_evidence",
            self._record_stage("validate_evidence", self._validate_evidence),
        )
        builder.add_node(
            "review_evidence",
            self._record_stage("review_evidence", self._review_evidence),
        )
        builder.add_node(
            "validate_synthesis_input",
            self._record_stage(
                "validate_synthesis_input", self._validate_synthesis_input
            ),
        )
        builder.add_node(
            "check_final_evidence_sufficiency",
            self._record_stage(
                "check_final_evidence_sufficiency",
                self._check_final_evidence_sufficiency,
            ),
        )
        builder.add_node(
            "plan_supplement",
            self._record_stage("plan_supplement", self._plan_supplement),
        )
        builder.add_node(
            "synthesize_report",
            self._record_stage("synthesize_report", self._synthesize_report),
        )
        builder.add_node(
            "validate_report_integrity",
            self._record_stage(
                "validate_report_integrity", self._validate_report_integrity
            ),
        )
        builder.add_node(
            "persist_report",
            self._record_stage("persist_report", self._persist_report),
        )
        builder.add_node(
            "render_report",
            self._record_stage("render_report", self._render_report),
        )

        builder.add_edge(START, "extract_points")
        builder.add_edge("extract_points", "resolve_subject_references")
        builder.add_edge("resolve_subject_references", "plan")
        builder.add_edge("plan", "dispatch_planning_tasks")
        builder.add_conditional_edges(
            "dispatch_planning_tasks",
            self._dispatch_planning_tasks,
            ["plan_research_task", "dispatch_research_tasks"],
        )
        builder.add_edge("plan_research_task", "dispatch_research_tasks")
        builder.add_conditional_edges(
            "dispatch_research_tasks",
            self._dispatch_research_tasks,
            ["run_research_task", "validate_evidence"],
        )
        builder.add_edge("run_research_task", "validate_evidence")
        builder.add_edge("validate_evidence", "review_evidence")
        builder.add_edge("review_evidence", "validate_synthesis_input")
        builder.add_edge(
            "validate_synthesis_input", "check_final_evidence_sufficiency"
        )
        builder.add_conditional_edges(
            "check_final_evidence_sufficiency",
            self._route_after_evidence_sufficiency_check,
            {
                "supplement": "plan_supplement",
                "synthesize": "synthesize_report",
            },
        )
        builder.add_edge("plan_supplement", "dispatch_planning_tasks")
        builder.add_edge("synthesize_report", "validate_report_integrity")
        builder.add_edge("validate_report_integrity", "persist_report")
        builder.add_edge("persist_report", "render_report")
        builder.add_edge("render_report", END)
        return builder.compile()

    @staticmethod
    def _record_stage(
        stage_name: str,
        function: Callable[[NoveltyState], Awaitable[dict[str, Any]]],
    ) -> Callable[[NoveltyState], Awaitable[dict[str, Any]]]:
        """Instrument a graph node without giving business agents artifact duties."""

        async def recorded(state: NoveltyState) -> dict[str, Any]:
            runtime = current_runtime_artifacts()
            if runtime is None:
                return await function(state)
            handle = runtime.start_stage(stage_name, state)
            try:
                output = await function(state)
            except BaseException as exc:
                runtime.fail_stage(handle, exc)
                raise
            runtime.finish_stage(handle, output)
            return output

        recorded.__name__ = f"runtime_recorded_{stage_name}"
        return recorded

    async def _resolve_subject_references(
        self, state: NoveltyState
    ) -> dict[str, Any]:
        """按查新点预筛参考文献，只联网解析命中的少数条目。

        入口阶段只做了本地解析（条目状态 SKIPPED）；这里才按查新点挑选值得联网的
        参考文献，避免 90 条引用变成 90 次 arXiv 请求（耗时并触发 429 限流）。
        """

        paper = state["paper"]
        points = list(state.get("novelty_points", []))
        limit = self.config.reference_prefilter_limit
        if not self._arxiv_provider_enabled():
            # 该节点历史上无条件构造 arXiv 工具，绕过了 provider 的 enabled
            # 开关；arXiv 关闭时必须在这里短路，否则配置形同虚设。
            return {}
        if not paper.references or not points or limit <= 0:
            return {}

        from ..persistence import SubjectReferenceStore
        from ..processing.reference_bootstrap import (
            ReferenceBootstrapService,
            ReferenceProviderRegistry,
            ReferenceTarget,
        )
        from ..tools.database_search.providers.arxiv import (
            build_arxiv_search_tool,
        )

        # 只有入口阶段确实准备了本地台账（defer_resolution）才联网：否则说明这条
        # 链路已在入口解析完毕，或者根本没有参考文献语料库。
        store = SubjectReferenceStore(self.output_root)
        try:
            ledger = store.load_bootstrap(paper.paper_id)
        except Exception:
            return {}
        if not any(not entry.attempts for entry in ledger.entries):
            return {}

        targets = [
            ReferenceTarget(
                target_id=point.point_id,
                text=" ".join(
                    [
                        point.claim,
                        point.claim_en,
                        *point.technical_features,
                        *point.technical_features_en,
                    ]
                ).strip(),
            )
            for point in points
        ]
        service = ReferenceBootstrapService(
            ReferenceProviderRegistry(
                [build_arxiv_search_tool(self._arxiv_options())]
            ),
            SubjectReferenceStore(self.output_root),
            # bootstrap 是长批次：串行执行，不与工作流检索叠加请求。
            max_concurrency=1,
        )
        try:
            manifest = await service.bootstrap(
                paper.paper_id,
                list(paper.references),
                targets=targets,
                per_target_limit=limit,
                # 带显式 arXiv ID / DOI / URL 的条目一律解析：实测这类条目才是唯一
                # 解析得动的部分（19 条带 ID 成功 18 条，72 条无 ID 成功 0 条）。
                # 不开这个开关时，预筛选中的 10 条里 6 条注定 not_found，
                # 最终 reference_search 的本地语料只剩个位数。
                include_direct_identifiers=True,
            )
        except Exception as exc:
            # 参考文献解析失败不应击穿查新主流程。
            return {
                "issues": [
                    WorkflowIssue(
                        node="resolve_subject_references",
                        code="subject_reference_resolution_failed",
                        message=(
                            "按查新点解析参考文献失败："
                            f"{_safe_error(exc)}"
                        ),
                        severity=IssueSeverity.WARNING,
                    )
                ]
            }

        attempted = [entry for entry in manifest.entries if entry.attempts]
        return {
            "subject_reference_resolution": {
                "total": len(manifest.entries),
                "attempted": len(attempted),
                "resolved": sum(
                    1
                    for entry in attempted
                    if entry.resolution_status.value == "resolved"
                ),
                "skipped": len(manifest.entries) - len(attempted),
            }
        }

    def _arxiv_options(self) -> dict[str, Any]:
        """读取配置里的 arXiv 限速参数，供 bootstrap 与工作流共用。

        bootstrap 以前用构造函数默认值（比工作流更激进），两条链路叠加极易 429。
        """

        providers = (
            (self.runtime_config or {}).get("researcher", {})
            .get("tools", {})
            .get("database_search", {})
            .get("providers", {})
        )
        options = (
            providers.get("arxiv") if isinstance(providers, Mapping) else None
        )
        return dict(options) if isinstance(options, Mapping) else {}

    def _arxiv_provider_enabled(self) -> bool:
        """arXiv 提供方是否启用；历史配置缺少 enabled 字段时视为启用。"""

        return self._arxiv_options().get("enabled", True) is not False

    async def _extract_points(self, state: NoveltyState) -> dict[str, Any]:
        persist_workflow_input(state["paper"], output_root=self.output_root)
        try:
            digest = build_paper_digest(state["paper"])
            points_value = self.point_extractor.extract(
                digest,
                previous_brief=None,
                attempt=1,
            )
            points = list(await _resolve(points_value))
            validated = [
                point
                if isinstance(point, NoveltyPoint)
                else NoveltyPoint.model_validate(point)
                for point in points
            ]
        except (ValidationError, TypeError, ValueError) as exc:
            raise WorkflowExecutionError(f"查新点提取失败：{exc}") from exc
        if not validated:
            raise WorkflowExecutionError("查新点提取结果为空")
        # 测试版持久化：写入该论文独立工作目录（后续可替换为数据库存储）
        persist_novelty_points(
            state["paper"], validated, output_root=self.output_root
        )
        missing_english = [
            point.point_id
            for point in validated
            if not point.claim_en or not point.technical_features_en
        ]
        issues: list[WorkflowIssue] = []
        if missing_english:
            issues.append(
                WorkflowIssue(
                    node="extract_points",
                    code="missing_english_point",
                    message=(
                        "以下查新点缺少完整英文表述；英文检索任务将由 SearchPlanner "
                        "基于中文内容生成英文检索表达："
                        + ", ".join(missing_english)
                    ),
                    severity=IssueSeverity.WARNING,
                )
            )
        return {"novelty_points": validated, "issues": issues}

    def _apply_task_language_gate(
        self, tasks: Sequence[ResearchTask], *, node: str
    ) -> tuple[list[ResearchTask], list[WorkflowIssue]]:
        """按配置过滤被关闭语言的调研任务，使其不进入规划与派发。

        任务生成、Prompt 和工具代码全部保留；这里只做确定性闸门，并为每个
        被跳过的任务留下审计 Issue。
        """

        enabled = {
            str(code).strip().lower() for code in self.config.enabled_task_languages
        }
        kept: list[ResearchTask] = []
        issues: list[WorkflowIssue] = []
        for task in tasks:
            language = (task.language or "").strip().lower()
            if language in enabled:
                kept.append(task)
                continue
            issues.append(
                WorkflowIssue(
                    node=node,
                    code="task_language_disabled",
                    message=(
                        f"语言 {task.language!r} 已关闭，跳过 "
                        f"{task.novelty_point_id}/{task.task_id} 的方案生成与调研执行。"
                    ),
                    task_id=task.task_id,
                )
            )
        return kept, issues

    async def _plan(self, state: NoveltyState) -> dict[str, Any]:
        try:
            brief_value = self.services.coordinator.plan(
                state["paper"],
                points=state.get("novelty_points", []),
                attempt=1,
            )
            brief = NoveltyBrief.model_validate(await _resolve(brief_value))
        except (ValidationError, TypeError, ValueError) as exc:
            raise WorkflowExecutionError(f"Coordinator 未生成合法 NoveltyBrief：{exc}") from exc

        tasks, issues = self._apply_task_language_gate(
            brief.research_tasks, node="plan"
        )
        return {
            "brief": brief.model_copy(update={"research_tasks": tasks}),
            "research_tasks": tasks,
            "all_research_tasks": tasks,
            "rounds": 1,
            "issues": issues,
        }

    async def _dispatch_node(self, state: NoveltyState) -> dict[str, Any]:
        """显式 fan-out 汇合点；不把全局状态传入任务 Researcher。"""

        return {}

    async def _dispatch_planning_tasks(self, state: NoveltyState):
        tasks = state.get("research_tasks", [])
        if not tasks:
            return "dispatch_research_tasks"
        points = {item.point_id: item for item in state.get("novelty_points", [])}
        sends = [
            Send(
                "plan_research_task",
                {
                    "current_point": points[task.novelty_point_id],
                    "current_task": task,
                    "subject_paper_id": state["paper"].paper_id,
                },
            )
            for task in tasks
            if task.novelty_point_id in points
        ]
        return sends or "dispatch_research_tasks"

    async def _plan_research_task(self, state: NoveltyState) -> dict[str, Any]:
        point = state["current_point"]
        task = state["current_task"]
        try:
            plan_value = self.services.search_planner.plan(point, task)
            plan = SearchPlan.model_validate(await _resolve(plan_value))
        except (ValidationError, TypeError, ValueError) as exc:
            # 韧性：单个任务检索方案失败不应击穿整个查新流程——
            # 记录 PARTIAL 结果与告警，其余任务继续，最终数量检查可见该缺口。
            safe_error = _safe_error(exc)
            result = TaskResearchResult(
                task_id=task.task_id,
                novelty_point_id=point.point_id,
                status=TaskResearchStatus.FAILED,
                warnings=[f"planner failed: {safe_error}"],
                steps_used=0,
            )
            persist_task_research_result(
                state["subject_paper_id"],
                result,
                attempt=task.attempt,
                output_root=self.output_root,
            )
            return {
                "search_plans": [],
                "task_research_results": [result],
                "raw_evidence": [],
                "raw_evidence_cards": [],
                "issues": [
                    WorkflowIssue(
                        node="plan_research_task",
                        code="search_plan_failed",
                        message=(
                            f"检索方案生成失败（{point.point_id}/{task.task_id}）："
                            f"{safe_error}"
                        ),
                        task_id=task.task_id,
                    )
                ],
            }
        if plan.task_id != task.task_id or plan.novelty_point_id != point.point_id:
            raise WorkflowExecutionError(
                f"SearchPlan 与任务绑定不一致：{point.point_id} / {task.task_id}"
            )
        return {"search_plans": [plan]}

    async def _dispatch_research_tasks(self, state: NoveltyState):
        tasks = state.get("research_tasks", [])
        if not tasks:
            return "validate_evidence"
        _require_complete_search_plans(
            state.get("all_research_tasks", tasks), state.get("search_plans", [])
        )
        points = {item.point_id: item for item in state.get("novelty_points", [])}
        plans = {
            (item.novelty_point_id, item.task_id): item
            for item in state.get("search_plans", [])
        }
        persist_retrieval_plans(
            state["paper"],
            state.get("all_research_tasks", []),
            search_plans=state.get("search_plans", []),
            rounds=state.get("rounds", 0),
            point_order=[item.point_id for item in state.get("novelty_points", [])],
            output_root=self.output_root,
        )
        sends = []
        for task in tasks:
            point = points.get(task.novelty_point_id)
            plan = plans.get((task.novelty_point_id, task.task_id))
            if point is None or plan is None:
                continue
            sends.append(
                Send(
                    "run_research_task",
                    {
                        "subject_paper_id": state["paper"].paper_id,
                        "run_id": state["run_id"],
                        "current_point": point,
                        "current_task": task,
                        "current_search_plan": plan,
                    },
                )
            )
        return sends or "validate_evidence"

    async def _run_research_task(self, state: NoveltyState) -> dict[str, Any]:
        task = state["current_task"]
        point = state["current_point"]
        request = TaskResearchRequest(
            subject_paper_id=state["subject_paper_id"],
            run_id=state["run_id"],
            novelty_point=point,
            research_task=task,
            search_plan=state["current_search_plan"],
        )
        try:
            result = TaskResearchResult.model_validate(
                await self.services.task_researcher.ainvoke(request)
            )
            issues: list[WorkflowIssue] = []
        except Exception as exc:
            safe_error = _safe_error(exc)
            result = TaskResearchResult(
                task_id=task.task_id,
                novelty_point_id=point.point_id,
                status=TaskResearchStatus.FAILED,
                warnings=[f"task researcher failed: {safe_error}"],
                steps_used=0,
            )
            issues = [
                WorkflowIssue(
                    node="run_research_task",
                    code="research_task_failed",
                    message=(
                        f"调研任务 {point.point_id} / {task.task_id} 执行失败："
                        f"{safe_error}"
                    ),
                    task_id=task.task_id,
                )
            ]
        persist_task_research_result(
            state["subject_paper_id"],
            result,
            attempt=task.attempt,
            output_root=self.output_root,
        )
        return {
            "task_research_results": [result],
            "raw_evidence": result.evidence,
            "raw_evidence_cards": result.evidence_cards,
            "issues": issues,
        }

    async def _validate_evidence(self, state: NoveltyState) -> dict[str, Any]:
        persist_task_retrieval_audit(
            state["paper"],
            state.get("all_research_tasks", []),
            state.get("task_research_results", []),
            search_plans=state.get("search_plans", []),
            rounds=state.get("rounds", 0),
            point_order=[item.point_id for item in state.get("novelty_points", [])],
            output_root=self.output_root,
        )
        result_value = self.validator.validate(
            state.get("raw_evidence_cards", []),
            tasks=state.get("all_research_tasks", []),
        )
        result = await _resolve(result_value)

        rejected = [
            RejectedEvidence(card_id=card_id, reason=reason)
            for card_id, reason in result.rejected
        ]
        issues = [
            WorkflowIssue(
                node="validate_evidence",
                code=code,
                message=message,
                severity=IssueSeverity(severity),
                task_id=task_id,
            )
            for code, message, severity, task_id in result.issues
        ]
        return {
            "validator_accepted_cards": list(result.accepted),
            "evidence_cards": list(result.accepted),
            "rejected_evidence": rejected,
            "issues": issues,
        }

    def _assess_retrieval_coverage(
        self, state: NoveltyState
    ) -> list[RetrievalCoverage]:
        """按查新点聚合检索覆盖事实。

        必要来源来自配置（启用且非 testing_only），执行成败来自工具观测；
        两者共同决定该点能否支撑基于“未检索到”的否定性结论。
        """

        point_ids = [
            point.point_id for point in state.get("novelty_points", [])
        ]
        return assess_coverage(
            point_ids=point_ids,
            task_results=state.get("task_research_results", []),
            required_sources=required_retrieval_sources(self.runtime_config),
            testing_only_sources=testing_only_retrieval_sources(
                self.runtime_config
            ),
        )

    async def _review_evidence(self, state: NoveltyState) -> dict[str, Any]:
        """按 NoveltyPoint 综合证据；Reviewer 不过滤 Validator 放行的卡片。"""

        validator_accepted = state.get("validator_accepted_cards", [])
        if not validator_accepted:
            validator_accepted = state.get("evidence_cards", [])
        accepted = list(validator_accepted)
        rejected = list(state.get("rejected_evidence", []))
        reviews: list[NoveltyPointReview] = []
        decisions = []
        issues: list[WorkflowIssue] = []
        audit_decisions = None

        if self.services.reviewer is None:
            reviews = [
                _insufficient_point_review(
                    point.point_id, "Reviewer 未启用，未执行查新点级信息判定。"
                )
                for point in state.get("novelty_points", [])
            ]
            issues = [
                WorkflowIssue(
                    node="review_evidence",
                    code="reviewer_unavailable",
                    message="Reviewer 未提供或未运行；该结果不是证据不足裁定。",
                    severity=IssueSeverity.ERROR,
                )
            ]
        else:
            try:
                evidence_by_id = {
                    item.evidence_id: item for item in state.get("raw_evidence", [])
                }
                for point in state.get("novelty_points", []):
                    point_cards = [
                        card for card in validator_accepted
                        if card.novelty_point_id == point.point_id
                    ]
                    requested_ids = {
                        evidence_id for card in point_cards
                        for evidence_id in card.evidence_ids
                    }
                    request = NoveltyPointReviewRequest(
                        subject_paper_id=state["paper"].paper_id,
                        novelty_point=point,
                        tasks=[
                            task for task in state.get("all_research_tasks", [])
                            if task.novelty_point_id == point.point_id
                        ],
                        cards=point_cards,
                        evidence=[
                            evidence_by_id[evidence_id]
                            for evidence_id in requested_ids
                            if evidence_id in evidence_by_id
                            and evidence_by_id[evidence_id].novelty_point_id
                            == point.point_id
                        ],
                    )
                    review = await _resolve(self.services.reviewer.review(request))
                    reviews.append(NoveltyPointReview.model_validate(review))
            except TypeError:
                # 迁移桥：兼容仍实现旧 cards/points/tasks 接口的外部 Reviewer。
                try:
                    result = await _resolve(
                        self.services.reviewer.review(
                            validator_accepted,
                            points=state.get("novelty_points", []),
                            tasks=state.get("all_research_tasks", []),
                        )
                    )
                except Exception as exc:
                    safe_error = _safe_error(exc)
                    accepted = []
                    rejected.extend(
                        RejectedEvidence(card_id=card.card_id, reason="review_failed")
                        for card in validator_accepted
                    )
                    issues = [
                        WorkflowIssue(
                            node="review_evidence",
                            code="review_failed",
                            message=f"Reviewer 执行失败：{safe_error}",
                            severity=IssueSeverity.ERROR,
                        )
                    ]
                    result = None
                if result is None:
                    audit_decisions = decisions
                else:
                    accepted = list(result.accepted)
                    decisions = list(result.decisions)
                    rejected.extend(
                        RejectedEvidence(card_id=card_id, reason=reason)
                        for card_id, reason in result.rejected
                    )
                    issues = [
                        WorkflowIssue(
                            node="review_evidence",
                            code="needs_more_evidence",
                            message=f"证据卡 {card_id} 需要更多证据",
                        )
                        for card_id in result.needs_more
                    ]
                    issues.extend(
                        WorkflowIssue(
                            node="review_evidence",
                            code=decision.issues[0].code,
                            message=(
                                f"证据卡 {decision.card_id} 被审查拒绝："
                                f"{decision.issues[0].message}"
                            ),
                            severity=IssueSeverity(decision.issues[0].severity.value),
                        )
                        for decision in result.decisions
                        if decision.verdict.value == "reject" and decision.issues
                    )
                    audit_decisions = decisions
            except Exception as exc:
                safe_error = _safe_error(exc)
                reviewed_ids = {item.novelty_point_id for item in reviews}
                reviews.extend(
                    _insufficient_point_review(
                        point.point_id, f"Reviewer 执行失败：{safe_error}"
                    )
                    for point in state.get("novelty_points", [])
                    if point.point_id not in reviewed_ids
                )
                issues = [
                    WorkflowIssue(
                        node="review_evidence",
                        code="review_failed",
                        message=f"Reviewer 执行失败：{safe_error}",
                        severity=IssueSeverity.ERROR,
                    )
                ]

        # 覆盖不完整时，基于“未检索到”的裁定不成立，降级为证据不足。
        # 覆盖门可通过 workflow.enforce_retrieval_coverage=false 暂时关闭：关闭后
        # Reviewer 的裁定原样保留，报告局限改用“未经完整覆盖校验”的措辞。
        coverage = self._assess_retrieval_coverage(state)
        if self.config.enforce_retrieval_coverage:
            reviews, downgrades = apply_coverage_policy(reviews, coverage)
        else:
            downgrades = []

        # 0 卡时 Reviewer 根本不会运行（代码短路），所以“为什么没有证据”必须由
        # 覆盖事实自己回答；否则检索失败与检索成功但零命中会写成同一句话。
        cards_by_point: dict[str, int] = {}
        for card in accepted:
            cards_by_point[card.novelty_point_id] = (
                cards_by_point.get(card.novelty_point_id, 0) + 1
            )
        coverage_by_point = {
            item.novelty_point_id: item for item in coverage
        }
        reasoned: list[NoveltyPointReview] = []
        for review in reviews:
            item = coverage_by_point.get(review.novelty_point_id)
            if (
                item is not None
                and not cards_by_point.get(review.novelty_point_id, 0)
                and review.status is ReviewStatus.INSUFFICIENT_EVIDENCE
            ):
                review = review.model_copy(
                    update={
                        "supplement_request": SupplementRequest(
                            reason=zero_card_reason(item)
                        )
                    }
                )
            reasoned.append(review)
        reviews = reasoned
        issues.extend(
            WorkflowIssue(
                node="review_evidence",
                code="retrieval_coverage_insufficient",
                message=(
                    f"检索覆盖不完整（{downgrade.coverage_state.value}），"
                    f"查新点 {downgrade.novelty_point_id} 的 "
                    f"{downgrade.previous_verdict.value} 裁定降级为证据不足："
                    f"{downgrade.reason}"
                ),
                severity=IssueSeverity.WARNING,
            )
            for downgrade in downgrades
        )

        persist_evidence_cards(
            state["paper"],
            raw_cards=state.get("raw_evidence_cards", []),
            validator_accepted_cards=(
                validator_accepted if self.services.reviewer else None
            ),
            review_decisions=audit_decisions,
            accepted_cards=accepted,
            rejected_evidence=rejected,
            output_root=self.output_root,
        )
        persist_novelty_reviews(
            state["paper"], reviews, output_root=self.output_root
        )
        return {
            "evidence_cards": accepted,
            "rejected_evidence": rejected,
            "review_decisions": decisions,
            "novelty_reviews": reviews,
            "retrieval_coverage": coverage,
            "issues": issues,
        }

    async def _check_final_evidence_sufficiency(
        self, state: NoveltyState
    ) -> dict[str, Any]:
        """按查新点检查最终有效 EvidenceCard 数量是否达标。

        输入是 Validator 和 Provenance Integrity Gate 保留的 Card；Reviewer 只产出
        查新点级判断，不参与 Card 过滤。
        本节点只判断数量，不评价检索范围、来源多样性、证据质量或结论可信度。
        """
        brief = state["brief"]
        counts: dict[str, int] = {point.point_id: 0 for point in brief.novelty_points}
        for card in state.get("evidence_cards", []):
            if card.novelty_point_id in counts:
                counts[card.novelty_point_id] += 1

        configured_cut = self.config.min_final_evidence_cards_per_point
        insufficient = [
            InsufficientFinalEvidence(
                novelty_point_id=point.point_id,
                valid_card_count=counts[point.point_id],
                required_card_count=configured_cut,
            )
            for point in brief.novelty_points
            if counts[point.point_id] < configured_cut
        ]
        return {"insufficient_final_evidence_points": insufficient}

    async def _validate_synthesis_input(
        self, state: NoveltyState
    ) -> dict[str, Any]:
        """Gate A: filter cards with broken deterministic provenance chains."""

        result = validate_synthesis_input(
            state.get("evidence_cards", []),
            evidence=state.get("raw_evidence", []),
            tasks=state.get("all_research_tasks", []),
            novelty_points=state.get("novelty_points", []),
            paper_id=state["paper"].paper_id,
            reference_store=self.reference_store,
        )
        accepted = list(result.accepted)
        gate_rejections = [
            RejectedEvidence(card_id=card.card_id, reason="; ".join(reasons))
            for card, reasons in result.rejected
        ]
        rejected = [*state.get("rejected_evidence", []), *gate_rejections]
        gate_issues = [
            WorkflowIssue(
                node="validate_synthesis_input",
                code="synthesis_input_integrity",
                message=(
                    f"Evidence Card {card.card_id} failed synthesis input "
                    f"integrity: {'; '.join(reasons)}"
                ),
                severity=IssueSeverity.WARNING,
                task_id=card.task_id,
            )
            for card, reasons in result.rejected
        ]
        persist_evidence_cards(
            state["paper"],
            raw_cards=state.get("raw_evidence_cards", []),
            validator_accepted_cards=(
                state.get("validator_accepted_cards", [])
                if self.services.reviewer
                else None
            ),
            review_decisions=(state.get("review_decisions") or None),
            accepted_cards=accepted,
            rejected_evidence=rejected,
            output_root=self.output_root,
        )
        return {
            "evidence_cards": accepted,
            "rejected_evidence": rejected,
            "issues": gate_issues,
            "synthesis_integrity": result.audit(),
            "integrity_rejected_card_ids": [
                card.card_id for card, _reasons in result.rejected
            ],
        }

    async def _route_after_evidence_sufficiency_check(
        self, state: NoveltyState
    ) -> str:
        """根据数量检查事实和轮次上限选择补检或汇总。"""
        if (
            state.get("insufficient_final_evidence_points")
            and state.get("rounds", 0) < self.config.max_rounds
        ):
            return "supplement"
        return "synthesize"

    async def _plan_supplement(self, state: NoveltyState) -> dict[str, Any]:
        next_round = state.get("rounds", 1) + 1
        try:
            brief_value = self.services.coordinator.plan_supplement(
                state["paper"],
                brief=state["brief"],
                existing_evidence=state.get("evidence_cards", []),
                insufficient_final_evidence_points=state.get(
                    "insufficient_final_evidence_points", []
                ),
                attempt=next_round,
            )
            brief = NoveltyBrief.model_validate(await _resolve(brief_value))
        except (ValidationError, TypeError, ValueError) as exc:
            raise WorkflowExecutionError(f"Coordinator 未生成合法补充任务：{exc}") from exc

        existing_tasks = state.get("all_research_tasks", [])
        task_by_key = {_task_key(task): task for task in existing_tasks}
        new_tasks, issues = self._apply_task_language_gate(
            brief.research_tasks, node="plan_supplement"
        )
        for task in new_tasks:
            task_by_key[_task_key(task)] = task

        all_tasks = list(task_by_key.values())
        return {
            "brief": brief.model_copy(update={"research_tasks": new_tasks}),
            "research_tasks": new_tasks,
            "all_research_tasks": all_tasks,
            "rounds": next_round,
            "issues": issues,
        }

    async def _synthesize_report(self, state: NoveltyState) -> dict[str, Any]:
        integrity_rejected_ids = set(
            state.get("integrity_rejected_card_ids", [])
        )
        rejected_reasons = [
            f"{item.card_id}: {item.reason}"
            for item in state.get("rejected_evidence", [])
            if item.card_id not in integrity_rejected_ids
        ]
        try:
            report_value = self.services.coordinator.synthesize(
                state["paper"],
                brief=state["brief"],
                evidence=state.get("evidence_cards", []),
                novelty_reviews=state.get("novelty_reviews", []),
                rejected_evidence=rejected_reasons,
                insufficient_final_evidence_points=state.get(
                    "insufficient_final_evidence_points", []
                ),
                retrieval_coverage=state.get("retrieval_coverage", []),
            )
            draft = NoveltyReport.model_validate(await _resolve(report_value))
            report = bind_reviews_to_report(
                draft,
                novelty_reviews=state.get("novelty_reviews", []),
                novelty_points=state.get("novelty_points", []),
                evidence_cards=state.get("evidence_cards", []),
            )
        except (ValidationError, TypeError, ValueError) as exc:
            raise WorkflowExecutionError(f"Coordinator 未生成合法 NoveltyReport：{exc}") from exc

        if report.paper_id != state["paper"].paper_id:
            raise WorkflowExecutionError("NoveltyReport.paper_id 与输入论文不一致")
        # 报告局限由代码补齐：不让“检索失败 / 成功但零命中”只依赖模型措辞。
        card_counts: dict[str, int] = {}
        for card in state.get("evidence_cards", []):
            card_counts[card.novelty_point_id] = (
                card_counts.get(card.novelty_point_id, 0) + 1
            )
        coverage_lines = coverage_limitations(
            state.get("retrieval_coverage", []),
            zero_card_points=[
                point.point_id
                for point in state.get("novelty_points", [])
                if not card_counts.get(point.point_id, 0)
            ],
            coverage_gate=self.config.enforce_retrieval_coverage,
        )
        if coverage_lines:
            report = report.model_copy(
                update={
                    "limitations": list(
                        dict.fromkeys(
                            [*report.limitations, *coverage_lines]
                        )
                    )
                }
            )
        return {"report": report}

    async def _validate_report_integrity(
        self, state: NoveltyState
    ) -> dict[str, Any]:
        """Gate B: observe report reference failures without blocking output."""

        result = validate_report_integrity(
            state["report"],
            novelty_points=state.get("novelty_points", []),
            evidence_cards=state.get("evidence_cards", []),
            novelty_reviews=state.get("novelty_reviews", []),
        )
        return {"report_integrity": result.audit()}

    async def _persist_report(self, state: NoveltyState) -> dict[str, Any]:
        """Persist the unchanged report after the non-blocking output gate."""

        persist_report(
            state["paper"], state["report"], output_root=self.output_root
        )
        return {}

    async def _render_report(self, state: NoveltyState) -> dict[str, Any]:
        """在结构化报告落盘后生成默认 Markdown 报告。"""

        try:
            path = render_report(
                output_format="markdown",
                paper_name=state["paper"].paper_id,
                output_root=self.output_root,
            )
        except (OSError, ValueError, RuntimeError) as exc:
            raise WorkflowExecutionError(f"Markdown 报告渲染失败：{exc}") from exc
        return {"rendered_report_path": str(path)}

    async def arun(
        self,
        paper: PaperInput | dict[str, Any],
        *,
        run_identity: Mapping[str, Any] | None = None,
    ) -> NoveltyRunResult:
        """异步执行一次完整查新工作流。"""

        paper_input = PaperInput.model_validate(paper)
        run_id = f"run-{uuid.uuid4().hex}"
        self.last_runtime_run_id = run_id
        self.last_rendered_report_path = None
        initial: NoveltyState = {
            "paper": paper_input,
            "run_id": run_id,
            "research_tasks": [],
            "all_research_tasks": [],
            "task_research_results": [],
            "raw_evidence": [],
            "raw_evidence_cards": [],
            "search_plans": [],
            "validator_accepted_cards": [],
            "evidence_cards": [],
            "rejected_evidence": [],
            "review_decisions": [],
            "novelty_reviews": [],
            "insufficient_final_evidence_points": [],
            "issues": [],
            "integrity_rejected_card_ids": [],
            "rounds": 0,
        }
        model_client = getattr(self.services.task_researcher, "model_client", None)
        profile = getattr(model_client, "profile", None)
        tool_registry = getattr(self.services.task_researcher, "tools", None)
        manager = RuntimeArtifactManager(
            paper_input.paper_id,
            config=self.config.runtime_debug,
            run_id=run_id,
            run_identity=run_identity,
            runtime_config=self.runtime_config or {
                "workflow": {
                    "max_rounds": self.config.max_rounds,
                    "max_concurrency": self.config.max_concurrency,
                    "min_final_evidence_cards_per_point": (
                        self.config.min_final_evidence_cards_per_point
                    ),
                    "candidate_limit_per_task": self.config.candidate_limit_per_task,
                }
            },
            model_provider=getattr(profile, "provider", None),
            model_name=getattr(profile, "model", None),
            enabled_tools=getattr(tool_registry, "names", ()),
            stage_names=_STAGE_NAMES,
        )
        manager.activate()
        try:
            final = await self.graph.ainvoke(
                initial, config={"max_concurrency": self.config.max_concurrency}
            )
            if "brief" not in final or "report" not in final:
                raise WorkflowExecutionError("工作流结束时缺少 Brief 或 Report")
            result = NoveltyRunResult(
                brief=final["brief"],
                evidence_cards=final.get("evidence_cards", []),
                rejected_evidence=final.get("rejected_evidence", []),
                novelty_reviews=final.get("novelty_reviews", []),
                insufficient_final_evidence_points=final.get(
                    "insufficient_final_evidence_points", []
                ),
                issues=final.get("issues", []),
                rounds=final.get("rounds", 0),
                report=final["report"],
            )
            self.last_rendered_report_path = final.get("rendered_report_path")
        except (KeyboardInterrupt, asyncio.CancelledError) as exc:
            manager.finish_run("INTERRUPTED", error=exc)
            raise
        except Exception as exc:
            manager.finish_run("FAILED", error=exc)
            raise
        else:
            manager.finish_run("SUCCESS")
            return result
        finally:
            manager.deactivate()

    def run(
        self,
        paper: PaperInput | dict[str, Any],
        *,
        run_identity: Mapping[str, Any] | None = None,
    ) -> NoveltyRunResult:
        """同步入口；异步应用应直接调用 arun。"""

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.arun(paper, run_identity=run_identity))
        raise RuntimeError("检测到正在运行的事件循环，请改用 await workflow.arun(...) ")


def _task_key(task: ResearchTask) -> tuple[str, str]:
    return task.novelty_point_id, task.task_id


def _require_complete_search_plans(
    tasks: list[ResearchTask], plans: list[SearchPlan]
) -> None:
    """Fail closed when planning fan-in does not exactly cover current tasks."""

    expected = {_task_key(task) for task in tasks}
    actual = {(plan.novelty_point_id, plan.task_id) for plan in plans}
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    duplicate_count = len(plans) - len(actual)
    if missing or unexpected or duplicate_count:
        detail = {
            "expected_task_count": len(tasks),
            "search_plan_count": len(plans),
            "missing_task_keys": [list(key) for key in missing],
            "unexpected_plan_keys": [list(key) for key in unexpected],
            "duplicate_plan_count": duplicate_count,
        }
        raise WorkflowExecutionError(
            "SearchPlan completeness check failed: "
            + json.dumps(detail, ensure_ascii=False, sort_keys=True)
        )
