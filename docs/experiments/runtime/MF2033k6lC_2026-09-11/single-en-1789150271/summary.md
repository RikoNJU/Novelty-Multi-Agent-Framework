# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: single-en-1789150271
Status: SUCCESS
Start: 2026-09-11T18:11:11.698595+00:00
End: 2026-09-11T18:12:22.161248+00:00
Duration: 70515 ms

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
| reader | 8 | 6 | 2 | 0 |
| database_search | 5 | 4 | 1 | 0 |

## LLM Token Usage and Cost

Calls: 16
Input tokens: 270368
Cached input tokens: 239616
Output tokens: 6846
Reasoning tokens: 0
Total tokens: 277214
Cost: RMB 0.11287740
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 16 | 270368 | 239616 | 6846 | 277214 | 0.11287740 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- - / tool_0007: HarnessPolicyError: reader required after database_search returned artifact_ids
- - / tool_0010: HarnessPolicyError: reader required after database_search returned artifact_ids
- - / tool_0014: HarnessPolicyError: reader required after database_search returned artifact_ids

## Integrity Gates

- None

## Last Completed Stage

None
