from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.reviewer_diagnostics import inspect_workspace


def _write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "outputs" / "paper"
    _write(
        workspace / "novelty-points.json",
        {"novelty_points": [{"point_id": "NP-1", "claim": "claim"}]},
    )
    _write(
        workspace / "evidence-cards.json",
        {
            "validator_accepted_cards": [
                {
                    "card_id": "C-1",
                    "novelty_point_id": "NP-1",
                    "evidence_ids": ["E-1"],
                }
            ]
        },
    )
    _write(
        workspace / "research-runs/NP-1/T-1/attempt-1.json",
        {
            "evidence": [
                {
                    "evidence_id": "E-1",
                    "work_id": "W-1",
                    "artifact_id": "A-1",
                    "novelty_point_id": "NP-1",
                    "quote": "must not appear in diagnostics",
                }
            ]
        },
    )
    _write(
        workspace / "novelty-reviews.json",
        {
            "reviews": [
                {
                    "novelty_point_id": "NP-1",
                    "status": "reviewed",
                    "verdict": "partially_novel",
                    "verdict_reason": "partial overlap",
                    "confidence": 0.8,
                    "highly_relevant_works": [
                        {
                            "work_id": "W-1",
                            "card_ids": ["C-1"],
                            "evidence_ids": ["E-1"],
                            "relevance_reason": "direct",
                        }
                    ],
                }
            ]
        },
    )
    _write(
        workspace / "runtime/run-1/stages/0001_review_evidence/meta.json",
        {
            "debug_details": {
                "reviewer_information_adjudication": {
                    "cards_preserved": True,
                    "missing_review_point_ids": [],
                    "unresolved_evidence_ids": [],
                }
            }
        },
    )
    _write(
        workspace / "runtime/run-1/tools/0001_reader.json",
        {
            "stage_name": "review_evidence",
            "execution_status": "SUCCESS",
            "resolved_arguments": {
                "artifact_id": "A-1",
                "char_start": 0,
                "max_chars": 100,
            },
            "raw_result": {"payload": {"read_result": {"text": "secret text"}}},
            "error": None,
        },
    )
    return workspace


def test_inspector_reports_closed_reviewer_artifacts_without_source_text(tmp_path):
    report = inspect_workspace(_workspace(tmp_path))
    assert report["ok"] is True
    assert report["counts"] == {
        "novelty_points": 1,
        "validator_accepted_cards": 1,
        "evidence": 1,
        "reviews": 1,
        "runtime_review_stages": 1,
        "reviewer_reader_calls": 1,
    }
    assert "must not appear" not in json.dumps(report)
    assert "secret text" not in json.dumps(report)
    assert report["reader_calls"][0]["artifact_id"] == "A-1"


def test_inspector_finds_missing_review_and_unresolved_evidence(tmp_path):
    workspace = _workspace(tmp_path)
    _write(
        workspace / "evidence-cards.json",
        {
            "validator_accepted_cards": [
                {
                    "card_id": "C-1",
                    "novelty_point_id": "NP-1",
                    "evidence_ids": ["E-missing"],
                }
            ]
        },
    )
    _write(workspace / "novelty-reviews.json", {"reviews": []})

    report = inspect_workspace(workspace)
    assert report["ok"] is False
    assert report["missing_review_point_ids"] == ["NP-1"]
    assert report["unresolved_evidence_ids"] == ["E-missing"]


def test_runtime_reviewer_records_are_isolated_by_run_id(tmp_path):
    workspace = _workspace(tmp_path)
    _write(
        workspace / "runtime/run-2/tools/0002_reader.json",
        {
            "stage_name": "review_evidence",
            "execution_status": "FAILED",
            "resolved_arguments": {"artifact_id": "A-2"},
            "error": {"type": "ValueError", "message": "missing"},
        },
    )

    run_1 = inspect_workspace(workspace, run_id="run-1")
    run_2 = inspect_workspace(workspace, run_id="run-2")

    assert run_1["counts"]["reviewer_reader_calls"] == 1
    assert run_1["reader_calls"][0]["artifact_id"] == "A-1"
    assert run_2["counts"]["reviewer_reader_calls"] == 1
    assert run_2["reader_calls"][0]["artifact_id"] == "A-2"
    assert run_2["counts"]["runtime_review_stages"] == 0


_REAL_REVIEW_FIXTURE = (
    Path(__file__).parent / "fixtures/reviewer/diagnostics_registered_evidence.json"
)


def _registered_evidence_workspace(tmp_path: Path):
    """Materialize one point from a completed real Reviewer run."""
    fixture = json.loads(_REAL_REVIEW_FIXTURE.read_text(encoding="utf-8"))
    workspace = tmp_path / "real-review"
    _write(workspace / "novelty-points.json", fixture["novelty_points"])
    _write(workspace / "evidence-cards.json", fixture["evidence_cards"])
    _write(workspace / "novelty-reviews.json", fixture["novelty_reviews"])
    _write(
        workspace / "research-runs/NP-1/T-1/attempt-1.json",
        fixture["research_attempt"],
    )
    return workspace, fixture


