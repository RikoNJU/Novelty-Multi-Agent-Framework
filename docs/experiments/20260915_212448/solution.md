# 完整运行：跳过 MinerU

## 执行方式

样例 `examples/MF2033k6lC.pdf`，复用先前已解析的 PaperInput、full.md、content-list.json 及有效 subject-reference 缓存。从查新点提取重新运行，依次执行规划、Researcher、Validator、Reviewer、补检、报告综合、完整性校验、持久化和渲染。此次未调用 MinerU，也未重新做 OCR。

使用当前工作区整合后的 prompts/skills；补丁快照见 working_changes.diff，两个新增 skill 另存于 skills/。启用 arXiv、Springer、WebSearch，关闭 null_catalog；Browser 保持配置中的关闭状态。因此 Web 仅作来源发现，没有网页全文取回或网页证据链验证。

开始：2026-09-15 21:02:12（Asia/Shanghai）。结束：2026-09-15 21:24:48。程序记录耗时 1358.76 秒（约 22 分 39 秒）。独立目录运行，没有覆盖历史实验。

## 结果

| 项目 | 结果 |
| --- | --- |
| 工作流/报告完整性/渲染 | SUCCESS，报告已生成 |
| 查新点 / 轮数 / 任务 | 3 / 2 / 8 |
| 任务状态 | 7 completed，1 partial |
| 外部数据库文献 | 16 篇 |
| 外部 artifacts | 21：16 abstract、5 extracted_text |
| Researcher 读取 | 22 次 |
| 原始卡片 / 最终卡片 | 6 / 6 |
| 按查新点分配 | NP-1：2；NP-2：3；NP-3：1 |
| 来源 | 5 张来自缓存 subject references，1 张来自本轮 Springer 文献 |
| Evidence 类型 | 8 条 quote Evidence 均为 database_evidence；卡片与 quote 数量不同 |
| Web 来源 | 93 条 source record，全部 source_kind=web_supplement |
| WebSearch | 11 次成功，3 次本地查询长度校验失败 |
| 模型调用 / reported tokens | 124 / 1,170,857（含多轮上下文累计，不代表独立正文量） |

报告：[MF2033k6lC-report.md](run/MF2033k6lC/report/MF2033k6lC-report.md)。运行状态、完整响应、模型计量、工具记录、HTTP 状态和候选台账均保留在 run/；统计见 metrics.json，核对见 verification.json。

最终 Reviewer：NP-1 insufficient_evidence（返回非 JSON 导致解析失败）；NP-2 novel，confidence 0.70；NP-3 partially_novel，confidence 0.62。这些是本轮模型输出，不代表本次实验验证了其学术判断的正确性。报告成功不等于所有内部工具调用成功。

候选台账统计为按任务累计的记录数：102 acquisition_unavailable、55 not_read、10 read_without_card、6 card_produced、2 read_task_interrupted。跨任务重复出现的文献会重复计数，不能与 16 篇外部去重文献直接比较。

## 新 prompt/skill 的实际表现

- 观察到参考文献查询、数据库检索在 Web 补充之前执行；任务无证据说明出现 DATABASE_UNAVAILABLE 等原因。
- 新来源标记在 93 条 Web 记录中保留，未发现将这些 discovery 记录直接构建为原始 Evidence。
- Browser 关闭时仍发生多次 Web 检索，说明提示词不能代替确定性预算/路由控制。仅依据工具日志和最终任务说明，不能证明每次调用前模型都明确陈述了触发原因。
- 两轮得到六张卡；本轮没有出现预算最终整理或引文纠正恢复成功的记录，不能将卡数变化直接归因于这些补丁。

## 错误、影响与解决方案

### 1. Researcher 收尾结构冲突导致整任务无卡

NP-1/T-2 已读 4 份文本，但收尾同时包含 cards 与 no_evidence_reason，ResearchFinishDraft 互斥校验失败，任务 partial、0 卡。当前纠正逻辑只覆盖 Builder 拒绝，未覆盖此前的 JSON/schema 解析。

建议：对有效 JSON 中这一可判定的结构冲突做受控处理，例如 cards 非空时将说明移入任务 warnings 并清空 no_evidence_reason，再走完整 schema 和 Builder 校验；其他收尾错误最多一次禁用工具的格式纠正，保留全部 Reader 结果。

### 2. Reviewer 回读选择了错误 namespace

共 16 次 reader 失败，提示 subject-reference artifact 不在 research manifest 中。对应文件仍在 subject_references，并非文件丢失。另有 4 次 Reviewer 回读成功，表明工具不是整体不可用。

建议：ReviewerReader 根据输入 Evidence 的可信 artifact_namespace 与 artifact_id 绑定构造回读地址；省略 namespace 时仅在输入中唯一可确定的情况下推导，存在歧义则明确拒绝，不再默认到 research_reference 后反复重试。

### 3. Reviewer 返回非 JSON

第二轮 NP-1 输出以 “Based on my analysis ...” 开头的自由文本，严格解析失败后降级 insufficient_evidence。报告已反映这一解析问题。

建议：提供一次无工具、仅格式修复的调用，保留原判定内容并重新校验所有 point/work/card/evidence 引用；无法恢复时继续保持不足状态，不能默认给出 novel。

### 4. NP-2 检索式仍显示“无”

报告 5.3 的 NP-2 为“无”，但其实际执行过数据库检索。当前可信 bundle 提取过滤失败观测，失败执行无法进入后续检索式汇总。NP-2 本轮数据库执行均失败，但从参考文献库得到卡片。

建议：把检索执行审计与可信证据分开，失败和零命中执行均持久化 query/status/error，Renderer 展示实际执行式及状态；不要为了展示失败检索而把失败响应升级为可信证据。

### 5. 外部检索问题

arXiv：8 次实际 API 请求，6 次 429、2 次读取超时，0 次 200；调度器 interval_violation_count=0。本轮 metadata batch 为 0（复用缓存），不能验证 batch 合并效果或推断 429 的具体外部限流规则。

Springer：HTTP 200 共12次、404共7次。404 被 provider 归为失败；此前实验见过“无数据”形式的404，本轮日志未保存响应体，因此不能将本轮全部404认定为零命中。建议按响应体语义区分合法空结果与真实错误。

WebSearch：11次请求HTTP 200；另3次查询超过百度72单位长度限制，在本地失败。建议在工具描述和参数校验中暴露实际计数规则，超限时返回可操作的缩短建议并限制重试，不应静默截断查询含义。

## 尚存报告风险

顶层 issues=[] 未汇总内部任务/回读/格式失败。报告能说明 NP-1 格式错误，但“拒绝证据为空”仅指后续门控列表，不能理解为 Researcher 没发生格式性丢卡。建议将任务状态与失败阶段单独汇总到报告限制。

此次只完成一次运行和审计，没有在运行中修改生产代码，也未提交或推送。完整 original artifact 工程及上述修复留待后续处理。
