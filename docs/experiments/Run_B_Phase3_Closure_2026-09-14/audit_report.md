# Run B：Phase 3 P0 闭环审计报告

## 1. 审计结论

结果：`PASS（P0 闭环通过，保留已知 P1 问题）`。

本次 Run B 使用固定 PaperInput 验证了 Phase 3 的三个 P0 修复：

- BUG-001：标准完整工作流真实执行 Reviewer；
- BUG-003：`database_search` 的成功、空结果与失败状态保持真实；
- BUG-002：Reviewer 裁定完整进入 Final Report，并由 Renderer 仅依据 Final Report 展示。

Run B 最终状态为 `SUCCESS`，最后完成阶段为 `render_report`。Reviewer 与 Final Report 的三个 point 全部一一对应，Integrity Gate 未发现裁定漂移。

## 2. 冻结身份

| 项目 | 值 |
|---|---|
| Paper ID | `MF2033k6lC` |
| Run ID | `run-1c18f37841424901b40e5f7d76dfa80b` |
| 入口 | `paper_input` |
| PaperInput SHA-256 | `89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66` |
| Git commit | `f800449a84c69c98cdf249ce325a635915af9fbf` |
| Git subject | `fix(report): bind reviewer verdicts into final report` |
| 开始时间（UTC） | `2026-09-13T21:13:58.376883+00:00` |
| 结束时间（UTC） | `2026-09-13T22:07:15.578017+00:00` |
| 运行时长 | `3,197,292 ms`（约 53 分 17 秒） |
| 最大轮数 | `1` |
| 最大并发 | `4` |

运行命令：

```bash
/home/lya3106643285/miniconda3/envs/Novelty/bin/python \
  scripts/run_full_workflow_live.py \
  --paper-json outputs/MF2033k6lC/paper-input/others/paper.json \
  --output /tmp/part1-phase3-run-b-result.json \
  --max-rounds 1 \
  --max-concurrency 4
```

## 3. BUG-001：Reviewer 真实运行

结果：`PASS`。

- `review_evidence` 为真实 Runtime stage，状态为 `SUCCESS`；
- Reviewer diagnostic 的 `ok=true`；
- 输入包含 3 个 NoveltyPoint，输出包含 3 条 Review；
- `missing_review_point_ids=[]`；
- `duplicate_review_point_ids=[]`；
- `unexpected_review_point_ids=[]`；
- Gate A 接受 3/3 张 EvidenceCard，Reviewer 前后卡片集合保持一致；
- Reviewer 产生了 3 次 Reader 调用，证明不是 disabled 占位路径。

Reviewer 输出如下：

| Point | Review status | Verdict | Confidence | Highly relevant works |
|---|---|---|---:|---:|
| NP-1 | `insufficient_evidence` | `null` | `null` | 0 |
| NP-2 | `insufficient_evidence` | `null` | `null` | 0 |
| NP-3 | `reviewed` | `partially_novel` | 0.70 | 3 |

NP-1、NP-2 的 `verdict=null` 是证据不足语义，不是 Reviewer 未运行。

## 4. BUG-003：数据库检索状态真实性

结果：`PASS`。

Runtime summary 中的工具统计：

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| `reference_search` | 28 | 23 | 5 | 8 |
| `database_search` | 18 | 9 | 9 | 5 |
| `reader` | 25 | 22 | 3 | 0 |

在线 arXiv 检索出现 `ReadTimeout` / `all 6 search executions failed` 时：

- tool record 的 `execution_status` 为 `FAILED`；
- `failure_phase` 为 `TOOL_EXECUTION`；
- `execution_summary.all_failed=true`；
- `failed=6`、`succeeded=0`；
- 失败没有被折叠成正常的零结果。

因此 Run B 中的空结果只代表已成功执行但无命中，外部超时则保持为失败状态。工作流能够在部分检索失败时保留审计事实并继续完成。

## 5. BUG-002：Reviewer → Final Report → Renderer

结果：`PASS`。

### 5.1 Reviewer 与 Final Report 对照

| Point | Reviewer | Final Report | Renderer |
|---|---|---|---|
| NP-1 | `insufficient_evidence`, verdict `null` | `insufficient_evidence`, verdict `null` | 证据不足，无法裁定 |
| NP-2 | `insufficient_evidence`, verdict `null` | `insufficient_evidence`, verdict `null` | 证据不足，无法裁定 |
| NP-3 | `reviewed`, `partially_novel`, 0.70 | `reviewed`, `partially_novel`, 0.70 | 部分新颖，置信度 0.70 |

NP-3 的以下 Reviewer 权威字段完整保留到 `report.json`：

