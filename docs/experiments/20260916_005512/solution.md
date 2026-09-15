# 数据库成功结果复用与批量 Reader 验证

结束时间：2026-09-16 00:55:12（Asia/Shanghai）。

## 结论

本地确定性测试共 148 项通过，失败 0。此次没有运行真实模型或数据库请求，
因此没有端到端耗时改善的实测结论。arXiv 429 的 provider 策略未修改。

## 数据库复用边界

- Harness 原有单工具调用、检索后强制 Reader、调用次数和字符预算仍生效。
  这些约束本身不阻止 `Database → Reader → 同一个 Database`。
- 当前检索工具只有 `source_id` 参数，同一任务的 SearchPlan 固定；完整成功后
  原样调用同一来源会复用原结果，包括成功零命中，并标注 `reused_result=true`。
- 失败、部分成功、需要人工处理和无执行结果不缓存。429、超时等临时失败
  仍可重试，沿用现有 provider 的重试、退避和工具预算。此次没有新增自动换库调度。
- 缓存仅属于一次 Harness 调用，不跨任务或轮次；复用仍消耗工具调用预算。
  检索执行记录使用原 ID，不伪造一次新检索。

## 批量 Reader

单个 `reader` 工具调用支持最多四段独立读取，同时兼容旧单段参数：

```json
{
  "reads": [
    {"artifact_id": "artifact_a", "char_start": 0, "max_chars": 2000},
    {"artifact_id": "artifact_b", "char_start": 100, "max_chars": 3000}
  ]
}
```

- 批量内按顺序执行本地读取，减少模型决策往返；不是任意多工具并行。
- 每段沿用配置的默认值和上限。执行前按各段 `max_chars` 之和检查剩余预算，
  执行后按成功片段实际字符数累计。整批计一次工具调用。
- 返回 `read_results` 与 `read_errors`；错误带原请求索引（从 0 开始）和 Artifact ID。
  单段失败不丢弃其他成功片段；每段的 read_id、work_id、namespace、字符范围保持独立。
- Evidence 构建器接收经逐段校验的可信读取结果，跨文献、跨参考库仍分别生成卡。
- 强制 Reader 规则检查批量请求是否包含要求的 Artifact；只有读到要求的文献
  才视为成功满足约束。失败仅释放实际尝试的 Artifact，保留其他候选的约束。
- Reviewer 逐段执行其原有 Evidence 范围权限检查，批量请求不能扩大可读范围。

## 验证

`tests.xml`：110 项通过，覆盖 Harness、Reader 工具集成、跨库来源绑定、
Evidence 构建、Reviewer、读取失败诊断、工作流 Reviewer 和报告绑定。

`regression.xml`：38 项通过，覆盖 TaskResearcherWorkflow、运行日志、数据库工具
及 Harness 集成、Researcher 提示约束和底层 Reader。

关键新增用例包括完整成功与部分成功的缓存区分、失败后成功零命中的复用、
跨任务重新执行、批量部分失败、两篇文献分别成卡、累计预算、批量大小/参数校验、
强制读取规则及 Reviewer 逐段权限检查。

扩展回归首次在沙箱内停滞，已中止；获自动审批后运行同一组本地 mock 测试通过。
`git diff --check` 通过。修改保留在工作区，未提交。
