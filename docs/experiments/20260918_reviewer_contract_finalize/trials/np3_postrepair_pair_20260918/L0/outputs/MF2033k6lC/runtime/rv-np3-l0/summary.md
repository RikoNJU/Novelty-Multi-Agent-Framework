# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: rv-np3-l0
Entrypoint: -
Input Identity: {}
Status: SUCCESS
Start: 2026-09-17T17:19:34.249649+00:00
End: 2026-09-17T17:22:12.382100+00:00
Duration: 158146 ms

## Environment

Git Branch: lya
Git Commit: 60ae645feb0421f61af9eb574158cf6e68d1c1e9
Model: siliconflow / deepseek-ai/DeepSeek-V4-Flash
Python: 3.12.3

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| review_card | SUCCESS | 70877 ms |
| review_card | SUCCESS | 30703 ms |
| summarize_reviews | SUCCESS | 8318 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reader | 4 | 4 | 0 | 4 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | OK | 4 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | ERROR | 4 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | INCOMPLETE | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 7
Input tokens: 35162
Cached input tokens: 256
Output tokens: 7898
Reasoning tokens: 0
Total tokens: 43060
Cost: RMB 0.17587680
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 7 | 35162 | 256 | 7898 | 43060 | 0.17587680 | 0 |

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
