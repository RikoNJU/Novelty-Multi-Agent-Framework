# 查新点、Reviewer、报告与恢复审查

审查日期：2026-09-27。本分项以现有运行产物、生产代码、离线契约测试和两次冻结输入的本地 Qwen 调用为依据。没有云端模型调用，没有重跑整篇论文，也没有改变检索范围来提高成功率。

## 1. 已核实的结论与边界

1. 20260924 本地完整流程的 Sketch-DBH 丢失发生在 **Point Extraction 的模型去重**，并非 ResearchTask、SearchPlan 或报告阶段丢失。模型首次已经提取到它，Digest 与去重上下文也都包含其独立贡献原文。
2. 该运行最终确认的 NP-1、NP-2 均有任务、检索方案、Review 与报告行；两点最终状态都是 `material_unavailable`，没有新颖性裁定。运行 `SUCCESS` 只表示流程和产物完成，不表示查新成功或覆盖完整。
3. Reviewer 主体已有材料、预算、技术与语义原因的四分类，但工作流外围兜底遗漏了原因；旧 Reviewer 接口失败还会遗漏整个 Review 行。本轮已修补并离线回归。
4. 查新点删除现在要求 `index → duplicate_of + reason`，且代表项必须保留。旧裸编号、非法映射、环和缺理由不再授权删除；保留候选明确标记 `pending_dedup`，不等于独立贡献已核实；范围待核验/不足警告由程序写入最终报告 limitations，避免只留在日志。
5. **点完整性尚未解决。** 新协议本地反例仍把 DSGNN 框架判为 Sketch-DBH 算法的重复项，并抄写理由模板。结构有效并不等于语义等价。**尚不能确认属于纯模型能力边界**，因为基于原文的语义复核、合并后的特征覆盖检查仍不充分。
6. 当前补检只看有效卡数，不消费 Reviewer 补查语义、Provider 失败原因或缺失特征；错误分类和恢复动作仍缺统一结构。本轮给出方案，不扩大成状态机重写。

## 2. 查新点完整生命周期证据

主要证据：

- 历史本地完整包：[20260924 README](../20260924_local_llm_full_workflow/README.md)。
- 原始轨迹：[point_extraction_trace.json](../runtime/MF2033k6lC_2026-09-24/run-f41ac741cf6f49deaa52124ae5b23903/diagnostics/point_extraction_trace.json)。
- 本轮机器可读账本：[integrity_ledger.json](integrity_ledger.json)，可用 [build_integrity_ledger.py](build_integrity_ledger.py) 只读重建。

| 原候选 | 首次提取 | 原去重动作 | 原补核 | 最终状态 |
|---|---|---|---|---|
| GSAERU | 候选 1 | 保留 | 重复返回 | NP-1，无绑定材料，不能裁定 |
| GSAERU_Summary | 候选 2 | 删除，无映射和理由 | 未恢复 | 可能是 GSAERU 实现/效果复述；不能仅凭该次删除认定重复 |
| DSGNN | 候选 3 | 删除，无映射和理由 | 换措辞恢复 | NP-2，无绑定材料，不能裁定 |
| Sketch-DBH | 候选 4 | 删除，无映射和理由 | 未恢复 | 提取阶段消失，没有任务；需恢复独立贡献核验机会 |

原始去重输出为 `{"delete_indices":[2,3,4]}`。代码只防越界和全部删空；一次从 4 条删至 1 条合法。之后有界补核只恢复 DSGNN，故生成最终两点。`deletion_reason` 原始记录明确为 `not provided by model`。Digest 的 `full_text_excerpt` 共 4,428 字符，含 Sketch-DBH、Count-Min Sketch、最小堆、常数时间查询与负载均衡的作者贡献段，因此不能归因于正文未送达模型。

最终 NP-1 和 NP-2 都有 T-1 英文 ResearchTask 与对应 SearchPlan；两点 EvidenceCard 均为 0。Reviewer 在无材料入口直接返回 `insufficient_evidence/material_unavailable`，两点均进入报告且 `verdict=null`。这次全流程没有执行有材料的 Reviewer 模型判断，不能把它计作 Reviewer 模型语义失败。

范围还出现特征损失：GSAERU 最终技术特征未保留 RNN 时序建模，DSGNN 补核后的列表未保留原先的边分割机制和注意力汇总。仅比较 point_id 或点数发现不了这些变化。未来账本须追踪作者声明/特征到最终点的多对多映射，不能用“三个点”替代语义覆盖。

## 3. 历史强弱模型差异的可比性

选取 20260917 的 `run-bdb2796a9ad145e2b741706bd4dd4368` 与本地 `run-f41ac741cf6f49deaa52124ae5b23903` 对照。

