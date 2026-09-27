# Reviewer 增量证据诊断误报与汇总恢复接口审查

日期：2026-09-27。范围：离线历史产物、只读诊断脚本与本地回归。无在线请求、无模型调用、无 Provider 变更。

结论：已修复 `scripts/reviewer_diagnostics.py` 遗漏 `review.review_evidence` 的引用误报。真实完整运行的两条错误均消失；原始 Card 证据闭包、增量的 Card/Work/point 作用域仍严格检查。Reviewer 汇总失败的恢复接口仅提出设计，本轮不改变生产 Reviewer 或工作流行为。

## 1. 真实复现与来源

完整历史工作区：

`outputs/frontend-user-20260918/99703e948fce4f1eb12c37de318f764d/99703e948fce4f1eb12c37de318f764d`

包含 3 个查新点、4 张 Validator 接受的 Card、5 条 Researcher Evidence、3 份点级 Review、5 条 Reviewer 增量 Evidence、1 份 Reviewer stage 元数据及 8 次 Reader 调用记录。修前脚本只报告以下两条错误：

- `review references missing Evidence: rev_ev_3e77e610fafb464ad929b232`
- `review references missing Evidence: rev_ev_3c1baa094a1e8637ef533de0`

这两个 ID 实际存在于对应点的 `review_evidence`。前者的 `origin_card_id` 是 `card_59de824fb081565b0b00d1e6`，其 Work 是 `wrk_550019147260ce5861cd5a14`，且该 Card 的原始 Evidence 已绑定同一 Work。Review 的 `highly_relevant_works` 同时引用原始 Evidence 和此增量 Evidence。这里是诊断索引遗漏，并非实际引用缺失。

可移植回归 fixture 为 `tests/fixtures/reviewer/diagnostics_registered_evidence.json`。它提取该运行的 NP-1，保留原始点、两张 Card、两条 Researcher Evidence、一份 Review 和一条增量 Evidence；`source_workspace` 与 `source_files` 保存原文件路径和 SHA-256。生成修后报告时重新核对了这 4 个原文件 hash，均一致。Fixture 是原始结构抽取，不是重写模型输出。

## 2. 原因与最小修改

脚本原先仅从 `research-runs/**/attempt-*.json` 建立 Evidence 索引。生产 Reviewer 则先将 Reader 引用注册为 `ReviewEvidence`，再允许 RelevantWork 引用其 ID，并以 `origin_card_id` 将它与 Card 关联。诊断未适配这个已存在的契约，因此误报。

修改仅在诊断脚本中：

1. 每份 Review 单独建立增量索引。重复 ID、覆盖原始 Evidence ID、缺失 origin Card、跨 point，以及无法由 origin Card 的原始 Evidence 证明 Work 绑定的增量均报错，不进入有效索引。
2. RelevantWork 的引用从原始索引或当前 Review 的有效增量索引解析。Card/Evidence 关联仅增加该 Card 自己的合法增量 ID。
3. 原始 Card 的闭包检查仍只查 Researcher Evidence；新增 ReviewEvidence 不能用于填补原始 Card 缺失的 Evidence，也不能跨 Review 借用。
4. `counts.evidence` 计入有效原始证据与有效增量证据的总数；原有仅 Researcher Evidence 的工作区数值不变。

不改生产 Reviewer 的引用绑定、Reader 注册、quote 校验或汇总逻辑。诊断输出不包含原始 quote、exact_quote 或 Reader 正文。

本脚本的 `ok` 表示其实现的产物结构与引用闭包检查通过；它不等价于重新执行 Reader ledger、artifact hash、字符区间或引文语义核验，也不新增对 `feature_comparisons` 的完整审查。恢复接口不能仅凭本脚本 `ok` 授权复用证据。

## 3. 修前/修后对照及测试

| 检查 | 修前 | 修后 |
| --- | --- | --- |
| 真实完整运行 `ok` | false | true |
| 真实完整运行 errors | 2 条合法增量 ID 误报 | 0 |
| 原始 Card 未解析 Evidence | 0 | 0 |
| `counts.evidence` | 5（漏计增量） | 10（5 原始 + 5 增量） |
| 真实 NP-1 fixture | 失败：增量 ID missing | 通过 |
| 仅引用合法增量而不重复引用原始 Evidence | 失败：missing + Card link missing | 通过 |

先新增上述两个正向回归并在原实现运行，确认 **2 项失败**，结果保存在 [reviewer_diagnostics_before.log](reviewer_diagnostics_before.log)。随后实现最小修复。

回归命令：

```bash
/home/lya3106643285/miniconda3/envs/Novelty-web/bin/python -m pytest -q \
  tests/test_reviewer_diagnostics.py \
  tests/test_reviewer_evidence_repair.py \
  tests/test_novelty_point_reviewer.py
```

