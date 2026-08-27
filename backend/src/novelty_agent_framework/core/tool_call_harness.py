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
    max_total_read_chars: int | None = None

    def __post_init__(self) -> None:
        if self.max_turns < 1:
            raise ValueError("max_turns must be positive")
        if self.max_tool_calls < 1:
            raise ValueError("max_tool_calls must be positive")
        if any(value < 1 for value in self.per_tool_limits.values()):
            raise ValueError("per_tool_limits must be positive")
        if self.max_total_read_chars is not None and self.max_total_read_chars < 1:
            raise ValueError("max_total_read_chars must be positive")


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
    ) -> None:
        self.model_client = model_client
        self.registry = registry
        self.config = config or ToolCallHarnessConfig()

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
        per_tool_counts: dict[str, int] = {}
        total_read_chars = 0

        for turn in range(1, self.config.max_turns + 1):
            context = _build_context(system_prompt, tuple(log))
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
                _append_error(log, "total tool-call budget exhausted")
                raise ToolCallHarnessError(
                    "total tool-call budget exhausted", trace=tuple(log)
                )

            tool_call = response.tool_calls[0]
            tool_limit = self.config.per_tool_limits.get(tool_call.name)
            tool_count = per_tool_counts.get(tool_call.name, 0)
            if tool_limit is not None and tool_count >= tool_limit:
                detail = f"{tool_call.name} tool-call budget exhausted"
                _append_error(log, detail)
                raise ToolCallHarnessError(detail, trace=tuple(log))
            if tool_call.name == "reader" and self.config.max_total_read_chars is not None:
                requested = tool_call.arguments.get("max_chars", 0)
                if isinstance(requested, int) and total_read_chars + requested > self.config.max_total_read_chars:
                    detail = "reader cumulative character budget exhausted"
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
            per_tool_counts[tool_call.name] = tool_count + 1
            if tool_call.name == "reader" and observation.succeeded:
                read = observation.payload.get("read_result", {})
                start, end = read.get("char_start"), read.get("char_end")
                if isinstance(start, int) and isinstance(end, int):
                    total_read_chars += max(0, end - start)
                    if (
                        self.config.max_total_read_chars is not None
                        and total_read_chars > self.config.max_total_read_chars
                    ):
                        detail = "reader cumulative character budget exhausted"
                        _append_error(log, detail)
                        raise ToolCallHarnessError(detail, trace=tuple(log))
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
) -> list[ChatMessage]:
    messages = [ChatMessage(role="system", content=system_prompt)]
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
