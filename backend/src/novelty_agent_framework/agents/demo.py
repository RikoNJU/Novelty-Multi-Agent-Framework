"""无需模型和外部数据库的确定性演示实现。"""

from __future__ import annotations

import asyncio
import hashlib
from collections import defaultdict
from collections.abc import Sequence

from ..schemas import (
    ConclusionLevel,
    EvidenceCard,
    EvidenceSource,
    NoveltyBrief,
    NoveltyConclusion,
    NoveltyPoint,
    NoveltyReport,
    PaperInput,
    ResearchTask,
    SearchConcept,
    SearchPlan,
    SearchStrategy,
    Evidence,
    EvidenceLocator,
    TaskResearchRequest,
    TaskResearchResult,
    TaskResearchStatus,
)
from ..ports import FullTextTool, MetadataTool, SearchHit
from ..tools.adapter import QueryAdapter, QueryAdapterError


class DemoQueryAdapter(QueryAdapter):
    """默认演示工作流使用的数据库无关查询编译器。"""

    database = "demo"

    def _render_concept(self, concept: SearchConcept) -> str:
        terms: list[str] = []
        for raw_term in concept.terms:
            term = " ".join(raw_term.split())
            if not term:
                raise QueryAdapterError(f"Concept {concept.concept_id} 包含空 term")
            if term not in terms:
                terms.append(term)
        return f"DEMO_CONCEPT({' | '.join(terms)})"


class DemoCoordinator:
    """用规则模拟 Coordinator 的输入输出契约。"""

    def plan(
        self,
        paper: PaperInput,
        *,
        points: Sequence[NoveltyPoint],
        attempt: int,
    ) -> NoveltyBrief:
        tasks = [
            task
            for point in points
            for task in self._tasks_for(point, attempt)
        ]
        return NoveltyBrief(
            paper_summary=paper.abstract or paper.title,
            research_problem=paper.title,
            novelty_points=list(points),
            keywords_zh=list(paper.keywords_zh)
            or ([paper.title] if paper.title else []),
            keywords_en=list(paper.keywords_en),
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
            task
            for point in brief.novelty_points
            if point.point_id in missing_ids
            for task in self._tasks_for(point, attempt)
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
    def _tasks_for(
        point: NoveltyPoint, attempt: int
    ) -> tuple[ResearchTask, ResearchTask]:
        if attempt == 1:
            task_ids = ("T-1", "T-2")
        else:
            task_ids = (f"T-R{attempt}-1", f"T-R{attempt}-2")
        return (
            ResearchTask(
                task_id=task_ids[0],
                novelty_point_id=point.point_id,
                task_type="literature_search",
                language="zh",
                description="针对该查新点执行中文文献检索。",
                attempt=attempt,
            ),
            ResearchTask(
                task_id=task_ids[1],
                novelty_point_id=point.point_id,
                task_type="literature_search",
                language="en",
                description="针对该查新点执行英文文献检索。",
                attempt=attempt,
            ),
        )


class DemoResearchAgent:
    """返回合成证据，只用于验证工作流，不代表真实查新结果。"""

    async def research(
        self,
        task: ResearchTask,
        point: NoveltyPoint,
        candidates: Sequence[SearchHit],
        *,
        full_text_tool: FullTextTool | None = None,
        metadata_tool: MetadataTool | None = None,
    ) -> Sequence[EvidenceCard]:
        await asyncio.sleep(0.01)
        if not candidates:
            return []
        candidate = candidates[0]
        slug = task.novelty_point_id.lower()
        return [
            EvidenceCard(
                card_id=f"CARD-{task.novelty_point_id}-{task.task_id}",
                task_id=task.task_id,
                novelty_point_id=task.novelty_point_id,
                document_title=candidate.title,
                main_contribution="演示文献提出了一个与目标查新点相关的基础方法。",
                overlaps=["研究问题和核心技术路线存在部分重合"],
                differences=["目标论文声明了不同的组合方式和适用范围"],
                sources=[
                    EvidenceSource(
                        title=candidate.title,
                        quote=candidate.abstract,
                        location="Section 3, paragraph 1",
                        url=candidate.url
                        or f"https://example.org/demo/{slug}/round-{task.attempt}",
                    )
                ],
                cited_by_paper=False,
                possible_baseline=True,
                relevance=0.82,
                confidence=0.78,
            )
        ]


class DemoSearchPlanner:
    """用单个 Concept 确定性生成三档数据库无关检索策略。"""

    def plan(self, point: NoveltyPoint, task: ResearchTask) -> SearchPlan:
        term = point.claim_en if task.language == "en" and point.claim_en else point.claim
        concept = SearchConcept(concept_id="C1", name=term, terms=[term])
        return SearchPlan(
            task_id=task.task_id,
            novelty_point_id=point.point_id,
            concepts=[concept],
            strategies=[
                SearchStrategy(strategy_id="S1", level="strict", expression="C1"),
                SearchStrategy(strategy_id="S2", level="medium", expression="C1"),
                SearchStrategy(strategy_id="S3", level="broad", expression="C1"),
            ],
        )


class DemoSearchTool:
    """返回由查询字符串稳定派生的离线候选文献。"""

    def search(self, query: str, *, limit: int = 10) -> Sequence[SearchHit]:
        digest = hashlib.sha256(query.encode("utf-8")).hexdigest()[:12]
        text = "This synthetic passage is used only to validate the workflow."
        return [
            SearchHit(
                document_id=f"demo-{digest}",
                title=f"Demo Related Work {digest}",
                abstract=text,
                url=f"https://example.org/demo/{digest}",
            )
        ][:limit]


class DemoTaskResearcher:
    """默认离线主图使用的单任务确定性 Researcher。"""

    async def ainvoke(self, request: TaskResearchRequest) -> TaskResearchResult:
        task = request.research_task
        point = request.novelty_point
        evidence_id = f"EVD-{point.point_id}-{task.task_id}"
        quote = "This synthetic passage is used only to validate the workflow."
        evidence = Evidence(
            evidence_id=evidence_id,
            work_id=f"demo-work-{point.point_id}",
            artifact_id=f"demo-artifact-{point.point_id}",
            novelty_point_id=point.point_id,
            task_id=task.task_id,
            quote=quote,
            locator=EvidenceLocator(char_start=0, char_end=len(quote)),
            interpretation="离线演示证据",
            confidence=0.8,
        )
        card = EvidenceCard(
            card_id=f"CARD-{point.point_id}-{task.task_id}",
            task_id=task.task_id,
            novelty_point_id=point.point_id,
            document_title=f"Demo Related Work {point.point_id}",
            main_contribution="演示候选文献贡献",
            overlaps=["包含相关技术特征"],
            differences=["研究对象与目标论文不同"],
            sources=[
                EvidenceSource(
                    title=f"Demo Related Work {point.point_id}",
                    quote=quote,
                    location="artifact chars:0-64",
                    url=f"https://example.org/demo/{point.point_id}",
                )
            ],
            relevance=0.8,
            confidence=0.8,
            evidence_ids=[evidence_id],
        )
        return TaskResearchResult(
            task_id=task.task_id,
            novelty_point_id=point.point_id,
            status=TaskResearchStatus.COMPLETED,
            evidence=[evidence],
            evidence_cards=[card],
            steps_used=1,
        )
