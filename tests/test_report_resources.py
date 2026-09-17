"""Published report resources remain verifiable without a workflow service."""

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from novelty_agent_framework.config import NoveltyWebSettings
from novelty_agent_framework.core.report_binding import assemble_report_from_draft
from novelty_agent_framework.main import create_app
from novelty_agent_framework.schemas import (
    EvidenceCard, NoveltyPoint, NoveltyPointReview, ReportNarrativeDraft,
    ReviewStatus, NoveltyVerdict,
)
from novelty_agent_framework.services.report_resources import ReportResourceError, ReportResourceStore


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bundle(root: Path, *, count: int = 3) -> Path:
    root.mkdir()
    points = [NoveltyPoint(point_id=f"P-{i}", claim=f"claim {i}") for i in range(count)]
    cards = [EvidenceCard(card_id=f"C-{i}", task_id="T-1", novelty_point_id=point.point_id,
                          document_title="shared work", main_contribution="body", relevance=.8,
                          confidence=.8) for i, point in enumerate(points)]
    reviews = [NoveltyPointReview(
        novelty_point_id=point.point_id,
        status=ReviewStatus.INSUFFICIENT_EVIDENCE if i in ({0, 2} if count >= 3 else {0}) else ReviewStatus.REVIEWED,
        verdict=None if i in ({0, 2} if count >= 3 else {0}) else NoveltyVerdict.NOVEL,
        verdict_reason=None if i in ({0, 2} if count >= 3 else {0}) else "original judgment",
        confidence=None if i in ({0, 2} if count >= 3 else {0}) else .8,
        incomplete_reason="technical_error" if i == 0 else "semantic_evidence" if i == 2 else None,
    ) for i, point in enumerate(points)]
    draft_data = {"conclusions": [{"novelty_point_id": point.point_id,
        "summary": "short", "supporting_card_ids": [cards[i].card_id],
        "counter_card_ids": []} for i, point in enumerate(points)], "limitations": []}
    draft = ReportNarrativeDraft.model_validate(draft_data)
    report = assemble_report_from_draft(draft, paper_id="paper-X", novelty_points=points,
                                        novelty_reviews=reviews, evidence_cards=cards)
    (root / "report.json").write_text(report.model_dump_json(indent=2))
    (root / "report.md").write_text("# 恢复报告\n\n" + "\n".join(p.point_id for p in points))
    response = {"status": "SUCCESS", "finish_reason": "stop",
                "response": {"content": json.dumps(draft_data)}}
    (root / "live-response.json").write_text(json.dumps(response))
    audit = {"paper_id": "paper-X", "source_input_sha256": "source-hash",
             "source_run_manifest": {"status": "FAILED", "run_id": "runtime-source", "paper_id": "paper-X"},
             "novelty_points": [p.model_dump(mode="json") for p in points],
             "novelty_reviews": [r.model_dump(mode="json") for r in reviews],
             "evidence_cards": [c.model_dump(mode="json") for c in cards],
             "rejected_evidence": []}
    (root / "audit.json").write_text(json.dumps(audit))
    (root / "synthesis-input.json").write_text(json.dumps({
        "novelty_points": audit["novelty_points"],
        "novelty_reviews": audit["novelty_reviews"],
        "evidence_cards": audit["evidence_cards"],
        "rejected_evidence": [],
    }))
    audit["source_input_sha256"] = _sha((root / "synthesis-input.json").read_bytes())
    (root / "audit.json").write_text(json.dumps(audit))
    provenance = {"source_run_id": "failed-source", "source_runtime_id": "runtime-source",
                  "source_run_status": "FAILED", "live_recovery_id": "live-answer",
                  "assembly_id": "captured-assembly", "report_kind": "captured_response_reassembly",
                  "paper_id": "paper-X", "upstream_recomputed": False,
                  "source_issues": [{"point_id": r.novelty_point_id,
                                     "review_status": r.status.value,
                                     "incomplete_reason": r.incomplete_reason} for r in reviews]}
    (root / "provenance.json").write_text(json.dumps(provenance))
    files = {name: {"sha256": _sha((root / name).read_bytes()),
                    "bytes": (root / name).stat().st_size, "mime": mime}
             for name, mime in (("report.md", "text/markdown"),
                                ("report.json", "application/json"),
                                ("provenance.json", "application/json"))}
    manifest = {**provenance, "source_input_sha256": audit["source_input_sha256"],
                "live_response_sha256": _sha((root / "live-response.json").read_bytes()),
                "files": files}
    (root / "manifest.json").write_text(json.dumps(manifest))
    return root


