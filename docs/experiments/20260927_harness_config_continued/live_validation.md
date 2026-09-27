# 服务恢复后的全流程与 Reader A/B 复核

日期：2026-09-27。复核方式：读取已完成运行及其配置、LLM/tool/provider 日志，不新增网络或模型请求，不改原产物。随后对新发现的报告原因传递缺口进行了最小代码修复和离线重绑，见第 7 节。机器可读结果见 [live_metrics.json](live_metrics.json)，其中保存 88 份来源文件的 SHA-256。

本轮全流程正常结束并生成报告，但没有得到可裁定的新颖性证据。Sketch-DBH 已进入后续研究链路；这证明它不再被这次非法去重链静默删除，不能证明贡献完整性已经恢复。Reader A/B 观察到开启状态机制后重复读取较少，但两组都没有 replay、没有有效 Card，且开启组耗时更长，不能归因于缓存 I/O 或宣称语义质量提升。

## 1. 本轮全流程：完成状态与逐点链路

原始运行：`outputs/harness-config-audit-continued/0001/`，Runtime ID 为 `run-d55196716d254641a84cf1b0c19f14e9`。输入 paper SHA-256 为 `89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66`。外层耗时 91.900473 秒，Runtime 计时 91.665 秒；实际执行的 20 个 stage 均结束为 `SUCCESS`，另有 `plan_supplement` 被记录为 `NOT_RUN`；最后阶段是 `render_report`。

| 点 | 实际提取范围 | Task / SearchPlan | 实际数据库搜索 / 未执行计划项 | Reader / Card | Review → Report |
| --- | --- | --- | --- | --- | --- |
| NP-1 | GSAERU 节点表示学习；2 条特征 | T-1 英文任务，各 1 份 | 1 次 HTTP406 / 5 项 not_run | 0 / 0 | insufficient_evidence / material_unavailable → 同状态，verdict=null |
| NP-2 | Sketch-DBH 边分割、Count-Min Sketch 与最小堆；2 条特征 | T-1 英文任务，各 1 份 | 1 次 HTTP406 / 3 项 not_run | 0 / 0 | insufficient_evidence / material_unavailable → 同状态，verdict=null |
| NP-3 | GSAERU 训练效率与性能差距实验描述；0 条特征 | T-1 英文任务，各 1 份 | 1 次 HTTP406 / 3 项 not_run | 0 / 0 | insufficient_evidence / material_unavailable → 同状态，verdict=null |
| NP-4 | DSGNN 实现三个分布式模型的实验描述；0 条特征 | T-1 英文任务，各 1 份 | 1 次 HTTP406 / 5 项 not_run | 0 / 0 | insufficient_evidence / material_unavailable → 同状态，verdict=null |

四个研究 attempt 均记录 `status=completed, steps_used=3`，实际各调用一次 `database_search` 和一次 `reference_search`。数据库搜索全部执行失败；reference_search 为本地查找，四次执行成功但为空。不存在返回成功且确认“无匹配文献”的数据库搜索。全部 raw Evidence、raw Card、Validator 接受 Card、最终 Card 都是 0，候选列表为空。

四个点均进入报告，报告没有丢点、没有伪造新颖性 verdict；引用完整性校验通过，结论与 Review 对齐 4/4。`check_final_evidence_sufficiency` 同时明确四点全部不足，配置的一轮上限禁止继续补查。这些事实说明报告正确保留了未完成裁定状态；stage/run 的 `SUCCESS` 不是查新成功。

## 2. 失败分类

| 观察 | 分类与边界 |
| --- | --- |
| arXiv 四次返回 HTTP406 | Provider HTTP/协议层技术失败。不能解释为正常空结果、文献不存在或已经证明权限不足。406 根因仍未定。物理事件的 `error_type=null` 也不抹去其 HTTP406 状态。 |
| Researcher 四份 `no evidence` 警告说未找到论文、剩余预算不够 | 是模型给出的停止解释。每任务只执行 2 个工具调用，配置上限为 24；全局实际模型调用 20/40、物理请求 4/12，未记录全局预算触发。因此该措辞不能替代真实 Provider 失败原因，也不能证明所有预算耗尽。 |
| 全流程 Reader 为 0 | 检索没有获得可读候选，因此下游未执行。不能归类为 Reader 失败或评价 Reader 修复效果。 |
| Reviewer 四个 `material_unavailable` | 无已绑定材料时的规则路径，实际 Reviewer stage 模型调用为 0；不是 Reviewer 模型推理失败，也不是文献新颖性裁定。 |
| report integrity 通过但零证据 | 输出对齐与闭包检查通过；仍不满足最终证据数量阈值。 |
| 去重错误映射及无特征补核点 | 提取/语义范围未核实，见下节；不能与上游 HTTP406 混为同一故障。 |

