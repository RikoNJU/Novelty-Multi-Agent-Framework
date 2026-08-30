from __future__ import annotations

import pytest

from novelty_agent_framework.core.search_plan_expression import (
    SearchPlanExpressionError,
    parse_search_plan_expression,
)


@pytest.mark.parametrize(
    "expression",
    [
        "C1",
        "C1 AND C2",
        "C1 OR C2",
        "C1 AND (C2 OR C3)",
        "(C1 OR C2) AND C3",
        "(C1 AND C2) OR (C3 AND C4)",
    ],
)
def test_valid_expressions_return_tokens(expression: str) -> None:
    tokens = parse_search_plan_expression(
        expression, defined_concepts={"C1", "C2", "C3", "C4"}
    )

    assert tokens
    assert "".join(tokens).replace("AND", "").replace("OR", "")


@pytest.mark.parametrize(
    "expression",
    [
        "C1 AND dynamic",
        "C1 && C2",
        "C1 C2",
        "C1 AND AND C2",
        "AND C1",
        "OR C1",
        "C1 AND",
        "C1 OR",
        "C1 AND (C2",
        "C1 AND C2)",
        "()",
        "C1 AND ()",
    ],
)
def test_invalid_expressions_are_rejected(expression: str) -> None:
    with pytest.raises(SearchPlanExpressionError):
        parse_search_plan_expression(
            expression, defined_concepts={"C1", "C2", "C3", "C4"}
        )


def test_undefined_concept_is_rejected() -> None:
    with pytest.raises(SearchPlanExpressionError, match="未定义 Concept：C3"):
        parse_search_plan_expression(
            "C1 AND C3", defined_concepts={"C1", "C2"}
        )
