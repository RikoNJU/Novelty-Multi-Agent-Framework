"""查新点级 Reviewer：综合 EvidenceCard/Evidence 并按需回读原文。"""

from __future__ import annotations

import json
import asyncio
import hashlib
import re
import time
from datetime import datetime, timezone
from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import Any

from pydantic import ValidationError

from backend.env import ChatMessage, ModelCallOptions, ModelClient, ModelRegistry, PromptLibrary

from ..ports import EvidenceReviewer, ReviewResult
from ..core.format_repair import repair_json
from ..core import ToolCallHarness, ToolCallHarnessConfig
from ..schemas import (
    EvidenceCard,
    EvidenceReviewDecision,
    EvidenceReviewIssue,
    IssueSeverity,
    NoveltyPoint,
    NoveltyPointReview,
    NoveltyPointReviewRequest,
    ReviewStatus,
    SupplementRequest,
    ResearchTask,
    ReviewVerdict,
)
from ..tools.researcher_registry import ResearcherToolRegistry
from ..tools.reader import ReviewerReaderTool
from ..schemas.domain import ReviewEvidence
from ..core.runtime_artifacts import current_runtime_artifacts


class _BudgetedClient:
    """Apply the remaining card budget to both async waiting and HTTP I/O."""

    def __init__(self, client, seconds):
        self.client = client
        self.deadline = time.monotonic() + seconds

    async def acomplete(self, messages, *, options=None):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("review budget exhausted")
        options = options or ModelCallOptions()
        options = replace(options, timeout_seconds=min(options.timeout_seconds or 90, remaining))
        return await asyncio.wait_for(self.client.acomplete(messages, options=options), remaining)

_ALLOWED_ISSUE_CODES = frozenset(
    {
        "unsupported_main_contribution",
        "unsupported_overlap",
        "unsupported_difference",
        "quote_not_supporting_claim",
        "scope_overstatement",
        "abstract_only_overclaim",
        "novelty_point_mismatch",
        "task_mismatch",
        "internal_contradiction",
        "confidence_overstated",
        "relevance_overstated",
        "missing_evidence_detail",
        "metadata_unverified",
        "fulltext_unavailable",
        "retrieval_coverage_unknown",
    }
)

_EVIDENCE_BOUNDARY = (
    "区分原文明确支持的事实与未核验的特征。摘要、局部片段或截短引文未提及某特征，"
    "不能证明文献未采用该特征；取得全文也不等于已读到关键段落。"
    "若最终裁定依赖尚未核验的关键差异，返回 status=insufficient_evidence，"
    "说明缺少的比较证据，不得仅降低 confidence 后继续裁定。"
    "保留已证实的局部重合；多篇分别覆盖部分特征不等于单篇公开完整组合。"
    "检索或获取失败、零命中、未展示证据均不能支持新颖性。"
    "不影响当前有限结论的次要未知可以作为局限保留。"
)

_CARD_FALLBACK = (
    "本轮只核验一张 Card 对应的一篇论文，是中间结果，不作最终查新裁定。"
    "复用 NoveltyPointReview 格式；verdict 仅描述该文献与查新点的关系。"
    "记录已覆盖特征、差异、引用可靠性和证据局限；部分相关文献也必须保留。"
    "优先使用输入 Evidence 原文，仅在具体疑问时回读。理由不超过300字。"
)

_SUMMARY_FALLBACK = (
    "你是查新点级汇总 Reviewer。综合带索引的单卡核验结果和已核验关键引文，"
    "输出 NoveltyPointReview。单卡结果是派生分析，不是原始证据。"
    "单卡失败、证据不足及 quote_truncated=true 的局限必须保留。"
    "本轮不可调用工具，不得用模型记忆填补缺口；只能引用输入已核验的 "
    "work_id、card_id 和 evidence_id。网页补充资料不得用于裁定。"
    "必要时返回 insufficient_evidence，并在 supplement_request 中列明待复核索引。"
    "理由简洁，只输出严格 JSON。"
)


@dataclass(frozen=True)
class EvidenceReviewerConfig:
    """Reviewer 运行配置。"""

    enabled: bool = False
    model_alias: str = "reviewer"
    temperature: float = 0.0
    max_cards_per_call: int = 8
    fail_closed: bool = True
    max_steps: int = 8
    max_tool_calls: int = 6
    max_total_read_chars: int = 32_000
    prompt_name: str = "reviewer/review_evidence"
    card_timeout_seconds: float = 240.0
    summary_timeout_seconds: float = 180.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature 必须位于 0 到 2 之间")
        if self.max_cards_per_call < 1:
            raise ValueError("max_cards_per_call 必须至少为 1")
        if min(self.max_steps, self.max_tool_calls, self.max_total_read_chars) < 1:
            raise ValueError("reviewer harness budgets must be positive")
        if min(self.card_timeout_seconds, self.summary_timeout_seconds) <= 0:
            raise ValueError("reviewer timeouts must be positive")
        if not self.prompt_name.strip():
            raise ValueError("prompt_name 不能为空")


