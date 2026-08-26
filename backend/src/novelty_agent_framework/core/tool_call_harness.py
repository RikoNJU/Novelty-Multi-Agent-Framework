"""Serial model tool-calling loop over the Researcher tool registry.

This module will bridge:
- ModelClient native tool-calling protocol
- ResearcherToolRegistry tool definitions and execution
- assistant/tool message trajectory

The first implementation is serial:
- 0 tool calls -> finish
- 1 tool call -> execute and continue
- >1 tool calls -> protocol/policy error

Business tool implementations do not belong here.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field, replace
from typing import Literal

from backend.env import (
    ChatMessage,
    ModelCallOptions,
    ModelClient,
    ModelToolCall,
    ToolDefinition,
)

from ..schemas import ResearcherToolObservation, TaskResearchRequest
from ..tools import ResearcherToolRegistry
from .harness_progress import HarnessProgressProjector

HarnessEventKind = Literal[
    "initial_user_message",
    "assistant_response",
    "tool_call",
    "tool_result",
    "error",
    "finish",
]


@dataclass(frozen=True)
class ToolCallHarnessEvent:
    """One immutable fact appended during a harness run."""

    kind: HarnessEventKind
    message: ChatMessage | None = None
    tool_call: ModelToolCall | None = None
    observation: ResearcherToolObservation | None = None
    detail: str | None = None


class ToolCallHarnessError(RuntimeError):
    """Serial policy, model, or budget failure with the trace so far."""

    def __init__(
        self, message: str, *, trace: tuple[ToolCallHarnessEvent, ...] = ()
    ) -> None:
        super().__init__(message)
        self.trace = trace


@dataclass(frozen=True)
class ToolCallHarnessConfig:
    max_turns: int = 12
    max_tool_calls: int = 10
    per_tool_limits: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.max_turns < 1:
            raise ValueError("max_turns must be positive")
        if self.max_tool_calls < 1:
            raise ValueError("max_tool_calls must be positive")
        for name, limit in self.per_tool_limits.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("per_tool_limits keys must be non-empty tool names")
            if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
                raise ValueError(f"per_tool_limits[{name!r}] must be positive")


@dataclass(frozen=True)
class ToolCallHarnessResult:
    final_content: str | None
    trace: tuple[ToolCallHarnessEvent, ...]
    tool_calls_used: int
    turns_used: int


class ToolCallHarness:
    """Run a model until it finishes, executing at most one tool per turn."""

    def __init__(
        self,
        model_client: ModelClient,
        registry: ResearcherToolRegistry,
        *,
        config: ToolCallHarnessConfig | None = None,
        progress_projector: HarnessProgressProjector | None = None,
        progress_config: object | None = None,
        context_fragments: tuple[str, ...] = (),
    ) -> None:
        self.model_client = model_client
        self.registry = registry
        self.config = config or ToolCallHarnessConfig()
        self.progress_projector = progress_projector
        self.progress_config = progress_config
        self.context_fragments = context_fragments

    async def run(
        self,
        *,
        system_prompt: str,
        initial_user_message: str,
        scope: TaskResearchRequest,
        options: ModelCallOptions | None = None,
    ) -> ToolCallHarnessResult:
        log: list[ToolCallHarnessEvent] = [
            ToolCallHarnessEvent(
                kind="initial_user_message",
                message=ChatMessage(role="user", content=initial_user_message),
            )
        ]
        tool_definitions = _build_tool_definitions(self.registry)
        call_options = replace(options or ModelCallOptions(), tools=tool_definitions)
        tool_calls_used = 0
        per_tool_calls: Counter[str] = Counter()

        for turn in range(1, self.config.max_turns + 1):
            trace = tuple(log)
            progress = (
                self.progress_projector.project(
                    trace=trace,
                    registry=self.registry,
                    config=self.progress_config,
                )
                if self.progress_projector is not None
                else None
            )
            context = _build_context(
                system_prompt,
                trace,
                progress=progress,
                context_fragments=self.context_fragments,
            )
            try:
                response = await self.model_client.acomplete(
                    context, options=call_options
                )
            except Exception as exc:
                _append_error(log, f"model call failed: {type(exc).__name__}: {exc}")
                raise ToolCallHarnessError(
                    "model call failed", trace=tuple(log)
                ) from exc

            assistant_message = ChatMessage(
                role="assistant",
                content=response.content,
                tool_calls=tuple(response.tool_calls),
            )
            log.append(
                ToolCallHarnessEvent(
                    kind="assistant_response", message=assistant_message
                )
            )

            if not response.tool_calls:
                log.append(
                    ToolCallHarnessEvent(kind="finish", detail="model finished")
                )
                return ToolCallHarnessResult(
                    final_content=response.content,
                    trace=tuple(log),
                    tool_calls_used=tool_calls_used,
                    turns_used=turn,
                )

            if len(response.tool_calls) > 1:
                _append_error(log, "serial harness policy violation: multiple tool calls")
                raise ToolCallHarnessError(
                    "serial harness policy violation: expected at most one tool call",
                    trace=tuple(log),
                )

            if tool_calls_used >= self.config.max_tool_calls:
                _append_error(log, "tool-call budget exhausted")
                raise ToolCallHarnessError(
                    "tool-call budget exhausted", trace=tuple(log)
                )

            tool_call = response.tool_calls[0]
            tool_limit = self.config.per_tool_limits.get(tool_call.name)
            if tool_limit is not None and per_tool_calls[tool_call.name] >= tool_limit:
                detail = f"per-tool budget exhausted: {tool_call.name}"
                _append_error(log, detail)
                raise ToolCallHarnessError(detail, trace=tuple(log))
            log.append(
                ToolCallHarnessEvent(kind="tool_call", tool_call=tool_call)
            )
            observation = await self.registry.execute(
                tool_call.name,
                dict(tool_call.arguments),
                scope=scope,
            )
            tool_calls_used += 1
            per_tool_calls[tool_call.name] += 1
            model_context = self.registry.project_model_context(
                tool_call.name, observation
            )
            tool_message = ChatMessage(
                role="tool",
                tool_call_id=tool_call.id,
                content=_serialize_tool_result(model_context),
            )
            log.append(
                ToolCallHarnessEvent(
                    kind="tool_result",
                    message=tool_message,
                    tool_call=tool_call,
                    observation=observation,
                )
            )

        _append_error(log, "turn budget exhausted")
        raise ToolCallHarnessError("turn budget exhausted", trace=tuple(log))


def _build_tool_definitions(
    registry: ResearcherToolRegistry,
) -> tuple[ToolDefinition, ...]:
    return tuple(
        ToolDefinition(
            name=item["name"],
            description=item["description"],
            parameters=item["arguments_schema"],
        )
        for item in registry.descriptions()
    )


def _build_context(
    system_prompt: str,
    trace: tuple[ToolCallHarnessEvent, ...],
    *,
    progress: object | None = None,
    context_fragments: tuple[str, ...] = (),
) -> list[ChatMessage]:
    messages = [ChatMessage(role="system", content=system_prompt)]
    messages.extend(
        ChatMessage(role="system", content=fragment)
        for fragment in context_fragments
    )
    if progress is not None:
        content = (
            progress
            if isinstance(progress, str)
            else json.dumps(progress, ensure_ascii=False, sort_keys=True)
        )
        messages.append(
            ChatMessage(
                role="system",
                content=f"[HARNESS_PROGRESS]\n{content}\n[/HARNESS_PROGRESS]",
            )
        )
    messages.extend(
        event.message
        for event in trace
        if event.message is not None
        and event.kind
        in {"initial_user_message", "assistant_response", "tool_result"}
    )
    return messages


def _serialize_tool_result(model_context: dict) -> str:
    return json.dumps(
        model_context,
        ensure_ascii=False,
        sort_keys=True,
    )


def _append_error(log: list[ToolCallHarnessEvent], detail: str) -> None:
    log.append(ToolCallHarnessEvent(kind="error", detail=detail))