报告表达的专项检查：渲染报告 §5.3 已对四条实际检索逐条标出“arxiv；执行失败”，§7 四点均为“核验未完成，无法裁定”。因此未发现把技术失败包装成“零命中”“无相关文献”或否定性科研结论。四个 `material_unavailable` 正确描述 Reviewer 的直接材料状态，但不完整表达上游故障原因。

报告仍有可定位的原因传递缺口：正文未出现 HTTP406，没有直接说明四点无材料由 arXiv 请求失败导致；§8 固定写“本报告节点输入未提供完整检索执行事实，检索覆盖状态未知”。实际工作流 state 和落盘 ResearchTask 已有 `search_executions`。`workflows/novelty.py::_synthesize_report`（约 984 行）只把 Review/Card 等传给 Coordinator；`core/report_binding.py:71` 固定加入未知覆盖句；`tools/renderer.py:269` 只把 failed 映射成“执行失败”，没有显示 query.error。

最小后续建议：在工作流绑定报告时，从现有结构化 SearchExecution 确定性汇总每点 Provider、实际失败次数/HTTP 状态及 not_run 数，并加入报告 limitations，例如“arXiv 搜索 1 次因 HTTP406 执行失败，未获得材料，另有 5 项未执行；不能据此推断无相关文献”。保留 Reviewer 的 `material_unavailable`，不改 verdict、不让模型猜根因、不把原始异常全文或带凭据 URL 直接拼入用户报告。这是原始 live 报告的缺口；后续已按该方案最小修复并离线重绑，见第 7 节。原始 live 报告仍保留，不能把 amended 结果当成重新执行全流程。

## 3. `pending_dedup` 的四点到底恢复了什么

`diagnostics/point_extraction_trace.json` 记录的初始候选只有三项，依次是 GSAERU、DSGNN 框架、Sketch-DBH。去重模型给出 `2→1`、`3→2`，两条理由均直接复用“技术目标、机制和范围等价的具体依据”模板。

Harness 接受 `2→1`，因此初始 DSGNN 框架候选被删除；`3→2` 因代表项 2 同时被删除而违反契约，被拒绝，记录 `representative_also_marked_for_deletion:3` 与 `pending_indices=[3]`。Sketch-DBH 因而被保留。补核又提出 GSAERU 和 DSGNN 的两条实验结果描述，合并后得到最终四点；trace 为 `scope_status=pending_dedup`、`semantic_equivalence_verified_by_harness=false`。

此次有实据支持的改善是：Sketch-DBH 的 Count-Min Sketch/最小堆特征保留在 NP-2，并真的进入 T-1、SearchPlan、一次物理搜索、Review 和报告。它恢复了后续核验机会。

尚不能宣称贡献完整性修好：原 DSGNN 框架的工作节点小批量学习、图摘要子图等机制没有作为独立技术点保留；NP-4 只是分布式实验描述，并无 technical_features，不能替代原框架。NP-3/4 的独立贡献资格也未确认。`target_reached` 和点数从 2 变成 4 都不是语义覆盖通过的证据。

## 4. 实际模型与 Provider 边界

全流程逐份核对了 **20** 份 `llm_calls`：全部记录 `model=qwen2.5-7b-instruct`、alias=`local-qwen2.5-7b`、endpoint=`http://127.0.0.1:8000/v1/chat/completions`，20 次均成功；输入 71,360 token，输出 3,613 token，合计 74,973。分布为提取 3、SearchPlanner 4、Researcher 12、报告合成 1。没有 Reviewer 模型调用，没有云端模型 endpoint。价格记录为 UNPRICED/PARTIAL，不能把缺报价写成免费。

