# 回读、JSON恢复、查询限制与执行审计修复

## 已完成

1. ReviewerReaderTool 从输入卡片引用的可信 Evidence 解析 namespace/work_id，不再固定 research_reference。未标记的旧证据保持 research_reference 兼容默认；同一个 artifact_id 出现多个可达地址时明确拒绝。回读返回的 namespace、work_id、artifact_id 必须与请求一致。
2. Researcher 的非空cards与no_evidence_reason冲突在本地规范化：保留cards，将原因移到warnings，再经过完整schema与Builder验证。其他JSON/schema错误最多进行一次无工具格式恢复；失败时保留读取结果并返回partial。既有引文纠正仍独立至多一次。与预算整理叠加时，Researcher最多额外三次模型调用，不会无限恢复。
3. Reviewer 的JSON/schema解析失败最多进行一次无工具格式恢复，之后仍验证查新点、work/card/evidence引用；非法引用或再次失败继续降级insufficient_evidence。原判定和引用校验没有放宽。格式修复指令禁止新增事实、引文或增强结论。
4. WebSearch 的Baidu参数schema、工具描述和skill/prompt明确72单位限制：ASCII（含空格）计1，非ASCII计2，建议控制在60以内。query只传检索词，不传思考、解释或整个任务。合格示例：`图摘要 分布式GNN`；`graph summarization distributed GNN`。超限查询不发HTTP，返回INVALID_QUERY、实际单位数、上限及缩短建议，供下一次受预算约束的模型调用纠正；不静默截断。
5. 独立保存SearchExecution审计，失败、成功零命中和有命中分别保留。可信research_bundles仍不接收失败响应。持久化记录query/status/error/result_marker，Renderer显示“零命中/有命中/执行失败/部分成功”等。相同查询的不同执行时间保留为独立记录；同一次执行的重复嵌套载荷去重。成功空结果传给模型时带zero_hits标记。

## “失败检索”到底是什么

分析来源：../20260915_212448。

此前报告NP-2检索式显示“无”，实际有4次执行：Springer HTTP404两次、arXiv读取超时一次、arXiv熔断一次。它们不是超长查询错误。被过滤的是succeeded=False观测中的SearchExecution，而不是没有生成查询。

该轮全部21次逻辑数据库执行中，Springer成功3次、HTTP404七次，arXiv失败11次（包括服务错误、超时与熔断）。物理HTTP请求数与逻辑执行数不同，不混为一谈。

超长的是另外3次WebSearch参数校验失败，发生在发出HTTP之前。历史effective_config确有Researcher和SearchPlanner的enable_thinking=false；factory会将非None的enable_thinking放入ModelCallOptions.extra_body，客户端再序列化。关闭thinking并不限制query字符串长度，因此此次使用显式prompt示例与工具校验共同处理。

如果检索成功但没有命中，保留检索式与空results、succeeded状态，并标记zero_hits，不升级成失败。对于只有HTTP404而没有响应体的历史Springer记录，不能直接推定它等于无命中；此次保留失败标记，没有无条件把404改成空结果。

arXiv429策略按用户要求未调整，也没有发起新的arXiv探测。

## 验证

- 完整默认测试：736项，730 passed、6 skipped、0 failed/errors。
- 最后完善重复执行审计并补充回归：17项定向测试全部通过。
- 原实验真实文件本地回读：6/6成功，其中subject_reference五个、research_reference一个；见archived_read_replay.json及replay_reads.py。这一验证调用实际ReviewerReaderTool和ReferenceArtifactReaderTool，没有网络请求。
- 原实验工具观测回放：21条数据库执行全部保留，NP-1六条、NP-2四条、NP-3十一条。NP-2四条均显示“执行失败”，见query-audit-preview.md、audit_replay_summary.json及audit-replay/。未覆盖原实验文件。
- 回归覆盖地址歧义、错误返回namespace、互斥字段保留有效卡片、恢复失败保留读取、一次格式恢复、恢复后非法引用拒绝、查询超限不发送HTTP、零命中与失败标记、重复查询执行保留。
- git diff --check通过。

未执行新的在线完整流程，真实模型的格式恢复成功率和新prompt遵循率尚未测量；本次验证证明确定性路径和有界恢复机制。恢复模型仍可能失败，失败时继续保持partial/insufficient_evidence而非编造结果。所有改动尚未提交。
