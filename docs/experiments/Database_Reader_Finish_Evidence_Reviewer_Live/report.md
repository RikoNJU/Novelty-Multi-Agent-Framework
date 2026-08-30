# Database → Reader → Finish → EvidenceCard → Reviewer 单 Task 真实实验报告

## 1. 实验目标

本实验验证一项临时 Researcher 停止策略：

> 完成至少一次成功数据库检索和一次成功 Reader 后，不再调用任何工具；模型必须基于
> 已读正文立即返回 `ResearchFinishDraft`。若存在逐字支持文本则生成卡片，否则明确返回
> `cards=[] + no_evidence_reason`。

同时验证完整下游链路：

```text
database_search
  → reader
  → ResearchFinishDraft
  → EvidenceCardBuilder
  → EvidenceCard
  → NoveltyEvidenceReviewer
  → EvidenceReviewDecision
```

结论：**临时停止策略、EvidenceCard 生成和正式 Reviewer 调用均完成真实验证。Builder
生成 1 张 EvidenceCard 和 2 条 Evidence；Reviewer 返回 1 条结构化 reject decision。Reviewer
拒绝理由依赖错误的“当前日期”前提，因此证明了审查管线可运行，但不证明该卡应被内容性拒绝。**

## 2. 实验范围与控制变量

- 实验时间：2026-08-30 19:01:32–19:04:40（Asia/Shanghai）
- Reviewer 恢复审查：随后单独执行，耗时 52,535 ms
- 代码基线：`1e17ad7d4d4e9f531045f909603a67ba3edd1c10` 加未提交实验修正
- 论文输入：MF2033k6lC 已持久化真实输入
- NoveltyPoint / Task：`NP-1 / T-1`
- Task 类型：`literature_search`
- 注册工具：`database_search`、`reader`
- 禁用工具：`web_search`、`browser`
- Researcher 临时 Prompt：`research/database_reader_finish_once`
- Reviewer：正式 `NoveltyEvidenceReviewer`，模型别名 `deepseek-flash`，fail-closed

第一次尝试使用当轮实时 Planner 计划，但 arXiv 和 null_catalog 均返回 0 条，模型正确输出
`cards=[] + no_evidence_reason`。这验证了临时策略的无证据分支，但无法测试 Builder 和 Reviewer。

为聚焦本实验目标，最终复验改用前序 live 已验证能召回 arXiv 候选的固定控制 SearchPlan。
该计划仍使用正式 SearchPlan schema、共享 Expression Grammar、QueryAdapter 和真实 arXiv；
仅固定 Concept/term/strategy，避免 Planner 随机召回质量成为干扰变量。最终实验的 Planner
调用与 token 均记为 0。

## 3. 临时停止策略

实验专用 Prompt 明确要求：

1. 只使用注册工具和工具描述列出的 `source_id`；
2. 数据库返回 `artifact_ids` 后选择一个 Artifact 调用 Reader；
3. 至少一次数据库成功且一次 Reader 成功后，不得再次调用工具；
4. 有逐字证据时生成卡片；文本不足时明确无证据结束；
5. quote 必须逐字复制 Reader 内容，禁止翻译、改写或重构。

该策略只用于本实验，没有替换正式 `research/native_tool_loop`。

## 4. 实际工具与 Finish 轨迹

最终轨迹严格收敛为：

```text
database_search(source_id="arxiv")
  → SUCCESS：8 个候选作品及可读 Artifact

reader(artifact_id="art_aa745815ca866a6efdec7c9e")
  → SUCCESS：读取字符 [0, 8000)

无后续工具调用
  → ResearchFinishDraft JSON
```

指标：

| 指标 | 结果 |
| --- | ---: |
| database_search | 1 |
| reader | 1 |
| web_search | 0 |
| browser | 0 |
| Legacy Planner | 0 |
| Finish reached | true |
| Finish schema valid | true |
| Finish draft cards | 1 |
| Task status | completed |
| Task warnings | 0 |

因此 `database_search → reader → finish` 临时策略通过真实模型验证。

## 5. EvidenceCardBuilder 结果

Builder 从一张模型草稿生成：

- Evidence：2 条；
- EvidenceCard：1 张；
- Card ID：`card_3e303f9b5f542fab369d6d7d`；
- 文献：*Enhancing Distance-Based Graph Autoencoders with Structural Penalties for Dynamic Graph Embedding*；
- arXiv：`2608.18762v1`，页面正文标注 19 Aug 2026；
- relevance：0.4；
- confidence：0.9。

两条 quote 为：

```text
Graph autoencoders (GAEs) are widely used for learning representations of dynamic graphs.
```

```text
We propose three distance-based GAE variants that incorporate structural penalties into the reconstruction loss.
```

