# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: single-en-1789150154
Status: SUCCESS
Start: 2026-09-11T18:09:14.238825+00:00
End: 2026-09-11T18:10:13.536570+00:00
Duration: 59343 ms

## Environment

Git Branch: hyl
Git Commit: 8a7e17bbf6442541e6b8a32dd4839fce562aeba6
Model: None / None
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| run_research_task | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 5 | 4 | 1 | 0 |
| database_search | 4 | 4 | 0 | 0 |
| reader | 8 | 7 | 1 | 0 |

## LLM Token Usage and Cost

Calls: 17
Input tokens: 324486
Cached input tokens: 290048
Output tokens: 3323
Reasoning tokens: 0
Total tokens: 327809
Cost: RMB 0.11011770
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 17 | 324486 | 290048 | 3323 | 327809 | 0.11011770 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- - / tool_0012: HarnessPolicyError: reader required after database_search returned artifact_ids
- - / tool_0017: HarnessPolicyError: reader cumulative character budget exhausted

## Integrity Gates

- None

## Last Completed Stage

None
