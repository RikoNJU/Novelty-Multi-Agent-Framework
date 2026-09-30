# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-480a9f6d8a59475f860887c3a6f45324
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-30T07:01:53.033620+00:00
End: 2026-09-30T07:09:58.347062+00:00
Duration: 485329 ms

## Environment

Git Branch: main
Git Commit: 2bd79ff672658605b3962d6833e121506751b7b9
Model: openai_compatible / qwen2.5-7b-instruct
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 25737 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 6264 ms |
| plan_research_task | SUCCESS | 6682 ms |
| plan_research_task | SUCCESS | 4724 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 53351 ms |
| run_research_task | SUCCESS | 45414 ms |
| run_research_task | SUCCESS | 95876 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 31647 ms |
| validate_synthesis_input | SUCCESS | 1 ms |
| check_final_evidence_sufficiency | SUCCESS | 2 ms |
| plan_supplement | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 6557 ms |
| plan_research_task | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 0 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 78364 ms |
| run_research_task | SUCCESS | 20141 ms |
| run_research_task | SUCCESS | 9424 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 68171 ms |
| validate_synthesis_input | SUCCESS | 3 ms |
| check_final_evidence_sufficiency | SUCCESS | 1 ms |
| synthesize_report | SUCCESS | 32388 ms |
| validate_report_integrity | SUCCESS | 1 ms |
| persist_report | SUCCESS | 2 ms |
| render_report | SUCCESS | 2 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| database_search | 5 | 5 | 0 | 2 |
| reference_search | 1 | 1 | 0 | 1 |
| reader | 6 | 6 | 0 | 0 |
| submit_evidence | 12 | 9 | 3 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | OK | 6 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | ERROR | 6 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 46
Input tokens: 318652
Cached input tokens: 0
Output tokens: 11754
Reasoning tokens: 0
Total tokens: 330406
Estimated API cost (RMB): Unknown (priced subtotal 0.00000000)
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 46 | 318652 | 0 | 11754 | 330406 | Unknown (priced subtotal 0.00000000) | 46 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 1
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: True
Actual next stage: plan_supplement

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 1 | 1 | PASS |
| NP-3 | 0 | 1 | INSUFFICIENT |

### Round 2

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
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 2 | 1 | PASS |
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
| NP-1 | insufficient_evidence | - | 0 | True |
| NP-2 | insufficient_evidence | - | 1 | True |
| NP-3 | insufficient_evidence | - | 0 | True |

### Stage stage_0025

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
| NP-2 | insufficient_evidence | - | 2 | True |
| NP-3 | insufficient_evidence | - | 0 | True |


## Errors

- run_research_task / tool_0011: ValidationError: 1 validation error for EvidenceCheckpointArguments
cards
  List should have at least 1 item after validation, not 0 [type=too_short, input_value=[], input_type=list]
    For further information visit https://errors.pydantic.dev/2.13/v/too_short
- run_research_task / tool_0013: ValidationError: 1 validation error for EvidenceCheckpointArguments
cards
  List should have at least 1 item after validation, not 0 [type=too_short, input_value=[], input_type=list]
    For further information visit https://errors.pydantic.dev/2.13/v/too_short
- run_research_task / tool_0017: ValidationError: 1 validation error for EvidenceCheckpointArguments
cards
  List should have at least 1 item after validation, not 0 [type=too_short, input_value=[], input_type=list]
    For further information visit https://errors.pydantic.dev/2.13/v/too_short

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
