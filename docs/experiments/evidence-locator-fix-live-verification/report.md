# Evidence Locator 修复后全流程 Live 验证

## 结论

修复后真实全流程运行中，EvidenceCard 能正常通过 Validator，最终报告包含带
`supporting_card_ids` 的查新结论；此前“生成证据卡后全部被拒、报告无证据”的断链已闭合。

## 运行条件

- 论文：MG19333vrw（MinerU 文本层输入，复用 `outputs/MG19333vrw/paper-input`）
- 命令：`scripts/run_full_workflow_live.py --paper-json ... --max-rounds 1 --max-concurrency 1`
- 模型：全角色 `deepseek-flash`（通过 `NOVELTY_*_MODEL` 环境变量覆盖）
  - 说明：默认 SearchPlanner 模型（r1-qwen3-8b）当前持续输出 v2 schema 禁止的
    `concept_id/strategy_id` 导致规划失败，属于既有模型/提示词适配问题；本验证沿用
    此前成功实验的 deepseek-flash 全角色覆盖。
- 运行时间：2026-09-04T15:57 UTC – 16:15 UTC（约 18 分钟，含 6 个研究任务）

## 产物与结果

- 原始证据卡：1 张（NP-1/T-1，Museformer 论文）
- 通过 Validator：1 张，拒绝：0 张
- 拒绝原因“缺少原文摘录或原文位置”：0 条
- 证据定位示例：`artifact art_1a8c528bc80025cb8f47a55f chars:393-498`
- 报告结论：
  - NP-1：`weak`，`supporting_card_ids=[card_92068590e4b476859ca5f63b]`
  - NP-2 / NP-3：`insufficient`（真实零命中；报告明确说明“无被拒绝证据”，未把零命中写成技术性拒绝）

## 关键文件

- `outputs/MG19333vrw/full-workflow-after-locator-fix.json`
- `outputs/MG19333vrw/evidence-cards.json`
- `outputs/MG19333vrw/report.json`
- `outputs/MG19333vrw/report/MG19333vrw-report.md`

## 相关回归

- `tests/test_evidence_card_builder.py`：locator/location 非空、偏移映射、Validator 放行
- `tests/test_coordinator_json_robustness.py`：synthesize Markdown 围栏解析与重试
- 全量离线回归通过（排除既有的 Chromium runtime 环境用例与 `test_api.py` 生命周期用例）
- 旧 MG19333vrw 真实产物回放：`REPLAY_OK cards=3`