class DemoEvidenceReviewer:
    """Null/Demo 实现：不伪造语义判断，显式返回证据不足。"""

    def review(
        self, request: NoveltyPointReviewRequest
    ) -> NoveltyPointReview:
        request = NoveltyPointReviewRequest.model_validate(request)
        return _insufficient_review(
            request.novelty_point.point_id,
            "Demo Reviewer 不执行新颖性语义判定。",
            cause="technical_error",
        )


class NoveltyEvidenceReviewer(EvidenceReviewer):
    """基于 LLM 与受限 Reader Harness 的查新点级 Reviewer。"""

    def __init__(
        self,
        model_client: ModelClient | None = None,
        *,
        prompts: PromptLibrary | None = None,
        models: ModelRegistry | None = None,
        config: EvidenceReviewerConfig | None = None,
        model_options: ModelCallOptions | None = None,
        tool_registry: ResearcherToolRegistry | None = None,
    ) -> None:
        self.model_client = model_client
        self._prompts = prompts
        self._models = models
        self.config = config or EvidenceReviewerConfig()
        self.model_options = model_options
        self.tools = tool_registry or ResearcherToolRegistry()
        self.harness = ToolCallHarness(
            self._client(),
            self.tools,
            config=ToolCallHarnessConfig(
                max_turns=self.config.max_steps,
                max_tool_calls=self.config.max_tool_calls,
                per_tool_limits={"reader": self.config.max_tool_calls},
                max_total_read_chars=self.config.max_total_read_chars,
            ),
        )

    def review(
        self,
        request: NoveltyPointReviewRequest | Sequence[EvidenceCard],
        *,
        points: Sequence[NoveltyPoint] = (),
        tasks: Sequence[ResearchTask] = (),
    ) -> Any:
        """评审一个查新点；旧的 cards 调用形状仅保留迁移兼容。"""

        if isinstance(request, NoveltyPointReviewRequest):
            return self._review_point(request)
        return self._review_cards_legacy(request, points=points, tasks=tasks)

    async def _review_point(
        self, request: NoveltyPointReviewRequest, *, card_only: bool = False
    ) -> NoveltyPointReview:
        request = NoveltyPointReviewRequest.model_validate(request)
        if not request.cards or not request.evidence:
            return _insufficient_review(
                request.novelty_point.point_id,
                "当前查新点没有可供可靠判定的已绑定证据。",
                cause="material_unavailable",
            )

        system, user = self._render_point_prompt(request)
        reader_tool = self.tools.get("reader") if "reader" in self.tools.names else None
        catalog = reader_tool.material_catalog(request) if isinstance(reader_tool, ReviewerReaderTool) else []
        user += "\n已授权材料目录（只可读取这些 Artifact）：\n" + json.dumps(catalog, ensure_ascii=False)
        user += "\n固定特征 ID：\n" + json.dumps(_feature_catalog(request.novelty_point), ensure_ascii=False)
        if card_only:
            system += "\n" + self._render_instruction("reviewer/review_card", _CARD_FALLBACK)
        system += "\n" + _EVIDENCE_BOUNDARY
        try:
            harness = self.harness
            client = self._client()
            if card_only:
                client = _BudgetedClient(client, self.config.card_timeout_seconds)
                harness = ToolCallHarness(client, self.tools, config=replace(
                    self.harness.config, max_turns=min(self.config.max_steps, 6),
                    max_tool_calls=min(self.config.max_tool_calls, 4),
                    per_tool_limits={"reader": min(self.config.max_tool_calls, 4)},
                ))
            result = await harness.run(
                system_prompt=system,
                initial_user_message=user,
                scope=request,
                options=self.model_options
                or ModelCallOptions(
                    temperature=self.config.temperature,
                    tool_choice="auto",
                ),
            )
            try:
                review = NoveltyPointReview.model_validate_json(_extract_json(result.final_content))
            except (ValidationError, ValueError):
                repaired = await repair_json(client, result.final_content,
                                             NoveltyPointReview.model_json_schema(), self.model_options)
                review = NoveltyPointReview.model_validate_json(_extract_json(repaired))
            if review.review_evidence:
                raise ValueError("model cannot assign review_evidence")
            review = review.model_copy(update={"incomplete_reason":
                "semantic_evidence" if review.status is ReviewStatus.INSUFFICIENT_EVIDENCE else None})
            review = _register_review_reads(review, request, result.trace, catalog)
            review = _validate_review_references(review, request)
            _record_review_event("single_card_result", request, {
                "material_catalog": catalog, "actual_model_input": {"system": system, "user": user},
                "review": review.model_dump(mode="json"),
                "read_registration": [{"read_id": item.read_id,
                    "evidence_id": item.evidence_id, "status": "validated"}
                    for item in review.review_evidence],
                "raw_model_output": result.final_content,
                "legacy_guard_shadow": _legacy_guard_shadow(review, request),
            })
            return review
        except Exception as exc:
            if not self.config.fail_closed:
                raise
            return _insufficient_review(
                request.novelty_point.point_id,
                f"Reviewer 无法完成可靠判定：{type(exc).__name__}: {exc}"[:500],
                cause="budget_exhausted" if isinstance(exc, TimeoutError) else "technical_error",
            )

    async def review_card(self, request: NoveltyPointReviewRequest) -> NoveltyPointReview:
        """Reuse the existing review contract for one indexed intermediate result."""
        if len(request.cards) != 1:
            raise ValueError("review_card requires exactly one card")
        try:
            return await asyncio.wait_for(
                self._review_point(request, card_only=True), self.config.card_timeout_seconds
            )
        except TimeoutError:
            return _insufficient_review(request.novelty_point.point_id, "单卡评审超过时间预算，核验未完成。", cause="budget_exhausted")

    async def summarize_reviews(self, request, card_reviews) -> NoveltyPointReview:
        """Synthesize compact card reviews; validate against originals locally."""
        system = self._render_instruction("reviewer/summarize_reviews", _SUMMARY_FALLBACK)
        system += "\n" + _EVIDENCE_BOUNDARY
        try:
            rows, validated_ids = _compact_summary_rows(request, card_reviews)
            user = json.dumps({
                "today": datetime.now(timezone.utc).date().isoformat(),
                "novelty_point": request.novelty_point.model_dump(mode="json"),
                "card_reviews": _summary_model_rows(rows),
                "review_schema": NoveltyPointReview.model_json_schema(),
            }, ensure_ascii=False)
            response = await asyncio.wait_for(self._client().acomplete(
                [ChatMessage(role="system", content=system), ChatMessage(role="user", content=user)],
                options=replace(self.model_options or ModelCallOptions(), tools=(), tool_choice="none",
                                timeout_seconds=self.config.summary_timeout_seconds),
            ), self.config.summary_timeout_seconds)
            if response.tool_calls:
                raise ValueError("summary attempted a tool call")
            review = NoveltyPointReview.model_validate_json(_extract_json(response.content))
            if review.review_evidence or review.read_citations:
                raise ValueError("summary cannot create new read evidence")
            review = review.model_copy(update={"incomplete_reason":
                _summary_incomplete_reason(rows) if review.status is ReviewStatus.INSUFFICIENT_EVIDENCE else None})
            incremental = [ReviewEvidence.model_validate(item) for row in rows
                           for item in row.get("review_evidence", [])]
            review = review.model_copy(update={"review_evidence": incremental})
            if any(evidence_id not in validated_ids for work in review.highly_relevant_works
                   for evidence_id in work.evidence_ids):
                raise ValueError("summary cites evidence not verified by a card review")
            review = _validate_review_references(review, request)
            _record_review_event("summary_result", request, {
                "rows": rows, "actual_model_input": user,
                "raw_model_output": response.content, "review": review.model_dump(mode="json"),
                "legacy_guard_shadow": _legacy_guard_shadow(review, request),
            })
            return review
        except Exception as exc:
            if not self.config.fail_closed:
                raise
            return _insufficient_review(
                request.novelty_point.point_id,
                f"Reviewer 汇总失败：{type(exc).__name__}: {exc}"[:500],
                cause="budget_exhausted" if isinstance(exc, TimeoutError) else "technical_error",
            )

    def _render_point_prompt(
        self, request: NoveltyPointReviewRequest
    ) -> tuple[str, str]:
        variables = {
            "today": datetime.now(timezone.utc).date().isoformat(),
            "novelty_point_json": json.dumps(
                request.novelty_point.model_dump(mode="json"), ensure_ascii=False
            ),
            "tasks_json": json.dumps(
                [item.model_dump(mode="json") for item in request.tasks],
                ensure_ascii=False,
            ),
            "cards_json": json.dumps(
                [item.model_dump(mode="json") for item in request.cards],
                ensure_ascii=False,
            ),
            "evidence_json": json.dumps(
                [item.model_dump(mode="json") for item in request.evidence],
                ensure_ascii=False,
            ),
            "review_schema": json.dumps(
                NoveltyPointReview.model_json_schema(), ensure_ascii=False
            ),
        }
        if self._prompts is not None:
            rendered = self._prompts.render(
                self.config.prompt_name, **variables
            )
            return rendered.system, rendered.user
        return _fallback_point_system_prompt(), "\n".join(
            f"{key}: {value}" for key, value in variables.items()
        )

    def _render_instruction(self, name: str, fallback: str) -> str:
        if self._prompts is None:
            return fallback
        return self._prompts.render(name).system

    def _review_cards_legacy(
        self,
        cards: Sequence[EvidenceCard],
        *,
        points: Sequence[NoveltyPoint],
        tasks: Sequence[ResearchTask],
    ) -> ReviewResult:
        """临时兼容旧调用方；正式 Workflow 不再使用逐卡过滤结果。"""
        if not cards:
            return ReviewResult(accepted=(), rejected=(), needs_more=(), decisions=())

        self._client()
        valid_card_ids = frozenset(card.card_id for card in cards)
        decisions: list[EvidenceReviewDecision] = []
        failures: list[tuple[str, str]] = []

        for batch in _chunked(cards, self.config.max_cards_per_call):
            try:
                raw = self._call_model(batch, points, tasks)
                parsed = self._parse_decisions(raw, valid_card_ids)
            except Exception as exc:
                reason = f"review_failed: {exc}"
                for card in batch:
                    failures.append((card.card_id, reason))
                    decisions.append(
                        _failure_decision(card.card_id, reason, self.config.fail_closed)
                    )
                continue
            decisions.extend(parsed.decisions)
            failures.extend(parsed.failures)

        accepted, rejected, needs_more = self._apply_verdict(cards, decisions)
        return ReviewResult(
            accepted=tuple(accepted),
            rejected=tuple(rejected),
            needs_more=tuple(needs_more),
            decisions=tuple(decisions),
        )

    def _call_model(
        self,
        cards: Sequence[EvidenceCard],
        points: Sequence[NoveltyPoint],
        tasks: Sequence[ResearchTask],
    ) -> Any:
        today = datetime.now(timezone.utc).date().isoformat()
        payload = {
            "today": today,
            "points": [point.model_dump(mode="json") for point in points],
            "tasks": [task.model_dump(mode="json") for task in tasks],
            "cards": [card.model_dump(mode="json") for card in cards],
            "review_schema": _review_output_schema(),
        }
        variables = {
            "today": today,
            "points_json": json.dumps(payload["points"], ensure_ascii=False),
            "novelty_point_json": json.dumps(
                payload["points"][0] if payload["points"] else {},
                ensure_ascii=False,
            ),
            "tasks_json": json.dumps(payload["tasks"], ensure_ascii=False),
            "cards_json": json.dumps(payload["cards"], ensure_ascii=False),
            "evidence_json": "[]",
            "review_schema": json.dumps(payload["review_schema"], ensure_ascii=False),
        }
        if self._prompts is not None:
            rendered = self._prompts.render(self.config.prompt_name, **variables)
            system, user = rendered.system, rendered.user
        else:
            system = _fallback_system_prompt()
            user = (
                "请审查以下 EvidenceCard 列表，逐卡输出结构化决定。\n"
                f"当前可信日期（UTC）：{today}\n"
                "该日期是判断来源可核验性的唯一时间基准；不得使用模型内部日期，"
                "也不得仅凭 arXiv 编号的月份推断来源不可能存在。\n\n"
                f"输入数据：\n{json.dumps(payload, ensure_ascii=False)}"
            )
        response = self._client().complete(
            [
                ChatMessage(role="system", content=system),
                ChatMessage(role="user", content=user),
            ],
            options=self.model_options
            or ModelCallOptions(temperature=self.config.temperature),
        )
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ValueError("NoveltyEvidenceReviewer 返回内容不是合法 JSON") from exc

    def _parse_decisions(self, raw: Any, valid_card_ids: frozenset[str]) -> "_ParsedBatch":
        items = _normalize_decision_list(raw)
        decisions: list[EvidenceReviewDecision] = []
        failures: list[tuple[str, str]] = []
        for item in items:
            try:
                decision = EvidenceReviewDecision.model_validate(item)
            except ValidationError:
                continue
            if decision.card_id not in valid_card_ids:
                continue
            decisions.append(_sanitize_issues(decision))
        return _ParsedBatch(decisions=decisions, failures=failures)

    def _apply_verdict(
        self,
        cards: Sequence[EvidenceCard],
        decisions: Sequence[EvidenceReviewDecision],
    ) -> tuple[list[EvidenceCard], list[tuple[str, str]], list[str]]:
        decision_by_id = {decision.card_id: decision for decision in decisions}
        accepted: list[EvidenceCard] = []
        rejected: list[tuple[str, str]] = []
        needs_more: list[str] = []
        for card in cards:
            decision = decision_by_id.get(card.card_id)
            if decision is None:
                if self.config.fail_closed:
                    rejected.append((card.card_id, "review_missing_decision"))
                else:
                    accepted.append(card)
                continue
            if decision.verdict is ReviewVerdict.ACCEPT:
                accepted.append(card)
            elif decision.verdict is ReviewVerdict.REJECT:
                rejected.append((card.card_id, _summarize_decision(decision)))
            else:
                needs_more.append(card.card_id)
        return accepted, rejected, needs_more

    def _client(self) -> ModelClient:
        if self.model_client is not None:
            return self.model_client
        if self._models is not None:
            return self._models.client_for(self.config.model_alias)
        raise NotImplementedError("NoveltyEvidenceReviewer 需要注入 ModelClient 或 ModelRegistry")


