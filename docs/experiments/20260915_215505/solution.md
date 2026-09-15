# Web 补充资料策略与运行错误分析

## 策略修改

WebSearch 结果仅作内部补充资料，继续保留 source_kind=web_supplement 供审计。新策略不允许从网页内容生成 Evidence/Card；即使网页已由 Browser 获取并经 Reader 读取，Builder 仍拒绝其作为论文证据。此类策略拒绝不会再触发一次无意义的引文纠正。

Renderer 不把 Web 记录列入相关文献或附件文献清单。整份报告只要有论文候选、论文卡片或参考文献候选，就不显示 Web 建议；有论文但没有卡片不等于没有论文。只有整份报告未取得论文且存在 Web 记录时，才显示一段后续检索建议，使用网页检索方向帮助调整论文查询，不罗列网页标题/链接，不复述网页断言为已证实事实。Web 的采集记录不会因此被删除。

同步更新 Researcher、database_research、web_supplement、Reviewer 与 Coordinator 提示词。新策略替代之前“五种条件下允许 Web Evidence”的策略。Web 何时被模型调用仍由提示词约束；禁止 Web 产卡和报告展示条件由代码执行。

使用上一轮完整运行产物重新渲染报告，未再次调用模型或外部检索。因为该轮确实检索到论文，预览没有 Web 建议，也没有 Web 来源清单；保留原有论文卡片和论文附件。旧实验报告未覆盖，预览位于本目录 MF2033k6lC-report.md。

## 运行错误：已确认根因

分析对象：../20260915_212448，8个研究任务、6张最终卡片、完整报告生成成功。以下故障仍存在，此次只分析，未把它们混入策略修改。

### P0：Reviewer 16次回读失败是代码强制查错库

`tools/reader.py` 的 ReviewerReaderTool.ainvoke 已检查 artifact_id 属于输入 Evidence，但构造 ReferenceReadRequest 时硬编码 `namespace=ArtifactNamespace.RESEARCH_REFERENCE`，注释还写着“自带参考语料不在其职责范围内”。实际生产输入包含5张 subject-reference 卡，且 Evidence.provenance.artifact_namespace 已准确标记 subject_reference。硬编码与当前输入契约冲突。

因此之前把这一现象解释为“模型选择 namespace 错误”不准确：ReaderArguments 没有交给模型选择该命名空间，服务端自己固定了它。16次错误均在research manifest找subject artifact，文件实际存在。研究库文本回读可成功，进一步吻合此原因。

方案：从卡片引用的 Evidence 中以 artifact_id 解析唯一的 namespace/work_id 地址；歧义时明确拒绝，缺少旧字段时保留明示兼容策略；请求和返回都核对该地址。增加 subject/research 双命名空间及相同artifact ID冲突测试。

### P1：Researcher 有文本但收尾 schema 冲突，导致一任务0卡

NP-1/T-2 已读取4份文本，模型同时返回非空cards与no_evidence_reason。schemas/research_tools.py 的 ResearchFinishDraft.require_cards_or_reason 正确拒绝互斥冲突；workflows/research_task.py 在解析失败处分支直接partial返回，未进入Builder。因此Builder的逐卡拒绝纠正逻辑不会触发。

方案：对于可确定的互斥冲突，将说明移入warnings、保留cards并重新完整校验；对于其他结构错误最多一次无工具格式纠正。仍须经过Builder的真实原文引用与来源校验，不可直接接受未校验cards。

### P1：Reviewer 最终非JSON导致NP-1降级

第二轮NP-1返回以“Based on my analysis”开头的自由文本。agents/evidence_reviewer.py 的 JSON 提取仅能提取现有JSON片段，无法将自然语言转换为模型契约；model_validate_json失败，被fail-closed降级为insufficient_evidence。该轮没有后续格式恢复，首轮判定也不直接沿用。

方案：一次无工具格式修复，提供schema并限制只能转写已有结论，重新验证所有引用；仍失败则维持不足。失败原因应区分模型格式错误与真正的证据覆盖不足，避免用户误读。

### P1：NP-2检索式为“无”是审计过滤，非没生成检索式

原始runtime tools中保存了NP-2实际查询和失败执行；workflows/research_task.py 的 _trusted_bundles 跳过 succeeded=False 的观测，故失败查询未进入后续research_bundles和检索式聚合。Renderer使用持久化query_plan.queries，没有失败查询就展示“无”。NP-2的卡片来自subject references，与数据库检索失败并不矛盾。

方案：单独持久化全部执行审计（query/status/error/source/task/point），包括失败、空结果、部分成功；只有证据内容继续走可信门控。报告展示实际执行式及失败状态，不能用放宽可信bundle来修复审计。

### P2：3次WebSearch错误是本地输入超限

tools/web_search_backend.py 的 _validate_baidu_query 计数为ASCII字符1单位、非ASCII字符2单位，大于72直接抛BaiduSearchError。这3次没有发送到百度API；另11次HTTP 200说明工具并非整体不可用。

方案：工具描述明确长度算法与上限；返回超限单位数，允许一次缩短查询。避免静默截断关键检索概念或不断重复长查询。新策略限制Web用途，也会减少不必要的Web调用。

## 无法从当前证据确定的外部原因

### arXiv：6次429、2次读取超时

调度器记录8次物理请求、0次200、interval_violation_count=0，且metadata batch=0。说明本轮未违反其自身配置间隔，不能据此推断服务端限流阈值、共享出口IP影响、服务拥塞或具体429触发规则。复用缓存使本轮没有metadata合并，不是batch补丁有效性实验。

方案：后续独立低频探测保存响应Retry-After和时间、区分网络超时与HTTP429，核对出口和跨进程并发；避免在未明确外部原因前不断扩大重试。当前有证据证明发生限流，但没有证据证明具体外部根因。

### Springer：7次HTTP404

搜索侧使用providers/common.py的通用状态校验，把HTTP404归ProviderRequestError；全文侧反而把403/404当无可用全文。此前实验出现过“无数据”404响应，本轮仅记录状态未保存body，因此不能证明本轮七次404全部为正常空结果。

方案：搜索侧按响应体业务语义识别合法无结果，其余404保留错误；把响应中的非敏感诊断字段保存到审计，不能无条件把404改成空结果。

## 验证与限制

完整默认回归726项：720 passed、6 skipped、0 failed。包括Web正文拒绝产卡、拒绝不触发引文修复、旧Web记录兼容、已有论文/无论文/无卡三类报告分支、论文附件保留等。

预览仅验证当前Renderer对已归档输入的展示；没有重跑在线流程，也没有验证模型对新Web调用提示词的遵循率。新报告仍保留此前运行中的NP-2检索式缺失和NP-1评审不足，因为这些根因未在本次修改中修复。
