"""Trace-derived, model-visible progress projection contracts."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Any, Mapping, Protocol

if TYPE_CHECKING:
    from .tool_call_harness import ToolCallHarnessEvent
    from ..tools import ResearcherToolRegistry


class HarnessProgressProjector(Protocol):
    """Derive a replaceable progress view from immutable harness facts."""

    def project(
        self,
        *,
        trace: tuple["ToolCallHarnessEvent", ...],
        registry: "ResearcherToolRegistry",
        config: object | None = None,
    ) -> Mapping[str, Any] | str | None: ...


class TraceHarnessProgressProjector:
    """Compute only provider- and business-neutral statistics."""

    def project(
        self,
        *,
        trace: tuple["ToolCallHarnessEvent", ...],
        registry: "ResearcherToolRegistry",
        config: object | None = None,
    ) -> Mapping[str, Any]:
        del registry, config
        tool_calls = [event for event in trace if event.kind == "tool_call"]
        counts = Counter(
            event.tool_call.name
            for event in tool_calls
            if event.tool_call is not None
        )
        last_tool_name = (
            tool_calls[-1].tool_call.name
            if tool_calls and tool_calls[-1].tool_call is not None
            else None
        )
        last_tool_succeeded: bool | None = None
        if last_tool_name is not None:
            for event in reversed(trace):
                if (
                    event.kind == "tool_result"
                    and event.tool_call is not None
                    and event.tool_call.name == last_tool_name
                    and event.observation is not None
                ):
                    last_tool_succeeded = event.observation.succeeded
                    break
        return {
            "turns_used": sum(
                event.kind == "assistant_response" for event in trace
            ),
            "total_tool_calls": len(tool_calls),
            "per_tool_call_counts": dict(sorted(counts.items())),
            "last_tool_name": last_tool_name,
            "last_tool_succeeded": last_tool_succeeded,
        }
