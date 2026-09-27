# Reviewer 读取失败分类与显式汇总恢复

日期：2026-09-28（延续 2026-09-27 任务包）。本分项补齐此前审计发现的机械失败分类与汇总恢复入口，不以产出 `reviewed` 当作语义正确性验收。

## 1. Failure → 复现

新增 `tests/test_reviewer_failure_classification.py`，修改前五项全部失败，见 [修前日志](reviewer-classification-before.log)：

1. Reviewer Reader 越权失败作为 `succeeded=false` 返回后，模型合法输出 insufficient，原实现无条件标 `semantic_evidence`。
2. 合法 reviewed 结果没有系统字段保存此前非阻断读取失败。
3. 已授权 Artifact 文件缺失，被材料目录过滤掉，后续读取误报 `outside reviewer scope`。
4. 已授权 Artifact SHA 不匹配同样误报越权。
5. 批量读取部分成功、部分材料缺失，最后合法 insufficient 仍被标为纯语义不足。

原汇总失败路径则返回空 `highly_relevant_works/review_evidence/feature_comparisons`。旧 `novelty-reviews.json` 通常仍保存单卡行，因此准确问题是点级结果未展示这些局部核验状态，且没有只恢复汇总的入口，而非磁盘上的单卡结果全部消失。

## 2. 分类修复与边界

`NoveltyPointReview.execution_issues` 使用统一 `FailureEvent`，由 Harness 写入，模型 Card/Summary Draft 不开放该字段。`reader_observations` 同样为系统字段，只保存成功 Reader 的 read_id、namespace、Work/Artifact、文件 hash、原始区间和文本 hash；不把正文再复制进模型汇总上下文。

- Registry 保留真实异常 `error_type`，不通过异常消息文字猜技术原因。
- 已授权但不可获取材料返回 `material.unavailable`；文件/文本完整性校验异常返回 `material.integrity`。已绑定 Artifact 从 manifest 消失同样记为材料不可获取。
- 任意未知/跨 Work Artifact 仍受原权限规则拒绝。没有通过恢复功能扩大 Reader 范围。
- 批量读取继续保留成功片段，失败项和结构化原因同时保留。
- 模型返回 insufficient 且存在读取失败时，结果不再仅宣称语义不足：纯材料不可获取归 `material_unavailable`，其他执行问题归 `technical_error`，并保留具体事件。
- 模型完成合法 reviewed 时，非阻断的读取失败只记录为 `limits_coverage`，不强制覆盖 verdict。这不等于模型 verdict 已被程序证明正确。
- 模型上下文超限、计量不可用、超时、Draft schema 和引用校验失败分别记录精确事件，原四类 incomplete_reason 继续兼容。

原因聚合是保守的执行状态说明，不声称机械失败是模型语义不足的唯一原因。通过结构/引用门控也不保证裁定有充分语义支持。

## 3. 显式 summary checkpoint / 恢复

新增 `agents/reviewer_checkpoint.py`。生产接线由主代理在工作流完成；本分项提供以下 API：

```python
attempt = await reviewer.summarize_with_checkpoint(
    request, card_rows, output_root=output_root, run_id=run_id,
)
# attempt.review 沿用原 NoveltyPointReview；partial_card_results 独立保留单卡状态。
recovered = await reviewer.recover_summary(
    request, output_root=output_root, run_id=run_id,
    checkpoint_id=attempt.checkpoint_id,
)
```

`ReviewSummaryAttempt` 明确区分 `completed/failed/checkpoint_unavailable`，返回 `durable`、checkpoint/attempt ID、点级 Review、原单卡结果和失败事件。合法语义不足属于已完成的汇总，不能借恢复入口重新采样争取其他 verdict。

每个 checkpoint 包含完整 request/run 绑定、不可覆盖的单卡原结果、源 Work/SourceRecord/Artifact 快照、Reviewer 选读登记、摘要日期、配置/模型身份及 Prompt hash；内容 hash 用于完整性检查。它是本地可信 Runtime 产物的防误用校验，不是对可任意重写文件攻击者的数字签名。

