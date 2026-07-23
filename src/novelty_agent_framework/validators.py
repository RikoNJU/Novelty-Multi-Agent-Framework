"""Evidence Card 的确定性质量门控。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from .ports import ValidationResult
from .schemas import EvidenceCard, ResearchTask


@dataclass(frozen=True)
class EvidenceValidationConfig:
    """证据门槛可以独立调整，不需要修改 Agent Prompt。"""

    minimum_confidence: float = 0.5
    minimum_relevance: float = 0.4
    require_direct_quote: bool = True

    def __post_init__(self) -> None:
        for name, value in (
            ("minimum_confidence", self.minimum_confidence),
            ("minimum_relevance", self.minimum_relevance),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} 必须位于 0 到 1 之间")


class DefaultEvidenceValidator:
    """拒绝不可追溯、低质量或任务归属错误的证据。"""

    def __init__(self, config: EvidenceValidationConfig | None = None) -> None:
        self.config = config or EvidenceValidationConfig()

    def validate(
        self,
        cards: Sequence[EvidenceCard],
        *,
        tasks: Sequence[ResearchTask],
    ) -> ValidationResult:
        task_by_id = {task.task_id: task for task in tasks}
        candidates: dict[tuple[str, str], list[EvidenceCard]] = {}
        rejected: list[tuple[str, str]] = []
        issues: list[tuple[str, str, str, str | None]] = []

        for card in cards:
            reason = self._rejection_reason(card, task_by_id)
            if reason is not None:
                rejected.append((card.card_id, reason))
                issues.append(
                    (
                        "invalid_evidence",
                        f"Evidence Card {card.card_id} 被拒绝：{reason}",
                        "warning",
                        card.task_id,
                    )
                )
                continue

            key = (card.novelty_point_id, self._normalize_title(card.document_title))
            candidates.setdefault(key, []).append(card)

        accepted: list[EvidenceCard] = []
        for duplicates in candidates.values():
            best = max(duplicates, key=lambda card: (card.confidence, card.relevance))
            accepted.append(best)
            for duplicate in duplicates:
                if duplicate is best:
                    continue
                rejected.append((duplicate.card_id, f"与 {best.card_id} 重复"))
                issues.append(
                    (
                        "duplicate_evidence",
                        f"Evidence Card {duplicate.card_id} 与 {best.card_id} 指向同一文献",
                        "warning",
                        duplicate.task_id,
                    )
                )

        accepted.sort(key=lambda card: (card.novelty_point_id, card.document_title))
        return ValidationResult(
            accepted=tuple(accepted),
            rejected=tuple(rejected),
            issues=tuple(issues),
        )

    def _rejection_reason(
        self,
        card: EvidenceCard,
        task_by_id: dict[str, ResearchTask],
    ) -> str | None:
        task = task_by_id.get(card.task_id)
        if task is None:
            return "task_id 不属于当前工作流"
        if task.novelty_point_id != card.novelty_point_id:
            return "查新点与调研任务不一致"
        if card.confidence < self.config.minimum_confidence:
            return "证据置信度低于门槛"
        if card.relevance < self.config.minimum_relevance:
            return "文献相关性低于门槛"
        if not card.sources:
            return "缺少可追溯文献来源"
        if not any(source.doi or source.url for source in card.sources):
            return "来源缺少 DOI 或 URL"
        if self.config.require_direct_quote and not any(
            source.quote and source.location for source in card.sources
        ):
            return "缺少原文摘录或原文位置"
        return None

    @staticmethod
    def _normalize_title(title: str) -> str:
        return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", title.casefold())
