# Reviewer 原文回读修补实施记录

基线 `3ca091d0b5a3ce8b746d1dde3084d057b9888e0d`。生产 ReviewerReaderTool 从单卡已绑定 Evidence 确定 Work，再通过同一项目的 Manifest 验证摘要和正文 Artifact，材料目录与实际权限由同一结果产生。读取后核对 Work、namespace、Artifact 和哈希；摘要 EOF 单独记录，并列出同 Work 的其他材料。正文 `extracted_text` 仍保留原有 `content_extent=unknown`。

单卡模型可引用真实 `read_id`，Harness 从返回文本及字符范围建立不可变的 ReviewEvidence，分配稳定 ID；旧 Card/Evidence 保持不变。新证据进入单卡结果、汇总输入、正式 Review、报告对象及 Markdown。特征对应仅验证固定 feature_id、授权 Work 与证据引用，技术语义仍由现有 Reviewer 判断。旧否定词规则仅计算影子结果，不修改正式单卡或汇总结果。

本地使用已归档 NP-3 的 2PS/WStream 材料和脚本模型替身，离线测试未调用外部模型或网络。测试命令与结果见 `tests/commands.txt`、`tests/offline-pytest.log`；172 项相关回归通过。A/G/P 的固定输入结果见 `analysis/`。

2026-09-18 用户进一步授权本任务的实际实验预算及向 SiliconFlow 发送固定 NP-3 材料。使用 `scripts/run_reviewer_np3_live_pair.py` 执行 L0/L1 Reviewer-only 诊断；输入、限制、调用记录和输出见 `trials/np3_live_pair_20260918/`。实际 16 次模型调用，Runtime 计价人民币 0.2345532 元，没有外部文献获取。L1 确实读取两篇正文；L0 因模型自行填写 `review_evidence` 被结构校验拒绝，L1 因本次冻结的读取／工具次数上限而未完成。详见 `report.md`，不将此诊断记为语义效果通过。
