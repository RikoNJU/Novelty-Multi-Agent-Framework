# 已证实的问题与拟议修复（不改变三组实验代码）

## P1：任务降级状态未进入最终报告

证据：第一组 10 个任务中 8 个 partial；arXiv API 无成功响应；result.json 的 issues=[]；报告 NP-1 却给出明确“新颖”结论。

根因链：

1. `workflows/novelty.py:_run_research_task` 仅捕捉抛出的异常后创建 WorkflowIssue。Researcher 正常返回 partial/failed、warnings 时 issues 仍为空。
2. `NoveltyPointReviewRequest` 与 `_render_point_prompt` 提供点、计划任务、卡片、证据，没有结构化 provider 成功率、检索错误、覆盖度。
3. `_synthesize_report` 不传递 workflow issues 或 task warnings。
4. `_check_final_evidence_sufficiency` 按设计只检查卡片数量，不负责检索覆盖；不能将其当作检索完整性门禁。

修复方案：

- 对正常返回的 partial/failed 生成结构化 WorkflowIssue，同时保存 provider、operation、error_type、retryable、point/task 标识。
- 按查新点聚合 RetrievalHealth：尝试/成功/零结果/失败/熔断/预算耗尽计数、来源与缓存来源；零结果不能与失败合并。
- 将健康度传入 Reviewer、Coordinator 和报告模板。外部检索整体失败时保留有依据的对比，但不能因“未检出”得出无条件的新颖结论；输出范围受限的结论或无法裁定。
- API 返回 execution_status 与 evidence_quality_status 两个字段；报告生成成功与证据充分性分别表达。

验收：构造有3张有效本地证据卡但所有外部 search 失败的场景，流程仍生成报告；报告必须写明检索降级、不得给出无限定新颖结论；result.issues 必须非空。另测真实零结果且 API 成功，不能被归为服务故障。

## P1：参考文献缓存刷新留下失联旧作品

证据：`stale_reference_reproduction.json`。刷新 ledger 没有 resolved 条目，但 manifest 留有9篇旧作品；reference_search 仍返回5项，引用标识为 work:...。

根因：ReferenceBootstrapService.bootstrap(force=True) 更新 ledger 并 merge manifest，未以本轮 resolved 集合构建新快照；ReferenceSearchTool.search 遍历全部 manifest.works，并为 ledger 中找不到的作品生成 fallback ID。

注意：bootstrap_ready 是 property（所有条目均有 attempts），并非 JSON 中必须有的布尔字段。失败条目有 attempts，仍可 ready；历史缓存此次重建的明确原因之一是缺少 references_digest。全失败仍可 ready 应配套健康度，不能把它解释为全部解析成功。

修复方案：在临时目录构建完整 ledger/manifest/artifacts，校验引用闭合后原子切换；检索严格限定为本轮 resolved_work_id 集合。如果业务选择保留 last-known-good 缓存，应保留旧 ledger 与 manifest 的一致快照，并标注 stale/fallback、刷新错误及时间，不能混合新失败 ledger 与旧 manifest。

验收：先成功解析A，再强制刷新为全失败，确认新快照没有无映射作品；选择回退策略时须整个旧快照一起保留且可观察。并发刷新期间读者不能见到半成品。

## P2：batch 指标混淆重试与逻辑批次

独立探测：6个逻辑请求、4个不同ID，一个逻辑批次，首次超时后重试。当前记录 unique_metadata_ids=8、dedup_count=4、batch_count=2；实际唯一ID=4、逻辑去重=2、逻辑批次=1。

根因：arxiv_scheduler.py:_record_physical 每次物理尝试都累加上述字段；它们描述的是尝试累计，不是名称容易让人理解的全局唯一量。physical_api_requests=2 是正确的。

修复方案：引入稳定 logical_batch_id，重试沿用该ID。分别记录 logical_batch_count、physical_attempt_count、unique_metadata_ids、logical_dedup_count、retry_count；合并压缩率采用首发物理请求数，重试开销单独统计。熔断拒绝也单列，不能把 logical/physical 的高比例直接称为 batch 收益。

