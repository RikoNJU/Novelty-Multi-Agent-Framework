import json
from pathlib import Path

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


def test_search_planner_example_filename_is_canonical():
    assert DEFAULT_SEARCH_PLANNER_PATH.name == "search_planner.example.json"
    assert DEFAULT_SEARCH_PLANNER_PATH.exists()
    assert not (DEFAULT_SEARCH_PLANNER_PATH.parent / "search_panner.example.json").exists()


@pytest.mark.parametrize(
    "mutate",
    [
        lambda raw: raw["tools"]["reader"].update(
            default_chars_per_read=1001, max_chars_per_read=1000
        ),
        lambda raw: raw["tools"]["reader"].update(max_chars_per_read=16001),
        lambda raw: raw["tools"]["web_search"].update(
            default_max_results=11, max_results_per_call=10
        ),
        lambda raw: raw["tools"]["web_search"].update(max_results_per_call=51),
    ],
)
def test_cross_field_limits_fail_fast(tmp_path: Path, mutate):
    raw = json.loads(DEFAULT_RESEARCHER_PATH.read_text())
    mutate(raw)
    path = tmp_path / "researcher.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValidationError):
        load_application_config(researcher_path=path)


def test_typed_config_builds_four_tool_workflow_without_legacy_projection(
    monkeypatch,
):
    config = load_application_config()
    monkeypatch.setattr(
        "novelty_agent_framework.config.factory.legacy_shape",
        lambda _: (_ for _ in ()).throw(AssertionError("legacy_shape called")),
    )
    workflow = build_workflow(config)
    assert workflow.services.task_researcher.tools.names == (
        "database_search", "web_search", "browser", "reader"
    )
    database = workflow.services.task_researcher.tools.get("database_search")
    planner = next(iter(database.tools_by_source.values())).search_planner
    assert planner._model_alias == config.search_planner.model.alias
