import asyncio
import hashlib
from datetime import datetime, timezone

from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.schemas import (
    AccessStatus,
    Artifact,
    ArtifactRole,
    CallToolAction,
    ContentExtent,
    EvidenceCardDraft,
    EvidenceQuoteDraft,
    FinishResearchAction,
    NoveltyPoint,
    ReferenceManifest,
    ReferenceReaderToolArguments,
    ResearcherToolObservation,
    ResearchTask,
    SourceKind,
    SourceRecord,
    StrictModel,
    StructuredRetrievalToolArguments,
    TaskResearchRequest,
    Work,
)
from novelty_agent_framework.tools import (
    ReferenceArtifactReaderTool,
    ReaderTool,
    ResearcherToolRegistry,
)
from novelty_agent_framework.workflows import TaskResearcherConfig, TaskResearcherWorkflow

NOW = datetime(2026, 8, 18, tzinfo=timezone.utc)
TEXT = "prefix Exact grounded quote. suffix"


def scope() -> TaskResearchRequest:
    point = NoveltyPoint(
        point_id="NP-1", claim="一种方法", technical_features=["特征"]
    )
    task = ResearchTask(
        task_id="T-1", novelty_point_id="NP-1",
        task_type="search", language="en",
    )
    return TaskResearchRequest(
        subject_paper_id="paper-1", run_id="run-1",
        novelty_point=point, research_task=task,
    )


def prepare_store(tmp_path):
    store = ReferenceStore(tmp_path)
    work = Work(
        work_id="wrk_1", work_type="article", title="Grounded Paper",
        identifiers=[{"namespace": "doi", "value": "10.1/test"}],
    )
    record = SourceRecord(
        source_record_id="src_1", work_id="wrk_1", source_id="test",
        source_kind=SourceKind.STRUCTURED_DATABASE, title=work.title,
        landing_url="https://example.test/paper",
        access_status=AccessStatus.FULL_TEXT_ACQUIRED, observed_at=NOW,
    )
    digest = hashlib.sha256(TEXT.encode()).hexdigest()
    store.write_document(
        "paper-1", work_id="wrk_1", artifact_id="art_1",
        extension="txt", content=TEXT,
    )
    artifact = Artifact(
        artifact_id="art_1", work_id="wrk_1", source_record_id="src_1",
        role=ArtifactRole.EXTRACTED_TEXT, media_type="text/plain",
        relative_path="documents/wrk_1/art_1.txt", sha256=digest,
        content_extent=ContentExtent.UNKNOWN, acquired_at=NOW,
    )
    store.persist_manifest(
        "paper-1",
        ReferenceManifest(
            subject_paper_id="paper-1", updated_at=NOW,
            works=[work], source_records=[record], artifacts=[artifact],
        ),
    )
    return store


class FakeAgent:
    def __init__(self, actions):
        self.actions = list(actions)
        self.states = []

    async def decide(self, state):
        self.states.append(state)
        return self.actions.pop(0)


class FakeRetrievalTool:
    name = "structured_source_retrieval"
    description = "fake retrieval"
    args_schema = StructuredRetrievalToolArguments

    def __init__(self):
        self.scopes = []

    async def ainvoke(self, arguments, *, scope):
        self.scopes.append(scope)
        return ResearcherToolObservation(
            tool_name=self.name,
            arguments=arguments.model_dump(mode="json"),
            succeeded=True,
            summary="retrieved",
            payload={
                "bundle": {
                    "bundle_id": "bnd_1",
                    "producer": "fake",
                    "search_executions": [],
                    "works": [],
                    "source_records": [],
                    "artifacts": [],
                    "evidence": [],
                    "warnings": [],
                }
            },
        )


def finish_action(quote="Exact grounded quote."):
    return FinishResearchAction(
        action="finish",
        cards=[
            EvidenceCardDraft(
                work_id="wrk_1", main_contribution="贡献",
                overlaps=["重合"], differences=["差异"],
                quotes=[
                    EvidenceQuoteDraft(
                        read_id="PLACEHOLDER", quote=quote,
                        interpretation="支持当前比较", confidence=0.9,
                    )
                ],
                relevance=0.9, confidence=0.9,
            )
        ],
    )


