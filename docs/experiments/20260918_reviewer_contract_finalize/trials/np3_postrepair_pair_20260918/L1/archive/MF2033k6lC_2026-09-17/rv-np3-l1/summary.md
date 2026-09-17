# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: rv-np3-l1
Entrypoint: -
Input Identity: {}
Status: SUCCESS
Start: 2026-09-17T17:19:34.271438+00:00
End: 2026-09-17T17:23:10.675417+00:00
Duration: 216415 ms

## Environment

Git Branch: lya
Git Commit: 60ae645feb0421f61af9eb574158cf6e68d1c1e9
Model: siliconflow / deepseek-ai/DeepSeek-V4-Flash
Python: 3.12.3

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| review_card | SUCCESS | 32922 ms |
| review_card | SUCCESS | 15242 ms |
| summarize_reviews | SUCCESS | 58233 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reader | 6 | 6 | 0 | 2 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 6 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 6 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | INCOMPLETE | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=4

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 9
Input tokens: 50079
Cached input tokens: 768
Output tokens: 5059
Reasoning tokens: 0
Total tokens: 55138
Cost: RMB 0.19369440
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 9 | 50079 | 768 | 5059 | 55138 | 0.19369440 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- None

## Integrity Gates

- None

## Last Completed Stage

summarize_reviews