- 完整 PaperInput JSON 规范化 SHA-256 相同：`b7cd72c67823f7798be06dcb7d607719dace9b98257bc6c15f3fce95ea0dff5c`。
- `full_text` SHA-256 相同：`fc920613a33bc74930b6633b85c4e1f152b07cb6cacd29fd2c6fc19a988dfc33`。
- 历史模型为 DeepSeek-V4-Flash，本地为 Qwen2.5-7B；历史三个点包括 Sketch-DBH，本地最终只有两个。
- 两次首轮都为每点一个英文任务，但提取 Prompt、调用选项、代码及检索条件并非全部相同。历史请求未显式记录/设置本地请求中的 `max_tokens=8192, temperature=0.2`。不能将跨时间差异直接当作受控模型能力因果结论。
- 历史样本也有 Reviewer 不足、材料缺失或过度否定问题。20260918 Reviewer 专项验收明确记录“抽象材料没有提及”被误推为“未采用/contradicted”；稳定重复标签不等于语义正确，见 [稳定性验收报告](../20260918_reviewer_stability_acceptance/report.md)。

## 4. 本轮有界局部旧新协议对照

执行脚本：[replay_dedup_local.py](replay_dedup_local.py)。原始请求、响应、SHA-256、usage 与耗时在 [dedup_local_pair/manifest.json](dedup_local_pair/manifest.json)、[legacy.json](dedup_local_pair/legacy.json)、[mapped.json](dedup_local_pair/mapped.json)。脚本固定 loopback 端点，顺序最多两次调用，拒绝覆盖既有观察，无 Provider 检索或全文读取。未重复实验或追加 Prompt 调优。

保持历史 4 候选、贡献段、模型、温度、输出上限等参数相同，只改变去重输出协议及对应 Prompt。候选和贡献段分别冻结散列。每条件仅一次采样，不构成稳定性或准确率估计。

| 条件 | 实际返回 | 输入/输出 Token | 结果解释 |
|---|---|---:|---|
| 原协议 v5 | 删除 `[2,3,4]` | 2,331 / 14 | 复现历史裸删除；新 Harness 对该旧输出会保留 2/3/4 待核验 |
| 映射协议 v6 | `2→1`、`3→4`，理由均抄模板 | 2,515 / 63 | 引用映射形式合法，但 DSGNN→Sketch-DBH 语义错误；不能称点完整性已通过 |

共 4,846 输入、77 输出、4,923 Total Token；两个请求分别约 12.25 秒与 4.99 秒。仅是模型推理资源使用；API 计费为 `UNPRICED`，实际本地推理成本未知，未以 0 元代替未知。

该对照没有运行生成/补核/研究/报告，不能把新去重阶段剩余候选数当作新的全流程结果。映射规则是必要的审计约束，而非充分的删除正确性证明。后续可考虑将“源候选特征都被保留代表覆盖”的核查交给另一次语义判定，并在未完成时保留待核验范围；不能通过关键词相同或名称包含的程序规则冒充语义等价。

## 5. Reviewer 与 Report 审查

### 已存在且应保留的可靠边界

- `NoveltyPointReviewRequest` 检查 Card/Evidence/Point 绑定；Reviewer Reader 只授予目录内 Artifact。
- `_validate_review_references()` 检查 Work/Evidence 对应、Card 绑定、feature_id、非 unknown 特征的引用，以及新登记 ReviewEvidence 的作用域。
- 单卡、汇总使用不同 Draft；模型不再填写 Harness 拥有的原文证据登记字段。
- 单卡 checkpoint 持久化成功或失败状态。汇总 quote 投影携带明确选择并登记的 Reviewer 证据，记录显示/截断/遗漏状态和散列。
- `assemble_report_from_draft()` 与 `bind_reviews_to_report()` 对确认点逐一绑定 Review，覆盖缺失、重复和未知点会失败；裁定字段由程序从 Review 复制，报告模型不能另造判定。

### 本轮修复

`workflows/novelty.py::_insufficient_point_review()` 过去不设置 `incomplete_reason`；Reviewer 禁用、逐点异常、单卡全部异常和汇总异常走此路径后，报告 `_limited_summary()` 会因原因 None 使用“关键比较证据不足”，混淆技术失败与语义不足。现明确为 `technical_error`。旧 Reviewer 接口抛异常时，过去 `novelty_reviews=[]`，现给每个已确认点保留一条技术失败状态。

“全部单卡失败”只指 `row.status==failed`，该状态来自异常或非法返回，不是有效的语义不足结果。合法 `insufficient_evidence/semantic_evidence` 仍作为 completed 单卡进入汇总，专门回归确保不被改写。现代接口失败仍保留 Validator 已接受卡；未降低任何引用、原文或语义标准。

### 仍存在的缺口

1. **引用合法不等于裁定有支持。** `reviewed` schema 强制 verdict/reason/confidence，但不强制最终判断有覆盖关键特征的材料；空/全 unknown 比较仍可能产生 reviewed/novel。现有正则否定保护也不能证明语义准确，不能恢复成“一不确定就整点失败”。建议分开记录局部已核事实、关键未决事实和最终可裁定性，逐项核对引用支持。
2. **错误兜底丢失点级局部结论。** 单卡事实虽在 checkpoint 保存，汇总异常返回的点级 Review 是空事实列表。应在报告明确暴露“已有单卡事实、点级汇总未完成”，允许重跑汇总或重读指定材料，而非重新研究全点。本轮未改变此聚合行为。
3. **摘要预算不是完整语义保障。** 每卡 12,000 字符预算可显示部分 quote，并把其 ID 纳入允许引用集合；范围和 hash 可审计，但最终理由是否真的由显示的部分支持仍需语义核验。总体输入 Token admission 也需要 Runtime 单独保证。
4. **诊断契约有滞后风险。** `scripts/reviewer_diagnostics.py` 从 research-runs 建 Evidence 表，RelevantWork 检查未合并 `review.review_evidence`；合法引用新增 RE 证据时可能误报 missing Evidence。此项为代码确认的可达风险，本分项未生成独立误报样本，不能当作已证实的全流程事故计数。Reviewer-only smoke 无整套 workspace 的诊断 `INCOMPLETE` 也不能当模型失败。

