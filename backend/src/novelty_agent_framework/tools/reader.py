"""Agent-facing Reader tool built on the deterministic artifact reader."""

from __future__ import annotations

import time
from typing import TypeAlias

from ..schemas import (
    ReferenceReaderToolArguments,
    ReferenceReadRequest,
    ResearcherToolObservation,
    TaskResearchRequest,
)
from .reference_reader import ReferenceArtifactReaderTool


class ReaderTool:
    """Expose bounded Artifact reads to a Researcher agent."""

    name = "reader"
    description = "按 Artifact ID 读取可验证的文本字符片段。"
    args_schema = ReferenceReaderToolArguments

    def __init__(self, reader: ReferenceArtifactReaderTool) -> None:
        self.reader = reader

    async def ainvoke(
        self,
        arguments: ReferenceReaderToolArguments,
        *,
        scope: TaskResearchRequest,
    ) -> ResearcherToolObservation:
        started = time.monotonic()
        result = await self.reader.ainvoke(
            ReferenceReadRequest(
                subject_paper_id=scope.subject_paper_id,
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


# Transitional import compatibility. This is the same implementation, not a
# second tool, and therefore exposes the canonical ``reader`` tool name.
ReferenceReaderResearcherTool: TypeAlias = ReaderTool
