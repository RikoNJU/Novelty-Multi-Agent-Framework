# 局部 Evidence checkpoint 与显式恢复

本分项完成了显式启用的 `submit_evidence` 工具和任务内 checkpoint。模型可在一次成功 Reader 之后提交局部 `EvidenceCardDraft`；系统立即调用原 `EvidenceCardBuilder`，原子保存其接受的证据，再允许继续研究。后续模型、上下文、预算收尾、JSON 修复或最终 Builder 失败时，已保存卡片进入 `PARTIAL` 任务结果，原始失败原因保留。

这是 **Builder provenance 层**的保留机制，不表示 Validator 放行、Reviewer 完成或证据充分。原有后续门控仍照常执行。该分项包含离线故障注入和一次纯本地引导探针，共 2 次模型调用，没有云端模型调用，也没有重跑历史实验。本地探针使用既有合成原文 fixture，并非论文自主研究产生的证据。

## 1. 原问题及机械边界

此前 `TaskResearcherWorkflow._research()` 只有在最终模型返回合法 `ResearchFinishDraft` 后才调用 Builder。此前所有 Reader 读取即使已提供足够材料，模型后续超时、超上下文或收尾失败时，也只能返回读取观察，Evidence/Card 全空。恢复路径需要把“模型已有局部语义草稿”与“整轮已完成”解耦。

本次没有将所有 Read 自动升级为 Evidence。模型仍负责挑选原文、解释技术对应、陈述差异和置信度；Harness 只负责原 Builder 校验、完整 scope 绑定、原子保存、状态隔离和失败后的合并。

## 2. 接口与启用

配置字段为 `researcher.harness.enable_evidence_checkpoint`，默认 `false`。配置 schema/factory 由主代理接入，TaskResearcherConfig 已支持同名字段。显式启用时新增：

```json
{
  "name": "submit_evidence",
  "arguments": {
    "cards": [
      {
        "main_contribution": "模型撰写的技术贡献解释",
        "quotes": [{"quote": "逐字Reader原文", "interpretation": "技术对应解释", "confidence": 0.8}],
        "relevance": 0.8,
        "confidence": 0.8
      }
    ]
  }
}
```

参数复用原 `EvidenceCardDraft`；新增单次 1–16 张上限。模型不能传入 scope、run_id、invocation_id、Artifact 或 Evidence ID 来授权引用。工具使用原总工具预算与 `per_tool_limits.submit_evidence`，没有额外免费调用。实验 Profile 可设 `submit_evidence: 4`；未配置独立额度时仍受总调用预算限制。

工具返回 `accepted_card_ids`、`accepted_evidence_ids`、逐卡 `rejections`、当前 checkpoint 卡数，以及 `validation_stage=builder_provenance_only`。`durable=true` 仅在本地原子写入成功后返回。零卡接受表示本次草稿没通过 Builder，不表示检索无相关文献。

原 `ResearchFinishDraft` 路径不变；关闭开关时工具不注册、不创建 checkpoint session，也不改变原工具表。启用后仍要求最终 finish，checkpoint 不是终止工具。

## 3. 实现与隔离

实现文件：

- `backend/src/novelty_agent_framework/tools/evidence_checkpoint.py`：session、工具、独立 registry 与恢复。
- `backend/src/novelty_agent_framework/workflows/research_task.py`：显式启用和失败结果合并。
- `tests/test_evidence_checkpoint.py`：原文 fixture 故障注入。

每次 `ainvoke()` 创建独立 session、UUID invocation 和新 Registry。原工具对象复用，原 Registry 的目标论文排除和参数校验仍由其基类执行；成功 Reader 观察通过执行后的窄边界收集。没有修改共享 `core/tool_call_harness.py`，没有与上下文 admission 实现交叉写入。

每张局部卡仍由原 Builder 处理：原文必须来自当前 invocation 的成功 Reader，Work/Artifact/SourceRecord 必须在当前论文工作区 manifest 中绑定；歧义、跨 Work 引文、未读材料、Web 辅助材料和 LLM 摘要不能因此升级为 Evidence。

存储路径：

```text
<output_root>/<paper_id>/evidence-checkpoints/<完整请求规范化SHA256>/<invocation_uuid>.json
```

完整请求包括 paper/run/point/task/attempt/SearchPlan/target_identity。路径使用安全 paper workspace 与散列、UUID，模型不能控制任意存储路径。不同任务、运行、轮次、检索方案和同一 request 的多次 invocation 均隔离。文件通过既有 `_atomic_write_json()` 临时文件、fsync 和原子替换落盘。

