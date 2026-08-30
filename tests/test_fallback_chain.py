"""M3 零命中放宽链的独立单测：链生成（纯函数）+ 执行降级（集成）。
"""

from __future__ import annotations

import asyncio

from novelty_agent_framework.agents import DemoQueryAdapter
from novelty_agent_framework.agents.search_plan_compiler import build_fallback_chain
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.ports import SearchHit
from novelty_agent_framework.schemas import (
    NoveltyPoint,
    ResearchTask,
    SearchConcept,
    SearchPlan,
    SearchStrategy,
    StructuredSourceRetrievalRequest,
)
from novelty_agent_framework.tools.database_search import (
    RetrievalSource,
    StructuredSourceRetrievalTool,
)


def make_plan(*, concepts=None, strategies=None) -> SearchPlan:
    concepts = concepts or [
        SearchConcept(concept_id="C1", name="对象", terms=["graph"], importance=3),
        SearchConcept(concept_id="C2", name="方法", terms=["gnn"], importance=2),
        SearchConcept(concept_id="C3", name="解法", terms=["condense"], importance=2),
    ]
    strategies = strategies or [
        SearchStrategy(strategy_id="S1", level="strict", expression="C1 AND C2", use_alias=False),
        SearchStrategy(strategy_id="S2", level="medium", expression="C1 AND C2", use_alias=True),
        SearchStrategy(
            strategy_id="S3", level="broad", expression="C1 OR C2 OR C3",
            use_alias=True, use_exclude=True,
        ),
    ]
    return SearchPlan(
        task_id="T1", novelty_point_id="NP1",
        concepts=concepts, strategies=strategies,
    )


# ---------- 链生成（纯函数） ----------


def test_chain_contains_base_and_fallback_variants() -> None:
    chain = build_fallback_chain(make_plan())
    assert [v.variant_id for v in chain] == [
        "S1", "S1-fb1", "S2", "S2-fb1", "S3", "S3-fb1",
    ]


def test_strict_fallback_drops_lowest_importance_concept() -> None:
    chain = build_fallback_chain(make_plan())
    s1_fb = chain[1]
    assert s1_fb.expression == "C1"  # C2 importance 2 < C1 3
    assert "C2" in s1_fb.drop_reason
    assert s1_fb.use_alias is False


def test_medium_fallback_keeps_alias_expansion() -> None:
    chain = build_fallback_chain(make_plan())
    s2_fb = chain[3]
    assert s2_fb.expression == "C1"
    assert s2_fb.use_alias is True


def test_broad_fallback_removes_exclude_only() -> None:
    chain = build_fallback_chain(make_plan())
    s3_fb = chain[5]
    assert s3_fb.expression == "C1 OR C2 OR C3"
    assert s3_fb.use_exclude is False
    assert "exclude" in s3_fb.drop_reason


def test_single_concept_strategy_has_no_drop_fallback() -> None:
    plan = make_plan(
        strategies=[SearchStrategy(strategy_id="S1", level="strict", expression="C1")]
    )
    assert [v.variant_id for v in build_fallback_chain(plan)] == ["S1"]


def test_chain_length_is_capped_at_twice_strategy_count() -> None:
    assert len(build_fallback_chain(make_plan())) <= 6


# ---------- 执行降级（集成） ----------


def hit(doc_id: str = "2305.12345") -> SearchHit:
    return SearchHit(
        document_id=doc_id,
        source_id="demo",
        external_id=f"{doc_id}v2",
        title=f"Paper {doc_id}",
        abstract="A complete abstract.",
        year=2023,
        url=f"https://example.test/{doc_id}",
    )


class QuerySearcher:
    source_id = "demo"

    def __init__(self, results: dict[str, list[SearchHit]]) -> None:
        self.results = results
        self.calls: list[str] = []

    def search(self, query: str, *, limit: int = 10):
        self.calls.append(query)
        return self.results.get(query, [])


def build_tool(tmp_path, results: dict[str, list[SearchHit]], *, candidate_limit: int = 5):
    searcher = QuerySearcher(results)
    source = RetrievalSource(
        source_id="demo",
        query_adapter=DemoQueryAdapter(),
        search_tool=searcher,
    )
    tool = StructuredSourceRetrievalTool(
        source=source,
        reference_store=ReferenceStore(tmp_path),
        candidate_limit=candidate_limit,
    )
    return tool, searcher


