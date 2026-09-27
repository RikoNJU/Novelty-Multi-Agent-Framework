# Harness 与配置审查：阶段成果上传索引

上传分支：`experiment/local-llm-baseline`。共同基线：`b378e44`。整理日期：2026-09-28。

**当前是阶段交付，原任务书整体验收尚未通过。** 已撤回“探索审查完成”的判断，详见 [验收状态纠正与缺项](20260927_harness_config_closure/acceptance_correction.md) 和 [逐项复核](20260927_harness_config_closure/task_acceptance.md)。本次提交没有新增在线模型调用、检索或改写原始实验结果。

## 按方面审阅实现

共 12 个提交：8 个实现方面、3 个实验阶段，以及独立导出时发现的测试输入归档修复。当前实现按依赖顺序拆分提交，而不是把最终代码伪装成每次历史实验时的源码。具体文件及提交主题见 [提交范围清单](20260928_harness_upload_manifest.json)。

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

上传保留原始失败、输出、用量、代码快照，以及复现所需的已处理论文正文和结构化输入。排除 Python 缓存、演示运行 `paper-1fa48a8cb5d121220ba897a0_2026-09-27`、本地任务书，以及用户已有的 `docs/Novelty_本地LLM使用手册.md` 改动。原文件仍保留在本地。