文件保留成功 Reader 切片、当前每个 Card 的已接受草稿、Builder 产物、所有提交的 Builder 历史、执行状态及已知失败原因。单个 Work 保持一个稳定 Card ID，后续合法提交可修订它；旧 Builder 产物仍在 `submission_history`，不会因修订消失。最终合法 finish 对相同 Card ID 的修订优先；finish 未重复提交某个 checkpoint 卡不会将其删除。输出按保留下来的 Card 引用收集 Evidence，避免悬空 ID。

## 4. 显式恢复边界

Python 调用：

```python
result = researcher.recover_checkpoint(request, invocation_id="运行产生的32位UUID")
```

此方法不调用模型、不重新检索、不重启工作流。必须显式给 invocation，完整 request 与 envelope 必须一致；没有“找到最近一次结果自动续跑”的旁路。

恢复时不相信文件内缓存的 Card/Evidence ID。它重新检查：

1. schema 版本、invocation 和完整 scope；
2. 当前目标论文排除规则；
3. 当前 manifest、Artifact 路径和文件 SHA-256；
4. 原 Reader 的 namespace、Work、Artifact、字符范围、文本和 read_id 是否完全一致；
5. 对保存的已接受草稿重新执行原 `EvidenceCardBuilder`。

保存的无关空 EOF 切片通过至少 1 字符的合法读取窗口重读，并要求结果仍与原空切片完全相同；不会因 `max_chars=0` 使整个合法 checkpoint 失效，也不绕过 Artifact 与切片核验。

任何 scope 越界、切片/文件变化、目标论文识别变化或 Builder 重校验失败均拒绝恢复。恢复结果固定为 `PARTIAL`，附原执行状态和已知原始失败原因；不会把故障变成 `SUCCESS`。取消或进程终止来不及写终态时，已确认 checkpoint 可从 `in_progress` 恢复，但报告明确原执行未完成，不能虚构具体中断原因。

当前最小恢复接口以整个 checkpoint 为单位重校验；任一保存 Artifact 已变更或不可获取时会拒绝该 checkpoint。它还不是逐卡容错恢复、全图断点续跑或模型上下文恢复。SearchExecution 和完整工具轨迹仍由原 Runtime/TaskResearchResult 承担，不能把这个文件当作一次完整实验记录。

## 5. 离线证据

使用既有 `test_evidence_card_builder.py` 的两段原文 fixture、Work/SourceRecord/Artifact 数据，补齐真实文本文件与 SHA 后，通过真实 Reader 和原 Builder 执行。模型仅为确定性的 fault-injection stub；没有将 mock Builder 的成功当作真实证据接受。

| 验证情景 | 结果 |
|---|---|
| 先 Reader→submit，后模型请求失败 | 保留 1 张 Builder 卡，任务 PARTIAL，原错误保留 |
| 同样流程后真实 `ModelContextAdmissionError` 类型拒绝 | 同上，无上下文失败伪装为成功 |
| 工具/轮次额度耗尽且预留收尾请求失败 | 保留局部卡并保留预算收尾及底层错误 |
| 最终 JSON 非法且修复失败 | 保留局部卡，PARTIAL |
| 最终 Builder 抛异常 | 保留此前已经接受的局部卡 |
| 原文不存在、未读取或来自另一个未读 Work | 0 张卡；草稿不升级 |
| Web 辅助材料、LLM 生成摘要 | 原 Builder 拒绝，0 张卡 |
| 低置信度但有原文的草稿 | Builder 可产卡，原 DefaultEvidenceValidator 继续拒绝 |
| 正常 finish 与 checkpoint 引用相同 Work | 稳定 ID 去重，原完成路径兼容 |
| 后续合法修订同 Work | 当前卡更新，旧 Builder 结果保留在提交历史 |
| 同一研究器对象重复或并发调用 | session/读取/卡不串任务；不同 invocation 文件隔离 |
| 跨 run/task/point/attempt/SearchPlan 提交或恢复 | 拒绝 scope 不匹配 |
| checkpoint 已确认后取消 | 原调用仍传播取消；可显式恢复为 PARTIAL |
| 修改本地 Artifact、目标论文身份或来源类型 | 重读/原门控拒绝恢复 |
| 伪造缓存的 Evidence/Card 字段 | 忽略缓存并从原文重新Builder；伪造无依据草稿被拒绝 |
| submit_evidence 独立额度为 1 | 第二次提交被原 Harness 预算阻止，没有绕过额度 |
| 同时保存有效引用与无关空 EOF 读取 | 原空切片可合法重读，完整 checkpoint 恢复成功 |
| checkpoint 原子持久化抛 OSError | 工具失败且不返回 durable 成功；未生成 checkpoint；内存中的 Builder 卡保留并附持久化失败警告 |

