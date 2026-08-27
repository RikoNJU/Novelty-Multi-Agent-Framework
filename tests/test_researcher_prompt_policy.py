from pathlib import Path

from backend.env import PromptLibrary


PROMPTS_ROOT = Path("backend/src/novelty_agent_framework/prompts")


def render_prompt():
    return PromptLibrary(PROMPTS_ROOT).render(
        "research/native_tool_loop",
        novelty_point_json='{"point_id":"NP-1"}',
        research_task_json='{"task_id":"T-1","language":"zh"}',
        finish_schema_json='{"type":"object"}',
    )


def test_researcher_prompt_renders_attempt3_retrieval_policy() -> None:
    rendered = render_prompt()

    assert rendered.version == "2"
    assert "Prefer database_search as the primary discovery tool" in rendered.system
    assert "For Chinese-language research tasks" in rendered.system
    assert "Search results and snippets are discovery metadata, not evidence" in rendered.system
    assert "Never issue consecutive web_search calls" in rendered.system
    assert "read it directly with reader" in rendered.system
    assert "Do not decide whether a source is evidentiary based only on search snippets" in rendered.system


def test_researcher_prompt_renders_exact_quote_and_empty_finish_policy() -> None:
    system = render_prompt().system

    assert "copied verbatim from a successful Reader observation" in system
    assert "Do not paraphrase, summarize, translate, normalize, rewrite" in system
    assert "exact supporting span in Reader text" in system
    assert "cards=[] and a concrete no_evidence_reason" in system
    assert "Never force a card" in system
