"""收尾 JSON 稳健解析（Markdown 围栏/叙述剥离）单测。"""

from __future__ import annotations

from novelty_agent_framework.workflows.research_task import _extract_finish_json


def test_plain_json_passthrough() -> None:
    payload = '{"cards": []}'
    assert _extract_finish_json(payload) == payload


def test_fenced_json_is_unwrapped() -> None:
    payload = '{"cards": []}'
    fenced = f"```json\n{payload}\n```"
    assert _extract_finish_json(fenced) == payload


def test_prose_prefix_and_fence_are_stripped() -> None:
    fenced = (
        'I have the complete abstract. Here is the finish:\n'
        '```json\n{"cards": [{"main_contribution": "x"}]}\n```'
    )
    assert _extract_finish_json(fenced) == '{"cards": [{"main_contribution": "x"}]}'


def test_prose_without_fence_extracts_json_span() -> None:
    text = 'Based on my research: {"cards": []} thanks.'
    assert _extract_finish_json(text) == '{"cards": []}'


def test_empty_content_returns_empty() -> None:
    assert _extract_finish_json(None) == ""
    assert _extract_finish_json("") == ""
