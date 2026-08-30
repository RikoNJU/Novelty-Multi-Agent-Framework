"""论文查新工作流的最低数据契约。"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """拒绝未声明字段，避免 Agent 静默改变接口。"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PaperInput(StrictModel):
    """查新工作流的论文输入。"""

    paper_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    abstract: str = ""
    english_abstract: str = ""
    full_text: str = Field(min_length=1)
    references: list[str] = Field(default_factory=list)
    claimed_contributions: list[str] = Field(default_factory=list)
    keywords_zh: list[str] = Field(default_factory=list)
    keywords_en: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    images: list[PaperImage] = Field(default_factory=list)
    tables: list[PaperTable] = Field(default_factory=list)
    equations: list[PaperEquation] = Field(default_factory=list)


class PaperPage(StrictModel):
    """论文处理模块的单页文本，page 从 1 开始。"""

    page: int = Field(ge=1)
    text: str = ""


class PaperImage(StrictModel):
    """MinerU 提取的图片/图表/印章等视觉块。"""

    image_id: str = ""
    kind: str = "image"  # image | chart | seal
    page: int = Field(ge=1)
    path: str = ""
    caption: str = ""
    footnote: str = ""
    bbox: list[float] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)


class PaperTable(StrictModel):
    """MinerU 提取的表格结构化块。"""

    table_id: str = ""
    page: int = Field(ge=1)
    caption: str = ""
    footnote: str = ""
    body: str = ""
    body_format: str = "html"
    bbox: list[float] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)


class PaperEquation(StrictModel):
    """MinerU 提取的公式块（LaTeX 表示）。"""

    equation_id: str = ""
    page: int = Field(ge=1)
    latex: str = ""
    bbox: list[float] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)


class PaperDocument(StrictModel):
    """论文处理模块的结构化产物（PDF → 文本 → 章节切分）。"""

    paper_id: str = Field(min_length=1)
    title: str = ""
    abstract: str = ""
    english_abstract: str = ""
    full_text: str = ""
    references: list[str] = Field(default_factory=list)
    claimed_contributions: list[str] = Field(default_factory=list)
    keywords_zh: list[str] = Field(default_factory=list)
    keywords_en: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    sections: dict[str, str] = Field(default_factory=dict)
    pages: list[PaperPage] = Field(default_factory=list)
    source: str = ""
    parse_warnings: list[str] = Field(default_factory=list)
    images: list[PaperImage] = Field(default_factory=list)
    tables: list[PaperTable] = Field(default_factory=list)
    equations: list[PaperEquation] = Field(default_factory=list)


class PaperDigest(StrictModel):
    """供查新点提取的精简论文摘要视图。"""

    paper_id: str = Field(min_length=1)
    title: str = ""
    abstract: str = ""
    english_abstract: str = ""
    claimed_contributions: list[str] = Field(default_factory=list)
    keywords_zh: list[str] = Field(default_factory=list)
    keywords_en: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    full_text_excerpt: str = ""


class NoveltyPoint(StrictModel):
    """可检索、可比较的单个查新点。"""

    point_id: str = Field(min_length=1)
    claim: str = Field(min_length=1)
    claim_en: str = ""
    technical_features: list[str] = Field(default_factory=list)
    technical_features_en: list[str] = Field(default_factory=list)
    source_locations: list[str] = Field(default_factory=list)


class ResearchTask(StrictModel):
    """某个 NoveltyPoint 下的一条独立调研任务。"""

    task_id: str = Field(min_length=1)
    novelty_point_id: str = Field(min_length=1)
    task_type: str = Field(min_length=1)
    language: str = Field(min_length=1)
    description: str = ""
    attempt: int = Field(default=1, ge=1)


class SearchConcept(StrictModel):
    """检索中的一个语义概念及其词项表达。

    role/alias/exclude/importance 为 v2 可选字段（默认 None/空），旧调用方不传时
    行为与 v1 完全一致；M2 模板编译器会填充这些字段。
    """

    concept_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    terms: list[str] = Field(min_length=1)
    role: Literal["object", "method", "feature", "setting", "escape"] | None = None
    alias: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    importance: int = Field(default=2, ge=1, le=3)


