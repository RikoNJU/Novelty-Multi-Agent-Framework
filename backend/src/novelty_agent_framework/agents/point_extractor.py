"""查新点提取 Agent：从论文摘要视图提取可检索、可比较的查新点。"""

from __future__ import annotations

import json
import re
import hashlib
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
MAX_MODEL_CALLS = 5  # generation, review and at most one coverage follow-up share this budget
EXCERPT_CHAR_LIMIT = 2000
CONTRIBUTION_EXCERPT_LIMIT = 1200
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
_POINT_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {"novelty_points": {
        "type": "array", "maxItems": MAX_POINTS,
        "items": NoveltyPoint.model_json_schema(),
    }},
    "required": ["novelty_points"],
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
        full_text_excerpt=_bounded_body_excerpt(paper.full_text),
    )


def _body_excerpt(full_text: str) -> str:
    """跳过封面页，从中文摘要标题之后开始截取正文片段。"""

    match = re.search(r"(?m)^\s*摘\s*要\s*$", full_text)
    return full_text[match.end():] if match else full_text


def _bounded_body_excerpt(full_text: str) -> str:
    """Add bounded author-contribution passages that may be beyond the opening."""
    opening = _truncate(_body_excerpt(full_text), EXCERPT_CHAR_LIMIT)
    passages = []
    for match in re.finditer(r"(?:主要|核心)贡献(?:可以)?总结", full_text):
        if match.start() < EXCERPT_CHAR_LIMIT:
            continue
        passage = full_text[match.start():match.start() + CONTRIBUTION_EXCERPT_LIMIT]
        if passage not in passages:
            passages.append(passage)
        if len(passages) == 3:
            break
    return opening + "".join(f"\n\n[作者贡献段 {index}]\n{part}"
                             for index, part in enumerate(passages, 1))


