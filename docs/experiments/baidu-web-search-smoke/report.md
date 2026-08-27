# BaiduSearchBackend v1 接入与真实预实验报告

## 1. 实验目标与结论

本实验验证百度 Web Search API → `BaiduSearchBackend` → `WebSearchTool` → `ReferenceStore` → `ReferenceManifest` 的真实链路。实验不使用 LLM 或 ToolCallHarness。

结论：三类 query 均完成真实 API 请求；WebSearch vertical smoke 返回 5 个 `WebSearchItem`，Manifest 持久化 5 个 `SourceRecord`。稳定 ID 检查为 `True`，返回 ID 均可从 Manifest 恢复为 `True`。

## 2. 时间与本地环境

- 开始：2026-08-24T18:50:53.565856+00:00
- 结束：2026-08-24T18:50:56.698984+00:00
- Python：3.11.15
- 平台：Linux-6.18.33.2-microsoft-standard-WSL2-x86_64-with-glibc2.39
- API Key：configured（值未记录）
- Endpoint：`https://qianfan.baidubce.com/v2/ai_search/web_search`
- 整体实验耗时：3133.125 ms
- 两次 WebSearch vertical smoke 合计耗时：901.955 ms

## 3. Backend contract 与固定请求

`BaiduSearchBackend.name == "baidu"`，实现冻结接口 `search(query, *, max_results) -> SearchBackendResult`。请求固定使用一个 user message、`baidu_search_v2`，以及 `resource_type_filter=[{"type":"web","top_k":max_results}]`，不设置 edition、filter、fallback 或 retry。

查询计量假设：ASCII 字符按 1 单位、所有非 ASCII Unicode code point 按 2 单位；超过 72 单位本地拒绝且不裁剪。

## 4. Backend-only smoke

| Query | 状态 | request_id | 原始 references | 标准化 SearchHit | 耗时 ms |
|---|---|---|---:|---:|---:|
| 多智能体 科技查新 | 成功 | 27b48067-8232-4f0f-80c6-4f9bdea534af | 5 | 5 | 848.276 |
| 多智能体 科技查新 论文 | 成功 | 7ad4049f-9796-4d3f-a069-8a19a3fc9a3a | 5 | 5 | 659.351 |
| multi-agent novelty search | 成功 | a5a13b2a-0a74-4a64-8025-ca6cfc17df0d | 5 | 5 | 723.144 |

字段映射为：title ← title（缺失回退 URL）、url ← url、snippet ← snippet、published_at ← date、source_name ← website、external_id ← id、score ← None；request_id、web_anchor 和 content 仅保留在 `raw_metadata`。

## 5. 缺失、过滤与重复情况

- snippet 缺失：0
- date 缺失：0
- website 缺失：0
- 非 web 结果：0
- 缺少 URL 的 web 结果：0
- 重复 URL：0
- 来源域名分布：`baijiahao.baidu.com` × 5、`mp.weixin.qq.com` × 4、`blog.csdn.net` × 3、`www.mbachina.com` × 1、`www.163.com` × 1、`cloud.tencent.com` × 1

## 6. WebSearch vertical smoke

真实 `BaiduSearchBackend` 无适配地注入现有 `WebSearchTool`。每个标准化结果被转换为 Agent-facing `WebSearchItem`，并在返回前持久化为 `SourceRecord`：`source_id="baidu"`、`source_kind="web"`、`access_status="discovered"`、`landing_url=hit.url`。

相同 query 连续执行两次，source_record_id 序列保持一致：**True**。Manifest 未因第二次搜索无限追加重复记录，且所有第二次返回 ID 均存在于 Manifest：**True**。

`WebSearchTool` 与 `SearchBackend` frozen contract 均为零修改。

## 7. 中文结果定性观察

本节是 smoke experiment 的定性观察，不是 precision、recall、MAP 或 NDCG 结论。结果标题、URL、snippet 与来源域名可用于候选筛选；应结合上面的域名集中度和字段缺失统计判断来源多样性。任何 snippet 或 provider content 都只是搜索阶段候选发现信息，不能作为已验证证据。

本次 15 条 Backend-only 结果中，百家号、微信公众号与 CSDN 合计 12 条，占 80%。结果中未出现明显的一手学术出版平台或论文数据库，来源以二次传播、技术博客和资讯页面为主。`多智能体 科技查新 论文` 查询还混入论文 AI 降重、AIGC 检测平台等商业内容；英文 query 仍主要返回中文二手内容。这说明 API 连通性与中文候选发现能力成立，但当前固定请求缺少学术来源约束、语言控制和质量过滤，不能直接满足正式科技查新的来源质量要求。

所有标准化结果均提供 snippet、date 和 website，字段完整性较好；但字段完整不等于内容权威。当前 `content` 体量较大，只保留为 provider metadata，后续应评估是否需要裁剪以控制 Manifest 膨胀。

正式证据链仍应为：WebSearch → Browser → Artifact → Reader → EvidenceCardBuilder。

## 8. 实验发现的数据缺口

- 缺少一手论文数据库、大学机构库或正式出版平台结果；
- 缺少“学术/论文来源”过滤参数，query 中加入“论文”不足以保证学术质量；
- 英文 query 没有带来英文来源，当前 v1 没有语言控制；
- 来源集中于少数内容平台，候选多样性有限；
- provider `content` 与 snippet 仍是未验证搜索材料，不具备 Artifact/Evidence 身份；
- 尚未通过 Browser 验证 URL 可访问性、正文真实性、页面稳定性和元数据一致性；
- 没有标注集，因此不能给出 precision、recall、MAP 或 NDCG；
- 当前仅验证 standard 默认 edition 和 `baidu_search_v2`，没有比较其他可选搜索策略。

## 9. 边界与下一步

本实验未使用 LLM、ToolCallHarness、Browser、Reader 或 EvidenceCardBuilder，未实现缓存、复杂 retry、Router 或多 backend fallback。下一步可在确认结果质量与稳定性后进行 WebSearch + Harness live smoke；在正式 Researcher 工作流接入前，仍需实现 Browser 并验证候选 URL 到 Artifact 的可信转换。
