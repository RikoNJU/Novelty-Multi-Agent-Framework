# 候选文献多但EvidenceCard少：逐篇追踪结论

结束时间：2026-09-15T19:46:23+08:00。本次仅分析已有三组产物并调用本地引文匹配函数复现，没有重新运行模型或检索服务，也没有修改产卡生产代码。前一轮renderer修改保持不变。

## 结论

**数量偏低不能完全解释为文献不相关。主要原因是阅读覆盖不足，以及任务预算耗尽后直接跳过产卡步骤；另有确定的引文改写导致Builder丢卡。Validator不是主要损耗点。**

| 指标 | 第一组 | 第二组 | 第三组 |
|---|---:|---:|---:|
| 新增数据库独立文献 | 0 | 16 | 16 |
| 其中被Researcher读取 | 0 | 6 | 3 |
| 获取全文 / 真正读取全文（不同文献） | 0 / 0 | 4 / 1 | 3 / 1 |
| partial任务 | 8 | 5 | 9 |
| partial任务中已成功读取次数（含原参考池、重复） | 22 | 20 | 24 |
| raw卡 / Validator后 / final卡 | 3 / 3 / 3 | 3 / 3 / 3 | 2 / 2 / 2 |
| 最终来自新增数据库的卡 | 0 | 1 | 1 |
| 最终来自原参考文献池的卡 | 3 | 2 | 1 |
| Web来源 / Web Artifact | 0 / 0 | 0 / 0 | 227 / 0 |

## 第二组16篇文献的去向

| 原因 | 篇数 | 证据 |
|---|---:|---|
| 未读取 | 10 | manifest已落盘，但没有对应Researcher read_results；不能断言均不相关 |
| 读取后任务预算耗尽，未进入Builder | 3 | 均出现在NP-1/T-2，最终partial、0卡 |
| 引文改写，被Builder丢弃 | 1 | HGP-IC，ungrounded quote |
| 已读取但未选入卡片，原因未记录 | 1 | LocalDGP |
| 成功产生数据库证据卡 | 1 | A two-phase streaming edge partitioning algorithm for large-scale uncertain graphs |

其余两张最终卡为AGL、AliGraph，来自原论文参考文献池，不属于新增16篇Springer文献。

第三组16篇：13篇未读取，1篇只在中断任务中被读取，HGP-IC再次引文失配，1篇《Scalability and performance in distributed graph databases》产卡。第二张最终卡AliGraph来自原参考池。

## 原因1：预算耗尽后，已读材料没有产卡机会（首要流程问题）

代码链：`core/tool_call_harness.py` 在总预算、单工具预算或轮数耗尽时抛ToolCallHarnessError；`workflows/research_task.py:ainvoke` 捕捉后直接 `_partial()` 返回。虽然保留read_results和research_bundles，却未调用evidence_builder.build，Evidence/Card字段保持空列表。正常模型完成且返回ResearchFinishDraft，才会调用Builder。

**典型案例：第二组NP-1/T-2**，成功读取9次、涉及5篇文献，其中《A Survey of Link Prediction in Temporal Networks》的全文被读5次；随后因total tool-call budget exhausted结束，0卡。该任务的3篇外部文献均未进入Builder，其余2篇为原参考池文献。其他多个任务因reference_search或web_search预算耗尽，走相同路径。

这不是“已有有效卡片被清空”：当前实现是在最后才统一构建卡片，所以中断时尚未产卡。也不能保证这些已读文献一定都能产有效卡，但目前没有给它们最后评估/提交的机会。

**建议修复：**

1. 将搜索预算与最终整理预算分开，预留至少一次不可再调用搜索工具的finalize机会。某个搜索工具耗尽时禁用它并返回结构化反馈，不应无条件杀死整个任务。
2. 每轮向模型提供剩余调用、读取和轮数预算；接近上限时停止扩展候选，优先整理已有Reader文本。
3. 对已有可验证引文采用增量草稿/检查点保存，再由Builder校验；最终产卡仍须有原文支撑，不能机械地把每个候选转为证据卡。
4. finalize失败仍标记partial并保留审计，不伪造证据；应有独立失败原因。

