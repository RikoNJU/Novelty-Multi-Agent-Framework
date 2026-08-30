"""SearchPlanner Agent 的独立数据流和确定性校验测试（v2 契约）。

模型契约 v2：concepts（role/terms/alias/exclude/importance）+ strategies
（level/focus_concepts）；布尔表达式由 search_plan_compiler 模板生成。
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.env import ModelClientError, ModelResponse, PromptLibrary
from novelty_agent_framework.agents import SearchPlannerAgent
from novelty_agent_framework.schemas import NoveltyPoint, ResearchTask, SearchPlan

PROMPTS_ROOT = Path("backend/src/novelty_agent_framework/prompts")


class StubModelClient:
    def __init__(self, *outputs: str) -> None:
        self.outputs = list(outputs)
        self.calls: list[tuple[list, object]] = []

    def complete(self, messages, *, options=None):  # type: ignore[no-untyped-def]
        self.calls.append((list(messages), options))
        index = min(len(self.calls) - 1, len(self.outputs) - 1)
        return ModelResponse(content=self.outputs[index])


def make_point(*, english: bool = True) -> NoveltyPoint:
    return NoveltyPoint(
        point_id="NP-1",
        claim="采用动态邻居采样降低动态图神经网络训练通信开销",
        claim_en=(
            "Dynamic neighbor sampling reduces communication overhead in dynamic GNN training"
            if english
            else ""
        ),
        technical_features=["动态邻居采样", "分布式训练"],
    )


def make_task(*, language: str = "zh", task_type: str = "literature_search") -> ResearchTask:
    return ResearchTask(
        task_id="T-1" if language == "zh" else "T-2",
        novelty_point_id="NP-1",
        task_type=task_type,
        language=language,
        description=(
            "现有证据未覆盖动态邻居采样特征。"
            if task_type != "literature_search"
            else ""
        ),
    )


def valid_draft(task: ResearchTask, *, language: str | None = None) -> dict:
    """v2 最小模型契约：concepts（role/terms/...）+ strategies（level）。"""

    use_en = (language or task.language) == "en"
    if use_en:
        concepts = [
            {"role": "object", "terms": ["dynamic graph neural network"], "alias": ["DGNN"], "importance": 3},
            {"role": "method", "terms": ["dynamic neighbor sampling"], "importance": 3},
            {"role": "escape", "terms": ["communication efficient graph training"], "importance": 2},
        ]
    else:
        concepts = [
            {"role": "object", "terms": ["动态图神经网络"], "importance": 3},
            {"role": "method", "terms": ["动态邻居采样"], "importance": 3},
            {"role": "escape", "terms": ["低通信开销图训练"], "importance": 2},
        ]
    return {
        "concepts": concepts,
        "strategies": [{"level": "strict"}, {"level": "medium"}, {"level": "broad"}],
    }


def build_agent(client: StubModelClient) -> SearchPlannerAgent:
    return SearchPlannerAgent(
        model_client=client,
        prompts=PromptLibrary(PROMPTS_ROOT),
    )


def test_plans_normal_chinese_task_and_renders_prompt() -> None:
    task = make_task(language="zh")
    client = StubModelClient(json.dumps({"search_plan": valid_draft(task)}))

    plan = build_agent(client).plan(make_point(), task)

    assert isinstance(plan, SearchPlan)
    assert plan.task_id == "T-1"
    assert plan.novelty_point_id == "NP-1"
    assert plan.concepts[0].name == "动态图神经网络"  # name = terms[0]，补全器生成
    assert [c.concept_id for c in plan.concepts] == ["C1", "C2", "C3"]
    assert [c.role for c in plan.concepts] == ["object", "method", "escape"]
    assert [s.strategy_id for s in plan.strategies] == ["S1", "S2", "S3"]
    assert [strategy.level for strategy in plan.strategies] == [
        "strict",
        "medium",
        "broad",
    ]
    assert [s.use_alias for s in plan.strategies] == [False, True, True]
    assert plan.strategies[0].description == "动态图神经网络 AND 动态邻居采样"
    messages, options = client.calls[0]
    assert '"language": "zh"' in messages[1].content
    assert "SearchPlanDraft" in messages[0].content
    assert options.response_format == {"type": "json_object"}


def test_custom_prompt_name_is_used_for_rendering() -> None:
    task = make_task()
    client = StubModelClient(json.dumps(valid_draft(task)))

    class RecordingPrompts:
        def __init__(self) -> None:
            self.names: list[str] = []

        def render(self, name, **variables):
            self.names.append(name)
            return SimpleNamespace(system="system", user=json.dumps(variables))

    prompts = RecordingPrompts()
    agent = SearchPlannerAgent(
        model_client=client,
        prompts=prompts,
        prompt_name="test/custom_prompt",
    )

    agent.plan(make_point(), task)

    assert prompts.names == ["test/custom_prompt"]


def test_plans_english_task_when_point_has_no_english_claim() -> None:
    task = make_task(language="en")
    client = StubModelClient(json.dumps(valid_draft(task, language="en")))

    plan = build_agent(client).plan(make_point(english=False), task)

    assert plan.concepts[0].name == "dynamic graph neural network"
    assert len(client.calls) == 1


def test_task_point_mismatch_fails_before_model_call() -> None:
    task = make_task()
    task = task.model_copy(update={"novelty_point_id": "NP-2"})
    client = StubModelClient(json.dumps(valid_draft(task)))

    with pytest.raises(ValueError, match="不一致"):
        build_agent(client).plan(make_point(), task)

    assert client.calls == []


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda data: data["concepts"][0].update(terms=[""]),
            "词项全为空",
        ),
        (
            lambda data: data["concepts"][0].update(terms=["efficient robust learning"]),
            "generic_term",
        ),
    ],
)
def test_rejects_invalid_draft_semantics(mutation, message) -> None:  # type: ignore[no-untyped-def]
    task = make_task(language="en")
    data = valid_draft(task)
    mutation(data)
    output = json.dumps(data)
    client = StubModelClient(output, output)

    with pytest.raises(ValueError, match=message):
        build_agent(client).plan(make_point(), task)

    assert len(client.calls) == 3


def test_retries_once_after_invalid_json_then_succeeds() -> None:
    task = make_task()
    client = StubModelClient("not json", json.dumps(valid_draft(task)))

    plan = build_agent(client).plan(make_point(), task)

    assert plan.task_id == task.task_id
    assert len(client.calls) == 2
    assert "不是合法 JSON" in client.calls[1][0][1].content


def test_retries_after_model_network_error_then_succeeds() -> None:
    """单次模型网络超时不应击穿工作流：进入重试并携带网络错误原因。"""

    task = make_task()

    class FlakyClient(StubModelClient):
        def __init__(self, *outputs: str) -> None:
            super().__init__(*outputs)
            self.fail_first = True

        def complete(self, messages, *, options=None):
            self.calls.append((list(messages), options))
            if self.fail_first:
                self.fail_first = False
                raise ModelClientError("模型网络调用失败: The read operation timed out")
            index = min(len(self.calls) - 1, len(self.outputs) - 1)
            return ModelResponse(content=self.outputs[index])

    client = FlakyClient(json.dumps(valid_draft(task)))
    plan = build_agent(client).plan(make_point(), task)

    assert plan.task_id == task.task_id
    assert len(client.calls) == 2
    assert "模型网络调用失败" in client.calls[1][0][1].content

def test_invalid_schema_fails_after_one_retry() -> None:
    client = StubModelClient("{}", "{}")

    with pytest.raises(ValueError, match="3 次生成均失败"):
        build_agent(client).plan(make_point(), make_task())

    assert len(client.calls) == 3


def test_legacy_v1_output_is_rejected() -> None:
    """v1 契约（含 expression）因 extra=forbid 被拒并重试。"""

    task = make_task()
    legacy = {
        "concepts": [{"terms": ["x"]}],
        "strategies": [{"expression": "C1"}],
    }
    client = StubModelClient(json.dumps(legacy), json.dumps(legacy))

    with pytest.raises(ValueError, match="3 次生成均失败"):
        build_agent(client).plan(make_point(), task)

    assert len(client.calls) == 3


def test_structured_retry_feedback_is_forwarded_to_prompt() -> None:
    task = make_task(language="en")
    bad = valid_draft(task)
    bad["concepts"][0]["terms"] = ["efficient robust learning"]  # 泛词失败
    good = valid_draft(task)
    client = StubModelClient(json.dumps(bad), json.dumps(good))

    plan = build_agent(client).plan(make_point(), task)

    assert plan.strategies[0].expression == "C1 AND C2"
    retry_message = client.calls[1][0][1].content
    assert "generic_term" in retry_message
    assert '"code"' in retry_message


def test_supplement_task_can_use_focused_strategy_count() -> None:
    task = make_task(language="en", task_type="feature_supplement")
    data = valid_draft(task)
    data["strategies"] = [{"level": "strict", "focus_concepts": ["C2"]}]
    client = StubModelClient(json.dumps(data))

    plan = build_agent(client).plan(make_point(), task)

    assert len(plan.strategies) == 1
    assert plan.strategies[0].level == "strict"
    assert plan.strategies[0].expression == "C2"
    assert "动态邻居采样" in client.calls[0][0][1].content