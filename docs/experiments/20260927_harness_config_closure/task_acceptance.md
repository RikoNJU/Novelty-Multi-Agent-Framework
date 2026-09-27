# 原任务书逐项复核：尚未通过整体验收

日期：2026-09-28。依据[原任务书](../../../task/Novelty%20Framework%20Harness%20与配置管理系统审查任务定义.md)，综合 audit、continued、closure 三阶段证据。

**任务部分完成，尚未通过整体验收；撤回此前“探索审查已完成”的收尾判断。** 已交付的是局部修复、限定验证与实验记录。根据用户再次复核要求，原任务第8、9节仍缺充分真实材料下的能力验证、修后真实消融和整合流程证据。负面结果可以构成调查结论，但验证对象未覆盖不能仅靠标记Unknown或“科研效果未通过”视为任务完成。详见[验收状态纠正](acceptance_correction.md)。

最终整合版本非 live 回归 **1,263 passed、6 deselected、1 条既有 Starlette 弃用警告，30.32 秒**，见 [完整日志](full-tests.log)和[机器结果](full-tests.xml)。各分项测试有重叠，不相加。旧阶段结果保持原样，旧 full 缺少启动时源码的限制也没有被事后快照补写。

## 3：Harness 逐项核对

| 条款 | 完成交付与直接证据 | 限定结论 |
| --- | --- | --- |
| 3.1 小模型压力测试、强弱 differential | [历史轨迹对比](../20260927_harness_config_audit/harness_findings.md)、[完整性审查](../20260927_harness_config_audit/integrity_findings.md)；同论文输入hash核对；新增[Reader六样本](reader_repeated_local.md)、[Reviewer三样本](reviewer_recovery.md) | 强模型也有机械重复；历史条件混杂，无新增云对照，不能量化净性能差距 |
| 3.2 不必要自由度 | [机械状态投影](context_projection.md)、Reader区间/EOF/必读门控、Builder checkpoint、[受限恢复动作](recovery.md) | 预算、已读、Provider状态与次数交给程序；保留语义选文、特征比较、检索方向和合法重读。状态明确区分Builder接受与最终验证 |
| 3.3 工具/Provider能力 | [注册、参数、材料、认证矩阵](../20260927_harness_config_audit/provider_findings.md)、[错误目录与操作映射](recovery.md)、[错误工具选择对照](tool_choice_before_after.json)；Springer特定404和[ScienceDirect补齐](sciencedirect_enrichment.md)修复 | 区分认证/授权/协议/网络/限流/服务/资源/全文/策略/参数/工具不可用，未知原因不猜；错误选工具可返回明确拒绝，不再在投影阶段二次崩溃 |
| 3.4 数据库调查 | [现有与候选表](../20260927_harness_config_audit/provider_findings.md)覆盖arXiv、Springer、ScienceDirect、IEEE、ChinaXiv、OpenAlex、Crossref、Semantic Scholar、万方、知网、机构、专利及科技成果材料 | 已实现/禁用/离线验证/凭据不足/部分能力/预留/未接入分开，说明覆盖、授权成本、成证材料及优先级；本轮没有追求接入数量 |
| 3.5 查新点生命周期 | [候选覆盖账本与固定holdout](point_coverage.md)；[point_lifecycle到报告](recovery.md)区分提取、任务未建、计划/结果缺失、无有效卡、Review/Report遗漏 | 固定反例原24个中英特征实例丢12项→全部保留；不同claim未证实等价则pending。贡献语义完整及独立性仍未确认，点数不是质量 |
| 3.6 Researcher/Evidence | [机械规则](../20260927_harness_config_audit/harness_findings.md)、[严格checkpoint](../20260927_harness_config_continued/evidence_checkpoint.md)、[六次真实摘要探针](reader_repeated_local.md) | 已提交Builder结果可在中断后保留/显式恢复；六次均0卡、partial，不能证明自主可靠产证据或及时提交 |
| 3.7 Reviewer | [失败分类、单卡保存、单次summary恢复、固定真实材料核验](reviewer_recovery.md)；[报告partial来源验证](recovery.md) | 3次真实材料均有语义不一致；6份冻结card/summary输出经窄规则拒绝欠支持的not_novel，局部结果保留。不是修后新模型准确率，不把所有不确定结果统一失败 |
| 3.8 Error taxonomy | [实际目录](failure_catalog.json)、[字段、生产映射、因果去重及恢复含义](recovery.md) | code不只是异常名；scope、retry上限、恢复/人工/停止、结论影响受约束；未识别异常保留unknown，不产生科学结论 |
| 3.9 定向恢复 | [同输入故障分流与工具约束](recovery.md)、[121项相关回归](recovery-tests.log)、最终全套 | 区分补读、按已有句柄获取全文、语义补检、原计划换源/一次重试、仅恢复summary、停止；不重复失败句柄、不突破原Registry/预算。真实多Provider fallback E2E未验证 |
| 3.10 Context | [精确准入/真实token核对](../20260927_harness_config_continued/context_admission.md)、[长轨迹投影](context_projection.md) | 每次只替换一条机械状态，保留原始轨迹/provenance和任务隔离；max_turns及显式context enforce形成边界。投影有额外输入开销，不是语义压缩，也不保证超限后完成 |
| 3.11 Runtime | [继续/停止/补检原因、历史cause及报告绑定](recovery.md)，含卡数PASS仍需语义补检的真实路由；Reader/Reviewer诊断契约回归 | 模型自称预算不足不是实际预算耗尽。运行SUCCESS、日志合法或诊断OK都不证明科研结论正确 |
| 3.12 Token/Cost | [历史及continued核对](../20260927_harness_config_continued/README.md)、[取消/解析失败漏账修复](usage_accounting.md)、[本轮39次逐调用账](scope_accounting.json) | 同call精确一次，晚到usage更新归档，失败状态保留；本轮241,783 tokens。无usage、未定价、GPU成本与实账均可Unknown；未分别报告cached/reasoning不代表无相关算力 |

