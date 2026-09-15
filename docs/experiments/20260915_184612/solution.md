# MF2033k6lC：PaperInput 后三组真实实验与解决方案

## 1. 结论

**三组完整工作流均已完成并生成报告；流程完成不等于证据充分。**

1. **batch 合并有效，但当前 arXiv 限流仍存在。** 第一组10次物理API请求中6次429、4次超时，没有200。生产流程没有触发metadata调用；独立探测确认6调用/4不同ID合并为同一个id_list，首次请求后重试一次，仍收到超时和429。不能宣称补丁已经解决429。
2. **Springer Nature 确实扩张检索。** 第二组新增16篇数据库作品、4份全文文本。固定同一英文计划补充对照得到24条结果、去重22篇；这些补充文献不混入主流程统计。元数据404中的“No data”被误当故障，会阻断自动放宽链。
3. **web_search 工具真实可用。** 第三组成功调用39次，返回385条结果（含重复），保存227个独立Web来源。browser关闭意味着本轮仅验证Web发现能力，未完成网页获取→reader→证据闭环。长度校验错误及预算耗尽也真实发生。

开始：2026-09-15T10:13:12.069856+00:00；第三组结束：2026-09-15T10:44:17.537542+00:00。整理时间：2026-09-15T18:44:41+08:00（Asia/Shanghai）。归档结束时间：2026-09-15T18:46:12+08:00；目录名按该时间精确到秒。

## 2. 实验设计与复现条件

- PDF：[MF2033k6lC.pdf](input/MF2033k6lC.pdf)，原路径 `examples/MF2033k6lC.pdf`，90页。标题为“面向大规模动态图的图神经网络优化机制研究”。
- PDF SHA-256：`1fa48a8cb5d121220ba897a051b1468c2f0cefa211a0f5311c1d74c47aed8c79`。
- PaperInput SHA-256：`89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66`，三组完全一致。复用既有text_layer解析输入、91条参考文献；本任务从PaperInput后执行，没有重跑MinerU。
- 生产 `build_standard_full_workflow`，默认max_rounds=2、max_concurrency=4；保留生产Reviewer、Validator和报告完整性检查。未抽样任务，未修改生产代码。
- 仅切换provider及web_search开关；第一组仅arxiv，第二组加springer，第三组再开启百度千帆web_search。其他provider（含null_catalog）禁用；browser三组均关闭。
- 模型为项目配置的deepseek-flash，通过SiliconFlow调用；所有真实联网操作已获用户明确授权。配置、版本和完整产物均随目录保存。
- arXiv参数：共享scheduler、4秒间隔、200ms批窗口、最大32 ID、20秒请求超时、max_retries=1、45秒重试预算。
- 查新点原文对照见 [novelty_point_comparison.json](novelty_point_comparison.json)，实际配置差异见 [config_diff.json](config_diff.json)。尤其第二、三组NP-3变成边分割图流划分，而第一组NP-3是注意力融合，不能按相同NP编号直接比较证据覆盖。
- 每组重新执行查新点提取、计划及两轮上限研究；模型随机性导致计划/任务数量不完全相同。三组不是严格的固定计划A/B因果实验，固定计划补充对照用于单独验证provider扩张。
- 第一组自动刷新历史bootstrap；该轮90条failed、1条not_found，之后两组复用同一已刷新的快照。历史manifest仍含9篇缓存文献的问题见第5节。原始输入工作区未改写。

## 3. 三组主流程结果