恢复必须给相同完整 request、run_id 和 checkpoint UUID，且配置/模型/Prompt 不变。程序重新执行原 Gate A 和单卡引用校验，再检查当前磁盘 Artifact 路径/文件 SHA/Work 绑定、原 Evidence Reader 范围/read_id/quote locator、增量 Evidence 的实际成功读取登记、选择范围、逐字引用与登记 ID。无原始读取来源的旧增量结果不能仅凭诊断 `ok` 获得恢复许可。

验证通过后只调用原工具禁用的 `summarize_reviews`。不进行数据库/网页请求，不重新运行单卡模型，不调用 Agent Reader；来源重验仍会读取本地原文件。首次摘要输入日期冻结，恢复不偷偷改变日期或模型条件。

每 checkpoint 最多显式恢复一次，用独占 attempt 目录防止并发重复请求。原单卡 snapshot 永远不覆盖，初次和恢复结果分别保存。汇总取消传播取消异常并保留 checkpoint；再次失败保留原单卡状态与各次失败记录。持久化失败不会返回 durable 成功。未通过来源验证时保留原 summary 调用兼容路径，但明确 checkpoint_unavailable，不授权之后恢复。

这里保存的是此前单卡核验的原始状态，包括局部支持、未知或不足，**不是把每条模型解释重新认证为正确科研事实**。恢复只重做汇总，也不保证新的汇总语义准确。

## 4. 离线回归

覆盖规则加入前，相关九文件 **132 passed in 3.01s**。覆盖规则后的八文件定向结果为 **125 passed in 2.59s**，见 [日志](reviewer-tests.log)、[JUnit](reviewer-tests.xml) 与 [源码/请求验证清单](reviewer-validation.json)，与主任务最终整合回归分别解释。包含：

- 五个修前失败用例、缺失 manifest、两类上下文错误；合法 reviewed 保留非阻断失败而不变 verdict。
- 真实既有 NP-3 论文 Artifact 上，summary 超时后保留单卡事实，仅一个 summary 请求即可恢复；同时覆盖增量选读的子区间。
- 跨 run/request、配置变化、源文件变化、伪造 Work、删除读取登记、错误范围/引文、改动 checkpoint hash 均在模型调用前拒绝。
- 缺失/重复/跨点单卡行拒绝，两个并发恢复只有一个获得调用机会；第二次恢复拒绝。
- 合法语义不足不允许重新采样；首次及恢复失败分别保留；取消后可恢复；初始/结果持久化失败不声称 durable。
- 相邻 Reviewer、Reader、诊断、工作流和报告原有契约继续通过。

旧九月真实材料用于来源验证，模型响应为确定性故障注入，不能把这些离线状态当成本轮模型语义准确率。

## 5. 固定真实材料的本地重复观察

脚本：[probe_reviewer_local.py](probe_reviewer_local.py)。观察目录：[reviewer_local_fixed](reviewer_local_fixed/)。原材料来自 2026-09-17 完整运行的 NP-3 / 2PS Card、摘要与全文 Artifact，不使用合成占位原文。

执行前冻结完整 request、配置、脚本和实际导入的 backend/env 与 Framework 源码副本；从该副本执行，后续其他代理编辑不会改变实验代码。模型固定本地 `qwen2.5-7b-instruct`，loopback 端点，温度 0，输出上限 1024，单卡最多两步/一次 Reader，三次相同输入，每次最多四个物理请求、全局最多十二个。不强制工具选择，不改 Prompt，不外检，不调用云模型。模型失败或预算不足原样保存。

三次已完成，共 **9 次本地物理模型请求**，每次样本 3 次：Reader 决策→单卡完成→点级汇总。没有格式修复、传输失败、预算超支或云调用。输入 38,854 / 输出 5,123 / 合计 43,977 tokens，请求耗时合计 286.881 秒；API 未定价，本地算力成本未知。三次 request hash 一致：`91bc705dff16749231dd3b180cc558cb8d894970fd3a4778bbe3c971969e5dc1`。