def make_request() -> StructuredSourceRetrievalRequest:
    return StructuredSourceRetrievalRequest(
        subject_paper_id="paper-1",
        source_id="demo",
        novelty_point=NoveltyPoint(point_id="NP1", claim="claim"),
        research_task=ResearchTask(
            task_id="T1", novelty_point_id="NP1", task_type="search", language="en"
        ),
        search_plan=make_plan(),
        run_id="run-1",
    )


def _query(expression: str, *, use_alias: bool = False) -> str:
    plan = make_plan(
        strategies=[
            SearchStrategy(
                strategy_id="S1", level="strict", expression=expression,
                use_alias=use_alias,
            )
        ]
    )
    return DemoQueryAdapter().compile(plan)[0].query


def test_zero_hit_strategy_falls_back_and_audits_variants(tmp_path) -> None:
    q_s1 = _query("C1 AND C2")
    q_s1_fb = _query("C1")
    tool, searcher = build_tool(
        tmp_path,
        {q_s1: [], q_s1_fb: [hit("a")]},
    )

    bundle = asyncio.run(tool.ainvoke(make_request()))

    executed = [item for item in bundle.search_executions]
    assert [item.parameters.get("strategy_id") for item in executed][:2] == ["S1", "S1-fb1"]
    assert executed[0].results == []  # 零命中
    assert [rank for item in executed[1].results for rank in [item.rank]] == [1]
    assert executed[1].parameters.get("base_strategy") == "S1"
    assert "丢弃概念" in executed[1].parameters.get("fallback_reason", "")
    assert bundle.source_records  # 放宽变体命中的文献进入结果池
    # 唯一命中数 1 < candidate_limit 5，链继续走到 S3-fb1 耗尽
    assert len(searcher.calls) == 6


def test_hit_base_strategy_skips_its_fallback_variant(tmp_path) -> None:
    q_s1 = _query("C1 AND C2")
    tool, searcher = build_tool(tmp_path, {q_s1: [hit("a")]})

    bundle = asyncio.run(tool.ainvoke(make_request()))

    variant_ids = [item.parameters.get("strategy_id") for item in bundle.search_executions]
    assert "S1-fb1" not in variant_ids  # S1 命中，其放宽变体被跳过
    # S2 与 S1 同查询串同样命中 → S2-fb1 跳过；S3 组零命中走到耗尽
    assert variant_ids == ["S1", "S2", "S3", "S3-fb1"]
    assert len(searcher.calls) == 4


def test_candidate_limit_stops_chain_early(tmp_path) -> None:
    q_s1 = _query("C1 AND C2")
    tool, searcher = build_tool(
        tmp_path, {q_s1: [hit("a")]}, candidate_limit=1
    )

    bundle = asyncio.run(tool.ainvoke(make_request()))

    assert [item.parameters.get("strategy_id") for item in bundle.search_executions] == ["S1"]
    assert len(searcher.calls) == 1


def test_all_zero_hits_exhausts_chain_without_error(tmp_path) -> None:
    tool, searcher = build_tool(tmp_path, {})

    bundle = asyncio.run(tool.ainvoke(make_request()))

    assert len(bundle.search_executions) == 6  # 链耗尽
    assert all(item.status.value == "succeeded" for item in bundle.search_executions)
    assert all(item.results == [] for item in bundle.search_executions)
    assert bundle.source_records == []


def test_search_failure_continues_chain_and_keeps_audit(tmp_path) -> None:
    q_s1 = _query("C1 AND C2")

    class FlakySearcher(QuerySearcher):
        def __init__(self) -> None:
            super().__init__({})
            self.first = True

        def search(self, query: str, *, limit: int = 10):
            self.calls.append(query)
            if self.first:
                self.first = False
                raise RuntimeError("boom")
            return []

    searcher = FlakySearcher()
    source = RetrievalSource(
        source_id="demo",
        query_adapter=DemoQueryAdapter(),
        search_tool=searcher,
    )
    tool = StructuredSourceRetrievalTool(
        source=source,
        reference_store=ReferenceStore(tmp_path),
    )

    bundle = asyncio.run(tool.ainvoke(make_request()))

    assert bundle.search_executions[0].status.value == "failed"
    assert bundle.search_executions[0].error.startswith("RuntimeError")
    assert len(bundle.search_executions) == 6
