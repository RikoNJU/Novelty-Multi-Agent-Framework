# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-406adb9875de4754877ad098b6674c82
Status: SUCCESS
Start: 2026-09-11T17:28:40.046905+00:00
End: 2026-09-11T17:43:33.154570+00:00
Duration: 893046 ms

## Environment

Git Branch: hyl
Git Commit: 40f1c05e5e63d56871706fcf6e1c35669ce6984e
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 51610 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 7546 ms |
| plan_research_task | SUCCESS | 3593 ms |
| plan_research_task | SUCCESS | 7609 ms |
| plan_research_task | SUCCESS | 6078 ms |
| plan_research_task | SUCCESS | 3531 ms |
| plan_research_task | SUCCESS | 5812 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 487485 ms |
| run_research_task | SUCCESS | 433093 ms |
| run_research_task | SUCCESS | 487468 ms |
| run_research_task | SUCCESS | 433484 ms |
| run_research_task | SUCCESS | 177453 ms |
| run_research_task | SUCCESS | 175656 ms |
| validate_evidence | SUCCESS | 16 ms |
| review_evidence | SUCCESS | 186733 ms |
| validate_synthesis_input | SUCCESS | 14 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 9141 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 31 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 21 | 20 | 1 | 6 |
| database_search | 18 | 15 | 3 | 5 |
| reader | 47 | 32 | 15 | 0 |
| browser | 1 | 0 | 1 | 0 |

## LLM Token Usage and Cost

Calls: 106
Input tokens: 1174881
Cached input tokens: 918528
Output tokens: 39613
Reasoning tokens: 7919
Total tokens: 1214494
Cost: RMB 1.40113440
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 106 | 1174881 | 918528 | 39613 | 1214494 | 1.40113440 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 1
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 1 | 1 | PASS |
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
| NP-2 | reviewed | novel | 1 | True |
| NP-3 | insufficient_evidence | - | 0 | True |


## Errors

- run_research_task / tool_0016: ValueError: artifact art_06a333ffbcc8e250f6785baa sha256 mismatch
- run_research_task / tool_0019: ValueError: artifact art_5a95e23353233acf80dfb52a sha256 mismatch
- run_research_task / tool_0023: ValueError: artifact art_375e70992c2d9a1dbba2ff17 sha256 mismatch
- run_research_task / tool_0029: ValueError: artifact art_6cc149e03eff16cca0999368 sha256 mismatch
- run_research_task / tool_0031: ValueError: artifact art_c99db0fec9626da863cc2c54 sha256 mismatch
- run_research_task / tool_0035: ValueError: artifact art_0e0b76110b06e28d52d3110d sha256 mismatch
- run_research_task / tool_0039: ValueError: artifact art_1a3adb67f158610c2c6c0cca sha256 mismatch
- run_research_task / tool_0044: ValueError: artifact art_03a5fc2bdb0a7ce02e231c0d sha256 mismatch
- run_research_task / tool_0047: BrowserDependencyError: Chromium runtime libraries are unavailable in both the system loader and the current Python environment; install them with 'playwright install-deps chromium' during deployment
- run_research_task / tool_0051: ValueError: artifact art_06a333ffbcc8e250f6785baa sha256 mismatch
- run_research_task / tool_0052: ValueError: unknown artifact_id 'art_1d5b5c31caf645335b110cd' in the research or subject reference manifest
- run_research_task / tool_0053: ValueError: artifact art_2126b98ada23a422d928d9e0 sha256 mismatch
- run_research_task / tool_0055: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0056: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0071: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0072: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0079: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0083: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0084: HarnessPolicyError: reader cumulative character budget exhausted
- review_evidence / tool_0085: ValueError: unknown artifact_id 'art_b8b821043e4485fda0b8527c' in the research manifest

## Integrity Gates

- validate_synthesis_input: FAILED
- validate_report_integrity: PASS
  - card_fa58976d87c718a7d5817694: missing Work: wrk_b6b76b1dae1837f54a226290
  - card_fa58976d87c718a7d5817694: missing Artifact: art_b8b821043e4485fda0b8527c
  - card_d3ae4ea3ad208a4f19e5be7c: missing Work: wrk_712252459ef2697739d75d40
  - card_d3ae4ea3ad208a4f19e5be7c: missing Artifact: art_ea01d9c5f48ad68092a07bf7

## Last Completed Stage

render_report
