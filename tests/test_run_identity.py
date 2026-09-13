from __future__ import annotations

import hashlib

from novelty_agent_framework.core.run_identity import file_run_identity


def test_file_run_identity_uses_file_bytes_and_stable_repo_path(tmp_path) -> None:
    project = tmp_path / "project"
    paper = project / "fixtures" / "case" / "paper.json"
    paper.parent.mkdir(parents=True)
    paper.write_bytes(b'{"paper_id":"paper"}\n')

    identity = file_run_identity("paper_input", paper, project_root=project)

    assert identity["entrypoint"] == "paper_input"
    assert identity["input_identity"]["paper_json"] == "fixtures/case/paper.json"
    assert identity["input_identity"]["paper_sha256"] == hashlib.sha256(
        paper.read_bytes()
    ).hexdigest()