验收：构造先成功读取相关文本、再请求超额检索的任务，任务能进入finalize并尝试生成经校验的卡片；不能无限续费或突破原搜索预算。

## 原因2：只有候选选择，没有逐篇消费和闭环状态

目前database_search返回一批候选后只要求下一步至少读取一个Artifact，并不保证阅读完8个候选；Researcher随后可以继续reference_search/database_search/web_search。候选规模增长而读取预算固定，很多文献甚至没被查看。4份全文落盘不等于4份全文被读；第二组实际上只读取其中1份。

未读取文献和LocalDGP没有结构化排除理由，因此本次无法把它们标为“无关”，也无法精确推断模型未选择的动机。第三组甚至《Distributed Temporal Graph Neural Network Learning over Large-Scale Dynamic Graphs》等主题上可能相关的条目也没有读取记录，不能凭标题直接判定其证据价值。

**建议修复：** 建立候选处理台账，逐项记录discovered→queued→read→card/rejected/deferred及原因；先排序、再在预算内消费。为未读取项目明确写deferred_budget，不等于irrelevant。下一批搜索前检查当前高优先级队列；需要全面覆盖时为文献分配独立阅读/产卡任务，而不是让一个任务无限累积候选。

验收：每个候选都有明确终态或待处理状态；未读取候选不能被写作“不相关”；统计候选、已读、产卡、拒绝、延后应能闭合。

## 原因3：HGP-IC的引文改写导致两次丢卡

原始Reader文本：

```text
the "graph partitioning $$ + $$ + local learning" framework splits the global graph into smaller subgraphs for independent training
```

第二组模型写成 `graph partitioning + + local learning`，第三组写成 `graph partitioning + local learning`。提示已要求逐字引用，但模型仍改写了数学标记。Builder `_quote_matches` 对这两条均为false；原始逐字片段为true。见 [quote_reproduction.json](quote_reproduction.json)。

两次均在EvidenceCardBuilder阶段单卡丢弃，不是Validator拒绝。Builder成功保护了溯源要求，但当前流程只记录warning，没有给模型纠正这张卡的机会。

**建议修复：** 用Reader片段选择/字符范围确定引用，原文由程序回填；如仍采用模型逐字quote，Builder应返回逐卡可修复错误，并给一次有界纠正机会。若要规范化LaTeX，应在摄取阶段保留原文与偏移映射，不能靠模糊匹配放行改写后的引文。

验收：使用本次两条失败quote作为fixture，改写仍拒绝，逐字复制通过；一张失败不影响同任务其他卡，修复后保留正确出处和字符位置。

## 原因4：Web仅发现，没有网页获取路径

第三组227个Web source_record均无对应网页Artifact。browser关闭时，web_search本身只保存标题、链接和snippet；Reader没有可读网页制品，不能据此生成可验证引文。研究任务还出现把source_record_id误当artifact_id，以及反复Web搜索耗尽预算。

**建议修复：** 完整Web证据工作流显式开启并验证browser，执行web_search→browser→reader→Builder；仅发现模式则应禁用依赖browser的提示步骤，将候选标记待获取。不要放宽为用snippet直接证明论点。

## 排除项与边界

- 三组raw卡均全部通过Validator：3→3、3→3、2→2。不能把大量候选未产卡归因于Validator过严。
- EvidenceCardBuilder实际有2次已证实的引文丢卡，必须与Validator拒绝区分。其余未产卡并不意味着一定存在可恢复有效证据。
- Reviewer的判定失败或证据不足影响报告结论，不是本次大规模卡片数量损耗的环节。
- 全文可用、主题看似相关都不是强制产卡的充分条件；真正需要的是每篇文献可解释的处理状态，以及让已经读取的内容有正常结束和产卡的机会。

## 追踪附件

- [card_trace.md](card_trace.md)：第二、三组每篇数据库文献的读取与产卡去向，以及三组全部任务记录，均链接原始产物。
- [card_trace.json](card_trace.json)：含数据库、原参考池文献及227个Web来源的机器可读记录。
- [trace_cards.py](trace_cards.py)：仅使用已有产物的离线追踪脚本，可从仓库根目录复现。
- [quote_reproduction.json](quote_reproduction.json)：使用当前Builder匹配函数复现HGP-IC引用失配。
