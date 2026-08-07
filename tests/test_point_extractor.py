import json
from pathlib import Path

import pytest

from backend.env import ModelResponse, PromptLibrary
from novelty_agent_framework.agents import (
    DemoPointExtractor,
    NoveltyPointExtractorAgent,
    build_paper_digest,
)
from novelty_agent_framework.agents.point_extractor import _extract_points_list
from novelty_agent_framework.persistence import persist_novelty_points
from novelty_agent_framework.schemas import PaperDigest, PaperInput

PROMPTS_ROOT = Path("backend/src/novelty_agent_framework/prompts")


class SequencedClient:
    """按调用顺序返回预设 JSON，超出后重复最后一个。"""

    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls: list[tuple[list, object]] = []

    def complete(self, messages, *, options=None):
        self.calls.append((list(messages), options))
        index = min(len(self.calls) - 1, len(self.outputs) - 1)
        return ModelResponse(content=self.outputs[index])


POINT_ITEM = {
    "point_id": "X-1",
    "claim": "提出一种基于图摘要的大规模时序图表示学习方法",
    "technical_features": ["图摘要压缩", "图自编码器", "循环神经网络时序建模"],
    "source_locations": ["abstract"],
}


def three_items() -> list[dict]:
    return [
        dict(POINT_ITEM, point_id=f"X-{index}", claim=f"查新点{index}")
        for index in range(1, 4)
    ]


def make_paper() -> PaperInput:
    return PaperInput(
        paper_id="paper-1",
        title="测试论文",
        abstract="测试论文摘要",
        full_text="测试论文正文",
        claimed_contributions=["贡献一", "贡献二"],
    )


def make_agent(client) -> NoveltyPointExtractorAgent:
    return NoveltyPointExtractorAgent(
        model_client=client,
        prompts=PromptLibrary(PROMPTS_ROOT),
    )


def test_extractor_generates_then_reviews():
    client = SequencedClient([json.dumps(three_items()), json.dumps(three_items())])

    points = make_agent(client).extract(
        build_paper_digest(make_paper()),
        previous_brief=None,
        attempt=1,
    )

    assert [point.point_id for point in points] == ["NP-1", "NP-2", "NP-3"]
    assert len(client.calls) == 2  # 生成步 + 审查步
    second_system, second_user = client.calls[1][0]
    assert "审查" in second_system.content
    assert "候选查新点" in second_user.content


def test_extractor_generation_retries_then_review():
    singles = [
        dict(POINT_ITEM, point_id=f"X-{index}", claim=f"查新点{index}")
        for index in (1, 2, 3)
    ]
    client = SequencedClient(
        [
            json.dumps(singles[0]),
            json.dumps(singles[1]),
            json.dumps(singles[2]),
            json.dumps(three_items()),
        ]
    )

    points = make_agent(client).extract(
        build_paper_digest(make_paper()),
        previous_brief=None,
        attempt=1,
    )

    assert len(points) == 3
    assert len(client.calls) == 4  # 3 次生成重试 + 1 次审查


def test_extractor_incremental_retry_supplements():
    first = three_items()[:1]  # 查新点1
    supplement = three_items()[1:]  # 查新点2、查新点3
    client = SequencedClient(
        [json.dumps(first), json.dumps(supplement), json.dumps(three_items())]
    )

    points = make_agent(client).extract(
        build_paper_digest(make_paper()),
        previous_brief=None,
        attempt=1,
    )

    assert len(points) == 3
    assert len(client.calls) == 3  # 2 次生成（增量补充）+ 1 次审查
    second_gen_user = client.calls[1][0][1].content
    assert "查新点1" in second_gen_user  # 已生成的查新点反馈给重试


def test_extractor_review_dedupes_only():
    two = three_items()[:2]
    client = SequencedClient([json.dumps(two), json.dumps({"delete_indices": [1]})])

    points = make_agent(client).extract(
        build_paper_digest(make_paper()),
        previous_brief=None,
        attempt=1,
    )

    assert len(points) == 1  # 审查只去重，不强制数量


def test_extractor_review_deletes_by_index():
    client = SequencedClient(
        [json.dumps(three_items()), json.dumps({"delete_indices": [2]})]
    )

    points = make_agent(client).extract(
        build_paper_digest(make_paper()),
        previous_brief=None,
        attempt=1,
    )

    assert [point.claim for point in points] == ["查新点1", "查新点3"]


def test_extractor_review_never_empties():
    client = SequencedClient(
        [json.dumps(three_items()), json.dumps({"delete_indices": [1, 2, 3]})]
    )

    points = make_agent(client).extract(
        build_paper_digest(make_paper()),
        previous_brief=None,
        attempt=1,
    )

    assert len(points) == 3  # 不允许删空，全部保留


def test_extractor_single_object_passthrough():
    client = SequencedClient([json.dumps(POINT_ITEM), json.dumps(POINT_ITEM)])

    points = make_agent(client).extract(
        build_paper_digest(make_paper()),
        previous_brief=None,
        attempt=1,
    )

    assert len(points) == 1


