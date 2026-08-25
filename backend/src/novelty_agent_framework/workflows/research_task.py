"""Native tool-calling workflow for one formal ResearchTask."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from backend.env import ModelCallOptions, ModelClient, PromptLibrary
from pydantic import ValidationError

from ..core import ToolCallHarness, ToolCallHarnessConfig, ToolCallHarnessError
from ..schemas import ReferenceReadResult, ResearchFinishDraft, TaskResearchRequest
from ..schemas import TaskResearchResult, TaskResearchStatus
from ..tools import EvidenceCardBuilder, ResearcherToolRegistry


@dataclass(frozen=True)
class TaskResearcherConfig:
    """Formal harness budgets plus temporarily retained legacy settings."""

    max_steps: int = 12
    max_tool_calls: int = 10
    max_chars_per_read: int = 8_000
    max_total_read_chars: int = 48_000
    per_tool_limits: dict[str, int] = field(
        default_factory=lambda: {"web_search": 3, "browser": 3, "reader": 8}
    )

    def __post_init__(self) -> None:
        if min(self.max_steps, self.max_tool_calls, self.max_chars_per_read,
               self.max_total_read_chars) < 1:
            raise ValueError("researcher budgets must be positive")


class TaskResearcherWorkflow:
    """Drive a model through native tools, then compile trusted observations."""

    def __init__(
        self,
        model_client: ModelClient,
        tool_registry: ResearcherToolRegistry,
        evidence_builder: EvidenceCardBuilder,
        *,
        prompts: PromptLibrary | None = None,
        config: TaskResearcherConfig | None = None,
    ) -> None:
        self.model_client = model_client
        self.tools = tool_registry
        self.evidence_builder = evidence_builder
        self.prompts = prompts
        self.config = config or TaskResearcherConfig()
        self.harness = ToolCallHarness(
            model_client,
            tool_registry,
            config=ToolCallHarnessConfig(
                max_turns=self.config.max_steps,
                max_tool_calls=self.config.max_tool_calls,
            ),
        )

    async def ainvoke(self, request: TaskResearchRequest) -> TaskResearchResult:
        request = TaskResearchRequest.model_validate(request)
        system_prompt, user_message = self._render_prompt(request)
        try:
            harness_result = await self.harness.run(
                system_prompt=system_prompt,
                initial_user_message=user_message,
                scope=request,
                options=ModelCallOptions(temperature=0.0, tool_choice="auto"),
            )
        except ToolCallHarnessError as exc:
            reads, read_warnings = _trusted_reads(exc.trace)
            return _partial(
                request,
                reads=reads,
                warnings=[f"native tool harness failed: {exc}", *read_warnings],
                steps=_turns_in_trace(exc.trace),
            )
        except Exception as exc:
            return _partial(
                request,
                warnings=[f"native tool harness failed: {_safe_error(exc)}"],
            )

        reads, read_warnings = _trusted_reads(harness_result.trace)
        try:
            draft = ResearchFinishDraft.model_validate_json(
                harness_result.final_content or ""
            )
        except (ValidationError, ValueError) as exc:
            return _partial(
                request,
                reads=reads,
                warnings=[*read_warnings,
                          f"invalid ResearchFinishDraft: {_safe_error(exc)}"],
                steps=harness_result.turns_used,
            )

        try:
            built = self.evidence_builder.build(
                draft, scope=request, read_results=reads
            )
        except Exception as exc:
            return _partial(
                request,
                reads=reads,
                warnings=[*read_warnings,
                          f"evidence builder failed: {_safe_error(exc)}"],
                steps=harness_result.turns_used,
            )

        return TaskResearchResult(
            task_id=request.research_task.task_id,
            novelty_point_id=request.novelty_point.point_id,
            status=TaskResearchStatus.COMPLETED,
            read_results=reads,
            evidence=built.evidence,
            evidence_cards=built.evidence_cards,
            warnings=[*read_warnings, *built.warnings],
            steps_used=harness_result.turns_used,
        )

    def _render_prompt(self, request: TaskResearchRequest) -> tuple[str, str]:
        variables = {
            "novelty_point_json": json.dumps(
                request.novelty_point.model_dump(mode="json"), ensure_ascii=False
            ),
            "research_task_json": json.dumps(
                request.research_task.model_dump(mode="json"), ensure_ascii=False
            ),
            "finish_schema_json": json.dumps(
                ResearchFinishDraft.model_json_schema(), ensure_ascii=False
            ),
        }
        if self.prompts is not None:
            rendered = self.prompts.render("research/native_tool_loop", **variables)
            return rendered.system, rendered.user
        return (
            "Use only registered tools. Finish with strict ResearchFinishDraft JSON. "
            "Never invent provenance handles.",
            "\n".join(f"{key}: {value}" for key, value in variables.items()),
        )


def _trusted_reads(trace) -> tuple[list[ReferenceReadResult], list[str]]:
    reads: list[ReferenceReadResult] = []
    warnings: list[str] = []
    for event in trace:
        observation = event.observation
        if (event.kind != "tool_result" or observation is None
                or observation.tool_name != "reader" or not observation.succeeded):
            continue
        try:
            reads.append(ReferenceReadResult.model_validate(
                observation.payload.get("read_result")
            ))
        except (ValidationError, ValueError, TypeError) as exc:
            warnings.append(f"ignored malformed reader observation: {_safe_error(exc)}")
    return reads, warnings


def _turns_in_trace(trace) -> int:
    return sum(event.kind == "assistant_response" for event in trace)


def _partial(request, *, reads=None, warnings=None, steps=0) -> TaskResearchResult:
    return TaskResearchResult(
        task_id=request.research_task.task_id,
        novelty_point_id=request.novelty_point.point_id,
        status=TaskResearchStatus.PARTIAL,
        read_results=reads or [],
        warnings=warnings or [],
        steps_used=steps,
    )


def _safe_error(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"[:500]