@dataclass(frozen=True)
class _ParsedBatch:
    decisions: list[EvidenceReviewDecision]
    failures: list[tuple[str, str]]


def _chunked(cards: Sequence[EvidenceCard], size: int) -> list[list[EvidenceCard]]:
    if size <= 0:
        raise ValueError("chunk size 必须为正")
    return [list(cards[index : index + size]) for index in range(0, len(cards), size)]


def _normalize_decision_list(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, dict):
        for key in ("decisions", "review_decisions"):
            if isinstance(raw.get(key), list):
                return [item for item in raw[key] if isinstance(item, dict)]
        if isinstance(raw.get("card_id"), str):
            return [raw]
        return []
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    return []


def _sanitize_issues(decision: EvidenceReviewDecision) -> EvidenceReviewDecision:
    if not decision.issues:
        return decision
    cleaned: list[EvidenceReviewIssue] = []
    for issue in decision.issues:
        if issue.code in _ALLOWED_ISSUE_CODES:
            cleaned.append(issue)
        else:
            cleaned.append(
                EvidenceReviewIssue(
                    code="missing_evidence_detail",
                    message=f"模型返回未知 issue.code '{issue.code}'：{issue.message}",
                    severity=IssueSeverity.WARNING,
                    field=issue.field,
                    source_index=issue.source_index,
                )
            )
    return decision.model_copy(update={"issues": cleaned})


