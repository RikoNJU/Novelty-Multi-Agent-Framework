# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: rv-np3-l1
Entrypoint: -
Input Identity: {}
Status: SUCCESS
Start: 2026-09-17T16:26:31.664796+00:00
End: 2026-09-17T16:27:05.438857+00:00
Duration: 33786 ms

## Environment

Git Branch: lya
Git Commit: 80aafbd07fa91d51f22f5c34a0302096b85cd58a
Model: siliconflow / deepseek-ai/DeepSeek-V4-Flash
Python: 3.12.3

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| review_card | SUCCESS | 3107 ms |
| review_card | SUCCESS | 27453 ms |
| summarize_reviews | SUCCESS | 3182 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reader | 7 | 5 | 2 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 7 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 7 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | INCOMPLETE | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=7

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 8
Input tokens: 53020
Cached input tokens: 33024
Output tokens: 3962
Reasoning tokens: 0
Total tokens: 56982
Cost: RMB 0.10555320
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 8 | 53020 | 33024 | 3962 | 56982 | 0.10555320 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- review_card / tool_0002: HarnessPolicyError: reader cumulative character budget exhausted
- review_card / tool_0007: HarnessPolicyError: total tool-call budget exhausted

## Integrity Gates

- None

## Last Completed Stage

summarize_reviews
