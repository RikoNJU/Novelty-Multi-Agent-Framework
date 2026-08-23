"""任务级 Researcher 的可扩展工具端口、注册表和作用域适配器。"""

from __future__ import annotations

import re
import time
from typing import Any, Protocol

from ..schemas import (
    ResearcherToolObservation,
    StrictModel,
    StructuredRetrievalToolArguments,
    StructuredSourceRetrievalRequest,
    TaskResearchRequest,
)
from .structured_retrieval import StructuredSourceRetrievalTool


class ResearcherTool(Protocol):
    name: str
    description: str
    args_schema: type[StrictModel]

    async def ainvoke(
        self, arguments: StrictModel, *, scope: TaskResearchRequest
    ) -> ResearcherToolObservation: ...


class ResearcherToolRegistry:
    def __init__(self, tools: list[ResearcherTool] | None = None) -> None:
        self._tools: dict[str, ResearcherTool] = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: ResearcherTool) -> None:
        name = tool.name.strip()
        if not name:
            raise ValueError("tool name cannot be empty")
        if name in self._tools:
            raise ValueError(f"duplicate researcher tool {name!r}")
        self._tools[name] = tool

    def get(self, name: str) -> ResearcherTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ValueError(f"unregistered researcher tool {name!r}") from exc

    def descriptions(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "arguments_schema": tool.args_schema.model_json_schema(),
            }
            for tool in self._tools.values()
        ]

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._tools)

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        scope: TaskResearchRequest,
    ) -> ResearcherToolObservation:
        started = time.monotonic()
        try:
            tool = self.get(tool_name)
            validated = tool.args_schema.model_validate(arguments)
            return await tool.ainvoke(validated, scope=scope)
        except Exception as exc:
            return ResearcherToolObservation(
                tool_name=tool_name,
                arguments=_json_arguments(arguments),
                succeeded=False,
                error=_safe_error(exc),
                elapsed_ms=int((time.monotonic() - started) * 1000),
            )


class StructuredRetrievalResearcherTool:
    name = "structured_source_retrieval"
    description = "在一个已配置结构化来源中检索并保存候选文献。"
    args_schema = StructuredRetrievalToolArguments

    def __init__(self, tools_by_source: dict[str, StructuredSourceRetrievalTool]) -> None:
        self.tools_by_source = dict(tools_by_source)

    async def ainvoke(
        self,
        arguments: StructuredRetrievalToolArguments,
        *,
        scope: TaskResearchRequest,
    ) -> ResearcherToolObservation:
        source_id = arguments.source_id.strip().lower()
        try:
            tool = self.tools_by_source[source_id]
        except KeyError as exc:
            raise ValueError(f"structured source {source_id!r} is unavailable") from exc
        started = time.monotonic()
        bundle = await tool.ainvoke(
            StructuredSourceRetrievalRequest(
                subject_paper_id=scope.subject_paper_id,
                source_id=source_id,
                novelty_point=scope.novelty_point,
                research_task=scope.research_task,
                run_id=scope.run_id,
            )
        )
        return ResearcherToolObservation(
            tool_name=self.name,
            arguments=arguments.model_dump(mode="json"),
            succeeded=True,
            summary=(
                f"发现 {len(bundle.works)} 个作品，保存 {len(bundle.artifacts)} 个制品"
            ),
            payload={"bundle": bundle.model_dump(mode="json")},
            elapsed_ms=int((time.monotonic() - started) * 1000),
        )


def _safe_error(exc: Exception) -> str:
    message = re.sub(
        r"(?i)(api[_-]?key|authorization|cookie)\s*[:=]\s*\S+",
        r"\1=<redacted>",
        str(exc),
    )
    return f"{type(exc).__name__}: {message}"[:1000]


def _json_arguments(arguments: Any) -> dict[str, Any]:
    if not isinstance(arguments, dict):
        return {"invalid_arguments_type": type(arguments).__name__}
    return {
        str(key): value
        for key, value in arguments.items()
        if value is None or isinstance(value, (str, int, float, bool, list, dict))
    }