## 4：Configuration Management逐项核对

共同证据：[配置闭环](configuration.md)、[修前/后](configuration_after.json)、[独立进程重建](configuration_rebuild.log)、[使用说明](../../../config/README.md)、[最终有效配置](final_configuration_manifest.json)。

| 条款 | 实际交付 | 验收边界 |
| --- | --- | --- |
| 4.1 单一有效配置 | 模型/端点/window/能力、角色选项、Prompt版本hash、Provider、预算、入口、并发、轮次、flags及字段来源 | 正式入口已接，凭据仅存引用；不保证外部服务当前健康 |
| 4.2 优先级 | schema→分片→profile→支持的env→显式override；typed timeout不再被factory暗改，legacy实际来源留账 | isolated-config阻止配置env覆盖；不等于清空凭据/外部处理器环境 |
| 4.3 实验Profile与复现 | 本地/远端/Reader/guarded及新增closure示例；每次启动保存源码内容、Prompt/模板/技能、依赖、输入与有效配置，逐文件hash | 独立源码重建通过；不冻结远端权重、服务tokenizer、Provider返回、外部MinerU或随机输出；不修补旧full缺失的启动源码 |
| 4.4 模型切换 | 五角色alias、timeout/token/window/thinking/endpoint；tool_calling/json_object/vision三态、tool_choices与声明依据 | 未知必需能力在启动前拒绝；没有追加强云模型证明性能；OCR vision只为官方文档声明，非live |
| 4.5 Provider切换 | 局部注册适配、启停/认证/限制、单多源profile、显式recovery_provider_order | 默认空；只接受已启用非testing来源，不自动开新库；在线可用性和授权不能靠有key推断 |
| 4.6 Harness参数实验 | 调用/阅读/轮次/并发/timeout、Reader/checkpoint/context/projection、保守去重等配置化，typed/legacy接线 | 每个参数的算法效果需独立实验；Reader开关含状态提示和重放，不是纯I/O缓存干预 |
| 4.7 模式入口 | 标准Full、PaperInput、SingleTask、Web PDF、Service共享预检与构造；只校验实际使用角色/processing | 低层组合工具、历史脚本仍有兼容边界；未来所有Reviewer-only/Replay产品入口非本轮必建 |
| 4.8 运行前验证 | 未知来源、凭据、能力、参数、预算/窗口、Prompt、processing、OCR开关、恢复顺序在外部调用前检查 | 静态window不是精确token准入；凭据存在不是授权成功；无法预知临时406 |
| 4.9 Runtime/脱敏 | 有效配置、字段来源、启动manifest、输入/Prompt/源码hash和环境版本与结果关联；源码快照不拷.env | [最终扫描](secret_scan.json)检查已知密钥未泄漏，但不是任意秘密不泄漏的证明；远端tokenizer版本未探测就明确not_probed |

## 5–8：结构、报告和工作方法

- **结构/解耦：** 改动沿既有组合根、Provider适配器、Harness及数据契约进行。各报告说明具体failure、减少的机械自由度与代价；没有为代码美观改写系统。模型和已实现Provider、暴露参数切换无需改业务源码；新Provider仍需局部实现。
- **报告冻结：** 未改视觉/PDF版式。增加机器契约、既有limitations事实和局部结果；最终Gate A剔除的卡不能经partial回流，Gate B审计原Evidence及增量读闭包。没有将执行失败包装成“没有相关文献”。
- **探索边界：** 全部新增推理使用本地Qwen；没有隐式更强模型/云回退。未删失败点、未降低Builder/Reviewer来源标准。摘要、合成checkpoint探针、冻结输出回放、在线全流程各自标明。
- **方法：** 重要修复有现象、原始证据、限定假设、修前反例/故障注入、修复与回归。Reader重复实验的runner收尾错误、未重发样本及缺少正常summary的边界原样保留。最终源码补丁和新冻结目录与每次live启动快照分开，禁止事后改写实验条件。

