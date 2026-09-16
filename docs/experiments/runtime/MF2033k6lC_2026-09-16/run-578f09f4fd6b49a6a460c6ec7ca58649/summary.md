# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-578f09f4fd6b49a6a460c6ec7ca58649
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "430dc1a41d55724e42a21b10e28d25146e931ed1c06e68a712de60006f4f3768", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T01:11:32.892761+00:00
End: 2026-09-16T01:18:37.249216+00:00
Duration: 424625 ms

## Environment

Git Branch: hyl
Git Commit: 44d7a1b045333d448bea63b77876fd11ae91ead2
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 13438 ms |
| resolve_subject_references | SUCCESS | 192453 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 1719 ms |
| plan_research_task | SUCCESS | 21609 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 43390 ms |
| run_research_task | SUCCESS | 93625 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 67391 ms |
| validate_synthesis_input | SUCCESS | 30 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 33703 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 15 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 5 | 3 | 2 | 0 |
| database_search | 5 | 2 | 3 | 0 |
| reader | 14 | 9 | 5 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 14 | 5 | WRONG_NAMESPACE | `diagnostics/reader.json` |
| reference_namespace | ERROR | 14 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: OTHER=1, WRONG_NAMESPACE=4

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 33
Input tokens: 305101
Cached input tokens: 250112
Output tokens: 14711
Reasoning tokens: 4228
Total tokens: 319812
Cost: RMB 0.37239960
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 33 | 305101 | 250112 | 14711 | 319812 | 0.37239960 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 3
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 3 | 1 | PASS |


## Reviewer Information Adjudication

### Stage stage_0011

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
| NP-2 | reviewed | novel | 3 | True |


## Retrieval Coverage

### Stage stage_0011

Stage status: SUCCESS
Actual next stage: validate_synthesis_input

| Novelty Point | Coverage | Required Sources | Failed | Not Attempted | Zero Hit |
|---|---|---|---|---|---|
| NP-1 | partial | arxiv, springer | - | springer | - |
| NP-2 | partial | arxiv, springer | - | springer | - |


## Errors

- run_research_task / tool_0005: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0006: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0008: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0010: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0011: HarnessPolicyError: reader required after database_search returned artifact_ids
- review_evidence / tool_0020: ValueError: unknown artifact_id 'art_d66e0ee9dd302e32ea2daf52' in the research manifest
- review_evidence / tool_0021: ValueError: unknown artifact_id 'art_962e6cebe936ceaba611b473' in the research manifest
- review_evidence / tool_0022: ValueError: unknown artifact_id 'art_f3ade99e35dbf7c9385b5639' in the research manifest
- review_evidence / tool_0023: PermissionError: artifact 'unused' is outside reviewer scope
- review_evidence / tool_0024: ValueError: unknown artifact_id 'art_962e6cebe936ceaba611b473' in the research manifest

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
