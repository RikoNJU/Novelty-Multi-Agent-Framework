# OOP_NeurIPS2025_FullPipelineLive 实验报告

## 1. 实验目的

验证 SearchPlanner 默认模型收敛为 `deepseek-flash` 后，不设置任何
`NOVELTY_*_MODEL` 角色覆盖即可完成 MG19333vrw 工作流并生成报告。

## 2. 基线

- branch: `hyl`
- commit: `d21d39995978c76583f1e107aa1767f67b77aac4`
- started_at: `2026-09-11T15:47:24.962088+00:00`
- execution_status: **COMPLETED**
- status: **INVALID / DEGRADED**

## 3. 固定实验条件

- `paper = MG19333vrw`
- Prompt 与工具预算保持当前仓库配置
- `max_rounds = 1`
- `require_direct_quote = true`
- `require_source_location = false`
- `locator_gate_disabled = true`

## 4. 输入

- PDF: `examples\OOP_NeurIPS2025.pdf`
- size: 1412356 bytes
- pages: 22

## 5. 实际生效配置

- `NOVELTY_*_MODEL` 覆盖：无
- 无覆盖完整运行验收：**PASS**
- SearchPlanner 实际调用模型：['deepseek-flash']
- 工作流正常返回：True
- 质量门结果：INVALID / DEGRADED（与“进程完成”分开记录）
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
      "max_turns": 12,
      "max_total_tool_calls": 10,
      "per_tool_limits": {
        "database_search": 3,
        "web_search": 5,
        "browser": 3,
        "reader": 8
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
            "min_interval_seconds": 3,
            "timeout_seconds": 20,
            "max_retries": 2,
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
  "pages": 22,
  "backend": "pipeline",
  "method": "auto",
  "fallback_triggered": false,
  "warnings": [
    "abstract: 未检测到",
    "keywords: 未检测到",
    "introduction: 未检测到",
    "methods: 未检测到",
    "results: 未检测到",
    "discussion: 未检测到",
    "conclusion: 未检测到",
    "abstract: 使用首页回退"
  ],
  "elapsed_seconds": 87.694633
}
```

## 7. Reference Bootstrap

```json
{
  "paper_id": "OOP_NeurIPS2025",
  "total": 69,
  "bootstrap_ready": true,
  "resolved": 30,
  "ambiguous": 0,
  "not_found": 29,
  "failed": 10,
  "success": true,
  "elapsed_seconds": 202.421367,
  "stderr": ""
}
```

## 8. 工作流结果

- rounds: 1
- ResearchTasks: 6
- insufficient final evidence points: [{'novelty_point_id': 'NP-1', 'valid_card_count': 0, 'required_card_count': 1, 'reason': 'insufficient_final_evidence'}, {'novelty_point_id': 'NP-2', 'valid_card_count': 0, 'required_card_count': 1, 'reason': 'insufficient_final_evidence'}, {'novelty_point_id': 'NP-3', 'valid_card_count': 0, 'required_card_count': 1, 'reason': 'insufficient_final_evidence'}]

## 9. Tool 调用统计

```json
[
  {
    "point": "NP-1",
    "task": "T-1",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 5.89516150000054,
    "researcher_seconds": 152.23635769999964,
    "tool_calls": {
      "reference_search": {
        "attempts": 4,
        "success": 4
      },
      "database_search": {
        "attempts": 3,
        "success": 3
      },
      "web_search": {
        "attempts": 3,
        "success": 0
      }
    },
    "tool_counters": {
      "tool_rejection_count": 1,
      "multiple_tool_call_dropped_count": 2,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 3,
      "zero_hit_count": 6
    },
    "tokens": 192981,
    "model_calls": 13,
    "warnings": [
      "native tool harness failed: total tool-call budget exhausted"
    ]
  },
  {
    "point": "NP-1",
    "task": "T-2",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 7.409855699999753,
    "researcher_seconds": 134.36287860000084,
    "tool_calls": {
      "reference_search": {
        "attempts": 4,
        "success": 4
      },
      "database_search": {
        "attempts": 2,
        "success": 2
      },
      "web_search": {
        "attempts": 4,
        "success": 0
      }
    },
    "tool_counters": {
      "tool_rejection_count": 1,
      "multiple_tool_call_dropped_count": 1,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 4,
      "zero_hit_count": 5
    },
    "tokens": 194488,
    "model_calls": 13,
    "warnings": [
      "native tool harness failed: total tool-call budget exhausted"
    ]
  },
  {
    "point": "NP-2",
    "task": "T-1",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 8.512216399998579,
    "researcher_seconds": 130.34652959999949,
    "tool_calls": {
      "reference_search": {
        "attempts": 5,
        "success": 5
      },
      "web_search": {
        "attempts": 2,
        "success": 0
      },
      "database_search": {
        "attempts": 2,
        "success": 2
      },
      "reader": {
        "attempts": 1,
        "success": 1
      }
    },
    "tool_counters": {
      "tool_rejection_count": 1,
      "multiple_tool_call_dropped_count": 4,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 2,
      "zero_hit_count": 7
    },
    "tokens": 117280,
    "model_calls": 13,
    "warnings": [
      "native tool harness failed: total tool-call budget exhausted"
    ]
  },
  {
    "point": "NP-2",
    "task": "T-2",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 8.675461999999243,
    "researcher_seconds": 152.20057919999817,
    "tool_calls": {
      "reference_search": {
        "attempts": 3,
        "success": 3
      },
      "database_search": {
        "attempts": 2,
        "success": 2
      },
      "web_search": {
        "attempts": 4,
        "success": 0
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
      "tool_execution_failure_count": 4,
      "zero_hit_count": 5
    },
    "tokens": 124351,
    "model_calls": 13,
    "warnings": [
      "native tool harness failed: total tool-call budget exhausted"
    ]
  },
  {
    "point": "NP-3",
    "task": "T-1",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 7.837171300001501,
    "researcher_seconds": 56.68525719999889,
    "tool_calls": {
      "reference_search": {
        "attempts": 3,
        "success": 3
      },
      "web_search": {
        "attempts": 4,
        "success": 0
      },
      "database_search": {
        "attempts": 2,
        "success": 2
      },
      "reader": {
        "attempts": 1,
        "success": 1
      }
    },
    "tool_counters": {
      "tool_rejection_count": 1,
      "multiple_tool_call_dropped_count": 3,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 4,
      "zero_hit_count": 6
    },
    "tokens": 75543,
    "model_calls": 13,
    "warnings": [
      "native tool harness failed: total tool-call budget exhausted"
    ]
  },
  {
    "point": "NP-3",
    "task": "T-2",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 10.883354999998119,
    "researcher_seconds": 59.48817060000147,
    "tool_calls": {
      "reference_search": {
        "attempts": 4,
        "success": 4
      },
      "reader": {
        "attempts": 2,
        "success": 2
      },
      "web_search": {
        "attempts": 3,
        "success": 0
      },
      "database_search": {
        "attempts": 1,
        "success": 1
      }
    },
    "tool_counters": {
      "tool_rejection_count": 1,
      "multiple_tool_call_dropped_count": 4,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 3,
      "zero_hit_count": 5
    },
    "tokens": 194693,
    "model_calls": 13,
    "warnings": [
      "native tool harness failed: total tool-call budget exhausted"
    ]
  }
]
```

## 10. Evidence

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

## 11. 时间统计

```json
{
  "paper_processing_seconds": 87.694633,
  "reference_bootstrap_seconds": 202.421367,
  "workflow_seconds": 277.881974,
  "MinerU + Paper processing_seconds": 87.654679,
  "PointExtractor_seconds": 27.083206,
  "Coordinator_seconds": 5.2e-05,
  "SearchPlanner_seconds": 49.213222,
  "Researcher_seconds": 685.319773,
  "Validator_seconds": 1.2e-05,
  "Reviewer_seconds": 4e-06,
  "Report synthesis/render_seconds": 7.128759,
  "total_seconds": 568.150688,
  "previous_attempt_seconds": 0
}
```

## 12. Token 统计

```json
{
  "total": {
    "prompt_tokens": 954338,
    "completion_tokens": 16046,
    "total_tokens": 970384,
    "calls": 83,
    "unreported_calls": 0
  },
  "by_role": {
    "PointExtractor": {
      "prompt_tokens": 26035,
      "completion_tokens": 2621,
      "total_tokens": 28656,
      "calls": 4
    },
    "Report synthesis/render": {
      "prompt_tokens": 41773,
      "completion_tokens": 619,
      "total_tokens": 42392,
      "calls": 1
    },
    "Researcher": {
      "prompt_tokens": 869679,
      "completion_tokens": 7385,
      "total_tokens": 877064,
      "calls": 66
    },
    "SearchPlanner": {
      "prompt_tokens": 16851,
      "completion_tokens": 5421,
      "total_tokens": 22272,
      "calls": 12
    }
  }
}
```

MinerU external API tokens: 0  
MinerU internal inference tokens: N/A

## 13. 最终报告

- path: `C:\Users\PC\Desktop\Novelty-Multi-Agent-Framework\outputs\OOP_NeurIPS2025\report\OOP_NeurIPS2025-report.md`
- generated: True

## 14. 与上次实验对比

| 指标 | 上轮 Full Workflow | 本轮 Locator Disabled |
|---|---:|---:|
| PDF parser | text_layer | mineru |
| NoveltyPoints | 2 | 3 |
| ResearchTasks | 4 | 6 |
| EvidenceCards built | 3 | 0 |
| Validator accepted | 0 | 0 |
| Reviewer accepted | 0 | 0 |
| 有效最终报告 | ❌ | False |
| 总耗时 | ≈35 min | 568.150688 s |
| Total tokens | 未完整记录 | 970384 |
| PDF→Report 总耗时 | 未记录 | 568.150688 s |

## 15. 暴露的新问题

见 metrics.json 中的 issues / rejected reasons。

## 16. 结论

程序已闭环，但未同时满足 MinerU、Validator、Reviewer 和有效报告标准。

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
  "actual_cost_cny": 0.27443256,
  "by_model": {
    "deepseek-ai/DeepSeek-V4-Flash": {
      "calls": 83,
      "cache_miss_input_tokens": 227810,
      "cache_hit_input_tokens": 726528,
      "output_tokens": 16046,
      "cost_cny": 0.27443256,
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
