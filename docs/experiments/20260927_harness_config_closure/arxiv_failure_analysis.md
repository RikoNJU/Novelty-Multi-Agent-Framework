# arXiv query HTTP 406 的有界复查

执行时间：2026-09-28 00:18:19–00:18:24 Asia/Shanghai（JSON 保存 UTC）。追加授权范围为最多 4 次公开固定词查询 GET。本次准确发起 4 次，未自动重试，未跟随重定向，无模型调用、无论文派生查询、无 API key。固定 query 为 `all:"graph neural network"`，start=0，max_results=1。User-Agent 固定 `NoveltyFramework-Audit/1.0`。

| 对照 | 请求差别 | HTTP | 可公开响应证据 |
| --- | --- | --- | --- |
| 基准 export.arxiv.org/api/query | 空格 `%20`；Accept `application/atom+xml` | 406 | 空 body；cache-control private,no-store；via 两级 varnish |
| 编码变体 | 同一 query 的空格 `+`；其余同基准 | 406 | 同样空 body、no-store、via |
| Accept 变体 | 空格 `%20`；Accept `*/*` | 406 | 同样空 body、no-store、via |
| arxiv.org/api/query 主机 | 与基准同编码和 headers，主机改 arxiv.org | 302 | Apache；Location 为 `http://export.arxiv.org/api/query?...`；357 字节 HTML，未跟随 |

完整 URL、请求时间、状态、选定响应 headers、body 前 200 字节及 body hash 见 `arxiv_public_probe.json`。`arxiv_public_probe.py` 保存具体方法；重新执行会再次发请求，因此未自动重跑。

**有证据的结论**：在这次网络路径/服务状态下，query 操作仍没有获得 Atom 成功响应；两种常见空格编码和放宽 Accept 都没有消除 406。arxiv.org 主机只给出通向 export 的重定向，没有提供成功替代路线。Via 字段证明响应路径涉及缓存/代理层，但不能据此把 406 归因到客户端代理、特定 WAF、CDN 或 arXiv 应用中的某一层。空 body 没有可用错误码或说明。

**根因仍 Unknown**：四次有界对照不能确认是否为协商、上游策略、网络出口条件、请求频率条件或其他服务限制。User-Agent 本轮保持恒定，没有做 UA 因果测试。前三次请求同一主机且连续执行，不能当作独立多环境试验；不据此下“所有编码/所有 Accept 均不可用”的普遍结论。

此前审查的 known-ID `1706.03762` 200 是历史上另一操作成功的证据，不是本轮同时间的健康对照；也不能用它宣称 query 搜索健康。本轮没有消耗授权之外请求重新测 ID 或全文。总体分类仍是 **检索技术失败，未获得材料**，不是“零相关文献”，不支持否定任何科研结论。没有证据支持更改生产 API 编码、Accept 或主机默认值，故生产配置保持原样。
