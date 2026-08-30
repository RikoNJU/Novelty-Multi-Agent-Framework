"""arXiv 真实网络冒烟测试。

默认跳过；显式执行：
    pytest -m live tests/test_live_arxiv_tools.py -s
需要外网可访问 export.arxiv.org / arxiv.org，模型链路需要 backend/.env。
"""

from __future__ import annotations

import asyncio

import pytest

from backend.env.model_client import _load_dev_env
from novelty_agent_framework.config import (
    build_workflow,
    load_application_config,
)
from novelty_agent_framework.schemas import (
    DatabaseSearchArguments,
    NoveltyPoint,
    ResearchTask,
    TaskResearchRequest,
)
from novelty_agent_framework.tools.database_search.providers.arxiv import (
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
    """完整链路跑一个查新点：真实 planner → 编译器 → 真实 arxiv 检索。"""

    _load_dev_env()
    workflow = build_workflow(load_application_config())
    researcher = workflow.services.task_researcher

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

    scope = TaskResearchRequest(
        subject_paper_id="live-test-subject",
        run_id="live-run-1",
        novelty_point=point,
        research_task=task,
        search_plan=plan,
    )
    database = researcher.tools.get("database_search")
    observation = asyncio.run(
        database.ainvoke(DatabaseSearchArguments(source_id="arxiv"), scope=scope)
    )
    result = observation.payload["database_search_result"]
    assert observation.succeeded
    assert result["results"], "真实 arxiv 检索应返回候选"
    print(f"\n检索式: {plan.strategies[0].expression}；返回 {len(result['results'])} 条候选")


def test_live_build_workflow_with_tools_enabled() -> None:
    _load_dev_env()
    workflow = build_workflow(load_application_config())
    researcher = workflow.services.task_researcher

    assert "reference_search" in researcher.tools.names
    database = researcher.tools.get("database_search")
    assert "arxiv" in database.tools_by_source
    assert "null_catalog" in database.tools_by_source
    assert "arxiv" in database.description
