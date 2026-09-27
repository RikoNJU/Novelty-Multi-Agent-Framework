"""Replay frozen HTTP responses after the ID fix; no network or model calls."""
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "backend/src")]
from novelty_agent_framework.tools.database_search.providers.arxiv import parse_entry

original = OUT.parent / "20260928_arxiv_http_boundary"
before = json.loads((original / "identifier_audit.json").read_text())
rows = []
for filename, digest in before["input_sha256"].items():
    data = (original / filename).read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest
    entries = ET.fromstring(data).findall("{http://www.w3.org/2005/Atom}entry")
    expected = [row for row in before["rows"] if row["response_file"] == filename]
    assert len(entries) == len(expected)
    for entry, old in zip(entries, expected):
        hit = parse_entry(entry)
        assert hit.external_id == old["expected_external_id"]
        assert hit.document_id == old["expected_document_id"]
        assert hit.url == old["expected_url"]
        assert hit.full_text_url == "https://arxiv.org/pdf/" + old["expected_document_id"]
        rows.append({"original_atom_id": old["original_atom_id"], "document_id": hit.document_id,
                     "url": hit.url, "full_text_url": hit.full_text_url})
result = {"network_calls": 0, "model_calls": 0, "rows_verified": len(rows),
          "previous_mismatches": before["mismatched_rows"], "current_mismatches": 0,
          "input_sha256": before["input_sha256"], "rows": rows}
(OUT / "identifier_replay.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k not in {"input_sha256", "rows"}}))
