# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: review-saved-card
Entrypoint: -
Input Identity: {}
Status: FAILED
Start: 2026-09-27T20:15:15.504591+00:00
End: 2026-09-27T20:15:36.746144+00:00
Duration: 21249 ms

## Environment

Git Branch: experiment/local-llm-baseline
Git Commit: 145723771fb615916f1fdd8199b21c603d31b59c
Model: None / None
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| review_card | SUCCESS | 21211 ms |
| summarize_review | FAILED | 2 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | OK | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | INCOMPLETE | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 1
Input tokens: 5044
Cached input tokens: 0
Output tokens: 854
Reasoning tokens: 0
Total tokens: 5898
Estimated API cost (RMB): Unknown (priced subtotal 0.00000000)
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 1 | 5044 | 0 | 854 | 5898 | Unknown (priced subtotal 0.00000000) | 1 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- summarize_review / -: KeyError: 'index'
- - / -: KeyError: 'index'

## Integrity Gates

- None

## Last Completed Stage

review_card
