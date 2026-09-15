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
from ..schemas.research_tools import ReaderCallArguments


class ReaderTool:
    """Expose bounded Artifact reads to a Researcher agent."""

    name = "reader"
    description = ('按 Artifact ID 读取可验证文本。发现多个候选后优先一次批量读取必要片段：'
                   'reads=[{"artifact_id":"...","max_chars":2000}, ...]，最多4段；'
                   '每段保留独立 read_id、来源和字符范围。也支持单个 artifact_id。')
    args_schema = ReaderCallArguments

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
        item_schema = create_model(
            f"ConfiguredReaderArguments{resolved_default}_{reader.max_chars_per_read}",
            __base__=ReaderArguments,
            max_chars=(int, Field(default=resolved_default, ge=1, le=reader.max_chars_per_read)),
        )
        self.args_schema = create_model(
            f"ConfiguredReaderCall{resolved_default}_{reader.max_chars_per_read}",
            __base__=ReaderCallArguments,
            max_chars=(int, Field(default=resolved_default, ge=1, le=reader.max_chars_per_read)),
            reads=(list[item_schema] | None, Field(default=None, min_length=1, max_length=4)),
        )

    async def ainvoke(
        self,
        arguments: ReaderArguments,
        *,
        scope: TaskResearchRequest,
    ) -> ResearcherToolObservation:
        if getattr(arguments, "reads", None) is not None:
            return await self._read_batch(arguments, scope=scope)
        started = time.monotonic()
        result = await self.reader.ainvoke(
            ReferenceReadRequest(
                subject_paper_id=scope.subject_paper_id,
                namespace=self._namespace_for(scope.subject_paper_id, arguments),
                artifact_id=arguments.artifact_id,
                char_start=arguments.char_start,
                max_chars=arguments.max_chars,
            )
        )
        return ResearcherToolObservation(
            tool_name=self.name,
            arguments=arguments.model_dump(mode="json", exclude_none=True),
            succeeded=True,
            summary=(
                f"读取 artifact {result.artifact_id} 字符 "
                f"[{result.char_start}, {result.char_end})"
            ),
            payload={"read_result": result.model_dump(mode="json")},
            elapsed_ms=int((time.monotonic() - started) * 1000),
        )

    async def _read_batch(self, arguments, *, scope) -> ResearcherToolObservation:
        started = time.monotonic()
        results, errors = [], []
        # Local reads are bounded; batching removes model round trips, without
        # weakening the single-tool policy or creating unbounded I/O concurrency.
        for index, request in enumerate(arguments.reads):
            try:
                observation = await self.ainvoke(request, scope=scope)
                results.append(observation.payload["read_result"])
            except Exception as exc:
                errors.append({"index": index, "artifact_id": request.artifact_id,
                               "error_type": type(exc).__name__, "message": str(exc)[:500]})
        return ResearcherToolObservation(
            tool_name=self.name, arguments=arguments.model_dump(mode="json"),
            succeeded=bool(results),
            summary=f"批量读取：成功 {len(results)} 段，失败 {len(errors)} 段",
            payload={"read_results": results, "read_errors": errors},
            elapsed_ms=int((time.monotonic() - started) * 1000),
        )

    def _namespace_for(
        self, subject_paper_id: str, arguments: ReaderArguments
    ) -> ArtifactNamespace:
        """按制品实际归属判定命名空间。

        模型只转述工具给出的 artifact_id，无法判断它属于研究语料还是论文自带
        参考语料（实测唯一的失败原因就是这里被默认成了 research_reference），
        所以归属由工具查 Manifest 决定，而不是让模型猜。
        """

        namespace = self.reader.locate(subject_paper_id, arguments.artifact_id)
        if namespace is None:
            raise ValueError(
                f"unknown artifact_id {arguments.artifact_id!r} in the research or "
                "subject reference manifest"
            )
        return namespace

    def project_model_context(
        self, observation: ResearcherToolObservation
    ) -> dict[str, object]:
        if "read_results" in observation.payload:
            return {"succeeded": observation.succeeded, "summary": observation.summary,
                    "read_results": observation.payload["read_results"],
                    "read_errors": observation.payload["read_errors"]}
        read = observation.payload["read_result"]
        return {
            "succeeded": observation.succeeded,
            "summary": observation.summary,
            "read_result": {
                key: read[key]
                for key in (
                    "namespace",
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

    description = "仅回读当前查新点 Evidence 可达的 Artifact。" + ReaderTool.description

    async def ainvoke(
        self,
        arguments: ReaderArguments,
        *,
        scope: NoveltyPointReviewRequest,
    ) -> ResearcherToolObservation:
        if getattr(arguments, "reads", None) is not None:
            return await self._read_batch(arguments, scope=scope)
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
        if arguments.artifact_id not in allowed_artifact_ids:
            raise PermissionError(
                f"artifact {arguments.artifact_id!r} is outside reviewer scope"
            )
        addresses = {
            (ArtifactNamespace(item.provenance.get("artifact_namespace", "research_reference")), item.work_id)
            for item in scope.evidence
            if item.evidence_id in referenced_evidence_ids and item.artifact_id == arguments.artifact_id
        }
        if len(addresses) != 1:
            raise PermissionError("ambiguous reviewer artifact address")
        namespace, work_id = next(iter(addresses))
        started = time.monotonic()
        result = await self.reader.ainvoke(
            ReferenceReadRequest(
                subject_paper_id=scope.subject_paper_id,
                namespace=namespace,
                artifact_id=arguments.artifact_id,
                char_start=arguments.char_start,
                max_chars=arguments.max_chars,
            )
        )
        if (result.artifact_id != arguments.artifact_id
                or result.namespace != namespace or result.work_id != work_id):
            raise PermissionError("reader returned an artifact outside reviewer scope")
        return ResearcherToolObservation(
            tool_name=self.name,
            arguments=arguments.model_dump(mode="json", exclude_none=True),
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
