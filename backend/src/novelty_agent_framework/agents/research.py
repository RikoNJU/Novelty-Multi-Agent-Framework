"""查新文献调研 Agent 的代码骨架。"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

from pydantic import ValidationError

from backend.env import (
    ChatMessage,
    ModelCallOptions,
    ModelClient,
    ModelRegistry,
    PromptLibrary,
)
from ..schemas import EvidenceCard, PaperInput, ResearchTask
from ..ports import FullTextTool, LiteratureResearchAgent, MetadataTool, SearchTool


class NoveltyResearchAgent(LiteratureResearchAgent):
    """负责单个查新任务的检索、阅读和证据抽取。"""

    def __init__(
        self,
        model_client: ModelClient | None = None,
        *,
        prompts: PromptLibrary | None = None,
        models: ModelRegistry | None = None,
        model_alias: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        self.model_client = model_client
        self._prompts = prompts
        self._models = models
        self._model_alias = model_alias
        self.temperature = temperature

    def research(
        self,
        task: ResearchTask,
        paper: PaperInput,
        *,
        search_tool: SearchTool | None = None,
        full_text_tool: FullTextTool | None = None,
        metadata_tool: MetadataTool | None = None,
    ) -> Sequence[EvidenceCard]:
        payload = {
            "task": task.model_dump(mode="json"),
            "paper": paper.model_dump(mode="json"),
        }
        data = self._complete_json(
            prompt_name="research/literature_review",
            variables={
                "task_json": json.dumps(payload["task"], ensure_ascii=False),
                "paper_json": json.dumps(payload["paper"], ensure_ascii=False),
                "evidence_schema": json.dumps(
                    EvidenceCard.model_json_schema(), ensure_ascii=False
                ),
            },
            payload=payload,
            fallback_user_prompt="请完整执行调研任务并输出 EvidenceCard 列表。",
        )
        if not isinstance(data, list):
            raise ValueError("NoveltyResearchAgent 返回 JSON 顶层必须是列表")

        cards: list[EvidenceCard] = []
        for index, item in enumerate(data):
            try:
                cards.append(EvidenceCard.model_validate(item))
            except ValidationError as exc:
                raise ValueError(
                    f"research 第 {index + 1} 张证据卡格式错误：{exc}"
                ) from exc
        return cards

    def _complete_json(
        self,
        *,
        prompt_name: str,
        variables: dict[str, Any],
        payload: dict[str, Any],
        fallback_user_prompt: str,
    ) -> Any:
        """渲染提示词并调用统一模型客户端，把回复解析为 JSON。"""

        client = self._client()
        if self._prompts is not None:
            rendered = self._prompts.render(prompt_name, **variables)
            system, user = rendered.system, rendered.user
        else:
            system = self._system_prompt()
            user = (
                f"{fallback_user_prompt}\n\n输入数据：\n"
                f"{json.dumps(payload, ensure_ascii=False)}"
            )

        response = client.complete(
            [
                ChatMessage(role="system", content=system),
                ChatMessage(role="user", content=user),
            ],
            options=ModelCallOptions(temperature=self.temperature),
        )
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ValueError("NoveltyResearchAgent 返回内容不是合法 JSON") from exc

    def _client(self) -> ModelClient:
        if self.model_client is not None:
            return self.model_client
        if self._models is not None:
            return self._models.client_for(self._model_alias or "research")
        raise NotImplementedError(
            "NoveltyResearchAgent 需要注入 ModelClient 或 ModelRegistry"
        )

    @staticmethod
    def _system_prompt() -> str:
        return (
            "你是论文查新系统的文献调研 Agent。你负责检索候选文献、阅读摘要或全文、"
            "与目标论文的查新点逐项比较，并输出 EvidenceCard。"
            "你不能编造文献、DOI、URL 或证据位置；所有重合和差异判断必须包含"
            "可追溯来源、原文摘录和位置。"
        )