def _summarize_decision(decision: EvidenceReviewDecision) -> str:
    if not decision.issues:
        return f"verdict={decision.verdict.value}"
    codes = ",".join(issue.code for issue in decision.issues)
    return f"{codes}: {decision.issues[0].message}"


def _failure_decision(card_id: str, reason: str, fail_closed: bool) -> EvidenceReviewDecision:
    if fail_closed:
        return EvidenceReviewDecision(
            card_id=card_id,
            verdict=ReviewVerdict.REJECT,
            issues=[EvidenceReviewIssue(code="missing_evidence_detail", message=reason, severity=IssueSeverity.ERROR)],
            reviewed_confidence=0.0,
        )
    return EvidenceReviewDecision(
        card_id=card_id,
        verdict=ReviewVerdict.ACCEPT,
        issues=[EvidenceReviewIssue(code="missing_evidence_detail", message=f"fail_open 放行（{reason}）", severity=IssueSeverity.WARNING)],
        reviewed_confidence=0.0,
    )


def _review_output_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "required": ["decisions"],
        "properties": {"decisions": {"type": "array", "items": EvidenceReviewDecision.model_json_schema()}},
    }


def _fallback_system_prompt() -> str:
    return (
        "你是论文查新系统的证据审查 Agent。你只能依据输入内容判断 EvidenceCard 的"
        "语义和证据一致性，不能修改 EvidenceCard，不能创造新的 DOI/URL/引文/相同点/"
        "不同点，不能使用模型记忆补充论文事实。无法判断时输出 needs_more_evidence，"
        "不能猜测。输出必须是 JSON：{\"decisions\": [EvidenceReviewDecision, ...]}。"
        "禁止输出开场白、解释性 Markdown 或自由文本。"
    )


