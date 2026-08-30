"""SearchPlanner Agent 的独立数据流和确定性校验测试。"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.env import ModelResponse, PromptLibrary
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


def valid_plan(task: ResearchTask, *, language: str | None = None) -> dict:
    use_en = (language or task.language) == "en"
    names = (
        ["dynamic graph neural network", "dynamic neighbor sampling", "communication overhead"]
        if use_en
        else ["动态图神经网络", "动态邻居采样", "通信开销"]
    )
    return {
        "task_id": task.task_id,
        "novelty_point_id": task.novelty_point_id,
        "concepts": [
            {"concept_id": f"C{index}", "name": name, "terms": [name]}
            for index, name in enumerate(names, start=1)
        ],
        "strategies": [
            {
                "strategy_id": "S1",
                "level": "strict",
                "expression": "C1 AND C2 AND C3",
                "description": "完整技术组合",
            },
            {
                "strategy_id": "S2",
                "level": "medium",
                "expression": "C1 AND C2",
                "description": "保留对象与方法",
            },
            {
                "strategy_id": "S3",
                "level": "broad",
                "expression": "C2 AND C3",
                "description": "围绕关键方法与目标扩大召回",
            },
        ],
    }


def build_agent(client: StubModelClient) -> SearchPlannerAgent:
    return SearchPlannerAgent(
        model_client=client,
        prompts=PromptLibrary(PROMPTS_ROOT),
    )


def test_plans_normal_chinese_task_and_renders_prompt() -> None:
    task = make_task(language="zh")
    client = StubModelClient(json.dumps({"search_plan": valid_plan(task)}))

    plan = build_agent(client).plan(make_point(), task)

    assert isinstance(plan, SearchPlan)
    assert plan.task_id == "T-1"
    assert plan.concepts[0].name == "动态图神经网络"
    assert [strategy.level for strategy in plan.strategies] == [
        "strict",
        "medium",
        "broad",
    ]
    messages, options = client.calls[0]
    assert '"language": "zh"' in messages[1].content
    assert "数据库无关" in messages[0].content
    assert options.response_format == {"type": "json_object"}


def test_custom_prompt_name_is_used_for_rendering() -> None:
    task = make_task()
    client = StubModelClient(json.dumps(valid_plan(task)))

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
    client = StubModelClient(json.dumps(valid_plan(task, language="en")))

    plan = build_agent(client).plan(make_point(english=False), task)

    assert plan.concepts[0].name == "dynamic graph neural network"
    assert len(client.calls) == 1


def test_task_point_mismatch_fails_before_model_call() -> None:
    task = make_task()
    task = task.model_copy(update={"novelty_point_id": "NP-2"})
    client = StubModelClient(json.dumps(valid_plan(task)))

    with pytest.raises(ValueError, match="不一致"):
        build_agent(client).plan(make_point(), task)

    assert client.calls == []


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda data: data["strategies"][0].update(expression="C1 AND C4"),
            "未定义 Concept：C4",
        ),
        (
            lambda data: data["concepts"][1].update(concept_id="C1"),
            "重复 Concept ID",
        ),
        (
            lambda data: data["strategies"][0].update(
                expression='abs:"graph neural network" AND C2'
            ),
            "数据库专用语法",
        ),
    ],
)
def test_rejects_invalid_plan_semantics(mutation, message) -> None:  # type: ignore[no-untyped-def]
    task = make_task(language="en")
    data = valid_plan(task)
    mutation(data)
    output = json.dumps(data)
    client = StubModelClient(output, output)

    with pytest.raises(ValueError, match=message):
        build_agent(client).plan(make_point(), task)

    assert len(client.calls) == 2


def test_retries_once_after_invalid_json_then_succeeds() -> None:
    task = make_task()
    client = StubModelClient("not json", json.dumps(valid_plan(task)))

    plan = build_agent(client).plan(make_point(), task)

    assert plan.task_id == task.task_id
    assert len(client.calls) == 2
    assert "不是合法 JSON" in client.calls[1][0][1].content


def test_retries_after_invalid_expression_grammar_then_succeeds() -> None:
    task = make_task()
    invalid = valid_plan(task)
    invalid["strategies"][1]["expression"] = "C1 AND dynamic neighbor sampling"
    repaired = valid_plan(task)
    repaired["strategies"][1]["expression"] = "C1 AND C2"
    client = StubModelClient(json.dumps(invalid), json.dumps(repaired))

    plan = build_agent(client).plan(make_point(), task)

    assert len(client.calls) == 2
    assert plan.strategies[1].expression == "C1 AND C2"
    retry_prompt = client.calls[1][0][1].content
    assert "invalid_expression_grammar" in retry_prompt
    assert "strategy S2" in retry_prompt


def test_invalid_schema_fails_after_one_retry() -> None:
    client = StubModelClient("{}", "{}")

    with pytest.raises(ValueError, match="2 次生成均失败"):
        build_agent(client).plan(make_point(), make_task())

    assert len(client.calls) == 2


def test_supplement_task_can_use_focused_strategy_count() -> None:
    task = make_task(language="en", task_type="feature_supplement")
    data = valid_plan(task)
    data["strategies"] = [data["strategies"][0]]
    client = StubModelClient(json.dumps(data))

    plan = build_agent(client).plan(make_point(), task)

    assert len(plan.strategies) == 1
    assert "动态邻居采样" in client.calls[0][0][1].content
