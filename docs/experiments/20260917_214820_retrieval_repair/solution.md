# 本轮实施记录

代码基线为 `00256091346b641834003957721035f5dfa834e5`，修补尚在工作树、未提交。依次修改了 SearchPlan 保护概念字段及 fallback 传播、检索器的基础方向优先调度与有限检索调用预算、候选轮转保留、审计报告字段差分、模型请求边界记录、大载荷内容文件和运行目录整包归档。Planner、Provider 标准化返回与候选去向也有增量事件；并发点位的模型／工具记录含作用域与父阶段 ID。

新增 `fallback_protection`、`legacy_candidate_stop` 两个检索器开关，用于局部 B0/BF/BE/BFE 对照；默认启用修补后的规则。测试直接调用生产函数，Provider 使用不联网替身。

测试依赖临时安装在 `/tmp/nstab-python-deps`。当前聚焦回归 333 项通过，命令及结果见 `tests/validated-pytest.log`。审计更正命令：`python3 scripts/single_point_stability_audit.py --repo . --output docs/experiments/20260917_214820_retrieval_repair/analysis/audit-correction`。没有覆盖旧实验原件。

旧 `tests/test_plan_compiler.py` 有 5 条断言期望 broad 使用 OR 或 focus 覆盖 anchor，与基线实现冲突；原始失败输出保留在 `tests/compiler-existing-pytest.log`，现已把断言更新为当前生产模板并通过全文件测试。

`max_provider_requests` 限制上层逻辑检索调用；新增全运行物理 Provider 请求上限 48 与模型调用上限 130，均在发出 HTTP 请求前占额。Provider 内部重试与分页计入物理上限。测试覆盖 Provider 重试、arXiv Web 重试和模型第二次调用被拒绝。完整入口的配置与 PaperInput 在运行前写入隔离目录。

八项本地 `debug-ready` 验收通过。根据历史同一论文完整运行 66–110 次模型调用、约 1.84–4.04 元，本次预定上限 130 次模型调用、48 次物理 Provider 请求；单次费用仍取决于实际 token。首次启动在发出请求前遭自动审批拒绝；用户随后明确授权。完整实验运行一次并成功结束；模型 75 次、物理 Provider 请求 27 次、计费 2.0774424 元。先前自动审批阻断记录仍保留。运行命令和实际结果见 `runs/full/0001/run.json` 与 `analysis/live-run-metrics.json`。
