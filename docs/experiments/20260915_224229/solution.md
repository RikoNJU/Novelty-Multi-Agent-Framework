# 修复后完整工作流复跑

## 结果

完整工作流成功，报告完整性校验、持久化和渲染均 SUCCESS。样例仍为 examples/MF2033k6lC.pdf，复用已解析 PaperInput 与参考文献缓存；未调用 MinerU。启用 arXiv、Springer、WebSearch，Browser 关闭；未修改 arXiv429策略。

**NP-2 的7条实际查询已经汇入最终报告，全部标记“执行失败”，不再显示“无”。** 三个查新点所有实际查询都在各自报告检索式小节中，逐条核对结果见 verification.json，原样小节见 report-query-section.md。

报告：[MF2033k6lC-report.md](run/MF2033k6lC/report/MF2033k6lC-report.md)。

## 运行经过与概念数量问题

首次尝试于2026-09-15 22:12:36开始，22:18:07中止，耗时330.89秒，尚未开始检索。NP-1/T-1的SearchPlanner三次尝试后仍生成7个概念，超过配置中的上限6，导致完整性校验缺少一份计划。失败产物完整保留在 failed_attempt_01/，不是成功运行的一部分。

关于用户提到的“概念数不设限”：SearchPlanDraft和SearchPlan的concepts字段确实只有min_length=1，没有schema上限。但是agents/search_plan_compiler.py的SemanticLimits.max_concepts默认6，config/schemas.py及search_planner配置也为6，编译器超过6即too_many_concepts。git blame表明该限制来自2026-08-30提交5e12b64，并非此次修复新增。当前prompt还建议2~4个，另有重试反馈建议4~6个，三处表达不一致。本轮只查明并记录，没有修改数量政策。

随后在相同配置下完整重试一次，未绕过校验或填造计划。成功尝试于22:18:51开始、22:42:29结束，程序记录耗时1421.34秒（约23分41秒）。过程中未修改生产代码。

## 成功尝试统计

| 项目 | 结果 |
| --- | --- |
| 查新点 / 轮数 / 研究任务 | 3 / 2 / 8 |
| 任务状态 | 3 completed、5 partial |
| 原始 / 最终卡片 | 8 / 8 |
| 按查新点分配 | NP-1：3，NP-2：2，NP-3：3 |
| 数据库候选文献 | 16篇 |
| Artifact | 17个：16个abstract、1个extracted_text |
| Researcher正文读取 | 35次成功 |
| Reviewer回读 | 18次成功：8次subject_reference，10次research_reference |
| 模型调用 / reported tokens | 149 / 1,460,383 |
| 最终附件论文条目 | 20 |

计量含多轮累计上下文，不是独立文档量。首次失败另有14次模型调用、42,089 reported tokens；两次尝试合计163次调用、1,502,472 reported tokens。

## 检索式汇入验证

| 查新点 | 执行记录 | 标记 |
| --- | ---: | --- |
| NP-1 | 16 | 13失败、2有命中、1部分成功 |
| NP-2 | 7 | 7失败 |
| NP-3 | 5 | 3失败、1有命中、1部分成功 |

共28条数据库执行记录全部保留。没有把服务错误改成零命中，也没有因为失败而删除查询。本轮未产生zero_hits记录，因此成功零命中标记的验证仍依据此前本地回归。

## 修复行为与剩余问题

### 回读命名空间

53次实际读取全部成功（Researcher35、Reviewer18），未复现原先到research manifest查找subject artifact的错误。另有5条Reader失败/拦截记录：Researcher reader预算耗尽1次；Reviewer总工具预算耗尽1次；非法placeholder一次、none两次。它们是预算或范围校验拒绝，不是读取了错误的文献库。

### 收尾恢复

5个Researcher任务触发预算后的无工具最终整理，均完成整理并保留partial状态。其中第二轮两个任务产生了NP-1的3张卡片，证明已读内容没有因预算边界直接全部丢失。

本轮没有最终JSON解析失败记录；没有足够独立记录证明Reviewer是否调用过格式恢复，因此不声称在线验证了其格式恢复成功率。NP-1最后仍降级insufficient_evidence，原因是Reviewer耗尽工具预算，并非零卡或JSON错误。

### Reviewer结果

NP-1：insufficient_evidence，原因是Reviewer总工具调用预算耗尽。
NP-2：reviewed / novel。
NP-3：reviewed / partially_novel，并建议补充流式图边划分文献。

以上是模型判定，不是此次实验对学术新颖性的独立背书。非法artifact ID被范围校验拒绝，说明防护有效，同时也说明模型工具调用行为仍不稳定。

### Web策略与检索服务

WebSearch共10次失败：9次百度HTTP429、1次74单位查询触发72单位本地上限。超长查询没有发送HTTP，返回INVALID_QUERY、计数和缩短建议，说明工具防线有效；prompt没有杜绝全部超长输出。

本轮没有获得Web来源记录，没有Web卡片或网页清单，也没有显示Web补充建议。由于不存在成功返回的网页内容，这次不能单独验证“取得Web内容后”的展示过滤；该规则此前已有渲染与Builder测试。

Springer有6次HTTP200、10次404；arXiv有4次429、2次读取超时。记录但不在本轮调整429策略。逻辑执行、工具调用和物理HTTP请求口径不同，不混用。

## 归档说明

run/保存成功尝试全部结果，failed_attempt_01/保存第一次失败。metrics.json、verification.json和experiment.json记录统计与边界；working_changes.diff和source_snapshot/记录启动时工作区改动。内部原始路径保留运行时临时目录名，访问归档请使用本目录相对路径。

没有提交或推送。概念数硬上限尚未移除，等待数量政策的后续明确调整；本轮成功尝试保持了启动时配置。
