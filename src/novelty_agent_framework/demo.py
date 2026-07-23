"""无需模型和外部数据库的确定性演示实现。"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Sequence

from .ports import FullTextTool, MetadataTool, SearchTool
from .schemas import (
    ConclusionLevel,
    EvidenceCard,
    EvidenceSource,
    NoveltyBrief,
    NoveltyConclusion,
    NoveltyPoint,
    NoveltyReport,
    PaperInput,
    ResearchTask,
)


class DemoCoordinator:
    """用规则模拟 Coordinator 的输入输出契约。"""

    def plan(
        self,
        paper: PaperInput,
        *,
        previous_brief: NoveltyBrief | None,
        existing_evidence: Sequence[EvidenceCard],
        coverage_gaps: Sequence[str],
        attempt: int,
    ) -> NoveltyBrief:
        claims = paper.claimed_contributions or [paper.abstract or paper.title]
        points = [
            NoveltyPoint(
                point_id=f"NP-{index}",
                claim=claim,
                technical_features=[claim],
                source_locations=["claimed_contributions"],
            )
            for index, claim in enumerate(claims, start=1)
        ]
        tasks = [self._task_for(point, attempt) for point in points]
        return NoveltyBrief(
            paper_summary=paper.abstract or paper.title,
            research_problem=paper.title,
            novelty_points=points,
            keywords_zh=[paper.title],
            keywords_en=[],
            research_tasks=tasks,
        )

    def plan_supplement(
        self,
        paper: PaperInput,
        *,
        brief: NoveltyBrief,
        existing_evidence: Sequence[EvidenceCard],
        coverage_gaps: Sequence[str],
        attempt: int,
    ) -> NoveltyBrief:
        missing_ids = {gap.split(":", 1)[0] for gap in coverage_gaps}
        tasks = [
            self._task_for(point, attempt)
            for point in brief.novelty_points
            if point.point_id in missing_ids
        ]
        return brief.model_copy(update={"research_tasks": tasks})

    def synthesize(
        self,
        paper: PaperInput,
        *,
        brief: NoveltyBrief,
        evidence: Sequence[EvidenceCard],
        rejected_evidence: Sequence[str],
        coverage_gaps: Sequence[str],
    ) -> NoveltyReport:
        grouped: dict[str, list[EvidenceCard]] = defaultdict(list)
        for card in evidence:
            grouped[card.novelty_point_id].append(card)

        conclusions: list[NoveltyConclusion] = []
        for point in brief.novelty_points:
            cards = grouped[point.point_id]
            if not cards:
                conclusions.append(
                    NoveltyConclusion(
                        novelty_point_id=point.point_id,
                        level=ConclusionLevel.INSUFFICIENT,
                        summary="当前检索范围内缺少足够的可追溯文献证据。",
                        confidence=0.0,
                    )
                )
                continue

            has_overlap = any(card.overlaps for card in cards)
            has_difference = any(card.differences for card in cards)
            if has_overlap and has_difference:
                level = ConclusionLevel.PARTIAL
                summary = "相关文献与该查新点存在技术重合，同时保留可辨识差异。"
            elif has_overlap:
                level = ConclusionLevel.WEAK
                summary = "现有证据显示该查新点与已有工作高度重合。"
            else:
                level = ConclusionLevel.STRONG
                summary = "当前证据未显示关键技术重合，但结论受检索范围限制。"

            conclusions.append(
                NoveltyConclusion(
                    novelty_point_id=point.point_id,
                    level=level,
                    summary=summary,
                    supporting_card_ids=[card.card_id for card in cards],
                    counter_card_ids=[card.card_id for card in cards if card.overlaps],
                    confidence=sum(card.confidence for card in cards) / len(cards),
                )
            )

        missing_references = sorted(
            {card.document_title for card in evidence if card.cited_by_paper is False}
        )
        missing_baselines = sorted(
            {
                card.document_title
                for card in evidence
                if card.possible_baseline and card.cited_by_paper is False
            }
        )
        limitations = list(coverage_gaps)
        if rejected_evidence:
            limitations.append(f"有 {len(rejected_evidence)} 条候选证据未通过质量门槛")

        return NoveltyReport(
            paper_id=paper.paper_id,
            conclusions=conclusions,
            missing_references=missing_references,
            missing_baselines=missing_baselines,
            citation_issues=[],
            limitations=limitations,
        )

    @staticmethod
    def _task_for(point: NoveltyPoint, attempt: int) -> ResearchTask:
        return ResearchTask(
            task_id=f"TASK-{point.point_id}-R{attempt}",
            novelty_point_id=point.point_id,
            queries=[point.claim, *point.technical_features],
            context=point.claim,
            attempt=attempt,
        )


class DemoResearchAgent:
    """返回合成证据，只用于验证工作流，不代表真实查新结果。"""

    async def research(
        self,
        task: ResearchTask,
        paper: PaperInput,
        *,
        search_tool: SearchTool | None = None,
        full_text_tool: FullTextTool | None = None,
        metadata_tool: MetadataTool | None = None,
    ) -> Sequence[EvidenceCard]:
        await asyncio.sleep(0.01)
        slug = task.novelty_point_id.lower()
        return [
            EvidenceCard(
                card_id=f"CARD-{task.task_id}",
                task_id=task.task_id,
                novelty_point_id=task.novelty_point_id,
                document_title=f"Demo Related Work for {task.novelty_point_id}",
                main_contribution="演示文献提出了一个与目标查新点相关的基础方法。",
                overlaps=["研究问题和核心技术路线存在部分重合"],
                differences=["目标论文声明了不同的组合方式和适用范围"],
                sources=[
                    EvidenceSource(
                        title=f"Demo Related Work for {task.novelty_point_id}",
                        quote="This synthetic passage is used only to validate the workflow.",
                        location="Section 3, paragraph 1",
                        url=f"https://example.org/demo/{slug}/round-{task.attempt}",
                    )
                ],
                cited_by_paper=False,
                possible_baseline=True,
                relevance=0.82,
                confidence=0.78,
            )
        ]
