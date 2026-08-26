import json
from dataclasses import fields

import pytest

from novelty_agent_framework.agents import NoveltyCoordinatorAgent, SearchPlannerAgent
from novelty_agent_framework.core import TraceHarnessProgressProjector
from novelty_agent_framework.tools import (
    BaiduSearchBackend, BrowserTool, EvidenceCardBuilder, PlaywrightBrowserBackend,
    RetrievalSourceRegistry, WebSearchTool,
)
from novelty_agent_framework.workflows import NoveltyWorkflowServices, TaskResearcherWorkflow
from novelty_agent_framework.config import (
    ResearcherRuntimeConfig,
    build_model_registry,
    build_structured_source_retrieval_tool,
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
    task_researcher = workflow.services.task_researcher
    assert isinstance(coordinator, NoveltyCoordinatorAgent)
    assert isinstance(task_researcher, TaskResearcherWorkflow)
    assert isinstance(task_researcher.evidence_builder, EvidenceCardBuilder)
    assert coordinator._client().profile.model == "model-a"
    assert task_researcher.model_client.profile.model == "model-b"
    assert coordinator.temperature == 0.1


def test_missing_researcher_section_uses_compatible_defaults():
    runtime = ResearcherRuntimeConfig.from_mapping()

    assert runtime.harness.max_turns == 12
    assert runtime.harness.max_total_tool_calls == 10
    assert runtime.harness.per_tool_limits == {}
    assert runtime.projection.enabled is False
    assert runtime.skills.enabled is False


def test_nested_researcher_config_reaches_harness():
    config = json.loads(json.dumps(BASE_CONFIG))
    config["task_researcher"] = {
        "harness": {
            "max_turns": 7,
            "max_total_tool_calls": 5,
            "per_tool_limits": {"tool_a": 1},
        },
        "projection": {},
        "skills": {},
    }

    researcher = build_workflow(config).services.task_researcher

    assert researcher.harness.config.max_turns == 7
    assert researcher.harness.config.max_tool_calls == 5
    assert researcher.harness.config.per_tool_limits == {"tool_a": 1}
    assert researcher.harness.progress_projector is None


def test_factory_enables_progress_projector_only_from_config():
    config = json.loads(json.dumps(BASE_CONFIG))
    config["task_researcher"] = {"projection": {"enabled": True}}

    researcher = build_workflow(config).services.task_researcher

    assert isinstance(
        researcher.harness.progress_projector, TraceHarnessProgressProjector
    )


def test_factory_enables_skills_with_metadata_only_catalog(tmp_path):
    skill_file = tmp_path / "example" / "SKILL.md"
    skill_file.parent.mkdir(parents=True)
    skill_file.write_text(
        "---\nname: example-skill\ndescription: Example.\n---\nPRIVATE BODY\n",
        encoding="utf-8",
    )
    config = json.loads(json.dumps(BASE_CONFIG))
    config["task_researcher"] = {
        "skills": {"enabled": True, "root": str(tmp_path), "max_loaded": 2}
    }

    researcher = build_workflow(config).services.task_researcher

    assert "load_skill" in researcher.tools.names
    fragments = researcher.harness.context_fragments
    assert "example-skill" in fragments[0]
    assert "Example." in fragments[0]
    assert "PRIVATE BODY" not in fragments[0]
    assert str(tmp_path) not in fragments[0]


def test_skills_disabled_keeps_business_tool_view_unchanged():
    config = json.loads(json.dumps(BASE_CONFIG))
    config["task_researcher"] = {"skills": {"enabled": False}}

    researcher = build_workflow(config).services.task_researcher

    assert researcher.tools.names == ("web_search", "browser", "reader")
    assert researcher.harness.context_fragments == ()


def test_legacy_flat_researcher_config_remains_loadable():
    runtime = ResearcherRuntimeConfig.from_mapping(
        {"max_steps": 4, "max_tool_calls": 3, "per_tool_limits": {"old": 2}}
    )

    assert runtime.harness.max_turns == 4
    assert runtime.harness.max_total_tool_calls == 3
    assert runtime.harness.per_tool_limits == {"old": 2}


@pytest.mark.parametrize(
    "raw",
    [
        {"harness": {"max_turns": 0}},
        {"harness": {"max_total_tool_calls": -1}},
        {"harness": {"per_tool_limits": {"tool_a": 0}}},
    ],
)
def test_researcher_runtime_rejects_invalid_budgets(raw):
    with pytest.raises(ValueError, match="positive"):
        ResearcherRuntimeConfig.from_mapping(raw)


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


def test_services_hide_retrieval_implementation_details():
    workflow = build_workflow(BASE_CONFIG)
    assert {item.name for item in fields(NoveltyWorkflowServices)} == {
        "coordinator",
        "task_researcher",
        "point_extractor",
        "validator",
    }
    assert workflow.services.task_researcher.tools.names == (
        "web_search", "browser", "reader")


def test_build_workflow_formal_path_ignores_legacy_arxiv_tools():
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

    assert workflow.services.task_researcher.tools.names == (
        "web_search", "browser", "reader")
    assert workflow.config.candidate_limit_per_task == 5


def test_formal_tools_share_one_reference_store():
    researcher = build_workflow(BASE_CONFIG).services.task_researcher
    web, browser, reader = [researcher.tools.get(name) for name in researcher.tools.names]
    store = researcher.evidence_builder.reference_store
    assert isinstance(web, WebSearchTool) and isinstance(web.backend, BaiduSearchBackend)
    assert isinstance(browser, BrowserTool) and isinstance(browser.backend, PlaywrightBrowserBackend)
    assert web.reference_store is browser.reference_store is reader.reader.reference_store is store


def test_registry_does_not_mask_builder_key_error():
    registry = RetrievalSourceRegistry()

    def broken_builder(config):
        raise KeyError("required_setting")

    registry.register("broken", broken_builder)
    with pytest.raises(KeyError, match="required_setting"):
        registry.build("broken", {})


def test_build_structured_retrieval_tool_does_not_modify_workflow():
    config = json.loads(json.dumps(BASE_CONFIG))
    config["retrieval"] = {
        "active_source": "null_catalog",
        "candidate_limit_per_task": 3,
        "sources": {"null_catalog": {"enabled": True}},
    }
    tool = build_structured_source_retrieval_tool(config)
    assert tool.name == "structured_source_retrieval"
    assert tool.source_id == "null_catalog"
    assert tool.candidate_limit == 3
