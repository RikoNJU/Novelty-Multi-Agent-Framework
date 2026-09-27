# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: state_off
Entrypoint: -
Input Identity: {}
Status: FAILED
Start: 2026-09-27T15:02:38.099756+00:00
End: 2026-09-27T15:03:01.663283+00:00
Duration: 23571 ms

## Environment

Git Branch: experiment/local-llm-baseline
Git Commit: b378e443e36d9d662c2e5c8937c4dfd25ee27bdc
Model: None / None
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| run_research_task | SUCCESS | 23543 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reader | 9 | 8 | 1 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 9 | 1 | OTHER | `diagnostics/reader.json` |
| reference_namespace | ERROR | 9 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | INCOMPLETE | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: OTHER=1

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 10
Input tokens: 75976
Cached input tokens: 0
Output tokens: 426
Reasoning tokens: 0
Total tokens: 76402
Estimated API cost (RMB): Unknown (priced subtotal 0.00000000)
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 10 | 75976 | 0 | 426 | 76402 | Unknown (priced subtotal 0.00000000) | 10 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- run_research_task / tool_0009: HarnessPolicyError: total tool-call budget exhausted

## Integrity Gates

- None

## Last Completed Stage

run_research_task
