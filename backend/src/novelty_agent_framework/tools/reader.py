"""Agent-facing Reader tool built on the deterministic artifact reader."""

from __future__ import annotations

import time
from typing import TypeAlias
from pydantic import Field, create_model

from ..schemas import (
    ReaderArguments,
    ArtifactNamespace,
    NoveltyPointReviewRequest,
    ReferenceReadRequest,
    ResearcherToolObservation,
    TaskResearchRequest,
)
from .reference_reader import ReferenceArtifactReaderTool


class ReaderTool:
    """Expose bounded Artifact reads to a Researcher agent."""

    name = "reader"
    description = "按 Artifact ID 读取可验证的文本字符片段。"
    args_schema = ReaderArguments

    def __init__(
        self,
        reader: ReferenceArtifactReaderTool,
        *,
        default_chars_per_read: int | None = None,
    ) -> None:
        self.reader = reader
        resolved_default = min(8_000, reader.max_chars_per_read) if default_chars_per_read is None else default_chars_per_read
        if not 1 <= resolved_default <= reader.max_chars_per_read:
            raise ValueError("default_chars_per_read exceeds reader limit")
        self.default_chars_per_read = resolved_default
        self.args_schema = create_model(
            f"ConfiguredReaderArguments{resolved_default}_{reader.max_chars_per_read}",
            __base__=ReaderArguments,
            max_chars=(int, Field(default=resolved_default, ge=1, le=reader.max_chars_per_read)),
        )

    async def ainvoke(
        self,
        arguments: ReaderArguments,
        *,
        scope: TaskResearchRequest,
    ) -> ResearcherToolObservation:
        started = time.monotonic()
        result = await self.reader.ainvoke(
            ReferenceReadRequest(
                subject_paper_id=scope.subject_paper_id,
                namespace=arguments.namespace,
                artifact_id=arguments.artifact_id,
                char_start=arguments.char_start,
                max_chars=arguments.max_chars,
            )
        )
        return ResearcherToolObservation(
            tool_name=self.name,
            arguments=arguments.model_dump(mode="json"),
            succeeded=True,
            summary=(
                f"读取 artifact {result.artifact_id} 字符 "
                f"[{result.char_start}, {result.char_end})"
            ),
            payload={"read_result": result.model_dump(mode="json")},
            elapsed_ms=int((time.monotonic() - started) * 1000),
        )

    def project_model_context(
        self, observation: ResearcherToolObservation
    ) -> dict[str, object]:
        read = observation.payload["read_result"]
        return {
            "succeeded": observation.succeeded,
            "summary": observation.summary,
            "read_result": {
                key: read[key]
                for key in (
                    "read_id",
                    "work_id",
                    "artifact_id",
                    "role",
                    "char_start",
                    "char_end",
                    "text",
                    "has_more",
                )
            },
        }


class ReviewerReaderTool(ReaderTool):
    """只允许 Reviewer 回读当前查新点 Evidence 可达的 Artifact。"""

    description = "按 Artifact ID 回读当前查新点已获证据的文本字符片段。"

    async def ainvoke(
        self,
        arguments: ReaderArguments,
        *,
        scope: NoveltyPointReviewRequest,
    ) -> ResearcherToolObservation:
        referenced_evidence_ids = {
            evidence_id
            for card in scope.cards
            for evidence_id in card.evidence_ids
        }
        allowed_artifact_ids = {
            item.artifact_id
            for item in scope.evidence
            if item.evidence_id in referenced_evidence_ids
        }
        if arguments.namespace is not ArtifactNamespace.RESEARCH_REFERENCE:
            raise PermissionError("reviewer may only read research-reference artifacts")
        if arguments.artifact_id not in allowed_artifact_ids:
            raise PermissionError(
                f"artifact {arguments.artifact_id!r} is outside reviewer scope"
            )
        started = time.monotonic()
        result = await self.reader.ainvoke(
            ReferenceReadRequest(
                subject_paper_id=scope.subject_paper_id,
                namespace=arguments.namespace,
                artifact_id=arguments.artifact_id,
                char_start=arguments.char_start,
                max_chars=arguments.max_chars,
            )
        )
        if result.artifact_id not in allowed_artifact_ids:
            raise PermissionError("reader returned an artifact outside reviewer scope")
        return ResearcherToolObservation(
            tool_name=self.name,
            arguments=arguments.model_dump(mode="json"),
            succeeded=True,
            summary=(
                f"读取 artifact {result.artifact_id} 字符 "
                f"[{result.char_start}, {result.char_end})"
            ),
            payload={"read_result": result.model_dump(mode="json")},
            elapsed_ms=int((time.monotonic() - started) * 1000),
        )


# Transitional import compatibility. This is the same implementation, not a
# second tool, and therefore exposes the canonical ``reader`` tool name.
ReferenceReaderResearcherTool: TypeAlias = ReaderTool