def test_complete_tool_read_finish_loop_and_scope_injection(tmp_path):
    store = prepare_store(tmp_path)
    retrieval = FakeRetrievalTool()
    reader = ReaderTool(ReferenceArtifactReaderTool(store))
    registry = ResearcherToolRegistry([retrieval, reader])
    finish = finish_action()
    agent = FakeAgent(
        [
            CallToolAction(
                action="call_tool", tool_name="structured_source_retrieval",
                arguments={"source_id": "test"},
            ),
            CallToolAction(
                action="call_tool", tool_name="reader",
                arguments={"artifact_id": "art_1", "char_start": 0, "max_chars": 100},
            ),
            finish,
        ]
    )

    # read_id is stable and can be known before the model's finish response.
    read = store.read_document_slice(
        "paper-1", artifact_id="art_1", char_start=0, max_chars=100
    )
    finish.cards[0].quotes[0].read_id = read.read_id
    result = asyncio.run(
        TaskResearcherWorkflow(agent, registry, reference_store=store).ainvoke(scope())
    )

    assert result.status.value == "completed"
    assert result.steps_used == 3
    assert len(result.research_bundles) == 1
    assert len(result.read_results) == 1
    assert len(result.evidence) == len(result.evidence_cards) == 1
    evidence = result.evidence[0]
    assert TEXT[evidence.locator.char_start:evidence.locator.char_end] == evidence.quote
    assert result.evidence_cards[0].evidence_ids == [evidence.evidence_id]
    assert retrieval.scopes == [scope()]
    assert all(state["request"].research_task.task_id == "T-1" for state in agent.states)


def test_bad_quote_is_dropped_without_losing_task_result(tmp_path):
    store = prepare_store(tmp_path)
    read = store.read_document_slice(
        "paper-1", artifact_id="art_1", char_start=0, max_chars=100
    )
    finish = finish_action("not in slice")
    finish.cards[0].quotes[0].read_id = read.read_id
    agent = FakeAgent([finish])
    workflow = TaskResearcherWorkflow(
        agent, ResearcherToolRegistry(), reference_store=store
    )
    # Inject the read as prior state through the compiler-facing graph node behavior.
    evidence, cards, warnings = __import__(
        "novelty_agent_framework.workflows.research_task",
        fromlist=["compile_evidence_drafts"],
    ).compile_evidence_drafts(scope(), finish.cards, [read], [], store)
    assert evidence == cards == []
    assert any("exact substring" in warning for warning in warnings)


def test_duplicate_calls_and_budget_terminate_partial(tmp_path):
    store = prepare_store(tmp_path)
    action = CallToolAction(
        action="call_tool", tool_name="reader",
        arguments={"artifact_id": "art_1", "char_start": 0, "max_chars": 10},
    )
    agent = FakeAgent([action, action, action, action])
    workflow = TaskResearcherWorkflow(
        agent,
        ResearcherToolRegistry(
            [ReaderTool(ReferenceArtifactReaderTool(store))]
        ),
        reference_store=store,
        config=TaskResearcherConfig(max_steps=3, max_tool_calls=3),
    )
    result = asyncio.run(workflow.ainvoke(scope()))
    assert result.status.value == "partial"
    assert result.steps_used <= 3
    assert any("duplicate" in warning for warning in result.warnings)


def test_registry_rejects_unknown_or_invalid_arguments_and_is_extensible(tmp_path):
    registry = ResearcherToolRegistry()
    unknown = asyncio.run(registry.execute("missing", {}, scope=scope()))
    assert not unknown.succeeded and "unregistered" in unknown.error

    reader = ReaderTool(
        ReferenceArtifactReaderTool(prepare_store(tmp_path))
    )
    registry.register(reader)
    invalid = asyncio.run(
        registry.execute(
            reader.name,
            {"artifact_id": "art_1", "unexpected": True},
            scope=scope(),
        )
    )
    assert not invalid.succeeded

    class PingArgs(StrictModel):
        value: str

    class PingTool:
        name = "ping"
        description = "generic extension"
        args_schema = PingArgs

        async def ainvoke(self, arguments, *, scope):
            return ResearcherToolObservation(
                tool_name=self.name, arguments={"value": arguments.value},
                succeeded=True, payload={"pong": arguments.value},
            )

    registry.register(PingTool())
    pong = asyncio.run(registry.execute("ping", {"value": "ok"}, scope=scope()))
    assert pong.succeeded and pong.payload == {"pong": "ok"}
