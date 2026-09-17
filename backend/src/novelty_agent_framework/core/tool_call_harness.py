"""Serial model tool-calling loop over the Researcher tool registry.

This module will bridge:
- ModelClient native tool-calling protocol
- task-scoped tool registry definitions and execution
- assistant/tool message trajectory

The first implementation is serial:
- 0 tool calls -> finish
- 1 tool call -> execute and continue
- >1 tool calls -> retain and execute only the first call

Business tool implementations do not belong here.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, replace
from typing import Any, Literal

from backend.env import (
    ChatMessage,
    ModelCallOptions,
    ModelClient,
    ModelResponse,
    ModelToolCall,
    ToolDefinition,
)

from ..schemas import ResearcherToolObservation
from .runtime_artifacts import current_runtime_artifacts

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


class ToolCallBudgetExhausted(ToolCallHarnessError):
    """A budget boundary eligible for one tool-free finalization."""


@dataclass(frozen=True)
class ToolCallHarnessConfig:
    finalize_on_budget: bool = False
    reuse_database_results: bool = False
    max_turns: int = 12
    max_tool_calls: int = 10
    per_tool_limits: dict[str, int] = field(default_factory=dict)
    max_total_read_chars: int | None = None
    finalization_instruction: str | None = None
    reserve_final_turn: bool = False
    report_budget: bool = False
    allow_one_read_budget_correction: bool = False

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
    stop_reason: str | None = None


class ToolCallHarness:
    """Run a model until it finishes, executing at most one tool per turn."""

    def __init__(
        self,
        model_client: ModelClient,
        registry: Any,
        *,
        config: ToolCallHarnessConfig | None = None,
    ) -> None:
        self.model_client = model_client
        self.registry = registry
        self.config = config or ToolCallHarnessConfig()

    async def run(
        self, *, system_prompt: str, initial_user_message: str,
        scope: Any, options: ModelCallOptions | None = None,
    ) -> ToolCallHarnessResult:
        try:
            return await self._run(
                system_prompt=system_prompt, initial_user_message=initial_user_message,
                scope=scope, options=options,
            )
        except ToolCallBudgetExhausted as exc:
            if not self.config.finalize_on_budget:
                raise
            return await self._finalize(system_prompt, exc, options)

    async def _finalize(self, system_prompt, error, options):
        # Complete any outstanding assistant/tool pair before appending a user turn.
        log = list(error.trace)
        pending = {}
        for event in log:
            message = event.message
            if message is None:
                continue
            for call in message.tool_calls or ():
                pending[call.id] = call
            if message.role == "tool":
                pending.pop(message.tool_call_id, None)
        for call in pending.values():
            log.append(ToolCallHarnessEvent(kind="tool_result", message=ChatMessage(
                role="tool", tool_call_id=call.id,
                content=json.dumps({"succeeded": False, "error": str(error)}),
            )))
        log.append(ToolCallHarnessEvent(kind="initial_user_message", message=ChatMessage(
            role="user", content=(self.config.finalization_instruction or (
                f"Research stopped: {error}. No further tool calls are allowed. "
                "This is the single reserved finalization turn. Return the required "
                "final JSON using only observations already received. Preserve exact "
                "Reader quotes, including mathematical markup. If no text supports "
                "evidence, return cards=[] with a concrete no_evidence_reason."
            )) + f"\nStop reason: {error}",
        )))
        try:
            response = await self.model_client.acomplete(
                _build_context(system_prompt, tuple(log)),
                options=replace(options or ModelCallOptions(), tools=(), tool_choice="none"),
            )
            if response.tool_calls:
                raise ValueError("finalization attempted a tool call")
        except Exception as exc:
            _append_error(log, f"budget finalization failed: {type(exc).__name__}: {exc}")
            raise ToolCallHarnessError("budget finalization failed", trace=tuple(log)) from exc
        log.append(ToolCallHarnessEvent(kind="assistant_response", message=ChatMessage(
            role="assistant", content=response.content,
        )))
        log.append(ToolCallHarnessEvent(kind="finish", detail="budget finalization"))
        return ToolCallHarnessResult(
            final_content=response.content, trace=tuple(log),
            tool_calls_used=sum(e.kind == "tool_call" for e in log),
            turns_used=sum(e.kind == "assistant_response" for e in log),
            stop_reason=str(error),
        )

    async def _run(
        self, *, system_prompt: str, initial_user_message: str,
        scope: Any, options: ModelCallOptions | None = None,
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
        read_budget_rejections = 0
        required_reader_artifact_ids: set[str] = set()
        database_results = {}  # Per invocation: never crosses task/plan/run scopes.

        exploration_turns = self.config.max_turns - int(self.config.reserve_final_turn)
        if exploration_turns < 1:
            raise ValueError("reserved final turn requires at least two total turns")
        for turn in range(1, exploration_turns + 1):
            if self.config.finalize_on_budget and self.config.reserve_final_turn \
                    and tool_calls_used >= self.config.max_tool_calls:
                raise ToolCallBudgetExhausted("tool-call exploration limit reached", trace=tuple(log))
            context = _build_context(system_prompt, tuple(log))
            if self.config.finalize_on_budget or self.config.report_budget:
                context[0] = replace(context[0], content=context[0].content + "\nBudget context: " + json.dumps({
                    "remaining_research_turns": exploration_turns - turn + 1,
                    "remaining_exploration_turns": exploration_turns - turn + 1,
                    "remaining_tool_calls": self.config.max_tool_calls - tool_calls_used,
                    "remaining_read_chars": (None if self.config.max_total_read_chars is None
                                             else self.config.max_total_read_chars - total_read_chars),
                    "remaining_exploration_seconds": (
                        max(0, round(self.model_client.deadline - time.monotonic(), 1))
                        if isinstance(getattr(self.model_client, "deadline", None), (int, float)) else None),
                    "finalization_reserved": self.config.finalize_on_budget and self.config.reserve_final_turn,
                    "remaining_per_tool": {
                        name: max(0, limit - per_tool_counts.get(name, 0))
                        for name, limit in self.config.per_tool_limits.items()
                    },
                    "instruction": "Finish within the remaining exploration budget; a reserved tool-free final turn follows if needed.",
                }))
            try:
                response = await self.model_client.acomplete(
                    context, options=call_options
                )
            except Exception as exc:
                _append_error(log, f"model call failed: {type(exc).__name__}: {exc}")
                raise ToolCallHarnessError(
                    "model call failed", trace=tuple(log)
                ) from exc

            if not response.tool_calls:
                assistant_message = ChatMessage(
                    role="assistant",
                    content=response.content,
                )
                log.append(
                    ToolCallHarnessEvent(
                        kind="assistant_response", message=assistant_message
                    )
                )
                log.append(
                    ToolCallHarnessEvent(kind="finish", detail="model finished")
                )
                return ToolCallHarnessResult(
                    final_content=response.content,
                    trace=tuple(log),
                    tool_calls_used=tool_calls_used,
                    turns_used=turn,
                )

            original_tool_calls = tuple(response.tool_calls)
            dropped_tool_calls = original_tool_calls[1:]
            if dropped_tool_calls:
                _append_error(
                    log,
                    json.dumps(
                        {
                            "policy": "SERIAL_FIRST_CALL",
                            "selected_tool_call_id": original_tool_calls[0].id,
                            "dropped_tool_call_ids": [
                                call.id for call in dropped_tool_calls
                            ],
                        },
                        sort_keys=True,
                    ),
                )
                response = ModelResponse(
                    content=response.content,
                    tool_calls=original_tool_calls[:1],
                    raw=response.raw,
                    usage=response.usage,
                )

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

            tool_call = response.tool_calls[0]
            try:
                validated_arguments = self.registry.validate_arguments(
                    tool_call.name, tool_call.arguments
                )
            except Exception:
                validated_arguments = None
            runtime = current_runtime_artifacts()
            resolved_arguments = (
                validated_arguments.model_dump(mode="json")
                if validated_arguments is not None
                else dict(tool_call.arguments)
            )
            runtime_call = (
                runtime.start_tool_call(
                    tool_call.name,
                    agent_arguments=dict(tool_call.arguments),
                    resolved_arguments=resolved_arguments,
                    agent_tool_call_id=tool_call.id,
                )
                if runtime is not None
                else None
            )

            if tool_calls_used >= self.config.max_tool_calls:
                detail = "total tool-call budget exhausted"
                _append_error(log, detail)
                if runtime is not None and runtime_call is not None:
                    runtime.finish_tool_call(
                        runtime_call,
                        raw_result=None,
                        normalized_result=None,
                        succeeded=False,
                        error={"type": "HarnessPolicyError", "message": detail},
                        failure_phase="PRE_TOOL",
                    )
                raise ToolCallBudgetExhausted(detail, trace=tuple(log))

            if required_reader_artifact_ids:
                requested_artifacts = _reader_artifact_ids(resolved_arguments)
                if (
                    tool_call.name != "reader"
                    or not requested_artifacts.intersection(required_reader_artifact_ids)
                ):
                    # 软性拒绝：不杀死任务，向模型回传拒绝消息（含必须读取的
                    # artifact_id），让它下一轮自我纠正；审计日志保留完整记录。
                    #
                    # 这里**不**递增 tool_calls_used：本次什么都没执行，却要占掉
                    # 一个调用名额，实测一个 16 次预算的任务里被白吃掉 5 次（31%）。
                    # 循环本身仍受 max_turns 约束，不存在无限拒绝的风险。
                    detail = (
                        "reader required after database_search returned artifact_ids"
                    )
                    _append_error(log, detail)
                    rejection = ChatMessage(
                        role="tool",
                        tool_call_id=tool_call.id,
                        content=json.dumps(
                            {
                                "succeeded": False,
                                "summary": detail,
                                "required_artifact_ids": sorted(
                                    required_reader_artifact_ids
                                ),
                            },
                            ensure_ascii=False,
                            sort_keys=True,
                        ),
                    )
                    log.append(
                        ToolCallHarnessEvent(
                            kind="tool_result",
                            message=rejection,
                            tool_call=tool_call,
                        )
                    )
                    if runtime is not None and runtime_call is not None:
                        runtime.finish_tool_call(
                            runtime_call,
                            raw_result=None,
                            normalized_result=json.loads(rejection.content),
                            succeeded=False,
                            error={"type": "HarnessPolicyError", "message": detail},
                            failure_phase="PRE_TOOL",
                        )
                    continue
            tool_limit = self.config.per_tool_limits.get(tool_call.name)
            tool_count = per_tool_counts.get(tool_call.name, 0)
            if tool_limit is not None and tool_count >= tool_limit:
                detail = f"{tool_call.name} tool-call budget exhausted"
                _append_error(log, detail)
                if runtime is not None and runtime_call is not None:
                    runtime.finish_tool_call(
                        runtime_call,
                        raw_result=None,
                        normalized_result=None,
                        succeeded=False,
                        error={"type": "HarnessPolicyError", "message": detail},
                        failure_phase="PRE_TOOL",
                    )
                raise ToolCallBudgetExhausted(detail, trace=tuple(log))
            if (
                tool_call.name == "reader"
                and validated_arguments is not None
                and self.config.max_total_read_chars is not None
            ):
                batch = getattr(validated_arguments, "reads", None)
                requested = (sum(item.max_chars for item in batch) if batch is not None
                             else getattr(validated_arguments, "max_chars"))
                remaining = self.config.max_total_read_chars - total_read_chars
                if requested > remaining:
                    detail = "reader cumulative character budget exhausted: request exceeds remaining"
                    _append_error(log, detail)
                    rejection = {"succeeded": False, "reason": "read_budget_exceeded",
                                 "requested_chars": requested, "remaining_chars": remaining,
                                 "instruction": "Shrink the request to the remaining limit or finish with the evidence already read."}
                    if runtime is not None and runtime_call is not None:
                        runtime.finish_tool_call(
                            runtime_call,
                            raw_result=None,
                            normalized_result=rejection,
                            succeeded=False,
                            error={"type": "HarnessPolicyError", "message": detail},
                            failure_phase="PRE_TOOL",
                        )
                    log.append(ToolCallHarnessEvent(kind="tool_result", tool_call=tool_call,
                        message=ChatMessage(role="tool", tool_call_id=tool_call.id,
                                            content=json.dumps(rejection))))
                    read_budget_rejections += 1
                    if (self.config.allow_one_read_budget_correction
                            and read_budget_rejections == 1 and turn < exploration_turns):
                        continue
                    raise ToolCallBudgetExhausted(detail, trace=tuple(log))
            log.append(
                ToolCallHarnessEvent(kind="tool_call", tool_call=tool_call)
            )
            cache_key = json.dumps(resolved_arguments, sort_keys=True, default=str)
            reusable = self.config.reuse_database_results and tool_call.name == "database_search"
            reused = reusable and cache_key in database_results
            try:
                if reused:
                    observation = database_results[cache_key]
                elif validated_arguments is None:
                    observation = await self.registry.execute(
                        tool_call.name,
                        dict(tool_call.arguments),
                        scope=scope,
                    )
                else:
                    observation = await self.registry.execute_validated(
                        tool_call.name, validated_arguments, scope=scope
                    )
                if reusable and not reused and _database_result_complete(observation):
                    database_results[cache_key] = observation
            except BaseException as exc:
                if runtime is not None and runtime_call is not None:
                    runtime.fail_tool_call(runtime_call, exc)
                raise
            try:
                model_context = self.registry.project_model_context(
                    tool_call.name, observation
                )
                if reused:
                    model_context = {**model_context, "reused_result": True,
                        "instruction": "同一任务和检索计划已执行过该来源，复用原结果，未重新请求数据库。读取已有候选或更换来源；无证据则如实收尾。"}
            except BaseException as exc:
                if runtime is not None and runtime_call is not None:
                    runtime.fail_tool_call(
                        runtime_call,
                        exc,
                        raw_result=observation.model_dump(mode="json"),
                        failure_phase="NORMALIZATION",
                    )
                raise
            if runtime is not None and runtime_call is not None:
                runtime.finish_tool_call(
                    runtime_call,
                    raw_result=observation.model_dump(mode="json"),
                    normalized_result=model_context,
                    succeeded=observation.succeeded,
                    error=observation.error,
                    failure_phase=(
                        None if observation.succeeded else "TOOL_EXECUTION"
                    ),
                )
            tool_calls_used += 1
            per_tool_counts[tool_call.name] = tool_count + 1
            if tool_call.name == "database_search" and observation.succeeded:
                required_reader_artifact_ids = _database_artifact_ids(observation)
            elif tool_call.name == "reader" and required_reader_artifact_ids:
                successful_artifacts = {
                    read.get("artifact_id") for read in _reader_results(observation)
                }
                if observation.succeeded and (
                    "read_results" not in observation.payload
                    or successful_artifacts.intersection(required_reader_artifact_ids)
                ):
                    required_reader_artifact_ids.clear()
                else:
                    # 失败时释放「这一个」制品的约束。否则该 id 永远读不出来时，
                    # 模型既不能换一篇读、也不能重新检索（其它工具全被拒），只能
                    # 反复重试同一个坏 id 直到耗尽整轮预算。
                    required_reader_artifact_ids.difference_update(
                        _reader_artifact_ids(resolved_arguments)
                    )
            if tool_call.name == "reader" and observation.succeeded:
                for read in _reader_results(observation):
                    start, end = read.get("char_start"), read.get("char_end")
                    if isinstance(start, int) and isinstance(end, int):
                        total_read_chars += max(0, end - start)
                    if (
                        self.config.max_total_read_chars is not None
                        and total_read_chars > self.config.max_total_read_chars
                    ):
                        detail = "reader cumulative character budget exhausted"
                        _append_error(log, detail)
                        raise ToolCallBudgetExhausted(detail, trace=tuple(log))
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

        detail = ("tool-call exploration limit reached" if tool_calls_used >= self.config.max_tool_calls
                  else "exploration turn budget exhausted")
        _append_error(log, detail)
        raise ToolCallBudgetExhausted(detail, trace=tuple(log))


def _reader_artifact_ids(arguments):
    reads = arguments.get("reads")
    rows = reads if isinstance(reads, list) else [arguments]
    return {row["artifact_id"] for row in rows
            if isinstance(row, dict) and isinstance(row.get("artifact_id"), str)}


def _reader_results(observation):
    if "read_results" in observation.payload:
        return observation.payload["read_results"]
    return [observation.payload.get("read_result", {})]


def _database_result_complete(observation):
    if not observation.succeeded:
        return False
    summary = observation.payload.get("execution_summary", {})
    if any(summary.get(key) for key in (
        "partial", "failed", "requires_human", "degraded", "all_failed", "no_execution"
    )):
        return False
    return all(row.get("status") == "succeeded"
               for row in observation.payload.get("search_executions", []))


def _build_tool_definitions(
    registry: Any,
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


def _database_artifact_ids(observation: ResearcherToolObservation) -> set[str]:
    result = observation.payload.get("database_search_result", {})
    return {
        artifact_id
        for item in result.get("results", [])
        for artifact_id in item.get("artifact_ids", [])
        if isinstance(artifact_id, str) and artifact_id
    }


def _append_error(log: list[ToolCallHarnessEvent], detail: str) -> None:
    log.append(ToolCallHarnessEvent(kind="error", detail=detail))
