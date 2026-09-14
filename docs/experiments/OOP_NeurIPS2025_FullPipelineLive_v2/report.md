# OOP_NeurIPS2025_FullPipelineLive_v2 实验报告

## 1. 实验目的

验证 SearchPlanner 默认模型收敛为 `deepseek-flash` 后，不设置任何
`NOVELTY_*_MODEL` 角色覆盖即可完成 MG19333vrw 工作流并生成报告。

## 2. 基线

- branch: `hyl`
- commit: `8c69cf4fa6c04d6bd69fcd1f2d5b667220782625`
- started_at: `2026-09-11T16:07:54.510557+00:00`
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
  "elapsed_seconds": 76.008224
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
  "elapsed_seconds": 0.518173,
  "stderr": "",
  "cooldown_seconds": 20.0
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
    "planner_seconds": 2.5126123999980337,
    "researcher_seconds": 839.2359147999996,
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
        "attempts": 5,
        "success": 5
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
      "tool_execution_failure_count": 1,
      "zero_hit_count": 6
    },
    "tokens": 126446,
    "model_calls": 12,
    "warnings": [
      "native tool harness failed: total tool-call budget exhausted"
    ]
  },
  {
    "point": "NP-1",
    "task": "T-2",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 5.426772599999822,
    "researcher_seconds": 458.73355040000024,
    "tool_calls": {
      "reference_search": {
        "attempts": 2,
        "success": 2
      },
      "database_search": {
        "attempts": 3,
        "success": 3
      },
      "reader": {
        "attempts": 4,
        "success": 4
      }
    },
    "tool_counters": {
      "zero_hit_count": 7,
      "tool_rejection_count": 1,
      "multiple_tool_call_dropped_count": 0,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 0
    },
    "tokens": 221683,
    "model_calls": 12,
    "warnings": [
      "native tool harness failed: database_search tool-call budget exhausted"
    ]
  },
  {
    "point": "NP-2",
    "task": "T-1",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 7.108288600000378,
    "researcher_seconds": 430.3599482999998,
    "tool_calls": {
      "reference_search": {
        "attempts": 1,
        "success": 1
      },
      "database_search": {
        "attempts": 1,
        "success": 1
      },
      "reader": {
        "attempts": 8,
        "success": 4
      }
    },
    "tool_counters": {
      "tool_rejection_count": 1,
      "multiple_tool_call_dropped_count": 1,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 4,
      "zero_hit_count": 5
    },
    "tokens": 147731,
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
    "planner_seconds": 2.9966999999996915,
    "researcher_seconds": 430.35772449999786,
    "tool_calls": {
      "reference_search": {
        "attempts": 2,
        "success": 2
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
      "tool_rejection_count": 1,
      "multiple_tool_call_dropped_count": 2,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 0,
      "zero_hit_count": 9
    },
    "tokens": 111850,
    "model_calls": 12,
    "warnings": [
      "native tool harness failed: total tool-call budget exhausted"
    ]
  },
  {
    "point": "NP-3",
    "task": "T-1",
    "attempt": 1,
    "status": "partial",
    "planner_seconds": 6.70539220000137,
    "researcher_seconds": 430.17539540000143,
    "tool_calls": {
      "reference_search": {
        "attempts": 6,
        "success": 6
      },
      "database_search": {
        "attempts": 1,
        "success": 1
      },
      "reader": {
        "attempts": 2,
        "success": 2
      }
    },
    "tool_counters": {
      "tool_rejection_count": 2,
      "multiple_tool_call_dropped_count": 8,
      "required_reader_correction_count": 1,
      "tool_execution_failure_count": 0,
      "zero_hit_count": 5
    },
    "tokens": 139034,
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
    "planner_seconds": 6.271136100000149,
    "researcher_seconds": 423.3394326000016,
    "tool_calls": {
      "reference_search": {
        "attempts": 2,
        "success": 2
      },
      "reader": {
        "attempts": 6,
        "success": 4
      },
      "database_search": {
        "attempts": 2,
        "success": 2
      }
    },
    "tool_counters": {
      "tool_rejection_count": 1,
      "multiple_tool_call_dropped_count": 2,
      "required_reader_correction_count": 0,
      "tool_execution_failure_count": 2,
      "zero_hit_count": 6
    },
    "tokens": 224682,
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
  "paper_processing_seconds": 76.008224,
  "reference_bootstrap_seconds": 0.518173,
  "workflow_seconds": 921.961899,
  "MinerU + Paper processing_seconds": 75.97201,
  "PointExtractor_seconds": 23.020792,
  "Coordinator_seconds": 5.8e-05,
  "SearchPlanner_seconds": 31.020902,
  "Researcher_seconds": 3012.201966,
  "Validator_seconds": 1.4e-05,
  "Reviewer_seconds": 4e-06,
  "Report synthesis/render_seconds": 6.504691,
  "total_seconds": 1018.665296,
  "previous_attempt_seconds": 0
}
```

## 12. Token 统计

```json
{
  "total": {
    "prompt_tokens": 1023286,
    "completion_tokens": 19505,
    "total_tokens": 1042791,
    "calls": 80,
    "unreported_calls": 0
  },
  "by_role": {
    "PointExtractor": {
      "prompt_tokens": 26313,
      "completion_tokens": 2511,
      "total_tokens": 28824,
      "calls": 4
    },
    "Report synthesis/render": {
      "prompt_tokens": 42071,
      "completion_tokens": 470,
      "total_tokens": 42541,
      "calls": 1
    },
    "Researcher": {
      "prompt_tokens": 939735,
      "completion_tokens": 11941,
      "total_tokens": 951676,
      "calls": 65
    },
    "SearchPlanner": {
      "prompt_tokens": 15167,
      "completion_tokens": 4583,
      "total_tokens": 19750,
      "calls": 10
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
| 总耗时 | ≈35 min | 1018.665296 s |
| Total tokens | 未完整记录 | 1042791 |
| PDF→Report 总耗时 | 未记录 | 1018.665296 s |

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
  "actual_cost_cny": 0.2419184,
  "by_model": {
    "deepseek-ai/DeepSeek-V4-Flash": {
      "calls": 80,
      "cache_miss_input_tokens": 186166,
      "cache_hit_input_tokens": 837120,
      "output_tokens": 19505,
      "cost_cny": 0.2419184,
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
