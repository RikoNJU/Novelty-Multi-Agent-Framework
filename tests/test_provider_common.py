from __future__ import annotations

import httpx
import pytest

from novelty_agent_framework.tools.database_search.providers.common import (
    HttpRequestPolicy,
    MissingProviderCredentialError,
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
