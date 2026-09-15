# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-c44139b2ff1e462a9b84dea99a7e3a79
Entrypoint: paper_input
Input Identity: {"paper_json": "docs/experiments/.full_run_no_mineru/input/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-15T13:02:12.663032+00:00
End: 2026-09-15T13:24:48.059556+00:00
Duration: 1358630 ms

## Environment

Git Branch: lya
Git Commit: f0b0238599841d767177a7b377a7cf0797af15d8
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 247727 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 7121 ms |
| plan_research_task | SUCCESS | 2505 ms |
| plan_research_task | SUCCESS | 3095 ms |
| plan_research_task | SUCCESS | 6695 ms |
| plan_research_task | SUCCESS | 22195 ms |
| plan_research_task | SUCCESS | 5565 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 161351 ms |
| run_research_task | SUCCESS | 184539 ms |
| run_research_task | SUCCESS | 72142 ms |
| run_research_task | SUCCESS | 199211 ms |
| run_research_task | SUCCESS | 79545 ms |
| run_research_task | SUCCESS | 101826 ms |
| validate_evidence | SUCCESS | 3 ms |
| review_evidence | SUCCESS | 326868 ms |
| validate_synthesis_input | SUCCESS | 7 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| plan_supplement | SUCCESS | 11801 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 35163 ms |
| plan_research_task | SUCCESS | 2208 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 52310 ms |
| run_research_task | SUCCESS | 48396 ms |
| validate_evidence | SUCCESS | 3 ms |
| review_evidence | SUCCESS | 352400 ms |
| validate_synthesis_input | SUCCESS | 12 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 28699 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 5 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 18 | 18 | 0 | 7 |
| database_search | 21 | 3 | 18 | 0 |
| web_search | 14 | 11 | 3 | 0 |
| reader | 42 | 26 | 16 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 42 | 14 | WRONG_NAMESPACE | `diagnostics/reader.json` |
| reference_namespace | ERROR | 42 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=2, WRONG_NAMESPACE=14

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 124
Input tokens: 1103129
Cached input tokens: 103424
Output tokens: 67728
Reasoning tokens: 19293
Total tokens: 1170857
Cost: RMB 3.63969420
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 124 | 1103129 | 103424 | 67728 | 1170857 | 3.63969420 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 5
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: True
Actual next stage: plan_supplement

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 2 | 1 | PASS |
| NP-2 | 3 | 1 | PASS |
| NP-3 | 0 | 1 | INSUFFICIENT |

### Round 2

Configured cut: 1
Stage status: SUCCESS
Check status: PASS
Input final valid Cards: 6
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 2 | 1 | PASS |
| NP-2 | 3 | 1 | PASS |
| NP-3 | 1 | 1 | PASS |


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
| NP-1 | reviewed | partially_novel | 2 | True |
| NP-2 | reviewed | novel | 3 | True |
| NP-3 | insufficient_evidence | - | 0 | True |

### Stage stage_0029

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
| NP-3 | reviewed | partially_novel | 1 | True |


## Errors

- run_research_task / tool_0005: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0010: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0006: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0007: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0009: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0013: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0015: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0019: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0022: BaiduSearchError: query exceeds Baidu's 72-unit limit (93)
- run_research_task / tool_0023: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0026: BaiduSearchError: query exceeds Baidu's 72-unit limit (86)
- run_research_task / tool_0040: BaiduSearchError: query exceeds Baidu's 72-unit limit (112)
- run_research_task / tool_0043: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0049: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0051: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0056: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0059: ToolExecutionError: all 1 search executions failed
- review_evidence / tool_0061: ValueError: unknown artifact_id 'art_b8b821043e4485fda0b8527c' in the research manifest
- review_evidence / tool_0062: ValueError: unknown artifact_id 'art_ea01d9c5f48ad68092a07bf7' in the research manifest
- review_evidence / tool_0063: ValueError: unknown artifact_id 'art_b8b821043e4485fda0b8527c' in the research manifest
- review_evidence / tool_0064: ValueError: unknown artifact_id 'art_ea01d9c5f48ad68092a07bf7' in the research manifest
- review_evidence / tool_0065: ValueError: unknown artifact_id 'art_6f98816ebc9005d24844fdfd' in the research manifest
- review_evidence / tool_0066: ValueError: unknown artifact_id 'art_d88778158223021b818fdd97' in the research manifest
- review_evidence / tool_0067: ValidationError: 1 validation error for ConfiguredReaderArguments8000_16000
artifact_id
  String should have at least 1 character [type=string_too_short, input_value='', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/string_too_short
- review_evidence / tool_0068: ValueError: unknown artifact_id 'art_4144023700aceff174c81183' in the research manifest
- run_research_task / tool_0070: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0072: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0073: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0075: ToolExecutionError: all 1 search executions failed
- review_evidence / tool_0084: ValueError: unknown artifact_id 'art_b8b821043e4485fda0b8527c' in the research manifest
- review_evidence / tool_0085: ValueError: unknown artifact_id 'art_ea01d9c5f48ad68092a07bf7' in the research manifest
- review_evidence / tool_0086: ValueError: unknown artifact_id 'art_b8b821043e4485fda0b8527c' in the research manifest
- review_evidence / tool_0087: ValueError: unknown artifact_id 'art_6f98816ebc9005d24844fdfd' in the research manifest
- review_evidence / tool_0088: ValueError: unknown artifact_id 'art_d88778158223021b818fdd97' in the research manifest
- review_evidence / tool_0089: ValueError: unknown artifact_id 'art_4144023700aceff174c81183' in the research manifest
- review_evidence / tool_0090: ValueError: unknown artifact_id 'art_6f98816ebc9005d24844fdfd' in the research manifest
- review_evidence / tool_0093: ValidationError: 1 validation error for ConfiguredReaderArguments8000_16000
artifact_id
  String should have at least 1 character [type=string_too_short, input_value='', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/string_too_short

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
