"""查新文献调研 Agent：检索编排 + 模型比较 + 证据绑定校验。"""

from __future__ import annotations

import json
import re
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
from ..ports import FullTextTool, LiteratureResearchAgent, MetadataTool, SearchTool
from ..schemas import EvidenceCard, EvidenceSource, NoveltyPoint, PaperInput, ResearchTask
from ..tools.retrieval import (
    RetrievalCandidate,
    merge_candidates,
    search_expansion,
    search_reference_seed,
)

REFERENCE_VIEW_LIMIT = 15


class NoveltyResearchAgent(LiteratureResearchAgent):
    """负责单个查新任务的检索、阅读和证据抽取。

    未注入 SearchTool 时退化为单次模型调用（骨架路径）；注入工具后执行
    “种子检索 → 扩展检索 → 合并打分 → 取全文/元数据 → 模型比较 → 绑定校验”。
    """

    def __init__(
        self,
        model_client: ModelClient | None = None,
        *,
        prompts: PromptLibrary | None = None,
        models: ModelRegistry | None = None,
        model_alias: str | None = None,
        temperature: float = 0.2,
        candidate_limit: int = 8,
        candidate_excerpt_chars: int = 2000,
        paper_excerpt_chars: int = 5000,
    ) -> None:
        self.model_client = model_client
        self._prompts = prompts
        self._models = models
        self._model_alias = model_alias
        self.temperature = temperature
        self.candidate_limit = candidate_limit
        self.candidate_excerpt_chars = candidate_excerpt_chars
        self.paper_excerpt_chars = paper_excerpt_chars

    def research(
        self,
        task: ResearchTask,
        paper: PaperInput,
        *,
        search_tool: SearchTool | None = None,
        full_text_tool: FullTextTool | None = None,
        metadata_tool: MetadataTool | None = None,
    ) -> Sequence[EvidenceCard]:
        if search_tool is None:
            return self._research_without_tools(task, paper)
        return self._research_with_tools(
            task, paper, search_tool, full_text_tool, metadata_tool
        )

    def _research_without_tools(
        self,
        task: ResearchTask,
        paper: PaperInput,
    ) -> list[EvidenceCard]:
        payload = {
            "task": task.model_dump(mode="json"),
            "paper": paper.model_dump(mode="json"),
        }
        data = self._complete_json(
            prompt_name="research/literature_review",
            variables={
                "task_json": json.dumps(payload["task"], ensure_ascii=False),
                "paper_json": json.dumps(payload["paper"], ensure_ascii=False),
                "candidates_json": "[]",
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

    def _research_with_tools(
        self,
        task: ResearchTask,
        paper: PaperInput,
        search_tool: SearchTool,
        full_text_tool: FullTextTool | None,
        metadata_tool: MetadataTool | None,
    ) -> list[EvidenceCard]:
        candidates = self._retrieve_candidates(task, paper, search_tool)
        if not candidates:
            return []
        pack = self._build_evidence_pack(candidates, full_text_tool, metadata_tool)
        if not pack:
            return []
        try:
            data = self._complete_cards(task, paper, pack)
        except ValueError:
            # 模型偶发返回非法 JSON：重试一次
            data = self._complete_cards(task, paper, pack)
        return self._validate_card_binding(data, task, pack)

    def _retrieve_candidates(
        self,
        task: ResearchTask,
        paper: PaperInput,
        search_tool: SearchTool,
    ) -> list[RetrievalCandidate]:
        seed = search_reference_seed(paper, search_tool)
        point = _point_from_task(task)
        expansion = search_expansion(point, search_tool)
        return merge_candidates(seed, expansion, point, top_n=self.candidate_limit)

    def _build_evidence_pack(
        self,
        candidates: Sequence[RetrievalCandidate],
        full_text_tool: FullTextTool | None,
        metadata_tool: MetadataTool | None,
    ) -> list[dict[str, Any]]:
        pack: list[dict[str, Any]] = []
        for candidate in candidates:
            hit = candidate.hit
            full_text = self._safe_fetch(full_text_tool, hit.document_id)
            source = self._safe_resolve(metadata_tool, hit.document_id) or EvidenceSource(
                title=hit.title,
                doi=hit.doi,
                url=hit.url,
            )
            body = full_text.text if full_text is not None else (hit.abstract or "")
            pack.append(
                {
                    "document_id": hit.document_id,
                    "title": hit.title or source.title,
                    "abstract": hit.abstract or "",
                    "excerpt": body[: self.candidate_excerpt_chars],
                    "doi": source.doi or hit.doi,
                    "url": source.url or hit.url,
                    "cited_by_paper": candidate.cited_by_paper,
                }
            )
        return pack

    def _complete_cards(
        self,
        task: ResearchTask,
        paper: PaperInput,
        pack: Sequence[dict[str, Any]],
    ) -> Any:
        payload = {
            "task": task.model_dump(mode="json"),
            "paper": _paper_model_view(paper, max_excerpt=self.paper_excerpt_chars),
            "candidates": list(pack),
        }
        return self._complete_json(
            prompt_name="research/literature_review",
            variables={
                "task_json": json.dumps(payload["task"], ensure_ascii=False),
                "paper_json": json.dumps(payload["paper"], ensure_ascii=False),
                "candidates_json": json.dumps(payload["candidates"], ensure_ascii=False),
                "evidence_schema": json.dumps(
                    EvidenceCard.model_json_schema(), ensure_ascii=False
                ),
            },
            payload=payload,
            fallback_user_prompt=(
                "请基于给定的候选文献逐篇比较，输出 EvidenceCard 列表；"
                "只能引用候选列表中的文献，quote 必须来自提供的文本，禁止编造 DOI/URL。"
            ),
        )

    def _validate_card_binding(
        self,
        data: Any,
        task: ResearchTask,
        pack: Sequence[dict[str, Any]],
    ) -> list[EvidenceCard]:
        data = _normalize_card_list(data)
        if not isinstance(data, list):
            raise ValueError("NoveltyResearchAgent 返回 JSON 顶层必须是列表")
        rows = [
            (
                _norm_url(item["url"]),
                (item["doi"] or "").casefold(),
                item["document_id"],
                item["cited_by_paper"],
            )
            for item in pack
        ]
        seen: set[str] = set()
        bound: list[EvidenceCard] = []
        for item in data:
            try:
                card = EvidenceCard.model_validate(item)
            except ValidationError:
                continue
            if card.task_id != task.task_id or card.novelty_point_id != task.novelty_point_id:
                continue
            match = _match_pack_source(card, rows)
            if match is None or card.card_id in seen:
                continue
            seen.add(card.card_id)
            bound.append(card.model_copy(update={"cited_by_paper": match[1]}))
        return bound

    @staticmethod
    def _safe_fetch(tool: FullTextTool | None, document_id: str) -> Any:
        if tool is None:
            return None
        try:
            return tool.fetch(document_id)
        except Exception:
            return None

    @staticmethod
    def _safe_resolve(tool: MetadataTool | None, document_id: str) -> Any:
        if tool is None:
            return None
        try:
            return tool.resolve(document_id)
        except Exception:
            return None

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


def _is_english_query(query: str) -> bool:
    letters = [char for char in query if char.isascii() and char.isalpha()]
    if not letters:
        return False
    return len(letters) / max(1, len(query)) >= 0.5


def _point_from_task(task: ResearchTask) -> NoveltyPoint:
    """从 ResearchTask 重建查新点视图（工作流只传 task，不传 point）。"""

    english = [query for query in task.queries if _is_english_query(query)]
    return NoveltyPoint(
        point_id=task.novelty_point_id,
        claim=task.context or (task.queries[0] if task.queries else "未命名查新点"),
        claim_en=english[0] if english else "",
        technical_features_en=english[1:],
    )


def _norm_url(url: str | None) -> str:
    return (url or "").casefold().rstrip("/")


def _normalize_card_list(data: Any) -> Any:
    """兼容模型输出包装形态：单证据卡对象或含 evidence_cards 键的对象 → 列表。"""

    if isinstance(data, dict):
        for key in ("evidence_cards", "cards"):
            if isinstance(data.get(key), list):
                return data[key]
        return [data]
    return data


def _match_pack_source(
    card: EvidenceCard,
    rows: Sequence[tuple[str, str, str, bool]],
) -> tuple[str, bool] | None:
    """卡片任一条来源命中候选包（URL 或 DOI 一致）即视为绑定。"""

    for source in card.sources:
        url = _norm_url(source.url)
        doi = (source.doi or "").casefold()
        for pack_url, pack_doi, doc_id, cited in rows:
            if (url and url == pack_url) or (doi and doi == pack_doi):
                return doc_id, cited
    return None


def _paper_model_view(paper: PaperInput, *, max_excerpt: int = 5000) -> dict[str, Any]:
    """论文摘要视图：避免把全文全量塞进模型上下文。"""

    return {
        "paper_id": paper.paper_id,
        "title": paper.title,
        "abstract": paper.abstract,
        "english_abstract": paper.english_abstract,
        "keywords_zh": list(paper.keywords_zh),
        "keywords_en": list(paper.keywords_en),
        "claimed_contributions": list(paper.claimed_contributions),
        "references": list(paper.references)[:REFERENCE_VIEW_LIMIT],
        "full_text_excerpt": _body_excerpt(paper.full_text, max_excerpt),
    }


def _body_excerpt(full_text: str, max_excerpt: int) -> str:
    match = re.search(r"(?m)^\s*摘\s*要\s*$", full_text)
    start = match.end() if match else 0
    return full_text[start : start + max_excerpt]
