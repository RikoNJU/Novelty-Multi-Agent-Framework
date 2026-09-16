# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-fb1de326c099455984af33097a9c386a
Entrypoint: paper_input
Input Identity: {"paper_json": "docs/experiments/20260916_194850/input/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T11:52:44.538359+00:00
End: 2026-09-16T12:10:49.803153+00:00
Duration: 1085316 ms

## Environment

Git Branch: lya
Git Commit: ce3c20d809ea484aaea7f4e4f71adebf07238330
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 211390 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 5441 ms |
| plan_research_task | SUCCESS | 21196 ms |
| plan_research_task | SUCCESS | 2322 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 387651 ms |
| run_research_task | SUCCESS | 391970 ms |
| run_research_task | SUCCESS | 325799 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 365191 ms |
| validate_synthesis_input | SUCCESS | 19 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 87266 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 4 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 16 | 14 | 2 | 1 |
| database_search | 9 | 6 | 3 | 0 |
| reader | 38 | 37 | 1 | 0 |
| web_search | 1 | 1 | 0 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 38 | 1 | NEVER_PERSISTED | `diagnostics/reader.json` |
| reference_namespace | ERROR | 38 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=27, NEVER_PERSISTED=1

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 94
Input tokens: 1238168
Cached input tokens: 148992
Output tokens: 52218
Reasoning tokens: 15095
Total tokens: 1290386
Cost: RMB 3.78218760
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 94 | 1238168 | 148992 | 52218 | 1290386 | 3.78218760 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: PASS
Input final valid Cards: 7
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 2 | 1 | PASS |
| NP-2 | 4 | 1 | PASS |
| NP-3 | 1 | 1 | PASS |


## Reviewer Information Adjudication

### Stage stage_0012

Stage status: SUCCESS
Cards preserved: True
Supplement requests control route: False
Missing reviews: []
Unexpected reviews: []
Duplicate reviews: []
Unresolved Evidence IDs: []
Actual next stage: validate_synthesis_input

| Novelty Point | Status | Verdict | Relevant Works | Supplement |
|---|---|---|---:|---|
| NP-1 | reviewed | partially_novel | 2 | True |
| NP-2 | reviewed | partially_novel | 3 | True |
| NP-3 | reviewed | partially_novel | 1 | True |


## Errors

- run_research_task / tool_0007: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0013: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0015: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0016: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0024: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0045: ValueError: unknown artifact_id 'art_5b6b3d5723031d0cc49df623' in the research or subject reference manifest

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