class NoveltyPointExtractorAgent(NoveltyPointExtractor):
    """两步查新点 Agent：先生成候选查新点，再审查去重。

    生成、去重和一次有界补核查共享调用预算。目标数量只用于诊断，
    不足时保留已证实的点并报告范围局限；编号由代码重排。
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
        self.last_trace: dict[str, Any] = {}
        self._model_calls_used = 0

    def extract(
        self,
        digest: PaperDigest,
        *,
        previous_brief: NoveltyBrief | None,
        attempt: int,
    ) -> Sequence[NoveltyPoint]:
        """两步编排：生成候选查新点，再由审查步去重。"""

        self._model_calls_used = 0
        digest_data = digest.model_dump(mode="json")
        self.last_trace = {
            "paper_id": digest.paper_id,
            "digest": digest_data,
            "digest_sha256": hashlib.sha256(json.dumps(digest_data, ensure_ascii=False,
                sort_keys=True).encode()).hexdigest(),
            "target_count": MIN_POINTS,
            "max_candidates": MAX_POINTS,
            "model_call_budget": MAX_MODEL_CALLS,
            "calls": [],
        }
        candidates = self._generate_candidates(digest, previous_brief, attempt)
        result = self._review_candidates(digest, candidates, previous_brief, attempt)
        self.last_trace["final_points"] = [p.model_dump(mode="json") for p in result]
        self.last_trace["final_count"] = len(result)
        self.last_trace["exit_reason"] = (
            "target_reached" if len(result) >= MIN_POINTS else "below_target_review_scope"
        )
        self.last_trace["model_calls_used"] = self._model_calls_used
        return result

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
            if self._model_calls_used >= MAX_MODEL_CALLS - 1:
                break  # reserve one call for deduplication
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
                        "point_schema": json.dumps(_POINT_OUTPUT_SCHEMA, ensure_ascii=False),
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
                        "提取有原文依据的独立技术机制；框架中的独立子算法单列，"
                        "性能指标不单独凑点。已有候选非空时只返回遗漏机制。"
                        "输出 JSON 对象 {\"novelty_points\": [...]}，没有新增则返回空数组。"
                    ),
                )
                self.last_trace.setdefault("parse_branches", []).append(_point_parse_branch(data))
                candidates = validate_point_items(_extract_points_list(data))
            except ValueError as exc:
                last_error = exc
                candidates = []
                self.last_trace.setdefault("generation_errors", []).append(str(exc))
            self.last_trace.setdefault("generation", []).append({
                "existing_count": len(existing),
                "candidate_count": len(candidates),
                "candidates": [p.model_dump(mode="json") for p in candidates],
            })
            if not aggregated and len(candidates) >= MIN_POINTS:
                self.last_trace["merged_candidates"] = [p.model_dump(mode="json") for p in candidates]
                return candidates
            for point in candidates:
                aggregated.setdefault(point.claim.strip(), point)
            if len(aggregated) >= MIN_POINTS:
                break
        selected = list(aggregated.values())
        self.last_trace["merged_candidates"] = [p.model_dump(mode="json") for p in selected]
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
            {"index": index, "claim": point.claim,
             "technical_features": point.technical_features,
             "source_locations": point.source_locations}
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
                "只有技术目标、核心机制和适用范围等价且仅为复述时才删除；"
                "框架与独立子算法不能仅因包含关系被删除。无重复输出空数组。"
            ),
        )
        delete_indices = _parse_delete_indices(data)
        raw_indices = data.get("delete_indices", data.get("delete", data.get("indices"))) if isinstance(data, dict) else data
        invalid_entries = [entry for entry in raw_indices if type(entry) is not int] if isinstance(raw_indices, list) else []
        invalid_indices = sorted(index for index in delete_indices
                                 if index < 1 or index > len(candidates))
        delete_indices -= set(invalid_indices)
        kept = [
            point
            for index, point in enumerate(candidates, start=1)
            if index not in delete_indices
        ]
        if not kept and candidates:
            kept = list(candidates)  # 安全兜底：不允许删空
            delete_indices.clear()
        self.last_trace["deduplication"] = {
            "input": numbered,
            "raw_delete_indices": data,
            "invalid_entries": invalid_entries,
            "invalid_indices": invalid_indices,
            "deleted_indices": sorted(delete_indices),
            "retained_indices": [i for i in range(1, len(candidates) + 1)
                                 if i not in delete_indices],
            "deletion_reason": "not provided by model",
        }
        if len(kept) < MIN_POINTS and len(candidates) >= MIN_POINTS \
                and self._model_calls_used < MAX_MODEL_CALLS:
            # One bounded coverage check after deletion; do not regenerate all points.
            try:
                self.last_trace["coverage_followup_attempted"] = True
                data = self._complete_json(
                    prompt_name="extractor/extract_points",
                    variables={
                        "digest_json": json.dumps(digest.model_dump(mode="json"), ensure_ascii=False),
                        "existing_points_json": json.dumps([p.model_dump(mode="json") for p in kept], ensure_ascii=False),
                        "previous_brief_json": json.dumps(previous_brief.model_dump(mode="json") if previous_brief else None, ensure_ascii=False),
                        "attempt": attempt,
                        "point_schema": json.dumps(_POINT_OUTPUT_SCHEMA, ensure_ascii=False),
                    },
                    payload={"digest": digest.model_dump(mode="json"),
                             "existing_points": [p.model_dump(mode="json") for p in kept]},
                    fallback_user_prompt="只核查已有候选和删除结果是否遗漏原文支持的独立技术机制；没有则返回空 novelty_points 数组。",
                )
                self.last_trace["coverage_followup_parse_branch"] = _point_parse_branch(data)
                additions = validate_point_items(_extract_points_list(data))
                for point in additions:
                    if point.claim.strip() not in {p.claim.strip() for p in kept}:
                        kept.append(point)
                self.last_trace["coverage_followup_candidates"] = [p.model_dump(mode="json") for p in additions]
            except ValueError as exc:
                self.last_trace["coverage_followup_error"] = str(exc)
        return renumber_points(kept)

    def _complete_json(
        self,
        *,
        prompt_name: str,
        variables: dict[str, Any],
        payload: dict[str, Any],
        fallback_user_prompt: str,
    ) -> Any:
        if self._model_calls_used >= MAX_MODEL_CALLS:
            raise ValueError("查新点提取共享模型调用预算耗尽")
        self._model_calls_used += 1
        client = self._client()
        prompt_version = None
        if self._prompts is not None:
            rendered = self._prompts.render(prompt_name, **variables)
            system, user = rendered.system, rendered.user
            prompt_version = rendered.version
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
        if self.last_trace:
            self.last_trace["calls"].append({
                "prompt_name": prompt_name,
                "prompt_version": prompt_version,
                "system_sha256": hashlib.sha256(system.encode()).hexdigest(),
                "user_sha256": hashlib.sha256(user.encode()).hexdigest(),
                "visible_output": response.content,
            })
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
            "提取有原文依据、可独立检索的技术贡献；框架内有独立机制的子算法单列。"
            "性能数字通常是效果验证，不单独凑点。只输出 JSON 对象 novelty_points；"
            "证据不足时可以少于三个，不得编造。中文与英文声明应对应。"
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


def _point_parse_branch(data: Any) -> str:
    if isinstance(data, dict) and "novelty_points" in data:
        return "canonical_object"
    if isinstance(data, list):
        return "legacy_array"
    if isinstance(data, dict) and "claim" in data:
        return "legacy_single_point"
    if _extract_points_list(data) is not None:
        return "legacy_nested_object"
    return "invalid"


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
    if len(data) > MAX_POINTS:
        raise ValueError(f"查新点候选数 {len(data)} 超过上限 {MAX_POINTS}；不得静默截断")
    for index, item in enumerate(data):
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
        if type(item) is int:
            indices.add(item)
    return indices
