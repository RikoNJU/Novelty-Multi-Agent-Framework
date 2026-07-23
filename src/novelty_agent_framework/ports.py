"""论文查新工作流的可替换接口。

这里刻意不绑定具体模型、学术数据库或全文解析库。实现方只需要实现这些
接口，就可以把真实能力接入 LangGraph 工作流。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Sequence

from .schemas import (
    EvidenceCard,
    EvidenceSource,
    NoveltyBrief,
    NoveltyReport,
    PaperInput,
    ResearchTask,
)


@dataclass(frozen=True)
class SearchHit:
    """搜索工具返回的最小候选文献描述。"""

    document_id: str
    title: str
    abstract: str = ""
    authors: tuple[str, ...] = ()
    year: int | None = None
    doi: str | None = None
    url: str | None = None


@dataclass(frozen=True)
class FullText:
    """全文工具返回的文本及其来源信息。"""

    document_id: str
    title: str
    text: str
    source: EvidenceSource | None = None
    sections: dict[str, str] = field(default_factory=dict)


class SearchTool(Protocol):
    """候选文献检索工具。"""

    def search(self, query: str, *, limit: int = 10) -> Sequence[SearchHit]:
        ...


class FullTextTool(Protocol):
    """文献摘要或全文获取工具。"""

    def fetch(self, document_id: str) -> FullText | None:
        ...


class MetadataTool(Protocol):
    """文献元数据和引用信息核验工具。"""

    def resolve(self, document_id: str) -> EvidenceSource | None:
        ...


class NoveltyCoordinator(Protocol):
    """查新主 Agent 的能力边界。"""

    def plan(
        self,
        paper: PaperInput,
        *,
        previous_brief: NoveltyBrief | None,
        existing_evidence: Sequence[EvidenceCard],
        coverage_gaps: Sequence[str],
        attempt: int,
    ) -> NoveltyBrief:
        """理解论文并生成本轮文献调研任务。"""

    def plan_supplement(
        self,
        paper: PaperInput,
        *,
        brief: NoveltyBrief,
        existing_evidence: Sequence[EvidenceCard],
        coverage_gaps: Sequence[str],
        attempt: int,
    ) -> NoveltyBrief:
        """针对证据缺口生成补充调研任务。"""

    def synthesize(
        self,
        paper: PaperInput,
        *,
        brief: NoveltyBrief,
        evidence: Sequence[EvidenceCard],
        rejected_evidence: Sequence[str],
        coverage_gaps: Sequence[str],
    ) -> NoveltyReport:
        """从全局视角汇总证据并形成查新报告。"""


class LiteratureResearchAgent(Protocol):
    """文献调研子 Agent 的能力边界。"""

    def research(
        self,
        task: ResearchTask,
        paper: PaperInput,
        *,
        search_tool: SearchTool | None = None,
        full_text_tool: FullTextTool | None = None,
        metadata_tool: MetadataTool | None = None,
    ) -> Sequence[EvidenceCard]:
        """完整执行一个查新任务并返回结构化文献证据。"""


class EvidenceValidator(Protocol):
    """证据质量门控接口。"""

    def validate(
        self,
        cards: Sequence[EvidenceCard],
        *,
        tasks: Sequence[ResearchTask],
    ) -> "ValidationResult":
        ...


@dataclass(frozen=True)
class ValidationResult:
    """校验器的标准输出。"""

    accepted: tuple[EvidenceCard, ...]
    rejected: tuple[tuple[str, str], ...]
    issues: tuple[tuple[str, str, str, str | None], ...] = ()
