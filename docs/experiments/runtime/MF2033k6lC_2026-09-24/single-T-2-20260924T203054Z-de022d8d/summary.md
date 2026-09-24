# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: single-T-2-20260924T203054Z-de022d8d
Entrypoint: single_task
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": "NP-1", "task_id": "T-2", "search_plan_id": "T-2"}
Status: SUCCESS
Start: 2026-09-24T20:30:54.946920+00:00
End: 2026-09-24T20:30:55.036161+00:00
Duration: 107 ms

## Environment

Git Branch: experiment/local-llm-baseline
Git Commit: d4e4039a81acb92edd7d6c15a2c7809068e3eda6
Model: None / None
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| run_research_task | SUCCESS | 64 ms |
| validate_synthesis_input | SUCCESS | 0 ms |

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

- point_id: NP-1
- task_id: T-2
- task_status: partial
- steps_used: 0
- read_count: 0
- evidence_count: 0
- card_count_before_gate_a: 0
- card_count_after_gate_a: 0
- gate_a_validation_passed: True
- gate_a_rejected_card_ids: []
- warning_count: 1

## LLM Token Usage and Cost

Calls: 1
Input tokens: 0
Cached input tokens: 0
Output tokens: 0
Reasoning tokens: 0
Total tokens: 0
Cost: RMB 0.00000000
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 1 | 0 | 0 | 0 | 0 | 0.00000000 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- None

## Integrity Gates

- validate_synthesis_input: PASS

## Last Completed Stage

validate_synthesis_input
