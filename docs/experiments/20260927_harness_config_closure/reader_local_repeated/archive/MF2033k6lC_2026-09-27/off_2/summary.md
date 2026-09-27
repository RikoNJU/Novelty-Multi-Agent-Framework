# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: off_2
Entrypoint: -
Input Identity: {}
Status: FAILED
Start: 2026-09-27T16:34:28.839879+00:00
End: 2026-09-27T16:34:40.907157+00:00
Duration: 12073 ms

## Environment

Git Branch: experiment/local-llm-baseline
Git Commit: b378e443e36d9d662c2e5c8937c4dfd25ee27bdc
Model: None / None
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| run_research_task | SUCCESS | 12050 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reader | 4 | 4 | 0 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | OK | 4 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | ERROR | 4 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | INCOMPLETE | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 5
Input tokens: 32660
Cached input tokens: 0
Output tokens: 207
Reasoning tokens: 0
Total tokens: 32867
Estimated API cost (RMB): Unknown (priced subtotal 0.00000000)
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 5 | 32660 | 0 | 207 | 32867 | Unknown (priced subtotal 0.00000000) | 5 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- None

## Integrity Gates

- None

## Last Completed Stage

run_research_task
