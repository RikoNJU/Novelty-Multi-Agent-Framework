"""SearchPlanner Agent：把查新点和调研任务转换为数据库无关的检索计划。

模型只输出最小契约 SearchPlanDraft（concepts.terms + strategies.expression）；
机械字段（concept_id/strategy_id/task_id/novelty_point_id/level/name/description）
由 search_plan_compiler.build_runtime_plan 确定性补全，模型不参与生成。
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from backend.env import (
    ChatMessage,
    ModelCallOptions,
    ModelClient,
    ModelRegistry,
    PromptLibrary,
)

from ..ports import SearchPlanner
from ..schemas import NoveltyPoint, ResearchTask, SearchPlan, SearchPlanDraft
from .search_plan_compiler import build_runtime_plan


class SearchPlannerAgent(SearchPlanner):
    """用 LLM 生成最小契约 SearchPlanDraft，并补全为运行时 SearchPlan。"""

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
        """将 NoveltyPoint + ResearchTask 转换为经过补全的运行时 SearchPlan。"""

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
                draft = _validate_draft_data(data)
                return build_runtime_plan(draft, task=task)
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
            "draft_schema": json.dumps(
                SearchPlanDraft.model_json_schema(), ensure_ascii=False
            ),
            "retry_reason": retry_reason or "无（首次生成）",
        }
        if self._prompts is not None:
            rendered = self._prompts.render(self.prompt_name, **variables)
            system, user = rendered.system, rendered.user
        else:
            system = self._system_prompt()
            user = (
                "请把输入转换为数据库无关的 SearchPlanDraft JSON。"
                "不得输出数据库字段语法，也不得输出 concept_id/strategy_id/"
                "level/description/task_id/novelty_point_id 等系统分配字段。\n\n输入：\n"
                f"{json.dumps(payload, ensure_ascii=False)}\n\n"
                f"输出 schema：\n{variables['draft_schema']}"
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
            "ResearchTask 转换为最小检索草稿 SearchPlanDraft：概念词项 terms 与"
            "策略组合 expression（引用 C1..Cn，编号按 concepts 顺序由系统分配）。"
            "不能检索文献、编造来源、输出数据库专用语法，也不能输出任何系统分配"
            "字段（concept_id/strategy_id/level/description/task_id/novelty_point_id）。"
        )


def _validate_draft_data(data: Any) -> SearchPlanDraft:
    if isinstance(data, dict) and isinstance(data.get("search_plan"), dict):
        data = data["search_plan"]
    if not isinstance(data, dict):
        raise ValueError("SearchPlanner 输出顶层必须是 SearchPlanDraft 对象")
    try:
        return SearchPlanDraft.model_validate(data)
    except ValidationError as exc:
        raise ValueError(
            f"SearchPlanner 输出不符合 SearchPlanDraft schema：{exc}"
        ) from exc