def test_inspector_accepts_registered_evidence_in_real_reviewer_fixture(tmp_path):
    workspace, fixture = _registered_evidence_workspace(tmp_path)

    report = inspect_workspace(workspace)

    assert report["ok"] is True, report["errors"]
    assert report["counts"]["evidence"] == 3
    assert report["unresolved_evidence_ids"] == []
    serialized = json.dumps(report, ensure_ascii=False)
    for item in fixture["research_attempt"]["evidence"]:
        assert item["quote"] not in serialized
    for item in fixture["novelty_reviews"]["reviews"][0]["review_evidence"]:
        assert item["exact_quote"] not in serialized


def test_registered_evidence_links_to_its_origin_card_without_base_citation(tmp_path):
    workspace, fixture = _registered_evidence_workspace(tmp_path)
    review = fixture["novelty_reviews"]["reviews"][0]
    review["highly_relevant_works"][0]["evidence_ids"] = [
        review["review_evidence"][0]["evidence_id"]
    ]
    _write(workspace / "novelty-reviews.json", fixture["novelty_reviews"])

    report = inspect_workspace(workspace)

    assert report["ok"] is True, report["errors"]


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        ("missing_origin", "ReviewEvidence references missing Card:"),
        ("cross_point", "cross-point ReviewEvidence:"),
        ("wrong_work", "ReviewEvidence outside Card/Work scope:"),
        ("duplicate_id", "duplicate ReviewEvidence ID:"),
        ("base_collision", "ReviewEvidence shadows original Evidence:"),
    ],
)
def test_inspector_rejects_invalid_registered_evidence_bindings(
    tmp_path, mutation, expected_error
):
    workspace, fixture = _registered_evidence_workspace(tmp_path)
    review = fixture["novelty_reviews"]["reviews"][0]
    addition = review["review_evidence"][0]
    if mutation == "missing_origin":
        addition["origin_card_id"] = "C-missing"
    elif mutation == "cross_point":
        addition["novelty_point_id"] = "NP-other"
    elif mutation == "wrong_work":
        addition["work_id"] = "W-other"
    elif mutation == "duplicate_id":
        review["review_evidence"].append(copy.deepcopy(addition))
    elif mutation == "base_collision":
        addition["evidence_id"] = (
            fixture["research_attempt"]["evidence"][0]["evidence_id"]
        )
    _write(workspace / "novelty-reviews.json", fixture["novelty_reviews"])

    report = inspect_workspace(workspace)

    assert report["ok"] is False
    assert any(error.startswith(expected_error) for error in report["errors"])


def test_registered_evidence_cannot_link_an_unrelated_card(tmp_path):
    workspace, fixture = _registered_evidence_workspace(tmp_path)
    review = fixture["novelty_reviews"]["reviews"][0]
    addition = review["review_evidence"][0]
    other_card = next(
        item for item in fixture["evidence_cards"]["validator_accepted_cards"]
        if item["card_id"] != addition["origin_card_id"]
    )
    review["highly_relevant_works"][0]["card_ids"] = [other_card["card_id"]]
    review["highly_relevant_works"][0]["evidence_ids"] = [addition["evidence_id"]]
    _write(workspace / "novelty-reviews.json", fixture["novelty_reviews"])

    report = inspect_workspace(workspace)

    assert report["ok"] is False
    assert (
        f"Card/Evidence link missing in RelevantWork: {other_card['card_id']}"
        in report["errors"]
    )


def test_registered_evidence_is_not_shared_between_reviews(tmp_path):
    workspace, fixture = _registered_evidence_workspace(tmp_path)
    other_review = copy.deepcopy(fixture["novelty_reviews"]["reviews"][0])
    evidence_id = other_review["review_evidence"][0]["evidence_id"]
    other_review["novelty_point_id"] = "NP-other"
    other_review["review_evidence"] = []
    fixture["novelty_reviews"]["reviews"].append(other_review)
    _write(workspace / "novelty-reviews.json", fixture["novelty_reviews"])

    report = inspect_workspace(workspace)

    assert report["ok"] is False
    assert f"review references missing Evidence: {evidence_id}" in report["errors"]


def test_registered_evidence_cannot_replace_missing_original_card_evidence(tmp_path):
    workspace, fixture = _registered_evidence_workspace(tmp_path)
    addition = fixture["novelty_reviews"]["reviews"][0]["review_evidence"][0]
    card = next(
        item for item in fixture["evidence_cards"]["validator_accepted_cards"]
        if item["card_id"] == addition["origin_card_id"]
    )
    card["evidence_ids"] = [addition["evidence_id"]]
    _write(workspace / "evidence-cards.json", fixture["evidence_cards"])

    report = inspect_workspace(workspace)

    assert report["ok"] is False
    assert report["unresolved_evidence_ids"] == [addition["evidence_id"]]
    assert (
        f"Card references missing Evidence: {addition['evidence_id']}"
        in report["errors"]
    )


def test_inspector_still_rejects_unknown_evidence_with_registered_evidence(tmp_path):
    workspace, fixture = _registered_evidence_workspace(tmp_path)
    work = fixture["novelty_reviews"]["reviews"][0]["highly_relevant_works"][0]
    work["evidence_ids"].append("E-missing")
    _write(workspace / "novelty-reviews.json", fixture["novelty_reviews"])

    report = inspect_workspace(workspace)

    assert report["ok"] is False
    assert "review references missing Evidence: E-missing" in report["errors"]
