"""查新点级 Reviewer：综合 EvidenceCard/Evidence 并按需回读原文。"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from backend.env import ChatMessage, ModelCallOptions, ModelClient, ModelRegistry, PromptLibrary

from ..ports import EvidenceReviewer, ReviewResult
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

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature 必须位于 0 到 2 之间")
        if self.max_cards_per_call < 1:
            raise ValueError("max_cards_per_call 必须至少为 1")
        if min(self.max_steps, self.max_tool_calls, self.max_total_read_chars) < 1:
            raise ValueError("reviewer harness budgets must be positive")


class DemoEvidenceReviewer:
    """Null/Demo 实现：不伪造语义判断，显式返回证据不足。"""

    def review(
        self, request: NoveltyPointReviewRequest
    ) -> NoveltyPointReview:
        request = NoveltyPointReviewRequest.model_validate(request)
        return _insufficient_review(
            request.novelty_point.point_id,
            "Demo Reviewer 不执行新颖性语义判定。",
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
        self, request: NoveltyPointReviewRequest
    ) -> NoveltyPointReview:
        request = NoveltyPointReviewRequest.model_validate(request)
        if not request.cards or not request.evidence:
            return _insufficient_review(
                request.novelty_point.point_id,
                "当前查新点没有可供可靠判定的已绑定证据。",
            )

        system, user = self._render_point_prompt(request)
        try:
            result = await self.harness.run(
                system_prompt=system,
                initial_user_message=user,
                scope=request,
                options=self.model_options
                or ModelCallOptions(
                    temperature=self.config.temperature,
                    tool_choice="auto",
                ),
            )
            review = NoveltyPointReview.model_validate_json(
                _extract_json(result.final_content)
            )
            return _validate_review_references(review, request)
        except Exception as exc:
            if not self.config.fail_closed:
                raise
            return _insufficient_review(
                request.novelty_point.point_id,
                f"Reviewer 无法完成可靠判定：{type(exc).__name__}: {exc}"[:500],
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
                "reviewer/review_evidence", **variables
            )
            return rendered.system, rendered.user
        return _fallback_point_system_prompt(), "\n".join(
            f"{key}: {value}" for key, value in variables.items()
        )

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
            rendered = self._prompts.render("reviewer/review_evidence", **variables)
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
    )


def _extract_json(content: str | None) -> str:
    text = (content or "").strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    return text[start : end + 1] if start != -1 and end > start else text


def _insufficient_review(point_id: str, reason: str) -> NoveltyPointReview:
    return NoveltyPointReview(
        novelty_point_id=point_id,
        status=ReviewStatus.INSUFFICIENT_EVIDENCE,
        supplement_request=SupplementRequest(reason=reason),
    )


def _validate_review_references(
    review: NoveltyPointReview,
    request: NoveltyPointReviewRequest,
) -> NoveltyPointReview:
    if review.novelty_point_id != request.novelty_point.point_id:
        raise ValueError("review novelty_point_id is outside request scope")
    cards = {item.card_id: item for item in request.cards}
    evidence = {item.evidence_id: item for item in request.evidence}
    for work in review.highly_relevant_works:
        if any(card_id not in cards for card_id in work.card_ids):
            raise ValueError("relevant work cites an unknown card_id")
        cited_evidence = []
        for evidence_id in work.evidence_ids:
            item = evidence.get(evidence_id)
            if item is None:
                raise ValueError("relevant work cites an unknown evidence_id")
            if item.work_id != work.work_id:
                raise ValueError("relevant work_id does not match cited evidence")
            cited_evidence.append(evidence_id)
        if any(
            not set(cards[card_id].evidence_ids).intersection(cited_evidence)
            for card_id in work.card_ids
        ):
            raise ValueError("relevant work card_ids are not linked to cited evidence")
    return review