| 样本 | 单卡与汇总最终标签 | F1/F2 关系 | F3/F4/F5 | 来源门控 | 语义验收 |
|---|---|---|---|---|---|
| 1 | reviewed / not_novel | contradicted / direct_statement | unknown | 引用、绑定、登记合法 | 不通过 |
| 2 | reviewed / not_novel | unknown | unknown | 引用、绑定、登记合法 | 不通过 |
| 3 | reviewed / not_novel | unknown | unknown | 引用、绑定、登记合法 | 不通过 |

三次实际只选择读取原摘要 `[844,1397)`，尽管授权目录还提供全文。逐份重新核对文件 hash、逐字切片、Work 绑定均通过。原文支持的局部事实是 2PS 先做流式聚类，再进行边划分；该摘要没有直接证明其“未使用 Count-Min Sketch/最小堆”。样本 1 将未提及错误转成 contradicted/direct_statement；样本 2/3 的结构化特征均 unknown，但理由仍断言未采用，而且三者都给出 not_novel。不能把此结果解释为原文公开全部技术组合，或声称已经读取充分全文仍不能正确比较。

[逐条引文与语义核对](reviewer_semantic_audit.json)、[调用/用量汇总](reviewer_local_fixed/summary.json)、[冻结来源清单](reviewer_local_fixed/source_manifest.json) 和全部原始请求响应均保存。三次完成仅证明该固定材料下节点可以执行并保留引用；没有通过 Reviewer 语义正确性验收，不能把重复标签当稳定正确。

## 6. 新反例 → 限定结构一致性修复 → 固定输出回放

实验完成后，没有追加采样或改变原观察。先核对现有 Reviewer 业务约束：多篇分别覆盖部分特征不能等同单篇公开完整组合。因此对 `not_novel` 增加一条**必要而非充分**的确定性条件：同一 Work 必须对所有明确 technical_features 各有唯一 `supported` 比较及非空、已通过原引用门控的 Evidence 引用。

缺项、unknown、partially_supported、contradicted、重复同特征行、多 Work 拼凑和无明确特征均不能通过这一条件。失败转为 `insufficient_evidence/semantic_evidence`、verdict=null，记录 `review.missing_features`，保留原单卡局部比较、RelevantWork、登记引文；原模型 Draft 和 guard 前结果仍保存在 Runtime/固定回放证据。

此规则不按名称或否定词猜测 `contradicted` 是否真实，不将所有部分新颖性/次要 unknown 一刀切失败，也不能保证模型填写 supported 就确实获得原文支持。尤其样本 1 的错误局部关系仍原样保留为待审状态，不被程序假装修正为正确科研事实。

对三份冻结真实输出分别重放 card 和 summary，共 **6 份**：原 `not_novel` 均被拒绝，全部局部关系、Work 绑定与登记引文保持一致。见 [before/after 完整回放](reviewer_verdict_guard_replay.json)。此为已固定模型输出的程序规则验证，**不是新模型实验或修后语义准确率**。新增 14 项回归覆盖八种缺口、合法单 Work 完整支持、其他标签不被扩展规则覆盖，以及三份真实输出。

## 7. 操作与验收边界

恢复入口保持显式调用：从首次 `ReviewSummaryAttempt.checkpoint_id` 获取 ID，使用同一 `NoveltyPointReviewRequest`、原 run_id、output_root 和同配置 Reviewer 调用上面的 `recover_summary`。首次 summary 只有技术失败/取消/未写终态时才可恢复；合法 reviewed 或合法语义不足已完成后拒绝重新采样。一次恢复预算耗尽、并发重复、来源/范围/配置变化均拒绝；不自动重做 Research、检索或单卡 Reviewer。

工作流和正式报告中的 partial_card_reviews 接线由主代理负责另行回归。这些字段用于保留原单卡核验状态，并非把有疑点的局部关系标成已经确认无误。

本分项可验收：已复现读取失败分类、局部持久化、显式summary恢复、确定性标签/特征覆盖矛盾拦截。仍未验收：模型对真实论文特征的全面语义正确性，以及有充分全文支撑的正确最终查新裁定。现有反例为下一轮冻结 holdout，不以提高样本数或更换模型掩盖。
