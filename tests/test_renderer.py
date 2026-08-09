"""确定性 Markdown 报告 Renderer 测试。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from novelty_agent_framework.persistence import (
    persist_evidence_cards,
    persist_novelty_points,
    persist_report,
    persist_retrieval_plans,
    persist_workflow_input,
)
from novelty_agent_framework.schemas import (
    ConclusionLevel,
    EvidenceCard,
    EvidenceSource,
    NoveltyConclusion,
    NoveltyPoint,
    NoveltyReport,
    PaperInput,
    ResearchTask,
)
from novelty_agent_framework.tools.renderer import ReportRenderError, render_report


def seed_workspace() -> None:
    paper = PaperInput(
        paper_id="renderer-paper",
        title="Renderer Test | Paper",
        abstract="Test abstract.",
        full_text="# Test\n\nBody",
        keywords_en=["graph learning"],
    )
    point = NoveltyPoint(
        point_id="NP-1",
        claim="图学习方法",
        claim_en="Graph learning method",
    )
    task = ResearchTask(
        task_id="T1",
        novelty_point_id="NP-1",
        queries=["graph learning"],
    )
    card = EvidenceCard(
        card_id="C1",
        task_id="T1",
        novelty_point_id="NP-1",
        document_title="Related Paper",
        main_contribution="Related contribution",
        sources=[EvidenceSource(title="arXiv", url="https://arxiv.org/abs/1234.5678")],
        relevance=0.9,
        confidence=0.8,
    )
    report = NoveltyReport(
        paper_id=paper.paper_id,
        conclusions=[
            NoveltyConclusion(
                novelty_point_id="NP-1",
                level=ConclusionLevel.PARTIAL,
                summary="存在部分技术差异。",
                supporting_card_ids=["C1"],
                confidence=0.8,
            )
        ],
    )
    persist_workflow_input(paper)
    persist_novelty_points(paper, [point])
    persist_retrieval_plans(paper, [task], rounds=1, point_order=["NP-1"])
    persist_evidence_cards(
        paper,
        raw_cards=[card],
        accepted_cards=[card],
        rejected_evidence=[],
    )
    persist_report(paper, report)


def test_markdown_renderer_reads_workspace_and_uses_default_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    seed_workspace()

    path = render_report(paper_name="renderer-paper")
    content = path.read_text(encoding="utf-8")

    assert path == Path("outputs/renderer-paper/report/renderer-paper-report.md")
    assert "# 科技查新报告" in content
    assert "Renderer Test \\| Paper" in content
    assert "Graph learning method" in content
    assert "Related Paper" in content
    assert "存在部分技术差异" in content
    assert "{{" not in content


def test_renderer_rejects_unsupported_format() -> None:
    with pytest.raises(ReportRenderError, match="不支持的报告格式"):
        render_report(output_format="pdf", paper_name="renderer-paper")


def test_renderer_requires_all_workspace_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "outputs" / "incomplete").mkdir(parents=True)

    with pytest.raises(ReportRenderError, match="缺少报告输入产物"):
        render_report(paper_name="incomplete")


def test_custom_template_and_save_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    seed_workspace()
    template = tmp_path / "custom.md"
    template.write_text("# {{ paper_name }}\n\n{{ novelty_conclusions }}", encoding="utf-8")

    path = render_report(
        output_format="md",
        template_path=template,
        paper_name="renderer-paper",
        save_path=tmp_path / "custom-report",
    )

    assert path == tmp_path / "custom-report.md"
    assert json.loads(
        (tmp_path / "outputs/renderer-paper/report.json").read_text(encoding="utf-8")
    )["paper_id"] == "renderer-paper"
