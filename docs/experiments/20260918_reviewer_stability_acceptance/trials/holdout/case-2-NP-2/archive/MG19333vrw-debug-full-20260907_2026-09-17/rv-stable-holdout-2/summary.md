# Runtime Summary

## Run

Paper ID: MG19333vrw-debug-full-20260907
Run ID: rv-stable-holdout-2
Entrypoint: -
Input Identity: {}
Status: SUCCESS
Start: 2026-09-17T19:10:24.368722+00:00
End: 2026-09-17T19:10:47.201924+00:00
Duration: 22840 ms

## Environment

Git Branch: lya
Git Commit: 8fa658573310e329fc0e89defaeafc527eea3325
Model: siliconflow / deepseek-ai/DeepSeek-V4-Flash
Python: 3.12.3

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| review_card | SUCCESS | 17331 ms |
| summarize_reviews | SUCCESS | 5477 ms |

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

reader classifications: INCOMPLETE_RECORD=1

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 5
Input tokens: 24530
Cached input tokens: 1280
Output tokens: 3129
Reasoning tokens: 0
Total tokens: 27659
Cost: RMB 0.04914750
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 5 | 24530 | 1280 | 3129 | 27659 | 0.04914750 | 0 |

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
