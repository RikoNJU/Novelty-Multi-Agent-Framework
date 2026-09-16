# MF2033k6lC 第二查新点（NP-2）主站通道实测报告

日期：2026-09-16 凌晨
执行：`search_transport="web"`，节流 8 秒，`candidate_limit_per_task=8`
驱动方式：用上一轮**真实落库的检索计划**（`retrieval-plans.json` 的 NP-2）走正式装配路径
（`build_structured_source_retrieval_tool` → `StructuredSourceRetrievalTool.ainvoke`），只换通道。

## NP-2 是什么

> 提出了一种基于图摘要的分布式图神经网络优化训练算法 DSGNN，采用领导-工作者模式，
> 领导节点利用基于边分割的图流划分算法对原图进行划分，工作节点执行基于图摘要技术的
> 小批量训练，并通过注意力层返回训练结果……在链路预测任务上的 F1 分数显著高于其他
> 分布式图神经网络模型。

NP-2 共有 4 个任务，其中 T-1 / T-R2-1 是**中文**任务。`enabled_task_languages=["en"]`，
真实链路不会执行，本次只跑英文的 T-2 / T-R2-2。

## 结果对比

| | 基线（API 通道） | 本次（主站通道） |
|---|---|---|
| arXiv 请求成功数 | **0**（429×4 + 超时×2，`http_200_count=0`） | 8/8 succeeded |
| T-2 | `partial`，0 bundle，0 evidence | 524.2s，6 次执行，**1 条候选（不相关）** |
| T-R2-2 | `completed`，3 evidence | 108.5s，2 次执行，**8 条候选 / 16 制品** |
| T-R2-2 证据来源 | 全部来自论文**自己的参考文献**（`subject_reference`），非检索所得 | 新增 8 条外部检索候选 |

基线那 3 条 evidence 的 `artifact_namespace` 是 `subject_reference` —— 即 AliGraph 等
是从论文自带引用列表里读到的，不是检索出来的。**基线的 NP-2 检索产出为零。**

## 通道侧：达标

- 8 次请求全部 `succeeded`，0 失败，8 秒间隔下未触发限流。
- 严格策略（S1）在 API 侧恒为 0 命中的那些"10 词级 AND"查询，主站同样 0 —— 行为一致。
- 元数据富化没有额外请求（结果页 abs 缓存预热生效）。

## 候选侧：质量差，而且瓶颈不在通道

### 1. T-2 的 1 条候选是假阳性

命中来自 `abs:graph AND abs:summarization AND abs:based AND abs:mini-batch AND abs:training`，
返回 2105.08330《Residual Network and Embedding Usage: New Tricks of Node Classification》——
一篇节点分类论文，与分布式 GNN 训练无关。它只是恰好同时含有这几个词。

**根因在查询构造**：`render_arxiv_term` 对超过 3 词的术语做词级 AND 拆分，
把 "graph summarization based mini-batch training" 拆成 5 个必含词，其中
**"based" 是纯粹的噪声要求**。要求摘要里同时出现 `based` 和 `mini-batch`，几乎必然 0 命中。
这在官方 API 上同样是 0 —— 不是通道的问题。

### 2. 放宽链第一步就丢掉了最重要的概念

T-R2-2 的 S1 是 `C1 AND C2`（两个概念 importance 都是 3）。放宽变体 `S1-fb1` 按
`(importance 升序, 概念序号升序)` 丢弃，结果丢掉了 **C1（distributed GNN training）**，
只剩 `abs:"graph summarization"` —— 一条宽泛的单主题查询，与查新点意图基本无关，
却因为它能返回 8 条而**提前终止了整条放宽链**（`len(unique) >= candidate_limit`）。

也就是说：一条跑偏的宽松查询，把后面更精确的 S2/S3 全部挡掉了。

### 3. 主站短语会做词干化，带来 ~24% 形态变体

对 `abs:"graph summarization"` 逐条核对：

- **加引号**：25 条中 19 条摘要**逐字**含 "graph summarization" → 引号确实按短语生效。
- **不加引号**：25 条中 **0 条**逐字命中，返回的全是"医院出院摘要""扩散语言模型"之类 → 退化为宽松 AND。
- 未逐字命中的 6 条，**全部**是同一个现象：摘要里写的是 "**graph summarizing**"
  （如 mapper/TDA 那批："constructs a graph summarizing the shape of a high-dimensional dataset"）。

