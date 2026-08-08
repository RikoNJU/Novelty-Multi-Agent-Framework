import json

from novelty_agent_framework.agents import (
    NoveltyCoordinatorAgent,
    NoveltyResearchAgent,
)
from novelty_agent_framework.config import (
    build_model_registry,
    build_workflow,
    load_config,
)

BASE_CONFIG = {
    "workflow": {
        "max_rounds": 3,
        "max_concurrency": 2,
        "minimum_evidence_per_point": 2,
    },
    "models": {
        "m1": {
            "model": "model-a",
            "base_url": "https://a.test/v1",
            "api_key_env": "TEST_KEY_A",
            "supported_params": ["enable_thinking"],
        },
        "m2": {
            "model": "model-b",
            "base_url": "https://b.test/v1",
            "api_key_env": "TEST_KEY_B",
        },
    },
    "agents": {
        "coordinator": {"model": "m1", "temperature": 0.1},
        "research": {"model": "m2", "temperature": 0.5},
    },
}


def test_load_config_default_contains_models_and_agents():
    config = load_config()
    assert "models" in config
    assert "agents" in config
    assert config["agents"]["coordinator"]["model"] == "glm4.7"


def test_build_workflow_wires_role_models(monkeypatch):
    monkeypatch.setenv("TEST_KEY_A", "key-a")
    monkeypatch.setenv("TEST_KEY_B", "key-b")

    workflow = build_workflow(BASE_CONFIG)

    assert workflow.config.max_rounds == 3
    assert workflow.config.max_concurrency == 2
    assert workflow.config.minimum_evidence_per_point == 2

    coordinator = workflow.services.coordinator
    research = workflow.services.research_agent
    assert isinstance(coordinator, NoveltyCoordinatorAgent)
    assert isinstance(research, NoveltyResearchAgent)
    assert coordinator._client().profile.model == "model-a"
    assert research._client().profile.model == "model-b"
    assert coordinator.temperature == 0.1
    assert research.temperature == 0.5


def test_build_workflow_env_overrides_role_model(monkeypatch):
    monkeypatch.setenv("TEST_KEY_A", "key-a")
    monkeypatch.setenv("TEST_KEY_B", "key-b")
    monkeypatch.setenv("NOVELTY_COORDINATOR_MODEL", "m2")

    workflow = build_workflow(BASE_CONFIG)

    assert workflow.services.coordinator._client().profile.model == "model-b"


def test_build_workflow_does_not_mutate_input_config(monkeypatch):
    monkeypatch.setenv("NOVELTY_COORDINATOR_MODEL", "m2")
    original = json.dumps(BASE_CONFIG, sort_keys=True)

    build_workflow(BASE_CONFIG)

    assert json.dumps(BASE_CONFIG, sort_keys=True) == original


def test_registry_resolves_api_key_env(monkeypatch):
    monkeypatch.setenv("TEST_KEY_A", "secret-a")

    registry = build_model_registry(BASE_CONFIG)
    client = registry.client_for("m1")

    assert client.profile.api_key == "secret-a"


def test_build_tools_disabled_by_default():
    workflow = build_workflow(BASE_CONFIG)

    assert workflow.services.search_tool is None
    assert workflow.services.full_text_tool is None
    assert workflow.services.metadata_tool is None


def test_build_workflow_injects_arxiv_tools_when_enabled():
    config = json.loads(json.dumps(BASE_CONFIG))
    config["tools"] = {
        "arxiv": {
            "enabled": True,
            "min_interval": 0.0,
            "timeout": 5.0,
            "candidate_limit": 5,
        }
    }

    workflow = build_workflow(config)

    assert workflow.services.search_tool is not None
    assert workflow.services.full_text_tool is not None
    assert workflow.services.metadata_tool is not None
    assert workflow.services.research_agent.candidate_limit == 5
