"""SearchPlan 补全器（build_runtime_plan）的独立单测。"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from novelty_agent_framework.agents.search_plan_compiler import (
    SearchPlanCompilationError,
    build_runtime_plan,
)
from novelty_agent_framework.schemas import ResearchTask
from novelty_agent_framework.schemas.search_plan_draft import (
    SearchConceptDraft,
    SearchPlanDraft,
    SearchStrategyDraft,
)


def make_task(task_type: str = "literature_search") -> ResearchTask:
    return ResearchTask(
        task_id="T-1",
        novelty_point_id="NP-1",
        task_type=task_type,
        language="zh",
        description="针对该查新点执行中文文献检索。",
        attempt=1,
    )


def make_draft(*, concepts=None, strategies=None) -> SearchPlanDraft:
    concepts = concepts or [
        ["图自编码器", "graph autoencoder", "GAE"],
        ["循环神经网络", "RNN", "recurrent neural network"],
        ["动态时序图处理", "sequential graph processing"],
    ]
    strategies = strategies or [
        "C1 AND C2 AND C3",
        "C1 AND C2",
        "(C1 OR C2 OR C3)",
    ]
    return SearchPlanDraft(
        concepts=[SearchConceptDraft(terms=terms) for terms in concepts],
        strategies=[SearchStrategyDraft(expression=expr) for expr in strategies],
    )


def test_runtime_plan_injects_identity_and_ids():
    plan = build_runtime_plan(make_draft(), task=make_task())
    assert plan.task_id == "T-1"
    assert plan.novelty_point_id == "NP-1"
    assert [c.concept_id for c in plan.concepts] == ["C1", "C2", "C3"]
    assert [c.name for c in plan.concepts] == ["图自编码器", "循环神经网络", "动态时序图处理"]
    assert [s.strategy_id for s in plan.strategies] == ["S1", "S2", "S3"]


def test_levels_assigned_by_position():
    plan = build_runtime_plan(make_draft(), task=make_task())
    assert [s.level for s in plan.strategies] == ["strict", "medium", "broad"]


def test_partial_strategies_use_prefix_levels():
    draft = make_draft(strategies=["C1", "C1 AND C2"])
    plan = build_runtime_plan(draft, task=make_task(task_type="feature_supplement"))
    assert [s.level for s in plan.strategies] == ["strict", "medium"]


def test_fourth_strategy_falls_back_to_broad():
    draft = make_draft(
        strategies=["C1", "C1 AND C2", "C1 OR C2 OR C3", "(C1 OR C2 OR C3) AND C1"]
    )
    plan = build_runtime_plan(draft, task=make_task(task_type="feature_supplement"))
    assert [s.level for s in plan.strategies] == ["strict", "medium", "broad", "broad"]


def test_description_uses_concept_names():
    plan = build_runtime_plan(make_draft(), task=make_task())
    assert plan.strategies[0].description == "图自编码器 AND 循环神经网络 AND 动态时序图处理"


def test_terms_are_normalized():
    draft = make_draft(concepts=[[" 图摘要 ", "图摘要 ", ""]], strategies=["C1"])
    plan = build_runtime_plan(draft, task=make_task(task_type="feature_supplement"))
    assert plan.concepts[0].terms == ["图摘要", "图摘要"]
    assert plan.concepts[0].name == "图摘要"


def test_rejects_empty_terms():
    draft = SearchPlanDraft(
        concepts=[SearchConceptDraft(terms=["", " "])],
        strategies=[SearchStrategyDraft(expression="C1")],
    )
    with pytest.raises(SearchPlanCompilationError, match="空词项"):
        build_runtime_plan(draft, task=make_task())


def test_rejects_undefined_concept_reference():
    draft = make_draft(strategies=["C1 AND C9"])
    with pytest.raises(SearchPlanCompilationError, match="未定义 Concept"):
        build_runtime_plan(draft, task=make_task())


def test_rejects_database_syntax():
    draft = make_draft(strategies=['all:"图自编码器"'])
    with pytest.raises(SearchPlanCompilationError, match="数据库专用语法"):
        build_runtime_plan(draft, task=make_task())


def test_rejects_wrong_strategy_count_for_literature_search():
    draft = make_draft(strategies=["C1"])
    with pytest.raises(SearchPlanCompilationError, match="三条策略"):
        build_runtime_plan(draft, task=make_task())


def test_supplement_tasks_allow_fewer_strategies():
    draft = make_draft(strategies=["C1 AND C2"])
    plan = build_runtime_plan(draft, task=make_task(task_type="feature_supplement"))
    assert len(plan.strategies) == 1
    assert plan.strategies[0].level == "strict"


def test_draft_schema_requires_at_least_one_concept():
    with pytest.raises(ValidationError):
        SearchPlanDraft(
            concepts=[],
            strategies=[SearchStrategyDraft(expression="C1")],
        )
