# 前端自主提交查新：单次失败归档（2026-09-18）

## 结果

用户在 `http://127.0.0.1:5173/` 自行提交 PDF，后端 stdout 观察到一次 `POST /api/novelty/runs/files`，创建 run `99703e948fce4f1eb12c37de318f764d`。本轮没有由执行者代点提交，也没有第二个业务 run。Runtime 从 `2026-09-17T20:55:26Z` 运行到 `21:00:42Z`，历时约 5 分 16 秒，终态 `FAILED`。失败发生在 `synthesize_report`，正式报告没有生成；`persist_report` 和 `render_report` 均标为 `NOT_RUN`。前端在用户反馈中显示运行失败；后端 30 分钟服务截止后已关闭，其内存任务状态现不可再查询。

实际上传文件大小 2,046,268 字节、SHA-256 `1fa48a8cb5d121220ba897a051b1468c2f0cefa211a0f5311c1d74c47aed8c79`，解析题名为《面向大规模动态图的图神经网络优化机制研究》。它与上一轮归档的 `MG19333vrw.pdf` 哈希不同。本轮仍使用未修改的代码提交 `a48fe7c`，Coordinator 配置的 `max_tokens` 保持 4096；用户要求只打开预算，因此未加入当时提出、随后撤回的输出上限改动。

## 直接失败原因

Coordinator 的第 77 和 78 次物理模型请求都收到响应，但回复各自在 JSON 字符串中途终止。两次请求的 `max_tokens` 均为 4096；返回 usage 扣除 reasoning tokens 后的内容 token 均恰好为 4096。两次解析均报 `Unterminated string`，生产内置的两次尝试耗尽，最终抛出“Coordinator 未生成合法 NoveltyReport：返回内容不是合法 JSON”。[failure-diagnosis.json](failure-diagnosis.json)保存请求编号、usage、响应哈希和解析错误；完整请求和响应保留在本地 Runtime 包。

这与上一轮**另一份 PDF**的报告合成失败机制相同，支持“当前输出上限不足”这一定位；两次输入不同，不能把它们当作同一样例的重复稳定性试验。即使中间 Reviewer 已给出裁定，也不得从其对象拼成一份冒充本轮正式输出的报告。

## 预算和中间结果

本轮使用经用户指定的单次测试预算：每 run 模型预留最多 15 元、最多 80 次物理请求；后端服务有 30 分钟截止。账本实际记录 **78 次**物理模型请求，均收到响应，保守预留 **6.246471 元**，按返回 usage 的本地费率估算 **1.1339793 元**。这两个数字都不是服务商实际账单；账单未核对。请求数已接近 80 次上限，不能据此保证同预算下又一次完整运行可容纳必要调用。解析使用本地 MinerU 路径；外部解析收费未观察到，也未独立核账。[budget-summary.json](budget-summary.json)索引原始逐次账本。

解析提取了 3 个查新点。逐点检索计划共留有 **68** 条执行记录：14 条成功、9 条失败、45 条未执行；9 条失败均为 Springer Nature API HTTP 404，不应标成零命中。参考文献库登记 15 个 Work、15 个 SourceRecord、16 个 Artifact。原始证据卡 4 张，接受卡 4 张。Reviewer 的中间结果中，NP-1 为 `insufficient_evidence` 且原因 `technical_error`，属于核验未完成；NP-2 和 NP-3 有 `reviewed` 中间裁定。没有正式报告、最终引用及浏览器预览/下载，因此语义支持与展示一致性均未通过本次验收。[point-ledger.json](point-ledger.json)保留各点的查询、候选、卡片和审查口径；多个点共享任务 `T-1`，逐点候选数不可直接相加为独立文献数。

## 归档与后续处理边界

完整原始输出在 `outputs/frontend-user-20260918/99703e948fce4f1eb12c37de318f764d/`，只读压缩包及 SHA-256 见 [artifact-index.json](artifact-index.json)。压缩包包含用户上传 PDF、模型实际输入/响应、检索与 Reader 轨迹，保存在本机输出目录，不随 Git 提交。Git 中提交的是脱敏元数据、逐点计数、失败诊断和关键文件哈希。由于未捕获浏览器 HAR，单次 POST 的来源是后端 stdout，页面状态由用户反馈和 Runtime 终态共同支持。

需要单独修补并验证 Coordinator 的报告输出边界，且复核 Springer 404 的接口/来源配置。任何后续付费运行都应有独立预算和版本冻结；本轮不通过追加运行或替换输入来改写失败事实。
