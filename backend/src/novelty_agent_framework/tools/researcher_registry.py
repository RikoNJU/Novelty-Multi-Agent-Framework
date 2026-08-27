"""Generic tool protocol and registry for task-scoped Researchers."""

from __future__ import annotations

import re
import time
from collections.abc import Mapping
from typing import Any, Protocol

from ..schemas import (
    ResearcherToolObservation,
    StrictModel,
    TaskResearchRequest,
)


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
            validated = self.validate_arguments(tool_name, arguments)
            return await self.execute_validated(
                tool_name, validated, scope=scope, started=started
            )
        except Exception as exc:
            return ResearcherToolObservation(
                tool_name=tool_name,
                arguments=_json_arguments(arguments),
                succeeded=False,
                error=_safe_error(exc),
                elapsed_ms=int((time.monotonic() - started) * 1000),
            )

    def validate_arguments(
        self, tool_name: str, arguments: Mapping[str, Any]
    ) -> StrictModel:
        """Return the canonical arguments, including schema-provided defaults."""

        tool = self.get(tool_name)
        return tool.args_schema.model_validate(dict(arguments))

    async def execute_validated(
        self,
        tool_name: str,
        arguments: StrictModel,
        *,
        scope: TaskResearchRequest,
        started: float | None = None,
    ) -> ResearcherToolObservation:
        """Execute one already-canonicalized argument object."""

        invoked_at = time.monotonic() if started is None else started
        try:
            tool = self.get(tool_name)
            if not isinstance(arguments, tool.args_schema):
                raise TypeError(
                    f"validated arguments for {tool_name!r} use the wrong schema"
                )
            return await tool.ainvoke(arguments, scope=scope)
        except Exception as exc:
            return ResearcherToolObservation(
                tool_name=tool_name,
                arguments=arguments.model_dump(mode="json"),
                succeeded=False,
                error=_safe_error(exc),
                elapsed_ms=int((time.monotonic() - invoked_at) * 1000),
            )

    def project_model_context(
        self,
        tool_name: str,
        observation: ResearcherToolObservation,
    ) -> dict[str, Any]:
        """Project a full audit observation into the model-visible data plane."""

        if not observation.succeeded:
            return {
                "succeeded": False,
                "summary": observation.summary,
                "error": observation.error,
            }
        tool = self.get(tool_name)
        projector = getattr(tool, "project_model_context", None)
        if projector is None:
            return observation.model_dump(mode="json")
        projected = projector(observation)
        if not isinstance(projected, dict):
            raise TypeError("tool model-context projector must return a dict")
        return projected


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
