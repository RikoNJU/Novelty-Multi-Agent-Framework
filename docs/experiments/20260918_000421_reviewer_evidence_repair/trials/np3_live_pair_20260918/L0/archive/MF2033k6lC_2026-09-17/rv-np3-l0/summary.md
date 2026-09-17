# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: rv-np3-l0
Entrypoint: -
Input Identity: {}
Status: SUCCESS
Start: 2026-09-17T16:25:39.424145+00:00
End: 2026-09-17T16:26:31.602052+00:00
Duration: 52190 ms

## Environment

Git Branch: lya
Git Commit: 80aafbd07fa91d51f22f5c34a0302096b85cd58a
Model: siliconflow / deepseek-ai/DeepSeek-V4-Flash
Python: 3.12.3

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| review_card | SUCCESS | 24552 ms |
| review_card | SUCCESS | 23606 ms |
| summarize_reviews | SUCCESS | 3982 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reader | 4 | 4 | 0 | 1 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 4 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 4 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | INCOMPLETE | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=3

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 8
Input tokens: 40387
Cached input tokens: 20480
Output tokens: 7015
Reasoning tokens: 0
Total tokens: 47402
Cost: RMB 0.12900000
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 8 | 40387 | 20480 | 7015 | 47402 | 0.12900000 | 0 |

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
