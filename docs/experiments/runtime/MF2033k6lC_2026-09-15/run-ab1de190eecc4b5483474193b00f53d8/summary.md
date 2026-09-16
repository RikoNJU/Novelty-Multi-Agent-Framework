# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-ab1de190eecc4b5483474193b00f53d8
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "430dc1a41d55724e42a21b10e28d25146e931ed1c06e68a712de60006f4f3768", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-15T14:00:29.384242+00:00
End: 2026-09-15T14:07:12.060432+00:00
Duration: 402969 ms

## Environment

Git Branch: hyl
Git Commit: 44d7a1b045333d448bea63b77876fd11ae91ead2
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 113125 ms |
| resolve_subject_references | SUCCESS | 0 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 14016 ms |
| plan_research_task | SUCCESS | 3405 ms |
| plan_research_task | SUCCESS | 10078 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 64203 ms |
| run_research_task | SUCCESS | 72155 ms |
| run_research_task | SUCCESS | 38188 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 136954 ms |
| validate_synthesis_input | SUCCESS | 15 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 52125 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 32 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 5 | 5 | 0 | 5 |
| database_search | 5 | 5 | 0 | 0 |
| reader | 22 | 21 | 1 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 22 | 1 | OTHER | `diagnostics/reader.json` |
| reference_namespace | ERROR | 22 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: OTHER=1

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 46
Input tokens: 420915
Cached input tokens: 334592
Output tokens: 24085
Reasoning tokens: 9836
Total tokens: 445000
Cost: RMB 0.57611160
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 46 | 420915 | 334592 | 24085 | 445000 | 0.57611160 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 2
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 1 | 1 | PASS |
| NP-3 | 1 | 1 | PASS |


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
| NP-2 | reviewed | partially_novel | 1 | True |
| NP-3 | insufficient_evidence | - | 0 | True |


## Retrieval Coverage

### Stage stage_0013

Stage status: SUCCESS
Actual next stage: validate_synthesis_input

| Novelty Point | Coverage | Required Sources | Failed | Not Attempted | Zero Hit |
|---|---|---|---|---|---|
| NP-1 | partial | springer | - | - | - |
| NP-2 | complete | springer | - | - | - |
| NP-3 | complete | springer | - | - | springer |


## Errors

- run_research_task / tool_0027: HarnessPolicyError: reader tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
