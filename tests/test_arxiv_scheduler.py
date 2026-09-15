"""Offline concurrency gates for ARXIV-BATCH-01."""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest

from novelty_agent_framework.core.runtime_artifacts import (
    RuntimeArtifactManager,
    RuntimeDebugConfig,
)

from novelty_agent_framework.tools.database_search.providers.arxiv import (
    ArxivMetadataTool,
    ArxivSearchTool,
)
from novelty_agent_framework.tools.database_search.providers.arxiv_scheduler import (
    ArxivRequestScheduler,
    ArxivResponseParseError,
)


def _feed(ids: list[str]) -> str:
    entries = "".join(
        f"""
        <entry>
          <id>http://arxiv.org/abs/{doc_id}v1</id>
          <title>Paper {doc_id}</title>
          <summary>abstract</summary>
          <published>2024-01-01T00:00:00Z</published>
          <author><name>Test Author</name></author>
        </entry>"""
        for doc_id in ids
    )
    return f"<feed xmlns='http://www.w3.org/2005/Atom'>{entries}</feed>"


def _client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_twenty_metadata_calls_with_fifteen_unique_ids_use_one_request():
    physical: list[list[str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        ids = request.url.params["id_list"].split(",")
        physical.append(ids)
        return httpx.Response(200, text=_feed(ids))

    scheduler = ArxivRequestScheduler(
        client=_client(handler),
        min_interval=0,
        metadata_batch_window_ms=100,
        metadata_batch_max_size=32,
    )
    tool = ArxivMetadataTool(scheduler=scheduler)
    unique = [f"2401.{index:05d}" for index in range(15)]
    logical = unique + unique[:5]
    barrier = threading.Barrier(len(logical))

    def resolve(doc_id: str):
        barrier.wait()
        return tool.resolve(doc_id)

    try:
        with ThreadPoolExecutor(max_workers=len(logical)) as executor:
            results = list(executor.map(resolve, logical))
        assert all(result is not None for result in results)
        assert len(physical) == 1
        assert set(physical[0]) == set(unique)
        metrics = scheduler.snapshot_metrics()
        assert metrics["metadata_logical_requests"] == 20
        assert metrics["metadata_physical_requests"] == 1
        assert metrics["unique_metadata_ids"] == 15
        assert metrics["dedup_count"] == 5
        assert metrics["average_batch_size"] == 15
        assert metrics["metadata_batch_ratio"] == 20
    finally:
        scheduler.shutdown()


def test_search_and_metadata_share_physical_minimum_interval():
    dispatches: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        dispatches.append(time.monotonic())
        ids = request.url.params.get("id_list")
        return httpx.Response(200, text=_feed(ids.split(",") if ids else []))

    scheduler = ArxivRequestScheduler(
        client=_client(handler),
        min_interval=0.04,
        metadata_batch_window_ms=0,
    )
    search = ArxivSearchTool(scheduler=scheduler)
    metadata = ArxivMetadataTool(scheduler=scheduler)
    try:
        search.search("first")
        assert metadata.resolve("2401.00001") is not None
        assert len(dispatches) == 2
        assert dispatches[1] - dispatches[0] >= 0.039
        assert scheduler.snapshot_metrics()["interval_violation_count"] == 0
    finally:
        scheduler.shutdown()


def test_metadata_batch_feature_switch_uses_one_request_per_id():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        ids = request.url.params["id_list"].split(",")
        return httpx.Response(200, text=_feed(ids))

    scheduler = ArxivRequestScheduler(
        client=_client(handler),
        min_interval=0,
        metadata_batch_enabled=False,
    )
    tool = ArxivMetadataTool(scheduler=scheduler)
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(tool.resolve, ["2401.10001", "2401.10002"]))
        assert all(result is not None for result in results)
        assert calls == 2
    finally:
        scheduler.shutdown()


def test_scheduler_feature_switch_keeps_central_path_but_disables_interval():
    dispatches: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        dispatches.append(time.monotonic())
        return httpx.Response(200, text=_feed([]))

    scheduler = ArxivRequestScheduler(
        client=_client(handler),
        min_interval=4,
        scheduler_enabled=False,
    )
    try:
        search = ArxivSearchTool(scheduler=scheduler)
        search.search("one")
        search.search("two")
        assert dispatches[1] - dispatches[0] < 0.5
    finally:
        scheduler.shutdown()


def test_429_fails_every_waiter_in_metadata_batch():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(429, headers={"Retry-After": "12"})

    scheduler = ArxivRequestScheduler(
        client=_client(handler),
        min_interval=0,
        max_retries=0,
        metadata_batch_window_ms=75,
        circuit_failure_threshold=100,
    )
    tool = ArxivMetadataTool(scheduler=scheduler)
    barrier = threading.Barrier(8)

    def resolve(index: int):
        barrier.wait()
        return tool.resolve(f"2402.{index:05d}")

    try:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(resolve, index) for index in range(8)]
            for future in futures:
                with pytest.raises(httpx.HTTPStatusError) as caught:
                    future.result(timeout=2)
                assert caught.value.response.status_code == 429
        assert calls == 1
        assert scheduler.snapshot_metrics()["http_429_count"] == 1
    finally:
        scheduler.shutdown()


