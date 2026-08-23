import json

import pytest

from novelty_agent_framework.agents import (
    NoveltyCoordinatorAgent,
    NoveltyResearchAgent,
    SearchPlannerAgent,
)
from novelty_agent_framework.tools import ArxivQueryAdapter
from novelty_agent_framework.tools import RetrievalSourceRegistry
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
    assert workflow.config.candidate_limit_per_task == 8

    coordinator = workflow.services.coordinator
    research = workflow.services.research_agent
    search_planner = workflow.services.search_planner
    assert isinstance(coordinator, NoveltyCoordinatorAgent)
    assert isinstance(research, NoveltyResearchAgent)
    assert isinstance(search_planner, SearchPlannerAgent)
    assert isinstance(workflow.services.query_adapter, ArxivQueryAdapter)
    assert coordinator._client().profile.model == "model-a"
    assert research._client().profile.model == "model-b"
    assert search_planner._client().profile.model == "model-b"
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
    assert isinstance(workflow.services.search_planner, SearchPlannerAgent)
    assert isinstance(workflow.services.query_adapter, ArxivQueryAdapter)


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
    assert workflow.config.candidate_limit_per_task == 5


@pytest.mark.parametrize(
    ("retrieval", "message"),
    [
        ({"active_source": "null_catalog", "sources": {}}, "未在.*配置"),
        (
            {
                "active_source": "null_catalog",
                "sources": {"null_catalog": {"enabled": False}},
            },
            "已被禁用",
        ),
        ({"active_source": "null_catalog", "sources": []}, "必须是对象映射"),
    ],
)
def test_active_source_must_exist_and_be_enabled(retrieval, message):
    config = json.loads(json.dumps(BASE_CONFIG))
    config["retrieval"] = retrieval
    with pytest.raises(ValueError, match=message):
        build_workflow(config)


def test_registry_does_not_mask_builder_key_error():
    registry = RetrievalSourceRegistry()

    def broken_builder(config):
        raise KeyError("required_setting")

    registry.register("broken", broken_builder)
    with pytest.raises(KeyError, match="required_setting"):
        registry.build("broken", {})