def test_extractor_single_qualified_no_merge():
    client = SequencedClient([json.dumps(three_items()), json.dumps(three_items())])

    points = make_agent(client).extract(
        build_paper_digest(make_paper()),
        previous_brief=None,
        attempt=1,
    )

    assert len(client.calls) == 2  # 单次生成合格直接过，无重试
    assert [point.point_id for point in points] == ["NP-1", "NP-2", "NP-3"]
    _, review_user = client.calls[1][0]
    assert "查新点1" in review_user.content
    assert "查新点2" in review_user.content
    assert "查新点3" in review_user.content


def test_extractor_parse_fail_raises():
    client = SequencedClient(["not json"])
    with pytest.raises(ValueError, match="合法 JSON"):
        make_agent(client).extract(
            build_paper_digest(make_paper()),
            previous_brief=None,
            attempt=1,
        )


def test_extractor_rejects_non_list():
    client = SequencedClient(['{"a": 1}'])
    with pytest.raises(ValueError, match="顶层必须是列表"):
        make_agent(client).extract(
            build_paper_digest(make_paper()),
            previous_brief=None,
            attempt=1,
        )


def test_extractor_truncates_over_eight():
    ten = [
        dict(POINT_ITEM, point_id=f"X-{index}", claim=f"查新点{index}")
        for index in range(1, 11)
    ]
    client = SequencedClient([json.dumps(ten), json.dumps(ten[:8])])

    points = make_agent(client).extract(
        build_paper_digest(make_paper()),
        previous_brief=None,
        attempt=1,
    )

    assert len(points) == 8
    assert points[-1].point_id == "NP-8"


def test_extractor_accepts_object_wrapper():
    client = SequencedClient(
        [json.dumps({"novelty_points": three_items()}), json.dumps(three_items())]
    )
    points = make_agent(client).extract(
        build_paper_digest(make_paper()),
        previous_brief=None,
        attempt=1,
    )
    assert len(points) == 3


def test_extractor_accepts_nested_wrapper():
    client = SequencedClient(
        [
            json.dumps({"data": {"novelty_points": three_items()}}),
            json.dumps(three_items()),
        ]
    )
    points = make_agent(client).extract(
        build_paper_digest(make_paper()),
        previous_brief=None,
        attempt=1,
    )
    assert len(points) == 3


def test_extractor_skips_string_list_fields():
    client = SequencedClient(
        [
            json.dumps(
                {
                    "technical_features": ["基于图摘要技术的图压缩方法"],
                    "查新点": three_items(),
                }
            ),
            json.dumps(three_items()),
        ]
    )
    points = make_agent(client).extract(
        build_paper_digest(make_paper()),
        previous_brief=None,
        attempt=1,
    )
    assert len(points) == 3


def test_extractor_rejects_missing_claim():
    bad_item = dict(POINT_ITEM, claim="")
    client = SequencedClient([json.dumps([bad_item])])
    with pytest.raises(ValueError, match="格式错误"):
        make_agent(client).extract(
            build_paper_digest(make_paper()),
            previous_brief=None,
            attempt=1,
        )


def test_extract_points_list_robustness():
    item = POINT_ITEM
    assert _extract_points_list([item]) == [item]
    assert _extract_points_list({"novelty_points": [item]}) == [item]
    assert _extract_points_list({"data": {"points": [item]}}) == [item]
    assert _extract_points_list({"technical_features": ["x"], "查新点": [item]}) == [item]
    assert _extract_points_list(item) == [item]
    assert _extract_points_list({"a": 1}) is None
    assert _extract_points_list([]) == []


def test_demo_extractor_from_contributions():
    digest = PaperDigest(
        paper_id="p",
        title="标题",
        abstract="摘要",
        claimed_contributions=["贡献一", "贡献二"],
    )
    points = DemoPointExtractor().extract(digest, previous_brief=None, attempt=1)

    assert [point.point_id for point in points] == ["NP-1", "NP-2"]
    assert points[0].source_locations == ["claimed_contributions"]


def test_demo_extractor_falls_back_to_abstract():
    digest = PaperDigest(
        paper_id="p",
        title="标题",
        abstract="这是第一句创新点。这是第二句创新点。",
        claimed_contributions=[],
    )
    points = DemoPointExtractor().extract(digest, previous_brief=None, attempt=1)

    assert len(points) >= 2
    assert points[0].source_locations == ["abstract"]


def test_build_paper_digest_truncates():
    paper = PaperInput(
        paper_id="p",
        title="t",
        abstract="a",
        full_text="x" * 3000,
        references=["r" * 200] * 40,
    )
    digest = build_paper_digest(paper)

    assert digest.references == []  # 当前不向提取模型提供参考文献
    assert digest.full_text_excerpt.endswith("…[截断]")
    assert len(digest.full_text_excerpt) <= 2000 + len("…[截断]")


def test_persist_novelty_points_writes_file(tmp_path):
    paper = make_paper()
    points = DemoPointExtractor().extract(
        build_paper_digest(paper),
        previous_brief=None,
        attempt=1,
    )

    path = persist_novelty_points(paper, list(points), output_dir=tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))

    assert path.name == "paper-1.points.json"
    assert data["paper_id"] == "paper-1"
    assert data["storage"] == "test-version-local-file"
    assert "后续需替换为数据库" in data["note"]
    assert [point["point_id"] for point in data["novelty_points"]] == ["NP-1", "NP-2"]