另对正常保存结果调用原 DefaultEvidenceValidator 与 Synthesis Integrity Gate A，确认原有正确引文可以继续通过，不只是在新 checkpoint 内自证。

最终相关八文件：**77 passed in 1.19s**。JUnit 记录：[checkpoint-tests.xml](checkpoint-tests.xml)；计数及本分项源码 SHA：[checkpoint-validation.json](checkpoint-validation.json)。

```bash
/home/lya3106643285/miniconda3/envs/Novelty-web/bin/python -m pytest \
  tests/test_evidence_checkpoint.py tests/test_task_researcher_workflow.py \
  tests/test_evidence_card_builder.py tests/test_evidence_builder_contracts.py \
  tests/test_research_finish_parsing.py tests/test_researcher_prompt_policy.py \
  tests/test_research_skills.py tests/test_target_paper_identity.py \
  -o addopts='' -q
```

## 6. 有界本地引导探针

在 `http://127.0.0.1:8000/v1` 的 `qwen2.5-7b-instruct` 上执行一次链路探针，脚本为 [probe_checkpoint_local.py](probe_checkpoint_local.py)。只调用本地模型，固定温度 0、单请求最大输出 1024 tokens；使用原有 `tests/test_evidence_card_builder.py` 的**人工编写合成原文 fixture**及真实磁盘 Artifact。没有数据库/网页检索，不是模型自主找到的论文证据。

两次请求分别显式指定 `reader` 和 `submit_evidence` 工具，并提供固定原文和引用指引。收到 Builder 接受且 `durable=true` 的确认后，在第三次模型调用边界直接注入 `RuntimeError("injected_failure_after_acknowledged_evidence_checkpoint")`，第三次请求不会发往模型。其用途是验证真实本地模型工具参数、Reader、Builder、持久化和恢复能串联，不能等同于自主研究及时提交 checkpoint 或证据语义充分。

| 观测 | 结果 |
|---|---|
| 实际本地模型调用数 | 2 |
| Reader 调用 / submit_evidence 调用 | 1 / 1 |
| 使用量 | 输入 5793、输出 243、合计 6036 tokens |
| 两次模型请求耗时 | 5.135s / 14.309s |
| 故障后任务状态 | PARTIAL |
| 原始失败原因 | `injected_failure_after_acknowledged_evidence_checkpoint` 留在结果 warnings |
| Builder 卡 / Validator 接受 / Integrity Gate A 接受 | 1 / 1 / 1 |
| 显式恢复与原保留卡及 Evidence ID | 一致 |
| Reviewer | 未执行 |
| 云端调用、检索调用 | 0、0 |
| 实际推理成本 | 未知，计费状态 UNPRICED，不声称为零成本 |

具体语义反例仍存在：合成原文只有 `Alpha unique quote.` 等占位句，模型却在 interpretation/main_contribution 中写入 distributed GNN 与 graph summarization。这些解释并没有由该原文证明。Builder/Validator/Gate A 的通过只证明该探针满足相应来源、引用和结构门控；未运行 Reviewer，不能把这张卡当作有效科研证据。

[summary.json](checkpoint_local_guided/summary.json) 记录结果；[call-1.json](checkpoint_local_guided/call-1.json) 和 [call-2.json](checkpoint_local_guided/call-2.json) 保留固定请求、响应、各自 SHA-256、usage 和耗时；同目录保存实际 TaskResearchResult、恢复结果、checkpoint 及原始 fixture。脚本拒绝覆盖输出目录，便于避免重复实验与混淆记录。

## 7. 当前结论

已证明“模型已经提交且通过原 Builder 的局部证据，不再因后续研究步骤失败而整批丢失”。本地探针确认引导条件下的实际调用链路可用；未证明模型在自主 live 研究中会及时或正确调用 submit_evidence，未证明保存的卡具有充分语义支持，也未验证 Reviewer 最终裁定。是否值得默认启用，应由固定输入、固定预算的后续局部对照评估；不能通过放宽原文验证或跳过 Validator/Reviewer 来提高 checkpoint 卡数。
