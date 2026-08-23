"""单个 ResearchTask 的受预算约束 Researcher LangGraph 子工作流。"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from ..agents import NoveltyResearchAgent
from ..persistence import ReferenceStore
from ..schemas import (
    CallToolAction,
    Evidence,
    EvidenceCard,
    EvidenceCardDraft,
    EvidenceLocator,
    EvidenceSource,
    FinishResearchAction,
    ReferenceReadResult,
    ResearchBundle,
    ResearcherToolObservation,
    TaskResearchRequest,
    TaskResearchResult,
    TaskResearchStatus,
)
from ..tools import ResearcherToolRegistry


@dataclass(frozen=True)
class TaskResearcherConfig:
    max_steps: int = 12
    max_tool_calls: int = 10
    max_chars_per_read: int = 8_000
    max_total_read_chars: int = 48_000
    per_tool_limits: dict[str, int] = field(
        default_factory=lambda: {
            "structured_source_retrieval": 1,
            "reader": 8,
        }
    )

    def __post_init__(self) -> None:
        if min(
            self.max_steps,
            self.max_tool_calls,
            self.max_chars_per_read,
            self.max_total_read_chars,
        ) < 1:
            raise ValueError("researcher budgets must be positive")


class TaskResearchState(TypedDict, total=False):
    request: TaskResearchRequest
    tool_descriptions: list[dict[str, Any]]
    observations: list[dict[str, Any]]
    last_action: CallToolAction | FinishResearchAction
    research_bundles: list[ResearchBundle]
    read_results: list[ReferenceReadResult]
    warnings: list[str]
    steps_used: int
    tool_calls: int
    per_tool_calls: dict[str, int]
    call_history: list[str]
    total_read_chars: int
    force_partial: bool
    result: TaskResearchResult


class TaskResearcherWorkflow:
    def __init__(
        self,
        agent: NoveltyResearchAgent,
        tools: ResearcherToolRegistry,
        *,
        reference_store: ReferenceStore | None = None,
        config: TaskResearcherConfig | None = None,
    ) -> None:
        self.agent = agent
        self.tools = tools
        self.reference_store = reference_store or ReferenceStore()
        self.config = config or TaskResearcherConfig()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(TaskResearchState)
        builder.add_node("decide_action", self._decide_action)
        builder.add_node("execute_tool", self._execute_tool)
        builder.add_node("compile_result", self._compile_result)
        builder.add_node("stop_with_partial_result", self._stop_partial)
        builder.add_edge(START, "decide_action")
        builder.add_conditional_edges(
            "decide_action",
            self._route_action,
            {
                "tool": "execute_tool",
                "finish": "compile_result",
                "partial": "stop_with_partial_result",
            },
        )
        builder.add_edge("execute_tool", "decide_action")
        builder.add_edge("compile_result", END)
        builder.add_edge("stop_with_partial_result", END)
        return builder.compile()

    async def ainvoke(self, request: TaskResearchRequest) -> TaskResearchResult:
        request = TaskResearchRequest.model_validate(request)
        final = await self.graph.ainvoke(
            {
                "request": request,
                "tool_descriptions": self.tools.descriptions(),
                "observations": [],
                "research_bundles": [],
                "read_results": [],
                "warnings": [],
                "steps_used": 0,
                "tool_calls": 0,
                "per_tool_calls": {},
                "call_history": [],
                "total_read_chars": 0,
                "force_partial": False,
            }
        )
        return final["result"]

    async def _decide_action(self, state: TaskResearchState) -> dict[str, Any]:
        steps = state.get("steps_used", 0)
        if steps >= self.config.max_steps:
            return {
                "force_partial": True,
                "warnings": [*state.get("warnings", []), "research step budget exhausted"],
            }
        decision_state = dict(state)
        decision_state["remaining_budget"] = {
            "steps": self.config.max_steps - steps,
            "tool_calls": self.config.max_tool_calls - state.get("tool_calls", 0),
            "read_chars": self.config.max_total_read_chars
            - state.get("total_read_chars", 0),
        }
        try:
            action = await self.agent.decide(decision_state)
            return {"last_action": action, "steps_used": steps + 1}
        except Exception as exc:
            return {
                "force_partial": True,
                "steps_used": steps + 1,
                "warnings": [
                    *state.get("warnings", []),
                    f"researcher action failed: {_safe_error(exc)}",
                ],
            }

    async def _route_action(self, state: TaskResearchState) -> str:
        if state.get("force_partial"):
            return "partial"
        action = state.get("last_action")
        if isinstance(action, FinishResearchAction):
            return "finish"
        if isinstance(action, CallToolAction):
            if state.get("tool_calls", 0) >= self.config.max_tool_calls:
                return "partial"
            return "tool"
        return "partial"

    async def _execute_tool(self, state: TaskResearchState) -> dict[str, Any]:
        action = state["last_action"]
        assert isinstance(action, CallToolAction)
        arguments = dict(action.arguments)
        if action.tool_name == "reader":
            arguments["max_chars"] = min(
                int(arguments.get("max_chars", self.config.max_chars_per_read)),
                self.config.max_chars_per_read,
            )
        normalized = json.dumps(
            [action.tool_name, arguments], ensure_ascii=False, sort_keys=True
        )
        warnings = list(state.get("warnings", []))
        per_tool = dict(state.get("per_tool_calls", {}))
        limit = self.config.per_tool_limits.get(
            action.tool_name, self.config.max_tool_calls
        )
        if normalized in state.get("call_history", []):
            observation = _failed_observation(
                action.tool_name, arguments, "duplicate tool call rejected"
            )
        elif per_tool.get(action.tool_name, 0) >= limit:
            observation = _failed_observation(
                action.tool_name, arguments, "per-tool call budget exhausted"
            )
        else:
            observation = await self.tools.execute(
                action.tool_name,
                arguments,
                scope=state["request"],
            )
            per_tool[action.tool_name] = per_tool.get(action.tool_name, 0) + 1
        bundles = list(state.get("research_bundles", []))
        reads = list(state.get("read_results", []))
        total_read = state.get("total_read_chars", 0)
        if observation.succeeded and "bundle" in observation.payload:
            bundles.append(ResearchBundle.model_validate(observation.payload["bundle"]))
        if observation.succeeded and "read_result" in observation.payload:
            read = ReferenceReadResult.model_validate(
                observation.payload["read_result"]
            )
            if total_read + len(read.text) > self.config.max_total_read_chars:
                warnings.append("total read character budget exhausted")
            else:
                reads.append(read)
                total_read += len(read.text)
        if not observation.succeeded:
            warnings.append(observation.error or "tool call failed")
        return {
            "observations": [
                *state.get("observations", []),
                observation.model_dump(mode="json"),
            ],
            "research_bundles": bundles,
            "read_results": reads,
            "warnings": warnings,
            "tool_calls": state.get("tool_calls", 0) + 1,
            "per_tool_calls": per_tool,
            "call_history": [*state.get("call_history", []), normalized],
            "total_read_chars": total_read,
        }

    async def _compile_result(self, state: TaskResearchState) -> dict[str, Any]:
        action = state["last_action"]
        assert isinstance(action, FinishResearchAction)
        evidence, cards, warnings = compile_evidence_drafts(
            state["request"],
            action.cards,
            state.get("read_results", []),
            state.get("research_bundles", []),
            self.reference_store,
        )
        return {
            "result": TaskResearchResult(
                task_id=state["request"].research_task.task_id,
                novelty_point_id=state["request"].novelty_point.point_id,
                status=TaskResearchStatus.COMPLETED,
                research_bundles=state.get("research_bundles", []),
                read_results=state.get("read_results", []),
                evidence=evidence,
                evidence_cards=cards,
                warnings=[*state.get("warnings", []), *warnings],
                steps_used=state.get("steps_used", 0),
            )
        }

    async def _stop_partial(self, state: TaskResearchState) -> dict[str, Any]:
        return {
            "result": TaskResearchResult(
                task_id=state["request"].research_task.task_id,
                novelty_point_id=state["request"].novelty_point.point_id,
                status=TaskResearchStatus.PARTIAL,
                research_bundles=state.get("research_bundles", []),
                read_results=state.get("read_results", []),
                warnings=state.get("warnings", []),
                steps_used=state.get("steps_used", 0),
            )
        }


def compile_evidence_drafts(
    request: TaskResearchRequest,
    drafts: list[EvidenceCardDraft],
    reads: list[ReferenceReadResult],
    bundles: list[ResearchBundle],
    store: ReferenceStore,
) -> tuple[list[Evidence], list[EvidenceCard], list[str]]:
    read_by_id = {item.read_id: item for item in reads}
    manifest = store.load_manifest(request.subject_paper_id)
    artifacts = {item.artifact_id: item for item in manifest.artifacts}
    works = {item.work_id: item for item in manifest.works}
    records = {item.source_record_id: item for item in manifest.source_records}
    evidence: list[Evidence] = []
    cards: list[EvidenceCard] = []
    warnings: list[str] = []
    for draft in drafts:
        if draft.work_id not in works:
            warnings.append(f"draft references unknown work {draft.work_id}")
            continue
        card_evidence: list[Evidence] = []
        sources: list[EvidenceSource] = []
        for quote in draft.quotes:
            read = read_by_id.get(quote.read_id)
            if read is None or read.work_id != draft.work_id:
                warnings.append(f"draft work {draft.work_id} references unknown read {quote.read_id}")
                continue
            local_start = read.text.find(quote.quote)
            if local_start < 0:
                warnings.append(f"quote from read {quote.read_id} is not an exact substring")
                continue
            artifact = artifacts.get(read.artifact_id)
            if artifact is None or artifact.work_id != draft.work_id:
                warnings.append(f"read {quote.read_id} artifact binding is invalid")
                continue
            start = read.char_start + local_start
            end = start + len(quote.quote)
            evidence_id = _stable_id(
                "evd",
                request.research_task.task_id,
                artifact.artifact_id,
                str(start),
                str(end),
                quote.quote,
            )
            item = Evidence(
                evidence_id=evidence_id,
                work_id=draft.work_id,
                artifact_id=artifact.artifact_id,
                novelty_point_id=request.novelty_point.point_id,
                task_id=request.research_task.task_id,
                quote=quote.quote,
                locator=EvidenceLocator(char_start=start, char_end=end),
                interpretation=quote.interpretation,
                confidence=quote.confidence,
                provenance={"read_id": read.read_id},
            )
            card_evidence.append(item)
            record = records.get(artifact.source_record_id or "")
            work = works[draft.work_id]
            sources.append(
                EvidenceSource(
                    title=work.title,
                    quote=quote.quote,
                    location=f"artifact:{artifact.artifact_id} chars:{start}-{end}",
                    doi=_identifier(work, "doi"),
                    url=record.landing_url if record is not None else None,
                )
            )
        if not card_evidence:
            warnings.append(f"draft work {draft.work_id} has no valid quote")
            continue
        card_id = _stable_id(
            "card",
            request.novelty_point.point_id,
            request.research_task.task_id,
            draft.work_id,
            *sorted(item.evidence_id for item in card_evidence),
        )
        cards.append(
            EvidenceCard(
                card_id=card_id,
                task_id=request.research_task.task_id,
                novelty_point_id=request.novelty_point.point_id,
                document_title=works[draft.work_id].title,
                main_contribution=draft.main_contribution,
                overlaps=draft.overlaps,
                differences=draft.differences,
                sources=sources,
                possible_baseline=draft.possible_baseline,
                relevance=draft.relevance,
                confidence=draft.confidence,
                evidence_ids=[item.evidence_id for item in card_evidence],
            )
        )
        evidence.extend(card_evidence)
    return evidence, cards, warnings


def _identifier(work, namespace: str) -> str | None:
    return next(
        (item.value for item in work.identifiers if item.namespace == namespace), None
    )


def _stable_id(prefix: str, *parts: str) -> str:
    return f"{prefix}_{hashlib.sha256(chr(31).join(parts).encode()).hexdigest()[:24]}"


def _failed_observation(
    tool_name: str, arguments: dict[str, Any], error: str
) -> ResearcherToolObservation:
    return ResearcherToolObservation(
        tool_name=tool_name,
        arguments=arguments,
        succeeded=False,
        error=error,
    )


def _safe_error(exc: Exception) -> str:
    text = str(exc)
    for marker in ("Authorization", "api_key", "cookie"):
        if marker.casefold() in text.casefold():
            return f"{type(exc).__name__}: sensitive error redacted"
    return f"{type(exc).__name__}: {text}"[:1000]
