"""Coordinator JSON 解析韧性与 synthesize 重试契约。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.env import ModelResponse, PromptLibrary
from novelty_agent_framework.agents import NoveltyCoordinatorAgent
from novelty_agent_framework.schemas import (
    ConclusionLevel,
    NoveltyBrief,
    NoveltyConclusion,
    NoveltyPoint,
    NoveltyReport,
    PaperInput,
)

PROMPTS_ROOT = Path("backend/src/novelty_agent_framework/prompts")


class SequenceClient:
    """按顺序返回预设内容的模型客户端，并记录调用次数。"""

    def __init__(self, *contents: str) -> None:
        self.contents = list(contents)
        self.calls = 0

    def complete(self, messages, *, options=None):
        content = self.contents[min(self.calls, len(self.contents) - 1)]
        self.calls += 1
        return ModelResponse(content=content)


def _paper() -> PaperInput:
    return PaperInput(paper_id="paper-1", title="测试论文", full_text="正文")


def _brief() -> NoveltyBrief:
    return NoveltyBrief(
        paper_summary="摘要",
        research_problem="测试论文",
        novelty_points=[
            NoveltyPoint(point_id="NP-1", claim="claim", claim_en="claim_en")
        ],
        research_tasks=[],
    )


def _report_json() -> str:
    return json.dumps(
        {
            "paper_id": "paper-1",
            "conclusions": [
                {
                    "novelty_point_id": "NP-1",
                    "level": "partial",
                    "summary": "存在部分技术差异",
                    "supporting_card_ids": ["C1"],
                    "counter_card_ids": [],
                    "confidence": 0.8,
                }
            ],
            "missing_references": [],
            "missing_baselines": [],
            "citation_issues": [],
            "limitations": [],
        },
        ensure_ascii=False,
    )


def _agent(client: SequenceClient) -> NoveltyCoordinatorAgent:
    return NoveltyCoordinatorAgent(
        model_client=client,
        prompts=PromptLibrary(PROMPTS_ROOT),
    )


def test_synthesize_accepts_markdown_fenced_json() -> None:
    prefix = "下面是报告：\n\n```json\n"
    suffix = "\n```"
    client = SequenceClient(prefix + _report_json() + suffix)
    report = _agent(client).synthesize(
        _paper(),
        brief=_brief(),
        evidence=[],
        rejected_evidence=[],
        coverage_gaps=[],
    )
    assert isinstance(report, NoveltyReport)
    assert report.paper_id == "paper-1"
    assert report.conclusions[0].level is ConclusionLevel.PARTIAL
    assert client.calls == 1


def test_synthesize_retries_once_when_first_response_is_not_json() -> None:
    client = SequenceClient("抱歉，输出如下：\n不是 JSON", _report_json())
    report = _agent(client).synthesize(
        _paper(),
        brief=_brief(),
        evidence=[],
        rejected_evidence=[],
        coverage_gaps=[],
    )
    assert isinstance(report, NoveltyReport)
    assert client.calls == 2


def test_synthesize_fails_after_both_attempts() -> None:
    client = SequenceClient("still not json", "still not json")
    agent = _agent(client)
    with pytest.raises(ValueError, match="不是合法 JSON"):
        agent.synthesize(
            _paper(),
            brief=_brief(),
            evidence=[],
            rejected_evidence=[],
            coverage_gaps=[],
        )
    assert client.calls == 2

