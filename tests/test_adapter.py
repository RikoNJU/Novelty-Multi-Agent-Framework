from __future__ import annotations

import pytest

from novelty_agent_framework.schemas import SearchConcept, SearchPlan, SearchStrategy
from novelty_agent_framework.tools.database_search import (
    AdapterFactory,
    QueryAdapterError,
    compile_search_plan,
)
from novelty_agent_framework.tools.database_search.providers.arxiv import ArxivQueryAdapter


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

    assert result[0].query == (
        "all:dynamic AND all:graph AND all:neural AND all:network"
    )
    assert (
        result[0].database,
        result[0].task_id,
        result[0].novelty_point_id,
        result[0].strategy_id,
        result[0].level,
    ) == ("arxiv", "T1", "NP1", "S1", "strict")




def test_short_terms_stay_quoted_phrases_in_v2() -> None:
    plan = _plan(
        concepts=[
            SearchConcept(concept_id="C1", name="gnn", terms=["graph neural network"])
        ]
    )
    assert compile_search_plan(plan)[0].query == 'all:"graph neural network"'


def test_long_terms_split_to_word_level_and_in_v2() -> None:
    plan = _plan(
        concepts=[
            SearchConcept(
                concept_id="C1", name="gnn",
                terms=["graph neural network distributed training"],
            )
        ]
    )
    assert compile_search_plan(plan)[0].query == (
        "all:graph AND all:neural AND all:network AND all:distributed AND all:training"
    )


def test_v1_mode_keeps_quoted_phrases_for_long_terms() -> None:
    adapter = ArxivQueryAdapter(render_v2=False)
    plan = _plan(
        concepts=[
            SearchConcept(
                concept_id="C1", name="gnn", terms=["dynamic graph neural network"]
            )
        ]
    )
    assert adapter.compile(plan)[0].query == 'all:"dynamic graph neural network"'


def test_build_arxiv_source_honors_render_v2_config() -> None:
    from novelty_agent_framework.tools.database_search.providers.arxiv import (
        build_arxiv_source,
    )

    source = build_arxiv_source({"enabled": False, "render_v2": False})
    plan = _plan(
        concepts=[
            SearchConcept(
                concept_id="C1", name="gnn", terms=["dynamic graph neural network"]
            )
        ]
    )
    assert source.query_adapter.compile(plan)[0].query == 'all:"dynamic graph neural network"'

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
        "(all:dynamic AND all:graph AND all:neural AND all:network OR "
        "all:temporal AND all:graph AND all:neural AND all:network OR "
        'all:"dynamic \\"GNN\\"")'
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


def test_role_fields_map_to_arxiv_fields() -> None:
    concepts = [
        SearchConcept(concept_id="C1", name="obj", terms=["graph summarization"], role="object"),
        SearchConcept(concept_id="C2", name="m", terms=["graph neural network"], role="method"),
        SearchConcept(concept_id="C3", name="e", terms=["communication efficient learning"], role="escape"),
    ]
    plan = _plan(concepts=concepts, expressions=[("S1", "strict", "C1 AND C2 AND C3")])
    assert compile_search_plan(plan)[0].query == (
        'ti:"graph summarization" AND abs:"graph neural network" AND '
        'all:"communication efficient learning"'
    )


def test_alias_expands_only_when_use_alias() -> None:
    concept = SearchConcept(
        concept_id="C1",
        name="obj",
        terms=["graph summarization"],
        alias=["graph condensation"],
        role="object",
    )
    plan = SearchPlan(
        task_id="T1",
        novelty_point_id="NP1",
        concepts=[concept],
        strategies=[
            SearchStrategy(strategy_id="S1", level="strict", expression="C1"),
            SearchStrategy(
                strategy_id="S2", level="medium", expression="C1", use_alias=True
            ),
            SearchStrategy(
                strategy_id="S3", level="broad", expression="C1", use_alias=True
            ),
        ],
    )
    compiled = compile_search_plan(plan)
    assert compiled[0].query == 'ti:"graph summarization"'
    assert compiled[1].query == (
        '(ti:"graph summarization" OR ti:"graph condensation")'
    )
    assert compiled[2].query == compiled[1].query


def test_exclude_terms_render_as_andnot() -> None:
    concept = SearchConcept(
        concept_id="C1",
        name="obj",
        terms=["graph summarization"],
        exclude=["survey"],
        role="object",
    )
    plan = SearchPlan(
        task_id="T1",
        novelty_point_id="NP1",
        concepts=[concept],
        strategies=[SearchStrategy(strategy_id="S1", level="strict", expression="C1")],
    )
    assert compile_search_plan(plan)[0].query == 'ti:"graph summarization" ANDNOT (all:"survey")'


def test_v2_long_term_word_level_respects_field() -> None:
    concept = SearchConcept(
        concept_id="C1",
        name="obj",
        terms=["graph summarization distributed training"],
        role="object",
    )
    plan = SearchPlan(
        task_id="T1",
        novelty_point_id="NP1",
        concepts=[concept],
        strategies=[SearchStrategy(strategy_id="S1", level="strict", expression="C1")],
    )
    assert compile_search_plan(plan)[0].query == (
        "ti:graph AND ti:summarization AND ti:distributed AND ti:training"
    )
