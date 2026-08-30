"""核心运行时能力；Harness 使用惰性导入以避免与 tools 形成导入环。"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .errors import WorkflowExecutionError

if TYPE_CHECKING:
    from .tool_call_harness import (
        ToolCallHarness,
        ToolCallHarnessConfig,
        ToolCallHarnessError,
        ToolCallHarnessResult,
    )

_HARNESS_EXPORTS = (
    "ToolCallHarness",
    "ToolCallHarnessConfig",
    "ToolCallHarnessError",
    "ToolCallHarnessResult",
)

__all__ = ["WorkflowExecutionError", *_HARNESS_EXPORTS]


def __getattr__(name: str) -> Any:
    if name not in _HARNESS_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from . import tool_call_harness

    value = getattr(tool_call_harness, name)
    globals()[name] = value
    return value
