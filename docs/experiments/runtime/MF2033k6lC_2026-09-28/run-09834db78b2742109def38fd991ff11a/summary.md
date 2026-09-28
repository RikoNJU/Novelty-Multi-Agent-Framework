# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-09834db78b2742109def38fd991ff11a
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-28T07:03:08.764259+00:00
End: 2026-09-28T07:09:01.550153+00:00
Duration: 352802 ms

## Environment

Git Branch: experiment/local-llm-baseline
Git Commit: 7e71dc96b24f87e8ea8fed2fa5b761dfaef53a83
Model: openai_compatible / qwen2.5-7b-instruct
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 35666 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 4860 ms |
| plan_research_task | SUCCESS | 6869 ms |
| plan_research_task | SUCCESS | 8495 ms |
| plan_research_task | SUCCESS | 6550 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 45346 ms |
| run_research_task | SUCCESS | 38853 ms |
| run_research_task | SUCCESS | 34494 ms |
| run_research_task | SUCCESS | 33068 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 91109 ms |
| validate_synthesis_input | SUCCESS | 3 ms |
| check_final_evidence_sufficiency | SUCCESS | 2 ms |
| synthesize_report | SUCCESS | 47060 ms |
| validate_report_integrity | SUCCESS | 2 ms |
| persist_report | SUCCESS | 2 ms |
| render_report | SUCCESS | 2 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| database_search | 4 | 4 | 0 | 1 |
| reader | 3 | 3 | 0 | 0 |
| submit_evidence | 3 | 3 | 0 | 0 |
| reference_search | 1 | 1 | 0 | 1 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | OK | 3 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | ERROR | 3 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 28
Input tokens: 154605
Cached input tokens: 0
Output tokens: 8734
Reasoning tokens: 0
Total tokens: 163339
Estimated API cost (RMB): Unknown (priced subtotal 0.00000000)
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 28 | 154605 | 0 | 8734 | 163339 | Unknown (priced subtotal 0.00000000) | 28 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
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
| NP-4 | 0 | 1 | INSUFFICIENT |


## Reviewer Information Adjudication

### Stage stage_0014

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
| NP-1 | insufficient_evidence | - | 1 | True |
| NP-2 | insufficient_evidence | - | 0 | True |
| NP-3 | insufficient_evidence | - | 1 | True |
| NP-4 | insufficient_evidence | - | 0 | True |


## Errors

- None

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
