# 稳定性原因报告：当前证据边界

本轮已完成 Part 0 原始材料核对，未运行 C1/E1、六单元编译对照、阅读重放或单点 live 实验。费用与新增业务调用均为 0。

**发现 F1（直接观察）：** run 4–6 的 `MF2033k6lC / NP-2` 对象内容不同。固定条件仅有论文 ID、查新点 ID 与首轮任务的结构字段；完整查新点未固定。最早可核验分叉发生在 Planner 前。证据：三个 run 的 `novelty-points.json`，对象哈希在 `source-manifest.json`。因此不能把后续查询、阅读差异直接解释成同一输入下的随机性。

**发现 F2（直接观察）：** 三次首轮任务的相同 arXiv 回退查询 `abs:"graph summarization"` 各返回 8 条；首轮读取记录分别为 5、3、4，原始卡均为 0。证据：各 run 的 `research-runs/NP-2/T-1/attempt-1.json` 中 `search_executions`、`read_results`、`evidence_cards`。这只定位了候选之后仍有不同去向的观察事实；缺少固定输入、片段和模型消息，尚不能判定成卡机制。

**发现 F3（直接观察）：** run 6 首轮任务另执行六条 `null_catalog` 查询且全部成功零结果；run 4/5 的该首轮任务没有这些执行记录。证据同 F2。测试源差异需纳入配置与执行比较，不能混入 arXiv 召回差异。

**阻断项：** 原始 SearchPlanDraft、完整渲染消息、精确任务前状态与 Provider wire response 未在已核对归档中建立可用快照。P4/P5/P6 × C0/C1 和严格响应重放均标为 `blocked_missing_fixture`。下一步最小动作是为未来单点运行旁路保存 Draft、消息及请求/响应附件，并实现默认禁止外部调用的编译入口；随后才可对固定输入作交叉对照。历史 SearchPlan 可作为 `derived_projection` 单独研究，不能称为历史 Draft 精确复现。
