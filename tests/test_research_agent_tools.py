"""Researcher 候选文献证据分析的单元测试（假工具 + 假模型）。"""

from __future__ import annotations

import json
import asyncio

import pytest

from backend.env import ModelResponse
from novelty_agent_framework.agents import NoveltyResearchAgent
from novelty_agent_framework.ports import FullText, SearchHit
from novelty_agent_framework.schemas import (
    CallToolAction,
    EvidenceSource,
    NoveltyPoint,
    ResearchTask,
    TaskResearchRequest,
)

QUOTE = "Dynamic neighbor sampling reduces communication overhead."


def hit(
    doc_id: str = "2305.00001",
    title: str = "Dynamic Graph Learning",
    *,
    abstract: str = QUOTE,
    doi: str | None = None,
) -> SearchHit:
    return SearchHit(
        document_id=doc_id,
        title=title,
        abstract=abstract,
        authors=("Alice", "Bob"),
        year=2023,
        doi=doi,
        url=f"https://arxiv.org/abs/{doc_id}",
    )


def card(
    doc_id: str = "2305.00001",
    *,
    title: str = "Dynamic Graph Learning",
    quote: str = QUOTE,
    url: str | None = None,
    doi: str | None = None,
    **overrides,
) -> dict:
    value = {
        "card_id": f"CARD-{doc_id}",
        "task_id": "TASK-1",
        "novelty_point_id": "NP-1",
        "document_title": title,
        "main_contribution": "提出动态邻居采样方法。",
        "overlaps": ["动态邻居采样"],
        "differences": ["应用范围不同"],
        "sources": [
            {
                "title": title,
                "quote": quote,
                "location": "abstract",
                "url": url or f"https://arxiv.org/abs/{doc_id}",
                "doi": doi,
            }
        ],
        "cited_by_paper": True,
        "relevance": 0.8,
        "confidence": 0.8,
    }
    value.update(overrides)
    return value


def make_task(*, point_id: str = "NP-1") -> ResearchTask:
    return ResearchTask(
        task_id="TASK-1",
        novelty_point_id=point_id,
        task_type="literature_search",
        language="en",
        description="检索动态邻居采样方法",
    )


def make_point(*, point_id: str = "NP-1") -> NoveltyPoint:
    return NoveltyPoint(
        point_id=point_id,
        claim="一种动态邻居采样方法",
        claim_en="A dynamic neighbor sampling method",
        technical_features=["动态邻居采样"],
    )


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
    def __init__(
        self,
        sources: dict[str, EvidenceSource] | None = None,
        *,
        fail: bool = False,
    ) -> None:
        self.sources = sources or {}
        self.fail = fail
        self.resolved: list[str] = []

    def resolve(self, document_id: str):
        self.resolved.append(document_id)
        if self.fail:
            raise RuntimeError("metadata unavailable")
        return self.sources.get(document_id)


class RecordingModelClient:
    def __init__(self, content: str) -> None:
        self.content = content
        self.calls: list[tuple[list, object]] = []

    def complete(self, messages, *, options=None):
        self.calls.append((list(messages), options))
        return ModelResponse(content=self.content)


class AsyncSequenceModelClient:
    def __init__(self, *contents: str) -> None:
        self.contents = list(contents)
        self.calls: list[list] = []

    async def acomplete(self, messages, *, options=None):
        self.calls.append(list(messages))
        return ModelResponse(content=self.contents.pop(0))


def test_candidate_is_analyzed_and_prompt_uses_point_not_paper() -> None:
    candidates = [hit(), hit("2305.00002", "Temporal Graph Learning")]
    full_text = FakeFullTextTool(
        {"2305.00001": f"Full text. {QUOTE}", "2305.00002": "Other text."}
    )
    metadata = FakeMetadataTool()
    client = RecordingModelClient(json.dumps([card()]))

    cards = NoveltyResearchAgent(model_client=client).research(
        make_task(),
        make_point(),
        candidates,
        full_text_tool=full_text,
        metadata_tool=metadata,
    )

    assert [item.card_id for item in cards] == ["CARD-2305.00001"]
    assert full_text.fetched == ["2305.00001", "2305.00002"]
    assert metadata.resolved == ["2305.00001", "2305.00002"]
    user_prompt = client.calls[0][0][1].content
    assert '"point"' in user_prompt
    assert '"candidates"' in user_prompt
    assert "paper_json" not in user_prompt


def test_empty_candidates_return_without_tools_or_model() -> None:
    client = RecordingModelClient("[]")
    full_text = FakeFullTextTool()
    metadata = FakeMetadataTool()

    cards = NoveltyResearchAgent(model_client=client).research(
        make_task(),
        make_point(),
        [],
        full_text_tool=full_text,
        metadata_tool=metadata,
    )

    assert cards == []
    assert client.calls == []
    assert full_text.fetched == []
    assert metadata.resolved == []


def test_task_point_mismatch_fails_before_model_call() -> None:
    client = RecordingModelClient("[]")
    with pytest.raises(ValueError, match="novelty_point_id"):
        NoveltyResearchAgent(model_client=client).research(
            make_task(point_id="NP-1"), make_point(point_id="NP-2"), [hit()]
        )
    assert client.calls == []


