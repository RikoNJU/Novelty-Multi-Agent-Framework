# ARXIV-ACCESS-01：网络、代理与 API 路径诊断

日期：2026-09-14

## 1. 结论

诊断排除了稳定的环境代理故障和底层网络故障：同一台机器、同一已知 ID 下，httpx 默认代理、httpx 强制直连、curl 默认代理、curl 绕过代理均能访问普通 arXiv 页面和 known-ID export API，全部返回 HTTP 200；两次 API 响应均为可解析 Atom feed 且包含 1 个 entry。

但访问尚未达到可用于测量 Query recall 的稳定状态：诊断突发请求后曾收到明确 HTTP 429；最终 canonical smoke 的 A 成功，B 精确标题查询在一次 retry 后仍 ReadTimeout，C 因 B Gate 未通过而没有发送。

最终判定：

```text
环境代理问题                  NO
底层网络问题                  NO
export API 持续不可达          NO
服务端明确限流                YES（观测到 HTTP 429）
known-ID access              PASS
exact-title access           FAIL（ReadTimeout）
structured-query recall      NOT_MEASURED
Query 层修复                  NOT ALLOWED
Run E                        NOT ALLOWED
```

## 2. 固定条件

| 项目 | 值 |
|---|---|
| 机器/工作区 | 与 Run D、ARXIV-RATE-01 相同 |
| 已知 ID | `1706.03762` |
| 普通页面 | `https://arxiv.org/abs/1706.03762` |
| export API | `https://export.arxiv.org/api/query?id_list=1706.03762&max_results=1` |
| httpx | `0.28.1` |
| curl | `8.5.0` |
| 环境 | HTTP/HTTPS proxy 与 NO_PROXY 的大小写变量均存在 |

报告只记录代理变量是否存在，不保存代理配置值或任何凭据。

## 3. httpx 对照

| trust_env | Target | HTTP | 类型 | 大小 | 时间 | Atom / Entry |
|---|---|---:|---|---:|---:|---|
| `True` | `arxiv.org/abs` | 200 | HTML | 43,644 B | 1.065 s | - |
| `True` | `export API` | 200 | Atom XML | 2,962 B | 0.787 s | parsed / 1 |
| `False` | `arxiv.org/abs` | 200 | HTML | 43,644 B | 0.292 s | - |
| `False` | `export API` | 200 | Atom XML | 2,962 B | 0.747 s | parsed / 1 |

默认环境与强制直连均成功，故不符合“默认失败 + `trust_env=False` 成功”的代理故障模式。

## 4. curl -v 对照

| 模式 | Target | HTTP | Remote | 时间 |
|---|---|---:|---|---:|
| 当前环境 | `arxiv.org/abs` | 200 | `127.0.0.1`（本机代理） | 1.018 s |
| 当前环境 | `export API` | 200 | `127.0.0.1`（本机代理） | 0.628 s |
| `--noproxy '*'` | `arxiv.org/abs` | 200 | `151.101.131.42` | 0.424 s |
| `--noproxy '*'` | `export API` | 200 | `146.75.47.42` | 1.014 s |

curl verbose 记录确认：默认环境通过本机 HTTP CONNECT proxy，绕过模式直接解析并连接 arXiv 地址；两条 TLS 链路证书校验均成功。普通页面与 export API 在两种链路上均返回 200。

## 5. Case A 修正

历史 Smoke Case A 使用：

```text
search_query=id:1706.03762
```

现已改为官方 known-ID 参数，并固定为与诊断相同的请求形状：

```text
id_list=1706.03762&max_results=1
```

不再附带 `search_query` 或 `start`。请求级测试直接检查最终 URL 参数，避免只验证配置对象。

提交：`d8503d9 fix(smoke): use id_list for known arxiv ids`。

## 6. canonical A/B/C Smoke

在诊断完成并修正 Case A 后，只执行一次最小 smoke：

| Case | HTTP | Atom | Entry | Match | 结果 |
|---|---:|---|---:|---|---|
| A：known ID | 200 | parsed | 1 | true | `VALID_HIT` |
| B：exact English title | 无响应 | 未测量 | - | - | `ReadTimeout` |
| C：Run D query | 未发送 | 未测量 | - | - | `SKIPPED_UPSTREAM_GATE` |

B 仍经过 provider single-flight、4 秒限速和 1 次有界 retry；最终没有 HTTP status，所以不能把它判为 `200 + EMPTY`，也不能进入 C。

另有一条重要时序观察：六项网络诊断刚结束后，曾使用 `id_list=1706.03762&start=0&max_results=5` 发起非 canonical A，请求收到 HTTP 429。这是服务端明确限流证据，也说明“单次 known-ID 200”不代表当前出口在连续请求下已经稳定。

## 7. 判定解释

当前不是单一的“代理坏了”或“export API 坏了”：

- proxy 与 direct 都能成功，排除稳定代理路由故障；
- 普通页面与 known-ID API 都能成功，排除持续底层断网和持续 API 路径故障；
- 同一时段同时出现 200、429 与 ReadTimeout，说明出口/API 访问具有明显的瞬时性和限流敏感性；
- known-ID A 已恢复，但 exact-title B 尚未建立稳定的 `200 + entry/empty` 基线；
- C 没有执行，所以 SearchPlan structured query recall 仍未测量。

下一步仍应停留在 access/rate 层，降低跨进程突发、留出冷却窗口，并重复最小 A/B；只有 A/B 稳定通过后才执行 C。当前不修 `ti/abs/all`、strict/medium/broad、中文 term、alias 或 fallback，也不运行 Run E。

## 8. 可追溯产物

机器可读结果：

```text
docs/experiments/ARXIV_ACCESS_01_2026-09-14/diagnostic.json
```

临时 httpx 诊断脚本位于 `/tmp`，只用于本次矩阵测试，归档完成后删除。
