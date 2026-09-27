# Novelty Framework Harness 与配置管理审查：阶段总结

整理日期：2026-09-28。对应本轮基线 `b378e44` 至发布验证提交 `da39ebf`；目标分支 `experiment/local-llm-baseline`。本文从三阶段试验记录提炼，不新增实验、不覆盖原始结果。

**结论：已经修复并验证若干确定性工程缺口，建立了配置与实验归档基础；原任务书整体验收仍未通过。** 现有结果不足以证明 Researcher 能稳定自主产出有效证据、Reviewer 能在充分材料下正确核验，或最终整合版本已改善整个查新流程。此前“探索审查完成”的表述已撤回，见 [验收状态纠正](20260927_harness_config_closure/acceptance_correction.md)。

## 1. 验收依据

原任务书第 8 节要求先完成“现象、证据、根因假设、验证实验、结论”，再完成“方案、实现、回归、消融”。每个重要改动需要说明具体失败模式、归属、动作自由度变化、实验条件变化和效果证据。

第 9 节观察同输入稳定性、查新点完整性、无效动作、Evidence 形成、Reviewer 核验、失败分类与恢复、Context、Token/成本、Harness 对模型差距的改善，以及配置复现与切换。一次 Workflow 的 `SUCCESS`、测试数量或目录名 `closure` 都不能代替这些能力验收。负面结果可以形成有效结论；尚未验证的核心问题不能全部标成 Unknown 后宣告任务完成。

## 2. 三阶段试验结果

| 阶段 | 主要观察 | 可以支持的结论与限制 |
| --- | --- | --- |
| 初始审查 | 历史轨迹有重复读取和 EOF 空读、请求超出上下文窗口、点去重丢失、Provider 错误误分类、未知成本显示不准确。初期 Reader 对照因模型连接失败未形成有效样本 | 失败同时来自工程、Provider 和语义判断，不能统一归因为权限或小模型能力。见 [初始审查](20260927_harness_config_audit/README.md) |
| 服务恢复后继续验证 | Reader off/on 各一次：模型调用 10→6、物理读取 8→4、独立读取字符均 3,026；0 replay、0 Card，耗时 23.571→34.573 秒 | 单样本少读不能证明稳定收益、缓存命中或提速。见 [续查记录](20260927_harness_config_continued/README.md) |
| 同阶段授权整流程 | 20 次本地模型调用；4 次物理 arXiv 搜索均 HTTP 406；0 Reader、0 Card；4 个点均无法裁定 | 已检查下游逐点记录，但外部检索失败阻断成证；无法评价充分材料下的研究与核验能力。见 [在线复核](20260927_harness_config_continued/live_validation.md) 与 [原始外层结果](20260927_harness_config_continued/original-live-run/README.md) |
| 后续 Reader 重复实验 | 仅真实摘要材料，off/on 各 3 次，共 30 次本地模型调用；每个样本 5 次模型调用、4 次物理读取，均 0 replay、0 Card、partial | 这组实验没有复现调用量或读取量下降，也不能证明证据质量提升。预算与前一单次实验不同，不能直接合并比较。见 [重复实验](20260927_harness_config_closure/reader_repeated_local.md) |
| 后续 Reviewer 实验 | 3 次实际材料实验共 9 次模型调用，实际均只选读摘要；引用合法，但 3/3 技术比较与结论不通过。修后使用 6 份冻结输出回放 | 证明引用合法不等于语义核验正确；冻结回放只验证限定规则，未验证修后真实模型在充分材料上的表现。见 [Reviewer 实验](20260927_harness_config_closure/reviewer_recovery.md) |

重复 Reader 实验的 `off_1` 另有实验脚本收尾异常：没有正常 summary/独立 trace sidecar，但原始模型、工具和阶段记录保留，未重发请求或补采样。这一偏差与样本 partial 状态均保留在原报告中。

所有真实本地模型实验使用已有 Qwen 服务，没有新增强云模型能力。后续阶段另有 4 次固定公共词的 arXiv GET，不能与前述整流程的 4 次论文检索混作同一实验；HTTP 406 根因仍未确定。见 [arXiv 故障分析](20260927_harness_config_closure/arxiv_failure_analysis.md)。

