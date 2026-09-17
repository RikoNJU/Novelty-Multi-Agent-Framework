# E2E-ACCEPT-20260918：单次真实联调验收

## 结论

冻结版本 `bd19a72f386f4cfaec52c096ccec9f9c0f985a6f` 的零业务调用预检通过有限范围；经用户批准后，模式 A 从真实浏览器上传 `examples/MG19333vrw.pdf` **一次**，创建业务 run `feabea311a0d4014bd4c9015491caf1b`。PDF 解析、检索、证据卡和三个查新点的 Reviewer 中间结果均落盘。报告合成阶段因 Coordinator 连续两次输出不完整 JSON 而失败；正式报告、预览和下载均未生成。本次真实端到端验收**未通过**，不能作为演示候选或可信查新结论。不新建第二个 run。

| 验收层 | 本次结果 | 实际边界 |
|---|---|---|
| 预检 | `passed_limited_scope` | 前端组件 8/8、浏览器 17/17、API/预算 9/9、Runtime/usage/Reviewer 回归 30/30，构建通过；使用本地缓存浏览器和依赖。 |
| 实际执行 | `failed_at_report_synthesis` | 浏览器 1 次 POST、1 个 run ID、1 个输出根；本地 MinerU 解析完成；后端终态 `failed`。 |
| 检索与证据 | `partial_intermediate_only` | 计划/执行查询、24 个 Work/SourceRecord/Artifact、3 张接受卡和 3 个 Reviewer 中间结果可追溯；没有最终报告引用链。 |
| 页面展示 | `partial` | 页面显示原 run 的进度及失败，刷新没有新建任务；因无报告，正式预览/下载无法验收。阶段业务详情接口仍缺。 |
| 语义质量 | `not_assessed` | 3 个自动 Reviewer 裁定只是中间产物，未逐条完成原文支持审计，也没有正式报告。 |
| 重复稳定性 | `not_established` | 本轮仅一次真实运行，且失败。 |

## 唯一调用及故障

浏览器于 `2026-09-17T20:18:07Z` 向 `/api/novelty/runs/files` 发出唯一业务 POST，刷新后仍轮询同一 ID。终态于 `20:22:00Z` 返回 `failed`；页面截图显示“本次查新未能完成”，没有把已生成的 Reviewer 中间对象当作正式结果。浏览器记录和截图见 [live-browser-observation.json](run/live-browser-observation.json)、[final-or-stopped.png](run/final-or-stopped.png)。浏览器控制台有两条资源加载失败记录，未见页面脚本异常；其来源与业务失败关系未确认。

Runtime 的实际失败节点为 `synthesize_report`，`render_report` 标为 `NOT_RUN`。页面聚合进度此时显示 `render_report`，只能理解为用户界面的报告阶段，不代表渲染节点执行过。Coordinator 的第 57、58 次物理模型请求均收到响应，但内容在 JSON 字符串中途终止；两次请求各配置 `max_tokens=4096`，按返回 usage 扣除 reasoning tokens 后各为 4096 个内容 token。第二次重试后 JSON 解析报错并终止工作流。原始请求、响应及异常留在 Runtime archive；概要哈希和定位见 [failure-diagnosis.json](run/failure-diagnosis.json)。这是本次轨迹支持的直接故障原因，不在冻结版本中改 Prompt、模型参数或报告结果，也不做第二次付费复验。

## 预算与调用范围

用户批准一次模式 A，模型预留上限 15 元、最多 80 次物理模型请求、总截止 30 分钟，并明确允许必要的 PDF 衍生内容发送至 SiliconFlow、检索查询发送至已启用的 arXiv/Springer。首次自动审批因外部数据范围不明确而拦截，尚未提交；得到明确授权后才启动上述唯一 POST。保留 [dispatch-denial.json](run/dispatch-denial.json) 作为前置历史事件。

本次账本记录 58 次物理模型请求，58 次均收到响应；保守预留 **4.752081 元**，返回 usage 按本地费率估算 **0.8509833 元**。这些不是服务商实际账单，实际账单未查证。预算没有到限，因此“到限后不再派发”只有本地替身测试支持。解析走配置中的本地 MinerU 子进程，未观察到另一个付费解析调用；外部解析费用仍记为未知而非零。完整预留账本位于输出根，摘要见 [budget-ledger.json](run/budget-ledger.json)。服务在终态记录后停止。

## 全点中间结果与证据范围

本次共提取 3 个查新点，检索计划记录 44 条逐点查询条目：14 条 `succeeded`、5 条 `failed`、25 条 `not_run`。5 条失败均为 Springer HTTP 404，不能算成零命中；`not_run` 也没有算成失败或零命中。三点分别有 4、23、17 条查询条目。参考文献仓库共有 24 个 Work、24 个 SourceRecord、24 个 Artifact；3 张原始卡均进入接受卡，Reviewer 为三点各输出一份中间审查。逐点数字、状态和原始路径见 [point-ledger.json](run/point-ledger.json)。各点共享 `T-1`，候选台账中的 8 个条目不可按三点相加为独立文献数。

原始 Runtime 包含 42 次工具调用记录，其中 Reader 19、reference search 10、database search 13；58 次模型调用及阶段输入输出可回读。仍未逐条完成 Reader 正文片段、Reviewer 实际输入 quote 与每个结论引用的人工并排审计。没有最终报告，故不能证明中间 Reviewer 的 `novel`/`partially_novel` 裁定已被正确写入报告，也不能对其语义正确性给出通过结论。先前 Reviewer 实验中的否定/冲突引文支持疑问仍然存在。

## 预检和集成修补

冻结前完成同意图上传去重、额外 multipart 字段拒绝、前端未知提交状态防重发、语义证据不足与技术未完成的显示区分、补查回环进度，以及可选的逐 run 派发前模型预算预留。实际 React 页面走 `/api/novelty/runs/files`，不是仓库内另一套 `/api/runs`；[interface-map.md](preflight/interface-map.md) 记录路径、30 MiB 限制和重启边界。历史报告只读浏览器回放的源文件和下载哈希一致，但它不是本次新结果。前端没有当前 run 的阶段业务详情接口，E07 仍未通过。

代码、前端构建、配置、Prompt、输入和缓存初态见 [trial-manifest.json](trial-manifest.json)；逐项 E01–E20 状态见 [acceptance-status.json](acceptance-status.json)。完整失败 run 的本地只读输出和 Runtime 位置及关键文件哈希见 [run-index.json](run/run-index.json)，展示/排错入口见 [demo/README.md](demo/README.md)。
