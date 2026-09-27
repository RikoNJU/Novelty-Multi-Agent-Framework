# Harness 与配置审查：阶段成果上传索引

上传分支：`experiment/local-llm-baseline`。共同基线：`b378e44`。整理日期：2026-09-28。

**当前是阶段交付，原任务书整体验收尚未通过。** 已撤回“探索审查完成”的判断，详见 [验收状态纠正与缺项](20260927_harness_config_closure/acceptance_correction.md) 和 [逐项复核](20260927_harness_config_closure/task_acceptance.md)。原始结果保持不变；后续在线检索补充按下方独立阶段记录。

独立提炼的结论、实验数字、工程边界与剩余验收工作见 [阶段总结报告](20260928_harness_config_review_summary.md)。三阶段原始试验记录一并提交。

## 按方面审阅实现

截至本次补充共 18 个提交：原 14 个实现/实验/说明提交，随后单独提交缓存忽略规则、使用手册，以及工具失效因果调查与码体系状态核查、HTTP 边界续查。当前实现按依赖顺序拆分提交，而不是把最终代码伪装成每次历史实验时的源码。具体文件及提交主题见 [提交范围清单](20260928_harness_upload_manifest.json)。

1. 模型请求、上下文准入与用量核算。
2. Provider 返回分类与检索错误保留。
3. 失败契约与 Reader Harness。
4. 查新点候选和特征覆盖。
5. Researcher Evidence 检查点。
6. Reviewer 核验、检查点与诊断；四个真实响应 fixture 随依赖测试一同提交。
7. Workflow 恢复策略与报告状态。
8. 配置 profile、来源追踪、冻结与正式入口。

这些提交是当前整合实现的审阅单元；历史运行必须以对应归档中的代码快照、配置和输入为准。没有声称每个中间提交都完成整套回归或科学效果验收。

## 按阶段审阅实验

| 阶段 | 记录入口 | 主要内容与边界 |
| --- | --- | --- |
| 初始审查 | [audit](20260927_harness_config_audit/) | 原始问题、配置盘点和早期定向检查，结论以该阶段条件为限 |
| 继续验证 | [continued](20260927_harness_config_continued/) / [真实 runtime](runtime/MF2033k6lC_2026-09-27/) | 已授权的本地模型加 arXiv 整流程；外部请求 HTTP 406，0 Evidence，不能作为充分材料能力验收 |
| 后续修复及复核 | [closure](20260927_harness_config_closure/README.md) | 修复、冻结回放、本地重复实验、源码快照、用量和回归；目录历史名称 closure 不代表整体验收完成 |

继续验证阶段的外层原始输出于本次发布时按原字节补充归档，见 [来源与 SHA-256](20260927_harness_config_continued/original-run-archive.json)。这是运行后归档，不是补造缺失的启动快照。

## 验证与保留范围

当前源码的已有完整非在线回归为 **1,263 passed、6 deselected**，见 [日志](20260927_harness_config_closure/full-tests.log) 和 [校验汇总](20260927_harness_config_closure/validation_summary.json)。该结果证明代码回归断言，不能代替真实正例、修后消融、整合流程和模型差距归因。发布前另行检查提交范围、哈希、补丁及凭据泄漏风险。独立导出首次发现一项测试依赖未提交输入，失败与后续修复单独保留，修复后独立导出全量复测 1,263 passed、6 deselected，见 [独立导出验证](20260927_harness_config_closure/publication_validation/README.md)。

上传保留原始失败、输出、用量、代码快照，以及复现所需的已处理论文正文和结构化输入。根据用户追加要求，[演示运行 runtime](runtime/paper-1fa48a8cb5d121220ba897a0_2026-09-27/README.md) 的 8 次运行、800 个原始文件也已纳入，保留其零模型/零检索调用属性，不计入真实实验成效。Python 缓存与本地任务书不提交。使用手册已按用户后续要求单独提交格式整理，缓存保留本地并修正忽略规则。

## 工具失效归因补充

[24 个离线对照与 8 次真实请求调查](20260928_tool_failure_causality/README.md)；[错误码与补检/恢复动作码状态](20260928_tool_failure_causality/code_system_status.md)。本次生产代码未改，406 根因仍未确定，任务验收状态不变。

## HTTP 边界续查与确定性解析缺陷

[24 次请求及同连接 ABBA 对照](20260928_arxiv_http_boundary/README.md)。等价 URL 稳定出现 200/406 差异，生产路径匹配失败 URL；具体服务端原因仍待确认。另确认旧式 ID 分类前缀丢失，5 个不同真实文献复现。本阶段只增加诊断与归档，0 模型调用，未修改生产代码。
