# MF2033k6lC_FullPipelineLive 实验报告

## 1. 实验目的

验证 SearchPlanner 默认模型收敛为 `deepseek-flash` 后，不设置任何
`NOVELTY_*_MODEL` 角色覆盖即可完成 MG19333vrw 工作流并生成报告。

## 2. 基线

- branch: `hyl`
- commit: `40f1c05e5e63d56871706fcf6e1c35669ce6984e`
- started_at: `2026-09-11T17:18:06.721267+00:00`
- execution_status: **COMPLETED**
- status: **SUCCESS**

## 3. 固定实验条件

- `paper = MG19333vrw`
- Prompt 与工具预算保持当前仓库配置
- `max_rounds = 1`
- `require_direct_quote = true`
- `require_source_location = false`
- `locator_gate_disabled = true`

## 4. 输入

- PDF: `examples\MF2033k6lC.pdf`
- size: 2046268 bytes
- pages: 90

## 5. 实际生效配置

- `NOVELTY_*_MODEL` 覆盖：无
- 无覆盖完整运行验收：**PASS**
- SearchPlanner 实际调用模型：['deepseek-flash']
- 工作流正常返回：True
- 质量门结果：SUCCESS（与“进程完成”分开记录）
- 完整无密钥快照：`effective-config.json`

```json
{
  "workflow": {
    "max_rounds": 1,
    "max_concurrency": 4,
    "min_final_evidence_cards_per_point": 1
  },
  "runtime_debug": {
    "enabled": true,
    "output_root": "outputs",
    "archive_root": "docs/experiments/runtime",
    "max_inline_bytes": 256000,
    "llm_pricing_path": null
  },
  "processing": {
    "parser": "mineru",
    "dpi": 200,
    "quality_min_chars_per_page": 200,
    "ocr_model": "deepseek-ocr",
    "llm_model": "deepseek-flash",
    "mineru_python": null,
    "mineru_env": "mineru",
    "mineru_worker": "scripts/mineru_worker.py",
    "mineru_backend": "pipeline",
    "mineru_method": "auto",
    "mineru_lang": "ch",
    "mineru_effort": "medium",
    "mineru_timeout_seconds": 1800,
    "mineru_work_root": "outputs/.mineru",
    "mineru_model_source": null
  },
  "coordinator": {
    "version": 1,
    "model": {
      "alias": "deepseek-flash",
      "temperature": 0.2,
      "max_tokens": 4096,
      "timeout_seconds": 300.0,
      "tool_choice": null,
      "enable_thinking": null,
      "thinking_budget": null,
      "reasoning_effort": null
    },
    "prompts": [
      "coordinator/plan",
      "coordinator/plan_supplement",
      "coordinator/synthesize"
    ]
  },
  "point_extractor": {
    "version": 1,
    "model": {
      "alias": "deepseek-flash",
      "temperature": 0.2,
      "max_tokens": 8192,
      "timeout_seconds": 600.0,
      "tool_choice": null,
      "enable_thinking": null,
      "thinking_budget": null,
      "reasoning_effort": null
    },
    "prompts": [
      "extractor/extract_points"
    ]
  },
  "researcher": {
    "version": 1,
    "model": {
      "alias": "deepseek-flash",
      "temperature": 0.3,
      "max_tokens": 4096,
      "timeout_seconds": 300.0,
      "tool_choice": "auto",
      "enable_thinking": false,
      "thinking_budget": null,
      "reasoning_effort": null
    },
    "prompt": "research/native_tool_loop",
    "harness": {
      "max_turns": 18,
      "max_total_tool_calls": 16,
      "per_tool_limits": {
        "database_search": 4,
        "web_search": 5,
        "browser": 3,
        "reader": 10
      }
    },
    "tools": {
      "database_search": {
        "active_source": "arxiv",
        "candidate_limit_per_task": 8,
        "candidate_excerpt_chars": 2000,
        "full_text_limit_per_task": 8,
        "max_concurrency": 4,
        "providers": {
          "arxiv": {
            "enabled": true,
            "min_interval_seconds": 4,
            "timeout_seconds": 20,
            "max_retries": 4,
            "full_text_max_chars": 100000
          },
          "null_catalog": {
            "enabled": true,
            "testing_only": true
          }
        }
      },
      "web_search": {
        "backend": "baidu",
        "enabled": false,
        "default_max_results": 10,
        "max_results_per_call": 50,
        "baidu": {
          "timeout_seconds": 30
        }
      },
      "browser": {
        "backend": "playwright",
        "network_mode": "inherit",
        "navigation_timeout_ms": 30000,
        "max_html_chars": 2000000,
        "max_text_chars": 500000
      },
      "reader": {
        "default_chars_per_read": 8000,
        "max_chars_per_read": 16000,
        "max_total_read_chars": 48000
      }
    }
  },
  "search_planner": {
    "version": 1,
    "model": {
      "alias": "deepseek-flash",
      "temperature": 0.2,
      "max_tokens": 2048,
      "timeout_seconds": 180.0,
      "tool_choice": null,
      "enable_thinking": false,
      "thinking_budget": null,
      "reasoning_effort": null
    },
    "prompt": "search_planner/plan",
    "max_attempts": 3,
    "limits": {
      "max_concepts": 6,
      "max_terms_per_concept": 5,
      "max_alias_per_concept": 4,
      "max_exclude_per_concept": 3,
      "max_term_words": 8,
      "require_escape": false
    }
  },
  "reviewer": {
    "version": 1,
    "enabled": true,
    "model": {
      "alias": "deepseek-flash",
      "temperature": 0.0,
      "max_tokens": 8192,
      "timeout_seconds": 600.0,
      "tool_choice": null,
      "enable_thinking": null,
      "thinking_budget": null,
      "reasoning_effort": null
    },
    "prompt": "reviewer/review_evidence",
    "max_cards_per_call": 8,
    "fail_closed": true
  },
  "models": {
    "glm4.7": {
      "provider": "openai_compatible",
      "base_url": "https://api.siliconflow.cn/v1",
      "model": "Pro/zai-org/GLM-4.7",
      "context_window": 200000,
      "supported_params": [
        "enable_thinking",
        "thinking_budget"
      ],
      "api_key_env": "SILICONFLOW_API_KEY"
    },
    "deepseek-flash": {
      "provider": "openai_compatible",
      "base_url": "https://api.siliconflow.cn/v1",
      "model": "deepseek-ai/DeepSeek-V4-Flash",
      "context_window": 128000,
      "supported_params": [
        "enable_thinking",
        "thinking_budget",
        "reasoning_effort"
      ],
      "api_key_env": "SILICONFLOW_API_KEY"
    },
    "r1-qwen3-8b": {
      "provider": "openai_compatible",
      "base_url": "https://api.siliconflow.cn/v1",
      "model": "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
      "context_window": 128000,
      "supported_params": [
        "enable_thinking",
        "thinking_budget"
      ],
      "api_key_env": "SILICONFLOW_API_KEY"
    },
    "deepseek-ocr": {
      "provider": "openai_compatible",
      "base_url": "https://api.siliconflow.cn/v1",
      "model": "deepseek-ai/DeepSeek-OCR",
      "context_window": 128000,
      "supported_params": [],
      "api_key_env": "SILICONFLOW_API_KEY"
    }
  }
}
```

