from pathlib import Path

import pytest

from novelty_agent_framework.tools.browser_runtime import (
    BrowserDependencyError,
    playwright_launch_kwargs,
    resolve_browser_network,
    resolve_chromium_runtime,
)


def test_browser_network_inherit_without_proxy() -> None:
    settings = resolve_browser_network("inherit", {})
    assert settings.mode == "inherit"
    assert settings.playwright_proxy() is None


def test_browser_network_inherit_with_uppercase_proxy() -> None:
    settings = resolve_browser_network(
        "inherit",
        {"HTTPS_PROXY": "http://proxy.example:8080"},
    )
    assert settings.playwright_proxy() == {
        "server": "http://proxy.example:8080"
    }


def test_browser_network_inherit_with_lowercase_proxy() -> None:
    settings = resolve_browser_network(
        "inherit",
        {"https_proxy": "https://lower.example:8443"},
    )
    assert settings.server == "https://lower.example:8443"


def test_browser_network_direct_ignores_proxy(tmp_path: Path) -> None:
    library_dir = tmp_path / "lib"
    library_dir.mkdir()
    for name in ("libnspr4.so", "libnss3.so", "libnssutil3.so", "libasound.so.2"):
        (library_dir / name).touch()
    kwargs, settings, runtime = playwright_launch_kwargs(
        "direct",
        {"HTTPS_PROXY": "http://ignored.example:8080"},
        python_prefix=tmp_path,
    )
    assert settings.mode == "direct"
    assert "proxy" not in kwargs
    assert runtime.mode in {"system", "environment_fallback"}


def test_browser_network_invalid_mode() -> None:
    with pytest.raises(ValueError, match="network mode"):
        resolve_browser_network("automatic", {})


def test_proxy_credentials_are_not_logged() -> None:
    secret = "never-print-this"
    settings = resolve_browser_network(
        "inherit",
        {"HTTPS_PROXY": f"http://user:{secret}@proxy.example:8080"},
    )
    proxy = settings.playwright_proxy()
    assert proxy == {
        "server": "http://proxy.example:8080",
        "username": "user",
        "password": secret,
    }
    assert secret not in str(settings.safe_summary())
    assert "proxy.example" not in str(settings.safe_summary())


def test_browser_network_inherit_no_proxy_bypass() -> None:
    settings = resolve_browser_network(
        "inherit",
        {
            "HTTP_PROXY": "http://proxy.example:8080",
            "NO_PROXY": "localhost,.internal.example",
        },
    )
    assert settings.playwright_proxy()["bypass"] == "localhost,.internal.example"


def test_conda_library_fallback_is_child_scoped(tmp_path: Path) -> None:
    library_dir = tmp_path / "lib"
    library_dir.mkdir()
    for name in ("libnspr4.so", "libnss3.so", "libnssutil3.so", "libasound.so.2"):
        (library_dir / name).touch()
    runtime = resolve_chromium_runtime(
        {"EXAMPLE": "value"},
        python_prefix=tmp_path,
        system_libraries_available=False,
    )
    child = runtime.child_environment
    assert runtime.mode == "environment_fallback"
    assert child["LD_LIBRARY_PATH"] == str(library_dir)
    assert child["EXAMPLE"] == "value"


def test_system_libraries_use_normal_launch_path(tmp_path: Path) -> None:
    runtime = resolve_chromium_runtime(
        {}, python_prefix=tmp_path, system_libraries_available=True
    )
    assert runtime.mode == "system"
    assert runtime.child_environment is None


def test_missing_system_and_environment_libraries_fail_clearly(tmp_path: Path) -> None:
    with pytest.raises(BrowserDependencyError, match="install-deps chromium"):
        resolve_chromium_runtime(
            {}, python_prefix=tmp_path, system_libraries_available=False
        )