## 9：科研效果最终判断

| 验收问题 | 实际结论 |
| --- | --- |
| 相同输入是否稳定 | 整体未证明。Reader off三次3026唯一字符；on为4112/3026/3026，轨迹有波动；n=3/条件不作泛化。Reviewer三次错误不能称稳定正确 |
| 查新点是否完整 | 候选/特征机械保留改善；作者全部贡献、技术组合及独立性语义仍未通过 |
| Researcher是否减少无效行为 | 六次均5chat、4物理读、0replay；on重复字符少，但调用/IO次数无改善，平均耗时也不支持加速 |
| Evidence是否可靠形成 | 未通过。六次均0卡；这也不等于模型错误或无相关文献，材料仅为摘要，允许证据不足时保守不产卡 |
| Reviewer是否正确用证据 | 来源/引用、局部保存和必要覆盖规则通过限定工程验证；三次真实材料语义不通过。修后只做固定输出回放 |
| 技术失败是否准确分类 | 已列HTTP/transport/材料/模型/context/参数/策略/预算故障通过限定回归；未知异常不强行归因 |
| 是否合理恢复 | 离线总图分流、动作范围、一次次数、原计划、因果与显式checkpoint恢复通过；没有新的在线多源恢复E2E |
| Context是否可控 | 选定投影/隔离/有界停止与精确准入成立；默认off需要实验profile明确开启，长任务成功仍未保证 |
| Token/成本是否可核对 | 本轮39/39实际usage逐条匹配，共235,350输入、6,433输出；API价格与本地算力成本Unknown |
| 强弱差距有多少由Harness改善 | Unknown。历史混杂，本轮没有同条件强模型对照；不能将所有剩余失败归为小模型能力边界 |
| 实验能否固定配置复现 | 新源码/配置/输入构造可重建，真实局部实验有独立启动副本；不承诺随机输出重现或旧full源码可追补 |
| 模型/Provider/Harness/模式能否配置切换 | 已公开配置面及正式入口通过；未知能力明确拒绝，未实现Provider或新算法仍需开发 |
| 改配置是否无需改业务源码 | 现有公开配置面成立；不是对任意未来功能的保证 |

## 最终四类结论及交付边界

**已验证解决：** 特定Springer业务404、ScienceDirect可选摘要补齐丢候选；取消/解析usage漏账；材料/越权误分；summary局部保存与严格显式恢复；必要覆盖矛盾；未注册工具投影崩溃；配置/超时来源漂移、能力预检与源码内容缺失；原按卡数补检误路由和报告来源旁路。各项只在所列边界内成立。

**改善但仍存在：** 候选不静默丢失、机械状态可见、已有局部成果可恢复，然而贡献语义、自主产卡、长研究成功与跨论文稳定性仍未通过。开关在配置中存在不构成效果证据。

**模型语义残余：** 摘要未提及被写成“未采用”、unknown仍给not_novel、合成原文出现不支持的技术解释。它们是实际输出反例；本轮没有排除全文未读、提示/动作策略等所有因素，**没有足够证据把剩余问题确认为模型固有能力上限**。

**Unknown/受限：** arXiv406细因、缺凭据/机构条件的来源、全文授权和费用、GPU成本、强弱模型净差距、完整作者贡献与跨论文泛化。调查以证据限定Unknown收尾，不靠更多测试数或SUCCESS状态替代科研标准。

最终工件：[完整测试](full-tests.log)、[恢复回归](recovery-tests.log)、[六样本](reader_repeated_local.md)、[Reviewer](reviewer_recovery.md)、[Context](context_projection.md)、[调用范围/用量](scope_accounting.json)、[源码/补丁索引](source_inventory.json)、[密钥扫描](secret_scan.json)。本轮闭环39个本地chat、4个固定公共arXiv GET，无新论文检索或云模型调用；前两轮分散探针没有完整统一物理计数账，不能将历史242次与采样账相加冒充整个任务总数。

最终整合版本未追加在线全流程；已授权的一轮论文arXiv full仍是continued原记录。新的验证采用冻结真实材料的局部重复与离线总图故障注入。这些材料构成当前阶段成果，尚不足以宣布整份探索审查完成；后续工作按原任务验收要求继续。
