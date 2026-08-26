"""Skill metadata discovery and on-demand loading infrastructure tests."""

from __future__ import annotations

import asyncio
import json

import pytest

from backend.env import ModelResponse, ModelToolCall, PromptLibrary
from novelty_agent_framework.core import ToolCallHarness
from novelty_agent_framework.schemas import (
    NoveltyPoint,
    ResearchTask,
    TaskResearchRequest,
)
from novelty_agent_framework.skills import (
    LoadSkillTool,
    SkillRegistry,
    SkillRegistryError,
)
from novelty_agent_framework.tools import ResearcherToolRegistry


def write_skill(root, folder="example", *, name="example-skill", body="# Guide\nDo it."):
    path = root / folder / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        f"---\nname: {name}\ndescription: Example instructions.\n---\n{body}\n",
        encoding="utf-8",
    )
    return path


def scope():
    return TaskResearchRequest(
        subject_paper_id="paper-1",
        run_id="run-1",
        novelty_point=NoveltyPoint(
            point_id="NP-1", claim="claim", technical_features=["feature"]
        ),
        research_task=ResearchTask(
            task_id="T-1",
            novelty_point_id="NP-1",
            task_type="search",
            language="en",
        ),
    )


class ScriptedModel:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    async def acomplete(self, messages, *, options=None):
        self.calls.append((list(messages), options))
        return self.responses.pop(0)


def load_call(call_id):
    return ModelResponse(
        content=None,
        tool_calls=(
            ModelToolCall(
                id=call_id, name="load_skill", arguments={"name": "example-skill"}
            ),
        ),
    )


def test_scan_lists_metadata_without_body_or_internal_path(tmp_path):
    path = write_skill(tmp_path, body="SECRET BODY")
    registry = SkillRegistry.scan(tmp_path)

    metadata = registry.list_metadata()
    assert metadata[0].name == "example-skill"
    assert metadata[0].description == "Example instructions."
    assert metadata[0].path == path
    assert registry.catalog() == (
        {"name": "example-skill", "description": "Example instructions."},
    )
    assert "SECRET BODY" not in json.dumps(registry.catalog())
    assert str(tmp_path) not in json.dumps(registry.catalog())


def test_load_returns_body_and_unknown_name_fails(tmp_path):
    write_skill(tmp_path, body="# Full\nComplete instructions.")
    registry = SkillRegistry.scan(tmp_path)

    assert registry.load("example-skill") == "# Full\nComplete instructions."
    with pytest.raises(SkillRegistryError, match="unknown skill"):
        registry.load("missing")


def test_duplicate_name_fails_fast(tmp_path):
    write_skill(tmp_path, "one", name="duplicate")
    write_skill(tmp_path, "two", name="duplicate")

    with pytest.raises(SkillRegistryError, match="duplicate skill name"):
        SkillRegistry.scan(tmp_path)


@pytest.mark.parametrize(
    "text, message",
    [
        ("name: no-frontmatter", "missing opener"),
        ("---\nname: unfinished", "missing closer"),
        ("---\ndescription: x\n---\nbody", "missing name"),
        ("---\nname: x\n---\nbody", "missing description"),
        ("---\nname x\ndescription: y\n---\nbody", "invalid frontmatter line"),
    ],
)
def test_invalid_frontmatter_fails_fast(tmp_path, text, message):
    path = tmp_path / "invalid" / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")

    with pytest.raises(SkillRegistryError, match=message):
        SkillRegistry.scan(tmp_path)


def test_empty_or_missing_skill_root_starts_without_production_skills(tmp_path):
    assert SkillRegistry.scan(tmp_path).catalog() == ()
    assert SkillRegistry.scan(tmp_path / "missing").catalog() == ()


def test_registry_is_independent_from_prompt_library(tmp_path):
    skill_root = tmp_path / "skills"
    prompt_root = tmp_path / "prompts"
    write_skill(skill_root)
    prompt_root.mkdir()

    skills = SkillRegistry.scan(skill_root)
    prompts = PromptLibrary(prompt_root)

    assert skills.get("example-skill").name == "example-skill"
    assert not hasattr(skills, "render")
    assert not hasattr(prompts, "load")


def test_load_skill_definition_exposes_only_name(tmp_path):
    write_skill(tmp_path)
    tools = ResearcherToolRegistry([LoadSkillTool(SkillRegistry.scan(tmp_path))])

    definition = tools.descriptions()[0]
    properties = definition["arguments_schema"]["properties"]
    assert definition["name"] == "load_skill"
    assert set(properties) == {"name"}


def test_catalog_precedes_lazy_body_and_duplicate_load_does_not_repeat(tmp_path):
    body = "UNIQUE FULL SKILL BODY"
    write_skill(tmp_path, body=body)
    skills = SkillRegistry.scan(tmp_path)
    tools = ResearcherToolRegistry([LoadSkillTool(skills)])
    catalog_fragment = (
        "[AVAILABLE_SKILLS]\n"
        + json.dumps(skills.catalog(), ensure_ascii=False, sort_keys=True)
        + "\n[/AVAILABLE_SKILLS]"
    )
    model = ScriptedModel(
        load_call("call-1"), load_call("call-2"), ModelResponse(content="done")
    )

    result = asyncio.run(
        ToolCallHarness(
            model, tools, context_fragments=(catalog_fragment,)
        ).run(
            system_prompt="system",
            initial_user_message="task",
            scope=scope(),
        )
    )

    initial_text = "\n".join(str(message.content) for message in model.calls[0][0])
    later_text = "\n".join(str(message.content) for message in model.calls[2][0])
    assert "example-skill" in initial_text
    assert body not in initial_text
    assert body in later_text
    assert later_text.count(body) == 1
    results = [event for event in result.trace if event.kind == "tool_result"]
    assert results[0].observation.payload["status"] == "loaded"
    assert results[1].observation.payload == {
        "name": "example-skill",
        "status": "already_loaded",
    }
