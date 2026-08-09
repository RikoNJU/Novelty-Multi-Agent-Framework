"""arXiv 真实网络冒烟测试。

默认跳过；显式执行：
    pytest -m live tests/test_live_arxiv_tools.py -s
需要外网可访问 export.arxiv.org / arxiv.org。
"""

from __future__ import annotations

import pytest

from novelty_agent_framework.config import build_workflow, load_config
from novelty_agent_framework.schemas import NoveltyPoint, ResearchTask
from novelty_agent_framework.tools import (
    ArxivFullTextTool,
    ArxivMetadataTool,
    ArxivSearchTool,
)

pytestmark = pytest.mark.live


def test_live_arxiv_search_fetch_resolve() -> None:
    search = ArxivSearchTool()
    full_text = ArxivFullTextTool()
    metadata = ArxivMetadataTool()

    hits = search.search('abs:"graph neural network"', limit=3)
    assert hits, "arXiv 检索应返回非空结果"
    first = hits[0]
    assert first.document_id and first.url.startswith("https://arxiv.org/abs/")

    resolved = metadata.resolve(first.document_id)
    assert resolved is not None and resolved.title

    text = full_text.fetch(first.document_id)
    if text is not None:
        assert len(text.text) > 0
        print(f"\n{first.document_id}: 全文 {len(text.text)} 字符")


def test_live_research_agent_runs_one_point() -> None:
    """完整 Agent 跑一个查新点：真实检索 + 假模型输出由绑定校验兜底。"""

    workflow = build_workflow()
    if workflow.services.search_tool is None:
        pytest.skip("默认配置未启用 tools.arxiv")

    point = NoveltyPoint(
        point_id="NP-1",
        claim="大规模时序图上的表示学习方法",
        claim_en="Graph representation learning on large-scale temporal graphs",
        technical_features_en=["temporal graph", "graph summarization"],
    )
    task = ResearchTask(
        task_id="TASK-NP-1-R1",
        novelty_point_id="NP-1",
        task_type="literature_search",
        language="en",
        description="检索大规模时序图表示学习方法",
        attempt=1,
    )
    plan = workflow.services.search_planner.plan(point, task)
    compiled = workflow.services.query_adapter.compile(plan)
    candidates = workflow.services.search_tool.search(compiled[0].query, limit=3)
    agent = workflow.services.research_agent
    cards = agent.research(
        task,
        point,
        candidates,
        full_text_tool=workflow.services.full_text_tool,
        metadata_tool=workflow.services.metadata_tool,
    )
    print(f"\n返回 {len(cards)} 张证据卡，均绑定真实检索结果")


def test_live_build_workflow_with_tools_enabled() -> None:
    config = load_config()
    config["tools"]["arxiv"]["enabled"] = True
    workflow = build_workflow(config)

    assert workflow.services.search_tool is not None
    assert workflow.services.full_text_tool is not None
    assert workflow.services.metadata_tool is not None
