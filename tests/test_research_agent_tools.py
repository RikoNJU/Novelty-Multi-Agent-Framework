"""Research Agent 工具编排路径的集成单测（假工具 + 假模型）。"""

from __future__ import annotations

import json

import pytest

from backend.env import ModelResponse
from novelty_agent_framework.agents import NoveltyResearchAgent
from novelty_agent_framework.ports import FullText, SearchHit
from novelty_agent_framework.schemas import EvidenceSource, PaperInput, ResearchTask
from novelty_agent_framework.tools.retrieval import clear_seed_cache


def hit(doc_id: str, title: str) -> SearchHit:
    return SearchHit(
        document_id=doc_id,
        title=title,
        abstract=f"Abstract of {title}",
        year=2023,
        url=f"https://arxiv.org/abs/{doc_id}",
    )


def card(doc_id: str, *, url: str | None = None, doi: str | None = None, **overrides) -> dict:
    base = {
        "card_id": f"CARD-{doc_id}",
        "task_id": "TASK-NP-1-R1",
        "novelty_point_id": "NP-1",
        "document_title": f"Paper {doc_id}",
        "main_contribution": "提出相关方法。",
        "overlaps": ["部分重合"],
        "differences": ["适用范围不同"],
        "sources": [
            {
                "title": f"Paper {doc_id}",
                "quote": "原文摘录",
                "location": "摘要",
                "url": url,
                "doi": doi,
            }
        ],
        "cited_by_paper": False,
        "relevance": 0.8,
        "confidence": 0.8,
    }
    base.update(overrides)
    return base


class FakeSearchTool:
    def __init__(self, hits: list[SearchHit]) -> None:
        self.hits = hits
        self.queries: list[tuple[str, int]] = []

    def search(self, query: str, *, limit: int = 10):
        self.queries.append((query, limit))
        return list(self.hits)


class FakeFullTextTool:
    def __init__(self, texts: dict[str, str] | None = None) -> None:
        self.texts = texts or {}
        self.fetched: list[str] = []

    def fetch(self, document_id: str):
        self.fetched.append(document_id)
        text = self.texts.get(document_id)
        if text is None:
            return None
        return FullText(document_id=document_id, title=document_id, text=text)


class FakeMetadataTool:
    def __init__(self, sources: dict[str, EvidenceSource] | None = None) -> None:
        self.sources = sources or {}
        self.resolved: list[str] = []

    def resolve(self, document_id: str):
        self.resolved.append(document_id)
        return self.sources.get(document_id)


class RecordingModelClient:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls: list[tuple[list, object]] = []

    def complete(self, messages, *, options=None):
        self.calls.append((list(messages), options))
        return ModelResponse(content=self.content)


def make_paper() -> PaperInput:
    return PaperInput(
        paper_id="paper-test",
        title="测试论文",
        abstract="测试论文摘要",
        full_text="测试论文正文",
    )


def make_task() -> ResearchTask:
    return ResearchTask(
        task_id="TASK-NP-1-R1",
        novelty_point_id="NP-1",
        queries=["图神经网络", "graph neural network"],
        context="查新点上下文",
        attempt=1,
    )


@pytest.fixture(autouse=True)
def _clear_seed_cache():
    clear_seed_cache()
    yield


def test_research_with_tools_retrieves_and_binds():
    search = FakeSearchTool(
        [hit("2305.00001", "Graph Neural Networks"), hit("2305.00002", "Dynamic Graph Learning")]
    )
    full_text = FakeFullTextTool(
        {"2305.00001": "Full text one.", "2305.00002": "Full text two."}
    )
    metadata = FakeMetadataTool(
        {
            "2305.00001": EvidenceSource(
                title="Graph Neural Networks", url="https://arxiv.org/abs/2305.00001"
            )
        }
    )
    client = RecordingModelClient(
        json.dumps([card("2305.00001", url="https://arxiv.org/abs/2305.00001")])
    )
    agent = NoveltyResearchAgent(model_client=client)

    cards = agent.research(
        make_task(),
        make_paper(),
        search_tool=search,
        full_text_tool=full_text,
        metadata_tool=metadata,
    )

    assert [item.card_id for item in cards] == ["CARD-2305.00001"]
    assert cards[0].cited_by_paper is False
    assert "2305.00001" in full_text.fetched
    assert "2305.00002" in full_text.fetched
    assert "2305.00001" in metadata.resolved
    assert any(query.startswith("abs:") for query, _ in search.queries)


