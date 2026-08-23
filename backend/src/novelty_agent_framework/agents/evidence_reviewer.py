"""证据 Reviewer：对通过 Validator 的 EvidenceCard 进行语义与证据一致性审查。

Reviewer 是 Validator 之后的第二道门控：

- Validator 负责字段/阈值/去重等便宜、稳定的硬规则；
- Reviewer 负责语义层判断：main_contribution 是否被 sources 支撑、
  overlaps/differences 是否有证据、引文与结论是否一致、摘要级证据是否
  被夸大为全文级结论、confidence 是否虚高、卡内是否自相矛盾等。

Reviewer 严格只读：不能修改 EvidenceCard 的任何字段，也不能创造新的
DOI/URL/引文/相同点/不同点。它只输出结构化裁定（accept / reject /
needs_more_evidence）和问题列表，由工作流决定是否放行。
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from backend.env import (
    ChatMessage,
    ModelCallOptions,
    ModelClient,
    ModelRegistry,
    PromptLibrary,
)

from ..ports import EvidenceReviewer, ReviewResult
from ..schemas import (
    EvidenceCard,
    EvidenceReviewDecision,
    EvidenceReviewIssue,
    IssueSeverity,
    NoveltyPoint,
    ResearchTask,
    ReviewVerdict,
)


# 受控问题代码白名单。模型返回的 issue.code 必须落在其中，否则视为无效。
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
    """Reviewer 运行配置。

    ``enabled=False`` 时工作流不会调用 Reviewer，维持原 Validator 后直通
    Coordinator 的兼容行为；默认值保证离线测试和 Demo 不依赖真实 LLM。
    """

    enabled: bool = False
    model_alias: str = "reviewer"
    temperature: float = 0.0
    max_cards_per_call: int = 8
    fail_closed: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature 必须位于 0 到 2 之间")
        if self.max_cards_per_call < 1:
            raise ValueError("max_cards_per_call 必须至少为 1")


class DemoEvidenceReviewer:
    """Null/Demo 实现：不调用 LLM，所有输入卡原样 ACCEPT。

    用于默认工作流、CI 和无模型环境，保证 Reviewer 接口可被注入但不消耗
    Token。``reviewed_confidence`` 直接复用卡片自身的 confidence。
    """

    def review(
        self,
        cards: Sequence[EvidenceCard],
        *,
        points: Sequence[NoveltyPoint],
        tasks: Sequence[ResearchTask],
    ) -> ReviewResult:
        if not cards:
            return ReviewResult(
                accepted=(),
                rejected=(),
                needs_more=(),
                decisions=(),
            )

        decisions = tuple(
            EvidenceReviewDecision(
                card_id=card.card_id,
                verdict=ReviewVerdict.ACCEPT,
                issues=[],
                reviewed_confidence=card.confidence,
            )
            for card in cards
        )
        return ReviewResult(
            accepted=tuple(cards),
            rejected=(),
            needs_more=(),
            decisions=decisions,
        )


class NoveltyEvidenceReviewer(EvidenceReviewer):
    """基于 LLM 的证据 Reviewer。

    复用项目已有的 ``ModelRegistry`` / ``PromptLibrary``，不自行读取 API
    Key 或创建模型客户端。失败策略由 ``EvidenceReviewerConfig.fail_closed``
    决定：``True``（默认）时审查失败的卡不进入最终证据；``False`` 仅用于
    开发兼容，会在 ``issues`` 中产生 warning。
    """

    def __init__(
        self,
        model_client: ModelClient | None = None,
        *,
        prompts: PromptLibrary | None = None,
        models: ModelRegistry | None = None,
        config: EvidenceReviewerConfig | None = None,
    ) -> None:
        self.model_client = model_client
        self._prompts = prompts
        self._models = models
        self.config = config or EvidenceReviewerConfig()

    def review(
        self,
        cards: Sequence[EvidenceCard],
        *,
        points: Sequence[NoveltyPoint],
        tasks: Sequence[ResearchTask],
    ) -> ReviewResult:
        if not cards:
            return ReviewResult(
                accepted=(),
                rejected=(),
                needs_more=(),
                decisions=(),
            )

        # fail fast：配置错误（未注入 ModelClient / ModelRegistry）不应被
        # 当成"单批失败"吞掉，让调用方尽早发现装配问题。
        self._client()

        valid_card_ids = {card.card_id for card in cards}
        decisions: list[EvidenceReviewDecision] = []
        failures: list[tuple[str, str]] = []  # (card_id, reason)

        for batch in _chunked(cards, self.config.max_cards_per_call):
            try:
                raw = self._call_model(batch, points, tasks)
                parsed = self._parse_decisions(raw, valid_card_ids)
            except Exception as exc:
                # 单批失败不崩全局；按 fail_closed 处理这一批。
                reason = f"review_failed: {exc}"
                for card in batch:
                    failures.append((card.card_id, reason))
                    decisions.append(
                        _failure_decision(
                            card.card_id, reason, self.config.fail_closed
                        )
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
        payload = {
            "points": [point.model_dump(mode="json") for point in points],
            "tasks": [task.model_dump(mode="json") for task in tasks],
            "cards": [card.model_dump(mode="json") for card in cards],
            "review_schema": _review_output_schema(),
        }
        variables = {
            "points_json": json.dumps(payload["points"], ensure_ascii=False),
            "tasks_json": json.dumps(payload["tasks"], ensure_ascii=False),
            "cards_json": json.dumps(payload["cards"], ensure_ascii=False),
            "review_schema": json.dumps(
                payload["review_schema"], ensure_ascii=False
            ),
        }

        if self._prompts is not None:
            rendered = self._prompts.render(
                "reviewer/review_evidence", **variables
            )
            system, user = rendered.system, rendered.user
        else:
            system = _fallback_system_prompt()
            user = (
                "请审查以下 EvidenceCard 列表，逐卡输出结构化决定。\n\n"
                f"输入数据：\n{json.dumps(payload, ensure_ascii=False)}"
            )

        client = self._client()
        response = client.complete(
            [
                ChatMessage(role="system", content=system),
                ChatMessage(role="user", content=user),
            ],
            options=ModelCallOptions(temperature=self.config.temperature),
        )
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ValueError("NoveltyEvidenceReviewer 返回内容不是合法 JSON") from exc

    def _parse_decisions(
        self,
        raw: Any,
        valid_card_ids: frozenset[str],
    ) -> "_ParsedBatch":
        """解析模型返回，严格过滤幻觉。

        - 顶层必须是 ``{"decisions": [...]}`` 或直接是 list；
        - 每个 decision 必须通过 ``EvidenceReviewDecision`` 严格校验（extra=forbid），
          自动丢弃模型擅自塞入的"修改后的 EvidenceCard"字段；
        - card_id 不在输入里的决定直接丢弃（防幻觉）；
        - issue.code 不在白名单的会被替换为 ``missing_evidence_detail``。
        """

        items = _normalize_decision_list(raw)
        decisions: list[EvidenceReviewDecision] = []
        failures: list[tuple[str, str]] = []

        for item in items:
            try:
                decision = EvidenceReviewDecision.model_validate(item)
            except ValidationError:
                continue
            if decision.card_id not in valid_card_ids:
                # 模型幻觉的 card_id：直接丢弃，不进入决定列表。
                continue
            cleaned = _sanitize_issues(decision)
            decisions.append(cleaned)

        return _ParsedBatch(decisions=decisions, failures=failures)

    def _apply_verdict(
        self,
        cards: Sequence[EvidenceCard],
        decisions: Sequence[EvidenceReviewDecision],
    ) -> tuple[list[EvidenceCard], list[tuple[str, str]], list[str]]:
        """根据裁定结果分组：accepted / rejected / needs_more。

        缺失决定的卡按 ``fail_closed`` 处理：
        - True：进入 rejected，原因 ``review_missing_decision``；
        - False：进入 accepted（兼容模式）。
        """

        decision_by_id = {d.card_id: d for d in decisions}
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

            verdict = decision.verdict
            if verdict is ReviewVerdict.ACCEPT:
                # Reviewer 不能修改卡，原样透传。
                accepted.append(card)
            elif verdict is ReviewVerdict.REJECT:
                rejected.append((card.card_id, _summarize_decision(decision)))
            else:  # NEEDS_MORE_EVIDENCE
                needs_more.append(card.card_id)

        return accepted, rejected, needs_more

    def _client(self) -> ModelClient:
        if self.model_client is not None:
            return self.model_client
        if self._models is not None:
            return self._models.client_for(self.config.model_alias)
        raise NotImplementedError(
            "NoveltyEvidenceReviewer 需要注入 ModelClient 或 ModelRegistry"
        )


@dataclass(frozen=True)
class _ParsedBatch:
    """单批 LLM 返回解析的中间结果。"""

    decisions: list[EvidenceReviewDecision]
    failures: list[tuple[str, str]]


def _chunked(cards: Sequence[EvidenceCard], size: int) -> list[list[EvidenceCard]]:
    if size <= 0:
        raise ValueError("chunk size 必须为正")
    return [list(cards[i : i + size]) for i in range(0, len(cards), size)]


def _normalize_decision_list(raw: Any) -> list[dict[str, Any]]:
    """兼容 ``{"decisions": [...]}`` 和直接 list 两种形态。"""

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
    """把不在白名单的 issue.code 替换为 ``missing_evidence_detail``。"""

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
    first = decision.issues[0].message
    return f"{codes}: {first}"


def _failure_decision(
    card_id: str, reason: str, fail_closed: bool
) -> EvidenceReviewDecision:
    """构造批失败时的兜底决定。

    - ``fail_closed=True``：verdict=REJECT，卡片不进入最终证据；
    - ``fail_closed=False``：verdict=ACCEPT，但 issues 中保留 review_failed 警告，
      兼容模式下放行但不静默吞错。
    """

    if fail_closed:
        return EvidenceReviewDecision(
            card_id=card_id,
            verdict=ReviewVerdict.REJECT,
            issues=[
                EvidenceReviewIssue(
                    code="missing_evidence_detail",
                    message=reason,
                    severity=IssueSeverity.ERROR,
                )
            ],
            reviewed_confidence=0.0,
        )
    return EvidenceReviewDecision(
        card_id=card_id,
        verdict=ReviewVerdict.ACCEPT,
        issues=[
            EvidenceReviewIssue(
                code="missing_evidence_detail",
                message=f"fail_open 放行（{reason}）",
                severity=IssueSeverity.WARNING,
            )
        ],
        reviewed_confidence=0.0,
    )


def _review_output_schema() -> dict[str, Any]:
    """供 Prompt 注入的输出 schema 说明。"""

    return {
        "type": "object",
        "required": ["decisions"],
        "properties": {
            "decisions": {
                "type": "array",
                "items": EvidenceReviewDecision.model_json_schema(),
            }
        },
    }


def _fallback_system_prompt() -> str:
    return (
        "你是论文查新系统的证据审查 Agent。你只能依据输入内容判断 EvidenceCard 的"
        "语义和证据一致性，不能修改 EvidenceCard，不能创造新的 DOI/URL/引文/相同点/"
        "不同点，不能使用模型记忆补充论文事实。无法判断时输出 needs_more_evidence，"
        "不能猜测。输出必须是 JSON：{\"decisions\": [EvidenceReviewDecision, ...]}。"
        "禁止输出开场白、解释性 Markdown 或自由文本。"
    )
