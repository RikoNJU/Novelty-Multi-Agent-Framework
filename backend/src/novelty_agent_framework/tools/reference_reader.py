"""按 Manifest Artifact ID 安全读取参考文献文本片段。"""

from __future__ import annotations

import asyncio

from ..persistence import ReferenceStore
from ..schemas import ReferenceReadRequest, ReferenceReadResult


class ReferenceArtifactReaderTool:
    name = "reference_artifact_reader"
    description = "读取已保存参考文献 Artifact 的受限文本片段。"

    def __init__(
        self,
        reference_store: ReferenceStore | None = None,
        *,
        max_chars_per_read: int = 16_000,
    ) -> None:
        if not 1 <= max_chars_per_read <= 16_000:
            raise ValueError("max_chars_per_read must be in 1..16000")
        self.reference_store = reference_store or ReferenceStore()
        self.max_chars_per_read = max_chars_per_read

    async def ainvoke(self, request: ReferenceReadRequest) -> ReferenceReadResult:
        request = ReferenceReadRequest.model_validate(request)
        if request.max_chars > self.max_chars_per_read:
            raise ValueError(
                f"max_chars exceeds reader limit {self.max_chars_per_read}"
            )
        return self.reference_store.read_document_slice(
            request.subject_paper_id,
            artifact_id=request.artifact_id,
            char_start=request.char_start,
            max_chars=request.max_chars,
        )

    def invoke(self, request: ReferenceReadRequest) -> ReferenceReadResult:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.ainvoke(request))
        raise RuntimeError(
            "检测到正在运行的事件循环，请改用 await reader.ainvoke(...)"
        )
