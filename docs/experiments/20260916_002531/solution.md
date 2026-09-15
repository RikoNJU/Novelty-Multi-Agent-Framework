# 单卡并行评审与单次汇总

## 实现

正式 Reviewer 先按 Card 并行核验，再按查新点汇总。每张 Card 使用现有
`NoveltyPointReview` 格式保存文献级中间分析，没有新增业务结果类。
单卡 verdict 仅是相对当前文献的中间判断，不直接用于报告。

`MF2033k6lC/novelty-reviews.json` 增加 `phase` 和 `card_reviews`：

```json
{
  "paper_id": "MF2033k6lC",
  "phase": "card_review",
  "reviews": [],
  "card_reviews": [
    {
      "index": 1,
      "novelty_point_id": "NP-1",
      "card_id": "示例ID",
      "status": "pending",
      "review": null
    }
  ]
}
```

每张卡完成后更新整份中间快照，采用原子文件替换。索引按输入 Card 顺序分配，
不受并发结束顺序影响。最终 `phase=complete`，`reviews` 仍然只包含查新点级
最终裁定；保留 `card_reviews` 便于核对，下一轮重新初始化。

每个有证据且有可用单卡结果的查新点额外调用一次汇总模型，不调用工具、不额外
做格式修复。汇总只收到查新点、单卡索引结果以及已核验的关键引文，明确区分“单篇
公开完整组合”与“多篇分别公开部分特征”。无卡、全卡执行异常、汇总格式错误或
超时均返回证据不足，不以获取失败证明新颖性。

原始 Card/Evidence 继续保留在本地，供结果引用校验，不整体发送给汇总模型。
每卡关键引文从单卡 `highly_relevant_works.evidence_ids` 中选择，最多 2 段，
每段最多 600 字符；使用原文前缀并标记 `quote_truncated`，额外引文数量记入
`omitted_quote_count`。保留所有单卡已核验的引用 ID，未展示全文不等同于没有该特征。
汇总不能引用未经过单卡核验的 Evidence；本地校验同时检查 Work/Card/Evidence
关联关系。中间结果格式和最终 `reviews` 格式不变。

单卡与汇总共用一个 semaphore，复用 `max_concurrency`（当前 4）。外部旧式
Reviewer 仍可使用旧接口。不同点最终结果按输入顺序保存，单点异常不拖累其他点。

## 耗时控制

- 单卡最多 6 轮模型交互、4 次 Reader 调用，若已有配置更小则遵循较小值。
- `reviewer.card_timeout_seconds` 默认 240 秒。
- `reviewer.summary_timeout_seconds` 默认 180 秒。
- 超时中止该阶段的等待并返回不足；底层同步 HTTP 线程可能仍在等网络超时，
  不代表外部请求已被取消或不再计费。
- 单卡提示优先核验输入 Evidence，只有具体疑问才回读，不要求全部重复读取。
- Researcher 的同一次 Harness 调用仅复用相同数据库参数的完整成功结果（包括零命中）。
  失败、部分成功、需要人工处理和无执行结果不缓存；临时失败仍可进入 provider 的重试与退避。
  复用不会发起新的数据库请求，模型上下文标记 `reused_result=true`，执行审计仍
  引用原 SearchExecution；不会伪造新检索。新任务/新轮次缓存独立，可以重试。
- 模型重复提出数据库调用仍消耗交互预算，防止无限空转。此改动减少重复 HTTP
  等待，不保证模型往返次数减少，也没有扩大检索式。

## 本地验证

上一阶段 92 项测试全部通过，详见 `tests.xml`。覆盖单卡并发、索引落盘、最终
一次汇总、同点完整证据输入、部分单卡失败、超时、错误 JSON、引用隔离、旧接口、
当时的数据库结果复用、跨任务重新执行、配置、持久化及报告绑定。
后续已修正失败缓存策略并增加批量 Reader，验证记录见相应后续实验目录。
此前另有一批包含工作流和运行日志的 130 项测试通过。

收紧汇总输入后，29 项 Reviewer、工作流 Reviewer 和报告绑定测试全部通过。
新增测试检查完整 Card/任务/interpretation/provenance 不进入模型消息、引文数量
与长度上限、省略标记，以及拒绝引用虽保存在本地但未经单卡核验的证据。

## 真实对比实验状态

`run.py` 准备使用 20260915_224229 的冻结证据，对比按点并行和单卡并行后汇总，
各自使用独立输出目录，不重新检索、不调用 MinerU。

真实实验尚未启动：自动审批拒绝调用，理由是向配置的外部模型目的地发送论文
Evidence 需要明确授权。没有模型调用、真实耗时或 token 对比数据，不能据本地
测试声称获得了某个加速比例。配置中的默认目的地为 SiliconFlow，
`https://api.siliconflow.cn/v1`，模型为 `deepseek-ai/DeepSeek-V4-Flash`。
