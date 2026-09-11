# MG19333vrw 全流程实验报告

> 实验日期：2026-09-07<br>
> 实验对象：`examples/MG19333vrw.pdf`<br>
> 运行模式：MinerU 解析 + 完整查新工作流 + Runtime Debug<br>
> 最终状态：流程成功，证据覆盖不足

## 结论摘要

这次实验成功跑通了从 PDF 解析到 Markdown 报告生成的完整链路。MinerU 真实执行且没有回退；三个查新点均经过任务规划、检索、证据校验、Reviewer 复核和报告生成；两个报告完整性门也全部通过。

不过，“流程成功”不等于“查新结论充分”。系统最终只保留了 1 张有效 EvidenceCard，覆盖 NP-2；NP-1 和 NP-3 均没有达到每个查新点至少 1 张有效 Card 的门槛。因此，本次实验得到了一份结构完整、可审计的报告，但还不是一份三个查新点都得到充分证据支持的完整查新结果。

| 问题 | 结果 |
|---|---|
| 能否完成 PDF → 报告全流程？ | 能 |
| MinerU 是否真实成功？ | 是，未触发文本层/OCR 回退 |
| 是否生成结构完整的最终报告？ | 是 |
| 三个查新点是否都有充分证据？ | 否，仅 NP-2 达到证据门槛 |
| 调试数据是否完整保存？ | 是 |

## 实验目标

本次实验主要验证以下内容：

1. 使用 MinerU 3.4.5 解析真实论文 PDF；
2. 在不设置任何 `NOVELTY_*_MODEL` 角色覆盖的情况下，由默认的 `deepseek-flash` 完成全流程；
3. 关闭 evidence locator 强制门，但继续要求证据包含直接引文；
4. 验证 Runtime Debug 能否记录阶段输入输出、模型调用、工具调用、错误、Token、成本和完整性门结果；
5. 判断最终能否生成可阅读、可追溯的科技查新报告。

## 实验条件

| 项目 | 配置 |
|---|---|
| 代码分支 | `lya` |
| Git commit | `5909b50993fdad4de4caf49bb0ea0bf1a62930bb` |
| 输入 PDF | `examples/MG19333vrw.pdf` |
| 文件大小 | 2,023,977 bytes |
| PDF 页数 | 74 |
| 主模型 | `deepseek-ai/DeepSeek-V4-Flash` |
| 工作流轮数 | 1 |
| 最大并发 | 4 |
| 每点最低有效 Card 数 | 1 |
| 直接引文要求 | 开启 |
| 来源位置要求 | 关闭 |
| Reviewer | 开启，fail-closed |
| Runtime Debug | 开启 |

完整、无密钥的配置快照见 [`effective-config.json`](effective-config.json)。

## 执行过程

### 1. PDF 解析

MinerU 在 53.28 秒内完成 74 页 PDF 的解析，解析来源被记录为 `mineru`，没有触发回退。系统生成了全文 Markdown、结构化 content list、版面与坐标数据，以及 50 张论文图片。

章节检测给出了三项警告：未识别到 `methods`、`results` 和 `discussion`。这不代表论文缺少相应内容，而是章节标题没有被当前规则识别；后续查新点提取仍然正常完成。

### 2. 参考文献预处理

系统从论文中识别出 85 条参考文献，bootstrap 本身成功完成，但 85 条均未自动解析到外部作品记录：

| 指标 | 数量 |
|---|---:|
| 识别出的参考文献 | 85 |
| 自动 resolved | 0 |
| ambiguous | 0 |
| not found | 85 |
| 处理失败 | 0 |

这说明“参考文献列表已提取”，但“引用记录自动对齐”没有取得有效结果。它没有阻塞主流程，却削弱了后续利用论文自带参考文献扩展证据的能力。

### 3. 查新点与检索任务

PointExtractor 提取了 3 个查新点，Coordinator 和 SearchPlanner 共生成 6 个研究任务，每个查新点包含 2 个任务。

| 查新点 | 核心主张 | 最终状态 | 有效 Card |
|---|---|---|---:|
| NP-1 | Museformer 结合细粒度与粗粒度注意力，兼顾长序列和音乐结构建模 | 证据不足 | 0 |
| NP-2 | 使用相似度统计自动识别与音乐结构最相关的小节 | 部分创新 | 1 |
| NP-3 | 使用 block-sparse 实现低复杂度编码，并支持更长序列和更快运行 | 证据不足 | 0 |