## 3. 按方面汇总实现与效果

| 方面 / 具体缺口 | 已实现的处理与动作边界 | 已有证据及尚未证明的部分 |
| --- | --- | --- |
| Context / 用量：窗口元数据未落实到请求；取消或解析失败可能漏账 | 对实际请求做显式精确计数准入，包含输出预留；保留失败及延迟到达的 usage，已知用量只记一次；未知报价与算力成本不填零 | [准入与计数](20260927_harness_config_continued/context_admission.md)、[用量核算](20260927_harness_config_closure/usage_accounting.md)。支持所测服务与故障场景，不等于通用上下文压缩或所有模型兼容 |
| Reader / Context：重复区间、EOF 和状态依赖模型自行回忆 | 可配置的精确重用、区间/EOF 状态、命名空间隔离；单独投影机械状态，保留原始历史。其他合法读取动作仍可用，模型 turn 仍计预算 | [状态投影](20260927_harness_config_closure/context_projection.md)。离线机械约束有证据；重复真实实验无净收益，投影未在该真实消融中开启 |
| 点完整性：形式合法的去重仍会误删技术机制 | 保守保留候选和字面特征，未核实的等价关系保持待核验，增加覆盖账本；收紧未经验证的删除动作 | [点覆盖](20260927_harness_config_closure/point_coverage.md)。固定 4 候选、24 个中英特征实例：原策略丢 12 项，保守策略丢 0 项，但完整性/语义覆盖标志仍为 false；不能证明从原论文开始没有漏提，也不以点数增加作为完整性证明 |
| Researcher：结束或汇总失败可能丢失已验证局部成果 | 新增显式 Evidence 检查点，经原 Builder 校验后保存；恢复时重新检查范围、来源与原文。提交和恢复仍受预算约束 | [检查点](20260927_harness_config_continued/evidence_checkpoint.md)。合成材料与受约束动作验证保存/恢复；尚无充分真实材料下稳定自主成证的正例 |
| Reviewer：技术失败与材料不足混淆、汇总失败覆盖局部事实 | 结构化失败和读证账本；显式且有界的汇总恢复；确定性检查引用、特征覆盖和结论绑定，不替模型判断技术等价 | [Reviewer 恢复](20260927_harness_config_closure/reviewer_recovery.md)。限定故障和冻结输出回归有效；真实正负例及充分材料核验仍待验证 |
| Provider：业务空结果误判故障，可选摘要补齐失败丢候选 | 精确识别 Springer no-data 响应；ScienceDirect 可选补齐失败保留已有命中并保留失败状态；区分传输、HTTP、未执行和材料问题 | [Provider 盘点](20260927_harness_config_audit/provider_findings.md)、[摘要补齐修复](20260927_harness_config_closure/sciencedirect_enrichment.md)。Springer 有限定在线证据；ScienceDirect/IEEE 不能因离线契约通过就称已在线可用 |
| Workflow / 报告：统一重试和失败包装掩盖实际缺口 | 按失败、材料和特征缺口选择有界恢复，约束 Provider/工具/计划范围；保留 partial 和失败事实，验证最终卡与逐点报告绑定 | [恢复与报告](20260927_harness_config_closure/recovery.md)。离线故障注入与路由回归有效；最终整合版本缺真实或固定外部观察的全流程对照。正式报告视觉和 PDF 版式未改 |
| 配置：隐式覆盖、Prompt 未实际绑定、入口预检不统一 | 统一有效配置、优先级与来源；Profile 控制角色/Provider/预算/模式；命名 Prompt 实际绑定；能力预检、输入/源码/配置冻结并接入正式入口 | [配置审查](20260927_harness_config_closure/configuration.md)、[Profile 使用说明](../../config/README.md)。入口与独立源码重建有验证；不能把后补离线快照当作早先 live 的启动快照 |

## 4. 按任务书分类的结论

