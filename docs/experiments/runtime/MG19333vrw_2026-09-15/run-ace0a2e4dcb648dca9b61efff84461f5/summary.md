# Runtime Summary

## Run

Paper ID: MG19333vrw
Run ID: run-ace0a2e4dcb648dca9b61efff84461f5
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MG19333vrw/paper-input/others/paper.json", "paper_sha256": "a2ca91bc21b1d356160dcbf4a1e49267a925b9c5527b085528c5653d7fc4367e", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-15T17:49:23.892425+00:00
End: 2026-09-15T17:57:27.158706+00:00
Duration: 483765 ms

## Environment

Git Branch: hyl
Git Commit: 44d7a1b045333d448bea63b77876fd11ae91ead2
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 25375 ms |
| resolve_subject_references | SUCCESS | 64719 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 2625 ms |
| plan_research_task | SUCCESS | 2688 ms |
| plan_research_task | SUCCESS | 2469 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 266000 ms |
| run_research_task | SUCCESS | 187796 ms |
| run_research_task | SUCCESS | 286671 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 65671 ms |
| validate_synthesis_input | SUCCESS | 15 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 32594 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 30 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 9 | 7 | 2 | 1 |
| database_search | 5 | 4 | 1 | 0 |
| reader | 32 | 26 | 6 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 32 | 6 | WRONG_NAMESPACE | `diagnostics/reader.json` |
| reference_namespace | ERROR | 32 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: NEVER_PERSISTED=1, OTHER=3, WRONG_NAMESPACE=2

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 58
Input tokens: 557466
Cached input tokens: 423424
Output tokens: 23288
Reasoning tokens: 6450
Total tokens: 580754
Cost: RMB 0.73874520
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 58 | 557466 | 423424 | 23288 | 580754 | 0.73874520 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 2
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 1 | 1 | PASS |
| NP-2 | 1 | 1 | PASS |
| NP-3 | 0 | 1 | INSUFFICIENT |


## Reviewer Information Adjudication

### Stage stage_0013

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
| NP-1 | insufficient_evidence | - | 1 | True |
| NP-2 | insufficient_evidence | - | 0 | True |
| NP-3 | insufficient_evidence | - | 0 | True |


## Retrieval Coverage

### Stage stage_0013

Stage status: SUCCESS
Actual next stage: validate_synthesis_input

| Novelty Point | Coverage | Required Sources | Failed | Not Attempted | Zero Hit |
|---|---|---|---|---|---|
| NP-1 | partial | arxiv, springer | - | springer | - |
| NP-2 | partial | arxiv, springer | - | springer | arxiv |
| NP-3 | partial | arxiv, springer | - | - | springer |


## Errors

- run_research_task / tool_0009: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0010: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0011: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0012: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0021: ValueError: unknown artifact_id 'art_ff0d7a2a0bbbd54e5062bb' in the research or subject reference manifest
- run_research_task / tool_0041: HarnessPolicyError: reader tool-call budget exhausted
- review_evidence / tool_0044: PermissionError: artifact 'x' is outside reviewer scope
- review_evidence / tool_0045: ValueError: unknown artifact_id 'art_a2682f8373e4e077b6056a06' in the research manifest
- review_evidence / tool_0046: ValueError: unknown artifact_id 'art_a2682f8373e4e077b6056a06' in the research manifest

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