验收：6调用/4ID/一次重试，断言logical_batch_count=1、physical_attempt_count=2、unique_metadata_ids=4、logical_dedup_count=2、retry_count=1。

## 限流处置建议

本次真实请求遵守4秒间隔，但仍收到 arXiv 429（Rate exceeded.），没有 Retry-After 响应头。批量合并可以减少请求，不能保证消除服务端/IP维度的限制。

- 429 时采用全进程共享、带抖动的自适应冷却；有 Retry-After 时遵守，没有时逐步延长（例如30/60/120秒，需后续实测调参）。
- 熔断状态向 Researcher 暴露 available_after；冷却内禁止对同一不可用provider反复消耗工具预算，应切换可用provider或结束为degraded。
- 缓存完全相同的查询和元数据成功结果；根据需求提供短TTL失败缓存；避免跨任务重复施压。
- 多进程部署时进程内共享调度器不足以约束同一出站IP，应共享限流状态。

## P1：Springer 无匹配数据的404被归为 provider 故障，提前终止放宽链

证据：第二组 Meta API 共11次404。补充探测复现其中一个中文查询，服务器 JSON 明确返回：

```json
{"status":"Fail","message":"No data was found for the given query.","error":{"error":"Not Found","error_description":"No matching data is available for the requested query."}}
```

`SpringerNatureSearchTool.search` 在解析该 JSON 前调用 `raise_for_provider_status`，于是抛 ProviderRequestError。`StructuredSourceRetrievalTool._search` 捕捉后设置 provider_failed=True 并 break，无法进入后续零命中放宽策略；模型再次调用同一provider也可能重复相同失败。

修复方案：仅在 Meta search endpoint、HTTP 404、合法JSON且确认为该 No data/No matching data 响应时返回空序列，并记录规范化 reason=no_matching_data；其余404（地址不存在、网关HTML等）保持错误。不得将所有404或所有非200统一吞掉。

验收：对上述真实响应建立fixture，断言SearchTool返回()；集成测试严格查询返回该404、后续放宽查询200命中时应继续得到候选。另测HTML 404、401、403、429与5xx仍归为真实故障，错误不得被当作零结果。

固定计划补充对照：第一组 NP-1 英文计划的3个编译查询，Springer返回24条候选、按 DOI/document_id 去重22篇；arXiv因429/熔断未返回候选。补充结果不混入第二组的16篇主流程候选中。

## P2：Web 查询长度约束未向模型充分暴露

第三组实测81、77单位查询触发 `query exceeds Baidu's 72-unit limit`，请求在本地被拒绝。后端校验本身正确，但 WebSearchArguments.query 仅声明非空字符串，工具描述未提供72单位规则（ASCII=1、非ASCII=2），失败会浪费工具调用预算。

方案：将长度规则写入已配置工具的query字段描述和工具schema；在发送请求前返回可纠正的结构化 validation error（当前units、max_units），由模型缩短/拆分查询。不要盲目截断布尔表达式或关键词。参数无效不应消耗网络执行预算，应设置独立纠错次数上限。

验收：72单位正常，73单位本地拒绝并提供可理解的修正信息；中英混合长度按相同算法计算；缩短后可恢复正常搜索且不会重置整个任务。

## P1/P2：Web discovery-only 配置与固定浏览获取提示不一致

第三组按控制变量仅打开web_search，browser保持默认关闭。因此Web来源可以发现和保存，但没有对应网页Artifact。这是配置能力边界，不能说web_search不可用。

实际观察：模型将Web source_record_id传给reader，得到unknown artifact_id；多次连续web_search后预算耗尽。`prompts/research/native_tool_loop.md` 固定要求每次web_search后调用browser并reader，却未按browser是否注册生成提示。

方案：构建时将能力清单与获取路径注入提示。browser缺失时明确声明Web只用于发现候选，不能直接reader(source_record_id)，也不能把snippet作为证据；允许转到可取得文献正文的数据库路径。如果业务目标是Web证据闭环，应显式启用browser并验证对应运行依赖，再测web_search→browser→reader→evidence→report全链路。没有为本次三组中途改变browser开关。

