# Coordinator 报告节点修补实验报告

## 结论

实现、离线回放和两份冻结来源的**真实模型报告节点**均通过结构验收。L1、L2 各收到一次完整响应，`finish_reason=stop`，全点覆盖、Reviewer 权威字段逐项保真，完整性校验、持久化和 Renderer 均成功。原两份端到端业务运行仍为 `FAILED`；本实验没有重新解析、检索或调用 Reviewer。最终报告是用已保存真实响应进行零费用确定性重组的产物，身份分别为 `L1-captured-reassembly` 和 `L2-captured-reassembly`。

## 原因与输出边界

两份历史失败运行的四个 Coordinator 原始响应均在 JSON 字符串内结束，不能解析；旧请求输出上限为 4096。原 Runtime 没有保存 `finish_reason`，因此旧调用是否由提供商明确按长度结束仍未知。响应尾部、错误位置、usage 和哈希见 `analysis/original-response-index.json`。完整报告字段重复生成增加输出负担是设计推断，不将 usage 差值作为跨模型通用终止规则。

新生产请求使用 `ReportNarrativeDraft` schema，只让模型生成每点短综述、授权卡片 ID 分组和有限表达性局限。正常、fallback 与纠错路径均不要求重新输出 Reviewer 裁定或原文对象。请求捕获见 `analysis/output-shape-comparison.json`：L1 请求 226,492 字节，L2 为 190,368 字节，输出上限仍为 4096，输入语义没有在本轮压缩。

## 组装与真实复验

组装器先检查全点和卡片作用域，再把原 Reviewer 八类权威字段注入最终对象。1／3／8 点、重排、长摘录、不同状态及非法引用的测试通过。冻结源的真实节点结果和原始响应哈希见 `analysis/live-node-results.json`；L1 的 NP-1 仍为 `insufficient_evidence / technical_error`。两份最终报告的逐字段比较全部为真，见 `analysis/authority-binding-checks.json`。

第一次 live 派发在网络连接阶段遭沙箱拒绝，未收到响应，账本保留 0.35817 元预留且实际计费未知。经授权在网络环境续跑后，L1、L2 各一次请求成功，响应耗时分别为 73.726 秒和 15.475 秒。旧失败、首次沙箱失败、真实响应和最终重组均保留独立目录，互不覆盖。

首次真实报告的模型自由局限包含若干未经本节点输入证实的检索覆盖判断。为防止这类文字成为最终事实，组装器改为仅发布由 Review 状态、补查请求、拒绝证据记录和覆盖未知推导的局限。使用**同一保存的真实响应**重新执行生产合成、完整性校验、持久化和 Renderer，没有额外模型调用。原模型自由局限保留在受控 Runtime 中供审计；最终报告不包含它们。模型短综述仍需独立语义复核，字段保真不能证明综述内容正确。

## 费用与调用范围

同一账本记录 3 次物理请求，其中第一次网络失败、两次收到响应；上限为 4 次、预留 4 元。总预留 1.020324 元。两次已收到响应的 usage 费率估算合计 0.183507 元；第一笔实际计费未知，供应商最终账单未知，不能把估算当实付。无在途请求。详情见 `analysis/cost-ledger.json`。所有上游模型和检索请求数为 0。

## 页面

Playwright Chromium 使用测试拦截把本机最终 Markdown 送入现有报告页面，显示“基于历史失败 run 的真实模型响应零调用重组；非完整查新成功”。预览、刷新与下载通过；下载和源文件 SHA-256 一致，业务 POST 为 0。页面证据见 `display/live-source-and-download-hashes.json`、`display/live-browser-observation.json`。这不是生产恢复任务 API 的验收，也没有把原业务 run 改为成功。

## 结论边界

两份来源是已见过的回归输入，不是泛化评估集。Reviewer 语义风险、Springer 404、前端阶段详情接口和完整工作流稳定性未由本次报告节点恢复解决。详见 `analysis/known-issues.md`。
