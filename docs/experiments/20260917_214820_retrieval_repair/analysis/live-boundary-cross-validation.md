# 一次完整运行后的边界交叉核对

运行 `run-d606cd37534a47349b905d42c6141768` 复用了已落盘 PaperInput，执行了提取后完整下游工作流；未调用 MinerU。只运行一次 BFE，不把旧完整运行当成同输入因果 A/B。指标见 `live-run-metrics.json`。

| 边界 | 本次实际核对 | 结果与限制 |
|---|---|---|
| X1 Planner／编译 | 固定本次已记录的三个 compiled SearchPlan，分别本地生成 F0、F1 fallback。三个点都保护 C1。 | F0 在 NP-1 的 S1/S2 fallback、NP-2 和 NP-3 的 S2 fallback 会删除 C1；F1 均保留。证明本次实际计划暴露 R-01 机制，不能由此推算 F0 的真实文献结果。 |
| X2 fallback／执行 | B0/BF/BE/BFE 合成响应矩阵已在 `variant-matrix.md`；本次真实响应逐方向检查。 | NP-1/2/3 的 arXiv 三个基础策略都执行。NP-3 前两个基础方向为 0，第三个才观察到 8 个身份；本次实际响应不构成“早期 8 篇截断”反事实。F0 会改变请求，缺同请求真实响应，记为 replay_miss，不把旧动作冒充反事实。 |
| X3 Provider／候选 | 固定本次 Provider 返回与候选事件核对；27 次物理请求中 arXiv 指标记录 20 次成功 API 请求。 | arXiv 候选选择 NP-1=5、NP-2=2、NP-3=8；Springer 四次查询均 HTTP 404，导致其后 20 个方向标为 `NOT_RUN/provider_failed`，不是“无相关文献”。未新增局部探针。 |
| X4 Reader／成卡 | 固定已选择候选，核对生产 tool 记录、阅读与最终卡片。 | Reader 成功次数 NP-1/2/3=6/5/8；NP-1 另有一次批读参数校验失败。七次 `reader required after database_search` 为调用顺序被 Harness 拒绝。最终卡片 1/2/2；缺少同候选的替代阅读／成卡输出，无法把候选到卡片的差额单独归因于 Reader、Researcher 或 Builder。 |
| X5 审查／渲染 | 固定本次五张卡、三条 Reviewer 裁定，核对报告 JSON、结果 JSON、Markdown 与完整性门禁。 | 三点 Reviewer 均 `insufficient_evidence`，理由是缺乏支持“未采用关键特征”的原文证据。报告 JSON 与结果中的报告对象相同，5 张卡均被引用，报告引用完整性通过；前端页面与 API 未在本次运行中启动验证。 |

结论：R-01 在本次真实计划中有实际触发条件并已阻止保护项被删；R-02 的修补路径执行正常，但这次真实返回不足以证明它改变了候选或最终证据。当前证据不足主要由 Reviewer 对原文否定性断言的要求体现，另有 Springer 404 和模型工具调用格式／顺序错误。不能只凭卡片数或 `SUCCESS` 推断检索质量改善。
