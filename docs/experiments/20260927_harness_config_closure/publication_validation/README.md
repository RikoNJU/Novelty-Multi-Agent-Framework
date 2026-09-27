# 独立导出验证

2026-09-28，发布前从实现提交 `48cff0f1d5a03fedb43fd1d9d75a5235b039415e` 使用 `git archive` 导出到独立目录，执行完整非在线回归。

[首次日志](initial-export-tests.log) / [JUnit](initial-export-tests.xml)：**1,262 passed、1 failed、6 deselected**。`test_real_paper_digest_includes_bounded_independent_contribution` 读取被忽略的本地 `outputs/MF2033k6lC/paper-input/others/paper.json`，导出目录没有该文件。

这与原工作区 1,263 passed 的记录不矛盾，但说明当时的测试发布范围不完整。原始失败保留，测试输入与路径修复作为独立后续提交，不改写原始实验源码快照和日志。

修复后的 [完整日志](final-export-tests.log) / [JUnit](final-export-tests.xml)：**1,263 passed、6 deselected、1 warning，32.07s**。测试读取受版本管理的 `tests/fixtures/extractor/real_paper_input.json`；它与原输入逐字节一致。验证目录从暂存树独立导出，没有复制本地被忽略的输出或环境文件。来源见 [导出记录](final-export-provenance.json)，结果见 [汇总](summary.json)。

这次追加仅修改测试路径、补入样本及发布说明，生产代码没有变化。原目录的 `source_inventory.json`、`implementation.patch`、`final_startup_v2`、`verify_delivery.py` 和 `validation_summary.json` 保留第 11 个提交 `cfa58d91dc9048d3072c3da372b815ec4ff38e31` 的历史语义；原验证器应在该历史提交上运行，不能拿其测试文件哈希声称最终测试文件未变。

最终上传源码使用本目录的 [清单](source_inventory.json) 和 [校验器](verify_source.py)：

```bash
python docs/experiments/20260927_harness_config_closure/publication_validation/verify_source.py
```

非在线回归与发布可复现性通过，原任务书整体验收仍未通过。
