# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-4b07384acc6e4a9cbb6d11e4e0c96f9b
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "430dc1a41d55724e42a21b10e28d25146e931ed1c06e68a712de60006f4f3768", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-15T13:54:48.953100+00:00
End: 2026-09-15T13:57:48.714761+00:00
Duration: 180000 ms

## Environment

Git Branch: hyl
Git Commit: 44d7a1b045333d448bea63b77876fd11ae91ead2
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 63625 ms |
| resolve_subject_references | SUCCESS | 0 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 8890 ms |
| plan_research_task | SUCCESS | 7609 ms |
| plan_research_task | SUCCESS | 9219 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 57828 ms |
| run_research_task | SUCCESS | 46718 ms |
| run_research_task | SUCCESS | 33672 ms |
| validate_evidence | SUCCESS | 15 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 0 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 31829 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 14 ms |
| render_report | SUCCESS | 14 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 7 | 7 | 0 | 7 |
| database_search | 7 | 6 | 1 | 0 |
| reader | 14 | 13 | 1 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 14 | 1 | OTHER | `diagnostics/reader.json` |
| reference_namespace | ERROR | 14 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: OTHER=1

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 41
Input tokens: 371203
Cached input tokens: 288000
Output tokens: 15439
Reasoning tokens: 5691
Total tokens: 386642
Cost: RMB 0.47496000
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 41 | 371203 | 288000 | 15439 | 386642 | 0.47496000 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 0
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 0 | 1 | INSUFFICIENT |
| NP-3 | 0 | 1 | INSUFFICIENT |


## Reviewer Information Adjudication

### Stage stage_0013

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
| NP-3 | insufficient_evidence | - | 0 | True |


## Retrieval Coverage

### Stage stage_0013

Stage status: SUCCESS
Actual next stage: validate_synthesis_input

| Novelty Point | Coverage | Required Sources | Failed | Not Attempted | Zero Hit |
|---|---|---|---|---|---|
| NP-1 | complete | springer | - | - | - |
| NP-2 | complete | springer | - | - | springer |
| NP-3 | complete | springer | - | - | springer |


## Errors

- run_research_task / tool_0017: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0028: HarnessPolicyError: reader tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
