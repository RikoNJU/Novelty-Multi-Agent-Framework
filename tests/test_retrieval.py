"""两层检索（种子 + 扩展）与合并打分的离线单测。"""

from __future__ import annotations

import pytest

from novelty_agent_framework.ports import SearchHit
from novelty_agent_framework.schemas import NoveltyPoint, PaperInput
from novelty_agent_framework.tools.retrieval import (
    ExpansionResult,
    build_expansion_queries,
    clear_seed_cache,
    extract_reference_titles,
    merge_candidates,
    search_expansion,
    search_reference_seed,
    title_similarity,
)


def hit(doc_id: str, title: str, year: int = 2020, abstract: str = "") -> SearchHit:
    return SearchHit(
        document_id=doc_id,
        title=title,
        abstract=abstract,
        year=year,
        url=f"https://arxiv.org/abs/{doc_id}",
    )


class FakeSearchTool:
    def __init__(self, results: dict[str, list[SearchHit]]) -> None:
        self.results = results
        self.queries: list[tuple[str, int]] = []

    def search(self, query: str, *, limit: int = 10):
        self.queries.append((query, limit))
        return self.results.get(query, [])


@pytest.fixture(autouse=True)
def _clear_cache():
    clear_seed_cache()
    yield


def test_extract_reference_titles_standard_format():
    references = [
        "[1] Zhang, et al. GraphSAGE: Inductive representation learning on large graphs[J]. NeurIPS, 2017.",
        "[2] 面向大规模动态图的图神经网络优化机制研究[J]. 计算机学报, 2022.",
        "[3] Hamilton, et al. Inductive Representation Learning on Large Graphs[D]. 2017.",
    ]

    titles = extract_reference_titles(references, max_refs=5)

    assert "GraphSAGE: Inductive representation learning on large graphs" in titles
    assert "Inductive Representation Learning on Large Graphs" in titles
    assert all("中文" not in title for title in titles)


def test_extract_reference_titles_stops_at_marker():
    references = [
        "[3] PEROZZI B, AL-RFOU R, SKIENA S. Deepwalk: Online learning of social representations[C] // Proceedings of the 20th ACM SIGKDD international conference on Knowledge discovery and data mining, 2014."
    ]

    titles = extract_reference_titles(references, max_refs=5)

    assert titles == ["Deepwalk: Online learning of social representations"]


def test_extract_reference_titles_caps_at_max_refs():
    references = [f"[{i}] Author. Title number {i}[J]. Journal, 2020." for i in range(1, 30)]

    assert len(extract_reference_titles(references, max_refs=3)) == 3


def test_title_similarity_threshold():
    left = "GraphSAGE: Inductive representation learning on large graphs"

    assert title_similarity(left, "Inductive Representation Learning on Large Graphs") >= 0.5
    assert title_similarity(left, "Attention Is All You Need") == 0.0


def test_search_reference_seed_uses_ti_and_keywords():
    ref_title = "GraphSAGE: Inductive representation learning on large graphs"
    paper = PaperInput(
        paper_id="p1",
        title="t",
        abstract="a",
        full_text="f",
        references=[f"[1] Zhang. {ref_title}[J]. NeurIPS, 2017."],
        keywords_en=["graph neural network"],
    )
    exact = hit("2305.00001", ref_title)
    wrong = hit("2305.00002", "Unrelated Paper About Something Else")
    keyword_hit = hit("2305.00003", "A Survey of Graph Neural Networks")
    tool = FakeSearchTool(
        {
            f'ti:"{ref_title}"': [exact, wrong],
            'all:"graph neural network"': [keyword_hit],
        }
    )

    seed = search_reference_seed(paper, tool)

    assert {item.document_id for item in seed} == {"2305.00001", "2305.00003"}
    assert any(query.startswith("ti:") for query, _ in tool.queries)
    assert any(query.startswith("all:") for query, _ in tool.queries)


