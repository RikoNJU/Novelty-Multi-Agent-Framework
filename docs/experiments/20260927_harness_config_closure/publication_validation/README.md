# 独立导出验证

2026-09-28，发布前从实现提交 `48cff0f1d5a03fedb43fd1d9d75a5235b039415e` 使用 `git archive` 导出到独立目录，执行完整非在线回归。

[首次日志](initial-export-tests.log) / [JUnit](initial-export-tests.xml)：**1,262 passed、1 failed、6 deselected**。`test_real_paper_digest_includes_bounded_independent_contribution` 读取被忽略的本地 `outputs/MF2033k6lC/paper-input/others/paper.json`，导出目录没有该文件。

这与原工作区 1,263 passed 的记录不矛盾，但说明当时的测试发布范围不完整。原始失败保留，测试输入与路径修复作为独立后续提交，不改写原始实验源码快照和日志。
