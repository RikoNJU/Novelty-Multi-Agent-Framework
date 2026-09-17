"""Regression coverage for the zero-call single-point archive audit."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_audit_generates_six_local_compiler_units(tmp_path: Path) -> None:
    repo = Path(__file__).resolve().parents[1]
    output = tmp_path / "single-point"
    result = subprocess.run(
        [sys.executable, "scripts/single_point_stability_audit.py", "--repo", str(repo),
         "--output", str(output)],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    manifest = json.loads((output / "experiment-manifest.json").read_text())
    assert manifest["network"] == {
        "allow_model_calls": False,
        "allow_provider_calls": False,
        "allow_reader_fetch": False,
    }
    c1 = json.loads((output / "compiler-comparison/P4_C1/query-pool.json").read_text())
    assert c1["input_kind"] == "derived_projection"
    assert len(c1["strategies"]) == 16
    assert (output / "compiler-comparison/P6_C0/query-pool.json").is_file()
    findings = json.loads((output / "analysis/evidence-findings.json").read_text())
    assert all(item["c0_strategy_count"] == 3 and item["c0_dsl_count"] == 2
               for item in findings["findings"])
    report = (output / "report.md").read_text()
    assert "策略表达式不同" not in report
