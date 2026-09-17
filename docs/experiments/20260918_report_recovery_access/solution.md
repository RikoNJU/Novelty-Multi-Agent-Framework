# 实现

`prepare_report_resource.py` 按冻结 manifest 核对来源阶段输入、原失败 Runtime manifest、真实模型响应和最终报告的 SHA-256，建立独立受控包。包内含可迁移的审查输入投影、原失败身份、真实响应和原样 Markdown；生产 `validate_report_integrity()` 与 `assemble_report_from_draft()` 重新检查全点、Reviewer 字段、卡片引用和响应到最终报告的关系。移动整个包后仍可复验。

`register_report_resource.py` 的 dry-run 不写索引；正式登记只把报告 Markdown、结构化 JSON、脱敏来源说明和元数据复制到 `NOVELTY_REPORT_RESOURCE_ROOT`。资源 ID 由来源与恢复身份确定，同身份同内容幂等，不同内容拒绝覆盖。索引和资源文件持久化，GET 每次核对登记哈希；仅允许固定的三个文件名，路由实际暴露 Markdown 与 provenance。没有模型或工作流服务时仍能读取。

React 增加 `report_resource_id` 模式，独立读取资源元数据和 Markdown，显示原失败状态、恢复身份、各点 Reviewer 状态与未完成原因。现有 Markdown 阅读器处理预览与同字节下载。该模式没有创建任务、轮询进度或重试业务工作流。

原 Markdown 字节不改。下载文件名标为 `recovery-report-<resource_id>.md`，同时提供 `provenance.json` 下载，用于离开页面后确认来源和恢复范围。
