"""查新文献调研 Agent 的代码骨架。"""

from __future__ import annotations

from collections.abc import Sequence

from backend.env import ModelClient
from ..models import EvidenceCard, PaperInput, ResearchTask
from ..ports import FullTextTool, LiteratureResearchAgent, MetadataTool, SearchTool


class NoveltyResearchAgent(LiteratureResearchAgent):
    """负责单个查新任务的检索、阅读和证据抽取。"""

    def __init__(self, model_client: ModelClient | None = None) -> None:
        self.model_client = model_client

    def research(
        self,
        task: ResearchTask,
        paper: PaperInput,
        *,
        search_tool: SearchTool | None = None,
        full_text_tool: FullTextTool | None = None,
        metadata_tool: MetadataTool | None = None,
    ) -> Sequence[EvidenceCard]:
        raise NotImplementedError(
            "NoveltyResearchAgent.research 还未接入真实模型和检索工具"
        )