Reader A/B 的 off 10 次、on 6 次也逐份核对为同一个本地 Qwen endpoint，均无失败模型调用。因此本次三份新样本共 **36** 次已记录模型调用均是本地 Qwen 请求。结论基于实际调用日志；未独立检查服务端所装载权重。三份新样本合计输入 **182,722**、输出 **5,394**、总计 **188,116 token**；成本金额仍为 unknown/unpriced，不是已确认的零成本。

全流程 Provider 目录有 8 份事件，必须区分 **4 logical + 4 physical**，不能相加声称发了 8 次请求。全部 physical event 都是 `provider=arxiv, operation=search, transport=api, status_code=406`，每点一次，无重试。将同 point 的 SearchExecution HTTP 异常 URL 与 physical scope 关联后，四次请求主机均为 **`export.arxiv.org`**、路径均为 `/api/query`。Runtime 预留物理请求数也是 4，未超过本轮预算 12。

| 样本 | 记录的物理 Provider 请求 | 目标主机 | 是否处于本轮 arXiv 范围 |
| --- | --- | --- | --- |
| 全流程 | 4 | export.arxiv.org | 是 |
| Reader state_off | 0 | 无 | 是，无新增 Provider 请求 |
| Reader state_on | 0 | 无 | 是，无新增 Provider 请求 |

未发现其他 Provider、web_search 或 browser 执行。effective-config 中远端模型/禁用 Provider 的声明、论文链接、HTTP 异常中的 MDN 帮助链接都不是物理请求。此核对依据应用 telemetry 和对应 HTTP 错误 URL，不是网络抓包；physical event 本身没有 endpoint 字段，所以机器指标中逐条保留了主机的证据来源。

## 5. 服务重启后的 Reader A/B

来源：[reader_local_pair_restarted/validity.json](reader_local_pair_restarted/validity.json)、[state_off.json](reader_local_pair_restarted/state_off.json)、[state_on.json](reader_local_pair_restarted/state_on.json)。这是仅暴露 Reader 的单任务冻结输入实验，不包含新的检索、完整 Reviewer 或新报告。`fixture/` 里的两点报告是历史输入副本，不能算成本次 A/B 的报告输出。

两组输入 hash 均为 `05605b0711abed8365f326e6fad97cec098da3176604406322788528d9971099`；温度 0、max_steps=10、max_tool_calls=8、Reader 预算和基础提示配置相同。配置开关 `reuse_reader_results` 改变的不只有 exact-request replay，还会向后续模型请求附加 Reader state。实际 on 有 **4** 份模型请求包含该状态提示，off 为 0；不能将此称为只改变底层缓存 I/O。

| 指标 | off | on |
| --- | ---: | ---: |
| Runtime 耗时 | 23.571 秒 | 34.573 秒 |
| 模型调用 | 10 | 6 |
| 输入 token | 75,976 | 35,386 |
| 输出 token | 426 | 1,355 |
| Reader 真实执行 | 8 | 4 |
| Reader replay | 0 | 0 |
| Reader 空结果 | 0 | 0 |
| PRE_TOOL 预算拒绝 | 1 | 0 |
| 唯一 read_id | 3 | 4 |
| 唯一 artifact | 3 | 3 |
| 返回总字符 | 7,873 | 3,325 |
| 区间去重覆盖字符 | 3,026 | 3,026 |
| 有效 Evidence / Card | 0 / 0 | 0 / 0 |
| 任务状态 | partial | completed |

off 重复读取相同三个摘要，8 次真实执行之后第 9 次 Reader 请求在 PRE_TOOL 被预算拒绝；on 读取三个摘要后又读了一段与既有区间重叠的尾段，因此虽然有 4 个不同 read_id，独立材料和覆盖字符没有增加。两组均未读取全文。

on 尝试提交的引文不能在实际 Reader 材料中匹配，生产 EvidenceCardBuilder 拒绝原稿及一次引文修正，最终仍为 0 Card；`completed` 仅是工具循环结束。off 则因预算停止，最终也为 0 Card。开启组减少了重复执行和输入 token，但墙钟时间从 23.571 增到 34.573 秒，不能写成提速。

两个样本均为 0 replay，因此本轮没有观测到缓存复用节省 I/O 的直接效果。观察到的行为差异与状态提示/后续生成路径同时变化，每条件只有一次，尚不足以证明稳定性、因果净收益或 Reviewer 质量改善。

