# arXiv 标识修复与 406 恢复路径验证

2026-09-28。修前基线 `4878dec`。用户同意继续修复后，本阶段开始修改生产代码；此前调查记录保持原样。

## 已修复：旧式 ID 在两处被截断

搜索 Atom 解析与 scheduler 的元数据批量匹配都曾用最后一个 `/` 分段提取 ID。现在共用 `atom_identifier`，保留 `/abs/` 后的完整路径及版本，再按原逻辑移除版本用于文献标识。`cond-mat/0011267v1` 能形成 `cond-mat/0011267`，并传递给元数据和全文工具。

修前新增的四个链路用例为 2 failed / 2 passed，见 [before.log](before.log)：旧式失败、现代 ID 通过。修后同组全部通过，同时验证搜索输出、元数据实际 id_list 参数和 HTML 全文请求地址。全文传输使用 MockTransport，不是在线全文可用性证明。

[真实响应离线回放](identifier_replay.json) 使用上一轮三个 Atom body，校验原哈希不变；12 个条目的标识、摘要和 PDF 地址全部正确，修前 6 处不匹配降至 0。脚本 [replay_identifiers.py](replay_identifiers.py) 不访问网络、不调用模型。它不会覆盖上一轮缺陷记录。

## 已改善：not_run 的直接失败关联

后续因 Provider 失败未执行的查询现在在 parameters 中保存：

- `blocked_by_execution_id`：实际失败的请求执行标识。
- `blocked_by_failure_event_id`：对应结构化失败事件。
- `blocked_by_failure_code`：原失败码。

原始失败仍保留，跳过项仍为 `not_run` / `coverage.not_executed`，不伪装成执行过的 406 或成功空结果。预算停止仍保留自己的原因；不扩大重试范围。

## 已验证的现有恢复行为

新增衔接测试从 HTTP 406 分类开始，经过 Workflow 证据不足检查、supplement 路由、目标任务与原计划复用，再进入 RecoveryToolRegistry：只允许调用显式配置的备用源，原失败源调用被拒绝。实际调用由 RecordingTool 记录，**不是备用源真实网络成功**。

已有机制的前提仍是 `recovery_provider_order` 配置了可用来源、`max_rounds` 允许下一轮，且没有预算等阻断。无备用源时停止；不把 406 当作无匹配或新颖性结论。本阶段没有改恢复决策算法、默认配置或启用新的外部服务。

## 验证结果及边界

[after.log](after.log) / [JUnit](tests.xml)：**120 passed**，覆盖 arXiv 工具/调度器、结构化检索、恢复闭环、检索修复、报告及检索工具输出。修复阶段新增网络请求 0、模型调用 0。

测试编写期间，衔接用例首次按 task_id 读取恢复映射而出现 KeyError；检查生产代码后改用其实际复合键，未为适配测试修改生产路由。首次 95 项检查通过后，补入该衔接用例及报告/工具覆盖，最终 120 项通过。这里不将测试编写错误计作生产缺陷。

本阶段源码已有变更，旧调查的 86 文件哈希清单仅代表当时基线，不再声称匹配当前源码。当前变更范围及哈希见 [validation.json](validation.json)。

**HTTP 406 服务端根因尚未解决。** 未改冒号编码、UA 或自动切网页通道：上一轮真实图查询已反证仅改编码不是通用修复。本阶段证明的是确定性 ID 修复和失败可追溯性，不能替代完整在线 Search→Evidence→Reviewer 验收。
