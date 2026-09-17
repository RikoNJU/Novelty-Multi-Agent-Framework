# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: rv-stable-1
Entrypoint: -
Input Identity: {}
Status: SUCCESS
Start: 2026-09-17T19:07:35.264127+00:00
End: 2026-09-17T19:07:43.465200+00:00
Duration: 8208 ms

## Environment

Git Branch: lya
Git Commit: 8fa658573310e329fc0e89defaeafc527eea3325
Model: siliconflow / deepseek-ai/DeepSeek-V4-Flash
Python: 3.12.3

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| summarize_reviews | SUCCESS | 8179 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | INCOMPLETE | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | INCOMPLETE | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 1
Input tokens: 9805
Cached input tokens: 0
Output tokens: 1638
Reasoning tokens: 0
Total tokens: 11443
Cost: RMB 0.02207850
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 1 | 9805 | 0 | 1638 | 11443 | 0.02207850 | 0 |

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
