"""基于 LangGraph 的论文查新总分总工作流。"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Sequence
from typing import Any, TypeVar, cast

from langgraph.graph import END, START, StateGraph
from pydantic import ValidationError

from novelty_agent_framework.core.errors import WorkflowExecutionError
from novelty_agent_framework.persistence import persist_novelty_points

from ..agents import (
    DefaultEvidenceValidator,
    DemoCoordinator,
    DemoPointExtractor,
    DemoResearchAgent,
    build_paper_digest,
)
from ..schemas import (
    EvidenceCard,
    IssueSeverity,
    NoveltyBrief,
    NoveltyPoint,
    NoveltyReport,
    NoveltyRunResult,
    PaperInput,
    RejectedEvidence,
    ResearchTask,
    WorkflowIssue,
)
from .state import NoveltyState, NoveltyWorkflowConfig, NoveltyWorkflowServices

T = TypeVar("T")


async def _resolve(value: T | Awaitable[T]) -> T:
    """兼容同步实现和异步实现，便于接入不同模型 SDK。"""

    if inspect.isawaitable(value):
        return await cast(Awaitable[T], value)
    return value


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
                research_agent=DemoResearchAgent(),
                point_extractor=DemoPointExtractor(),
            )
        )

    def __init__(
        self,
        services: NoveltyWorkflowServices,
        config: NoveltyWorkflowConfig | None = None,
    ) -> None:
        self.services = services
        self.config = config or NoveltyWorkflowConfig()
        self.validator = services.validator or DefaultEvidenceValidator()
        self.point_extractor = services.point_extractor or DemoPointExtractor()
        self.graph = self._build_graph()

    def _build_graph(self) -> Any:
        builder = StateGraph(NoveltyState)
        builder.add_node("extract_points", self._extract_points)
        builder.add_node("plan", self._plan)
        builder.add_node("parallel_research", self._parallel_research)
        builder.add_node("validate_evidence", self._validate_evidence)
        builder.add_node("assess_coverage", self._assess_coverage)
        builder.add_node("plan_supplement", self._plan_supplement)
        builder.add_node("synthesize_report", self._synthesize_report)

        builder.add_edge(START, "extract_points")
        builder.add_edge("extract_points", "plan")
        builder.add_edge("plan", "parallel_research")
        builder.add_edge("parallel_research", "validate_evidence")
        builder.add_edge("validate_evidence", "assess_coverage")
        builder.add_conditional_edges(
            "assess_coverage",
            self._route_after_assessment,
            {
                "supplement": "plan_supplement",
                "synthesize": "synthesize_report",
            },
        )
        builder.add_edge("plan_supplement", "parallel_research")
        builder.add_edge("synthesize_report", END)
        return builder.compile()

    async def _extract_points(self, state: NoveltyState) -> dict[str, Any]:
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
        # 测试版持久化：把查新点写入固定目录（后续替换为数据库存储）
        persist_novelty_points(state["paper"], validated)
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
                        "以下查新点缺少英文表述，已降级为中文-only："
                        + ", ".join(missing_english)
                    ),
                    severity=IssueSeverity.WARNING,
                )
            )
        return {"novelty_points": validated, "issues": issues}

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

        return {
            "brief": brief,
            "research_tasks": list(brief.research_tasks),
            "all_research_tasks": list(brief.research_tasks),
            "rounds": 1,
        }

    async def _parallel_research(self, state: NoveltyState) -> dict[str, Any]:
        tasks = state.get("research_tasks", [])
        if not tasks:
            return {
                "raw_evidence_cards": [],
                "issues": [
                    WorkflowIssue(
                        node="parallel_research",
                        code="no_research_tasks",
                        message="Coordinator 本轮未生成文献调研任务",
                    )
                ],
            }

        semaphore = asyncio.Semaphore(self.config.max_concurrency)

        async def run_one(task: ResearchTask) -> tuple[list[EvidenceCard], list[WorkflowIssue]]:
            async with semaphore:
                try:
                    result_value = self.services.research_agent.research(
                        task,
                        state["paper"],
                        search_tool=self.services.search_tool,
                        full_text_tool=self.services.full_text_tool,
                        metadata_tool=self.services.metadata_tool,
                    )
                    raw_cards = await _resolve(result_value)
                    cards: list[EvidenceCard] = []
                    issues: list[WorkflowIssue] = []
                    for index, raw_card in enumerate(raw_cards):
                        try:
                            cards.append(EvidenceCard.model_validate(raw_card))
                        except ValidationError as exc:
                            issues.append(
                                WorkflowIssue(
                                    node="parallel_research",
                                    code="malformed_evidence_card",
                                    message=(
                                        f"调研任务 {task.task_id} 的第 {index + 1} 张证据卡格式错误："
                                        f"{exc}"
                                    ),
                                    severity=IssueSeverity.WARNING,
                                    task_id=task.task_id,
                                )
                            )
                    return cards, issues
                except Exception as exc:  # 单个子任务失败不能破坏其他并行结果
                    return [], [
                        WorkflowIssue(
                            node="parallel_research",
                            code="research_task_failed",
                            message=f"调研任务 {task.task_id} 执行失败：{exc}",
                            severity=IssueSeverity.WARNING,
                            task_id=task.task_id,
                        )
                    ]

        results = await asyncio.gather(*(run_one(task) for task in tasks))
        cards = [card for task_cards, _ in results for card in task_cards]
        issues = [issue for _, task_issues in results for issue in task_issues]
        return {"raw_evidence_cards": cards, "issues": issues}

    async def _validate_evidence(self, state: NoveltyState) -> dict[str, Any]:
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
            "evidence_cards": list(result.accepted),
            "rejected_evidence": rejected,
            "issues": issues,
        }

    async def _assess_coverage(self, state: NoveltyState) -> dict[str, Any]:
        """评估证据覆盖度。

        工作流整体通过 ``ainvoke`` 执行，并包含补检回边。保持图节点为异步
        callable，避免 LangGraph 的异步循环在同步节点线程池收尾阶段挂起。
        """
        brief = state["brief"]
        counts: dict[str, int] = {point.point_id: 0 for point in brief.novelty_points}
        for card in state.get("evidence_cards", []):
            if card.novelty_point_id in counts:
                counts[card.novelty_point_id] += 1

        gaps = [
            (
                f"{point.point_id}: 仅有 {counts[point.point_id]} 条有效证据，"
                f"至少需要 {self.config.minimum_evidence_per_point} 条"
            )
            for point in brief.novelty_points
            if counts[point.point_id] < self.config.minimum_evidence_per_point
        ]
        return {"coverage_gaps": gaps}

    async def _route_after_assessment(self, state: NoveltyState) -> str:
        """根据覆盖度异步选择补检或汇总分支。"""
        if state.get("coverage_gaps") and state.get("rounds", 0) < self.config.max_rounds:
            return "supplement"
        return "synthesize"

    async def _plan_supplement(self, state: NoveltyState) -> dict[str, Any]:
        next_round = state.get("rounds", 1) + 1
        try:
            brief_value = self.services.coordinator.plan_supplement(
                state["paper"],
                brief=state["brief"],
                existing_evidence=state.get("evidence_cards", []),
                coverage_gaps=state.get("coverage_gaps", []),
                attempt=next_round,
            )
            brief = NoveltyBrief.model_validate(await _resolve(brief_value))
        except (ValidationError, TypeError, ValueError) as exc:
            raise WorkflowExecutionError(f"Coordinator 未生成合法补充任务：{exc}") from exc

        existing_tasks = state.get("all_research_tasks", [])
        task_by_id = {task.task_id: task for task in existing_tasks}
        for task in brief.research_tasks:
            task_by_id[task.task_id] = task

        return {
            "brief": brief,
            "research_tasks": list(brief.research_tasks),
            "all_research_tasks": list(task_by_id.values()),
            "rounds": next_round,
        }

    async def _synthesize_report(self, state: NoveltyState) -> dict[str, Any]:
        rejected_reasons = [
            f"{item.card_id}: {item.reason}"
            for item in state.get("rejected_evidence", [])
        ]
        try:
            report_value = self.services.coordinator.synthesize(
                state["paper"],
                brief=state["brief"],
                evidence=state.get("evidence_cards", []),
                rejected_evidence=rejected_reasons,
                coverage_gaps=state.get("coverage_gaps", []),
            )
            report = NoveltyReport.model_validate(await _resolve(report_value))
        except (ValidationError, TypeError, ValueError) as exc:
            raise WorkflowExecutionError(f"Coordinator 未生成合法 NoveltyReport：{exc}") from exc

        if report.paper_id != state["paper"].paper_id:
            raise WorkflowExecutionError("NoveltyReport.paper_id 与输入论文不一致")
        return {"report": report}

    async def arun(self, paper: PaperInput | dict[str, Any]) -> NoveltyRunResult:
        """异步执行一次完整查新工作流。"""

        paper_input = PaperInput.model_validate(paper)
        initial: NoveltyState = {
            "paper": paper_input,
            "research_tasks": [],
            "all_research_tasks": [],
            "raw_evidence_cards": [],
            "evidence_cards": [],
            "rejected_evidence": [],
            "coverage_gaps": [],
            "issues": [],
            "rounds": 0,
        }
        final = await self.graph.ainvoke(initial)
        if "brief" not in final or "report" not in final:
            raise WorkflowExecutionError("工作流结束时缺少 Brief 或 Report")

        return NoveltyRunResult(
            brief=final["brief"],
            evidence_cards=final.get("evidence_cards", []),
            rejected_evidence=final.get("rejected_evidence", []),
            coverage_gaps=final.get("coverage_gaps", []),
            issues=final.get("issues", []),
            rounds=final.get("rounds", 0),
            report=final["report"],
        )

    def run(self, paper: PaperInput | dict[str, Any]) -> NoveltyRunResult:
        """同步入口；异步应用应直接调用 arun。"""

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.arun(paper))
        raise RuntimeError("检测到正在运行的事件循环，请改用 await workflow.arun(...) ")
