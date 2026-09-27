# arXiv HTTP 406：等价 URL、缓存路径与标识解析续查

2026-09-28，生产代码基线 `a97a587`。延续 [上一轮因果调查](../20260928_tool_failure_causality/README.md)。本次 **没有修改生产代码，没有模型调用**。

**新结论：已经稳定复现语义等价 URL 在同一 TCP 连接上分别返回 200 和 406，生产调度器生成的 URL 正是失败形式。故障已缩小到 HTTP 请求形式及响应路径的差异；最终是边缘过滤、缓存/回源处理还是源站规则，仍缺服务端证据。** 另独立发现旧式 arXiv ID 被本地解析器截断的确定性缺陷。

## 1. 官方依据与实验设计

本次读取官方 [API 手册](https://info.arxiv.org/help/api/user-manual.html)、[API 使用条款](https://info.arxiv.org/help/api/tou.html) 和 [状态页](https://status.arxiv.org/)。手册给出了 `all:electron` 示例；说明省略参数有默认值、响应中的查询会正规化、通常的参数错误由 Atom 错误条目解释。条款要求单连接且请求间隔不小于 3 秒。本次直接探针按 4 秒间隔串行调度（记录中的实际请求间隔均大于 3 秒），禁止自动重试与重定向。

状态页采集时标记主站、搜索和 export 为 Up，见 `official_status.body`。它没有逐请求/API路径的诊断粒度，不能据此断言本项目请求正常。

先执行 12 次公开请求（包含状态页），改变 UA、编码请求头、HTTP/HTTPS、参数形态，并检查摘要与网页搜索；出现成功对照后，追加 8 次 URL 等价性/健康对照；最后 4 次同连接 ABBA，共 **24 次直接 HTTP 请求**。查询只有公开 `electron`、`graph neural network` 及公开 ID，无论文派生查询、密钥或云模型。多数查询 max_results=1；minimal_query 刻意省略分页参数，返回默认 10 条。

浏览工具另读取官方资料，并尝试访问编码后的 URL；浏览工具会重排参数且仅报告不可访问，未给出可用于对照的原始 HTTP 状态。**该尝试不计为一次观测到的 406，也不能证明独立公网出口。** 24 仅指本目录脚本记录的直接请求，不冒充全部浏览操作总数。

## 2. 成功对照：原 UA 本身并不必然导致失败

同一官方示例 URL：

```text
https://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1
```

原有 `NoveltyFramework-Audit/1.0`、附项目地址的 UA、真实 httpx UA、不发送 UA，以及 `Accept-Encoding: identity`，均返回 **200** 和相同 SHA-256 的有效 Atom。HTTP 示例入口返回 301 到 HTTPS，未跟随。主站与 export 摘要页、主站网页搜索也返回 200。

这排除了“原 UA 在所有路径上都被拒绝”与“整个 arXiv 完全不可访问”的解释。它不证明 UA 对所有未缓存路径都无影响。此前失败的图神经网络查询改用项目标识 UA 后仍为 406。

## 3. 语义等价 URL 的确定性差异

以下请求都表达 `search_query=all:electron, start=0, max_results=1`；空 id_list 与未指定等价：

| 形式 | 结果 |
| --- | --- |
| `search_query=all:electron&start=0&max_results=1` | 200，有效 Atom |
| `search_query=all%3Aelectron&start=0&max_results=1` | 406，空 body |
| `start=0&max_results=1&search_query=all:electron` | 406，空 body |
| `search_query=all:electron&start=0&max_results=1&id_list=` | 406，空 body |
| 再次请求最初形式 | 200，相同内容 |

最简 `?id_list=1706.03762` 返回 200；上一轮带 start/max_results 的同 ID 请求为 406。这是参数形态差异的补充观察，两轮不在完全同一时刻，强度低于上述同轮配对。

将原图神经网络查询仅改成原样冒号仍返回 406。因此，**不能把“不编码冒号”当作已经验证的通用修复**。固定例子成功可能依赖该精确 URL 已存在的缓存内容。

## 4. 同连接 ABBA 排除时间/换连接混杂

[persistent_results.json](persistent_results.json) 记录同一个直连 httpx HTTP/1.1 client 上：

```text
A 原样冒号 → 200
B %3A 冒号 → 406
B %3A 冒号 → 406
A 原样冒号 → 200
```

解码后的参数完全相同，request headers 相同。底层 trace 只出现 **1 次 TCP 建连和 1 次 TLS 建立**，后续请求复用连接；保存了实际发送的 `wire_raw_path`，不是仅比较输入字符串。这个对照比之前“同环境先后请求”更能排除换连接、客户端/出口切换及整站暂时恢复等解释。

四个请求均已收到完整 HTTP 响应；随后采集 TLS 证书的可选诊断步骤出现 TypeError，原始记录保留 exception_type。它不是请求失败，也未触发重试。TLS 发行者信息未从此次 response stream 获取到，不能据此认定具体 TLS 终端。单连接也不使我们拥有边缘层之后的路由/源站日志。

## 5. 缓存线索：有相关性，尚非完整根因证明

本轮成功的 API 响应带 `Google Frontend`、Atom 内容以及 `X-Cache` 中的 HIT；406 为空 body、`private, no-store`，`X-Cache` 为 MISS。参数顺序和等价编码可以改变缓存键，因此现象**符合“已有缓存内容可以返回，而另一请求处理/回源路径失败”**的假设。

但我们没有控制服务端缓存状态，也没有缓存规则、WAF/源站日志，不能将相关性升级为“已证明 Fastly 某规则故障”或“确定是缓存未命中造成 406”。普通无效 ID 也收到空体 406，未得到手册描述的 Atom 错误条目，提示错误响应边界有异于正常 API 错误，但仍不足以断定在哪一层产生。

## 6. 与项目生产请求的直接连接

[production_path_probe.py](production_path_probe.py) 使用真实 `ArxivRequestScheduler`、`ArxivSearchTool` 和 httpx MockTransport：

1. `search('all:electron', limit=1)` 被序列化为 `search_query=all%3Aelectron&start=0&max_results=1`，**与本轮实际失败 URL 精确一致**。这是客户端标准参数序列化的结果，不是 Qwen 输出 `%3A`。
2. 注入本轮真实 200 Atom，原生产解析器能解析出一条结果。
3. 注入 406，原路径抛出 HTTPStatusError，发生在 Atom 解析之前。

结果见 [production_path_results.json](production_path_results.json)。这把故障链进一步拆成：模型/人工计划 → 确定性查询编译 → 参数序列化 → 外部 HTTP 406 → 原执行器停止链 → not_run。

**能解析出一条结果不等于结果标识正确**，下节记录新发现的另一个缺陷。诊断脚本首次误用清理接口 close，改为生产已有 shutdown 后仅离线重跑，偏差见 [diagnostic_deviation.json](diagnostic_deviation.json)。没有新增外部请求或改写首轮网络结果。

## 7. 已定位的独立本地缺陷：旧式 ID 截断

生产 [arxiv.py](../../../backend/src/novelty_agent_framework/tools/database_search/providers/arxiv.py) 的 `parse_entry` 使用：

```python
external_id = entry_id.rsplit("/", 1)[-1]
```

真实 Atom 给出 `http://arxiv.org/abs/cond-mat/0011267v1`，当前代码却得到 `0011267v1`，最终生成 `https://arxiv.org/abs/0011267` 和对应错误全文 URL；旧式 ID 所需的 `cond-mat/` 丢失。

用本轮两份 electron 响应和一个现代 ID 响应离线检查，共 **12 个条目观察，6 个不匹配，涉及 5 个不同的旧式文献 ID**（其中一个条目重复出现）。现代 ID 对照不发生该类截断。逐项原始 ID、期望/实际标识及 URL 见 [identifier_audit.json](identifier_audit.json)。这些计数仅描述这批响应，不代表总体错误率。

这是已确定的本地解析代码缺陷，可能导致后续元数据或全文定位错误；本次没有请求错误 URL 验证具体状态码。**它发生在收到 200 之后，不是此前 406 的根因，也不是本地小模型造成。** 当前只记录复现，尚未修改生产代码。

## 8. 后续处理边界

- HTTP 406：带上等价 URL、ABBA、请求时间和 headers 向有权限查看源站/边缘日志的一方核查，才能进一步确认过滤或回源原因。本目录已有最小复现，不擅自联系外部人员。
- 不将改编码、换 UA 或切网页搜索直接合入生产作为“修好”；图神经网络真实查询仍失败，网页路径也未验证完整 Search→Evidence/Reviewer。
- 旧式 ID：修复时应保留 `/abs/` 后的完整标识，并独立覆盖现代/旧式 ID、版本号、URL 与全文定位。该修复可以离线验证，但本次未实施。
- 原任务书的真实成证、语义核验和整体验收仍未完成。

## 9. 记录入口

- [首轮 12 请求](results.json)，脚本 [probe.py](probe.py)。
- [后续 8 请求](url_equivalence/results.json)，脚本 [url_equivalence_probe.py](url_equivalence_probe.py)。
- [同连接 4 请求](persistent_results.json)，脚本 [persistent_connection_probe.py](persistent_connection_probe.py)。
- [生产请求/解析复核](production_path_results.json)，[标识缺陷复核](identifier_audit.json)。
- [一致性与扫描校验](validation.json)。所有 `.body` 保留对应原始响应；没有将失败文件改成成功。
