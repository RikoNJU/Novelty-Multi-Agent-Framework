# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-20260916T041107564936Z-cfd54ec903
Entrypoint: parallel
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T04:11:07.564982+00:00
End: 2026-09-16T04:15:14.323548+00:00
Duration: 246791 ms

## Environment

Git Branch: fix/arxiv-rate-limit-final
Git Commit: 674c7ff7657a3dda7a4dddd9d39d5b88344a2f05
Model: None / None
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| run_research_task | SUCCESS | 198810 ms |
| run_research_task | SUCCESS | 246720 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 8 | 8 | 0 | 0 |
| database_search | 4 | 4 | 0 | 3 |
| reader | 16 | 15 | 1 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 16 | 1 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 16 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | INCOMPLETE | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=5, OTHER=1

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 30
Input tokens: 423087
Cached input tokens: 6912
Output tokens: 11036
Reasoning tokens: 0
Total tokens: 434123
Cost: RMB 1.34992260
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 30 | 423087 | 6912 | 11036 | 434123 | 1.34992260 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- run_research_task / tool_0007: HarnessPolicyError: reader required after database_search returned artifact_ids

## Integrity Gates

- None

## Last Completed Stage

run_research_task
