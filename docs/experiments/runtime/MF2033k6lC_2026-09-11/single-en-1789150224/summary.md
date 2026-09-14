# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: single-en-1789150224
Status: SUCCESS
Start: 2026-09-11T18:10:24.647744+00:00
End: 2026-09-11T18:11:10.519658+00:00
Duration: 45921 ms

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
| reference_search | 2 | 2 | 0 | 0 |
| database_search | 4 | 2 | 2 | 0 |
| reader | 4 | 4 | 0 | 0 |

## LLM Token Usage and Cost

Calls: 11
Input tokens: 132064
Cached input tokens: 112640
Output tokens: 2848
Reasoning tokens: 0
Total tokens: 134912
Cost: RMB 0.05884800
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 11 | 132064 | 112640 | 2848 | 134912 | 0.05884800 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- - / tool_0008: HarnessPolicyError: reader required after database_search returned artifact_ids
- - / tool_0009: HarnessPolicyError: reader required after database_search returned artifact_ids

## Integrity Gates

- None

## Last Completed Stage

None
