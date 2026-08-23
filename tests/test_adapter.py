from __future__ import annotations

import pytest

from novelty_agent_framework.schemas import SearchConcept, SearchPlan, SearchStrategy
from novelty_agent_framework.tools import (
    AdapterFactory,
    ArxivQueryAdapter,
    QueryAdapterError,
    compile_search_plan,
)


def _plan(
    *,
    concepts: list[SearchConcept] | None = None,
    expressions: list[tuple[str, str, str]] | None = None,
) -> SearchPlan:
    return SearchPlan(
        task_id="T1",
        novelty_point_id="NP1",
        concepts=concepts
        or [
            SearchConcept(
                concept_id="C1",
                name="dynamic graph",
                terms=["dynamic graph neural network"],
            )
        ],
        strategies=[
            SearchStrategy(strategy_id=strategy_id, level=level, expression=expression)
            for strategy_id, level, expression in (
                expressions or [("S1", "strict", "C1")]
            )
        ],
    )


def test_single_concept_single_term_and_tracking_fields() -> None:
    result = compile_search_plan(_plan())

    assert result[0].query == 'all:"dynamic graph neural network"'
    assert (
        result[0].database,
        result[0].task_id,
        result[0].novelty_point_id,
        result[0].strategy_id,
        result[0].level,
    ) == ("arxiv", "T1", "NP1", "S1", "strict")


def test_multiple_terms_are_normalized_deduplicated_and_or_joined() -> None:
    plan = _plan(
        concepts=[
            SearchConcept(
                concept_id="C1",
                name="dynamic graph",
                terms=[
                    " dynamic   graph neural network ",
                    "temporal graph neural network",
                    "dynamic graph neural network",
                    'dynamic "GNN"',
                ],
            )
        ]
    )

    assert compile_search_plan(plan)[0].query == (
        '(all:"dynamic graph neural network" OR '
        'all:"temporal graph neural network" OR all:"dynamic \\"GNN\\"")'
    )


def test_concepts_and_parentheses_preserve_boolean_logic() -> None:
    concepts = [
        SearchConcept(concept_id="C1", name="one", terms=["one", "first"]),
        SearchConcept(concept_id="C2", name="two", terms=["two"]),
        SearchConcept(concept_id="C3", name="three", terms=["three"]),
    ]
    query = compile_search_plan(
        _plan(concepts=concepts, expressions=[("S1", "strict", "C1 AND (C2 OR C3)")])
    )[0].query

    assert query == (
        '(all:"one" OR all:"first") AND '
        '(all:"two" OR all:"three")'
    )


def test_strategy_order_is_preserved() -> None:
    plan = _plan(
        expressions=[
            ("S1", "strict", "C1"),
            ("S2", "medium", "C1"),
            ("S3", "broad", "C1"),
        ]
    )
    assert [item.strategy_id for item in compile_search_plan(plan)] == ["S1", "S2", "S3"]


def test_concept_id_prefixes_are_tokenized_independently() -> None:
    plan = _plan(
        concepts=[
            SearchConcept(concept_id="C1", name="one", terms=["one"]),
            SearchConcept(concept_id="C10", name="ten", terms=["ten"]),
        ],
        expressions=[("S1", "strict", "C10 OR C1")],
    )
    assert compile_search_plan(plan)[0].query == 'all:"ten" OR all:"one"'


@pytest.mark.parametrize(
    ("expression", "message"),
    [
        ("C1 AND C999", "未定义 Concept"),
        ("C1 NEAR C1", "不支持的 token"),
        ("C1 AND (C1 OR C1", "括号不平衡"),
        ("C1 C1", "缺少 AND/OR"),
    ],
)
def test_invalid_expressions_are_rejected(expression: str, message: str) -> None:
    with pytest.raises(QueryAdapterError, match=message):
        compile_search_plan(_plan(expressions=[("S1", "strict", expression)]))


def test_blank_term_is_rejected() -> None:
    plan = _plan(
        concepts=[SearchConcept(concept_id="C1", name="one", terms=["one", "   "])]
    )
    with pytest.raises(QueryAdapterError, match="空 term"):
        compile_search_plan(plan)


def test_adapter_factory_normalizes_name_and_rejects_unsupported_database() -> None:
    assert isinstance(AdapterFactory.create(" ArXiV "), ArxivQueryAdapter)
    with pytest.raises(QueryAdapterError, match="当前支持：arxiv"):
        AdapterFactory.create("cnki")
