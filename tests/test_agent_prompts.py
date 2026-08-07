import json
from pathlib import Path

import pytest

from backend.env import ModelResponse, PromptLibrary
from novelty_agent_framework.agents import (
    NoveltyCoordinatorAgent,
    NoveltyResearchAgent,
)
from novelty_agent_framework.schemas import NoveltyPoint, PaperInput, ResearchTask

PROMPTS_ROOT = Path("backend/src/novelty_agent_framework/prompts")


class RecordingModelClient:
    """记录调用消息并返回预设 JSON 的假模型客户端。"""

    def __init__(self, content: str) -> None:
        self.content = content
        self.calls: list[tuple[list, object]] = []

    def complete(self, messages, *, options=None):
        self.calls.append((list(messages), options))
        return ModelResponse(content=self.content)


TASKS_JSON = json.dumps(
    [
        {
            "task_id": "TASK-NP-1-R1",
            "novelty_point_id": "NP-1",
            "queries": ["多智能体协作"],
            "context": "提出一个测试查新点",
            "attempt": 1,
        }
    ]
)


POINTS = [
    NoveltyPoint(
        point_id="NP-1",
        claim="提出一个测试查新点",
        technical_features=["多智能体协作"],
        source_locations=["abstract"],
    )
]


CARD_JSON = {
    "card_id": "CARD-1",
    "task_id": "TASK-NP-1-R1",
    "novelty_point_id": "NP-1",
    "document_title": "相关工作",
    "main_contribution": "提出了一个相关方法。",
    "overlaps": ["技术路线部分重合"],
    "differences": ["目标论文声明了不同组合"],
    "sources": [
        {
            "title": "相关工作",
            "quote": "原文摘录",
            "location": "Section 3",
            "url": "https://example.org/paper",
        }
    ],
    "cited_by_paper": False,
    "possible_baseline": True,
    "relevance": 0.82,
    "confidence": 0.78,
}


def make_paper() -> PaperInput:
    return PaperInput(
        paper_id="paper-1",
        title="测试论文",
        abstract="测试论文摘要",
        full_text="测试论文正文",
    )


def test_coordinator_renders_prompt_from_library():
    client = RecordingModelClient(TASKS_JSON)
    agent = NoveltyCoordinatorAgent(
        model_client=client,
        prompts=PromptLibrary(PROMPTS_ROOT),
    )

    brief = agent.plan(
        make_paper(),
        points=POINTS,
        attempt=1,
    )

    assert brief.novelty_points[0].point_id == "NP-1"
    assert brief.research_tasks[0].task_id == "TASK-NP-1-R1"
    assert brief.paper_summary == "测试论文摘要"
    messages, options = client.calls[0]
    system, user = messages[0].content, messages[1].content
    assert "Coordinator" in system
    assert '"paper_id": "paper-1"' in user
    assert "ResearchTask" in user  # schema 动态注入
    assert options.response_format == {"type": "json_object"}


def test_research_renders_prompt_and_validates_cards():
    client = RecordingModelClient(json.dumps([CARD_JSON]))
    agent = NoveltyResearchAgent(
        model_client=client,
        prompts=PromptLibrary(PROMPTS_ROOT),
    )
    task = ResearchTask(
        task_id="TASK-NP-1-R1",
        novelty_point_id="NP-1",
        queries=["多智能体协作"],
        context="提出一个测试查新点",
        attempt=1,
    )

    cards = agent.research(task, make_paper())

    assert len(cards) == 1
    assert cards[0].card_id == "CARD-1"
    messages, _ = client.calls[0]
    system, user = messages[0].content, messages[1].content
    assert "文献调研 Agent" in system
    assert '"task_id": "TASK-NP-1-R1"' in user


def test_research_rejects_malformed_card():
    bad_card = dict(CARD_JSON)
    bad_card["relevance"] = 1.5  # 超出 0..1 范围
    client = RecordingModelClient(json.dumps([bad_card]))
    agent = NoveltyResearchAgent(
        model_client=client,
        prompts=PromptLibrary(PROMPTS_ROOT),
    )
    task = ResearchTask(
        task_id="TASK-NP-1-R1",
        novelty_point_id="NP-1",
        queries=["q"],
        attempt=1,
    )

    with pytest.raises(ValueError, match="证据卡格式错误"):
        agent.research(task, make_paper())


def test_agent_without_client_or_registry_raises():
    agent = NoveltyCoordinatorAgent()
    with pytest.raises(NotImplementedError):
        agent.plan(
            make_paper(),
            points=[],
            attempt=1,
        )


def test_plan_rejects_task_for_unknown_point():
    tasks_json = json.dumps(
        [
            {
                "task_id": "TASK-X",
                "novelty_point_id": "NP-99",
                "queries": ["q"],
                "attempt": 1,
            }
        ]
    )
    agent = NoveltyCoordinatorAgent(
        model_client=RecordingModelClient(tasks_json),
        prompts=PromptLibrary(PROMPTS_ROOT),
    )

    with pytest.raises(ValueError, match="未知查新点"):
        agent.plan(make_paper(), points=POINTS, attempt=1)
