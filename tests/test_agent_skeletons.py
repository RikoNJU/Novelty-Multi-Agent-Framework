from backend.env import ModelResponse
from novelty_agent_framework.schemas import NoveltyPoint, PaperInput
from novelty_agent_framework.agents import (
    NoveltyCoordinatorAgent,
    NoveltyResearchAgent,
)


class FakeModelClient:
    def __init__(self, content: str) -> None:
        self.content = content

    def complete(self, messages, *, options=None):  # type: ignore[no-untyped-def]
        return ModelResponse(content=self.content)


def test_agent_skeletons_are_importable():
    assert NoveltyCoordinatorAgent().__class__.__name__ == "NoveltyCoordinatorAgent"
    assert NoveltyResearchAgent().__class__.__name__ == "NoveltyResearchAgent"


def test_coordinator_agent_parses_model_brief():
    agent = NoveltyCoordinatorAgent()
    paper = PaperInput(
        paper_id="paper-1",
        title="测试论文",
        abstract="测试论文摘要",
        full_text="测试论文正文",
    )
    points = [
        NoveltyPoint(
            point_id="NP-1",
            claim="提出一个测试查新点",
            technical_features=["多智能体协作"],
            source_locations=["abstract"],
        )
    ]

    brief = agent.plan(
        paper,
        points=points,
        attempt=1,
    )

    assert brief.novelty_points[0].point_id == "NP-1"
    assert [(task.task_id, task.language) for task in brief.research_tasks] == [
        ("T-1", "zh"),
        ("T-2", "en"),
    ]


def test_coordinator_plan_does_not_need_model_client():
    agent = NoveltyCoordinatorAgent()
    paper = PaperInput(
        paper_id="paper-1",
        title="测试论文",
        abstract="测试论文摘要",
        full_text="测试论文正文",
    )
    points = [
        NoveltyPoint(
            point_id="NP-1",
            claim="提出一个测试查新点",
            technical_features=["多智能体协作"],
            source_locations=["abstract"],
        )
    ]

    brief = agent.plan(paper, points=points, attempt=1)

    assert len(brief.research_tasks) == 2


def test_demo_coordinator_creates_zh_and_en_tasks():
    from novelty_agent_framework.agents import DemoCoordinator

    paper = PaperInput(
        paper_id="paper-1",
        title="测试论文",
        abstract="测试论文摘要",
        full_text="测试论文正文",
    )
    points = [
        NoveltyPoint(
            point_id="NP-1",
            claim="中文声明",
            technical_features=["中文特征"],
            claim_en="english claim",
            technical_features_en=["english feature"],
        )
    ]

    brief = DemoCoordinator().plan(paper, points=points, attempt=1)

    assert [
        (task.task_id, task.task_type, task.language)
        for task in brief.research_tasks
    ] == [
        ("T-1", "literature_search", "zh"),
        ("T-2", "literature_search", "en"),
    ]
    assert brief.keywords_zh == ["测试论文"]  # 无关键词时兜底标题