即主站对短语做**词干化匹配**，"summarization" 会命中 "summarizing / summarized / summarize"。
所以那 8 条候选里，真正谈"图摘要"的可能不到一半，其余是拓扑数据分析的 "mapper graph summarizing"。
**这是与官方 API 的一个语义差异**（API 的 `abs:"..."` 是严格短语）。

## 时间成本

T-2 用了 **524 秒**（6 次执行 × ~87s），换来 1 条无关候选。
按 3 个查新点 × 2 个英文任务估算，纯检索开销在**半小时量级**，且期间无法并行（节流是串行的）。

## 结论与建议

1. **通道已经可用**，不再是瓶颈。同一份计划在 API 通道上 0 次成功请求，在主站通道上 8/8 成功。
2. **真正的瓶颈转移到了查询侧**，两个待修项都在计划/放宽链，不在 provider：
   - 长短语不该拆成含停用词的词级 AND（"based" 这类词应当被过滤或保留整短语）。
   - 放宽链不该优先丢弃最重要的概念；且一条跑偏的宽松查询不该终止整条链。
3. 主站通道的引用短语要预期 ~20% 形态变体噪声，候选需过一层相关性筛选。
4. 这 8 条 T-R2-2 候选建议人工/LLM 过一遍，但按上述分析，预期有效的不多。

## 这些候选能不能出卡：能，且已经实测跑通

用正式代码路径验证（`ReferenceArtifactReaderTool` → `EvidenceCardBuilder`），
引文机械取自读取结果以保证「引文有据」这一环不掺假：

| 环节 | 结果 |
|---|---|
| 落库产物 | 9 篇 × (摘要 + 全文)，全文 38–106 KB，全部 `text/plain` 可读 |
| `ReferenceArtifactReaderTool` 读取 | **9/9 成功**（硬上限 16K 字符/次，超长需按 `char_start` 翻页） |
| `EvidenceCardBuilder.build` | **9 draft → 9 cards，0 警告，9 条 evidence** |

出卡后的溯源链是完整的：每张卡的 evidence 都带
`read_id` + `read_char_start/end` + `quote_char_start/end` + `source_record_id`，
`EvidenceSource` 带 title / quote / location / url / doi。
落库的 `SourceRecord` 也齐：landing_url、full_text_url、abstract 都有。

**结论：主站通道的产物在「读→出卡」这一环没有任何结构性障碍。**
它和 API 通道的产物在下游无法区分——两条通道写的是同一套 Artifact/SourceRecord 结构。

真正决定「能不能出有用的卡」的是**候选相关性**，不是链路（见上文「候选侧」）：
9 篇里只有 CGS（可配置图摘要）与 COREKG（知识图谱摘要）与 NP-2 沾边，
而 NP-2 要的是「图摘要 + 分布式 GNN 训练」，这两篇都没有分布式训练部分。
其余 7 篇（mapper/TDA、代码摘要、光谱解释、节点分类）是宽松查询捞进来的噪声——
它们**能出卡，但出的卡对查新无意义**。

顺带验证出的两个真实缺陷（均已修复）：

- **摘要带折叠开关文字**：主站结果页 `abstract-full` span 末尾挂着 `<a>△ Less</a>`，
  `_clean` 只剥标签不剥文字 → 主站落库的 **9/9 篇摘要都以 `△ Less` 结尾**（API 通道没有）。
  已加 `_clean_abstract()` 剥除，线上复测 5/5 干净。
- **`external_id` 丢版本号**：API 通道是 `2504.14937v1`，主站原先填无版本形态 →
  同一篇论文换通道就多落一条 `SourceRecord`（实测 124 work / 125 记录，多出的正是
  Causal DAG Summarization），并让 `has no observed version` 警告对每篇候选触发。
  已按结果页 `id="<id>v<n>-abstract-*"` 与详情页 `og:url` 取回版本，
  离线复算证明修复后 record_id 与 API 通道那条**逐字相同**（`src_11143ab70...`），不再重复。

## 复现

```bash
# 正式链路（约 11 分钟）
python .workbuddy/tmp/run_np2_web.py

# 只看编译结果，不联网
python .workbuddy/tmp/dryrun_np2_web.py

# 短语语义核实
python .workbuddy/tmp/arxiv_web_phrase_fidelity.py
python .workbuddy/tmp/arxiv_web_phrase_miss.py

# 读→出卡全链路验证（不联网，读落库产物）
python .workbuddy/tmp/verify_web_cards.py

# 记录去重验证（不联网）
python .workbuddy/tmp/verify_record_dedup.py
```
