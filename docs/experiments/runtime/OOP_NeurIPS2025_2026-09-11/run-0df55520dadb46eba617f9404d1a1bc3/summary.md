# Runtime Summary

## Run

Paper ID: OOP_NeurIPS2025
Run ID: run-0df55520dadb46eba617f9404d1a1bc3
Status: SUCCESS
Start: 2026-09-11T16:54:39.525468+00:00
End: 2026-09-11T17:05:37.839850+00:00
Duration: 658235 ms

## Environment

Git Branch: hyl
Git Commit: 3010a89be2e2965c82e982e1c3f0f85dcbaf6994
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 32110 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3827 ms |
| plan_research_task | SUCCESS | 7125 ms |
| plan_research_task | SUCCESS | 8031 ms |
| plan_research_task | SUCCESS | 8062 ms |
| plan_research_task | SUCCESS | 7422 ms |
| plan_research_task | SUCCESS | 8561 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 455250 ms |
| run_research_task | SUCCESS | 414906 ms |
| run_research_task | SUCCESS | 257218 ms |
| run_research_task | SUCCESS | 458750 ms |
| run_research_task | SUCCESS | 276311 ms |
| run_research_task | SUCCESS | 152484 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 16 ms |
| validate_synthesis_input | SUCCESS | 0 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 14811 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 15 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 24 | 22 | 2 | 6 |
| database_search | 33 | 19 | 14 | 3 |
| reader | 32 | 27 | 5 | 0 |

## LLM Token Usage and Cost

Calls: 106
Input tokens: 1935953
Cached input tokens: 1694720
Output tokens: 26034
Reasoning tokens: 2517
Total tokens: 1961987
Cost: RMB 1.46642100
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 106 | 1935953 | 1694720 | 26034 | 1961987 | 1.46642100 | 0 |

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

- run_research_task / tool_0013: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0030: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0031: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0032: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0035: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0043: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0045: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0046: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0047: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0048: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0055: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0058: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0059: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0060: HarnessPolicyError: reader cumulative character budget exhausted
- run_research_task / tool_0071: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0073: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0080: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0083: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0084: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0087: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0089: HarnessPolicyError: total tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
