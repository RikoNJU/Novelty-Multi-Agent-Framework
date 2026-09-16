# Runtime Summary

## Run

Paper ID: demo-paper-001
Run ID: run-e072d7f46c7f49e597ce00b81ab064b3
Entrypoint: -
Input Identity: {}
Status: SUCCESS
Start: 2026-09-15T17:04:14.212056+00:00
End: 2026-09-15T17:04:14.494026+00:00
Duration: 312 ms

## Environment

Git Branch: hyl
Git Commit: 44d7a1b045333d448bea63b77876fd11ae91ead2
Model: None / None
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 0 ms |
| resolve_subject_references | SUCCESS | 0 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 0 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 0 ms |
| validate_evidence | SUCCESS | 15 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 0 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 0 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 16 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | ERROR | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 0
Input tokens: 0
Cached input tokens: 0
Output tokens: 0
Reasoning tokens: 0
Total tokens: 0
Cost: RMB 0.00000000
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: PASS
Input final valid Cards: 2
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 1 | 1 | PASS |
| NP-2 | 1 | 1 | PASS |


## Reviewer Information Adjudication

### Stage stage_0015

Stage status: SUCCESS
Cards preserved: True
Supplement requests control route: False
Missing reviews: []
Unexpected reviews: []
Duplicate reviews: []
Unresolved Evidence IDs: []
Actual next stage: validate_synthesis_input

| Novelty Point | Status | Verdict | Relevant Works | Supplement |
|---|---|---|---:|---|
| NP-1 | insufficient_evidence | - | 0 | True |
| NP-2 | insufficient_evidence | - | 0 | True |


## Retrieval Coverage

### Stage stage_0015

Stage status: SUCCESS
Actual next stage: validate_synthesis_input

| Novelty Point | Coverage | Required Sources | Failed | Not Attempted | Zero Hit |
|---|---|---|---|---|---|
| NP-1 | unconfigured | - | - | - | - |
| NP-2 | unconfigured | - | - | - | - |


## Errors

- None

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: FAILED
  - supporting/counter conflict: NP-1 -> CARD-NP-1-T-1
  - supporting/counter conflict: NP-2 -> CARD-NP-2-T-1

## Last Completed Stage

render_report