- `review_status`；
- `verdict`；
- `verdict_reason`；
- `confidence`；
- 3 条 `highly_relevant_works`，包括 `work_id`、`card_ids`、`evidence_ids` 与 `relevance_reason`。

Coordinator 生成的报告摘要仍被保留，但不再拥有覆盖 Reviewer 裁定与置信度的权限。

### 5.2 Integrity Gate

`validate_report_integrity` 的 Review → Conclusion closure 审计：

```text
review_count=3
conclusion_count=3
checked_conclusion_count=3
matched_count=3
mismatch_count=0
mismatched_point_ids=[]
issues=[]
validation_passed=true
```

Gate 同时确认 Final Report 引用 3 张 EvidenceCard，所有引用均可解析。

### 5.3 Renderer

Renderer 只消费 Final Report 的权威结论，不读取 `novelty-reviews.json` 决定优先级。生成的 Markdown 中可见：

- `NP-1 · 证据不足，无法裁定`；
- `NP-2 · 证据不足，无法裁定`；
- `NP-3 · 部分新颖`；
- NP-3 的 Reviewer 裁定理由、`0.70` 置信度、报告摘要与高相关工作。

这与 Run A 中 Reviewer 为 `insufficient_evidence`、最终报告却输出 `strong` 的失败情况形成直接闭环。

## 6. 自动化测试

BUG-002 定向测试共 64 项通过，覆盖：

- `novel`、`partially_novel`、`not_novel`、`insufficient_evidence` 的报告及中文渲染；
- Coordinator verdict 漂移与 confidence 漂移；
- 缺失 Review、未知 Review、重复 point；
- `highly_relevant_works` 传递；
- Renderer 仅依赖 `report.json`；
- Integrity Gate 的匹配计数与 mismatch 明细。

广泛回归命令：

```bash
/home/lya3106643285/miniconda3/envs/Novelty/bin/pytest -q \
  --ignore=tests/test_api.py \
  -k 'not test_fetch_collects_rendered_content_and_applies_limits'
```

结果通过，6 项跳过。排除项是既有环境问题：TestClient 挂起，以及 Playwright mock 与当前代理参数不兼容；不属于本次修复。

## 7. 已知 P1 问题

本次 P0 验收不掩盖以下问题：

- NP-1、NP-2 的中英文检索均未形成最终有效 EvidenceCard，只能判定为证据不足；
- Reviewer 对 NP-3 的 3 次 Reader 调用因 research manifest namespace 不包含对应 artifact 而失败，但既有 EvidenceCard 已足以完成 Reviewer 裁定；
- `diagnostics/reviewer.json` 总体仍为 `ok=true`，其内部 Reader namespace 失败应作为后续“namespace diagnostic 假阳性”P1 项继续处理；
- arXiv 在线端存在多次读取超时，导致 Run B 用时较长。

这些问题不改变本次结论：Reviewer 已真实运行，数据库失败状态可信，Reviewer 的权威裁定已无漂移地进入最终报告与 Renderer。

## 8. 可追溯产物

完整 Runtime 现场：

```text
outputs/MF2033k6lC/runtime/run-1c18f37841424901b40e5f7d76dfa80b/
```

业务产物：

| 产物 | SHA-256 |
|---|---|
| `outputs/MF2033k6lC/novelty-reviews.json` | `f3db3cded4964c894577a3cd9b2470bb75aa6a652138deaad6ccc43023fe8b41` |
| `outputs/MF2033k6lC/report.json` | `e60d45b91f945901e12297704dd282df745b7ec705b0bfd0e51b496e12fed1e2` |
| `outputs/MF2033k6lC/report/MF2033k6lC-report.md` | `b1a3d286232fec4e80d68cdb889c290da6a317887cf6de21f77bfea80a6b08db` |
| Runtime `manifest.json` | `c366081b492fef067871a754aa33db4d183a77636fca2cefbaa9ba9f6af7d2f3` |
| Runtime `summary.json` | `c9e60570bf82c41f5fb28b1c82ad1e03a3ec65a34cbd3f8e5e8ec8f3135c0a25` |

Runtime 目录受 `.gitignore` 管理，本报告记录其身份、关键指标与内容哈希，不复制运行现场。

## 9. 最终判定

| 验收项 | 结果 |
|---|---|
| BUG-001 Reviewer 真实运行 | PASS |
| BUG-003 database_search 状态真实 | PASS |
| BUG-002 Reviewer → Report 权威字段闭合 | PASS |
| BUG-002 Report → Renderer 语义闭合 | PASS |
| Review/Conclusion 一一覆盖 | PASS（3/3） |
| 裁定漂移 | 0 |
| Phase 3 P0 | CLOSED |