6 个任务中只有 NP-2/T-2 正常完成，其余 5 个以 `partial` 结束。部分任务仍检索到候选文献，但在浏览、读取或预算阶段未能形成符合契约的最终证据。

## 最终结果

系统构建、校验并经 Reviewer 保留了 1 张 EvidenceCard：

| 阶段 | Card 数量 |
|---|---:|
| 构建 | 1 |
| Validator 接受 | 1 |
| Validator 拒绝 | 0 |
| Reviewer 接受 | 1 |
| Reviewer 拒绝 | 0 |

### NP-1：证据不足

没有形成与 Museformer 细粒度/粗粒度注意力核心贡献直接对应的有效 EvidenceCard，因此无法可靠评价该主张的新颖性。

### NP-2：部分创新

系统找到论文 *Generating Music with Structure Using Self-Similarity as Attention* 作为有效相关证据。该工作已将自相似度矩阵用于音乐结构建模，但主要使用用户提供的结构模板；MG19333vrw 主张从训练集相似度分布中自动确定结构相关小节，两者存在方法差异。

最终结论为“部分创新”，置信度为 0.7。由于只有一张有效 Card，该结论仍需要更多文献支持。

### NP-3：证据不足

检索过程没有形成直接覆盖 block-sparse 细/粗粒度注意力实现、复杂度下降和长序列能力的有效 EvidenceCard，因此无法可靠评价该主张的新颖性。

## 调试结果

Runtime Debug 完整记录了 25 个工作流阶段、79 次模型调用、65 次工具调用和 30 个可恢复错误。工作流最后仍正常到达 `render_report`，两个完整性门均通过。

### 工具调用情况

| 工具 | 调用 | 成功 | 失败 | 空结果 |
|---|---:|---:|---:|---:|
| Reference Search | 6 | 6 | 0 | 6 |
| Database Search | 6 | 6 | 0 | 3 |
| Web Search | 18 | 10 | 8 | 0 |
| Browser | 12 | 4 | 8 | 0 |
| Reader | 23 | 9 | 14 | 0 |

Reference Search 虽然调用成功，但 6 次均为空。Database Search 的调用稳定性较好，但一半查询没有命中。真正影响证据产出的环节主要是 Browser 和 Reader：Browser 成功率为 33%，Reader 成功率约为 39%。

### 主要失败模式

30 个调试错误均发生在单任务工具链内部，没有导致主工作流崩溃。主要问题如下：

1. **Artifact/SourceRecord 句柄不可解析。** 多次 Reader 或 Browser 调用了当前 namespace 中不存在的 `artifact_id` 或 `source_record_id`。这是证据读取失败的最大来源。
2. **工具预算耗尽。** 4 次任务耗尽总工具调用预算，另有任务耗尽 Browser 预算；这直接导致 5 个任务只能以 `partial` 结束。
3. **Reader 顺序策略冲突。** Database Search 返回 artifact 后，Harness 要求优先 Reader；模型的后续动作有 4 次被该策略拒绝。
4. **Baidu 查询过长。** 3 次搜索超过 Baidu 的 72-unit 限制，说明 SearchPlanner 或 Web Search Adapter 还需要做长度裁剪。
5. **动态页面读取不稳定。** Playwright 有 3 次在页面持续导航时无法读取内容。

Reviewer 专项诊断和 namespace 诊断均返回 `ok: true`。最终 Card 的 Evidence → Artifact 绑定能够正确解析，报告中引用的 Card 也通过了 provenance 与 report integrity 检查。因此，当前问题主要发生在候选证据形成之前，而不是最终证据链被错误接受。

## 性能与成本

### 时间

| 阶段 | 耗时 |
|---|---:|
| MinerU 与论文处理 | 53.28 秒 |
| Reference bootstrap | 0.64 秒 |
| 工作流墙钟时间 | 215.94 秒 |
| PDF → 最终报告 | 269.91 秒 |

6 个 Researcher 的累计任务耗时为 538.13 秒。该值高于工作流墙钟时间是正常的，因为任务以最大并发 4 并行执行。

### 模型调用与 Token

| 模块 | 调用 | Token |
|---|---:|---:|
| PointExtractor | 4 | 12,956 |
| SearchPlanner | 7 | 10,585 |
| Researcher | 64 | 527,236 |
| 报告汇总 | 1 | 55,477 |
| 未归类调用 | 3 | 14,178 |
| **合计** | **79** | **620,432** |

