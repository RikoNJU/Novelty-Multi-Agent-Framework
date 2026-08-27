# Reader + ToolCallHarness 真实纵向预实验报告

## 1. 实验结论

本次实验成功验证了真实 LLM、原生 Tool Calling 协议、串行 `ToolCallHarness`、`ResearcherToolRegistry`、`ReaderTool`、`ReferenceArtifactReaderTool` 与真实 `ReferenceStore` 之间的完整纵向链路。

模型第一轮主动发出 `reader` tool call；Harness 未修改模型参数，经 Registry 调用真实 Reader 后，将读取结果以相同 `tool_call_id` 返回模型；模型第二轮基于真实 Artifact 文本生成了最终摘要。

实验状态：**成功**。

## 2. 实验范围

本实验仅验证 Reader vertical slice：

```text
临时 System Prompt
  → 真实 LLM
  → ToolCallHarness
  → ResearcherToolRegistry
  → ReaderTool
  → ReferenceArtifactReaderTool
  → ReferenceStore
  → ReferenceManifest + Artifact
  → role=tool result
  → 真实 LLM 最终回答
```

本实验不包含 WebSearch、Browser、EvidenceCardBuilder、Validator、并行 Tool Call 或完整 Researcher 生产工作流。

## 3. 实验环境与输入

| 项目 | 值 |
|---|---|
| 实验名称 | `reader-harness-smoke` |
| 执行时间（北京时间） | 2026-08-25 00:56:55 – 00:57:06 |
| 模型别名 | `deepseek-flash` |
| 模型 | `deepseek-ai/DeepSeek-V4-Flash` |
| Provider | SiliconFlow OpenAI-compatible API |
| Subject Paper ID | `MF2033k6lC` |
| Artifact ID | `art_1b4f8b3b8cb082d6ef83ed76` |
| 恢复的 Work ID | `wrk_0f9c0c8dac32a93811fff24c` |
| 请求字符范围 | `char_start=0, max_chars=3000` |
| 实际字符范围 | `[0, 1041)` |
| Harness turns | 2 |
| Tool calls | 1 |

API Key 由既有环境配置读取，未写入代码、日志或实验产物。`backend/.env` 已确认处于 Git ignore 状态。

## 4. 前置检查

正式调用 LLM 前，实验通过真实 `ReferenceArtifactReaderTool` 和 `ReferenceStore` 完成了本地预检，没有直接打开 Artifact 文件。

预检覆盖：

- `ReferenceManifest` 加载与 Artifact 查找；
- `artifact.relative_path` 安全检查；
- SHA256 一致性校验；
- UTF-8 文本读取；
- 有界字符切片。

预检结果：成功，耗时 **2.184 ms**，读取 1041 个字符。

预检期间发现既有 Manifest 包含 `publication_stage` 与 `publication_stage_provenance` 持久化字段，而当前基线 schema 不再接受这些字段。实验前已恢复最小兼容字段并补充 schema 测试，没有修改 Reader 或 Harness 的业务逻辑。

## 5. 实际调用轨迹

### Turn 1：模型选择 Reader

第一轮上下文角色：

```text
system → user
```

模型发出的原生 Tool Call：

```json
{
  "id": "01a034b42f2530ca7c662c58c622ba98",
  "name": "reader",
  "arguments": {
    "artifact_id": "art_1b4f8b3b8cb082d6ef83ed76",
    "char_start": 0,
    "max_chars": 3000
  }
}
```

Harness 将参数原样传给 Registry，没有 clamp、补写 `subject_paper_id` 或其他静默改写。可信的 `subject_paper_id` 由 `TaskResearchRequest` scope 注入 Reader。

### Tool 执行

真实执行路径：

```text
ResearcherToolRegistry.execute
  → ReaderArguments 校验
  → ReaderTool.ainvoke
  → ReferenceArtifactReaderTool.ainvoke
  → ReferenceStore.read_document_slice
```

执行结果：

- `succeeded=true`；
- Reader 工具耗时：**1 ms**；
- `read_id=read_f12f6808593c00bc9c5981d9`；
- 实际范围：`[0, 1041)`；
- `has_more=false`；
- Artifact role：`abstract`。

### Turn 2：模型读取 Tool Result

第二轮上下文角色：

```text
system → user → assistant(tool_call) → tool(tool_result)
```

Assistant Tool Call ID 与 Tool Result ID 均为：

```text
01a034b42f2530ca7c662c58c622ba98
```

模型第二轮未继续请求工具，并基于 Reader 返回的原文生成最终摘要，Harness 正常结束。

## 6. 耗时数据

| 阶段 | 耗时 |
|---|---:|
| 总 Harness 实验 | 10,549.330 ms |
| 模型调用合计 | 10,546.363 ms |
| Turn 1：Tool Call 决策 | 1,915.390 ms |
| Reader 工具执行 | 1 ms |
| Turn 2：最终摘要 | 8,630.973 ms |
| 本地 Reader 预检 | 2.184 ms |

模型调用占总 Harness 时间约 **99.97%**；Reader 本地读取耗时相对于模型调用可忽略。Turn 2 包含 1041 字符的 Tool Result 上下文及最终摘要生成，因此耗时显著高于 Turn 1。

## 7. Token 消耗

| 模型轮次 | Prompt tokens | Completion tokens | Reasoning tokens | Total tokens |
|---|---:|---:|---:|---:|
| Turn 1 | 571 | 120 | 23 | 691 |
| Turn 2 | 1,446 | 387 | 41 | 1,833 |
| **合计** | **2,017** | **507** | **64** | **2,524** |

两轮均无 prompt cache hit。第二轮 Prompt tokens 增至 1,446，主要来自原始 system/user 消息、assistant tool call 以及完整 Reader Observation。

