# 单查新点稳定性实验：Part 0 基线

实验编号：`NSTAB-SP-20260917`。本次只读取既有归档，没有发起模型、检索、Reader 或论文解析调用。

## 版本与输入

- 当前代码：`2d7aec0add49bda85e8436827fd168c2a191c84f`；开始检查时工作区无差异。
- 历史 run 4–6 的 `run.json` 均记录提交 `68dcaad43a0178aa1f200446fd5704e5b15ddd40`。历史归档另有 `implementation.patch`，其内容哈希见 `source-manifest.json`。不能只凭提交号声称当前编译器与历史编译器相同。
- 选样依任务书优先级采用 run 4 的 `MF2033k6lC / NP-2 / T-1`。`T-1` 的 `task_type=literature_search`、`attempt=1`，因此是可确认的首轮任务。单点输入包位于 `fixtures/np2/`，其中初始可写状态仍不完整。
- run 4–6 的完整 NP-2 对象不同。run 4 的中文 claim 与技术特征、来源位置均与 run 5/6 有差异；run 5/6 之间也有差异。`point_id=NP-2` 不能充当同一输入哈希。每次的点、任务和编译后计划哈希见 `source-manifest.json`。

## 原始产物与缺口

`source-inventory.csv` 登记了三个 run 的任务归档、运行时 Planner stage 输入/输出、候选审计、参考文献资产及哈希。`retrieval-plans.json` 和 Planner stage 输出保存的是 **编译后的 SearchPlan**；归档的 LLM call 文件只有调用元数据，未见完整模型消息与原始 SearchPlanDraft。因此不能把从 SearchPlan 反推的字段标为原始 Draft，不能完成任务书定义的 P4/P5/P6 × C0/C1 六单元精确对照。

首轮 `attempt-1.json` 保存了实际 `search_executions` 的查询、状态与结果，可用于核对已执行请求。但 Provider 原始 wire response、精确请求选项与初始可写缓存快照尚未证实完整，因此不能直接宣称精确响应回放。

## 当前代码边界

`SearchPlannerAgent.plan` 调模型获得 Draft 后立即调用 `build_runtime_plan`；归档产物只保留后者的 SearchPlan。当前编译器的 `_pool_for` 在没有 `focus_concepts` 时按 `importance` 排序并受 strict/medium/broad 上限裁剪。Researcher 的任务入口接收已构造的 `search_plan`，但现有归档是整篇 `paper_input` 运行，不能因此声称已有受控的单点离线实验入口。后续需先核实工具内部有无再次规划、固定查询池与网络拦截能力。

## 允许的离线结论

三个 run 的 NP-2 首轮 arXiv 都执行了相同的 strict 查询和 `abs:"graph summarization"` 回退查询；前者返回 0 条，后者各返回 8 条。首轮读取记录数分别为 5、3、4，原始卡片数均为 0。run 6 还执行了六条 `null_catalog` 测试源请求，均为成功零结果。这个局部事实支持“相同已核对 arXiv 查询的八篇结果没有变化”，不能推广到整个 Provider 或全部候选来源。

最早可直接核验的跨 run 差异是 NP-2 输入内容；下游也有读取选择和测试源调用差异。目前不能把这些差异归因给单一组件，因为完整输入没有固定，且缺少原始 Draft 与模型决策轨迹。按照任务书停止条件，先交付缺口和最小验证动作，不启动付费重跑。