所有模型调用均返回了 usage 数据。输入 Token 为 603,601，其中缓存输入 Token 为 414,976；输出 Token 为 16,831，另记录 reasoning Token 3,110。

### 成本口径

Runtime Debug 按 2026-09-07 的当前价格表估算本次模型成本为 **0.8418468 元**。该结果使用 DeepSeek-V4-Flash 的日间价格：非缓存输入 3 元/百万 Token、缓存输入 0.3 元/百万 Token、输出 9 元/百万 Token。

`metrics.json` 中另有一项 0.23058652 元的旧实验脚本估算。它使用了 2026-08-31 写死在脚本中的旧费率，与当前 Runtime Debug 价格表不一致。为了避免误导，本报告以 Runtime Debug 的 0.8418468 元为当前估算；平台优惠、券、税费和账户侧实际结算仍不在此估算内。MinerU 为本地运行，不计 API Token 成本。

## 与上一轮实验的对比

| 指标 | 上一轮 | 本轮 |
|---|---:|---:|
| PDF parser | text layer | MinerU |
| 查新点 | 2 | 3 |
| 研究任务 | 4 | 6 |
| 构建的 EvidenceCard | 3 | 1 |
| Validator 接受 | 0 | 1 |
| Reviewer 接受 | 0 | 1 |
| 是否生成有效报告 | 否 | 是 |
| 总耗时 | 约 35 分钟 | 约 4 分 30 秒 |
| Token 是否完整记录 | 否 | 是，620,432 |

本轮在流程稳定性、运行速度、调试能力和最终证据闭环方面都有明显进展，但证据召回与读取的有效率仍不足。Card 数量从 3 降至 1 不应简单理解为效果退化：上一轮的 3 张 Card 最终全部被 Validator 拒绝，而本轮唯一的 Card 通过了 Validator、Reviewer 和完整性门。不过，两个查新点仍为零证据，说明系统离稳定产出完整查新结论还有距离。

## 对实验结果的判断

本次实验达到以下目标：

- MinerU 真实成功并生成结构化论文输入；
- 默认模型配置可以跑通完整工作流；
- Runtime Debug 能够完整记录阶段、工具、模型、成本和错误；
- 系统能够生成结构完整、引用闭环正确的最终报告；
- 至少一个查新点形成了有效证据和可解释结论。

本次实验尚未达到以下目标：

- 三个查新点全部满足最低证据门槛；
- 参考文献 bootstrap 形成可用的引用资产；
- 大多数研究任务正常完成；
- Browser 和 Reader 达到足以支撑稳定证据生产的成功率。

因此，最准确的实验结论是：**全流程已经可运行，也能生成一份完整格式的报告；但证据生产链仍不够稳定，本次报告只有一个查新点获得实质性结论，不能视为完整的科技查新成果。**

## 后续改进建议

建议按以下顺序处理：

1. 修复跨工具的 Artifact/SourceRecord 句柄恢复与 namespace 选择；
2. 在 Baidu Adapter 层确定性裁剪过长查询，而不是依赖模型自行缩短；
3. 调整 Harness 的 Reader 强制顺序提示和纠错逻辑，减少无效重试；
4. 根据检索命中情况动态分配工具预算，避免 Reader 错误快速耗尽整个任务预算；
5. 修复参考文献 bootstrap 的 85/85 `not_found` 问题；
6. 完成上述修复后，将 `max_rounds` 恢复为 2，验证补检回边能否为 NP-1 和 NP-3 补足证据；
7. 统一实验脚本与 Runtime Debug 的价格表，删除脚本内写死的旧费率。

## 产物索引

- 最终科技查新报告：`outputs/MG19333vrw-debug-full-20260907/report/MG19333vrw-debug-full-20260907-report.md`
- 结构化报告：`outputs/MG19333vrw-debug-full-20260907/report.json`
- 查新点：`outputs/MG19333vrw-debug-full-20260907/novelty-points.json`
- 检索计划：`outputs/MG19333vrw-debug-full-20260907/retrieval-plans.json`
- EvidenceCard：`outputs/MG19333vrw-debug-full-20260907/evidence-cards.json`
- Runtime 调试摘要：`outputs/MG19333vrw-debug-full-20260907/runtime/run-1978a1e85dc54f958289e728cc59dad6/summary.md`
- 完整实验指标：[`metrics.json`](metrics.json)
- 模型调用明细：[`model_calls.jsonl`](model_calls.jsonl)
