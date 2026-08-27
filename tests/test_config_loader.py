import json

import pytest
from pydantic import ValidationError

from novelty_agent_framework.config import build_workflow, load_application_config
from novelty_agent_framework.config.loader import (
    DEFAULT_MODELS_PATH,
    DEFAULT_PROJECT_PATH,
    DEFAULT_RESEARCHER_PATH,
    DEFAULT_SEARCH_PLANNER_PATH,
)


def test_split_files_load_and_project_settings_are_slim():
    config = load_application_config()
    project = json.loads(DEFAULT_PROJECT_PATH.read_text())
    assert not {"models", "agents", "task_researcher", "retrieval"} & set(project)
    assert config.models and config.researcher.version == config.search_planner.version == 1
    assert config.researcher.model.alias != config.search_planner.model.alias


def test_example_files_contain_no_secret_values():
    combined = "\n".join(path.read_text() for path in (
        DEFAULT_MODELS_PATH, DEFAULT_RESEARCHER_PATH, DEFAULT_SEARCH_PLANNER_PATH
    ))
    assert "api_key_env" in combined
    assert '"api_key"' not in combined
    assert "Bearer " not in combined


def test_invalid_numeric_value_fails_fast(tmp_path):
    raw = json.loads(DEFAULT_RESEARCHER_PATH.read_text())
    raw["harness"]["max_turns"] = 0
    path = tmp_path / "researcher.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValidationError):
        load_application_config(researcher_path=path)


def test_unknown_model_alias_fails_fast(tmp_path):
    raw = json.loads(DEFAULT_RESEARCHER_PATH.read_text())
    raw["model"]["alias"] = "missing-model"
    path = tmp_path / "researcher.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValidationError, match="unknown model aliases"):
        load_application_config(researcher_path=path)


def test_environment_model_override_is_loader_owned():
    config = load_application_config(environ={"NOVELTY_RESEARCH_MODEL": "glm4.7"})
    assert config.researcher.model.alias == "glm4.7"


def test_typed_config_builds_four_tool_workflow():
    config = load_application_config()
    workflow = build_workflow(config)
    assert workflow.services.task_researcher.tools.names == (
        "database_search", "web_search", "browser", "reader"
    )
    database = workflow.services.task_researcher.tools.get("database_search")
    planner = next(iter(database.tools_by_source.values())).search_planner
    assert planner._model_alias == config.search_planner.model.alias