@pytest.mark.parametrize("count", [1, 3, 8])
def test_register_is_idempotent_and_serves_verified_bytes_without_workflow(tmp_path, monkeypatch, count):
    bundle = _bundle(tmp_path / "bundle", count=count)
    moved = tmp_path / "moved"
    shutil.copytree(bundle, moved)
    bundle = moved
    store = ReportResourceStore(tmp_path / "registry")
    preview = store.register(bundle, dry_run=True)
    assert not store.root.exists()
    item = store.register(bundle)
    assert item["report_resource_id"] == preview["report_resource_id"]
    assert store.register(bundle) == item
    different = tmp_path / "different"
    shutil.copytree(bundle, different)
    (different / "report.md").write_text("different published bytes")
    different_manifest = json.loads((different / "manifest.json").read_text())
    changed = (different / "report.md").read_bytes()
    different_manifest["files"]["report.md"] = {"sha256": _sha(changed), "bytes": len(changed),
                                                  "mime": "text/markdown"}
    (different / "manifest.json").write_text(json.dumps(different_manifest))
    with pytest.raises(ReportResourceError, match="different content"):
        store.register(different)
    import novelty_agent_framework.main as main
    monkeypatch.setattr(main, "build_real_workflow_service", lambda _: (_ for _ in ()).throw(RuntimeError("no key")))
    app = create_app(NoveltyWebSettings(workflow_mode="real"), report_resources_root=store.root,
                     static_root=tmp_path / "no-frontend")
    with TestClient(app) as client:
        base = f"/api/novelty/report-artifacts/{item['report_resource_id']}"
        metadata = client.get(base)
        assert metadata.status_code == 200
        assert metadata.json()["source_run_status"] == "FAILED"
        assert client.get(base + "/content").content == (bundle / "report.md").read_bytes()
        attachment = client.get(base + "/download")
        assert attachment.content == (bundle / "report.md").read_bytes()
        assert "attachment" in attachment.headers["content-disposition"]
        assert attachment.headers["content-type"].startswith("text/markdown")
        assert client.get(base + "/provenance").json()["source_run_id"] == "failed-source"
        assert client.get("/api/novelty/runs/failed-source").status_code == 503
        assert client.get("/api/novelty/report-artifacts/../../etc/passwd").status_code != 200
        assert client.get("/api/novelty/report-artifacts/%2e%2e%2fetc").status_code != 200
        assert client.get("/api/novelty/report-artifacts/rr-00000000000000000000000000000000").status_code == 404


def test_tampering_conflicts_missing_files_and_symlink_are_rejected(tmp_path):
    bundle = _bundle(tmp_path / "bundle")
    store = ReportResourceStore(tmp_path / "registry")
    item = store.register(bundle)
    resource_id = item["report_resource_id"]
    (bundle / "report.md").write_text("altered")
    with pytest.raises(ReportResourceError, match="Hash or size mismatch"):
        store.register(bundle)
    target = store.root / resource_id / "report.md"
    target.write_text("altered")
    with pytest.raises(ReportResourceError, match="Published file changed"):
        store.get(resource_id)
    target.unlink()
    target.symlink_to(tmp_path / "outside")
    with pytest.raises(ReportResourceError, match="Missing or linked"):
        store.get(resource_id)


def test_wrong_lineage_or_review_cannot_publish(tmp_path):
    bundle = _bundle(tmp_path / "bundle")
    audit_path = bundle / "audit.json"
    audit = json.loads(audit_path.read_text())
    audit["novelty_reviews"][1]["verdict_reason"] = "changed authority"
    audit_path.write_text(json.dumps(audit))
    with pytest.raises(ReportResourceError, match="Audit projection differs"):
        ReportResourceStore(tmp_path / "registry").register(bundle)


def test_corrupt_index_or_manifest_is_not_served(tmp_path):
    bundle = _bundle(tmp_path / "bundle")
    store = ReportResourceStore(tmp_path / "registry")
    resource_id = store.register(bundle)["report_resource_id"]
    index_path = store.root / "index.json"
    index = json.loads(index_path.read_text())
    index[resource_id] = "0" * 64
    index_path.write_text(json.dumps(index))
    with pytest.raises(ReportResourceError, match="manifest changed"):
        store.get(resource_id)
    index_path.unlink()
    with pytest.raises(ReportResourceError, match="not registered"):
        store.get(resource_id)


def test_missing_published_file_has_distinct_error(tmp_path):
    bundle = _bundle(tmp_path / "bundle")
    store = ReportResourceStore(tmp_path / "registry")
    resource_id = store.register(bundle)["report_resource_id"]
    (store.root / resource_id / "report.md").unlink()
    with pytest.raises(ReportResourceError) as exc:
        store.get(resource_id)
    assert exc.value.code == "missing_artifact"
