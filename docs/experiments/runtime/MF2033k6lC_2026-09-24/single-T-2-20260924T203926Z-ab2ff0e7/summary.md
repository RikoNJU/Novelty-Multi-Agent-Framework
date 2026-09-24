# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: single-T-2-20260924T203926Z-ab2ff0e7
Entrypoint: single_task
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": "NP-1", "task_id": "T-2", "search_plan_id": "T-2"}
Status: SUCCESS
Start: 2026-09-24T20:39:26.678431+00:00
End: 2026-09-24T20:41:38.878535+00:00
Duration: 132216 ms

## Environment

Git Branch: experiment/local-llm-baseline
Git Commit: d4e4039a81acb92edd7d6c15a2c7809068e3eda6
Model: None / None
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| run_research_task | SUCCESS | 132166 ms |
| validate_synthesis_input | SUCCESS | 1 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| database_search | 2 | 1 | 1 | 0 |
| reader | 16 | 16 | 0 | 8 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | OK | 16 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | ERROR | 16 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- point_id: NP-1
- task_id: T-2
- task_status: completed
- steps_used: 20
- read_count: 16
- evidence_count: 0
- card_count_before_gate_a: 0
- card_count_after_gate_a: 0
- gate_a_validation_passed: True
- gate_a_rejected_card_ids: []
- warning_count: 7

## LLM Token Usage and Cost

Calls: 20
Input tokens: 185631
Cached input tokens: 0
Output tokens: 3790
Reasoning tokens: 0
Total tokens: 189421
Cost: RMB 0.00000000
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 20 | 185631 | 0 | 3790 | 189421 | 0.00000000 | 20 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- run_research_task / tool_0001: ToolExecutionError: all 1 search executions failed

## Integrity Gates

- validate_synthesis_input: PASS

## Last Completed Stage

validate_synthesis_input
