# 只读归档与排错入口

本次唯一真实业务 run `feabea311a0d4014bd4c9015491caf1b` **失败于报告合成**，没有正式报告、预览或下载。它不能用于“查新完成”的现场演示。可用于展示上传、进度、刷新保持同一任务，以及真实失败态；截图在 `../run/final-or-stopped.png`，浏览器轨迹在 `../run/live-browser-observation.json`。

完整本地输出目录：`outputs/e2e-acceptance-20260918/feabea311a0d4014bd4c9015491caf1b/`。其中 `runtime-archive/` 保存模型输入与响应、工具调用、阶段输入输出和异常；`budget-ledger.json` 是物理请求预留账本；同名子目录保存 PDF 解析结果、检索计划、候选审计、卡片和 Reviewer 中间结果。关键路径与哈希见 `../run/run-index.json`，逐点摘要见 `../run/point-ledger.json`，异常见 `../run/failure-diagnosis.json`。本目录是只读证据入口，不应修改历史对象或将其重新投影成新 run。

预检期的 `preflight/browser/historical-replay.png` 仅显示**历史运行回放**，源和下载 SHA-256 均为 `fabcca133bfc09187cd55caaecb92508881004a2bbff77c07bfb4f817cbd0177`，与本次失败 run 无关。既有历史报告不得冒充本次产物。当前浏览器服务已停，`/api/novelty` 任务状态存于内存，重启后不可凭同一任务 ID 获取页面状态；以本地输出和索引复核。

为后续离线排错另存只读压缩包：`outputs/e2e-acceptance-20260918/feabea311a0d4014bd4c9015491caf1b-readonly.tar.gz`，SHA-256 `d3a1629e734baf523bcdda5811ab2d3375d2d53f337fbc3e37a5203ad5fb2523`。压缩包含输入 PDF、原始模型和检索轨迹；按已批准的材料范围保管，勿公开发布。归档索引已提交，压缩包及完整 Runtime 保留在本地输出目录。
