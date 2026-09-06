# Integrity Gates V1

The workflow has two deterministic integrity stages:

```text
review_evidence
→ validate_synthesis_input
→ assess_coverage
...
→ synthesize_report
→ validate_report_integrity
→ persist_report
→ render_report
```

`validate_synthesis_input` checks only cards that are about to enter coverage
and synthesis. It verifies card identity and task ownership, resolves every
Evidence reference, validates Evidence-to-Artifact-to-Work relationships, and
uses the current paper's `ReferenceStore` to verify Artifact path containment,
existence, and SHA-256. Character locators are compared with persisted UTF-8
text using the same whitespace normalization as `EvidenceCardBuilder`.

Cards that fail are removed from `state["evidence_cards"]` and added to the
existing rejected-evidence and workflow-issue collections. Other cards and
novelty points continue, so coverage is calculated from the final accepted
card set. Gate-only rejection reasons are retained for audit but excluded from
the rejected-evidence list passed to report synthesis, preventing integrity
diagnostics from leaking into the formal report; the resulting coverage gap is
still passed through normally.

`validate_report_integrity` checks exact NoveltyPoint conclusion counts,
unknown or cross-point Card references, duplicate references, and overlap
between supporting and counter references. A failed validation never changes
the `NoveltyReport` and never blocks `persist_report` or `render_report`.

Both stages have normal runtime execution status when their validators execute
successfully—even when `validation_passed` is false. Detailed counts, rejected
cards, and reasons are recorded in the stage artifacts and the Runtime Summary;
they are not inserted into the formal report.
