# B0/BF/BE/BFE 局部控制流矩阵

生产函数测试：`tests/test_retrieval_repair.py::test_four_control_flow_variants_keep_changes_separate`。四单元共用固定的查询→合成响应映射；不是历史 Provider 原始响应，也不评价论文相关性。最终候选上限 8、每查询返回上限 8、逻辑检索调用预算 6。

| 单元 | fallback | 执行策略 | 受测结论 |
|---|---|---|---|
| B0 | F0 | E0 | S1 零结果后，S1-fb1 丢 C1；8 篇填满后 S2/S3 不执行 |
| BF | F1 | E0 | S1-fb1 保留 C1、丢 C2；8 篇填满后 S2/S3 不执行 |
| BE | F0 | E1 | S1/S2/S3 基础方向均得到执行机会；S1-fb1 仍丢 C1 |
| BFE | F1 | E1 | S1/S2/S3 基础方向均得到执行机会；S1-fb1 保留 C1 |

E1 在此场景比 E0 执行更多查询；不能据此称同成本的召回或证据质量提高。F0/E0 开关仅用于局部对照，默认生产值为 F1/E1。
