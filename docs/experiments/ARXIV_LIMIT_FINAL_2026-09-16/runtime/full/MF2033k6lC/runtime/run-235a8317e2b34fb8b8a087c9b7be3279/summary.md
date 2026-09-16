# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-235a8317e2b34fb8b8a087c9b7be3279
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T04:15:57.092428+00:00
End: 2026-09-16T04:32:21.227606+00:00
Duration: 986265 ms

## Environment

Git Branch: fix/arxiv-rate-limit-final
Git Commit: 674c7ff7657a3dda7a4dddd9d39d5b88344a2f05
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 131949 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3234 ms |
| plan_research_task | SUCCESS | 6031 ms |
| plan_research_task | SUCCESS | 3030 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 508536 ms |
| run_research_task | SUCCESS | 228112 ms |
| run_research_task | SUCCESS | 427403 ms |
| validate_evidence | SUCCESS | 3 ms |
| review_evidence | SUCCESS | 94080 ms |
| validate_synthesis_input | SUCCESS | 7 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| plan_supplement | SUCCESS | 41439 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 16681 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 138512 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 23903 ms |
| validate_synthesis_input | SUCCESS | 9 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 18163 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 3 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 23 | 21 | 2 | 0 |
| database_search | 8 | 7 | 1 | 2 |
| reader | 43 | 43 | 0 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 43 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 43 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=28

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 100
Input tokens: 1413576
Cached input tokens: 35072
Output tokens: 44750
Reasoning tokens: 13165
Total tokens: 1458326
Cost: RMB 4.54878360
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 100 | 1413576 | 35072 | 44750 | 1458326 | 4.54878360 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 2
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: True
Actual next stage: plan_supplement

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 1 | 1 | PASS |
| NP-2 | 1 | 1 | PASS |
| NP-3 | 0 | 1 | INSUFFICIENT |

### Round 2

Configured cut: 1
Stage status: SUCCESS
Check status: PASS
Input final valid Cards: 3
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 1 | 1 | PASS |
| NP-2 | 1 | 1 | PASS |
| NP-3 | 1 | 1 | PASS |


## Reviewer Information Adjudication

### Stage stage_0012

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
| NP-1 | reviewed | partially_novel | 1 | False |
| NP-2 | reviewed | partially_novel | 1 | True |
| NP-3 | insufficient_evidence | - | 0 | True |

### Stage stage_0021

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
| NP-1 | reviewed | partially_novel | 1 | True |
| NP-2 | reviewed | partially_novel | 1 | True |
| NP-3 | reviewed | partially_novel | 1 | False |


## Errors

- run_research_task / tool_0008: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0015: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0058: HarnessPolicyError: reference_search tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