## 6. MinerU

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
  "elapsed_seconds": 215.251206
}
```

## 7. Reference Bootstrap

```json
{
  "paper_id": "MF2033k6lC",
  "total": 91,
  "bootstrap_ready": true,
  "resolved": 18,
  "ambiguous": 0,
  "not_found": 73,
  "failed": 0,
  "success": true,
  "elapsed_seconds": 397.846819,
  "stderr": "",
  "cooldown_seconds": 20.0
}
```

## 8. 工作流结果

- rounds: 1
- ResearchTasks: 6
- insufficient final evidence points: [{'novelty_point_id': 'NP-1', 'valid_card_count': 0, 'required_card_count': 1, 'reason': 'insufficient_final_evidence'}, {'novelty_point_id': 'NP-3', 'valid_card_count': 0, 'required_card_count': 1, 'reason': 'insufficient_final_evidence'}]

## 9. Tool 调用统计

```json
[
  {
    "point": "NP-1",
    "task": "T-1",
    "attempt": 1,
    "status": "completed",
    "planner_seconds": 7.548584199998004,
    "researcher_seconds": 487.4741375999947,
    "tool_calls": {
      "reference_search": {
        "attempts": 7,
        "success": 7
      },
      "database_search": {
        "attempts": 1,
        "success": 1
      },
      "reader": {
        "attempts": 4,
        "success": 4
      }
    },
    "tool_counters": {
      "tool_rejection_count": 0,
      "multiple_tool_call_dropped_count": 7,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 0,
      "zero_hit_count": 12
    },
    "tokens": 147903,
    "model_calls": 15,
    "warnings": []
  },
  {
    "point": "NP-1",
    "task": "T-2",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 3.592843399994308,
    "researcher_seconds": 433.0809025000053,
    "tool_calls": {
      "reference_search": {
        "attempts": 3,
        "success": 3
      },
      "reader": {
        "attempts": 10,
        "success": 6
      },
      "database_search": {
        "attempts": 3,
        "success": 3
      }
    },
    "tool_counters": {
      "tool_rejection_count": 1,
      "multiple_tool_call_dropped_count": 4,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 4,
      "zero_hit_count": 11
    },
    "tokens": 221493,
    "model_calls": 18,
    "warnings": [
      "native tool harness failed: total tool-call budget exhausted"
    ]
  },
  {
    "point": "NP-2",
    "task": "T-1",
    "attempt": 1,
    "status": "completed",
    "planner_seconds": 7.602335699994001,
    "researcher_seconds": 487.464902300002,
    "tool_calls": {
      "reference_search": {
        "attempts": 1,
        "success": 1
      },
      "database_search": {
        "attempts": 3,
        "success": 3
      },
      "reader": {
        "attempts": 6,
        "success": 6
      }
    },
    "tool_counters": {
      "tool_rejection_count": 0,
      "multiple_tool_call_dropped_count": 1,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 0,
      "zero_hit_count": 8
    },
    "tokens": 113666,
    "model_calls": 13,
    "warnings": []
  },
  {
    "point": "NP-2",
    "task": "T-2",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 6.080060799999046,
    "researcher_seconds": 433.47248930000205,
    "tool_calls": {
      "reference_search": {
        "attempts": 3,
        "success": 3
      },
      "reader": {
        "attempts": 10,
        "success": 3
      },
      "database_search": {
        "attempts": 2,
        "success": 2
      },
      "browser": {
        "attempts": 1,
        "success": 0
      }
    },
    "tool_counters": {
      "tool_rejection_count": 1,
      "multiple_tool_call_dropped_count": 1,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 8,
      "zero_hit_count": 7
    },
    "tokens": 180312,
    "model_calls": 19,
    "warnings": [
      "native tool harness failed: total tool-call budget exhausted"
    ]
  },
  {
    "point": "NP-3",
    "task": "T-1",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 3.531237399998645,
    "researcher_seconds": 177.45062979999784,
    "tool_calls": {
      "reference_search": {
        "attempts": 5,
        "success": 5
      },
      "database_search": {
        "attempts": 2,
        "success": 2
      },
      "reader": {
        "attempts": 6,
        "success": 6
      }
    },
    "tool_counters": {
      "tool_rejection_count": 2,
      "multiple_tool_call_dropped_count": 1,
      "required_reader_correction_count": 1,
      "tool_execution_failure_count": 0,
      "zero_hit_count": 10
    },
    "tokens": 208384,
    "model_calls": 16,
    "warnings": [
      "native tool harness failed: reader cumulative character budget exhausted"
    ]
  },
  {
    "point": "NP-3",
    "task": "T-2",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 5.818985500001872,
    "researcher_seconds": 175.65394079999533,
    "tool_calls": {
      "reference_search": {
        "attempts": 1,
        "success": 1
      },
      "database_search": {
        "attempts": 4,
        "success": 4
      },
      "reader": {
        "attempts": 5,
        "success": 5
      }
    },
    "tool_counters": {
      "tool_rejection_count": 3,
      "multiple_tool_call_dropped_count": 1,
      "required_reader_correction_count": 2,
      "tool_execution_failure_count": 0,
      "zero_hit_count": 6
    },
    "tokens": 195830,
    "model_calls": 15,
    "warnings": [
      "native tool harness failed: database_search tool-call budget exhausted"
    ]
  }
]
```

## 10. Evidence

```json
{
  "built": 3,
  "validator_accepted": 3,
  "validator_rejected": 2,
  "reviewer_accepted": 1,
  "reviewer_rejected": 2,
  "rejected": [
    {
      "card_id": "card_fa58976d87c718a7d5817694",
      "reason": "missing Work: wrk_b6b76b1dae1837f54a226290; missing Artifact: art_b8b821043e4485fda0b8527c"
    },
    {
      "card_id": "card_d3ae4ea3ad208a4f19e5be7c",
      "reason": "missing Work: wrk_712252459ef2697739d75d40; missing Artifact: art_ea01d9c5f48ad68092a07bf7"
    }
  ]
}
```

## 11. 时间统计

```json
{
  "paper_processing_seconds": 215.251206,
  "reference_bootstrap_seconds": 397.846819,
  "workflow_seconds": 893.171546,
  "MinerU + Paper processing_seconds": 215.138803,
  "PointExtractor_seconds": 51.59672,
  "Coordinator_seconds": 5.8e-05,
  "SearchPlanner_seconds": 34.174047,
  "Researcher_seconds": 2194.597002,
  "Validator_seconds": 0.000622,
  "Reviewer_seconds": 8e-06,
  "Report synthesis/render_seconds": 9.139941,
  "total_seconds": 1526.417348,
  "previous_attempt_seconds": 0
}
```

## 12. Token 统计

```json
{
  "total": {
    "prompt_tokens": 1174881,
    "completion_tokens": 39613,
    "total_tokens": 1214494,
    "calls": 106,
    "unreported_calls": 0
  },
  "by_role": {
    "PointExtractor": {
      "prompt_tokens": 23104,
      "completion_tokens": 4275,
      "total_tokens": 27379,
      "calls": 4
    },
    "Report synthesis/render": {
      "prompt_tokens": 77015,
      "completion_tokens": 835,
      "total_tokens": 77850,
      "calls": 1
    },
    "Researcher": {
      "prompt_tokens": 1036083,
      "completion_tokens": 15877,
      "total_tokens": 1051960,
      "calls": 86
    },
    "SearchPlanner": {
      "prompt_tokens": 11523,
      "completion_tokens": 4105,
      "total_tokens": 15628,
      "calls": 10
    },
    "unattributed": {
      "prompt_tokens": 27156,
      "completion_tokens": 14521,
      "total_tokens": 41677,
      "calls": 5
    }
  }
}
```

MinerU external API tokens: 0  
MinerU internal inference tokens: N/A

## 13. 最终报告

- path: `C:\Users\PC\Desktop\Novelty-Multi-Agent-Framework\outputs\MF2033k6lC\report\MF2033k6lC-report.md`
- generated: True

## 14. 与上次实验对比

| 指标 | 上轮 Full Workflow | 本轮 Locator Disabled |
|---|---:|---:|
| PDF parser | text_layer | mineru |
| NoveltyPoints | 2 | 3 |
| ResearchTasks | 4 | 6 |
| EvidenceCards built | 3 | 3 |
| Validator accepted | 0 | 3 |
| Reviewer accepted | 0 | 1 |
| 有效最终报告 | ❌ | True |
| 总耗时 | ≈35 min | 1526.417348 s |
| Total tokens | 未完整记录 | 1214494 |
| PDF→Report 总耗时 | 未记录 | 1526.417348 s |

## 15. 暴露的新问题

见 metrics.json 中的 issues / rejected reasons。

## 16. 结论

Full Pipeline Success；MinerU 真实成功且 locator gate 关闭后存在有效证据闭环。

## 17. 完整规模估算

```json
{}
```

## 18. 金额成本

```json
{
  "currency": "CNY",
  "rate_card_effective_at": "2026-08-31 Asia/Shanghai",
  "pricing_source": "https://siliconflow.cn/pricing",
  "future_pricing_notice": "https://api-docs.siliconflow.cn/docs/release-notes/overview",
  "actual_cost_cny": 0.35394956,
  "by_model": {
    "deepseek-ai/DeepSeek-V4-Flash": {
      "calls": 106,
      "cache_miss_input_tokens": 256353,
      "cache_hit_input_tokens": 918528,
      "output_tokens": 39613,
      "cost_cny": 0.35394956,
      "rates": {
        "cache_miss_input_cny_per_million": 1.0,
        "cache_hit_input_cny_per_million": 0.02,
        "output_cny_per_million": 2.0
      }
    }
  },
  "formula": "(cache_miss_input * miss_rate + cache_hit_input * hit_rate + output * output_rate) / 1,000,000",
  "notes": [
    "MinerU local inference cost is not token-billed and is excluded.",
    "Network/browser/arXiv tools have no metered price in this experiment.",
    "Platform discounts, coupons, taxes, and account-specific billing adjustments are excluded."
  ]
}
```