def _fallback_point_system_prompt() -> str:
    return (
        "你是查新点级信息判定 Agent。只依据输入 EvidenceCard、Evidence 和 reader "
        "回读结果综合多个 Work；不得搜索或使用模型记忆补充事实。证据充分时输出 "
        "NoveltyPointReview；证据不足时输出 insufficient_evidence，不能猜测。"
        "仅使用论文 Evidence；source_kind=web_supplement 或旧 web_supplement_evidence "
        "仅为补充资料，不得用于裁定。LLM summary 不能作为原始 Evidence。"
    )


def _extract_json(content: str | None) -> str:
    text = (content or "").strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    return text[start : end + 1] if start != -1 and end > start else text


def _insufficient_review(point_id: str, reason: str, *, cause: str = "semantic_evidence") -> NoveltyPointReview:
    return NoveltyPointReview(
        novelty_point_id=point_id,
        status=ReviewStatus.INSUFFICIENT_EVIDENCE,
        supplement_request=SupplementRequest(reason=reason),
        incomplete_reason=cause,
    )


_STRONG_ABSENCE = re.compile(
    r"未(?:使用|采用|涉及|包含|公开|披露|用)|不涉及|没有(?:使用|采用|包含)|"
    r"\b(?:does not use|doesn't use|does not include|does not involve|without)\b",
    re.IGNORECASE,
)
_NOVEL_ABSENCE = re.compile(r"未(?:覆盖|见|报告|呈现)|不包含|\b(?:not disclosed|not reported)\b", re.IGNORECASE)
_EXPLICIT_NEGATION = re.compile(
    r"未(?:使用|采用|包含|涉及)|不(?:使用|采用|包含|涉及)|"
    r"\b(?:not|without|no)\b", re.IGNORECASE,
)


