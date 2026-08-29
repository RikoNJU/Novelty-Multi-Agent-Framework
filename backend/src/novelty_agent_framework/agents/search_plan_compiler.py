"""确定性补全器：把最小模型契约 SearchPlanDraft 编译为运行时 SearchPlan。

设计边界（见 docs/search-planner-optimization.md）：
- LLM 只生成语义载荷（concepts.terms + strategies.expression）；
- 编号、任务绑定、level、name/description 全部由本模块代码补全；
- 本模块不调用 LLM、不访问网络，是可单测的纯函数。
"""

from __future__ import annotations

import re

from ..schemas import ResearchTask, SearchConcept, SearchPlan, SearchStrategy
from ..schemas.search_plan_draft import SearchPlanDraft

CONCEPT_ID_PATTERN = re.compile(r"C\d+")
FORBIDDEN_DATABASE_SYNTAX = re.compile(
    r"(?i)(?:\b(?:abs|ti|all)\s*:|\b(?:SU|TS|AU)\s*=)"
)
LEVELS = ("strict", "medium", "broad")


class SearchPlanCompilationError(ValueError):
    """SearchPlanDraft 无法被可靠地补全为运行时 SearchPlan。"""


def build_runtime_plan(
    draft: SearchPlanDraft,
    *,
    task: ResearchTask,
) -> SearchPlan:
    """把最小模型契约补全为完整运行时 SearchPlan（纯代码，无 LLM）。"""

    _validate_draft(draft, task=task)

    concepts: list[SearchConcept] = []
    for index, concept in enumerate(draft.concepts):
        terms = [term.strip() for term in concept.terms if term.strip()]
        concept_id = f"C{index + 1}"
        concepts.append(
            SearchConcept(
                concept_id=concept_id,
                name=terms[0],
                terms=terms,
            )
        )

    by_id = {concept.concept_id: concept for concept in concepts}
    strategies: list[SearchStrategy] = []
    for index, strategy in enumerate(draft.strategies):
        level = LEVELS[index] if index < len(LEVELS) else LEVELS[-1]
        strategies.append(
            SearchStrategy(
                strategy_id=f"S{index + 1}",
                level=level,
                expression=strategy.expression.strip(),
                description=_describe(strategy.expression, by_id),
            )
        )

    return SearchPlan(
        task_id=task.task_id,
        novelty_point_id=task.novelty_point_id,
        concepts=concepts,
        strategies=strategies,
    )


def _validate_draft(draft: SearchPlanDraft, *, task: ResearchTask) -> None:
    if not draft.concepts:
        raise SearchPlanCompilationError("SearchPlanDraft 必须包含至少一个概念")
    if not draft.strategies:
        raise SearchPlanCompilationError("SearchPlanDraft 必须包含至少一条策略")

    for concept in draft.concepts:
        if not any(term.strip() for term in concept.terms):
            raise SearchPlanCompilationError("SearchPlanDraft 存在空词项概念")

    concept_ids = {f"C{index + 1}" for index in range(len(draft.concepts))}
    for strategy in draft.strategies:
        expression = strategy.expression.strip()
        if not expression:
            raise SearchPlanCompilationError("SearchPlanDraft 存在空表达式策略")
        if FORBIDDEN_DATABASE_SYNTAX.search(expression):
            raise SearchPlanCompilationError(
                f"SearchStrategy {expression!r} 包含数据库专用语法"
            )
        referenced = set(CONCEPT_ID_PATTERN.findall(expression))
        undefined = sorted(referenced - concept_ids)
        if undefined:
            raise SearchPlanCompilationError(
                f"SearchPlan 引用了未定义 Concept：{', '.join(undefined)}"
            )

    if task.task_type == "literature_search" and len(draft.strategies) != 3:
        raise SearchPlanCompilationError(
            "普通 literature_search 任务必须恰好生成三条策略（strict/medium/broad）"
        )


def _describe(expression: str, by_id: dict[str, SearchConcept]) -> str:
    """把表达式中的概念 ID 替换为概念名，生成可读描述。"""

    return re.sub(
        CONCEPT_ID_PATTERN,
        lambda match: by_id[match.group(0)].name,
        expression,
    )
