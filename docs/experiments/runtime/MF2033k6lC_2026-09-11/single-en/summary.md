# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: single-en
Status: SUCCESS
Start: 2026-09-11T18:07:50.256577+00:00
End: 2026-09-11T18:09:00.620662+00:00
Duration: 70406 ms

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
| reader | 8 | 6 | 2 | 0 |
| database_search | 3 | 3 | 0 | 0 |

## LLM Token Usage and Cost

Calls: 17
Input tokens: 307401
Cached input tokens: 273664
Output tokens: 5506
Reasoning tokens: 0
Total tokens: 312907
Cost: RMB 0.11643210
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 17 | 307401 | 273664 | 5506 | 312907 | 0.11643210 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- - / tool_0007: HarnessPolicyError: reader required after database_search returned artifact_ids
- - / tool_0013: ValueError: char_start 8000 exceeds artifact art_a4b03ccff6df4518c3399802 length
- - / tool_0014: HarnessPolicyError: reader required after database_search returned artifact_ids

## Integrity Gates

- None

## Last Completed Stage

None