def _guard_unsupported_absence(
    review: NoveltyPointReview, request: NoveltyPointReviewRequest
) -> NoveltyPointReview:
    """Fail closed on absence claims when no supplied quotation states an absence.

    This is a narrow syntactic guard, not a substitute for semantic review. It
    deliberately preserves the relevant works so partial overlap remains visible.
    """
    if review.status is not ReviewStatus.REVIEWED:
        return review
    assertions = "\n".join([
        review.verdict_reason or "",
        *(work.relevance_reason for work in review.highly_relevant_works),
    ])
    if not (_STRONG_ABSENCE.search(assertions) or
            (review.verdict is not None and review.verdict.value == "novel" and
             _NOVEL_ABSENCE.search(assertions))):
        return review
    if any(_EXPLICIT_NEGATION.search(item.quote) for item in request.evidence):
        return review
    return NoveltyPointReview(
        novelty_point_id=review.novelty_point_id,
        status=ReviewStatus.INSUFFICIENT_EVIDENCE,
        highly_relevant_works=[work.model_copy(update={
            "relevance_reason": "该文献与查新点存在局部相关性；具体技术差异尚待原文核验。",
        }) for work in review.highly_relevant_works],
        supplement_request=SupplementRequest(
            reason="裁定依赖文献未采用特征的断言，但输入引文没有直接支持该否定；需核验原文。",
            missing_aspects=["核验被声称未采用的关键特征"],
        ),
    )


def _legacy_guard_shadow(review, request) -> dict[str, Any]:
    """Report the old lexical decision without affecting the formal review."""
    previous = _guard_unsupported_absence(review, request)
    assertions = "\n".join([review.verdict_reason or "", *(
        work.relevance_reason for work in review.highly_relevant_works)])
    matches = [{"rule": name, "start": match.start(), "end": match.end(),
                "text": match.group()}
               for name, pattern in (("strong_absence", _STRONG_ABSENCE),
                                     ("novel_absence", _NOVEL_ABSENCE))
               for match in pattern.finditer(assertions)]
    quote_matches = [{"evidence_id": item.evidence_id, "start": match.start(),
                      "end": match.end(), "text": match.group()}
                     for item in request.evidence
                     for match in _EXPLICIT_NEGATION.finditer(item.quote)]
    return {"variant_id": "G0_shadow", "would_change": previous.status != review.status,
            "old_status": previous.status.value, "formal_status": review.status.value,
            "old_verdict": previous.verdict.value if previous.verdict else None,
            "old_relevance_reasons": [work.relevance_reason for work in previous.highly_relevant_works],
            "assertion_matches": matches, "input_quote_matches": quote_matches}


def _record_review_event(phase: str, request, payload: dict[str, Any]) -> None:
    runtime = current_runtime_artifacts()
    if runtime is not None:
        runtime.record_reviewer_event({"phase": phase,
            "point_id": request.novelty_point.point_id,
            "card_ids": [c.card_id for c in request.cards], **payload})


def _feature_catalog(point) -> list[dict[str, str]]:
    return [{"feature_id": f"F{i}", "text": value,
             "sha256": hashlib.sha256(value.encode()).hexdigest()}
            for i, value in enumerate(point.technical_features, 1)]


