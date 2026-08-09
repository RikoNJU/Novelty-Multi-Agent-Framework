"""按 paper 隔离的本地产物目录测试。"""

from __future__ import annotations

import json

from novelty_agent_framework.persistence import (
    paper_workspace,
    persist_evidence_cards,
    persist_report,
    persist_retrieval_plans,
)
from novelty_agent_framework.schemas import (
    EvidenceCard,
    EvidenceSource,
    PaperInput,
    NoveltyReport,
    RejectedEvidence,
    ResearchTask,
    SearchConcept,
    SearchPlan,
    SearchStrategy,
)


def make_paper() -> PaperInput:
    return PaperInput(
        paper_id="paper-one",
        title="Paper One",
        full_text="body",
    )


def make_task(task_id: str, point_id: str, query: str, attempt: int) -> ResearchTask:
    return ResearchTask(
        task_id=task_id,
        novelty_point_id=point_id,
        task_type="literature_search",
        language="en",
        description=query,
        attempt=attempt,
    )


def make_plan(task: ResearchTask, term: str) -> SearchPlan:
    return SearchPlan(
        task_id=task.task_id,
        novelty_point_id=task.novelty_point_id,
        concepts=[SearchConcept(concept_id="C1", name=term, terms=[term])],
        strategies=[SearchStrategy(strategy_id="S1", level="strict", expression="C1")],
    )


def test_workspace_creates_required_directories(tmp_path) -> None:
    workspace = paper_workspace(make_paper(), output_root=tmp_path)

    assert (workspace / "paper-input" / "images").is_dir()
    assert (workspace / "paper-input" / "others").is_dir()
    assert (workspace / "report").is_dir()


def test_retrieval_plans_group_tasks_by_novelty_point_order(tmp_path) -> None:
    tasks = [
        make_task("T2", "NP-2", "query two", 1),
        make_task("T1", "NP-1", "query one", 1),
        make_task("T1-R2", "NP-1", "query retry", 2),
    ]

    path = persist_retrieval_plans(
        make_paper(),
        tasks,
        search_plans=[
            make_plan(tasks[0], "query two"),
            make_plan(tasks[1], "query one"),
            make_plan(tasks[2], "query retry"),
        ],
        executed_queries=[
            {
                "database": "arxiv",
                "novelty_point_id": task.novelty_point_id,
                "task_id": task.task_id,
                "strategy_id": "S1",
                "level": "strict",
                "query": query,
            }
            for task, query in zip(tasks, ["query two", "query one", "query retry"])
        ],
        rounds=2,
        point_order=["NP-1", "NP-2", "NP-3"],
        output_root=tmp_path,
    )
    data = json.loads(path.read_text(encoding="utf-8"))

    plans = data["novelty_point_plans"]
    assert [plan["novelty_point_id"] for plan in plans] == ["NP-1", "NP-2", "NP-3"]
    assert [task["task_id"] for task in plans[0]["research_tasks"]] == ["T1", "T1-R2"]
    assert plans[0]["query_plan"] == {
        "queries": ["query one", "query retry"],
        "attempts": [1, 2],
    }
    assert len(plans[0]["search_plans"]) == 2
    assert len(plans[0]["executed_queries"]) == 2
    assert plans[2]["research_tasks"] == []


def test_evidence_cards_keep_raw_accepted_and_rejected_results(tmp_path) -> None:
    paper = make_paper()
    card = EvidenceCard(
        card_id="C1",
        task_id="T1",
        novelty_point_id="NP-1",
        document_title="Related",
        main_contribution="Contribution",
        sources=[EvidenceSource(title="Related", url="https://example.test")],
        relevance=0.9,
        confidence=0.9,
    )

    path = persist_evidence_cards(
        paper,
        raw_cards=[card],
        accepted_cards=[card],
        rejected_evidence=[RejectedEvidence(card_id="C2", reason="low relevance")],
        output_root=tmp_path,
    )
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["raw_evidence_cards"][0]["card_id"] == "C1"
    assert data["accepted_evidence_cards"][0]["card_id"] == "C1"
    assert data["rejected_evidence"] == [{"card_id": "C2", "reason": "low relevance"}]


def test_report_is_written_at_paper_workspace_root(tmp_path) -> None:
    paper = make_paper()
    report = NoveltyReport(paper_id=paper.paper_id, limitations=["demo limitation"])

    path = persist_report(paper, report, output_root=tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))

    assert path == tmp_path / "paper-one" / "report.json"
    assert data == report.model_dump(mode="json")