## 6. 历史两点基线仅作观察对照

旧运行：`outputs/local-llm-full-workflow/0002`、`run-f41ac741cf6f49deaa52124ae5b23903`（2026-09-24）。paper hash 相同，最终只有 GSAERU 与 DSGNN 两点，Sketch-DBH 在旧提取去重阶段丢失。旧运行 30 次 Qwen 调用、输入 226,576 token、输出 3,204 token、外层耗时 119.253821 秒；Reader 16 次成功、1 次 PRE_TOOL 失败，最终两点同样没有有效裁定。

新运行 4 点、20 次模型调用、91.900473 秒，不能据此认定新 Harness 导致端到端成本/耗时下降。旧/新代码、去重提示、预算（80/48 → 40/12）、检索上下文和取得的可读材料均不同；新运行根本没有进入 Reader。两次全流程都是零有效 Card/无新颖性 verdict，只能作为可审计的历史观察对照。


## 7. 报告执行事实绑定的最小修复与 amended 产物

父任务确认这是新 live 的确定性缺口后，修改 `core/report_binding.py` 和 `workflows/novelty.py`：在 Coordinator/Reviewer 绑定之后，读取现有 `TaskResearchResult.search_executions`（含兼容的 bundle 内记录），按 point/provider 汇总成功、失败、未执行、部分成功及需人工处理状态；同一逻辑执行在扁平与 bundle 两处出现时去重。数字代表 SearchExecution，不冒充物理 HTTP 请求数。

只有错误中明确的 HTTP 状态数字进入报告；原始错误正文、URL/参数不复制到用户报告。存在执行事实时移除不适用的固定“未提供完整检索执行事实”；无执行事实时仍保留覆盖未知，部分点缺失则逐点标注。执行失败不转为 NOT_FOUND 或零命中，Reviewer 的 `material_unavailable`、verdict 和所有已核验字段保持原值。

离线产物：

- [amended Markdown 报告](amended-report/MF2033k6lC-report.md)
- [amended 结构化报告](amended-report/report.json)
- [仅 limitations 的可审查差异](amended-report/report-limitations.patch)
- [来源 hash 与修改证明](amended-report/amendment.json)

离线重绑再次核对了原始 88 份来源文件 hash，全部保持一致。结构化报告唯一变化字段是 `limitations`；四份 Reviewer conclusion 完全相同，原报告显示时间也保留。amended 明确显示 NP-1/4 各失败 1 次、未执行 5 项，NP-2/3 各失败 1 次、未执行 3 项，均为 HTTP406，并明确不能推断无相关文献。该步骤没有模型调用或网络请求。

定向与相邻检查：report binding/narrative/workflow/resources **46 项通过**，覆盖 all-fail、mixed、no-executions、bundle 去重、scope 隔离、错误参数不外泄及工作流接线。全套第一次发现旧 Gate A 测试把“限制列表必须为空”误当作隔离目的；更新为允许唯一真实覆盖未知提示，并明确禁止 gate-only、ev-missing、missing Evidence 出现在报告，随后 integrity gates + binding **33 项通过**。日志分别为 [report_search_coverage_tests.log](report_search_coverage_tests.log) 和 [report_gate_coverage_tests.log](report_gate_coverage_tests.log)。最终全套结果由主任务统一记录；上述两批用例有重叠，不相加作为独立测试总数。

## 8. 全流程源码复现边界

本轮 full run 保存了 dirty commit、Python 源码整体 fingerprint、完整有效配置和输入身份，但没有在 full run 开始时单独保存源码 patch。其他 agent 在运行期间继续修改未启用的 guard/checkpoint 模块，因此最终累计 patch 不等于该次 live 开始源码。整体 fingerprint 能识别差异，不能单独重建差异内容；不能声称 full run 的精确起始代码已可重建。

Reader A/B 则有自己的 `implementation_at_start.patch`。它也只支持该 Reader 单任务样本的实现追踪，不能替代 full run 起始 patch。后续新增或未启用的配置/guard/checkpoint 路径没有被这次 full live 验证；本轮不能宣称增强配置已经全部通过端到端验收。历史 manifest 保持不变。
