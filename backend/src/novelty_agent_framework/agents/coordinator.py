"""查新主 Agent。

该文件只描述主 Agent 如何组织论文理解、查新点拆解、补充检索规划和
最终查新结论汇总。真实模型、模型供应商和 API 调用方式由 `backend.env`
统一提供，避免不同开发者在 Agent 内部各写一套模型调用代码。
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import replace
from typing import Any

from pydantic import ValidationError

from backend.env import (
    ChatMessage,
    ModelCallOptions,
    ModelClient,
    ModelCallBudgetExceeded,
    ModelTransportTimeout,
    ModelRegistry,
    PromptLibrary,
)
from ..schemas import (
    EvidenceCard,
    InsufficientFinalEvidence,
    NoveltyBrief,
    NoveltyPoint,
    NoveltyPointReview,
    NoveltyReport,
    ReportNarrativeDraft,
    PaperInput,
    ResearchTask,
)
from ..ports import NoveltyCoordinator
from ..core.report_binding import assemble_report_from_draft


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
        model_options: ModelCallOptions | None = None,
        research_languages: Sequence[str] = ("en",),
    ) -> None:
        self.model_client = model_client
        self._prompts = prompts
        self._models = models
        self._model_alias = model_alias
        self.temperature = temperature
        self.model_options = model_options
        languages = tuple(dict.fromkeys(research_languages))
        if not languages or any(item not in {"en", "zh"} for item in languages):
            raise ValueError("research_languages must contain en and/or zh")
        self.research_languages = languages

    def plan(
        self,
        paper: PaperInput,
        *,
        points: Sequence[NoveltyPoint],
        attempt: int,
    ) -> NoveltyBrief:
        """按配置的检索语言分配首轮任务并组装查新规划。

        首轮分工是确定性的，不调用模型，也不生成检索词或 SearchPlan。
        """

        tasks = [
            task
            for point in points
            for task in _initial_tasks_for_point(
                point, attempt=attempt, languages=self.research_languages
            )
        ]
        return NoveltyBrief(
            paper_summary=paper.abstract or paper.title,
            research_problem=paper.title,
            novelty_points=list(points),
            keywords_zh=list(paper.keywords_zh)
            or ([paper.title] if paper.title else []),
            keywords_en=list(paper.keywords_en),
            research_tasks=tasks,
        )

    def plan_supplement(
        self,
        paper: PaperInput,
        *,
        brief: NoveltyBrief,
        existing_evidence: Sequence[EvidenceCard],
        insufficient_final_evidence_points: Sequence[InsufficientFinalEvidence],
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
            "insufficient_final_evidence_points": [
                item.model_dump(mode="json")
                for item in insufficient_final_evidence_points
            ],
            "attempt": attempt,
        }
        data = self._complete_json(
            prompt_name="coordinator/supplement",
            variables={
                "paper_json": json.dumps(payload["paper"], ensure_ascii=False),
                "brief_json": json.dumps(payload["brief"], ensure_ascii=False),
                "existing_evidence_json": json.dumps(
                    payload["existing_evidence"], ensure_ascii=False
                ),
                "insufficient_final_evidence_points_json": json.dumps(
                    payload["insufficient_final_evidence_points"], ensure_ascii=False
                ),
                "attempt": attempt,
                "research_languages_json": json.dumps(
                    self.research_languages, ensure_ascii=False
                ),
                "task_schema": json.dumps(
                    ResearchTask.model_json_schema(), ensure_ascii=False
                ),
            },
            payload=payload,
            system_prompt=self._system_prompt(),
            fallback_user_prompt=(
                "请只针对最终有效 EvidenceCard 数量低于系统门槛的查新点"
                "生成 ResearchTask 列表。只能引用已有"
                " novelty_point_id，不生成检索词、SearchPlan 或数据库查询。"
            ),
        )
        data = _normalize_task_list(data)
        if not isinstance(data, list):
            raise ValueError(
                "Coordinator plan_supplement 输出顶层必须是 ResearchTask 列表"
            )

        allowed_ids = {point.point_id for point in brief.novelty_points}
        task_counts: dict[str, int] = {}
        supplemental_tasks: list[ResearchTask] = []
        for index, item in enumerate(data):
            try:
                task = ResearchTask.model_validate(item)
            except ValidationError as exc:
                raise ValueError(
                    f"plan_supplement 第 {index + 1} 个任务格式错误：{exc}"
                ) from exc
            if task.novelty_point_id not in allowed_ids:
                raise ValueError(
                    "plan_supplement 任务引用了未知查新点 "
                    f"{task.novelty_point_id}"
                )
            if task.language not in self.research_languages:
                continue
            task_counts[task.novelty_point_id] = (
                task_counts.get(task.novelty_point_id, 0) + 1
            )
            supplemental_tasks.append(
                task.model_copy(
                    update={
                        "task_id": (
                            f"T-R{attempt}-{task_counts[task.novelty_point_id]}"
                        ),
                        "attempt": attempt,
                    }
                )
            )
        return brief.model_copy(update={"research_tasks": supplemental_tasks})

    def synthesize(
        self,
        paper: PaperInput,
        *,
        brief: NoveltyBrief,
        evidence: Sequence[EvidenceCard],
        novelty_reviews: Sequence[NoveltyPointReview],
        rejected_evidence: Sequence[str],
        insufficient_final_evidence_points: Sequence[InsufficientFinalEvidence],
    ) -> NoveltyReport:
        """汇总全部有效证据，形成最终查新报告。

        输入来自多个 Research Agent 和证据校验器。主 Agent 在这里负责把局部
        证据上升为全局结论，但不能凭空生成不存在的文献依据。
        """

        payload = {
            "paper": paper.model_dump(mode="json"),
            "brief": brief.model_dump(mode="json"),
            "evidence": [item.model_dump(mode="json") for item in evidence],
            "novelty_reviews": [
                item.model_dump(mode="json") for item in novelty_reviews
            ],
            "rejected_evidence": list(rejected_evidence),
            "insufficient_final_evidence_points": [
                item.model_dump(mode="json")
                for item in insufficient_final_evidence_points
            ],
        }
        variables = {
                "paper_json": json.dumps(payload["paper"], ensure_ascii=False),
                "brief_json": json.dumps(payload["brief"], ensure_ascii=False),
                "evidence_json": json.dumps(payload["evidence"], ensure_ascii=False),
                "novelty_reviews_json": json.dumps(
                    payload["novelty_reviews"], ensure_ascii=False
                ),
                "rejected_evidence_json": json.dumps(
                    payload["rejected_evidence"], ensure_ascii=False
                ),
                "insufficient_final_evidence_points_json": json.dumps(
                    payload["insufficient_final_evidence_points"], ensure_ascii=False
                ),
                "draft_schema": json.dumps(
                    ReportNarrativeDraft.model_json_schema(), ensure_ascii=False
                ),
            }
        if self._prompts is not None:
            rendered = self._prompts.render("coordinator/synthesize", **variables)
            system, user = rendered.system, rendered.user
        else:
            system = self._system_prompt()
            user = (
                "只输出 ReportNarrativeDraft JSON：每点一段简短 summary、已授权卡片 ID 分组和"
                "有限的表达性 limitations。不要输出 paper_id、Reviewer 裁定、证据对象或原文。"
                "严格覆盖输入的全部查新点；检索覆盖未知时不要推断零命中。\n"
                f"Draft schema: {variables['draft_schema']}\n"
                f"输入数据：{json.dumps(payload, ensure_ascii=False)}"
            )
        options = replace(
            self.model_options or ModelCallOptions(temperature=self.temperature),
            response_format={"type": "json_object"},
        )
        permitted_points = [point.point_id for point in brief.novelty_points]
        permitted_cards = [card.card_id for card in evidence]
        messages = [ChatMessage(role="system", content=system), ChatMessage(role="user", content=user)]
        for attempt in range(2):
            try:
                response = self._client().complete(messages, options=options)
            except ModelCallBudgetExceeded:
                raise
            except ModelTransportTimeout as exc:
                raise ValueError("response_unavailable: report narrative transport timeout") from exc
            finish = _finish_reason(response.raw)
            if finish == "length":
                raise ValueError("output_truncated: report narrative reached provider length limit")
            if not response.content:
                raise ValueError("response_unavailable: report narrative content missing")
            try:
                draft = ReportNarrativeDraft.model_validate(
                    json.loads(_complete_report_json(response.content))
                )
                return assemble_report_from_draft(
                    draft,
                    paper_id=paper.paper_id,
                    novelty_reviews=novelty_reviews,
                    novelty_points=brief.novelty_points,
                    evidence_cards=evidence,
                    rejected_evidence=rejected_evidence,
                )
            except (json.JSONDecodeError, ValidationError, ValueError) as exc:
                if _suspected_report_truncation(response, options.max_tokens, exc):
                    raise ValueError(
                        "suspected_output_truncation: report narrative ended near output limit"
                    ) from exc
                if attempt:
                    raise ValueError(f"draft_contract_error: {exc}") from exc
                messages = [
                    *messages,
                    ChatMessage(role="assistant", content=response.content or ""),
                    ChatMessage(
                        role="user",
                        content=(
                            "上次 ReportNarrativeDraft 无效，请只按同一 Draft schema 重新输出完整 JSON。"
                            f"错误：{type(exc).__name__}: {str(exc)[:500]}。"
                            f"允许的 point ID：{json.dumps(permitted_points, ensure_ascii=False)}；"
                            f"允许的 card ID：{json.dumps(permitted_cards, ensure_ascii=False)}。"
                            f"Draft schema：{variables['draft_schema']}"
                        ),
                    ),
                ]
        raise AssertionError("unreachable report draft loop")

    def _complete_json(
        self,
        *,
        prompt_name: str,
        variables: dict[str, Any],
        payload: dict[str, Any],
        system_prompt: str,
        fallback_user_prompt: str,
        max_attempts: int = 1,
    ) -> Any:
        """渲染提示词并调用统一模型客户端，把回复解析为 JSON。"""

        if max_attempts < 1:
            raise ValueError("max_attempts 必须至少为 1")
        client = self._client()
        last_error: Exception | None = None
        for _attempt in range(max_attempts):
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
                options=replace(
                    self.model_options or ModelCallOptions(temperature=self.temperature),
                    response_format={"type": "json_object"},
                ),
            )
            try:
                return json.loads(_extract_json_object(response.content))
            except json.JSONDecodeError as exc:
                last_error = exc
        raise ValueError("NoveltyCoordinatorAgent 返回内容不是合法 JSON") from last_error

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
            "Reviewer 是新颖性裁定唯一权威来源，你不得改写其裁定字段。"
            "你不能编造文献、DOI、URL 或证据位置；证据不足时必须显式说明。"
            "你的输出必须严格符合调用方要求的 JSON schema。"
        )



def _extract_json_object(content: str | None) -> str:
    """Strip Markdown fences and prose so models may return fenced JSON."""

    text = (content or "").strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    return text


def _complete_report_json(content: str | None) -> str:
    """Accept a whole JSON object (or one complete fence), never a prefix."""

    text = (content or "").strip()
    fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    return fence.group(1).strip() if fence else text


def _finish_reason(raw: Any) -> str | None:
    if not isinstance(raw, dict):
        return None
    choices = raw.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        value = choices[0].get("finish_reason")
        return value if isinstance(value, str) else None
    return None


def _suspected_report_truncation(response, max_tokens: int | None, error: Exception) -> bool:
    """A local hint, not a cross-provider definition of billable output tokens."""

    if not isinstance(error, json.JSONDecodeError):
        return False
    if error.pos < len(error.doc) - 64:
        return False
    if error.msg.startswith("Unterminated string"):
        return True
    if not max_tokens:
        return False
    usage = response.usage if isinstance(response.usage, dict) else {}
    details = usage.get("completion_tokens_details") or {}
    completion = usage.get("completion_tokens")
    reasoning = details.get("reasoning_tokens", 0)
    return (
        isinstance(completion, int)
        and isinstance(reasoning, int)
        and completion - reasoning >= max_tokens
    )

def _normalize_task_list(data: Any) -> Any:
    """兼容模型输出包装形态：单任务对象或含 research_tasks 键的对象 → 列表。"""

    if isinstance(data, dict):
        for key in ("research_tasks", "tasks"):
            if isinstance(data.get(key), list):
                return data[key]
        return [data]
    return data


def _initial_tasks_for_point(
    point: NoveltyPoint,
    *,
    attempt: int,
    languages: Sequence[str],
) -> tuple[ResearchTask, ...]:
    """为单个查新点按启用语言创建首轮任务。"""

    descriptions = {
        "en": "针对该查新点执行英文文献检索。",
        "zh": "针对该查新点执行中文文献检索。",
    }
    return tuple(
        ResearchTask(
            task_id=f"T-{index}",
            novelty_point_id=point.point_id,
            task_type="literature_search",
            language=language,
            description=descriptions[language],
            attempt=attempt,
        )
        for index, language in enumerate(languages, 1)
    )
