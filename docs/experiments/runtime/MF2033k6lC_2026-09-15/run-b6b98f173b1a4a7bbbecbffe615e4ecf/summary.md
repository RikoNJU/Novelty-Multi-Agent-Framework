# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-b6b98f173b1a4a7bbbecbffe615e4ecf
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "430dc1a41d55724e42a21b10e28d25146e931ed1c06e68a712de60006f4f3768", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-15T23:26:32.105184+00:00
End: 2026-09-15T23:32:06.365743+00:00
Duration: 334796 ms

## Environment

Git Branch: hyl
Git Commit: 44d7a1b045333d448bea63b77876fd11ae91ead2
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 89062 ms |
| resolve_subject_references | SUCCESS | 72702 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3015 ms |
| plan_research_task | SUCCESS | 5594 ms |
| plan_research_task | SUCCESS | 2139 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 95719 ms |
| run_research_task | SUCCESS | 125687 ms |
| run_research_task | SUCCESS | 141984 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 0 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 19219 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 30 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 15 | 11 | 4 | 2 |
| database_search | 6 | 5 | 1 | 0 |
| reader | 25 | 24 | 1 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 25 | 1 | OTHER | `diagnostics/reader.json` |
| reference_namespace | ERROR | 25 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: OTHER=1

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 55
Input tokens: 673986
Cached input tokens: 572928
Output tokens: 18565
Reasoning tokens: 8664
Total tokens: 692551
Cost: RMB 0.32106870
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 55 | 673986 | 572928 | 18565 | 692551 | 0.32106870 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 0
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 0 | 1 | INSUFFICIENT |
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
| NP-1 | insufficient_evidence | - | 0 | True |
| NP-2 | insufficient_evidence | - | 0 | True |
| NP-3 | insufficient_evidence | - | 0 | True |


## Retrieval Coverage

### Stage stage_0013

Stage status: SUCCESS
Actual next stage: validate_synthesis_input

| Novelty Point | Coverage | Required Sources | Failed | Not Attempted | Zero Hit |
|---|---|---|---|---|---|
| NP-1 | partial | arxiv, springer | - | springer | - |
| NP-2 | complete | arxiv, springer | - | - | arxiv, springer |
| NP-3 | complete | arxiv, springer | - | - | arxiv, springer |


## Errors

- run_research_task / tool_0019: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0026: HarnessPolicyError: reader tool-call budget exhausted
- run_research_task / tool_0027: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0030: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0041: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0046: HarnessPolicyError: total tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