def _register_review_reads(review, request, trace, catalog):
    reads = {}
    for event in trace:
        observation = getattr(event, "observation", None)
        if getattr(event, "kind", None) != "tool_result" or observation is None \
                or observation.tool_name != "reader" or not observation.succeeded:
            continue
        payload = observation.payload
        for raw in ([payload["read_result"]] if "read_result" in payload else payload.get("read_results", [])):
            if raw.get("char_end", 0) > raw.get("char_start", 0):
                reads[raw["read_id"]] = raw
    requested = {cite.read_id: cite for cite in review.read_citations}
    requested.update({ref: None for work in review.highly_relevant_works
                      for ref in work.evidence_ids if ref.startswith("read_") and ref not in requested})
    requested.update({ref: None for comparison in review.feature_comparisons
                      for ref in comparison.evidence_refs if ref.startswith("read_") and ref not in requested})
    bound_work = {item.work_id for item in request.evidence
                  if any(item.evidence_id in card.evidence_ids for card in request.cards)}
    registered, id_map = [], {}
    for read_id, cite in requested.items():
        raw = reads.get(read_id)
        if raw is None:
            raise ValueError(f"unread or empty read_id {read_id}")
        entry = next((item for item in catalog if item["artifact_id"] == raw["artifact_id"]
                      and item["namespace"] == raw["namespace"]
                      and item["work_id"] == raw["work_id"]), None)
        if entry is None or raw["work_id"] not in bound_work \
                or (entry["content_hash"] is not None and entry["content_hash"] != raw["sha256"]):
            raise ValueError("read citation is outside the authorized material catalog")
        start = raw["char_start"] if cite is None or cite.char_start is None else cite.char_start
        end = raw["char_end"] if cite is None or cite.char_end is None else cite.char_end
        if not raw["char_start"] <= start < end <= raw["char_end"]:
            raise ValueError("read citation range is outside the returned text")
        quote = raw["text"][start - raw["char_start"]:end - raw["char_start"]]
        cards = [card for card in request.cards if any(
            item.work_id == raw["work_id"] and item.evidence_id in card.evidence_ids
            for item in request.evidence)]
        if len(cards) != 1:
            raise ValueError("read citation must bind one Card and Work")
        card = cards[0]
        digest = hashlib.sha256(f"{card.card_id}\x1f{read_id}\x1f{start}\x1f{end}".encode()).hexdigest()
        evidence_id = "rev_ev_" + digest[:24]
        id_map[read_id] = evidence_id
        registered.append(ReviewEvidence(
            evidence_id=evidence_id, review_id="review_" + hashlib.sha256(card.card_id.encode()).hexdigest()[:20],
            origin_card_id=card.card_id, novelty_point_id=request.novelty_point.point_id,
            work_id=raw["work_id"], source_record_id=entry["source_record_id"],
            artifact_id=raw["artifact_id"], namespace=raw["namespace"],
            artifact_hash=raw["sha256"], read_id=read_id, char_start=start, char_end=end,
            exact_quote=quote, role=entry["role"], content_extent=entry["content_extent"],
            version_label=entry["version_label"],
        ))
    works = [work.model_copy(update={"evidence_ids": [id_map.get(eid, eid) for eid in work.evidence_ids]})
             for work in review.highly_relevant_works]
    comparisons = [item.model_copy(update={"evidence_refs": [id_map.get(ref, ref) for ref in item.evidence_refs]})
                   for item in review.feature_comparisons]
    return review.model_copy(update={"highly_relevant_works": works,
                             "feature_comparisons": comparisons, "review_evidence": registered})