验收：仅web_search模式不得宣称可浏览，也不得调用未注册工具或把source ID当artifact ID；完整模式使用返回的ArtifactHandle进入reader并保存证据链；两种模式均须有界结束并在报告说明证据范围。

## P1：检索式在失败调用到报告之间丢失（用户补充问题）

**确认不是三个查新点没有生成计划，而是失败查询未进入报告。** 三组的每个查新点均有SearchPlan及数据库执行日志。

| 组别 | NP-1：报告式数 / 日志执行数 | NP-2 | NP-3 |
|---|---:|---:|---:|
| 1：arXiv | 0 / 6 | 0 / 14 | 0 / 12 |
| 2：加Springer | 1 / 16 | 0 / 6 | 1 / 7 |
| 3：再开Web | 1 / 8 | 0 / 11 | 1 / 13 |

报告式数是去重后的字符串数，日志执行数包含重复调用，二者用于定位遗漏，不作为去重命中率。第一组三点全部显示“无”；第二、三组NP-2显示“无”，但其日志分别有6、11条失败执行记录。熔断记录表示检索执行层接受了调用，不能声称一定发生了物理网络请求。

### 根因链

1. `workflows/research_task.py:_trusted_bundles` 第216行跳过所有 `observation.succeeded=False` 的工具结果，失败结果中真实存在的SearchExecution也随之丢失。
2. `persistence.py:persist_task_retrieval_audit` 第709行只遍历 `result.research_bundles[*].search_executions`，没有独立收集失败调用的审计记录。
3. `persist_retrieval_plans` 第603行只从上述执行集合生成 `query_plan.queries`，虽已保存完整 `search_plans`，但不用于说明计划状态。
4. `tools/renderer.py:_format_query_plans` 第245行只展示 `query_plan.queries`，空集合直接写“无”，没有区分“未规划”“未调用”“执行失败”。
5. Web查询目前也没有接入该报告段落；第三组虽然调用过Web，报告5.3仍仅呈现少量数据库查询。

### 解决方案

- 将**检索审计与可信证据收集分开**。新增独立的任务级query audit，从合法的数据库工具观察中收集所有SearchExecution，包括succeeded/partial/failed；保留point、task、attempt、provider、query、execution_id、status、error、时间及是否真的发起物理请求。
- 不要简单删除 `_trusted_bundles` 的成功过滤，避免把失败响应中的候选/制品直接当作可信证据。失败结果可以用于审计，不因此增加证据。
- 持久化按execution_id及调用上下文保留执行记录，展示时按point/task/provider/query分组，并保留多次尝试的状态；空结果和失败都必须展示实际查询。
- 报告按查新点列出：已生成的语义计划、实际数据库检索式及状态、实际Web查询及状态。没有调用时写“计划已生成，未执行”；发生错误时写“已尝试，失败原因…”，不能写“无”。语义计划的C1/C2表达式不应伪装成已发送的provider检索式。
- 无需让Coordinator模型重新编造检索式；直接从确定性审计产物渲染。真正未产生任何计划或执行记录时显式报告缺失并产生WorkflowIssue。

### 回归验收

1. 三点分别为成功有命中、成功零命中、429失败，报告均列出各点实际查询和对应状态；失败点不获得证据卡。
2. 一个点仅有语义计划但未调用provider，报告标记“未执行”，不能展示为“已检索”。
3. 只调用Web的点，报告显示Web查询及成功/本地参数拒绝状态；未发送请求不能算网络执行。
4. 多轮、同一task_id跨点、重复查询与多provider并存时，查询归属正确，不因全局去重丢失点/来源/尝试信息。
5. 本次原始日志回放应恢复表中的执行数；三份报告5.3不得再将这些有执行记录的点写成“无”。

### 已落盘的复核产物

- [report_query_audit.md](report_query_audit.md)：按查新点恢复实际数据库检索式、失败原因及原始日志链接；Web调用单独列出。
- [report_query_audit.json](report_query_audit.json)：机器可读审计数据。
- [audit_report_queries.py](audit_report_queries.py)：仅从原始产物恢复，无API请求。

原始三份报告保留作为复现证据；本次追加诊断与修复设计，未修改生产代码。
