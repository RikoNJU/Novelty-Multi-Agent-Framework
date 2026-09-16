from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.config import build_standard_full_workflow, load_application_config
from novelty_agent_framework.tools.database_search.factory import build_database_search_tool


def test_live_factory_hides_testing_only_source_but_explicit_test_can_use_it(tmp_path):
    providers = json.loads(Path(
        "backend/src/novelty_agent_framework/config/agents/researcher.example.json"
    ).read_text())["tools"]["database_search"]["providers"]
    config = {"active_source": "arxiv", "sources": providers}
    store = ReferenceStore(tmp_path)
    live = build_database_search_tool(config, reference_store=store,
                                      include_testing_only=False)
    assert set(live.tools_by_source) == {"arxiv"}
    assert "null_catalog" not in live.description
    test = build_database_search_tool(config, reference_store=store,
                                      include_testing_only=True)
    assert set(test.tools_by_source) == {"arxiv", "null_catalog"}


def test_standard_full_workflow_model_tool_schema_omits_null_catalog(tmp_path):
    workflow = build_standard_full_workflow(load_application_config(), output_root=tmp_path)
    registry = workflow.services.task_researcher.tools
    database = registry.get("database_search")
    assert "null_catalog" not in database.tools_by_source
    description = next(row["description"] for row in registry.descriptions()
                       if row["name"] == "database_search")
    assert "null_catalog" not in description
import json
from pathlib import Path
