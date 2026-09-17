# 修补方案

Coordinator 现在只请求 `ReportNarrativeDraft`：每点短综述、授权卡片 ID 分组及有限表达性局限。Draft schema 禁止额外字段；模型不能输出 `paper_id`、裁定、置信度、ReviewEvidence 或原文摘录。正常提示、无 PromptLibrary 的 fallback 和一次结构纠错都采用此契约。

`assemble_report_from_draft()` 按源查新点顺序检查全点覆盖和卡片作用域，在构造 `NoveltyReport` 之前逐项注入对应 Reviewer 的状态、裁定、理由、置信度、相关文献、核验证据、特征比较和未完成原因。旧绑定入口复用同一映射，重复绑定保持幂等。证据不足或技术错误仍作为未完成点进入报告，不能由模型综述提升成完成裁定。

报告专用解析只接受完整 JSON 或完整代码围栏。明确 `finish_reason=length` 和疑似尾部截断直接停止；无响应、传输超时、预算拒绝与完整但无效的 Draft 分开处理。完整的结构或组装错误最多纠正一次。规划与补查共用的旧 `_complete_json()` 未改动。

节点回放脚本验证原输入哈希及接受卡片集合，复用生产 Workflow 四个报告节点；完整性失败时不持久化报告。每个恢复结果有独立输出根目录和来源身份；脚本拒绝重置已经存在的 live 预算账本。Renderer 对未记录材料和检索计划采用有限陈述。
