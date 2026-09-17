from __future__ import annotations

import httpx
import pytest
from novelty_agent_framework.core.runtime_artifacts import (
    ProviderPhysicalBudgetExceeded, RuntimeArtifactManager, RuntimeDebugConfig,
)

from novelty_agent_framework.tools.database_search.providers.common import (
    HttpRequestPolicy,
    MissingProviderCredentialError,
    ProviderRequestError,
    ResilientHttpClient,
    resolve_env_credential,
)


def test_resolve_env_credential_reads_named_environment_variable(monkeypatch) -> None:
    monkeypatch.setenv("CATALOG_TEST_KEY", "secret")

    value = resolve_env_credential(
        {"api_key_env": "CATALOG_TEST_KEY"}, setting="api_key_env"
    )

    assert value == "secret"


def test_missing_credential_error_names_environment_not_secret(monkeypatch) -> None:
    monkeypatch.delenv("CATALOG_MISSING_KEY", raising=False)

    with pytest.raises(MissingProviderCredentialError, match="CATALOG_MISSING_KEY"):
        resolve_env_credential(
            {"api_key_env": "CATALOG_MISSING_KEY"}, setting="api_key_env"
        )


def test_resilient_client_retries_429() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(429, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"ok": True})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    transport = ResilientHttpClient(
        client,
        policy=HttpRequestPolicy(
            min_interval_seconds=0,
            max_retries=1,
            retry_backoff_seconds=0,
        ),
    )

    response = transport.get("https://catalog.test/items")

    assert response.json() == {"ok": True}
    assert calls["count"] == 2


def test_transport_error_does_not_expose_credential_bearing_url() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("cannot connect", request=request)

    transport = ResilientHttpClient(
        httpx.Client(transport=httpx.MockTransport(handler)),
        policy=HttpRequestPolicy(min_interval_seconds=0, max_retries=0),
    )

    with pytest.raises(ProviderRequestError) as exc_info:
        transport.get(
            "https://catalog.test/items",
            params={"api_key": "secret-key"},
        )

    assert "secret-key" not in str(exc_info.value)
    assert "catalog.test" not in str(exc_info.value)


def test_physical_budget_counts_retry_before_http_dispatch(tmp_path) -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(503)

    transport = ResilientHttpClient(
        httpx.Client(transport=httpx.MockTransport(handler)),
        policy=HttpRequestPolicy(max_retries=2, retry_backoff_seconds=0),
    )
    manager = RuntimeArtifactManager("paper", config=RuntimeDebugConfig(
        output_root=tmp_path / "output", archive_root=tmp_path / "archive",
        max_physical_provider_requests=1))
    manager.activate()
    try:
        with pytest.raises(ProviderPhysicalBudgetExceeded):
            transport.get("https://catalog.test/items")
    finally:
        manager.deactivate()
    assert len(calls) == 1
    assert len(list((manager.run_dir / "provider_budget").glob("*.json"))) == 1
