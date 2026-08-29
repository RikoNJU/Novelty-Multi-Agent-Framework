"""SearchPlanner 的最小模型契约。

只包含必须由 LLM 生成的语义载荷（concepts.terms + strategies.expression）。
运行时 SearchPlan 的机械字段（concept_id、strategy_id、task_id、
novelty_point_id、level、name、description）由
agents/search_plan_compiler.build_runtime_plan 确定性补全。
"""

from __future__ import annotations

from pydantic import Field

from .domain import StrictModel


class SearchConceptDraft(StrictModel):
    """一个语义概念及其词项；concept_id 由系统按顺序分配 C1..Cn。"""

    terms: list[str] = Field(min_length=1)


class SearchStrategyDraft(StrictModel):
    """一条检索策略；strategy_id 与 level 由系统按顺序分配。"""

    expression: str = Field(min_length=1)


class SearchPlanDraft(StrictModel):
    """LLM 输出的最小检索计划。

    约定：
    - concepts 按顺序编号为 C1..Cn（expression 按此引用）；
    - strategies 按顺序编号为 S1..Sn，level 按位置标注 strict/medium/broad；
    - literature_search 任务必须恰好三条策略。
    """

    concepts: list[SearchConceptDraft] = Field(min_length=1)
    strategies: list[SearchStrategyDraft] = Field(min_length=1)