def test_search_reference_seed_cached_by_paper_id():
    paper = PaperInput(
        paper_id="p1",
        title="t",
        abstract="a",
        full_text="f",
        keywords_en=["graph neural network"],
    )
    tool = FakeSearchTool({'all:"graph neural network"': [hit("2305.00001", "Survey of GNN")]})

    search_reference_seed(paper, tool)
    search_reference_seed(paper, tool)

    assert len(tool.queries) == 1


def test_build_expansion_queries_from_point():
    point = NoveltyPoint(
        point_id="NP-1",
        claim="c",
        claim_en="graph summarization for temporal graphs",
        technical_features_en=["graph summarization", "dynamic graph"],
    )

    queries = build_expansion_queries(point)

    assert 'abs:"graph summarization for temporal graphs"' in queries
    assert 'abs:"graph summarization" AND abs:"dynamic graph"' in queries
    assert 'abs:"graph summarization"' in queries
    assert 'abs:"dynamic graph"' in queries


def test_build_expansion_queries_skips_long_claim_and_empty():
    long_point = NoveltyPoint(
        point_id="NP-1",
        claim="c",
        claim_en="x" * 150,
        technical_features_en=["a", "b"],
    )
    queries = build_expansion_queries(long_point)
    assert not any("x" * 150 in query for query in queries)

    empty_point = NoveltyPoint(point_id="NP-2", claim="c")
    assert build_expansion_queries(empty_point) == []


def test_build_expansion_queries_uses_content_words_for_long_features():
    point = NoveltyPoint(
        point_id="NP-1",
        claim="c",
        claim_en="x" * 150,
        technical_features_en=[
            "Model dynamic sequential graphs as sequences of original graph snapshots at each moment"
        ],
    )

    queries = build_expansion_queries(point)

    assert any('all:"sequential"' in query and " AND " in query for query in queries)
    assert not any('abs:"Model dynamic sequential graphs' in query for query in queries)


def test_search_expansion_merges_and_counts():
    first = hit("2305.00001", "Temporal Graph Learning")
    second = hit("2305.00002", "Dynamic Graphs")
    point = NoveltyPoint(
        point_id="NP-1",
        claim="c",
        claim_en="temporal graph learning",
        technical_features_en=["graph summarization", "dynamic graph"],
    )
    tool = FakeSearchTool(
        {
            'abs:"temporal graph learning"': [first, second],
            'abs:"graph summarization" AND abs:"dynamic graph"': [first],
            'abs:"graph summarization"': [first],
            'abs:"dynamic graph"': [second],
        }
    )

    result = search_expansion(point, tool)

    assert {item.document_id for item in result.hits} == {"2305.00001", "2305.00002"}
    assert result.hit_counts["2305.00001"] == 3
    assert result.hit_counts["2305.00002"] == 2


def test_merge_candidates_marks_cited_and_orders():
    seed = [hit("2305.00001", "Cited Paper")]
    point = NoveltyPoint(
        point_id="NP-1",
        claim="c",
        claim_en="graph neural network",
        technical_features_en=["dynamic graph"],
    )
    expansion = ExpansionResult(
        hits=(
            hit("2305.00001", "Cited Paper"),
            hit("2305.00002", "Dynamic Graph Neural Networks"),
        ),
        hit_counts={"2305.00001": 2, "2305.00002": 3},
    )

    result = merge_candidates(seed, expansion, point, top_n=5, current_year=2026)
    by_id = {item.hit.document_id: item for item in result}

    assert by_id["2305.00001"].cited_by_paper is True
    assert by_id["2305.00002"].cited_by_paper is False
    assert by_id["2305.00002"].query_hits == 3
    assert result[0].score >= result[1].score


def test_merge_candidates_truncates_top_n():
    hits = tuple(hit(f"2305.0000{i}", f"Paper {i}") for i in range(1, 11))
    expansion = ExpansionResult(hits=hits, hit_counts={item.document_id: 1 for item in hits})
    point = NoveltyPoint(point_id="NP-1", claim="c")

    result = merge_candidates([], expansion, point, top_n=3, current_year=2026)

    assert len(result) == 3