## 8. 最终输出质量检查

模型最终输出正确识别文本主题为“基于视频时间压缩轨迹的烟雾检测与早期火灾预警”，并概括了：

- 现有视频烟雾检测方法的准确率与敏感性问题；
- 使用 CNN 提取动态轨迹特征、RNN 建模长程时间关系的方法；
- traj+CNN+RNNs 与 traj+SVM、CNN、C3D 等方法的比较结果；
- 方法在困难数据和早期弱小烟雾场景中的有效性。

摘要中的关键数值（如准确率提升 35.2%、真负率提升 15.6%、内存 2.31 GB 和帧率数据）均可在 Reader 返回文本中找到。本实验因此确认最终回答基于实际读取内容，而非根据 Artifact ID 猜测。

## 9. 实验过程中发现的数据缺口

本次纵向实验虽然成功，但同时暴露了两类需要后续处理的数据缺口。

### 9.1 真实引用只有摘要级文本

模型请求读取 3000 个字符，Reader 实际仅返回 1041 个字符，并给出：

```text
role = abstract
char_start = 0
char_end = 1041
has_more = false
```

这表明 `art_1b4f8b3b8cb082d6ef83ed76` 并不是完整论文文本，而是摘要级 Artifact；`has_more=false` 也说明当前 Artifact 后面没有更多内容可继续分页读取。

影响如下：

- 当前实验足以验证 Reader Tool Calling 协议和真实存储读取链路；
- 当前数据不足以验证长文档分段读取、跨段定位或全文证据提取；
- 最终摘要只能代表该摘要内容，不能视为对整篇文献的完整分析；
- 后续 EvidenceCardBuilder 或正式查新若依赖全文引文，必须先获得并持久化 `full_text` 或 `extracted_text` Artifact；
- Workflow 后续应显式区分摘要证据与全文证据，避免把摘要级读取误报为全文读取成功。

### 9.2 既有 Manifest 与当前 schema 存在版本差异

预检首次加载 `outputs/MF2033k6lC/references/list.json` 时，发现其中已经持久化：

```text
publication_stage
publication_stage_provenance
```

但从 `fcc78a9` 重开的当前 schema 未包含这两个字段，严格校验因此拒绝整个 Manifest，导致 Reader 无法访问 Artifact。此次通过恢复原有枚举及两个可选字段解决兼容问题，并增加了 schema 回归测试。

该问题说明当前 Reference Manifest 尚缺少明确的数据版本迁移机制：

- `STORAGE_VERSION` 尚未承担 schema migration 路由职责；
- 已持久化数据与代码回退/分支切换之间可能不兼容；
- 单个非 Reader 核心字段不兼容会阻断整个 Artifact 读取链路；
- 后续应设计显式 manifest schema version、向前/向后兼容策略或迁移工具，而不是长期依赖临时恢复字段。

### 9.3 本实验尚未覆盖的数据条件

本次只有一个摘要 Artifact 和一次从字符 0 开始的读取，尚未获得以下真实数据验证：

- 超过单次读取上限的长文本 Artifact；
- `has_more=true` 的连续分页读取；
- PDF 派生文本与原 PDF 页码/段落 locator 的绑定；
- 同一 Work 下多个版本或多个 Artifact 的选择；
- 中文摘要之外的完整正文、表格、公式和图片内容；
- Reader 输出进入 Evidence/EvidenceCard 后的引用定位完整性。

这些缺口不影响本次 Reader Tool Calling smoke 的成功结论，但限制了结论的适用范围。

## 10. 成功标准核对

| 成功标准 | 结果 |
|---|---|
| 真实 LLM 成功调用 | 通过 |
| LLM 收到 Reader ToolDefinition | 通过 |
| LLM 产生原生 Reader Tool Call | 通过 |
| Artifact ID 与读取参数正确 | 通过 |
| Harness 未静默修改参数 | 通过 |
| Registry 执行真实 ReaderTool | 通过 |
| Reader 读取真实 workspace Artifact | 通过 |
| Tool Result 使用相同 call ID | 通过 |
| 第二轮包含标准 assistant/tool trajectory | 通过 |
| 最终输出基于 Reader 文本 | 通过 |
| Harness Trace 完整写出 | 通过，共 6 条事件 |
| 结构化结果与最终文本写出 | 通过 |
| 实验输出不含 API Key | 通过 |

## 11. 实验产物

- `trace.jsonl`：Harness 的 6 条事实事件；
- `result.json`：实验状态、参数、成功标记、耗时与 token 汇总；
- `model_calls.json`：逐轮模型耗时、上下文角色、Tool Call 和 provider usage；
- `final.txt`：模型最终自然语言输出；
- `report.md`：本报告。

## 12. 结论与边界

Reader + ToolCallHarness 的真实纵向链路已经验证成功。协议层能够保留原生 Tool Call，Harness 能够串行执行真实 Reader，并用正确的 call ID 将 Tool Result 反馈给模型。当前性能数据表明，本地 Reader 不是该最小链路的耗时瓶颈，绝大多数耗时和 token 消耗发生在第二轮模型调用。

同时，本次读取的数据实际是摘要而非全文，且真实 Manifest 曾因 schema 版本差异无法加载。因此，本实验验证的是“真实摘要 Artifact 的 Reader vertical slice”，不能外推为全文读取、全文证据构建或持久化版本迁移已经完善。

本报告不证明完整查新流程已经可用。WebSearch、Browser、EvidenceCardBuilder 尚未接入，完整 Researcher 生产工作流也尚未迁移到 ToolCallHarness，并行 Tool Call 尚未实现。
