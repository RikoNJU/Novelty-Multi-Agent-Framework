# Harness 与配置审查：阶段成果（验收未完成）

发布补充：独立导出发现并修复了一项测试对本地输出的依赖，复测 **1,263 passed、6 deselected**。原实验快照不改写，历史清单与最终上传清单的区别见 [独立导出验证](publication_validation/README.md)。

2026-09-28。目录名保留本轮开始日期。原任务书的逐条证据、实际结论及尚未知边界见 [task_acceptance.md](task_acceptance.md)。

**当前为阶段成果，任务尚未完成整体验收。** 已撤回“探索审查已完成”的判断，见[状态纠正与剩余验收](acceptance_correction.md)。 最终代码1263项非live回归通过、6项live排除，1条既有弃用警告。Reader六次真实摘要实验均0卡/partial；Reviewer三次引用合法但语义不通过；arXiv公共查询仍406，根因Unknown。没有把这些结果改写为成功，也没有追加云模型能力。

## 修复与实验入口

| 分项 | 报告 | 主要证据 |
| --- | --- | --- |
| 取消/解析失败usage | [usage_accounting.md](usage_accounting.md) | 修前6失败；80项相关回归，已知usage精确一次入账 |
| 候选和特征保留 | [point_coverage.md](point_coverage.md) | 相同4候选/去重响应的holdout，原丢12个中英特征实例→全保留，语义覆盖仍pending |
| Reviewer与summary恢复 | [reviewer_recovery.md](reviewer_recovery.md) | 3次真实材料/9调用，原样失败保留；6份冻结输出窄规则回放；严格一次显式恢复 |
| 错误、恢复、报告 | [recovery.md](recovery.md) | 完整错误目录；按缺口分流；原计划/句柄/次数约束；partial及最终卡闭包 |
| Context机械状态 | [context_projection.md](context_projection.md) | 100项相关回归；30次读取长轨迹状态不膨胀、原历史保留，不宣称压缩 |
| 配置/能力/源码重建 | [configuration.md](configuration.md) | 84项定向回归，正式入口预检，独立快照重建；[Profile使用说明](../../../config/README.md) |
| Reader重复实验 | [reader_repeated_local.md](reader_repeated_local.md) | off/on各3，实际30本地chat；调用和物理读均未减少，无cache命中，0卡 |
| Provider故障 | [arxiv_failure_analysis.md](arxiv_failure_analysis.md)、[sciencedirect_enrichment.md](sciencedirect_enrichment.md) | 4个公共GET定位边界；离线修补可选补齐失败丢候选，保留失败状态 |

本轮闭环新增39个本地Qwen请求，逐调用原usage均匹配；235350输入+6433输出=241783 tokens。没有新论文外检/云模型调用；4个arXiv GET使用固定公共词，另读取公开官方能力文档。价格及本地算力成本Unknown。详细去重口径在 [scope_accounting.json](scope_accounting.json)，不能与历史242次或前轮采样调用相加冒充全任务总数。

## 最终验证与归档

- [full-tests.log](full-tests.log) / [full-tests.xml](full-tests.xml)：最终完整结果；命令 `PYTHONPATH=backend/src:.:tests /home/lya3106643285/miniconda3/envs/Novelty-web/bin/python -m pytest -o addopts='' -q -m 'not live'`。相邻前次结果保留为before文件，不当最终结果。
- [source_inventory.json](source_inventory.json)：85个backend/scripts/tests/config变更文件，包含新增文件。`implementation.patch`是相对该清单base_commit的累计补丁，反向应用检查通过；不是一次新git提交，未提交/推送。
- [final_configuration_manifest.json](final_configuration_manifest.json)和[final_startup_v2/manifest.json](final_startup_v2/manifest.json)：最终新离线冻结；原始输入、有效配置和源码内容。早期`final_startup/`及before-tool-boundary文件保留，均不能冒充此前live的启动状态。
- Reviewer真实实验用`reviewer_local_fixed/source_snapshot/`；Reader真实实验用`reader_local_repeated/startup/`。执行版本与最终代码不同处有明确时间/哈希边界。Reader runner收尾两处调用签名错误已记录，off_1未重复推理，原llm/tool/stage事实保留，但该样本缺正常summary/独立trace sidecar。
- [secret_scan.json](secret_scan.json)：新工件和已知真实密钥的扫描口径及结果；不含密钥值。只证明所列范围与已知值无命中。
- [validation_summary.json](validation_summary.json)：最终测试、源码/快照/补丁一致性和文档链接核对。

本次不改用户已有的`docs/Novelty_本地LLM使用手册.md`，累计补丁也不包含该文件。未更改报告视觉/PDF版式。仓库中零模型调用的测试运行归档不计入上述真实实验账本。

前两阶段：[初次审查](../20260927_harness_config_audit/README.md)、[continued原始结论和未完成复核](../20260927_harness_config_continued/README.md)。这些历史报告保留其当时结论；本文件与逐项验收表给出最新状态。
