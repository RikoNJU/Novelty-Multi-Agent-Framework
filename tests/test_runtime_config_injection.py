import json

from novelty_agent_framework.config import build_workflow, effective_safe_config
from novelty_agent_framework.config.loader import (
    DEFAULT_RESEARCHER_PATH,
    DEFAULT_SEARCH_PLANNER_PATH,
    load_application_config,
)


def test_perturbed_config_reaches_runtime_objects(tmp_path):
    researcher_raw = json.loads(DEFAULT_RESEARCHER_PATH.read_text())
    researcher_raw["model"].update(temperature=0.17, max_tokens=321, timeout_seconds=12)
    researcher_raw["harness"].update(max_turns=7, max_total_tool_calls=6)
    researcher_raw["harness"]["per_tool_limits"]["browser"] = 2
    database = researcher_raw["tools"]["database_search"]
    database.update(candidate_limit_per_task=3, full_text_limit_per_task=2, max_concurrency=5)
    database["providers"]["arxiv"].update(
        min_interval_seconds=0.07, timeout_seconds=4, max_retries=1,
        full_text_max_chars=4321,
    )
    researcher_raw["tools"]["web_search"].update(default_max_results=4, max_results_per_call=6)
    researcher_raw["tools"]["web_search"]["baidu"]["timeout_seconds"] = 7
    researcher_raw["tools"]["browser"].update(
        navigation_timeout_ms=4321, max_html_chars=2222, max_text_chars=1111
    )
    researcher_raw["tools"]["reader"].update(
        default_chars_per_read=1000, max_chars_per_read=1234,
        max_total_read_chars=2345,
    )
    planner_raw = json.loads(DEFAULT_SEARCH_PLANNER_PATH.read_text())
    planner_raw["model"].update(temperature=0.19, max_tokens=654, timeout_seconds=13)
    planner_raw["max_attempts"] = 1
    researcher_path = tmp_path / "researcher.json"
    planner_path = tmp_path / "planner.json"
    researcher_path.write_text(json.dumps(researcher_raw), encoding="utf-8")
    planner_path.write_text(json.dumps(planner_raw), encoding="utf-8")

    config = load_application_config(
        researcher_path=researcher_path, search_planner_path=planner_path
    )
    workflow = build_workflow(config)
    task = workflow.services.task_researcher
    database_tool = task.tools.get("database_search")
    internal = database_tool.tools_by_source["arxiv"]
    web = task.tools.get("web_search")
    browser = task.tools.get("browser")
    reader = task.tools.get("reader")
    planner = internal.search_planner

    assert task.config.max_steps == 7 and task.config.max_tool_calls == 6
    assert task.harness.config.per_tool_limits["browser"] == 2
    assert task.harness.config.max_total_read_chars == 2345
    assert task.config.model_options.temperature == 0.17
    assert task.config.model_options.max_tokens == 321
    assert task.config.model_options.timeout_seconds == 12
    assert internal.candidate_limit == 3 and internal.full_text_limit == 2
    assert internal.max_concurrency == 5
    assert internal.source.search_tool._min_interval == 0.07
    assert internal.source.search_tool._max_retries == 1
    assert internal.source.full_text_tool._max_chars == 4321
    assert web.default_max_results == 4 and web.max_results_per_call == 6
    assert web.backend.timeout_seconds == 7
    assert browser.backend.navigation_timeout_ms == 4321
    assert browser.backend.limits.html_chars == 2222
    assert browser.backend.limits.text_chars == 1111
    assert reader.default_chars_per_read == 1000
    assert reader.reader.max_chars_per_read == 1234
    assert planner.max_attempts == 1
    assert planner.model_options.temperature == 0.19
    assert planner.model_options.max_tokens == 654
    assert planner.model_options.timeout_seconds == 13

    safe = effective_safe_config(config)
    serialized = json.dumps(safe)
    assert "api_key\"" not in serialized and "secret" not in serialized.lower()
