"""Native tool-calling workflow for one formal ResearchTask."""

from __future__ import annotations

import json
import re
from pathlib import Path
from dataclasses import dataclass, field, replace

from backend.env import ChatMessage, ModelCallOptions, ModelClient, PromptLibrary
from pydantic import ValidationError

from ..core.format_repair import repair_json
from ..core import ToolCallHarness, ToolCallHarnessConfig, ToolCallHarnessError
from ..schemas import (
    ReferenceReadResult,
    SearchPlan,
    ResearchBundle,
    ResearchFinishDraft,
    TaskResearchRequest,
)
from ..schemas import TaskResearchResult, TaskResearchStatus
from ..schemas.references import SearchExecution
from ..tools import EvidenceCardBuilder, ResearcherToolRegistry
from .candidate_audit import build_candidate_audit


def _extract_finish_json(content: str | None) -> str:
    """从模型收尾文本中稳健提取 ResearchFinishDraft JSON 片段。

    DeepSeek-V4-Flash 等模型常把收尾 JSON 包在 ```json ... ``` 代码块里或
    夹带叙述文字；pydantic 的 model_validate_json 要求纯 JSON，这里先剥离
    Markdown 围栏，再截取首个 '{' 到末尾 '}' 之间的内容。
    """

    text = (content or "").strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        text = text[start : end + 1]
    return text