def test_read_timeout_fails_every_waiter_in_metadata_batch():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("batch timed out", request=request)

    scheduler = ArxivRequestScheduler(
        client=_client(handler),
        min_interval=0,
        max_retries=0,
        metadata_batch_window_ms=30,
        circuit_failure_threshold=100,
    )
    tool = ArxivMetadataTool(scheduler=scheduler)
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(tool.resolve, f"2402.1000{index}")
                for index in range(4)
            ]
            for future in futures:
                with pytest.raises(httpx.ReadTimeout):
                    future.result(timeout=2)
        metrics = scheduler.snapshot_metrics()
        assert metrics["metadata_physical_requests"] == 1
        assert metrics["read_timeout_count"] == 1
    finally:
        scheduler.shutdown()


@pytest.mark.parametrize("body", ["not xml", "<feed>"])
def test_invalid_atom_fails_every_waiter(body: str):
    scheduler = ArxivRequestScheduler(
        client=_client(lambda request: httpx.Response(200, text=body)),
        min_interval=0,
        metadata_batch_window_ms=20,
    )
    tool = ArxivMetadataTool(scheduler=scheduler)
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(tool.resolve, f"2403.0000{i}") for i in range(2)]
            for future in futures:
                with pytest.raises(ArxivResponseParseError):
                    future.result(timeout=2)
    finally:
        scheduler.shutdown()


def test_valid_atom_can_return_none_for_missing_id_only():
    scheduler = ArxivRequestScheduler(
        client=_client(lambda request: httpx.Response(200, text=_feed(["2404.00001"]))),
        min_interval=0,
        metadata_batch_window_ms=30,
    )
    tool = ArxivMetadataTool(scheduler=scheduler)
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            present = executor.submit(tool.resolve, "2404.00001")
            missing = executor.submit(tool.resolve, "2404.00002")
            assert present.result(timeout=2) is not None
            assert missing.result(timeout=2) is None
    finally:
        scheduler.shutdown()


def test_runtime_artifacts_include_logical_physical_and_summary(tmp_path):
    scheduler = ArxivRequestScheduler(
        client=_client(
            lambda request: httpx.Response(200, text=_feed(["2405.00001"]))
        ),
        min_interval=0,
        metadata_batch_window_ms=10,
    )
    manager = RuntimeArtifactManager(
        "arxiv-runtime-test",
        config=RuntimeDebugConfig(
            output_root=tmp_path / "outputs",
            archive_root=tmp_path / "archive",
        ),
        diagnostics=(),
    )
    try:
        with manager:
            assert ArxivMetadataTool(scheduler=scheduler).resolve("2405.00001") is not None
        summary_path, _ = manager.finish_run("SUCCESS")
        assert summary_path is not None
        import json

        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        metrics = summary["provider_requests"]
        assert metrics["logical_api_requests"] == 1
        assert metrics["physical_api_requests"] == 1
        assert metrics["metadata_batch_ratio"] == 1
        provider_files = list((manager.run_dir / "provider_requests").glob("*.json"))
        assert len(provider_files) == 2
    finally:
        scheduler.shutdown()
