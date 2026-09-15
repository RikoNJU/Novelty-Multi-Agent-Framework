# Renderer 文献附件与 arXiv 单篇独立查询

结束时间：2026-09-15T19:36:29+08:00。

## Renderer 修改

“附件与参考信息”新增“检索到的文献”，从 `references/list.json` 的已发现来源以及原始证据卡的文献来源汇总，优先全文链接、其次落地页；没有manifest的旧工作区仍可渲染。链接去重，arXiv abs链接规范化为pdf链接，不输出本地文件链接。候选无需通过最终证据审核，也可列入文献清单；原论文参考文献列表没有被直接整份抄入。

格式：

AliGraph: A Comprehensive Graph Neural Network Platform：[https://arxiv.org/pdf/1902.08730](https://arxiv.org/pdf/1902.08730)

验证：`python -m pytest tests/test_renderer.py -q`，10项通过，`git diff --check`通过。见 [renderer_validation.json](renderer_validation.json) 和使用第二组实验数据生成的 [报告预览](renderer-report-preview.md)，其中含上述AliGraph精确格式。历史实验报告没有覆盖。代码变更快照见renderer.patch。

## arXiv 独立实验

只查询同一篇AliGraph（1902.08730），不启动模型/工作流/批处理，不重试、不跟随重定向；每个网络条件仅发起一次请求，两次请求顺序执行。

`GET https://export.arxiv.org/api/query?id_list=1902.08730&max_results=1`

| 条件 | 请求数 | 结果 | 耗时 |
|---|---:|---|---:|
| 使用现有环境代理 | 1 | ReadTimeout，无HTTP状态 | 30.58秒 |
| trust_env=False，不使用环境代理 | 1 | ReadTimeout，无HTTP状态 | 30.54秒 |

原始结果：[result.json](result.json)、[no_env_proxy_result.json](no_env_proxy_result.json)。复现脚本：[probe.py](probe.py)，默认使用环境代理，`--no-env-proxy`禁用环境代理。

两个条件DNS均为198.18.0.34；本机路由为 `198.18.0.34 via 198.18.0.2 dev eth3 src 198.18.0.1`。因此禁用HTTP代理并未建立可确认的独立公网直连条件；不能凭这个对照断言代理与问题无关。当前环境代理指向127.0.0.1，未记录代理凭据。

## 429原因：已证实与仍未知

**本次没有复现429，不能确定之前429的具体触发规则。** 两个请求均在取得完整HTTP响应前读取超时；超时不能算429，也不能算成功。

历史三组实验与batch探测已保存真实429，正文为`Rate exceeded.`，响应头包含Google Frontend、Varnish等服务链信息；4秒调度间隔无违规，metadata合并也真实发生。这证明访问的服务链返回了限流，且并非只有多任务批处理时才可能出错；它不披露限流键、阈值、账户/IP桶或封禁期限。

候选原因包括当前出口IP上的共享/历史流量限制、服务端更长周期限额，以及网络/代理链问题。**这些均是待验证假设，不是本次已确认结论。** 本次尤其暴露了当前网络路径读取不稳定，但不能用超时解释全部历史429。

要进一步锁定原因，需要来自已确认不同公网出口的同一单请求对照，或出口代理日志与arXiv服务端限流日志/反馈。本机当前路由不提供这种独立对照证据。建议先确认代理出口及连接日志，恢复稳定响应后保留时间、状态、Retry-After与请求ID做低频诊断；不自动反复重试来制造更多限流。
