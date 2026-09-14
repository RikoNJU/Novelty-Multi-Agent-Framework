# Runtime Summary

## Run

Paper ID: OOP_NeurIPS2025
Run ID: run-41a3586ab5b845c39bb14b4473a5edc9
Status: SUCCESS
Start: 2026-09-11T16:29:27.505042+00:00
End: 2026-09-11T16:39:44.520781+00:00
Duration: 617062 ms

## Environment

Git Branch: hyl
Git Commit: e2a70467ff50280ed5fcf09c4aef34b1ea2f1cff
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 27780 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3030 ms |
| plan_research_task | SUCCESS | 3109 ms |
| plan_research_task | SUCCESS | 8203 ms |
| plan_research_task | SUCCESS | 6186 ms |
| plan_research_task | SUCCESS | 6640 ms |
| plan_research_task | SUCCESS | 3187 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 463078 ms |
| run_research_task | SUCCESS | 423860 ms |
| run_research_task | SUCCESS | 423344 ms |
| run_research_task | SUCCESS | 423485 ms |
| run_research_task | SUCCESS | 127313 ms |
| run_research_task | SUCCESS | 122343 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 16 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 7500 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 14 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 17 | 14 | 3 | 1 |
| database_search | 16 | 12 | 4 | 2 |
| reader | 25 | 24 | 1 | 0 |

## LLM Token Usage and Cost

Calls: 73
Input tokens: 1068302
Cached input tokens: 860416
Output tokens: 20854
Reasoning tokens: 1410
Total tokens: 1089156
Cost: RMB 1.06946880
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 73 | 1068302 | 860416 | 20854 | 1089156 | 1.06946880 | 0 |

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

### Stage stage_0018

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


## Errors

- run_research_task / tool_0021: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0031: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0035: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0036: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0049: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0055: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0057: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0058: HarnessPolicyError: total tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
