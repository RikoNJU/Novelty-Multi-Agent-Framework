# Coordinator 报告边界实验

本目录对应任务书 `RPT-BOUNDARY-20260918`。基线为 `64e4604`。两份历史失败运行的报告节点输入已冻结并在本机核对哈希；原始输入、原始模型响应和 PDF 留在受控 `outputs/`，不提交到 Git。外部克隆仓库只能核对索引和执行合成测试，不能凭本目录独立重放私有原文。

本轮已完成旧响应本地复现、简短 Draft 契约、权威字段确定性组装、两个来源的离线节点回放，以及离线报告的浏览器读取测试。**真实模型报告节点 L1／L2 尚未调用**：任务书明确要求本轮重新授权金额、次数、时间和材料传输范围。离线成功不代表实际模型成功，也不改变原业务 run 的 `FAILED` 状态。

入口：`scripts/replay_report_synthesis.py`。默认 `offline` 使用明确标记的脚本模型；`live` 仅运行 `synthesize_report`、完整性校验、持久化和渲染，并使用独立总预算账本。实际调用前应取得本轮许可。

详见 [报告](report.md)、[验收台账](acceptance-status.json)、[来源索引](fixtures/source-manifest.json) 和 [已知问题](analysis/known-issues.md)。
