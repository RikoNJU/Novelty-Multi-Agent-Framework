# Integrity Gates V1

The workflow has two deterministic integrity stages:

```text
review_evidence
→ validate_synthesis_input
→ check_final_evidence_sufficiency
...
→ synthesize_report
→ validate_report_integrity
→ persist_report
→ render_report
```

`validate_synthesis_input` checks only cards that are about to enter the final
evidence sufficiency check and synthesis. It verifies card identity and task
ownership, resolves every Evidence reference, validates Evidence-to-Artifact-to-Work relationships, and
uses the current paper's `ReferenceStore` to verify Artifact path containment,
existence, and SHA-256. Character locators are compared with persisted UTF-8
text using the same whitespace normalization as `EvidenceCardBuilder`.

Cards that fail are removed from `state["evidence_cards"]` and added to the
existing rejected-evidence and workflow-issue collections. Other cards and
novelty points continue, so the sufficiency check counts the final accepted
card set. Gate-only rejection reasons are retained for audit but excluded from
the rejected-evidence list passed to report synthesis, preventing integrity
diagnostics from leaking into the formal report. Any point below the configured
final valid Card threshold is still passed through normally as a structured
`insufficient_final_evidence` fact.

`validate_report_integrity` checks exact NoveltyPoint conclusion counts,
unknown or cross-point Card references, duplicate references, and overlap
between supporting and counter references. A failed validation never changes
the `NoveltyReport` and never blocks `persist_report` or `render_report`.

Both stages have normal runtime execution status when their validators execute
successfully—even when `validation_passed` is false. Detailed counts, rejected
cards, and reasons are recorded in the stage artifacts and the Runtime Summary;
they are not inserted into the formal report.

## Retrieval Coverage Gate (V1)

Retrieval coverage is a deterministic fact, never a model judgement. Before
Reviewer verdicts are persisted, `review_evidence` aggregates every
`database_search` execution recorded in the task products
(`TaskResearchResult.retrieval_executions`, which keeps failed executions that
`research_bundles` deliberately drops) into one state per NoveltyPoint:

| State | Meaning |
|---|---|
| `complete` | Every required source executed with no failed or degraded execution (zero hits allowed) |
| `partial` | Some required source failed, degraded, or was never executed |
| `failed` | Every attempted required-source execution failed |
| `not_attempted` | No execution recorded for any required source |
| `unconfigured` | No decidable required source in configuration |

Required sources are the configured providers with `enabled=true` and without
`testing_only` (currently arXiv only; `null_catalog` is a test stub whose zero
hits can never count as evidence).

Only `complete` permits absence-based verdicts (`novel`, `partially_novel`).
Under any other state those verdicts are rewritten to `insufficient_evidence`
(`highly_relevant_works` is preserved as a retrieved fact) and a
`retrieval_coverage_insufficient` workflow issue is recorded. Positive findings
(`not_novel`) are never downgraded: they rest on retrieved evidence, not on
absence.

The facts are recorded in the `review_evidence` stage artifact, in the Runtime
Summary (`retrieval_coverage_checks`) and `summary.md`
(`## Retrieval Coverage`), and passed to `synthesize_report` so that
`limitations` can distinguish retrieval failure from a successful zero-hit
search.

### Zero-card reporting

When a NoveltyPoint ends with zero accepted cards the per-point Reviewer never
runs (it short-circuits), so the cause is stated by code rather than by the
model: `zero_card_reason()` renders one deterministic sentence per coverage
state, and `review_evidence` writes it into the review's `supplement_request`.
`coverage_limitations()` then appends the same facts to the report
`limitations` inside `synthesize_report`, so "retrieval failed", "search ran
with zero hits" and "no search was attempted" can no longer collapse into the
same sentence. Points with complete coverage and at least one card get no
extra line.