def _compact_summary_rows(request, card_reviews):
    """Carry cited original and registered Reviewer quotes into a bounded summary."""
    cards = {card.card_id: card for card in request.cards}
    evidence = {item.evidence_id: item for item in request.evidence}
    rows, validated_ids = [], set()
    for row in card_reviews:
        card = cards.get(row.get("card_id"))
        if card is None or row.get("novelty_point_id") != request.novelty_point.point_id:
            raise ValueError("indexed card review is outside request scope")
        compact = {key: row[key] for key in ("index", "card_id", "novelty_point_id", "status")}
        compact["document_title"] = card.document_title
        if row.get("status") != "completed":
            compact["error"] = str(row.get("error", "单卡核验未完成"))[:500]
            rows.append(compact)
            continue
        review = NoveltyPointReview.model_validate(row.get("review"))
        single = NoveltyPointReviewRequest(
            subject_paper_id=request.subject_paper_id,
            novelty_point=request.novelty_point, tasks=request.tasks, cards=[card],
            evidence=[item for item in request.evidence if item.evidence_id in card.evidence_ids],
        )
        _validate_review_references(review, single)
        ids = list(dict.fromkeys(
            eid for work in review.highly_relevant_works for eid in work.evidence_ids
        ))
        ids = list(dict.fromkeys(ids + [eid for item in review.feature_comparisons
                                        for eid in item.evidence_refs]))
        validated_ids.update(ids)
        compact["review"] = review.model_dump(mode="json")
        additions = {item.evidence_id: item for item in review.review_evidence}
        ids.sort(key=lambda eid: eid not in additions)
        compact["review_evidence"] = [item.model_dump(mode="json") for item in review.review_evidence]
        budget = 12_000
        quotes = []
        for eid in ids:
            item = additions.get(eid) or evidence.get(eid)
            if item is None:
                raise ValueError("summary cites an unknown evidence_id")
            quote = item.exact_quote if isinstance(item, ReviewEvidence) else item.quote
            if len(quote) > budget:
                quotes.append({"evidence_id": eid, "work_id": item.work_id,
                    "artifact_id": item.artifact_id, "quote": quote[:max(0,budget)],
                    "quote_truncated": True, "original_chars": len(quote)})
                budget = 0
            else:
                quotes.append({"evidence_id": eid, "work_id": item.work_id,
                    "artifact_id": item.artifact_id, "quote": quote,
                    "quote_truncated": False, "original_chars": len(quote)})
                budget -= len(quote)
        compact["key_quotes"] = quotes
        compact["omitted_quote_count"] = sum(not item["quote"] for item in quotes)
        compact["summary_input_complete"] = all(not item["quote_truncated"] for item in quotes)
        rows.append(compact)
    return rows, validated_ids


def _summary_model_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Send each exact quote once, through the bounded key_quotes projection."""
    projected = []
    for row in rows:
        item = {key: value for key, value in row.items() if key != "review_evidence"}
        if "review" in item:
            item["review"] = {key: value for key, value in item["review"].items()
                              if key not in {"review_evidence", "read_citations"}}
        projected.append(item)
    return projected


def _summary_incomplete_reason(rows: list[dict[str, Any]]) -> str:
    reasons = [row.get("review", {}).get("incomplete_reason")
               for row in rows if row.get("status") == "completed"]
    if any(row.get("status") == "failed" for row in rows):
        reasons.append("technical_error")
    for cause in ("budget_exhausted", "technical_error", "material_unavailable"):
        if cause in reasons:
            return cause
    return "semantic_evidence"


def _validate_review_references(
    review: NoveltyPointReview,
    request: NoveltyPointReviewRequest,
) -> NoveltyPointReview:
    if review.novelty_point_id != request.novelty_point.point_id:
        raise ValueError("review novelty_point_id is outside request scope")
    cards = {item.card_id: item for item in request.cards}
    evidence = {item.evidence_id: item for item in request.evidence}
    additions = {item.evidence_id: item for item in review.review_evidence}
    if len(additions) != len(review.review_evidence):
        raise ValueError("duplicate review evidence ID")
    for item in additions.values():
        card = cards.get(item.origin_card_id)
        if card is None or item.novelty_point_id != request.novelty_point.point_id \
                or not any(e.work_id == item.work_id and e.evidence_id in card.evidence_ids
                           for e in request.evidence):
            raise ValueError("review evidence is outside Card and Work scope")
    for work in review.highly_relevant_works:
        if any(card_id not in cards for card_id in work.card_ids):
            raise ValueError("relevant work cites an unknown card_id")
        cited_evidence = []
        for evidence_id in work.evidence_ids:
            item = evidence.get(evidence_id) or additions.get(evidence_id)
            if item is None:
                raise ValueError("relevant work cites an unknown evidence_id")
            if item.work_id != work.work_id:
                raise ValueError("relevant work_id does not match cited evidence")
            cited_evidence.append(evidence_id)
        if any(not (set(cards[card_id].evidence_ids) |
                    {item.evidence_id for item in additions.values() if item.origin_card_id == card_id}
                   ).intersection(cited_evidence) for card_id in work.card_ids):
            raise ValueError("relevant work card_ids are not linked to cited evidence")
    feature_ids = {item["feature_id"] for item in _feature_catalog(request.novelty_point)}
    authorized_works = {item.work_id for item in request.evidence
                        if any(item.evidence_id in card.evidence_ids for card in request.cards)}
    for item in review.feature_comparisons:
        if item.feature_id not in feature_ids:
            raise ValueError("feature comparison cites an unknown feature_id")
        if item.work_id not in authorized_works:
            raise ValueError("feature comparison Work is outside request scope")
        if item.relation != "unknown" and not item.evidence_refs:
            raise ValueError("non-unknown feature comparison requires evidence")
        for evidence_id in item.evidence_refs:
            cited = evidence.get(evidence_id) or additions.get(evidence_id)
            if cited is None or cited.work_id != item.work_id:
                raise ValueError("feature comparison evidence is missing or from another Work")
    return review