class SearchStrategy(StrictModel):
    """一条数据库无关的检索策略。

    use_alias 为 v2 可选字段（默认 False）：strict 只渲染 terms，medium/broad
    渲染 terms+alias，由编译器模板赋值；旧调用方不传时行为与 v1 一致。
    """

    strategy_id: str = Field(min_length=1)
    level: str = Field(min_length=1)
    expression: str = Field(min_length=1)
    description: str = ""
    use_alias: bool = False
    use_exclude: bool = True


class SearchPlan(StrictModel):
    """ResearchTask 对应的数据库无关检索计划。"""

    task_id: str = Field(min_length=1)
    novelty_point_id: str = Field(min_length=1)
    concepts: list[SearchConcept] = Field(min_length=1)
    strategies: list[SearchStrategy] = Field(min_length=1)


class NoveltyBrief(StrictModel):
    """Coordinator 在第一阶段产生的查新规划。"""

    paper_summary: str = Field(min_length=1)
    research_problem: str = ""
    novelty_points: list[NoveltyPoint] = Field(min_length=1)
    keywords_zh: list[str] = Field(default_factory=list)
    keywords_en: list[str] = Field(default_factory=list)
    research_tasks: list[ResearchTask] = Field(default_factory=list)


class EvidenceSource(StrictModel):
    """Evidence Card 中可追溯的原始文献证据。"""

    title: str = Field(min_length=1)
    quote: str | None = None
    location: str | None = None
    doi: str | None = None
    url: str | None = None


class EvidenceCard(StrictModel):
    """文献调研 Agent 对候选文献的结构化分析。"""

    card_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    novelty_point_id: str = Field(min_length=1)
    document_title: str = Field(min_length=1)
    main_contribution: str = Field(min_length=1)
    overlaps: list[str] = Field(default_factory=list)
    differences: list[str] = Field(default_factory=list)
    sources: list[EvidenceSource] = Field(default_factory=list)
    cited_by_paper: bool | None = None
    possible_baseline: bool = False
    relevance: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)


class RejectedEvidence(StrictModel):
    """未通过框架证据门槛的 Evidence Card。"""

    card_id: str
    reason: str


class ConclusionLevel(StrEnum):
    """查新结论的受控枚举。"""

    STRONG = "strong"
    PARTIAL = "partial"
    WEAK = "weak"
    INSUFFICIENT = "insufficient"


class NoveltyConclusion(StrictModel):
    """单个查新点的最终结论。"""

    novelty_point_id: str
    level: ConclusionLevel
    summary: str
    supporting_card_ids: list[str] = Field(default_factory=list)
    counter_card_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class NoveltyReport(StrictModel):
    """查新工作流输出给后续系统的报告。"""

    paper_id: str
    conclusions: list[NoveltyConclusion] = Field(default_factory=list)
    missing_references: list[str] = Field(default_factory=list)
    missing_baselines: list[str] = Field(default_factory=list)
    citation_issues: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class IssueSeverity(StrEnum):
    WARNING = "warning"
    ERROR = "error"


class WorkflowIssue(StrictModel):
    """可恢复错误或质量问题的审计记录。"""

    node: str
    code: str
    message: str
    severity: IssueSeverity = IssueSeverity.WARNING
    task_id: str | None = None


class ReviewVerdict(StrEnum):
    """证据 Reviewer 对单张 Evidence Card 的裁定。"""

    ACCEPT = "accept"
    REJECT = "reject"
    NEEDS_MORE_EVIDENCE = "needs_more_evidence"


class EvidenceReviewIssue(StrictModel):
    """Reviewer 对单张证据卡发现的具体问题。"""

    code: str
    message: str
    severity: IssueSeverity = IssueSeverity.WARNING
    field: str | None = None
    source_index: int | None = None


class EvidenceReviewDecision(StrictModel):
    """Reviewer 对单张 Evidence Card 的结构化决定。"""

    card_id: str
    verdict: ReviewVerdict
    issues: list[EvidenceReviewIssue] = Field(default_factory=list)
    reviewed_confidence: float = Field(ge=0.0, le=1.0)


class NoveltyRunResult(StrictModel):
    """一次完整工作流的可测试结果。"""

    brief: NoveltyBrief
    evidence_cards: list[EvidenceCard]
    rejected_evidence: list[RejectedEvidence]
    coverage_gaps: list[str]
    issues: list[WorkflowIssue]
    rounds: int
    report: NoveltyReport
