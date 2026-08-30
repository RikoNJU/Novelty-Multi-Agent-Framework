"""把数据库无关的检索计划确定性编译为具体数据库查询。"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from ...core.search_plan_expression import (
    SearchPlanExpressionError,
    parse_search_plan_expression,
)
from ...schemas import SearchConcept, SearchPlan

_CONCEPT_ID = re.compile(r"C\d+")


class QueryAdapterError(ValueError):
    """检索计划无法被可靠地编译为数据库查询。"""


@dataclass(frozen=True)
class CompiledQuery:
    """带完整任务追踪信息的一条数据库查询。"""

    database: str
    task_id: str
    novelty_point_id: str
    strategy_id: str
    level: str
    query: str


class QueryAdapter(ABC):
    """数据库查询适配器的模板方法接口。"""

    database: str

    def compile(self, plan: SearchPlan) -> Sequence[CompiledQuery]:
        """按原顺序编译计划中的全部策略，不执行实际检索。"""

        concepts: dict[str, SearchConcept] = {}
        rendered: dict[str, str] = {}
        for concept in plan.concepts:
            if _CONCEPT_ID.fullmatch(concept.concept_id) is None:
                raise QueryAdapterError(f"非法 Concept ID：{concept.concept_id!r}")
            if concept.concept_id in concepts:
                raise QueryAdapterError(f"重复 Concept ID：{concept.concept_id}")
            concepts[concept.concept_id] = concept
            rendered[concept.concept_id] = self._render_concept(concept)

        compiled: list[CompiledQuery] = []
        for strategy in plan.strategies:
            query = self._compile_expression(strategy.expression, rendered)
            compiled.append(
                CompiledQuery(
                    database=self.database,
                    task_id=plan.task_id,
                    novelty_point_id=plan.novelty_point_id,
                    strategy_id=strategy.strategy_id,
                    level=strategy.level,
                    query=query,
                )
            )
        return compiled

    @abstractmethod
    def _render_concept(self, concept: SearchConcept) -> str:
        """把单个语义 Concept 编译为数据库专用查询片段。"""

    @staticmethod
    def _compile_expression(expression: str, concepts: dict[str, str]) -> str:
        try:
            tokens = parse_search_plan_expression(
                expression, defined_concepts=set(concepts)
            )
        except SearchPlanExpressionError as exc:
            raise QueryAdapterError(str(exc)) from exc
        output = [concepts.get(token, token) for token in tokens]
        return " ".join(output).replace("( ", "(").replace(" )", ")")


class AdapterFactory:
    """按数据库名称创建查询适配器。"""

    _adapters: dict[str, type[QueryAdapter]] = {}

    @classmethod
    def create(cls, database: str) -> QueryAdapter:
        normalized = database.strip().lower()
        adapter_type = cls._adapters.get(normalized)
        if adapter_type is None:
            supported = ", ".join(sorted(cls._adapters))
            raise QueryAdapterError(
                f"不支持的检索数据库：{database!r}；当前支持：{supported}"
            )
        return adapter_type()

    @classmethod
    def register(cls, database: str, adapter: type[QueryAdapter]) -> None:
        cls._adapters[database.strip().lower()] = adapter


def compile_search_plan(
    plan: SearchPlan,
    *,
    database: str = "arxiv",
) -> list[CompiledQuery]:
    """通过已注册 Adapter 编译 SearchPlan，不执行查询。"""

    # 兼容旧的默认 arXiv API；延迟加载保证通用模块导入不依赖具体实现。
    if database.strip().lower() == "arxiv" and "arxiv" not in AdapterFactory._adapters:
        from .providers.arxiv import ArxivQueryAdapter

        AdapterFactory.register("arxiv", ArxivQueryAdapter)
    return list(AdapterFactory.create(database).compile(plan))


def _escape_quoted_term(term: str) -> str:
    return term.replace("\\", "\\\\").replace('"', '\\"')
