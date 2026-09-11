# MF2033k6lC_LocatorDisabled_SampledOneTask 实验报告

## 1. 实验目的

验证原始 PDF 经 MinerU 到最终报告的闭环，仅关闭 locator gate，保留 quote gate。

## 2. 基线

- branch: `lya`
- commit: `fddb68436f330c943c4484f2be0787097d972228`
- started_at: `2026-08-31T08:02:30.920024+00:00`
- status: **INVALID / DEGRADED**

## 3. 唯一功能性改动

- `require_direct_quote = true`
- `require_source_location = false`
- `locator_gate_disabled = true`

## 4. 输入

- PDF: `examples/MF2033k6lC.pdf`
- size: 2046268 bytes
- pages: 90

## 5. MinerU

```json
{
  "success": true,
  "source": "mineru",
  "pages": 90,
  "backend": "pipeline",
  "method": "auto",
  "fallback_triggered": false,
  "warnings": [
    "methods: 未检测到",
    "results: 未检测到",
    "discussion: 未检测到"
  ],
  "elapsed_seconds": 60.309827,
  "reused": true
}
```

## 6. Reference Bootstrap

```json
{
  "paper_id": "MG19333vrw-locator-off-full",
  "total": 91,
  "bootstrap_ready": true,
  "resolved": 0,
  "ambiguous": 0,
  "not_found": 91,
  "failed": 0,
  "success": true,
  "elapsed_seconds": 0.406834,
  "stderr": "",
  "reused": true
}
```

## 7. 工作流结果

- rounds: 1
- ResearchTasks: 1
- coverage gaps: ['NP-1: 仅有 0 条有效证据，至少需要 1 条']

## 8. Tool 调用统计

```json
[
  {
    "point": "NP-1",
    "task": "T-1",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 160.0849133620004,
    "researcher_seconds": 211.84647029000007,
    "tool_calls": {
      "reference_search": {
        "attempts": 1,
        "success": 1
      },
      "web_search": {
        "attempts": 5,
        "success": 5
      },
      "browser": {
        "attempts": 3,
        "success": 1
      },
      "reader": {
        "attempts": 1,
        "success": 1
      }
    },
    "tool_counters": {
      "tool_rejection_count": 1,
      "multiple_tool_call_dropped_count": 1,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 2,
      "zero_hit_count": 7
    },
    "tokens": 227719,
    "model_calls": 12,
    "warnings": [
      "native tool harness failed: total tool-call budget exhausted"
    ]
  }
]
```

## 9. Evidence

```json
{
  "built": 0,
  "validator_accepted": 0,
  "validator_rejected": 0,
  "reviewer_accepted": 0,
  "reviewer_rejected": 0,
  "rejected": []
}
```

## 10. 时间统计

```json
{
  "paper_processing_seconds": 0.0,
  "reference_bootstrap_seconds": 0.0,
  "workflow_seconds": 399.032553,
  "PointExtractor_seconds": 1e-06,
  "Coordinator_seconds": 4.1e-05,
  "SearchPlanner_seconds": 160.084913,
  "Researcher_seconds": 211.84647,
  "Validator_seconds": 1.1e-05,
  "Reviewer_seconds": 6e-06,
  "Report synthesis/render_seconds": 27.084709,
  "total_seconds": 399.096593,
  "previous_attempt_seconds": 2057.663571
}
```

## 11. Token 统计

```json
{
  "total": {
    "prompt_tokens": 297767,
    "completion_tokens": 6081,
    "total_tokens": 303848,
    "calls": 13,
    "unreported_calls": 0
  },
  "by_role": {
    "Report synthesis/render": {
      "prompt_tokens": 75471,
      "completion_tokens": 658,
      "total_tokens": 76129,
      "calls": 1
    },
    "Researcher": {
      "prompt_tokens": 221091,
      "completion_tokens": 1584,
      "total_tokens": 222675,
      "calls": 11
    },
    "SearchPlanner": {
      "prompt_tokens": 1205,
      "completion_tokens": 3839,
      "total_tokens": 5044,
      "calls": 1
    }
  }
}
```

MinerU external API tokens: 0  
MinerU internal inference tokens: N/A

## 12. 最终报告

- path: `/home/lya3106643285/projects/Novelty-Multi-Agent-Framework/outputs/MG19333vrw-locator-off-full/report/MG19333vrw-locator-off-full-report.md`
- generated: True

## 13. 与上次实验对比

| 指标 | 上轮 Full Workflow | 本轮 Locator Disabled |
|---|---:|---:|
| PDF parser | text_layer | mineru |
| NoveltyPoints | 2 | 1 |
| ResearchTasks | 4 | 1 |
| EvidenceCards built | 3 | 0 |
| Validator accepted | 0 | 0 |
| Reviewer accepted | 0 | 0 |
| 有效最终报告 | ❌ | False |
| 总耗时 | ≈35 min | 399.096593 s |
| Total tokens | 未完整记录 | 303848 |
| PDF→Report 总耗时 | 未记录 | 399.096593 s |

## 14. 暴露的新问题

见 metrics.json 中的 issues / rejected reasons。

## 15. 结论

程序已闭环，但未同时满足 MinerU、Validator、Reviewer 和有效报告标准。

## 16. 完整规模估算

```json
{
  "method": "fixed cost + sampled per-task cost * estimated full task count",
  "estimated_tasks": 6,
  "sampled_tasks": 1,
  "estimated_total_tokens": 1455459,
  "caveats": [
    "Linear extrapolation; task complexity and retries vary.",
    "Parallel wall-clock can be lower than summed task elapsed.",
    "Supplement rounds are excluded because the sample fixes max_rounds=1."
  ],
  "estimated_workflow_seconds": 2258.673066,
  "estimated_pdf_to_report_seconds": 2515.0859269999996,
  "checkpoint_point_extraction_seconds": 195.6962,
  "checkpoint_point_extraction_tokens": 13016,
  "checkpoint_cost_source": "Observed in the first successful checkpoint run; raw call log was overwritten by a later interrupted attempt.",
  "estimated_pdf_to_report_minutes": 41.91809878333333,
  "rough_token_range": {
    "lower_0.8x_sampled_task_cost": 1182196,
    "upper_1.5x_sampled_task_cost": 2138616
  }
}
```
