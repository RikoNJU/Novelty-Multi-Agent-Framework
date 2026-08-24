"""Provider-neutral WebSearch core abstraction tests."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import pytest

from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.schemas import (
    AccessStatus,
    NoveltyPoint,
    ReaderArguments,
    ResearchTask,
    SourceKind,
    TaskResearchRequest,
    WebSearchArguments,
    Work,
)
from novelty_agent_framework.tools import (
    ResearcherToolRegistry,
    SearchBackendResult,
    SearchHit,
    WebSearchTool,
)

PUBLISHED_AT = datetime(2026, 8, 20, tzinfo=timezone.utc)


def scope(paper_id: str = "paper-1") -> TaskResearchRequest:
    return TaskResearchRequest(
        subject_paper_id=paper_id,
        run_id=f"run-{paper_id}",
        novelty_point=NoveltyPoint(
            point_id="NP-1", claim="一种方法", technical_features=["特征"]
        ),
        research_task=ResearchTask(
            task_id="TASK-1",
            novelty_point_id="NP-1",
            task_type="search",
            language="en",
        ),
    )


def hit(url: str = "https://Example.test/paper#abstract", **updates) -> SearchHit:
    values = {
        "title": "Candidate Paper",
        "url": url,
        "snippet": "A candidate discovery snippet.",
        "score": 0.87,
        "published_at": PUBLISHED_AT,
        "source_name": "Example Journal",
        "external_id": "ext-1",
        "raw_metadata": {"provider_rank": 3},
    }
    values.update(updates)
    return SearchHit(**values)


class StubSearchBackend:
    name = "stub"

    def __init__(self, hits=None, *, warnings=(), fail: bool = False) -> None:
        self.hits = list(hits or [hit()])
        self.warnings = list(warnings)
        self.fail = fail
        self.calls = []

    async def search(self, query: str, *, max_results: int) -> SearchBackendResult:
        self.calls.append((query, max_results))
        if self.fail:
            raise RuntimeError("backend unavailable")
        return SearchBackendResult(
            query=query,
            hits=self.hits,
            warnings=self.warnings,
        )


def execute(registry, arguments, *, request=None):
    return asyncio.run(
        registry.execute(
            "web_search",
            arguments,
            scope=request or scope(),
        )
    )


def test_metadata_arguments_items_persistence_and_warnings(tmp_path) -> None:
    backend = StubSearchBackend(warnings=["partial provider coverage"])
    store = ReferenceStore(output_root=tmp_path)
    tool = WebSearchTool(backend, store)
    registry = ResearcherToolRegistry([tool])

    observation = execute(
        registry,
        {"query": "multi agent novelty search", "max_results": 7},
    )

    assert backend.calls == [("multi agent novelty search", 7)]
    assert tool.name == "web_search"
    assert tool.args_schema is WebSearchArguments
    assert "本身不是证据" in tool.description
    assert registry.names == ("web_search",)
    assert registry.descriptions()[0]["arguments_schema"] == (
        WebSearchArguments.model_json_schema()
    )
    assert observation.succeeded is True
    result = observation.payload["search_result"]
    assert result["query"] == "multi agent novelty search"
    assert result["warnings"] == ["partial provider coverage"]
    item = result["results"][0]
    assert item == {
        "source_record_id": item["source_record_id"],
        "rank": 1,
        "title": "Candidate Paper",
        "url": "https://Example.test/paper#abstract",
        "snippet": "A candidate discovery snippet.",
        "score": 0.87,
        "published_at": PUBLISHED_AT.isoformat().replace("+00:00", "Z"),
        "source_name": "Example Journal",
    }

    manifest = store.load_manifest("paper-1")
    record = manifest.source_records[0]
    assert record.source_record_id == item["source_record_id"]
    assert record.source_kind is SourceKind.WEB
    assert record.source_id == backend.name
    assert record.landing_url == "https://Example.test/paper#abstract"
    assert record.access_status is AccessStatus.DISCOVERED
    assert record.raw_metadata["search_snippet"] == item["snippet"]
    assert record.raw_metadata["provider_rank"] == 3
    assert record.provenance["run_id"] == "run-paper-1"


def test_stable_ids_deduplicate_and_preserve_work_binding(tmp_path) -> None:
    backend = StubSearchBackend()
    store = ReferenceStore(output_root=tmp_path)
    registry = ResearcherToolRegistry([WebSearchTool(backend, store)])

    first = execute(
        registry,
        {"query": "first query", "max_results": 5},
    )
    first_id = first.payload["search_result"]["results"][0]["source_record_id"]
    manifest = store.load_manifest("paper-1")
    bound_record = manifest.source_records[0].model_copy(
        update={
            "work_id": "wrk_bound",
            "access_status": AccessStatus.METADATA_ONLY,
        }
    )
    store.persist_manifest(
        "paper-1",
        manifest.model_copy(
            update={
                "works": [
                    Work(
                        work_id="wrk_bound",
                        work_type="article",
                        title="Bound Work",
                    )
                ],
                "source_records": [bound_record],
            }
        ),
    )

    backend.hits = [
        hit(
            "https://example.test:443/paper",
            title="Updated Candidate",
            external_id=None,
        ),
        hit("https://example.test/other", external_id="ext-2"),
    ]
    second = execute(
        registry,
        {"query": "second query", "max_results": 5},
    )
    ids = [item["source_record_id"] for item in second.payload["search_result"]["results"]]

    assert ids[0] == first_id
    assert ids[1] != first_id
    manifest = store.load_manifest("paper-1")
    assert len(manifest.source_records) == 2
    preserved = next(item for item in manifest.source_records if item.source_record_id == first_id)
    assert preserved.work_id == "wrk_bound"
    assert preserved.access_status is AccessStatus.METADATA_ONLY
    assert preserved.external_id == "ext-1"
    assert preserved.title == "Updated Candidate"


def test_source_records_do_not_cross_paper_workspaces(tmp_path) -> None:
    backend = StubSearchBackend()
    store = ReferenceStore(output_root=tmp_path)
    registry = ResearcherToolRegistry([WebSearchTool(backend, store)])

    execute(registry, {"query": "paper one", "max_results": 1}, request=scope("paper-1"))
    assert len(store.load_manifest("paper-1").source_records) == 1
    assert store.load_manifest("paper-2").source_records == []

    execute(registry, {"query": "paper two", "max_results": 1}, request=scope("paper-2"))
    assert len(store.load_manifest("paper-1").source_records) == 1
    assert len(store.load_manifest("paper-2").source_records) == 1


def test_backend_exception_and_invalid_arguments_use_registry_failure(tmp_path) -> None:
    backend = StubSearchBackend(fail=True)
    registry = ResearcherToolRegistry(
        [WebSearchTool(backend, ReferenceStore(output_root=tmp_path))]
    )

    failed_backend = execute(
        registry,
        {"query": "will fail", "max_results": 2},
    )
    invalid_arguments = execute(
        registry,
        {
            "query": "cannot inject scope",
            "max_results": 2,
            "subject_paper_id": "evil-paper",
        },
    )

    assert failed_backend.succeeded is False
    assert "backend unavailable" in failed_backend.error
    assert invalid_arguments.succeeded is False
    assert "subject_paper_id" in invalid_arguments.error
    assert backend.calls == [("will fail", 2)]


def test_web_search_schema_is_independent_from_reader_schema() -> None:
    assert WebSearchArguments.model_fields.keys() == {"query", "max_results"}
    assert "artifact_id" in ReaderArguments.model_fields


def test_backend_contract_rejects_empty_identity_and_non_json_metadata() -> None:
    with pytest.raises(ValueError, match="title"):
        hit(title="   ")
    with pytest.raises(ValueError, match="url"):
        hit(url="")
    with pytest.raises(ValueError, match="JSON-compatible"):
        hit(raw_metadata={"timestamp": PUBLISHED_AT})
    with pytest.raises(ValueError, match="query"):
        SearchBackendResult(query="   ")
