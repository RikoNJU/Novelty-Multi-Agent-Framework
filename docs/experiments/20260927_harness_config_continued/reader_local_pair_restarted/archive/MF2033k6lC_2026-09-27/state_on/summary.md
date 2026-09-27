# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: state_on
Entrypoint: -
Input Identity: {}
Status: SUCCESS
Start: 2026-09-27T15:03:01.707472+00:00
End: 2026-09-27T15:03:36.273648+00:00
Duration: 34573 ms

## Environment

Git Branch: experiment/local-llm-baseline
Git Commit: b378e443e36d9d662c2e5c8937c4dfd25ee27bdc
Model: None / None
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| run_research_task | SUCCESS | 34548 ms |

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

Calls: 6
Input tokens: 35386
Cached input tokens: 0
Output tokens: 1355
Reasoning tokens: 0
Total tokens: 36741
Estimated API cost (RMB): Unknown (priced subtotal 0.00000000)
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 6 | 35386 | 0 | 1355 | 36741 | Unknown (priced subtotal 0.00000000) | 6 |

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
