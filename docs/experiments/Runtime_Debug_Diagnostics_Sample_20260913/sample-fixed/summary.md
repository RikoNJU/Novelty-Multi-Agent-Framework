# Runtime Summary

## Run

Paper ID: runtime-debug-sample
Run ID: sample-fixed
Status: PARTIAL
Start: 2026-09-13T14:01:39.364875+00:00
End: 2026-09-13T14:01:39.390232+00:00
Duration: 27 ms

## Environment

Git Branch: lya
Git Commit: 64f1ba6092960871bc1e98827db6086dfcd14e7c
Model: None / None
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| run_research_task | SUCCESS | 3 ms |
| validate_synthesis_input | SUCCESS | 0 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reader | 1 | 0 | 1 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader_failures | WARN | 1 | 1 | NEVER_PERSISTED | `diagnostics/reader_failures.json` |

reader_failures classifications: NEVER_PERSISTED=1

## Run Outcome

- point_id: NP-SAMPLE
- task_id: T-SAMPLE
- task_status: partial
- steps_used: 1
- read_count: 0
- evidence_count: 0
- card_count_before_gate_a: 1
- card_count_after_gate_a: 0
- gate_a_validation_passed: False
- gate_a_rejected_card_ids: ['CARD-SAMPLE']
- warning_count: 1

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

- None

## Reviewer Information Adjudication

- None

## Errors

- run_research_task / tool_0001: ValueError: unknown artifact_id 'art_missing' in the research or subject reference manifest

## Integrity Gates

- validate_synthesis_input: FAILED
  - CARD-SAMPLE: missing Evidence

## Last Completed Stage

validate_synthesis_input
