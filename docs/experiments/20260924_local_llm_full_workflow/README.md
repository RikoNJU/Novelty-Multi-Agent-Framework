# Local LLM 完整工作流实验

## 实验概要

- 论文 ID：`MF2033k6lC`
- 运行 ID：`run-f41ac741cf6f49deaa52124ae5b23903`
- 状态：`SUCCESS`
- 模型：`qwen2.5-7b-instruct`（vLLM / OpenAI-compatible API）
- 源码提交：`7e03fcca3eee05c9ce7b06ee9e74b5818b833726`
- 运行时间：2026-09-24 20:55:34 UTC 至 20:57:34 UTC
- 耗时：119.25 秒
- LLM 调用：30 次，均由本地 Qwen 完成
- Token：226,576 input / 3,204 output
- Tool Call：22 次

本目录是从 `outputs/local-llm-full-workflow/0002/` 中摘取的精简实验包。
原始论文输入和逐次 LLM/Tool 调试轨迹未重复收录；完整运行轨迹位于
`docs/experiments/runtime/MF2033k6lC_2026-09-24/`。

## 目录内容

- `effective-config.json`：当次运行的有效配置。
- `run.json`：运行元数据。
- `result.json`：工作流最终结果。
- `data/`：查新点、检索计划、候选审计、证据卡、评审和参考文献数据。
- `report/`：最终科技查新报告及其结构化 JSON。
- `runtime/`：已脱敏的运行摘要。

## 结果说明

工作流的所有主要阶段已成功执行，报告通过完整性门禁并成功落盘。
但本次检索未得到有效最终证据卡，NP-1 和 NP-2 的证据充分性均为
`INSUFFICIENT`。因此，该实验证明本地 LLM 可跑通完整工作流，不代表报告的
查新结论已获得充分文献证据。