- **已经验证解决，限已测场景**：若干 Provider 响应误分类、批量 Reader 与 Reviewer 诊断误报、失败/延迟 usage 核算、确定性配置预检与实际 Prompt 绑定、局部成果保存及有界恢复契约。
- **有所改善但仍存在**：查新点删除更可审计、候选保留更保守、机械状态更明确、恢复与报告事实更完整；语义覆盖、有效研究动作和整流程产出尚未获得充分效果验证。
- **确认属于模型能力边界**：目前没有足够受控证据确认剩余问题纯粹属于此类。历史强弱模型虽有相同论文输入，但代码、Prompt 与选项混杂，不能据此量化 Harness 改善比例。
- **仍然无法确定或未完成**：arXiv 406 根因、充分材料下的自主成证与正确核验、同输入整流程稳定性、修后 Context 与恢复的真实净收益，以及最终整合流程的可归因效果。

## 5. 用量与工程验证

用量按实验范围分别核对，不将局部合计冒充全任务总量：

- 续查阶段的整流程及 Reader 两组，共 36 次本地模型调用、188,116 total tokens；不含该阶段后续计数和检查点探针。
- 后续修复阶段共 39 次本地请求（Reviewer 9、Reader 30），235,350 输入 + 6,433 输出 = 241,783 tokens，逐调用与原始 usage 匹配。见 [用量范围](20260927_harness_config_closure/scope_accounting.json)。
- API 报价与本地推理资源成本未知，保持 Unknown / Unpriced；Token 可核对不代表货币成本已知。

发布前从 Git 导出独立目录，首次得到 **1,262 passed、1 failed、6 deselected**：一项测试依赖被忽略的本地 `outputs/` 输入。已把原输入逐字节保存为测试 fixture 并修复路径，重新独立导出得到 **1,263 passed、6 deselected、1 条既有弃用警告**。首次失败与复测日志均保留，见 [发布可复现性验证](20260927_harness_config_closure/publication_validation/README.md)。这只证明非在线回归，不替代原任务书能力验收。

## 6. 尚需完成的验收工作

1. 从原论文贡献及方法原文建立完整对照，追踪各项进入候选、任务、Evidence、Review 和报告的去向；不能只检查已提取的候选。
2. 用已知包含可引用相关材料的真实正例，以及不相关/材料不足例，验证 Researcher 自主读取、形成并保存 Evidence；明确材料、预算和干预条件。
3. 在同一材料基准上验证修后 Reviewer 的真实模型表现，覆盖充分、不足和技术故障，检查引用、逐特征比较、局部事实及最终结论。
4. 完成 Context/Reader/检查点等关键机制的真实有界消融，记录模型可见状态、必要材料、历史开销与停止/恢复；不能用冻结输出代替全部效果验证。
5. 冻结输入、配置、代码及外部材料/故障，对最终整合版本验证整条数据链与恢复行为，并核对同输入的重复稳定性。
6. 在可比条件下估计 Harness 的净改善；无法隔离的模型差距如实保留未知，不直接认定为小模型上限。

以上沿用原任务书，不追加“所有论文均成功”“全部 Provider 都接入”或“必须增加强云模型”等要求。完整映射见 [逐项验收复核](20260927_harness_config_closure/task_acceptance.md)。

## 7. 原始记录与版本

三阶段原始试验记录、失败样本、输入/配置/源码快照、运行日志和测试证据一并提交，入口见 [分阶段上传索引](20260928_harness_upload_index.md) 与 [提交范围清单](20260928_harness_upload_manifest.json)。原始输出与事后修订报告分开保存；外层补档的来源及 SHA-256 见 [原始运行归档](20260927_harness_config_continued/original-run-archive.json)。

试验归档包含用于复现的处理后论文正文和结构化输入。Python 缓存、零模型演示运行、本地任务书和用户已有的使用手册改动不在本轮提交范围。历史源码清单及补丁保持原采集时刻含义；最终发布源码另有 [清单与校验器](20260927_harness_config_closure/publication_validation/README.md)。
