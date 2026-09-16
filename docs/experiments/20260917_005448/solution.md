# v0.1 检索稳定化与双样本 Release Regression

实验结束：2026-09-17 00:54:48（Asia/Shanghai）。任务书：`task/Novelty_v0.1_Demo封版_检索稳定化任务书_2026-09-17.md`。

## 修复与验收

1. Target Paper Identity Gate 在检索结果进入候选和 Reader 前按 DOI、arXiv/PMID/provider ID、规范化标题、模糊标题加作者判定原论文。排除项写入 candidate audit；Reader 和全文获取再查持久化 manifest，防止直接传入旧 artifact ID 绕过。相同作者但不同标题不会被排除。
2. 正式工作流注册 provider 时排除 `testing_only`，测试工厂仍可显式使用。两次报告均没有 `null_catalog` 或 `NULL_QUERY(...)`；Runtime manifest 保留原始配置声明供审计，不代表 provider 已启用。
3. SearchPlan Compiler 拒绝正向 term/alias/核心 token 与 exclude 冲突，向 Planner 返回结构化错误。
4. strict、medium、broad 的编译都保留同一 anchor；medium 减少特征，broad 只保留 anchor 及其 alias。分布式计算、其他技术领域和合成概念均有单测。

定向回归：`tests/test_target_paper_identity.py`、`tests/test_live_testing_only_sources.py`、`tests/test_search_planner.py` 及现有工作流/Renderer 测试，共 100 项通过。更宽的数据库搜索集成测试在既有 scope planning / harness 集成路径中超时，未作为通过证据。

## 完整运行

两次均使用仓库已有 `scripts/run_full_workflow_live.py`，`--max-rounds 2 --max-concurrency 4`，从既有 PaperInput 入口运行；没有调用 MinerU。配置快照在 `input/`。在线数据源为 arXiv 和 Springer Nature，WebSearch/Browser 未启用。每篇只运行一次。

| 样本 | 输入 | 结果 | 用时 | 查新点 | 候选审计 | 有效卡 | Reviewer | 报告 |
|---|---|---|---:|---:|---:|---:|---|---|
| A 图计算 | `input/sample_a.paper.json` | SUCCESS | 417.8 秒 | 3 | 40 | 2 | 3 点均 `insufficient_evidence` | `runs/full/0001/MF2033k6lC/report/MF2033k6lC-report.md` |
| B 音乐生成 | `input/sample_b.paper.json` | SUCCESS | 252.6 秒 | 3 | 24 | 4 | 1 点 `reviewed`，2 点 `insufficient_evidence` | `runs/full/0002/MG19333vrw-debug-full-20260907/report/MG19333vrw-debug-full-20260907-report.md` |

B 来自真实论文的现有 PaperInput。原副本 OCR 将日期误识别为标题，因此实验副本只依据正文第 3–4 页修正中英文标题；正文、摘要和参考文献未改。原副本、修正副本与 SHA-256 均在 `input/` 和 `manifest.json`。

两次运行都完成 Reader → Evidence → Card → Reviewer → Markdown Renderer，Runtime Debug 包含阶段、工具调用、实际 query、provider 状态和报告路径。两次在线结果均未召回原论文自身，故排除计数为 0；召回后排除以及阻断 Reader/Evidence/Card 由定向注入测试验证，不将“没有召回”冒充在线排除成功。

检索失败与零命中分开记录。A 的 arXiv 有 9 次 `HAS_RESULTS`，Springer 有 11 次 `PROVIDER_FAILED`；B 的 arXiv 有 5 次 `HAS_RESULTS`，Springer 有 4 次 `PROVIDER_FAILED`。这些在线失败没有阻断两次报告生成，也没有被当作无相关文献的证明。

原始 `run.json` 和 Runtime Debug 记录的是执行时的 `20260917_v01_staging` 工作目录。实验结束后整体移至本目录；路径中的旧目录名是历史输入身份和执行环境记录，所有实际文件位于当前目录下的相同相对位置。

## Known Issues / v0.2

- Springer 在线查询有多次 provider 失败；arXiv、Reader 和完整工作流仍能产生可追溯证据。本轮按任务书不做 Springer 系统性修复。
- 两次运行的 `reference_namespace` 诊断显示 `ERROR`，但 `namespace_integrity_failures=0`，Evidence 绑定与最终完整性守卫均通过。应在 v0.2 调查诊断对失败 Reader 调用的误报。
- A 的 NP-3 没有有效卡，Reviewer 保守给出证据不足；任务书允许该结果，不为固定样本调 Prompt。
- 只测试了两篇不同主题的真实 PaperInput，不能推断跨学科泛化或检索召回率。在线排序、网络和限流会造成波动。
- Reviewer 的 `supplement_request` 尚不自动控制补检；数据库覆盖范围也不能替代正式科技查新机构。

封版判断：四项 P0 修复与两篇 release regression 均通过，未发现阻断 v0.1 Demo 的问题。按任务书停止本轮 backend 调优，后续改进进入 v0.2。
