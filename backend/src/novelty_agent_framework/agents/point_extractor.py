"""查新点提取 Agent：从论文摘要视图提取可检索、可比较的查新点。"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import replace
from typing import Any

from pydantic import ValidationError

from backend.env import (
    ChatMessage,
    ModelCallOptions,
    ModelClient,
    ModelRegistry,
    PromptLibrary,
)

from ..ports import NoveltyPointExtractor
from ..schemas import NoveltyBrief, NoveltyPoint, PaperDigest, PaperInput

MIN_POINTS = 3
MAX_POINTS = 8
MAX_ATTEMPTS = 3
EXCERPT_CHAR_LIMIT = 2000
TRUNCATION_MARK = "…[截断]"

DELETE_SCHEMA = {
    "type": "object",
    "properties": {
        "delete_indices": {
            "type": "array",
            "items": {"type": "integer"},
        }
    },
    "required": ["delete_indices"],
}


def _truncate(text: str, limit: int) -> str:
    return text[:limit] + TRUNCATION_MARK if len(text) > limit else text


def build_paper_digest(paper: PaperInput) -> PaperDigest:
    """从 PaperInput 构造精简摘要视图（供查新点提取）。"""

    return PaperDigest(
        paper_id=paper.paper_id,
        title=paper.title,
        abstract=paper.abstract,
        english_abstract=paper.english_abstract,
        claimed_contributions=list(paper.claimed_contributions),
        keywords_zh=list(paper.keywords_zh),
        keywords_en=list(paper.keywords_en),
        references=[],  # 暂不向提取模型提供参考文献，避免引入噪声
        full_text_excerpt=_truncate(_body_excerpt(paper.full_text), EXCERPT_CHAR_LIMIT),
    )


def _body_excerpt(full_text: str) -> str:
    """跳过封面页，从中文摘要标题之后开始截取正文片段。"""

    match = re.search(r"(?m)^\s*摘\s*要\s*$", full_text)
    return full_text[match.end():] if match else full_text


class NoveltyPointExtractorAgent(NoveltyPointExtractor):
    """两步查新点 Agent：先生成候选查新点，再审查去重。

    生成步：单次生成 ≥ MIN_POINTS 条直接使用（不合并）；否则重试至多
    MAX_ATTEMPTS 次，最后合并所有查新点。审查步只调用一次模型做去重。
    数量按需求固定为 MIN_POINTS（3）条，编号统一重排为 NP-1..NP-n
    （不信任模型编号）。
    """

    def __init__(
        self,
        model_client: ModelClient | None = None,
        *,
        prompts: PromptLibrary | None = None,
        models: ModelRegistry | None = None,
        model_alias: str | None = None,
        temperature: float = 0.2,
        model_options: ModelCallOptions | None = None,
    ) -> None:
        self.model_client = model_client
        self._prompts = prompts
        self._models = models
        self._model_alias = model_alias
        self.temperature = temperature
        self.model_options = model_options

    def extract(
        self,
        digest: PaperDigest,
        *,
        previous_brief: NoveltyBrief | None,
        attempt: int,
    ) -> Sequence[NoveltyPoint]:
        """两步编排：生成候选查新点，再由审查步去重。"""

        candidates = self._generate_candidates(digest, previous_brief, attempt)
        return self._review_candidates(digest, candidates, previous_brief, attempt)

    def _generate_candidates(
        self,
        digest: PaperDigest,
        previous_brief: NoveltyBrief | None,
        attempt: int,
    ) -> list[NoveltyPoint]:
        """生成步：首次合格（≥MIN_POINTS）直接返回；否则增量重试，每次要求补充不重复查新点。"""

        last_error: ValueError | None = None
        aggregated: dict[str, NoveltyPoint] = {}
        for _ in range(MAX_ATTEMPTS):
            existing = list(aggregated.values())
            existing_dicts = [point.model_dump(mode="json") for point in existing]
            try:
                data = self._complete_json(
                    prompt_name="extractor/extract_points",
                    variables={
                        "digest_json": json.dumps(
                            digest.model_dump(mode="json"), ensure_ascii=False
                        ),
                        "existing_points_json": json.dumps(
                            existing_dicts, ensure_ascii=False
                        ),
                        "previous_brief_json": json.dumps(
                            previous_brief.model_dump(mode="json")
                            if previous_brief
                            else None,
                            ensure_ascii=False,
                        ),
                        "attempt": attempt,
                        "point_schema": json.dumps(
                            NoveltyPoint.model_json_schema(), ensure_ascii=False
                        ),
                    },
                    payload={
                        "digest": digest.model_dump(mode="json"),
                        "existing_points": existing_dicts,
                        "previous_brief": (
                            previous_brief.model_dump(mode="json")
                            if previous_brief
                            else None
                        ),
                        "attempt": attempt,
                    },
                    fallback_user_prompt=(
                        "请从论文摘要视图中提取查新点。若输入数据中的 existing_points 非空，"
                        "请只输出新增的、与之不同的查新点，使总数达到 3 条；否则直接输出 3 条。"
                        "所有内容使用中文。"
                    ),
                )
                candidates = validate_point_items(_extract_points_list(data))
            except ValueError as exc:
                last_error = exc
                candidates = []
            if not aggregated and len(candidates) >= MIN_POINTS:
                return candidates[:MIN_POINTS]  # 单次合格，不合并，按需求固定 3 条
            for point in candidates:
                aggregated.setdefault(point.claim.strip(), point)
            if len(aggregated) >= MIN_POINTS:
                break
        selected = list(aggregated.values())[:MIN_POINTS]
        if not selected and last_error is not None:
            raise last_error
        return selected

    def _review_candidates(
        self,
        digest: PaperDigest,
        candidates: Sequence[NoveltyPoint],
        previous_brief: NoveltyBrief | None,
        attempt: int,
    ) -> list[NoveltyPoint]:
        """审查步：模型只判定重复条目编号，代码删除后原样保留其余。"""

        numbered = [
            {"index": index, "claim": point.claim}
            for index, point in enumerate(candidates, start=1)
        ]
        data = self._complete_json(
            prompt_name="reviewer/review_points",
            variables={
                "points_json": json.dumps(numbered, ensure_ascii=False),
                "delete_schema": json.dumps(
                    DELETE_SCHEMA, ensure_ascii=False
                ),
            },
            payload={"points": numbered},
            fallback_user_prompt=(
                "请判断候选查新点中哪些是重复条目，输出 {\"delete_indices\": [编号列表]}；"
                "只有 claim 语义完全相同时才算重复，无重复输出空数组。"
            ),
        )
        delete_indices = _parse_delete_indices(data)
        kept = [
            point
            for index, point in enumerate(candidates, start=1)
            if index not in delete_indices
        ]
        if not kept and candidates:
            kept = list(candidates)  # 安全兜底：不允许删空
        return renumber_points(kept[:MIN_POINTS])

    def _complete_json(
        self,
        *,
        prompt_name: str,
        variables: dict[str, Any],
        payload: dict[str, Any],
        fallback_user_prompt: str,
    ) -> Any:
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
            options=replace(
                self.model_options or ModelCallOptions(temperature=self.temperature),
                response_format={"type": "json_object"},
            ),
        )
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ValueError("NoveltyPointExtractorAgent 返回内容不是合法 JSON") from exc

    def _client(self) -> ModelClient:
        if self.model_client is not None:
            return self.model_client
        if self._models is not None:
            return self._models.client_for(self._model_alias or "point_extractor")
        raise NotImplementedError(
            "NoveltyPointExtractorAgent 需要注入 ModelClient 或 ModelRegistry"
        )

    @staticmethod
    def _system_prompt() -> str:
        return (
            "你是论文查新系统的查新点提取 Agent。你从论文摘要、作者声明贡献和正文片段中"
            "提取可检索、可比较的查新点。必须输出至少 3 个、最多 8 个查新点；数量不足 3 个视为不合格，"
            "必须基于论文信息补充到至少 3 个。所有 claim 与 technical_features 使用中文。"
            "你不能编造论文中不存在的内容。"
        )


class DemoPointExtractor(NoveltyPointExtractor):
    """规则版查新点提取：用作者声明贡献或摘要句子生成确定性查新点。"""

    def extract(
        self,
        digest: PaperDigest,
        *,
        previous_brief: NoveltyBrief | None,
        attempt: int,
    ) -> Sequence[NoveltyPoint]:
        claims = (
            list(digest.claimed_contributions)
            or _split_sentences(digest.abstract)
            or ([digest.title] if digest.title else [])
        )
        source = "claimed_contributions" if digest.claimed_contributions else "abstract"
        return [
            NoveltyPoint(
                point_id=f"NP-{index}",
                claim=claim.strip(),
                technical_features=[claim.strip()],
                source_locations=[source],
            )
            for index, claim in enumerate(claims[:MIN_POINTS], start=1)
        ]


def _split_sentences(text: str) -> list[str]:
    compact = re.sub(r"\s+", "", text)
    parts = re.split(r"[。；]+", compact)
    return [part for part in parts if len(part) >= 8][:MIN_POINTS]


def _extract_points_list(data: Any) -> list[Any] | None:
    """在模型输出中递归查找查新点数组，兼容对象包装等不稳定形态。"""

    if isinstance(data, dict) and "claim" in data:
        return [data]  # 模型有时直接返回单个查新点对象
    if isinstance(data, list):
        return data if _is_points_list(data) else None
    if isinstance(data, dict):
        for key in (
            "novelty_points",
            "points",
            "查新点",
            "data",
            "result",
            "items",
            "output",
        ):
            value = data.get(key)
            if _is_points_list(value):
                return value
        for value in data.values():
            found = _extract_points_list(value)
            if found is not None:
                return found
    return None


def _is_points_list(value: Any) -> bool:
    """判定列表是否可视为查新点列表：空列表合法，非空时每项都必须是含 claim 的字典。"""

    if not isinstance(value, list):
        return False
    if not value:
        return True
    return all(isinstance(item, dict) and "claim" in item for item in value)


def validate_point_items(data: Any) -> list[NoveltyPoint]:
    """把解析出的候选列表逐项校验为 NoveltyPoint。"""

    if data is None:
        raise ValueError("查新点输出顶层必须是列表")
    points: list[NoveltyPoint] = []
    for index, item in enumerate(data[:MAX_POINTS]):
        try:
            points.append(NoveltyPoint.model_validate(item))
        except ValidationError as exc:
            raise ValueError(f"查新点第 {index + 1} 条格式错误：{exc}") from exc
    return points


def renumber_points(points: Sequence[NoveltyPoint]) -> list[NoveltyPoint]:
    """统一重排编号为 NP-1..NP-n（不信任模型编号）。"""

    return [
        point.model_copy(update={"point_id": f"NP-{index}"})
        for index, point in enumerate(points, start=1)
    ]


def _parse_delete_indices(data: Any) -> set[int]:
    """从模型输出中解析要删除的编号集合（兼容多种包装形态）。"""

    if isinstance(data, dict):
        value = data.get("delete_indices") or data.get("delete") or data.get("indices")
    else:
        value = data
    if not isinstance(value, list):
        return set()
    indices: set[int] = set()
    for item in value:
        if isinstance(item, bool):
            continue
        if isinstance(item, (int, float)):
            indices.add(int(item))
        elif isinstance(item, str) and item.strip().isdigit():
            indices.add(int(item.strip()))
    return indices