| 指标 | 1：arXiv | 2：arXiv + Springer | 3：再开 web_search |
|---|---:|---:|---:|
| 流程返回 / 报告生成 | 成功 / 是 | 成功 / 是 | 成功 / 是 |
| 耗时（秒） | 516.03 | 606.97 | 467.8 |
| 轮次 | 2 | 2 | 2 |
| 查新点 | 3 | 3 | 3 |
| 任务 completed / partial / failed | 2 / 8 / 0 | 3 / 5 / 0 | 3 / 9 / 0 |
| arXiv 物理请求 | 10 | 6 | 6 |
| arXiv HTTP 200 | 0 | 0 | 0 |
| arXiv HTTP 429 | 6 | 0 | 4 |
| arXiv ReadTimeout | 4 | 6 | 2 |
| arXiv metadata 逻辑调用 | 0 | 0 | 0 |
| arXiv 间隔违规 | 0 | 0 | 0 |
| 外部数据库独立作品 | 0 | 16 | 16 |
| Springer source records | 0 | 16 | 16 |
| Web source records（去重） | 0 | 0 | 227 |
| 全文文本制品 | 0 | 4 | 3 |
| raw / validator / final证据卡 | 3 / 3 / 3 | 3 / 3 / 3 | 2 / 2 / 2 |
| 证据不足查新点 | NP-2, NP-3 | NP-1 | NP-1 |
| 模型调用 | 142 | 128 | 182 |
| API报告的total tokens | 975184 | 1034807 | 2432204 |

说明：数据库作品统计来自每组research references manifest，不含subject-reference池；Web source record尚未绑定work，不能与数据库作品数量混为同一指标。全文指已落盘extracted_text制品，不能用HTTP 200次数代替。第一组最终3张卡来自原参考文献缓存。arXiv统计包含该组bootstrap，第二、三组复用缓存不额外发起bootstrap请求。

- 第1组：[正式报告](01_arxiv/MF2033k6lC/report/MF2033k6lC-report.md) · [结果](01_arxiv/result.json) · [配置](01_arxiv/effective_config.json) · [arXiv统计](01_arxiv/arxiv_metrics.json) · [HTTP记录](01_arxiv/http_events.jsonl)
- 第2组：[正式报告](02_arxiv_springer/MF2033k6lC/report/MF2033k6lC-report.md) · [结果](02_arxiv_springer/result.json) · [配置](02_arxiv_springer/effective_config.json) · [arXiv统计](02_arxiv_springer/arxiv_metrics.json) · [HTTP记录](02_arxiv_springer/http_events.jsonl)
- 第3组：[正式报告](03_arxiv_springer_web/MF2033k6lC/report/MF2033k6lC-report.md) · [结果](03_arxiv_springer_web/result.json) · [配置](03_arxiv_springer_web/effective_config.json) · [arXiv统计](03_arxiv_springer_web/arxiv_metrics.json) · [HTTP记录](03_arxiv_springer_web/http_events.jsonl)

详细指标：[summary.json](summary.json)。每组目录同时包含模型调用、工具调用、runtime stages、LLM输入输出、研究任务结果、参考文献和报告。

## 4. 重点观察

### arXiv：429与batch效果

第一组所有429响应正文为 `Rate exceeded.`，调度事件未记录间隔违规。主流程metadata_logical_requests=0，因此不能从生产运行证明metadata合并是否发生。累计logical/physical比例还包含熔断拒绝，不能直接解释为batch压缩收益。

独立探测使用图学习相关4个arXiv ID，并让6个调用同步进入200ms窗口；两个ID重复。记录见 [batch/result.json](supplementary/batch/result.json)。两次物理尝试携带相同6个logical_request_ids及4个唯一ID，分别超时、429，6个等待者均正确收到失败。合并确实执行；没有无补丁同期对照，无法量化429发生率改善。

当前batch统计把重试当成新批次累加，故unique_metadata_ids=8、dedup_count=4、batch_count=2；真实逻辑值分别为4、2、1。需拆分逻辑批次与物理尝试，详见修复方案。

### Springer：结果扩张与错误分类

第二组Springer Meta API 3次200、11次404；Open Access 7次200，最终仅4份不同全文文本制品。检索命中、HTTP请求、独立文献与可读全文已分别统计。

