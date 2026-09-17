# Runtime Summary

## Run

Paper ID: MG19333vrw-debug-full-20260907
Run ID: rv-stable-holdout-1
Entrypoint: -
Input Identity: {}
Status: SUCCESS
Start: 2026-09-17T19:10:02.949206+00:00
End: 2026-09-17T19:10:24.334388+00:00
Duration: 21392 ms

## Environment

Git Branch: lya
Git Commit: 8fa658573310e329fc0e89defaeafc527eea3325
Model: siliconflow / deepseek-ai/DeepSeek-V4-Flash
Python: 3.12.3

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| review_card | SUCCESS | 15717 ms |
| summarize_reviews | SUCCESS | 5640 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reader | 3 | 3 | 0 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 3 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 3 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | INCOMPLETE | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=2

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 5
Input tokens: 32409
Cached input tokens: 256
Output tokens: 3124
Reasoning tokens: 0
Total tokens: 35533
Cost: RMB 0.06232590
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 5 | 32409 | 256 | 3124 | 35533 | 0.06232590 | 0 |

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
