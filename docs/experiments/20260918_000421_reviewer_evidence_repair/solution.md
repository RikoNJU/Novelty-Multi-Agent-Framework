# Reviewer 原文回读修补实施记录

基线 `3ca091d0b5a3ce8b746d1dde3084d057b9888e0d`。生产 ReviewerReaderTool 从单卡已绑定 Evidence 确定 Work，再通过同一项目的 Manifest 验证摘要和正文 Artifact，材料目录与实际权限由同一结果产生。读取后核对 Work、namespace、Artifact 和哈希；摘要 EOF 单独记录，并列出同 Work 的其他材料。正文 `extracted_text` 仍保留原有 `content_extent=unknown`。

单卡模型可引用真实 `read_id`，Harness 从返回文本及字符范围建立不可变的 ReviewEvidence，分配稳定 ID；旧 Card/Evidence 保持不变。新证据进入单卡结果、汇总输入、正式 Review、报告对象及 Markdown。特征对应仅验证固定 feature_id、授权 Work 与证据引用，技术语义仍由现有 Reviewer 判断。旧否定词规则仅计算影子结果，不修改正式单卡或汇总结果。

本地使用已归档 NP-3 的 2PS/WStream 材料和脚本模型替身，未调用外部模型或网络。测试命令与结果见 `tests/commands.txt`、`tests/offline-pytest.log`；172 项相关回归通过。A/G/P 的固定输入结果见 `analysis/`。Reviewer-only L0/L1 成对效果实验未运行：本任务没有独立的金额上限，上一轮完整运行的授权与费用不计入本轮许可。