[固定计划对照](supplementary/compare/result.json)复用第一组NP-1/T-2英文SearchPlan，以各provider自有QueryAdapter编译3个查询；全部变体均执行供对照，区别于生产命中后提前停止的路径。Springer每次8条，去重22篇；arXiv两项429失败、一项熔断拒绝。这证明当前运行条件下Springer带来可检索文献，不代表其对所有查询都比arXiv更好。

另复现第二组一个中文查询的Meta 404，正文明确为无匹配数据；见对照产物中的springer_404_diagnostic及http_events。当前程序将其标记ProviderRequestError并停止放宽链，是需要修复的真实语义错误。

### web_search：可用，但获取链缺口阻止证据转化

[web_summary.json](web_summary.json)记录成功/失败次数及原因。主流程已经真实调用工具并落盘来源，未另跑额外Web探测，也未使用助手自己的网页搜索工具代替项目工具。

```json
{
  "tool_statuses": {
    "FAILED": 16,
    "SUCCESS": 39
  },
  "returned_results_including_duplicates": 385,
  "unique_source_records": 227,
  "errors": {
    "web_search tool-call budget exhausted": 6,
    "query exceeds Baidu's 72-unit limit (88)": 1,
    "query exceeds Baidu's 72-unit limit (76)": 1,
    "query exceeds Baidu's 72-unit limit (81)": 1,
    "query exceeds Baidu's 72-unit limit (75)": 1,
    "query exceeds Baidu's 72-unit limit (113)": 1,
    "query exceeds Baidu's 72-unit limit (77)": 1,
    "query exceeds Baidu's 72-unit limit (85)": 1,
    "query exceeds Baidu's 72-unit limit (94)": 1,
    "query exceeds Baidu's 72-unit limit (96)": 1,
    "query exceeds Baidu's 72-unit limit (78)": 1
  },
  "browser_enabled": false
}
```

成功发现Web来源不等于证据获取成功。当前配置缺少browser，Web结果没有可交给reader的网页Artifact；模型仍有错误使用source_record_id读文档、连续搜索耗尽预算等行为。不能将这些后续失败描述为百度搜索API不可用。

## 5. 影响工作流和报告的bug及解决方案

下面问题均基于实际日志与本地复现。修复方案尚未应用到生产代码，以保留三组相同代码版本的可比性。


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

## 6. 验证、局限和归档说明

- 现有离线测试27项通过：[offline_tests.log](offline_tests.log)。覆盖arXiv scheduler、Springer provider、web_search；这些测试未覆盖本次发现的所有集成缺口，不能替代真实实验。
- 三组报告均检查存在且流程返回SUCCESS；证据质量必须另看各点不足项及检索降级。报告中出现的无条件“新颖”不能在外部检索失败背景下直接采信。
- 初次沙箱网络权限失败与后续审批拒绝保存在sandbox_start_failure及早期记录中，不计作三组实验，也不计入真实429统计；用户确认后已正常完成联网实验。
- 使用 `run_trial.py 1/2/3` 从仓库根目录启动（Python解释器为 `/home/lya3106643285/miniconda3/envs/Novelty/bin/python`）；该脚本针对本次目录运行，会写对应组别目录。要复跑应先复制脚本与input到新的实验目录，避免覆盖本次档案。
- `probe_tools.py batch/compare` 是独立补充探测；web模式已准备但未执行，因第三组已充分验证真实工具调用。`summarize.py` 可重新汇总原始产物，`write_solution.py` 可生成正文；诊断原文见diagnosis_notes.md。
- 归档时目录以结束时间重命名。原始日志中的绝对路径保留运行时原值；用path_mapping.json映射到当前目录，以上报告链接均为当前相对路径。原始来源观测、请求时间与错误未改写。
- 全部文本产物检查已配置凭据是否泄漏，结果见credential_scan.json；实验脚本不保存请求授权头和Springer请求中的api_key。文件清单及SHA-256见artifact_inventory.json。
