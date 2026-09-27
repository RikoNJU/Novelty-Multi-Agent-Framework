"""Literal coverage retention; no model or keyword-based semantic oracle."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from backend.env import ModelResponse
from novelty_agent_framework.agents.point_extractor import NoveltyPointExtractorAgent, _validated_deletion_mappings
from novelty_agent_framework.core.point_coverage import guard_deletions, merge_same_claim
from novelty_agent_framework.schemas import NoveltyPoint, PaperDigest


class Client:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = 0
    def complete(self, messages, *, options=None):
        self.calls += 1
        return ModelResponse(content=json.dumps(next(self.replies), ensure_ascii=False))


def point(claim, features, **kwargs):
    return NoveltyPoint(point_id="model-id", claim=claim, technical_features=features, **kwargs)


def extract(replies, *, conservative=True, digest=None):
    client = Client(replies)
    agent = NoveltyPointExtractorAgent(client, conservative_dedup=conservative)
    result = agent.extract(digest or PaperDigest(paper_id="p"), previous_brief=None, attempt=1)
    return result, agent.last_trace, client.calls


def generation(points):
    return {"novelty_points": [p.model_dump(mode="json") for p in points]}


def test_incremental_same_claim_retains_all_features_and_source_locations():
    first = point("same claim", ["first feature"], technical_features_en=["first"], source_locations=["s1"])
    increment = point("same claim", ["second feature"], technical_features_en=["second"], source_locations=["s2"])
    result, trace, calls = extract([generation([first]), generation([increment, point("other", ["third"])]),
        generation([point("third claim", ["fourth"])]), {"deletions": []}])
    assert result[0].technical_features == ["first feature", "second feature"]
    assert result[0].technical_features_en == ["first", "second"]
    assert result[0].source_locations == ["s1", "s2"]
    ledger = trace["coverage_ledger"]
    assert len(ledger["candidates"]) == 4
    assert all(feature["final_point_ids"] for feature in ledger["features"])
    assert calls == 4
    assert trace["scope_status"] == "pending_coverage"  # source support remains unknown
    assert ledger["source_coverage_status"] == "unknown_no_explicit_author_units"


def test_duplicates_in_one_generation_are_merged_without_losing_increment():
    rows = [point("same", ["a"]), point("same", ["b"]), point("other", ["c"])]
    result, trace, calls = extract([generation(rows), generation([point("third", ["d"])]), {"deletions": []}])
    assert len(result) == 3
    assert result[0].technical_features == ["a", "b"]
    assert len(trace["coverage_ledger"]["candidates"]) == 4
    assert calls == 3


def test_coverage_followup_same_claim_keeps_new_features():
    originals = [point("a", ["a1"]), point("b", ["b1"]), point("c", ["c1"])]
    result, trace, _ = extract([generation(originals),
        {"deletions": [{"index": 3, "duplicate_of": 1, "reason": "model proposal"}]},
        generation([point("a", ["new mechanism"], source_locations=["new source"])])], conservative=False)
    assert result[0].technical_features == ["a1", "new mechanism"]
    assert result[0].source_locations == ["new source"]
    assert len(trace["coverage_ledger"]["candidates"]) == 4
    assert trace["coverage_complete"] is False  # legacy deletion still lost c1


def test_literal_subset_is_a_retention_proof_not_semantic_equivalence():
    points = [point("same", ["a", "b"]), point("same", ["a"])]
    audit = _validated_deletion_mappings({"deletions": [{"index": 2, "duplicate_of": 1, "reason": "same"}]}, 2)
    result = guard_deletions(points, audit, enabled=True)
    assert len(result["accepted_deletions"]) == 1
    proof = result["accepted_deletions"][0]["coverage_proof"]
    assert proof["literal_coverage_proven"] is True
    assert proof["semantic_equivalence_verified"] is False


@pytest.mark.parametrize("source,target", [
    (point("claim A", ["feature"]), point("claim B", ["feature"])),
    (point("same", ["a", "b"]), point("same", ["a"])),
    (point("same", []), point("same", [])),
    (point("same", ["a"], claim_en="different English"), point("same", ["a"], claim_en="English")),
    (point("same", ["Mechanism"]), point("same", ["mechanism"])),
])
def test_unproven_literal_coverage_keeps_proposed_deletion_pending(source, target):
    audit = _validated_deletion_mappings({"deletions": [{"index": 1, "duplicate_of": 2, "reason": "similar"}]}, 2)
    result = guard_deletions([source, target], audit, enabled=True)
    assert result["accepted_deletions"] == []
    assert result["pending_indices"] == [1]
    assert result["coverage_issues"]


def test_featureless_experiment_remains_pending_not_confirmed_contribution():
    rows = [point("mechanism", ["a"]), point("other mechanism", ["b"]), point("accuracy experiment", [])]
    result, trace, calls = extract([generation(rows), {"deletions": []}])
    assert len(result) == 3 and calls == 2
    pending = trace["coverage_ledger"]["final_points"][2]
    assert pending["status"] == "pending_technical_features"
    assert pending["independent_contribution_confirmed"] is False
    assert trace["coverage_complete"] is False


def test_author_claims_and_bounded_excerpt_are_preserved_with_explicit_unknown():
    digest = PaperDigest(paper_id="p", claimed_contributions=["literal claim", "different author statement"],
        full_text_excerpt="opening\n\n[作者贡献段 1]\nfull bounded author passage")
    _, trace, _ = extract([generation([point("literal claim", ["a"]), point("second", ["b"]), point("third", ["c"])]),
        {"deletions": []}], digest=digest)
    rows = trace["coverage_ledger"]["source_units"]
    assert len(rows) == 3
    assert rows[0]["final_point_ids"] == ["NP-1"]
    assert rows[0]["semantic_support_verified"] is False
    assert rows[1]["status"] == rows[2]["status"] == "pending_source_alignment"
    assert rows[2]["text"] == "full bounded author passage"
    assert trace["coverage_complete"] is False


def test_conflicting_english_claim_is_not_silently_certified_by_union():
    first = point("same", ["a"], claim_en="English A")
    second = point("same", ["b"], claim_en="English B")
    result, trace, _ = extract([generation([first]), generation([second, point("other", ["c"]), point("third", ["d"])]),
        {"deletions": []}])
    assert result[0].technical_features == ["a", "b"]
    occurrence = trace["coverage_ledger"]["candidates"][1]
    assert occurrence["original"]["claim_en"] == "English B"
    assert occurrence["status"] == "pending_semantic_mapping"
    assert trace["coverage_complete"] is False


def test_frozen_historical_dsgnn_mapping_preserves_candidates_and_features():
    path = Path(__file__).parent / "fixtures/extractor/historical_dedup_20260924.json"
    fixture = json.loads(path.read_text())
    original = copy.deepcopy(fixture)
    # This is the same four-candidate payload used by the historical local pair.
    assert hashlib.sha256(json.dumps(fixture["deduplication_input"], ensure_ascii=False, sort_keys=True).encode()).hexdigest() == \
        "a1ffb46772154fcb1ff7e043f63cb8ba8c37c503dd4f00a2fd9a0b8dc989f464"
    rows = [NoveltyPoint.model_validate(item) for item in fixture["candidates"]]
    replies = [generation(rows), fixture["mapped_response"], {"novelty_points": []}]
    digest = PaperDigest.model_validate(fixture["digest"])
    legacy, old_trace, old_calls = extract(copy.deepcopy(replies), conservative=False, digest=digest)
    guarded, trace, calls = extract(copy.deepcopy(replies), conservative=True, digest=digest)
    assert len(legacy) == 2
    assert old_trace["coverage_ledger"]["candidate_features_preserved"] is False
    assert old_trace["coverage_complete"] is False
    assert [p.claim for p in guarded] == [p.claim for p in rows]
    assert [p.technical_features for p in guarded] == [p.technical_features for p in rows]
    assert trace["deduplication"]["deleted_indices"] == []
    assert trace["deduplication"]["pending_indices"] == [2, 3]
    assert trace["coverage_ledger"]["candidate_features_preserved"] is True
    assert trace["coverage_complete"] is False  # unresolved semantic/source claims are not certified
    assert len(trace["coverage_ledger"]["features"]) >= 12
    assert calls == 2 and old_calls == 3
    assert fixture == original


def test_dedup_transport_failure_still_exposes_pending_candidate_ledger():
    model = Client([generation([point("a", ["a1"]), point("b", ["b1"]), point("c", ["c1"])])])
    agent = NoveltyPointExtractorAgent(model)
    with pytest.raises(StopIteration):
        agent.extract(PaperDigest(paper_id="p", claimed_contributions=["source"]), previous_brief=None, attempt=1)
    ledger = agent.last_trace["coverage_ledger"]
    assert len(ledger["candidates"]) == 3
    assert all(row["status"] == "pending_unmapped_candidate" for row in ledger["candidates"])
    assert ledger["coverage_complete"] is False


def test_over_budget_original_candidates_are_pending_instead_of_absent_from_ledger():
    oversized = [point(f"original claim {i}", [f"feature {i}"]) for i in range(10)]
    accepted = oversized[:3]
    _, trace, calls = extract([generation(oversized), generation(accepted), {"deletions": []}])
    ledger = trace["coverage_ledger"]
    rejected_rows = [row for row in ledger["candidates"] if row["status"] == "pending_invalid_candidate_batch"]
    assert len(rejected_rows) == 10
    assert [row["original"]["claim"] for row in rejected_rows] == [p.claim for p in oversized]
    assert all(row["final_point_ids"] == [] for row in rejected_rows)
    assert ledger["unresolved_generation_errors"]
    assert ledger["coverage_complete"] is False
    assert calls == 3
