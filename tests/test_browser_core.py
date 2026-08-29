"""Deterministic Browser core and trusted handle-flow tests."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.schemas import (
    AccessStatus,
    BrowserArguments,
    NoveltyPoint,
    ResearchTask,
    SourceKind,
    SourceRecord,
    TaskResearchRequest,
    Work,
    WorkType,
)
from novelty_agent_framework.tools import (
    BrowserFetchResult,
    BrowserTool,
    ResearcherToolRegistry,
)
from conftest import minimal_search_plan


class StubBrowserBackend:
    name = "stub-browser"

    def __init__(self, *, text: str = "Rendered body", fail: bool = False) -> None:
        self.text = text
        self.fail = fail
        self.calls: list[str] = []

    async def fetch(self, url: str) -> BrowserFetchResult:
        self.calls.append(url)
        if self.fail:
            raise RuntimeError("browser unavailable")
        return BrowserFetchResult(
            requested_url=url,
            final_url=url + "?rendered=1",
            title="Rendered title",
            html=f"<body>{self.text}</body>",
            text=self.text,
            content_type="text/html",
            warnings=["stub warning"],
            metadata={"engine": "stub"},
        )


def scope() -> TaskResearchRequest:
    return TaskResearchRequest(
        subject_paper_id="paper-1",
        run_id="run-browser",
        novelty_point=NoveltyPoint(
            point_id="NP-1", claim="claim", technical_features=["feature"]
        ),
        research_task=ResearchTask(
            task_id="TASK-1",
            novelty_point_id="NP-1",
            task_type="browse",
            language="en",
        ),
        search_plan=minimal_search_plan("TASK-1", "NP-1"),
    )


def seed(store: ReferenceStore, **updates) -> SourceRecord:
    values = {
        "source_record_id": "src_known",
        "source_id": "search",
        "source_kind": SourceKind.WEB,
        "title": "Candidate",
        "landing_url": "https://landing.example/page",
        "full_text_url": "https://full.example/page",
        "access_status": AccessStatus.DISCOVERED,
        "observed_at": datetime.now(timezone.utc),
    }
    values.update(updates)
    record = SourceRecord(**values)
    manifest = store.load_manifest("paper-1")
    works = []
    if record.work_id:
        works.append(
            Work(
                work_id=record.work_id,
                work_type=WorkType.WEBPAGE,
                title="Existing work",
                canonical_source_record_id=record.source_record_id,
            )
        )
    store.persist_manifest(
        "paper-1",
        manifest.model_copy(update={"source_records": [record], "works": works}),
    )
    return record


def execute(registry, arguments):
    return asyncio.run(registry.execute("browser", arguments, scope=scope()))


def test_schema_and_tool_definition_expose_only_handle(tmp_path) -> None:
    store = ReferenceStore(tmp_path)
    backend = StubBrowserBackend()
    registry = ResearcherToolRegistry([BrowserTool(backend, store)])

    assert BrowserArguments.model_fields.keys() == {"source_record_id"}
    schema = registry.descriptions()[0]["arguments_schema"]
    assert schema["properties"].keys() == {"source_record_id"}
    assert "url" not in str(schema).lower()


def test_trusted_url_resolution_persistence_and_idempotence(tmp_path) -> None:
    store = ReferenceStore(tmp_path)
    seed(store)
    backend = StubBrowserBackend(text="A stable rendered page.")
    registry = ResearcherToolRegistry([BrowserTool(backend, store)])

    first = execute(registry, {"source_record_id": "src_known"})
    second = execute(registry, {"source_record_id": "src_known"})

    assert first.succeeded and second.succeeded
    assert backend.calls == ["https://full.example/page"] * 2
    result = first.payload["browser_result"]
    assert set(result) == {"source_record_id", "work_id", "artifacts", "warnings"}
    assert "A stable rendered page." not in str(result)
    assert first.payload["browser_fetch"]["text"] == "A stable rendered page."
    projection = registry.project_model_context("browser", first)
    assert "browser_fetch" not in projection
    assert "A stable rendered page." not in str(projection)
    assert result["work_id"].startswith("wrk_")
    assert result["artifacts"] == second.payload["browser_result"]["artifacts"]
    manifest = store.load_manifest("paper-1")
    assert len(manifest.works) == 1
    assert len(manifest.artifacts) == 1
    assert manifest.source_records[0].work_id == result["work_id"]
    assert manifest.source_records[0].access_status is AccessStatus.FULL_TEXT_ACQUIRED
    artifact = manifest.artifacts[0]
    assert artifact.artifact_id == result["artifacts"][0]["artifact_id"]
    read = store.read_document_slice(
        "paper-1", artifact_id=artifact.artifact_id, char_start=0, max_chars=100
    )
    assert read.text == "A stable rendered page."


def test_landing_fallback_and_existing_work_are_reused(tmp_path) -> None:
    store = ReferenceStore(tmp_path)
    seed(store, full_text_url=None, work_id="wrk_existing")
    backend = StubBrowserBackend()
    observation = execute(
        ResearcherToolRegistry([BrowserTool(backend, store)]),
        {"source_record_id": "src_known"},
    )

    assert observation.succeeded
    assert backend.calls == ["https://landing.example/page"]
    assert observation.payload["browser_result"]["work_id"] == "wrk_existing"
    assert len(store.load_manifest("paper-1").works) == 1


def test_unknown_missing_url_injection_and_backend_failure(tmp_path) -> None:
    store = ReferenceStore(tmp_path)
    seed(store, landing_url=None, full_text_url=None)
    backend = StubBrowserBackend(fail=True)
    registry = ResearcherToolRegistry([BrowserTool(backend, store)])

    unknown = execute(registry, {"source_record_id": "src_unknown"})
    missing = execute(registry, {"source_record_id": "src_known"})
    injected = execute(
        registry,
        {"source_record_id": "src_known", "url": "https://evil.example"},
    )
    assert not unknown.succeeded and "unknown source_record_id" in unknown.error
    assert not missing.succeeded and "no fetchable URL" in missing.error
    assert not injected.succeeded and "url" in injected.error
    assert backend.calls == []

    store = ReferenceStore(tmp_path / "failure")
    seed(store)
    failed = execute(
        ResearcherToolRegistry([BrowserTool(backend, store)]),
        {"source_record_id": "src_known"},
    )
    assert not failed.succeeded and "browser unavailable" in failed.error
