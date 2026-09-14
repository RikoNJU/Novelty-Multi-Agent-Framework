from __future__ import annotations

import asyncio
import threading
import time

import pytest

from novelty_agent_framework.agents import DemoQueryAdapter
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.ports import FullText, SearchHit
from novelty_agent_framework.schemas import (
    EvidenceSource,
    NoveltyPoint,
    ResearchTask,
    SearchConcept,
    SearchPlan,
    SearchStrategy,
    StructuredSourceRetrievalRequest,
)
from novelty_agent_framework.tools.database_search import (
    RetrievalSource,
    StructuredSourceRetrievalTool,
)
from novelty_agent_framework.tools.database_search.structured_retrieval import (
    _invoke_provider,
)


def _request() -> StructuredSourceRetrievalRequest:
    return StructuredSourceRetrievalRequest(
        subject_paper_id="async-boundary-paper",
        source_id="demo",
        novelty_point=NoveltyPoint(point_id="NP-1", claim="claim"),
        research_task=ResearchTask(
            task_id="T-1",
            novelty_point_id="NP-1",
            task_type="search",
            language="en",
        ),
        search_plan=SearchPlan(
            task_id="T-1",
            novelty_point_id="NP-1",
            concepts=[SearchConcept(concept_id="C1", name="term", terms=["term"])],
            strategies=[
                SearchStrategy(strategy_id="S1", level="strict", expression="C1")
            ],
        ),
        run_id="async-boundary-run",
    )


def _hit() -> SearchHit:
    return SearchHit(
        document_id="2305.12345",
        source_id="demo",
        external_id="2305.12345v1",
        title="Async Boundary",
        abstract="Abstract text.",
        url="https://example.test/2305.12345",
    )


class _BlockingSearch:
    source_id = "demo"

    def __init__(self, thread_ids: list[int], release: threading.Event) -> None:
        self.thread_ids = thread_ids
        self.release = release
        self.released_by_event_loop = False

    def search(self, query: str, *, limit: int = 10):
        self.thread_ids.append(threading.get_ident())
        self.released_by_event_loop = self.release.wait(timeout=0.5)
        return [_hit()]


class _BlockingMetadata:
    source_id = "demo"

    def __init__(self, thread_ids: list[int]) -> None:
        self.thread_ids = thread_ids

    def resolve(self, document_id: str):
        self.thread_ids.append(threading.get_ident())
        time.sleep(0.05)
        return EvidenceSource(title="Resolved title", url="https://example.test/resolved")


class _BlockingFullText:
    source_id = "demo"

    def __init__(self, thread_ids: list[int]) -> None:
        self.thread_ids = thread_ids

    def fetch(self, document_id: str):
        self.thread_ids.append(threading.get_ident())
        time.sleep(0.05)
        return FullText(document_id=document_id, title="Full text", text="Body text.")


def test_sync_provider_capabilities_do_not_block_event_loop(tmp_path) -> None:
    provider_threads: list[int] = []
    release = threading.Event()
    search = _BlockingSearch(provider_threads, release)
    source = RetrievalSource(
        source_id="demo",
        query_adapter=DemoQueryAdapter(),
        search_tool=search,
        metadata_tool=_BlockingMetadata(provider_threads),
        full_text_tool=_BlockingFullText(provider_threads),
    )
    tool = StructuredSourceRetrievalTool(
        source=source,
        reference_store=ReferenceStore(tmp_path),
    )

    async def run() -> int:
        event_loop_thread = threading.get_ident()
        retrieval_task = asyncio.create_task(tool.ainvoke(_request()))
        await asyncio.sleep(0.01)
        release.set()
        bundle = await retrieval_task
        assert bundle.search_executions[0].status.value == "succeeded"
        assert bundle.artifacts
        return event_loop_thread

    event_loop_thread = asyncio.run(run())

    assert len(provider_threads) == 3
    assert all(thread_id != event_loop_thread for thread_id in provider_threads)
    assert search.released_by_event_loop is True


def test_native_async_provider_runs_on_event_loop_thread(tmp_path) -> None:
    provider_threads: list[int] = []

    class AsyncSearch:
        source_id = "demo"

        async def search(self, query: str, *, limit: int = 10):
            provider_threads.append(threading.get_ident())
            return [_hit()]

    class AsyncMetadata:
        source_id = "demo"

        async def resolve(self, document_id: str):
            provider_threads.append(threading.get_ident())
            return EvidenceSource(title="Resolved title")

    class AsyncFullText:
        source_id = "demo"

        async def fetch(self, document_id: str):
            provider_threads.append(threading.get_ident())
            return FullText(document_id=document_id, title="Full text", text="Body text.")

    tool = StructuredSourceRetrievalTool(
        source=RetrievalSource(
            source_id="demo",
            query_adapter=DemoQueryAdapter(),
            search_tool=AsyncSearch(),
            metadata_tool=AsyncMetadata(),
            full_text_tool=AsyncFullText(),
        ),
        reference_store=ReferenceStore(tmp_path),
    )

    async def run() -> int:
        event_loop_thread = threading.get_ident()
        bundle = await tool.ainvoke(_request())
        assert bundle.search_executions[0].status.value == "succeeded"
        return event_loop_thread

    event_loop_thread = asyncio.run(run())

    assert len(provider_threads) == 3
    assert set(provider_threads) == {event_loop_thread}


def test_sync_provider_returning_awaitable_is_awaited_off_calling_thread() -> None:
    calling_threads: list[int] = []
    awaited_threads: list[int] = []

    def provider():
        calling_threads.append(threading.get_ident())

        async def result() -> str:
            awaited_threads.append(threading.get_ident())
            return "done"

        return result()

    async def run() -> tuple[str, int]:
        event_loop_thread = threading.get_ident()
        return await _invoke_provider(provider), event_loop_thread

    value, event_loop_thread = asyncio.run(run())

    assert value == "done"
    assert calling_threads[0] != event_loop_thread
    assert awaited_threads == [event_loop_thread]


def test_sync_provider_exception_keeps_original_type() -> None:
    class ProviderFailure(RuntimeError):
        pass

    def provider() -> None:
        raise ProviderFailure("provider failed")

    async def run() -> None:
        with pytest.raises(ProviderFailure, match="provider failed"):
            await _invoke_provider(provider)

    asyncio.run(run())
