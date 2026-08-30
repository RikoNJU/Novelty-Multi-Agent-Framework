# Reference Bootstrap 独立运行实验报告

## 1. 实验目标

验证 `Reference Bootstrap` 能否在不进入 Researcher 的情况下独立运行，并完成：

- 读取已持久化的 `PaperInput.references`；
- 对每条 citation 执行明确的 resolution attempt；
- 增量写入 `subject_references/bootstrap.json`；
- 将成功解析的 canonical literature assets 写入 `subject_references/list.json` 和 `documents/`；
- 达成 Bootstrap Barrier；
- 记录运行时间、召回结果和 provider 失败情况。

## 2. 实验对象与环境

- 实验日期：2026-08-30（Asia/Shanghai）
- `paper_id`：`MF2033k6lC`
- 原始参考文献数：91
- Provider：arXiv
- 最大 citation 并发配置：4
- Researcher：未启动
- LLM：未调用
- 执行入口：`scripts/reference_bootstrap.py`

正式实验命令：

```bash
/usr/bin/time -f 'WALL_SECONDS=%e USER_SECONDS=%U SYSTEM_SECONDS=%S MAX_RSS_KB=%M EXIT_CODE=%x' \
  python scripts/reference_bootstrap.py \
  --paper-id MF2033k6lC \
  --output-root outputs \
  --max-concurrency 4 \
  --provider arxiv \
  --force
```

正式运行前曾在受限沙箱中试跑，网络调用统一返回 `Operation not permitted`。该次运行被中止并通过 `--force` 全量重跑，其耗时和状态未计入正式结果。

## 3. 运行结果

### 3.1 Barrier 与进程结果

| 指标 | 结果 |
|---|---:|
| CLI exit code | 0 |
| Bootstrap Barrier | 通过 |
| terminal entries | 91 / 91 |
| 总 attempts | 101 |
| 墙钟时间 | 343.24 秒（5 分 43.24 秒） |
| CPU user time | 0.64 秒 |
| CPU system time | 0.17 秒 |
| 最大常驻内存 | 85,412 KB |

### 3.2 Citation 解析

| 字段 | 数量 | 占 91 条比例 |
|---|---:|---:|
| 至少解析出 title/identifier/url | 91 | 100.00% |
| title | 91 | 100.00% |
| year | 91 | 100.00% |
| arXiv ID | 18 | 19.78% |
| URL | 1 | 1.10% |
| DOI | 0 | 0.00% |

这里的“解析成功”只表示产生了结构化字段，不表示 title 切分质量已经达到可用于高质量 known-item search 的水平。

### 3.3 Resolution 终态

| 状态 | 数量 | 比例 |
|---|---:|---:|
| RESOLVED | 9 | 9.89% |
| AMBIGUOUS | 0 | 0.00% |
| NOT_FOUND | 49 | 53.85% |
| FAILED | 33 | 36.26% |
| 合计 | 91 | 100.00% |

成功解析的 9 条全部来自 `arxiv_exact`：citation ordinal 7、8、13、15、25、32、34、43、58。

Attempt 方法统计：

| 方法 | 调用次数 |
|---|---:|
| `arxiv_exact` | 18 |
| `url_exact` | 1 |
| `known_item` | 82 |
| 合计 | 101 |

Provider 调用全部由 `arxiv` 完成，没有调用 Researcher-facing 的 `database_search`、`web_search`、`browser` 或 `reader`。

### 3.4 召回率

本实验没有人工标注的 gold identity 集合，因此报告的是 Bootstrap resolution recall，而非传统 IR 的 gold-set recall。

主要指标：

```text
总体召回率 = RESOLVED / 全部 citations
           = 9 / 91
           = 9.89%
```

辅助指标：

```text
有效请求召回率 = RESOLVED / (全部 citations - provider FAILED)
               = 9 / (91 - 33)
               = 15.52%
```

```text
已识别 arXiv ID 的 exact resolve 成功率
= 9 / 18
= 50.00%
```

这三个指标不可互相替代。9.89% 是本次端到端实际结果；15.52% 用于观察剔除 provider 硬失败后的表现；50.00% 只衡量具有 arXiv 强标识符的子集。

## 4. Provider 失败分析

- 失败 attempts：42 次。
- 错误类型：42/42 均为 `HTTPStatusError`。
- HTTP 状态：全部为 arXiv API `429`。
- 最终受影响 citation：33 条 `FAILED`。

因此，本次低召回不能完全解释为 citation 不存在。后半段请求受到 arXiv 限流，至少 33 条 citation 未获得有效 provider 响应。

此外还观察到两个实现问题：

1. arXiv provider 是同步客户端，并在事件循环中执行节流，`max_concurrency=4` 没有实现预期的 citation 级网络并发。
2. 当前 title parser 对多数参考文献保留了作者、载体和页码等整段文本，导致 `known_item` 查询过长；本次 structured known-item resolve 为 0。

## 5. Materialization 结果

| 资产 | 数量 |
|---|---:|
| Work | 9 |
| SourceRecord | 9 |
| Artifact | 9 |
| abstract artifacts | 9 |
| metadata-only records | 9 |
| full-text artifacts | 0 |
| document 文件总字节 | 11,473 bytes |

本次 provider 仅在 Bootstrap 中接入 identity/known-item search；尚未接入 Bootstrap 的 full-text acquisition，因此 0 个全文属于当前 capability 边界，不是 Barrier 失败。

## 6. 输出目录验收

实际生成结构：

```text
outputs/MF2033k6lC/subject_references/
├── bootstrap.json                 # 134,093 bytes，91 条 citation ledger
├── list.json                      # 34,308 bytes，9 组 canonical assets
├── experiment-report.md           # 本报告
└── documents/
    ├── wrk_03271ba.../art_66c8b8....txt
    ├── wrk_3180db.../art_646de9....txt
    ├── wrk_712252.../art_ea01d9....txt
    ├── wrk_956798.../art_414402....txt
    ├── wrk_ad8ebe.../art_1f3171....txt
    ├── wrk_b6b76b.../art_b8b821....txt
    ├── wrk_e59b8b.../art_d88778....txt
    ├── wrk_f071f8.../art_0d2cde....txt
    └── wrk_ff5aa1.../art_6f9881....txt
```

`subject_references/` 的必需目录和文件均已生成。运行未把 Bootstrap 资产写入普通 `references/` corpus。

## 7. 结论

独立运行链路功能上成立：脚本未进入 Researcher，91 条 citation 全部获得可审计的 terminal attempt，Barrier 通过，CLI 正常返回 0，并生成了完整的 subject-reference ledger、manifest 和 documents 目录。

但检索质量尚未达到可接受水平。本次实际总体召回率仅为 9.89%，主要受 arXiv 429 限流、单 provider 覆盖范围和 title parser 查询质量影响。当前结果应视为“Bootstrap 基础设施与 exact arXiv 路径通过”，不能视为“多来源 Reference Bootstrap 已达到生产召回率”。

建议下一轮实验前完成：

1. 对 429 增加 `Retry-After`、指数退避与全局 provider rate limiter；
2. 将同步 provider 调用放入线程或改用 async client；
3. 改进 citation title/author/venue 边界解析；
4. 接入 DOI/Crossref/OpenAlex known-item provider；
5. 接入 metadata/full-text acquisition 后补测全文获得率；
6. 建立人工 gold identity 子集，报告真正的 precision、recall 和 ambiguous accuracy。