@pytest.mark.parametrize(
    "invalid_card",
    [
        card("9999.99999", title="Unknown Paper"),
        card(task_id="TASK-OTHER"),
        card(novelty_point_id="NP-OTHER"),
        card(quote="This sentence does not exist."),
    ],
)
def test_invalid_or_ungrounded_cards_are_rejected(invalid_card: dict) -> None:
    client = RecordingModelClient(json.dumps([invalid_card]))
    cards = NoveltyResearchAgent(model_client=client).research(
        make_task(), make_point(), [hit()]
    )
    assert cards == []


def test_grounded_quote_is_accepted_and_cited_flag_is_cleared() -> None:
    client = RecordingModelClient(json.dumps([card(cited_by_paper=True)]))
    cards = NoveltyResearchAgent(model_client=client).research(
        make_task(), make_point(), [hit()]
    )
    assert len(cards) == 1
    assert cards[0].cited_by_paper is None


def test_full_text_is_preferred_and_abstract_is_fallback() -> None:
    full_text_quote = "Full text provides stronger candidate evidence."
    client = RecordingModelClient(json.dumps([card(quote=full_text_quote)]))
    agent = NoveltyResearchAgent(model_client=client)

    cards = agent.research(
        make_task(),
        make_point(),
        [hit()],
        full_text_tool=FakeFullTextTool({"2305.00001": full_text_quote}),
    )
    assert len(cards) == 1
    payload = client.calls[0][0][1].content
    assert '"excerpt": "Full text provides stronger candidate evidence."' in payload
    assert '"text_source": "full_text"' in payload

    fallback_client = RecordingModelClient(json.dumps([card()]))
    NoveltyResearchAgent(model_client=fallback_client).research(
        make_task(),
        make_point(),
        [hit()],
        full_text_tool=FakeFullTextTool(),
    )
    fallback_payload = fallback_client.calls[0][0][1].content
    assert f'"excerpt": "{QUOTE}"' in fallback_payload
    assert '"text_source": "abstract"' in fallback_payload


def test_metadata_failure_falls_back_to_search_hit() -> None:
    client = RecordingModelClient(json.dumps([card()]))
    cards = NoveltyResearchAgent(model_client=client).research(
        make_task(),
        make_point(),
        [hit()],
        metadata_tool=FakeMetadataTool(fail=True),
    )
    assert len(cards) == 1


def test_binding_supports_doi_and_normalized_title() -> None:
    doi_client = RecordingModelClient(
        json.dumps([card(url=None, doi="https://doi.org/10.1000/XYZ")])
    )
    doi_card = json.loads(doi_client.content)[0]
    doi_card["sources"][0]["url"] = None
    doi_client.content = json.dumps([doi_card])
    assert NoveltyResearchAgent(model_client=doi_client).research(
        make_task(), make_point(), [hit(doi="10.1000/xyz")]
    )

    title_card = card(url=None)
    title_card["sources"][0]["url"] = None
    title_client = RecordingModelClient(json.dumps([title_card]))
    assert NoveltyResearchAgent(model_client=title_client).research(
        make_task(), make_point(), [hit()]
    )


def test_duplicate_cards_for_same_candidate_keep_first() -> None:
    first = card()
    second = card(card_id="CARD-SECOND")
    client = RecordingModelClient(json.dumps([first, second]))
    cards = NoveltyResearchAgent(model_client=client).research(
        make_task(), make_point(), [hit()]
    )
    assert [item.card_id for item in cards] == ["CARD-2305.00001"]


def test_single_card_object_is_supported() -> None:
    client = RecordingModelClient(json.dumps(card()))
    cards = NoveltyResearchAgent(model_client=client).research(
        make_task(), make_point(), [hit()]
    )
    assert [item.card_id for item in cards] == ["CARD-2305.00001"]


def test_decide_returns_strict_discriminated_action() -> None:
    client = AsyncSequenceModelClient(
        json.dumps(
            {
                "action": "call_tool",
                "tool_name": "reader",
                "arguments": {"artifact_id": "art_1"},
            }
        )
    )
    request = TaskResearchRequest(
        subject_paper_id="paper-1",
        run_id="run-1",
        novelty_point=make_point(),
        research_task=make_task(),
    )
    action = asyncio.run(
        NoveltyResearchAgent(model_client=client).decide(
            {
                "request": request,
                "tool_descriptions": [{"name": "reader"}],
                "observations": [],
            }
        )
    )
    assert isinstance(action, CallToolAction)
    assert action.tool_name == "reader"


def test_decide_repairs_invalid_json_once_then_fails() -> None:
    request = TaskResearchRequest(
        subject_paper_id="paper-1",
        run_id="run-1",
        novelty_point=make_point(),
        research_task=make_task(),
    )
    repaired = AsyncSequenceModelClient(
        "not-json",
        json.dumps(
            {
                "action": "finish",
                "draft": {
                    "cards": [],
                    "no_evidence_reason": "No grounded evidence found",
                },
            }
        ),
    )
    action = asyncio.run(
        NoveltyResearchAgent(model_client=repaired).decide({"request": request})
    )
    assert action.action == "finish"
    assert len(repaired.calls) == 2
    assert "不符合动作 schema" in repaired.calls[1][-1].content

    invalid = AsyncSequenceModelClient("{}", "{}")
    with pytest.raises(ValueError, match="连续返回非法动作"):
        asyncio.run(
            NoveltyResearchAgent(model_client=invalid).decide({"request": request})
        )
    assert len(invalid.calls) == 2
