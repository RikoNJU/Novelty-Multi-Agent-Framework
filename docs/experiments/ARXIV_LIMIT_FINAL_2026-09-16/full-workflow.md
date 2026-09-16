# PaperInput 工作流验收

输入：`outputs/MF2033k6lC/paper-input/others/paper.json`，SHA-256 `89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66`。
参考缓存：`docs/experiments/20260916_011551/input/MF2033k6lC/subject_references`，已通过现有 manifest 校验；仅复制到新运行目录。不调用 MinerU。

三轮均只启用 arXiv Web provider（8 秒），关闭其他数据库、WebSearch、Browser；本地 reference_search / reader 保留。Research Task max_concurrency=4，Reviewer/Renderer/SearchPlanner 不修改。

外部模型：当前配置的 `https://api.siliconflow.cn/v1` / `deepseek-ai/DeepSeek-V4-Flash`。首次启动因自动审批要求对目的地址和内容明确授权被拒，未产生模型调用；用户在明确目的地址的问题后授权，最终明确要求执行任务书三轮。

运行命令：`python docs/experiments/ARXIV_LIMIT_FINAL_2026-09-16/run_workflow.py {single,parallel,full}`。复用已有 single-task harness 的请求装配与现有标准工作流、Runtime Debug。

- Run 1: **SUCCESS**，NP-2/T-2(en)，213.91 秒，17 次 Reader 读取、3 张卡。10 次 Web 物理请求全部 200，最小间隔 8000.13 ms。8 个 research_reference 候选均被读取；最终卡全部来自 subject_reference，不能算 Web 新候选证据卡。
- Run 2: **SUCCESS**，NP-2/T-1(zh) + T-2(en)，246.88 秒；两个任务开始相差 8.84 ms，保持并发。16 次物理请求全部 200，最小间隔 8000.10 ms。两个任务分别 4/13 次读取、0/2 张卡，最终卡仍来自 subject_reference。
- Run 3: **SUCCESS**，同一个 PaperInput 标准完整工作流，986.37 秒（约 16.4 分钟），2 个工作流迭代轮次。SearchPlanner → 并发 Research Tasks → database_search → Reader → EvidenceCard → Reviewer → Renderer 全部执行。最终 3 张卡、3 个查新点评审，0 个最终证据不足点；其中 **2 张卡来自本次 Web 新候选**。39 次物理请求，37 次 200、2 次 406；0 retry、0 interval violation；最小间隔 8000.07 ms。

原始结果和摘要位于 runtime/{single,parallel,full}，派生审计见 [metrics/workflows.json](metrics/workflows.json)。

第一轮在最终“重定向逐跳调度”补丁前启动；观察到的全部请求均为直接 200，无重定向，故该差异没有影响本轮链路。第二/三轮基于生产提交 `9222d37`。

## 真实故障与证据验收

补检中发生两次 HTTP 406，分别位于完整工作流 Runtime 的 `0063_database_search.json` / `0066_database_search.json`。各自包含 4 个成功 SearchExecution 和 1 个 FAILED SearchExecution；`provider_failed=true`、`degraded=true`、business_status=PROVIDER_FAILED。保留已取得候选，因此工具整体为 SUCCESS；这不是把故障记为空结果。故障后对应 fallback 链停止，406 未重试。两次之间有成功请求，未达到连续失败熔断阈值。

NP-3 首轮因 reference_search 工具预算耗尽而 partial、没有卡；第二轮补检正常完成并形成新 Web 候选卡。此类策略/取证行为未在本次修改。

最终新候选卡：
- NP-1 / DGC，`card_7a049fd9d35cd2e205956ff7`，3 条绑定至本次 research_reference Artifact 的证据。
- NP-3 / `card_ede76afb2b96bb4d6c8f2297`，2 条绑定至本次 research_reference Artifact 的证据。

[来源链核验](metrics/web-card-provenance.json)确认两张卡均由 `arxiv-web-search` 来源生成且保留于最终报告；所有引文按既有 Builder 的原文或空白/排版归一化规则匹配 Reader 文本。两次证据完整性 Gate 和最终 report integrity Gate 全部通过。

Run 1 的 NP-2 单任务没有选中 Web 新候选生成最终卡；该局部验收缺口由 Run 3 的 NP-1/NP-3 真实 ResearchTask 新候选成卡补证，而不是人为修改研究结论。

最终报告：[MF2033k6lC-report.md](runtime/full/MF2033k6lC/report/MF2033k6lC-report.md)。

## 归档布局

完整原始运行文件保留于本地 `outputs/arxiv-limit-final-2026-09-16/raw-runtime/`（不入 Git）。本目录 runtime 保留原始 summary、逐请求事件、关键工具与 ResearchTask 输出、来源清单、最终报告；没有修改这些保留记录的内容。省略的完整输入/模型过程快照由 [runtime/raw-manifest.json](runtime/raw-manifest.json) 记录路径、字节数和 SHA-256，可在本机核验。