两条文本均可在成功 Reader observation 中逐字找到，Builder 将其绑定到同一真实来源，并生成
两个 Evidence ID。卡片明确区分了重叠点（图自编码器、动态图表示学习）和差异点（未使用图摘要、
未使用 RNN、核心为结构惩罚），没有形成全局新颖性结论。

## 6. Reviewer 检验

### 6.1 首次调用

Reviewer 首次使用默认模型读取超时，60 秒后 fail-closed，产生
`review_failed: The read operation timed out`。这暴露出实验装配没有把 reviewer.json 中的
`timeout_seconds=600` 和 `max_tokens=8192` 传入调用。

实验随后加入 `--review-only` 恢复模式和配置化 Reviewer client，复用同一 EvidenceCard，
不重复检索或 Researcher。

### 6.2 恢复审查结果

- Reviewer 真实模型调用：1 次；
- elapsed：52,535 ms；
- token：4,185；
- decision：1；
- verdict：`reject`；
- reviewed confidence：0.1；
- accepted / rejected / needs_more：0 / 1 / 0。

模型返回两个非标准 issue code：`INVALID_SOURCE_URL` 和 `UNVERIFIABLE_SOURCE`。正式 Reviewer
白名单清洗逻辑将二者安全转换为 `missing_evidence_detail`，没有让未知枚举污染正式 schema。

Reviewer 的核心理由是：它认为当前日期为 2026-04-27，而 arXiv `2608.18762` 属于
2026 年 8 月，所以来源“不可能存在”。该前提与实验实际日期 2026-08-30 冲突，且真实 arXiv
检索、元数据和 Reader 正文均记录论文日期为 19 Aug 2026。因此：

- Reviewer 调用、schema 校验、未知 issue 清洗、fail-closed 和 verdict 路由均验证成功；
- 本次 reject 不能作为卡片来源无效的可靠结论；
- Reviewer Prompt/上下文缺少可信当前日期，模型使用了错误内部日期。

## 7. Token 与耗时

| 阶段 | Token | 耗时 |
| --- | ---: | ---: |
| SearchPlanner | 0（控制计划） | 0 |
| Researcher | 15,048 | 127,761 ms |
| Reviewer 恢复审查 | 4,185 | 52,535 ms |
| 合计 | 19,233 | — |

## 8. 验收矩阵

| 验收项 | 结果 |
| --- | --- |
| 新实验与旧 Issue #7 实验隔离 | PASS |
| 实验专用临时 Prompt | PASS |
| WebSearch/Browser 禁用 | PASS |
| 一次数据库成功 | PASS |
| 至少一次 Reader 成功 | PASS |
| Reader 后不再调用工具 | PASS |
| ResearchFinishDraft 合法 | PASS |
| EvidenceCardBuilder 执行 | PASS |
| EvidenceCard 生成 | PASS（1 张） |
| quote 与 Reader 逐字一致 | PASS（2/2） |
| 正式 Reviewer 模型调用 | PASS |
| Reviewer 结构化 decision | PASS（1 条 reject） |
| Reviewer verdict 内容可靠 | FAIL（错误当前日期前提） |
| Legacy Planner 为 0 | PASS |

## 9. 限制与建议

1. 控制 SearchPlan 用于隔离停止策略，不代表实时 Planner 每次都能产生足够召回。
2. 当前临时策略只读一个 Artifact，可能过早停止；适合验证 Builder/Reviewer，不适合作为最终召回策略。
3. Reviewer 应在 Prompt 中接收运行时可信日期，且不得仅凭 arXiv 编号月份推断 URL 无效。
4. Reviewer 的模型调用应在正式实现中传递配置的 timeout/max_tokens，而不只由实验 wrapper 修正。
5. `INVALID_SOURCE_URL`、`UNVERIFIABLE_SOURCE` 是否应加入正式 issue 白名单，需要单独设计；本次清洗为
   `missing_evidence_detail` 符合当前防御性契约。

## 10. 实验产物

- `outputs/experiments/database-reader-finish-evidence-reviewer-live/summary.json`
- `outputs/experiments/database-reader-finish-evidence-reviewer-live/task_request.json`
- `outputs/experiments/database-reader-finish-evidence-reviewer-live/task_result.json`
- `outputs/experiments/database-reader-finish-evidence-reviewer-live/evidence_cards.json`
- `outputs/experiments/database-reader-finish-evidence-reviewer-live/review_result.json`
- `outputs/experiments/database-reader-finish-evidence-reviewer-live/trace.jsonl`
- `outputs/experiments/database-reader-finish-evidence-reviewer-live/model_calls.json`
- `outputs/experiments/database-reader-finish-evidence-reviewer-live/reviewer_resume_model_calls.json`
- `outputs/experiments/database-reader-finish-evidence-reviewer-live/effective_config.json`

本报告与 Issue #7 原报告分开保存；实验产物不包含 API Key。
