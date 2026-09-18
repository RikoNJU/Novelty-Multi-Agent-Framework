# DeepSeek 官方接口成功运行冻结记录

本目录冻结用户从前端提交的一次真实查新。前端任务 ID 为 `2f419fe0beed4e4db3e26096dad28439`，Runtime 运行 ID 为 `run-be230c241ed74d34833beb8632ba1553`；运行代码版本为 `c459bde`。Runtime 从 `2026-09-18T01:02:54.684078+00:00` 至 `01:05:54.438952+00:00`，耗时 179,821 毫秒，终态为 `SUCCESS`。报告生成、完整性验证、持久化与渲染阶段均已完成。此处的“成功”表示工作流和输出契约完成，不等于报告的科研结论已经人工核验。

## 运行规模

| 指标 | 实际记录 |
| --- | ---: |
| 输入 PDF | 1 篇，2,023,977 字节 |
| 查新点 | 3 个 |
| 研究任务 | 3 个 |
| 去重文献 Work | 35 个 |
| 文献 Artifact | 36 个 |
| 工具调用 | 57 次：reference_search 4、database_search 13、reader 40 |
| 模型调用 | 77 次，均成功 |
| Token | 输入 942,523；输出 25,619；合计 968,142 |
| 输入缓存命中 Token | 89,728 |

本轮未启用本地模型预算锁。Runtime 的 `llm_usage` 将 77 次调用全部记为 `unpriced`，其中 `amount_rmb=0` **不代表免费**。运行发生在北京时间周五 09:02—09:05；依据当时 [DeepSeek 官方价格表](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)的峰时费率（每百万输入缓存命中 0.04 元、未命中 2 元、输出 8 元），由返回的 usage 估算约 **1.91413112 元**。这不是已核对的服务商账单。

## 冻结文件

- [正式渲染报告](report.md)及[结构化报告](report.json)
- [Runtime 终态摘要](runtime-summary.json)
- [查新点](novelty-points.json)、[检索计划](retrieval-plans.json)、[证据卡](evidence-cards.json)、[Reviewer 结果](novelty-reviews.json)、[参考文献登记](references.json)
- [原始路径、大小和 SHA-256 索引](manifest.json)

用户上传的 PDF（SHA-256 `82580951dfddb8e0fd815f8f3c573828a8ca8ff0dfee63219cb7606116a0b04c`）、完整模型输入/响应与检索原文保留在本机 `outputs/live-experiment-20260918-deepseek-official-retry/2f419fe0beed4e4db3e26096dad28439/`，未纳入 Git。私密 API 密钥也未纳入本目录或仓库。冻结文件可用 `manifest.json` 与本地原始输出逐项校验。
