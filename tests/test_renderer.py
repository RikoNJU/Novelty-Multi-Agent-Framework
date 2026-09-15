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
    EvidenceCard,
    EvidenceSource,
    NoveltyConclusion,
    NoveltyPoint,
    NoveltyReport,
    NoveltyVerdict,
    PaperInput,
    RelevantWork,
    ResearchTask,
    SearchConcept,
    SearchPlan,
    ReviewStatus,
    SearchStrategy,
)
from novelty_agent_framework.tools.renderer import (
    ReportRenderError,
    _format_conclusions,
    render_report,
)


def seed_workspace(output_root: str | Path = "outputs") -> None:
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
        task_type="literature_search",
        language="en",
        description="graph learning",
    )
    plan = SearchPlan(
        task_id="T1",
        novelty_point_id="NP-1",
        concepts=[
            SearchConcept(concept_id="C1", name="graph learning", terms=["graph learning"])
        ],
        strategies=[SearchStrategy(strategy_id="S1", level="strict", expression="C1")],
    )
    card = EvidenceCard(
        card_id="C1",
        task_id="T1",
        novelty_point_id="NP-1",
        document_title="Related Paper",
        main_contribution="Related contribution",
        sources=[
            EvidenceSource(
                title="arXiv",
                url="https://arxiv.org/abs/1234.5678",
                quote="Exact source text.",
                location="artifact art_x chars:0-18",
            )
        ],
        relevance=0.9,
        confidence=0.8,
    )
    report = NoveltyReport(
        paper_id=paper.paper_id,
        conclusions=[
            NoveltyConclusion(
                novelty_point_id="NP-1",
                review_status=ReviewStatus.REVIEWED,
                verdict=NoveltyVerdict.PARTIALLY_NOVEL,
                verdict_reason="既有工作覆盖部分特征。",
                summary="存在部分技术差异。",
                supporting_card_ids=["C1"],
                confidence=0.8,
                highly_relevant_works=[
                    RelevantWork(
                        work_id="work-1",
                        card_ids=["C1"],
                        evidence_ids=["E1"],
                        relevance_reason="直接覆盖核心特征。",
                    )
                ],
            )
        ],
    )
    persist_workflow_input(paper, output_root=output_root)
    persist_novelty_points(paper, [point], output_root=output_root)
    persist_retrieval_plans(
        paper,
        [task],
        search_plans=[plan],
        executed_queries=[
            {
                "database": "arxiv",
                "novelty_point_id": "NP-1",
                "task_id": "T1",
                "strategy_id": "S1",
                "level": "strict",
                "query": 'all:"graph learning"',
            }
        ],
        rounds=1,
        point_order=["NP-1"],
        output_root=output_root,
    )
    persist_evidence_cards(
        paper,
        raw_cards=[card],
        accepted_cards=[card],
        rejected_evidence=[],
        output_root=output_root,
    )
    persist_report(paper, report, output_root=output_root)


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
    assert "引文：Exact source text." in content
    assert "位置：artifact art_x chars:0-18" in content
    assert "存在部分技术差异" in content
    assert "Reviewer 裁定：** 部分新颖" in content
    assert "work-1：直接覆盖核心特征" in content
    assert "最终有效证据数量" in content
    assert "| NP-1 | 1 | 有证据 |" in content
    assert "{{" not in content


def test_attachments_list_retrieved_candidates_and_card_sources(tmp_path: Path) -> None:
    seed_workspace(tmp_path)
    workspace = tmp_path / "renderer-paper"
    references = workspace / "references" / "list.json"
    references.parent.mkdir(parents=True, exist_ok=True)
    references.write_text(json.dumps({"source_records": [
        {"title": "AliGraph: A Comprehensive Graph Neural Network Platform",
         "landing_url": "https://arxiv.org/abs/1902.08730",
         "full_text_url": "https://arxiv.org/pdf/1902.08730"},
        {"title": "AliGraph duplicate", "landing_url": "http://arxiv.org/abs/1902.08730"},
        {"title": "Candidate without an evidence card", "landing_url": "https://doi.org/10.1/example"},
        {"title": "Local artifact", "landing_url": "file:///tmp/private.txt"},
    ]}), encoding="utf-8")
    content = render_report(paper_name="renderer-paper", output_root=tmp_path).read_text()
    attachments = content.split("### 检索到的文献", 1)[1]
    expected = "AliGraph: A Comprehensive Graph Neural Network Platform：[https://arxiv.org/pdf/1902.08730](https://arxiv.org/pdf/1902.08730)"
    assert expected in attachments
    assert "AliGraph duplicate" not in attachments
    assert "Candidate without an evidence card：[https://doi.org/10.1/example](https://doi.org/10.1/example)" in attachments
    assert "Related Paper：[https://arxiv.org/pdf/1234.5678](https://arxiv.org/pdf/1234.5678)" in attachments
    assert "file:///" not in attachments


@pytest.mark.parametrize(
    ("status", "verdict", "expected"),
    [
        ("reviewed", "novel", "新颖"),
        ("reviewed", "partially_novel", "部分新颖"),
        ("reviewed", "not_novel", "不新颖"),
        ("insufficient_evidence", None, "证据不足，无法裁定"),
    ],
)
def test_renderer_uses_authoritative_report_verdict(status, verdict, expected):
    rendered = _format_conclusions(
        [
            {
                "novelty_point_id": "NP-1",
                "review_status": status,
                "verdict": verdict,
                "verdict_reason": None if verdict is None else "review reason",
                "confidence": None if verdict is None else 0.75,
                "summary": "report summary",
                "highly_relevant_works": [],
            }
        ],
        {"NP-1": {"claim": "claim"}},
    )

    assert f"Reviewer 裁定：** {expected}" in rendered
    if verdict == "not_novel":
        assert "弱创新" not in rendered


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


def test_renderer_reads_only_the_requested_output_root(tmp_path: Path) -> None:
    run_root = tmp_path / "runs" / "0002"
    seed_workspace(run_root)

    path = render_report(paper_name="renderer-paper", output_root=run_root)

    assert path == run_root / "renderer-paper/report/renderer-paper-report.md"
    assert path.is_file()
    assert not (tmp_path / "outputs" / "renderer-paper").exists()
