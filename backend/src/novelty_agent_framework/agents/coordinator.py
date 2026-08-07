"""查新主 Agent。

该文件只描述主 Agent 如何组织论文理解、查新点拆解、补充检索规划和
最终查新结论汇总。真实模型、模型供应商和 API 调用方式由 `backend.env`
统一提供，避免不同开发者在 Agent 内部各写一套模型调用代码。
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

from pydantic import ValidationError

from backend.env import (
    ChatMessage,
    ModelCallOptions,
    ModelClient,
    ModelRegistry,
    PromptLibrary,
)
from ..schemas import (
    EvidenceCard,
    NoveltyBrief,
    NoveltyPoint,
    NoveltyReport,
    PaperInput,
    ResearchTask,
)
from ..ports import NoveltyCoordinator


class NoveltyCoordinatorAgent(NoveltyCoordinator):
    """负责查新任务中的全局判断和信息汇总。

    它是查新 Multi-Agent 的主 Agent，但不直接检索文献，也不直接校验证据。
    它的职责是：

    1. 读取论文输入，拆出需要被查证的创新点；
    2. 把创新点转化为可并行执行的文献调研任务；
    3. 根据证据缺口安排补充检索；
    4. 汇总 Research Agent 和 Evidence Validator 的结果，形成报告。
    """

    def __init__(
        self,
        model_client: ModelClient | None = None,
        *,
        prompts: PromptLibrary | None = None,
        models: ModelRegistry | None = None,
        model_alias: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        self.model_client = model_client
        self._prompts = prompts
        self._models = models
        self._model_alias = model_alias
        self.temperature = temperature

    def plan(
        self,
        paper: PaperInput,
        *,
        points: Sequence[NoveltyPoint],
        attempt: int,
    ) -> NoveltyBrief:
        """把查新点转化为调研任务并组装查新规划。

        查新点由提取 Agent 预先生成；本方法只负责任务分配与 NoveltyBrief 装配。
        """

        payload = {
            "paper": paper.model_dump(mode="json"),
            "points": [point.model_dump(mode="json") for point in points],
            "attempt": attempt,
        }
        data = self._complete_json(
            prompt_name="coordinator/plan",
            variables={
                "paper_json": json.dumps(payload["paper"], ensure_ascii=False),
                "points_json": json.dumps(payload["points"], ensure_ascii=False),
                "attempt": attempt,
                "task_schema": json.dumps(
                    ResearchTask.model_json_schema(), ensure_ascii=False
                ),
            },
            payload=payload,
            system_prompt=self._system_prompt(),
            fallback_user_prompt=(
                "请为给定查新点生成 ResearchTask 列表（JSON 数组）。"
            ),
        )
        if not isinstance(data, list):
            raise ValueError("Coordinator plan 输出顶层必须是 ResearchTask 列表")
        allowed_ids = {point.point_id for point in points}
        tasks: list[ResearchTask] = []
        for index, item in enumerate(data):
            try:
                task = ResearchTask.model_validate(item)
            except ValidationError as exc:
                raise ValueError(f"plan 第 {index + 1} 个任务格式错误：{exc}") from exc
            if task.novelty_point_id not in allowed_ids:
                raise ValueError(
                    f"plan 任务 {task.task_id} 引用了未知查新点 {task.novelty_point_id}"
                )
            tasks.append(task)
        return NoveltyBrief(
            paper_summary=paper.abstract or paper.title,
            research_problem=paper.title,
            novelty_points=list(points),
            keywords_zh=[paper.title] if paper.title else [],
            keywords_en=[],
            research_tasks=tasks,
        )

    def plan_supplement(
        self,
        paper: PaperInput,
        *,
        brief: NoveltyBrief,
        existing_evidence: Sequence[EvidenceCard],
        coverage_gaps: Sequence[str],
        attempt: int,
    ) -> NoveltyBrief:
        """针对证据不足的查新点生成补充调研任务。

        该函数只处理缺口，不重新推翻上一轮 `brief`。这样可以避免一次补检
        导致整个查新任务漂移，也能控制运行成本。
        """

        payload = {
            "paper": paper.model_dump(mode="json"),
            "brief": brief.model_dump(mode="json"),
            "existing_evidence": [
                item.model_dump(mode="json") for item in existing_evidence
            ],
            "coverage_gaps": list(coverage_gaps),
            "attempt": attempt,
        }
        data = self._complete_json(
            prompt_name="coordinator/plan_supplement",
            variables={
                "paper_json": json.dumps(payload["paper"], ensure_ascii=False),
                "brief_json": json.dumps(payload["brief"], ensure_ascii=False),
                "existing_evidence_json": json.dumps(
                    payload["existing_evidence"], ensure_ascii=False
                ),
                "coverage_gaps_json": json.dumps(
                    payload["coverage_gaps"], ensure_ascii=False
                ),
                "attempt": attempt,
                "brief_schema": json.dumps(
                    NoveltyBrief.model_json_schema(), ensure_ascii=False
                ),
            },
            payload=payload,
            system_prompt=self._system_prompt(),
            fallback_user_prompt=(
                "请只针对 coverage_gaps 生成补充调研任务。保持原有 novelty_points "
                "稳定，不要随意新增或改写查新点。输出完整 NoveltyBrief JSON。"
            ),
        )
        if not isinstance(data, dict):
            raise ValueError("Coordinator plan_supplement 输出顶层必须是对象")
        return self._validate_brief(data, action="生成补充查新计划")

    def synthesize(
        self,
        paper: PaperInput,
        *,
        brief: NoveltyBrief,
        evidence: Sequence[EvidenceCard],
        rejected_evidence: Sequence[str],
        coverage_gaps: Sequence[str],
    ) -> NoveltyReport:
        """汇总全部有效证据，形成最终查新报告。

        输入来自多个 Research Agent 和证据校验器。主 Agent 在这里负责把局部
        证据上升为全局结论，但不能凭空生成不存在的文献依据。
        """

        payload = {
            "paper": paper.model_dump(mode="json"),
            "brief": brief.model_dump(mode="json"),
            "evidence": [item.model_dump(mode="json") for item in evidence],
            "rejected_evidence": list(rejected_evidence),
            "coverage_gaps": list(coverage_gaps),
        }
        data = self._complete_json(
            prompt_name="coordinator/synthesize",
            variables={
                "paper_json": json.dumps(payload["paper"], ensure_ascii=False),
                "brief_json": json.dumps(payload["brief"], ensure_ascii=False),
                "evidence_json": json.dumps(payload["evidence"], ensure_ascii=False),
                "rejected_evidence_json": json.dumps(
                    payload["rejected_evidence"], ensure_ascii=False
                ),
                "coverage_gaps_json": json.dumps(
                    payload["coverage_gaps"], ensure_ascii=False
                ),
                "report_schema": json.dumps(
                    NoveltyReport.model_json_schema(), ensure_ascii=False
                ),
            },
            payload=payload,
            system_prompt=self._system_prompt(),
            fallback_user_prompt=(
                "请基于有效 EvidenceCard 生成最终 NoveltyReport JSON。每个结论必须"
                "绑定 supporting_card_ids 或明确标记证据不足，不得编造文献。"
            ),
        )
        if not isinstance(data, dict):
            raise ValueError("Coordinator synthesize 输出顶层必须是对象")
        return self._validate_report(data, paper_id=paper.paper_id)

    def _complete_json(
        self,
        *,
        prompt_name: str,
        variables: dict[str, Any],
        payload: dict[str, Any],
        system_prompt: str,
        fallback_user_prompt: str,
    ) -> Any:
        """渲染提示词并调用统一模型客户端，把回复解析为 JSON。"""

        client = self._client()
        if self._prompts is not None:
            rendered = self._prompts.render(prompt_name, **variables)
            system, user = rendered.system, rendered.user
        else:
            system = system_prompt
            user = (
                f"{fallback_user_prompt}\n\n输入数据：\n"
                f"{json.dumps(payload, ensure_ascii=False)}"
            )

        response = client.complete(
            [
                ChatMessage(role="system", content=system),
                ChatMessage(role="user", content=user),
            ],
            options=ModelCallOptions(
                temperature=self.temperature,
                response_format={"type": "json_object"},
            ),
        )
        try:
            data = json.loads(response.content)
        except json.JSONDecodeError as exc:
            raise ValueError("NoveltyCoordinatorAgent 返回内容不是合法 JSON") from exc
        return data

    def _client(self) -> ModelClient:
        if self.model_client is not None:
            return self.model_client
        if self._models is not None:
            return self._models.client_for(self._model_alias or "coordinator")
        raise NotImplementedError(
            "NoveltyCoordinatorAgent 需要注入 ModelClient 或 ModelRegistry"
        )

    @staticmethod
    def _validate_brief(data: dict[str, Any], *, action: str) -> NoveltyBrief:
        """把模型 JSON 校验为 `NoveltyBrief`，防止自由文本进入工作流。"""

        try:
            return NoveltyBrief.model_validate(data)
        except ValidationError as exc:
            raise ValueError(f"NoveltyCoordinatorAgent {action}输出不符合 NoveltyBrief") from exc

    @staticmethod
    def _validate_report(data: dict[str, Any], *, paper_id: str) -> NoveltyReport:
        """校验最终报告，并检查 paper_id 没有被模型改写。"""

        try:
            report = NoveltyReport.model_validate(data)
        except ValidationError as exc:
            raise ValueError("NoveltyCoordinatorAgent 输出不符合 NoveltyReport") from exc
        if report.paper_id != paper_id:
            raise ValueError("NoveltyReport.paper_id 与输入论文不一致")
        return report

    @staticmethod
    def _system_prompt() -> str:
        """主 Agent 的稳定系统职责说明。

        具体可调 Prompt 后续可以迁移到 `prompts/coordinator/`，这里先保留
        最小版本，方便开发者理解主 Agent 的边界。
        """

        return (
            "你是论文查新 Multi-Agent 系统的 Coordinator。"
            "你负责全局规划、任务拆分、补充检索规划和最终证据汇总。"
            "你不能编造文献、DOI、URL 或证据位置；证据不足时必须显式说明。"
            "你的输出必须严格符合调用方要求的 JSON schema。"
        )