共 **57 项通过**。其中诊断测试共 14 项，新增 11 项覆盖真实增量、仅增量引用、缺失 origin、跨 point、错误 Work、重复 ID、遮蔽原始 ID、跨 Card、跨 Review、原始 Card 缺证及未知引用。相邻生产 Reviewer 测试继续覆盖严格 evidence 边界与汇总输入行为。`git diff --check` 通过。

产物：

- [修前完整运行报告](reviewer_diagnostics_before.json)
- [修后完整运行报告](reviewer_diagnostics_after.json)
- [定向/相邻回归输出](reviewer_diagnostics_tests.log)

## 4. 汇总失败后的局部事实恢复：只读方案

代码事实：`workflows/novelty.py::_review_evidence` 在单 Card 开始、完成或失败时原子写出 `novelty-reviews.json`，其中包含 `card_reviews` 和 `phase=card_review`；最终写入仍保留这些行。因此已确认的单卡结果通常仍存在于持久化文件中。`agents/evidence_reviewer.py::summarize_reviews` 在汇总失败且 fail_closed 时返回 `_insufficient_review`，其点级 `highly_relevant_works`、`review_evidence`、`feature_comparisons` 均为空。损失发生在最终点级结果的可见性与恢复入口，不应直接描述为所有局部事实已经从磁盘丢失。

现有 `phase=complete` 也不能独立表示汇总成功：失败回退最终仍会进入该阶段。未发现独立的 summary checkpoint 恢复入口。现有 `_compact_summary_rows` 已重验单卡引用并生成引用原文/展示 hash，`_verify_summary_payload` 校验发往模型的展示内容；它们可以成为恢复流程的复用边界。

建议增加独立、显式的 checkpoint 与恢复结果契约，而不把技术失败强行提升为点级语义裁定：

```python
# 接口草案，未实现
load_summary_checkpoint(workspace, checkpoint_id) -> ReviewSummaryCheckpoint
validate_summary_checkpoint(checkpoint, request, artifact_store) -> ValidatedSummaryInput
resume_summary(validated_input, *, attempt_id, summary_options) -> SummaryAttemptResult
```

`ReviewSummaryCheckpoint` 至少保存：schema/version、原始 run/checkpoint ID、paper/point/card ID、原始 request 的规范化 hash、逐 Card 的状态/结果 hash、引用 Evidence 与 artifact hash/namespace/read_id/区间、原始 Reader 注册核验记录、prompt/schema/config/model 标识、冻结日期及引用展示 payload hash。原始已验证单卡结果保存为独立快照，不随一次汇总重试覆盖。

`SummaryAttemptResult` 分开记录 `summary_pending/running/completed/failed`、技术原因、重试预算与模型身份、是否收到响应、是否通过 draft/引用验证、正式点级 Review（仅成功时存在）。可将已验证 `card_reviews` 暴露为 `partial_card_results`，但保持每张 Card 的 Work/point/feature 边界、支持状态、证据 ID 和原文引用，不在技术失败时合并为新的点级 verdict，也不将局部缺证扩大为整点“没有相关工作”。`partial_card_results` 是保留原核验状态的单卡结果，而非声称其中每一条比较都已获得正向支持。

恢复前的约束：

1. 重新验证 checkpoint schema 和输入 hash，确认 Card/Work/point、源版本及 artifact hash 与当前输入一致。以 Reader 注册记录及原 Artifact 的 exact slice 校验增量证据；只有摘要脚本通过不能替代这些核验。
2. 每份 completed 单卡 Review 重新执行现有单卡引用校验；technical_error/budget_exhausted 行继续保留为诊断状态，不能转为可用语义证据。失配或缺少核验来源时标记 stale/unverifiable，保留旧快照，重新执行受影响单卡或明确停止。
3. 对有效快照，调用现有 compact/project/payload 校验和工具禁用的 summary 路径，不重做数据库检索或 Reader 读取。沿用原冻结日期；若显式更改 summary 模型/提示词/预算，创建新的 attempt 并记录新旧配置与 payload hash。
4. 成功后原子写入正式点级结果；失败只追加失败 attempt，并继续暴露原单卡快照。并发 worker 不能用局部视图覆盖共享 checkpoint；恢复需以 checkpoint hash 或版本进行更新条件检查。

建议未来验收：汇总超时/传输失败/JSON 格式错误后局部已核验引用完全保留；只重试汇总、不再次读源；跨 Work、改动 artifact hash、错误区间、陈旧 request、缺 Reader 来源均拒绝恢复；模型 draft 越界仍 fail_closed；失败卡与确认局部事实同时存在时不改变各自语义；重试并发不会覆盖较新的结果。

上述接口设计仅为下一步方案，本轮未增加恢复代码或隐式重试。