def test_research_drops_unbound_cards():
    search = FakeSearchTool([hit("2305.00001", "Graph Neural Networks")])
    client = RecordingModelClient(
        json.dumps(
            [
                card("2305.00001", url="https://arxiv.org/abs/2305.00001"),
                card("9999.99999", url="https://arxiv.org/abs/9999.99999"),
            ]
        )
    )
    agent = NoveltyResearchAgent(model_client=client)

    cards = agent.research(
        make_task(),
        make_paper(),
        search_tool=search,
        full_text_tool=FakeFullTextTool(),
        metadata_tool=FakeMetadataTool(),
    )

    assert [item.card_id for item in cards] == ["CARD-2305.00001"]


def test_research_drops_wrong_task_binding():
    search = FakeSearchTool([hit("2305.00001", "Graph Neural Networks")])
    client = RecordingModelClient(
        json.dumps(
            [
                card(
                    "2305.00001",
                    url="https://arxiv.org/abs/2305.00001",
                    task_id="TASK-OTHER",
                )
            ]
        )
    )
    agent = NoveltyResearchAgent(model_client=client)

    cards = agent.research(
        make_task(),
        make_paper(),
        search_tool=search,
        full_text_tool=FakeFullTextTool(),
        metadata_tool=FakeMetadataTool(),
    )

    assert cards == []


def test_research_overrides_cited_by_paper_from_seed():
    ref_title = "GraphSAGE: Inductive representation learning on large graphs"
    paper = make_paper()
    paper.references = [f"[1] Zhang. {ref_title}[J]. NeurIPS, 2017."]
    search = FakeSearchTool([hit("2305.00001", ref_title)])
    client = RecordingModelClient(
        json.dumps(
            [
                card(
                    "2305.00001",
                    url="https://arxiv.org/abs/2305.00001",
                    cited_by_paper=False,
                )
            ]
        )
    )
    agent = NoveltyResearchAgent(model_client=client)

    cards = agent.research(
        make_task(),
        paper,
        search_tool=search,
        full_text_tool=FakeFullTextTool(),
        metadata_tool=FakeMetadataTool(),
    )

    assert cards[0].cited_by_paper is True


def test_research_empty_candidates_returns_empty_without_model_call():
    search = FakeSearchTool([])
    client = RecordingModelClient("[]")
    agent = NoveltyResearchAgent(model_client=client)

    cards = agent.research(
        make_task(),
        make_paper(),
        search_tool=search,
        full_text_tool=FakeFullTextTool(),
        metadata_tool=FakeMetadataTool(),
    )

    assert cards == []
    assert client.calls == []


def test_research_paper_view_truncates_full_text():
    paper = make_paper()
    paper.full_text = "# Page 1\n封面信息\n\n摘 要\n" + "A" * 30000
    search = FakeSearchTool([hit("2305.00001", "Graph Neural Networks")])
    client = RecordingModelClient(
        json.dumps([card("2305.00001", url="https://arxiv.org/abs/2305.00001")])
    )
    agent = NoveltyResearchAgent(model_client=client, paper_excerpt_chars=1000)

    agent.research(
        make_task(),
        paper,
        search_tool=search,
        full_text_tool=FakeFullTextTool(),
        metadata_tool=FakeMetadataTool(),
    )

    messages, _ = client.calls[0]
    user = messages[1].content
    assert '"full_text_excerpt"' in user
    assert "封面信息" not in user
    assert "A" * 5000 not in user
    assert '"candidates"' in user


def test_research_accepts_single_card_object():
    """R1 等模型可能返回单张证据卡对象而非列表，绑定校验应兼容。"""

    search = FakeSearchTool([hit("2305.00001", "Graph Neural Networks")])
    client = RecordingModelClient(
        json.dumps(card("2305.00001", url="https://arxiv.org/abs/2305.00001"))
    )
    agent = NoveltyResearchAgent(model_client=client)

    cards = agent.research(
        make_task(),
        make_paper(),
        search_tool=search,
        full_text_tool=FakeFullTextTool(),
        metadata_tool=FakeMetadataTool(),
    )

    assert [item.card_id for item in cards] == ["CARD-2305.00001"]
