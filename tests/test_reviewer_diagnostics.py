from __future__ import annotations

import json
from pathlib import Path

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