@dataclass(frozen=True)
class TaskResearcherConfig:
    """Formal harness budgets plus temporarily retained legacy settings."""

    max_steps: int = 12
    max_tool_calls: int = 10
    max_chars_per_read: int = 8_000
    max_total_read_chars: int = 48_000
    per_tool_limits: dict[str, int] = field(
        default_factory=lambda: {
            "database_search": 2,
            "web_search": 3,
            "browser": 3,
            "reader": 8,
        }
    )
    model_options: ModelCallOptions = field(
        default_factory=lambda: ModelCallOptions(temperature=0.0, tool_choice="auto")
    )
    prompt_name: str = "research/native_tool_loop"

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
                finalize_on_budget=True,
                reuse_database_results=True,
                max_turns=self.config.max_steps,
                max_tool_calls=self.config.max_tool_calls,
                per_tool_limits=dict(self.config.per_tool_limits),
                max_total_read_chars=self.config.max_total_read_chars,
            ),
        )

    async def ainvoke(self, request: TaskResearchRequest) -> TaskResearchResult:
        result, trace = await self._research(request)
        return result.model_copy(update={"search_executions": _search_audit(trace), "candidate_audit": build_candidate_audit(
            trace, result.read_results, result.evidence, result.evidence_cards,
            interrupted=result.status == TaskResearchStatus.PARTIAL,
        )})

    async def _research(self, request: TaskResearchRequest):
        request = TaskResearchRequest.model_validate(request)
        system_prompt, user_message = self._render_prompt(request)
        try:
            harness_result = await self.harness.run(
                system_prompt=system_prompt,
                initial_user_message=user_message,
                scope=request,
                options=self.config.model_options,
            )
        except ToolCallHarnessError as exc:
            reads, read_warnings = _trusted_reads(exc.trace)
            bundles, bundle_warnings = _trusted_bundles(exc.trace)
            return _partial(
                request,
                reads=reads,
                bundles=bundles,
                warnings=[
                    f"native tool harness failed: {exc}",
                    *read_warnings,
                    *bundle_warnings,
                ],
                steps=_turns_in_trace(exc.trace),
            ), exc.trace
        except Exception as exc:
            return _partial(
                request,
                warnings=[f"native tool harness failed: {_safe_error(exc)}"],
            ), ()

        reads, read_warnings = _trusted_reads(harness_result.trace)
        bundles, bundle_warnings = _trusted_bundles(harness_result.trace)
        format_turns = 0
        format_warnings = []
        try:
            try:
                draft, format_warnings = _parse_finish(harness_result.final_content)
            except (ValidationError, ValueError):
                format_turns = 1
                repaired = await repair_json(self.model_client, harness_result.final_content,
                                             ResearchFinishDraft.model_json_schema(), self.config.model_options)
                draft, format_warnings = _parse_finish(repaired)
                format_warnings.append("single format repair recovered ResearchFinishDraft")
        except Exception as exc:
            return _partial(
                request, reads=reads, bundles=bundles,
                warnings=[*read_warnings, *bundle_warnings,
                          f"invalid ResearchFinishDraft after bounded recovery: {_safe_error(exc)}"],
                steps=harness_result.turns_used + format_turns,
            ), harness_result.trace

        try:
            built = self.evidence_builder.build(
                draft, scope=request, read_results=reads
            )
        except Exception as exc:
            return _partial(
                request,
                reads=reads,
                bundles=bundles,
                warnings=[*read_warnings, *bundle_warnings,
                          f"evidence builder failed: {_safe_error(exc)}"],
                steps=harness_result.turns_used + format_turns,
            ), harness_result.trace

        correction_turns = 0
        repairable = [item for item in built.rejections
                      if item.reason != "web supplementary material cannot be used as evidence"]
        if repairable:
            correction_turns = 1
            built = await self._correct_rejected_cards(
                draft, built.model_copy(update={"rejections": repairable}), reads, request,
            )
        stop_warnings = ([f"research stopped; finalization completed: {harness_result.stop_reason}"]
                         if harness_result.stop_reason else [])
        return TaskResearchResult(
            task_id=request.research_task.task_id,
            novelty_point_id=request.novelty_point.point_id,
            status=(TaskResearchStatus.PARTIAL if harness_result.stop_reason else TaskResearchStatus.COMPLETED),
            read_results=reads,
            research_bundles=bundles,
            evidence=built.evidence,
            evidence_cards=built.evidence_cards,
            warnings=[*stop_warnings, *read_warnings, *bundle_warnings, *format_warnings, *built.warnings],
            steps_used=harness_result.turns_used + format_turns + correction_turns,
        ), harness_result.trace

    async def _correct_rejected_cards(self, draft, built, reads, request):
        payload = {
            "novelty_point": _project_novelty_point(request.novelty_point),
            "rejected_cards": [
                {"card": draft.cards[item.card_index].model_dump(mode="json"), "error": item.reason}
                for item in built.rejections
            ],
            "reader_texts": [read.text for read in reads],
            "finish_schema": ResearchFinishDraft.model_json_schema(),
        }
        try:
            response = await self.model_client.acomplete([
                ChatMessage(role="system", content=(
                    "Correct only the rejected evidence drafts. No tools are available. "
                    "Copy quotes verbatim from reader_texts, preserving LaTeX and punctuation. "
                    "Do not invent provenance IDs. Return ResearchFinishDraft JSON, or "
                    "cards=[] and a no_evidence_reason if the drafts cannot be grounded."
                )),
                ChatMessage(role="user", content=json.dumps(payload, ensure_ascii=False)),
            ], options=replace(self.config.model_options, tools=(), tool_choice="none"))
            if response.tool_calls:
                raise ValueError("quote correction attempted a tool call")
            corrected = ResearchFinishDraft.model_validate_json(_extract_finish_json(response.content))
            if len(corrected.cards) > len(built.rejections):
                raise ValueError("correction returned more cards than rejected drafts")
            repaired = self.evidence_builder.build(corrected, scope=request, read_results=reads)
            existing = {card.card_id for card in built.evidence_cards}
            new_cards = [card for card in repaired.evidence_cards if card.card_id not in existing]
            needed_ids = {eid for card in new_cards for eid in card.evidence_ids}
            evidence_by_id = {item.evidence_id: item for item in built.evidence}
            evidence_by_id.update({item.evidence_id: item for item in repaired.evidence if item.evidence_id in needed_ids})
            return built.model_copy(update={
                "evidence": list(evidence_by_id.values()),
                "evidence_cards": [*built.evidence_cards, *new_cards],
                "warnings": [*built.warnings, *repaired.warnings,
                             f"single quote correction recovered {len(new_cards)} card(s)"],
            })
        except Exception as exc:
            return built.model_copy(update={"warnings": [
                *built.warnings, f"single quote correction failed: {_safe_error(exc)}",
            ]})

    def _render_prompt(self, request: TaskResearchRequest) -> tuple[str, str]:
        variables = {
            "novelty_point_json": json.dumps(
                _project_novelty_point(request.novelty_point), ensure_ascii=False
            ),
            "research_task_json": json.dumps(
                request.research_task.model_dump(mode="json"), ensure_ascii=False
            ),
            "search_plan_json": json.dumps(
                _project_search_plan(request.search_plan), ensure_ascii=False
            ),
            "finish_schema_json": json.dumps(
                ResearchFinishDraft.model_json_schema(), ensure_ascii=False
            ),
        }
        if self.prompts is not None:
            rendered = self.prompts.render(self.config.prompt_name, **variables)
            return rendered.system + self._research_skills(), rendered.user + "\n\n" + self._capability_note()
        return (
            "Use only registered tools. Finish with strict ResearchFinishDraft JSON. "
            "Never invent provenance handles." + self._research_skills(),
            "\n".join(f"{key}: {value}" for key, value in variables.items()) + "\n" + self._capability_note(),
        )

    @staticmethod
    def _research_skills() -> str:
        root = Path(__file__).resolve().parents[1] / "skills"
        return "\n\n" + "\n\n".join(
            (root / name / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[-1].strip()
            for name in ("database_research", "web_supplement")
        )

    def _capability_note(self):
        names = self.tools.names
        note = "Available tools: " + ", ".join(names) + ". "
        if "browser" not in names:
            note += (
                "browser is unavailable. Web search is discovery only: do not attempt "
                "browser or pass a source_record_id to reader. Read only actual artifact IDs "
                "from available tools; prefer database/reference artifacts. Do not repeat "
                "web searches when there is no acquisition path. Finish with available evidence "
                "or explain the acquisition limitation."
            )
        return note


def _parse_finish(content):
    payload = json.loads(_extract_finish_json(content))
    warnings = []
    if isinstance(payload, dict) and isinstance(payload.get("cards"), list) and payload["cards"]:
        if payload.get("no_evidence_reason") is not None:
            warnings.append("moved conflicting no_evidence_reason to warnings: " + str(payload["no_evidence_reason"]))
            payload = {**payload, "no_evidence_reason": None}
    return ResearchFinishDraft.model_validate(payload), warnings


def _trusted_reads(trace) -> tuple[list[ReferenceReadResult], list[str]]:
    reads: list[ReferenceReadResult] = []
    warnings: list[str] = []
    for event in trace:
        observation = event.observation
        if (event.kind != "tool_result" or observation is None
                or observation.tool_name != "reader" or not observation.succeeded):
            continue
        rows = observation.payload.get("read_results", [observation.payload.get("read_result")])
        for row in rows:
            try:
                reads.append(ReferenceReadResult.model_validate(row))
            except (ValidationError, ValueError, TypeError) as exc:
                warnings.append(f"ignored malformed reader observation: {_safe_error(exc)}")
    return reads, warnings


def _search_audit(trace) -> list[SearchExecution]:
    executions = {}
    for event in trace:
        observation = event.observation
        if event.kind != "tool_result" or observation is None:
            continue
        if observation.tool_name not in {"database_search", "structured_source_retrieval"}:
            continue
        payload = observation.payload
        bundle = payload.get("research_bundle") or payload.get("bundle") or {}
        rows = payload.get("search_executions", [])
        rows = rows if isinstance(rows, list) else []
        if isinstance(bundle, dict):
            nested = bundle.get("search_executions", [])
            rows = [*rows, *(nested if isinstance(nested, list) else [])]
        for row in rows:
            try:
                execution = SearchExecution.model_validate(row)
                executions[(execution.execution_id, execution.started_at)] = execution
            except (ValidationError, ValueError, TypeError):
                continue  # Malformed audit metadata must never discard evidence.
    return list(executions.values())


def _trusted_bundles(trace) -> tuple[list[ResearchBundle], list[str]]:
    bundles: list[ResearchBundle] = []
    warnings: list[str] = []
    for event in trace:
        observation = event.observation
        if event.kind != "tool_result" or observation is None or not observation.succeeded:
            continue
        payload = observation.payload.get("research_bundle")
        if payload is None and observation.tool_name == "structured_source_retrieval":
            payload = observation.payload.get("bundle")
        if payload is None:
            continue
        try:
            bundles.append(ResearchBundle.model_validate(payload))
        except (ValidationError, ValueError, TypeError) as exc:
            warnings.append(f"ignored malformed research bundle: {_safe_error(exc)}")
    return bundles, warnings


def _turns_in_trace(trace) -> int:
    return sum(event.kind == "assistant_response" for event in trace)


def _partial(
    request, *, reads=None, bundles=None, warnings=None, steps=0
) -> TaskResearchResult:
    return TaskResearchResult(
        task_id=request.research_task.task_id,
        novelty_point_id=request.novelty_point.point_id,
        status=TaskResearchStatus.PARTIAL,
        read_results=reads or [],
        research_bundles=bundles or [],
        warnings=warnings or [],
        steps_used=steps,
    )


def _safe_error(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"[:500]

def _project_novelty_point(point: Any) -> dict:
    """模型上下文投影：剔除 ``source_locations``。

    ``source_locations`` 是 PointExtractor 生成的、给人看的定位提示，**不保证
    逐字**——它会顺手清理 PDF 抽取残留（例如把 ``(model F _ { 2 } ) ) )`` 去掉）。
    但字符串本身带引号、还标着章节，模型会把它当成现成的引文直接写进 finish
    draft，随后必然被 EvidenceCardBuilder 判为 ungrounded，白白作废整轮检索。
    引文只应来自成功的 Reader 观测，因此这里不把它暴露给模型。
    """

    payload = point.model_dump(mode="json")
    payload.pop("source_locations", None)
    return payload


def _project_search_plan(plan: SearchPlan) -> dict:
    """模型上下文投影：只给最小语义（terms + expression），不给 ID/level/name/description/绑定。

    完整运行时 SearchPlan 只流向机器与审计；Researcher 提示词每轮工具循环
    都携带本投影，体积约省 30-40%。
    """

    return {
        "concepts": [
            {
                "terms": list(concept.terms),
                "role": concept.role,
                "alias": list(concept.alias),
            }
            for concept in plan.concepts
        ],
        "strategies": [
            {"expression": strategy.expression} for strategy in plan.strategies
        ],
    }
