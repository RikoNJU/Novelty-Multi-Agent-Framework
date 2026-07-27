from backend.env import ModelRuntimeConfig


def test_model_runtime_config_prefers_project_env(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "shared-model")
    monkeypatch.setenv("NOVELTY_MODEL", "novelty-model")
    monkeypatch.setenv("NOVELTY_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("NOVELTY_API_KEY", "project-key")

    config = ModelRuntimeConfig.from_env("NOVELTY")

    assert config.model == "novelty-model"
    assert config.base_url == "https://example.test/v1"
    assert config.api_key == "project-key"