## 6. 错误体系与针对缺口恢复方案

现有 `WorkflowIssue` 只有 node/code/message/severity/task_id；Reviewer `incomplete_reason` 只有四个大类；补检 `InsufficientFinalEvidence` 只有卡数。因此错误已有记录，却不能稳定推导是否 retry、换源、读取全文或停止。

建议增加一种可关联且可汇总的事件结构，先接在现有节点边界，不强制先建复杂状态机：

```json
{
  "event_id": "failure-...",
  "code": "review.output.reference_scope",
  "layer": "reviewer",
  "category": "contract",
  "scope": {"point_id": "NP-3", "task_id": "T-1", "card_id": "C-1"},
  "execution_status": "incomplete",
  "semantic_status": "not_adjudicated",
  "retry": {"allowed": true, "max_additional_attempts": 1, "same_input": false},
  "recovery": {"action": "repair_output", "target_ids": ["C-1"]},
  "conclusion_effect": "blocks_point_verdict",
  "cause_event_ids": [],
  "evidence_refs": [],
  "detail": "sanitized diagnostic"
}
```

| 事实类别 | 应保留的结论状态 | 有界恢复动作 | 不应自动做的事 |
|---|---|---|---|
| 无候选但所有计划成功执行 | coverage 已执行，语义待定 | 模型扩展语义方向/换策略 | 宣称已证实新颖 |
| Provider 401/403 | 技术阻塞，授权原因分别核查 | 更正认证/授权或换可用源 | 统一写成权限不足或盲重试 |
| 网络超时/429/5xx | 技术阻塞/部分覆盖 | 按 Retry-After/backoff 有界重试，预算后换源 | 把故障当零相关文献 |
| 406/协议解析失败 | 协议/响应异常，细因未确认 | 核对请求和 Provider 契约，必要换源 | 仅凭状态码断言认证错误 |
| 存在摘要但关键特征无材料 | 保留摘要可确认事实 | 对指定 Work 获取/读取全文 | 重跑已经成功的全部查询 |
| Reader scope/参数错误 | 工具动作失败 | 修正已知 Artifact/范围或参数一次 | 给模型重复消耗无效调用 |
| Reviewer schema/引用错误 | 技术不完整 | 同材料有界格式/引用修复 | 包装为语义不足 |
| 全部 Reviewer 因预算/超时失败 | 核验未完成，已有 Read/卡可保留 | 从持久化材料恢复卡或汇总 | 再跑全论文 |
| 部分特征匹配、关键特征 unknown | 保留局部对应，阻塞最终必要裁定 | 缺口清单驱动补读/补检 | 全部清空或强给 novel |
| 所有源不可用/预算耗尽/无新增材料 | 明确覆盖受限及终止原因 | 停止，输出受限报告 | 无限“再跑一轮” |

错误应按异常类型、HTTP 响应、工具结果和执行阶段分类；message 仅作说明，不作为唯一恢复依据。关联父事件可避免每次上抛都计成独立事故。Provider 外部恢复与模型输出修复分别消耗预算。是否影响最终裁定须按点和关键特征计算，而不是全局一刀切。

## 7. 验证与交付范围

- 修补前 Reviewer 新增断言 5 个失败：原因 None 四条、旧接口缺 Review 一条。
- 修补后及删除映射更改后，关联七个测试文件 **125 passed**（Novelty-web 环境，全部离线）。
- 本地模型仅进行了上节两次局部调用，服务正常；没有全流程成功声明。
- 生产更改限于 `agents/point_extractor.py`、去重 Prompt v6、`workflows/novelty.py`；测试为 `test_point_extractor.py` 与 `test_workflow_reviewer.py`。未更改用户本地 LLM 使用手册的既有修改。

复验命令：

```bash
/home/lya3106643285/miniconda3/envs/Novelty-web/bin/python -m pytest tests/test_point_extractor.py tests/test_workflow_reviewer.py tests/test_novelty_point_reviewer.py tests/test_report_binding.py tests/test_reviewer_stability.py tests/test_reviewer_evidence_repair.py tests/test_report_narrative_contract.py -o addopts='' -q
python3 docs/experiments/20260927_harness_config_audit/build_integrity_ledger.py
```

本地对照脚本需运行中的 loopback Qwen，且已存在观察文件时拒绝覆盖。当前新协议反例应作为下一轮冻结 holdout 保留；不能事后改写它来宣称修复成功。
