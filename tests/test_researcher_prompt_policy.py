from pathlib import Path

from backend.env import PromptLibrary

from novelty_agent_framework.schemas import NoveltyPoint
from novelty_agent_framework.workflows.research_task import _project_novelty_point


PROMPTS_ROOT = Path("backend/src/novelty_agent_framework/prompts")


def render_prompt():
    return PromptLibrary(PROMPTS_ROOT).render(
        "research/native_tool_loop",
        novelty_point_json='{"point_id":"NP-1"}',
        research_task_json='{"task_id":"T-1","language":"zh"}',
        search_plan_json='{"concepts":[{"terms":["term"]}],"strategies":[{"expression":"C1"}]}',
        finish_schema_json='{"type":"object"}',
    )


def test_researcher_prompt_renders_database_only_retrieval_policy() -> None:
    rendered = render_prompt()

    assert rendered.version == "4"
    assert "Rely on database_search as the discovery tool" in rendered.system
    assert "revise the query terms taken from the SearchPlan" in rendered.system
    assert "Search results and snippets are discovery metadata, not evidence" in rendered.system
    assert "Never guess an\nunlisted database source_id" in rendered.system
    assert (
        "the next tool\ncall MUST be reader for one returned artifact_id"
        in rendered.system
    )
    assert (
        "Do not call database_search\nagain until that Artifact has been read"
        in rendered.system
    )
    assert "When reference_search is available" in rendered.system
    assert "Do not decide whether a source is evidentiary based only on search snippets" in rendered.system


def test_researcher_prompt_prefers_abstract_artifact_and_reserves_finish_budget() -> None:
    """回归守卫（v4）：优先读摘要制品，且必须留预算交 finish。

    实测背景（MF2033k6lC run 0010/0011）：模型在扁平 artifact_ids 里盲选到
    107K 字符的全文，连续翻页耗尽 reader 预算后被 harness 硬中断，三轮 0 证据卡。
    """

    system = render_prompt().system

    assert "Prefer an id listed in abstract_artifact_ids" in system
    assert "the reading budget before you can finish" in system
    assert "keep the number of pages per artifact small" in system
    assert "If a budget warning appears" in system
    assert "emit the finish JSON for the evidence you already have" in system


def test_researcher_prompt_excludes_web_search_and_browser_policy() -> None:
    """回归守卫：v3 起不再向 Researcher 暴露 web_search / browser 策略。"""

    system = render_prompt().system.lower()

    assert "web_search" not in system
    assert "web search" not in system
    assert "browser" not in system


def test_researcher_prompt_renders_exact_quote_and_empty_finish_policy() -> None:
    system = render_prompt().system

    assert "copied verbatim from a successful Reader observation" in system
    assert "Do not paraphrase, summarize, translate, normalize, rewrite" in system
    assert "exact supporting span in Reader text" in system
    assert "cards=[] and a concrete no_evidence_reason" in system
    assert "Never force a card" in system


def test_novelty_point_projection_hides_source_locations() -> None:
    """回归守卫：source_locations 不保证逐字，不能暴露给 Researcher。

    PointExtractor 会顺手清理 PDF 抽取残留（实测把论文里的
    ``(model F _ { 2 } ) ) )`` 从引文中间去掉），于是 source_locations 里的
    「引文」并不逐字。模型看到这种带引号、还标了章节的现成字符串，会直接当作
    引文写进 finish draft，随后必然被判 ungrounded——引文只能来自成功的 Reader 观测。
    """

    point = NoveltyPoint(
        point_id="NP-1",
        claim="推理能力主要来自 o_proj",
        technical_features=["Delta Stethoscope"],
        source_locations=[
            "Section 2.3: 'simply tuning o_proj and layernorm leads to strong "
            "reasoning ability'"
        ],
    )

    projected = _project_novelty_point(point)

    assert "source_locations" not in projected
    assert projected["claim"] == "推理能力主要来自 o_proj"
    assert projected["technical_features"] == ["Delta Stethoscope"]
    assert projected["point_id"] == "NP-1"
