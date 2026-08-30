"""SearchPlanner Agent：把查新点和调研任务转换为数据库无关的检索计划。"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from backend.env import (
    ChatMessage,
    ModelCallOptions,
    ModelClient,
    ModelRegistry,
    PromptLibrary,
)

from ..core.search_plan_expression import (
    SearchPlanExpressionError,
    parse_search_plan_expression,
)
from ..ports import SearchPlanner
from ..schemas import NoveltyPoint, ResearchTask, SearchPlan

CONCEPT_ID_PATTERN = re.compile(r"C\d+")
STRATEGY_ID_PATTERN = re.compile(r"S\d+")
FORBIDDEN_DATABASE_SYNTAX = re.compile(
    r"(?i)(?:\b(?:abs|ti|all)\s*:|\b(?:SU|TS|AU)\s*=)"
)


class SearchPlannerAgent(SearchPlanner):
    """用 LLM 生成数据库无关 SearchPlan，并执行确定性语义校验。"""

    def __init__(
        self,
        model_client: ModelClient | None = None,
        *,
        prompts: PromptLibrary | None = None,
        models: ModelRegistry | None = None,
        model_alias: str | None = None,
        temperature: float = 0.2,
        model_options: ModelCallOptions | None = None,
        max_attempts: int = 2,
        prompt_name: str = "search_planner/plan",
    ) -> None:
        self.model_client = model_client
        self._prompts = prompts
        self._models = models
        self._model_alias = model_alias
        self.temperature = temperature
        self.model_options = model_options or ModelCallOptions(
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        self.max_attempts = max_attempts
        self.prompt_name = prompt_name

    def plan(self, point: NoveltyPoint, task: ResearchTask) -> SearchPlan:
        """将 NoveltyPoint + ResearchTask 转换为经过校验的 SearchPlan。"""

        if task.novelty_point_id != point.point_id:
            raise ValueError(
                "ResearchTask.novelty_point_id 与 NoveltyPoint.point_id 不一致"
            )

        last_error: ValueError | None = None
        for attempt_index in range(self.max_attempts):
            try:
                data = self._complete_json(
                    point=point,
                    task=task,
                    retry_reason=str(last_error) if last_error else "",
                )
                plan = _validate_plan_data(data)
                _validate_plan_semantics(plan, point=point, task=task)
                _validate_plan_expressions(plan)
                return plan
            except ValueError as exc:
                last_error = exc
                if attempt_index + 1 >= self.max_attempts:
                    break
        raise ValueError(
            f"SearchPlanner {self.max_attempts} 次生成均失败：{last_error or '未知错误'}"
        ) from last_error

    def _complete_json(
        self,
        *,
        point: NoveltyPoint,
        task: ResearchTask,
        retry_reason: str,
    ) -> Any:
        payload = {
            "point": point.model_dump(mode="json"),
            "task": task.model_dump(mode="json"),
            "retry_reason": retry_reason,
        }
        variables = {
            "point_json": json.dumps(payload["point"], ensure_ascii=False),
            "task_json": json.dumps(payload["task"], ensure_ascii=False),
            "search_plan_schema": json.dumps(
                SearchPlan.model_json_schema(), ensure_ascii=False
            ),
            "retry_reason": retry_reason or "无（首次生成）",
        }
        if self._prompts is not None:
            rendered = self._prompts.render(self.prompt_name, **variables)
            system, user = rendered.system, rendered.user
        else:
            system = self._system_prompt()
            user = (
                "请把输入转换为数据库无关的 SearchPlan JSON。"
                "不得输出数据库字段语法。\n\n输入：\n"
                f"{json.dumps(payload, ensure_ascii=False)}\n\n"
                f"输出 schema：\n{variables['search_plan_schema']}"
            )

        response = self._client().complete(
            [
                ChatMessage(role="system", content=system),
                ChatMessage(role="user", content=user),
            ],
            options=self.model_options,
        )
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ValueError("SearchPlanner 返回内容不是合法 JSON") from exc

    def _client(self) -> ModelClient:
        if self.model_client is not None:
            return self.model_client
        if self._models is not None:
            return self._models.client_for(self._model_alias or "search_planner")
        raise NotImplementedError(
            "SearchPlannerAgent 需要注入 ModelClient 或 ModelRegistry"
        )

    @staticmethod
    def _system_prompt() -> str:
        return (
            "你是科技查新系统中的 SearchPlanner。你只把 NoveltyPoint 和 "
            "ResearchTask 转换为数据库无关的 SearchPlan。你负责提取核心概念、"
            "规范词项、保守扩展同义词并建立逻辑策略；不能检索文献、编造来源或"
            "输出任何数据库专用语法。"
        )


def _validate_plan_data(data: Any) -> SearchPlan:
    if isinstance(data, dict) and isinstance(data.get("search_plan"), dict):
        data = data["search_plan"]
    if not isinstance(data, dict):
        raise ValueError("SearchPlanner 输出顶层必须是 SearchPlan 对象")
    try:
        return SearchPlan.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"SearchPlanner 输出不符合 SearchPlan schema：{exc}") from exc


def _validate_plan_semantics(
    plan: SearchPlan,
    *,
    point: NoveltyPoint,
    task: ResearchTask,
) -> None:
    if plan.task_id != task.task_id:
        raise ValueError("SearchPlan.task_id 与输入 ResearchTask 不一致")
    if plan.novelty_point_id != point.point_id:
        raise ValueError("SearchPlan.novelty_point_id 与输入 NoveltyPoint 不一致")
    if plan.novelty_point_id != task.novelty_point_id:
        raise ValueError("SearchPlan 与 ResearchTask 的 novelty_point_id 不一致")

    concept_ids = [concept.concept_id for concept in plan.concepts]
    _validate_ids(concept_ids, pattern=CONCEPT_ID_PATTERN, kind="Concept")
    strategy_ids = [strategy.strategy_id for strategy in plan.strategies]
    _validate_ids(strategy_ids, pattern=STRATEGY_ID_PATTERN, kind="Strategy")

    for strategy in plan.strategies:
        if FORBIDDEN_DATABASE_SYNTAX.search(strategy.expression):
            raise ValueError(
                f"SearchStrategy {strategy.strategy_id} 包含数据库专用语法"
            )

    if task.task_type == "literature_search":
        levels = [strategy.level for strategy in plan.strategies]
        if levels != ["strict", "medium", "broad"]:
            raise ValueError(
                "普通 literature_search 任务必须按 strict、medium、broad "
                "顺序生成三条策略"
            )


def _validate_plan_expressions(plan: SearchPlan) -> None:
    defined_concepts = {concept.concept_id for concept in plan.concepts}
    for strategy in plan.strategies:
        try:
            parse_search_plan_expression(
                strategy.expression,
                defined_concepts=defined_concepts,
            )
        except SearchPlanExpressionError as exc:
            raise SearchPlanExpressionError(
                "invalid_expression_grammar: "
                f"strategy {strategy.strategy_id}: {exc}"
            ) from exc


def _validate_ids(
    values: list[str],
    *,
    pattern: re.Pattern[str],
    kind: str,
) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"SearchPlan 中存在重复 {kind} ID")
    invalid = [value for value in values if pattern.fullmatch(value) is None]
    if invalid:
        raise ValueError(
            f"SearchPlan 中存在非法 {kind} ID：{', '.join(invalid)}"
        )
