# 2026-09-28 arXiv Web 与本地 Qwen 整流程实验归档

本次上传已有实验产物，没有重新运行模型或修改生产实现。

| 项目 | 记录 |
| --- | --- |
| Run ID | `run-09834db78b2742109def38fd991ff11a` |
| 代码版本 | `7e71dc96b24f87e8ea8fed2fa5b761dfaef53a83` |
| 模型 | `qwen2.5-7b-instruct` |
| 上下文窗口 | 32768 tokens |
| 耗时 | 352818 ms |
| 已预留物理 Provider 请求数 | 13（上限 24；预留数不等于成功请求数） |
| 归档文件 | 260 个 |
| 运行状态 | `SUCCESS`；仅表示流程完成，不表示所有查新点核验成功 |

## 单卡核验与上下文

| 查新点 | 输入 tokens | 预留输出 tokens | 总请求预算 | 观察结果 |
| --- | --- | --- | --- | --- |
| NP-1 | 4646 | 8192 | 12838 | 模型给出 not_novel，但特征比较含部分支持和未知；覆盖校验拒绝裁定 |
| NP-2 | 4076 | 8192 | 12268 | 引用了上游证据中的 read_id，本轮 Reviewer 未读取，引用注册失败 |
| NP-3 | 4023 | 8192 | 12215 | 模型给出 not_novel，但特征比较未满足完整支持要求；覆盖校验拒绝裁定 |
| NP-4 | — | — | — | 没有可供可靠核验的绑定证据，material_unavailable |

三次单卡模型调用均正常结束（`finish_reason=stop`），没有上下文溢出或输出截断证据。NP-2 的 read_id 已存在于模型输入的上游证据元数据，不能称为凭空编造；校验器只接受本轮 Reviewer reader 产生的读取记录。NP-2 随后因单卡技术错误跳过汇总，没有完成自动纠错闭环。

NP-3 的证据判断也存在质量疑点：模型将“没有提到”标为 contradicted，并以架构相似推导不新颖。扩大窗口能否改善判断没有对照证据，本次不能归因于 32768 不够。

## 补检与错误处理边界

本轮轮数上限为 1。恢复记录中 NP-1、NP-3、NP-4 均为 `stop`，原因是到达轮数上限；没有执行第二轮补检。NP-2 的单卡技术错误保留在 Review 中，但本轮恢复决策列表没有 NP-2，说明错误与恢复覆盖仍有缺口。

Reviewer 提出补查、报告写入补查说明、错误目录给出恢复建议，都不能作为已执行补检或已恢复成功的证明。完整补检器与错误恢复闭环仍待下一轮设计和验收。

## 原始证据

- [运行清单](runtime/MF2033k6lC_2026-09-28/run-09834db78b2742109def38fd991ff11a/manifest.json)
- [单卡及最终核验记录](runtime/MF2033k6lC_2026-09-28/run-09834db78b2742109def38fd991ff11a/workspace/MF2033k6lC/novelty-reviews.json)
- [第一轮恢复决策](runtime/MF2033k6lC_2026-09-28/run-09834db78b2742109def38fd991ff11a/workspace/MF2033k6lC/recovery-round-1.json)
- [NP-1 单卡模型调用](runtime/MF2033k6lC_2026-09-28/run-09834db78b2742109def38fd991ff11a/llm_calls/0022_local-qwen2.5-7b.json)
- [NP-2 单卡模型调用](runtime/MF2033k6lC_2026-09-28/run-09834db78b2742109def38fd991ff11a/llm_calls/0023_local-qwen2.5-7b.json)
- [NP-3 单卡模型调用](runtime/MF2033k6lC_2026-09-28/run-09834db78b2742109def38fd991ff11a/llm_calls/0024_local-qwen2.5-7b.json)
- [结构化报告](runtime/MF2033k6lC_2026-09-28/run-09834db78b2742109def38fd991ff11a/workspace/MF2033k6lC/report.json)
- [错误码与补检／恢复动作表](../error-and-supplement-codes.md)

归档包含日志、输入、证据及报告；清单中的启动快照路径指向原运行目录，本次归档不宣称独立包含该外部启动快照或模型服务。
