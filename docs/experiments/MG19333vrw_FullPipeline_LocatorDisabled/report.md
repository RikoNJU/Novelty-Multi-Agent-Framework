# MG19333vrw Full Pipeline / Locator Disabled 实验报告

## 1. 实验目的

验证原始 PDF 经 MinerU 到最终报告的闭环，仅关闭 locator gate，保留 quote gate。

## 2. 基线

- branch: `lya`
- commit: `fddb68436f330c943c4484f2be0787097d972228`
- started_at: `2026-08-31T07:26:12.848054+00:00`
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

- rounds: None
- ResearchTasks: 0
- coverage gaps: None

## 8. Tool 调用统计

```json
[]
```

## 9. Evidence

```json
{}
```

## 10. 时间统计

```json
{
  "total_seconds": 2057.663571
}
```

## 11. Token 统计

```json
{
  "total": {
    "prompt_tokens": 485698,
    "completion_tokens": 32377,
    "total_tokens": 518075,
    "calls": 57,
    "unreported_calls": 7
  },
  "by_role": {
    "PointExtractor": {
      "calls": 1
    },
    "Researcher": {
      "calls": 44,
      "prompt_tokens": 400952,
      "completion_tokens": 4853,
      "total_tokens": 405805
    },
    "SearchPlanner": {
      "prompt_tokens": 8549,
      "completion_tokens": 26637,
      "total_tokens": 35186,
      "calls": 11
    },
    "Supplement": {
      "prompt_tokens": 76197,
      "completion_tokens": 887,
      "total_tokens": 77084,
      "calls": 1
    }
  }
}
```

MinerU external API tokens: 0  
MinerU internal inference tokens: N/A

## 12. 最终报告

- path: `None`
- generated: None

## 13. 与上次实验对比

| 指标 | 上轮 Full Workflow | 本轮 Locator Disabled |
|---|---:|---:|
| PDF parser | text_layer | mineru |
| NoveltyPoints | 2 | None |
| ResearchTasks | 4 | 0 |
| EvidenceCards built | 3 | None |
| Validator accepted | 0 | None |
| Reviewer accepted | 0 | None |
| 有效最终报告 | ❌ | None |
| 总耗时 | ≈35 min | 2057.663571 s |
| Total tokens | 未完整记录 | 518075 |
| PDF→Report 总耗时 | 未记录 | 2057.663571 s |

## 14. 暴露的新问题

KeyboardInterrupt: 

## 15. 结论

实验未完成。
