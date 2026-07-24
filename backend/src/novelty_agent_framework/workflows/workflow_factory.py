"""将具体 Agent、模型和工具装配为查新工作流。"""

from novelty_agent_framework.agents import DemoCoordinator, DemoResearchAgent

from .novelty import NoveltyWorkflow
from .state import NoveltyWorkflowServices


def build_novelty_workflow() -> NoveltyWorkflow:
    """V0 使用 Demo 实现；生产环境在此替换真实服务。"""

    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=DemoCoordinator(),
            research_agent=DemoResearchAgent(),
        )
    )
