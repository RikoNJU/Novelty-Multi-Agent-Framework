# Coordinator 报告边界实验

本目录对应任务书 `RPT-BOUNDARY-20260918`。基线为 `64e4604`。两份历史失败运行的报告节点输入已冻结并在本机核对哈希；原始输入、原始模型响应和 PDF 留在受控 `outputs/`，不提交到 Git。外部克隆仓库只能核对索引和执行合成测试，不能凭本目录独立重放私有原文。

本轮已完成旧响应本地复现、简短 Draft 契约、权威字段确定性组装，以及两个来源的真实报告节点恢复。首次派发因沙箱网络限制失败并保留预算预留；续跑中 L1、L2 各获得一次真实模型响应。随后发现模型自由局限包含未由节点输入证实的覆盖判断，已从最终报告中排除，并用保存的真实响应零费用重新组装。原业务 run 的 `FAILED` 状态没有改变。

入口：`scripts/replay_report_synthesis.py`。`offline` 使用明确标记的脚本模型；`live` 仅运行 `synthesize_report`、完整性校验、持久化和渲染，并使用同一总预算账本；`captured` 复用已保存的真实响应，不再调用模型。最终采用 `L1-captured-reassembly` 与 `L2-captured-reassembly` 的产物。

详见 [报告](report.md)、[验收台账](acceptance-status.json)、[来源索引](fixtures/source-manifest.json) 和 [已知问题](analysis/known-issues.md)。

浏览器完整截图含报告正文，只留在本机受控目录；Git 归档记录测试观察与哈希，不分发该截图。
