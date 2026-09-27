# 业务失败、定向恢复与报告闭环

日期：2026-09-28。本分项使用固定离线响应与故障注入，不调用模型、数据库或新网络服务。它验证确定性边界，不能证明在线检索已经恢复或小模型能够可靠产卡。

## 修前证据与选择

`recovery-before.log` 保存两个实际失败断言：全部查询 HTTP 406、没有可用替代来源时，总图仍按卡数触发补检；卡数达标而 Reviewer 明确指出技术特征缺证时，总图却停止补检。原“卡数不足→Coordinator 再建任务”的自由度不足以表达这些不同原因。

新策略保留卡数阈值原义，不把卡数当证据充分性。模型仍负责语义检索方向、文献理解、特征比较和证据选取；系统从真实执行事实决定是否值得新检索、可用材料句柄、操作类型和追加次数。任务拆分、失败因果、次数消费与工具约束不再由模型自由解释。

## 契约与生产映射

`schemas/failures.py` 是独立版本化契约。`FailureEvent` 含 code、layer、category、paper/run/point/task/attempt/card/artifact/provider/feature scope、execution_status、固定的 semantic_status=not_adjudicated、retry 上限、recovery、conclusion_effect、证据引用与 cause_event_ids。目录校验层级、类别、允许动作、重试上限与需要变更输入的修复；错误事件绝不创建新颖性标签。

事件 ID 来自 code+scope+occurrence 的确定性摘要，重复观测按 ID 去重；不同请求/卡/轮次保持区别。最终报告累积历史失败，恢复决策 cause IDs 不因下一轮替换而悬空。错误描述使用固定安全文本，不用原始异常 URL 或凭据作为结构化分类依据。原 Runtime 仍保留实际调用和脱敏错误供调查。

| 边界 | 生产映射与意义 |
| --- | --- |
| Provider HTTP | 401认证、403授权响应、404资源、429限流、5xx服务、其余协议；HTTP状态不能证明WAF/账户/代理等根因 |
| Provider transport / contract | 实际 transport 异常归网络；显式结果契约异常归协议；未知异常保留 unknown；共享包装异常携带 status_code/transport_error_type |
| 未执行查询 | provider失败后的跳过、离线replay miss归coverage.not_executed；物理或局部请求预算拒绝归harness.budget_exhausted；不是已完成零结果 |
| metadata / fulltext | 补全失败保存操作失败；全文异常同时保留Provider原因和material.unavailable因果，原摘要仍可用；无全文能力/空正文也单独记录，不能抹掉已召回候选 |
| Researcher | context超限/不可测、模型超时/transport、schema、provenance、真实预算边界映射；工具 scope/参数/文件缺失和批量Reader局部失败保留；未识别异常为unknown |
| Reviewer | 实际Reader可用性/完整性、timeout/context/schema/ref及汇总问题由Reviewer分项映射；合法材料不足与技术失败分开；not_novel必要条件不成立记录特征缺口 |
| 语义/覆盖 | 缺少有效卡、Reviewer缺特征与成功查询零候选分别记录；三者都不产生“无相关文献”或“新颖”结论 |

完整代码目录由 `failure_catalog.json` 从实际生产定义导出。目录允许动作是诊断建议，不是新网络授权；不是每一个建议都在总图中自动执行，例如摘要恢复和checkpoint恢复为显式接口。

## 下一步决策与约束

1. 轮数或明确预算耗尽时停止；保留所有已获得材料和未解决状态。
2. 已有卡的 Reviewer 技术失败优先停止新 Research，使用独立 summary checkpoint 恢复；模型/context中断也要求先恢复checkpoint或修正故障，不能一概重检。
3. 已知候选未读时只安排 Reader；同一point+namespace+artifact只消费一次恢复机会，失败后不跨轮重复。
4. 所有已执行查询技术失败时，按显式 `recovery_provider_order` 选择尚未用过且配置已启用的来源，复用原SearchPlan；没有替代来源，仅网络/限流/服务异常可按来源追加一次同计划任务。协议/认证/授权未知原因不盲重试。底层原有HTTP退避和物理请求预算继续独立生效；“一次”指一个恢复任务，并非把底层HTTP请求数说成一次。
5. Reviewer缺证且只有摘要时，只获取已有同库source_record_ids的全文（最多4个）；已尝试记录不再重复获取。已有材料仍不足时，才让SearchPlanner扩展未解决特征或语义方向。
6. 成功但零候选时重新规划检索方向；记录“当前查询覆盖不足”，不声明科研否定结论。

`RecoveryToolRegistry` 保留原 Registry 的目标论文排除、权限、checkpoint hook；不能通过包裹工具绕开原 gate。Reader恢复仅可读冻结的无歧义namespace/artifact；实际Reader自行确定namespace，模型不能提供namespace授权。全文恢复不能切回新查询，搜索重试/换源也不能夹带全文句柄改变动作。允许新全文句柄只能来自受限工具真实返回的同记录Artifact。终止/人工/非Researcher动作没有可执行Research工具。

## 报告和 Runtime

恢复阶段落盘每轮 `recovery-round-N.json`，Runtime sufficiency 仍展示原卡数计算，并增加实际recovery决策和routing_basis，避免“卡数PASS却补检”被误报。报告新增结构化 execution_failures / recovery_decisions / point_coverage / point_lifecycle；原版式不变，limitations记载真实停止原因。

生命周期逐点记录任务是否创建、计划是否存在、任务结果是否返回、原始与最终卡、Reviewer状态和报告覆盖。机械候选账本不声明作者贡献语义完整。

单卡核验成功但点级汇总技术失败时，partial_card_reviews保留原局部事实并明确summary_status=failed，不提升为最终裁定。仅最终Gate A接受、同point的卡可进入partial；Gate B进一步验证原Evidence和Reviewer增量读来源闭包。持久化失败但汇总实际完成不会被误标成“汇总未完成”。源卡被剔除时不能经partial字段回流。

## 验证与边界

`tests/test_recovery_closure.py` 覆盖上述两个原反例、状态码、非法retry、换源顺序、次数消费、预算、目标论文排除、空结果、实际Reader namespace、跨run、动作变更拒绝、原Registry hook、Researcher timeout/context、原计划复用、Runtime路由、历史因果闭包、局部报告过滤，以及全文403保留摘要与原因。

独立审查额外发现并修正：Reviewer技术失败优先级、重复补读、持久化状态误报、搜索动作偏离、partial卡回流和历史cause丢失。相关修复后定向与最终测试结果见 `recovery-tests.log/.xml` 和 `full-tests.log/.xml`；中间并行集成未完成时的失败单独保留，不作为最终结果。

本分项证明受控故障下采取不同且有界的机械动作。尚未进行真实多Provider fallback E2E、未证明自动语义补检有效、未改变外部调用授权；默认恢复来源列表为空。全文能力不可用、真实材料不足或模型裁定欠支持都可保留为未解决结果。

最终补充：未注册工具的失败投影此前再次调用 registry.get，导致合法拒绝变成NORMALIZATION异常且轨迹中断。现在保留 `tool.unavailable`，参数校验则为 `tool.arguments`；模型可以收到失败观察后合法收尾。`tool_choice_before_after.json` 用相同输入复现原查找边界：旧路径1次fixture调用后partial/unknown，新路径2次后合法无证据finish并保留失败事件。该实验是边界回放，不是旧完整源码checkout或真实推理。对应112项定向测试及最终1,263项全套均通过。
