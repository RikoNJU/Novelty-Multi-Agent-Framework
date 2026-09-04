# 实验记录：MG19333vrw 完整工作流 Live 运行（DeepSeek-Flash 全角色）

## 实验概述

| 项目 | 内容 |
| --- | --- |
| 实验名称 | MG19333vrw 完整工作流 Live 运行 |
| 论文 | 《面向长序列和音乐结构建模的生成模型研究》（南大硕士论文，PDF：`examples/MG19333vrw.pdf`） |
| 论文处理 | `processing.cli --parser text_layer`，全文 71,923 字符，`outputs/MG19333vrw/paper-input/` |
| 模型 | **全角色 deepseek-flash（deepseek-ai/DeepSeek-V4-Flash）**：查新点提取 / 协调器 / 检索规划 / 研究员 / 评审 |
| 环境 | conda `Novelty`（Python 3.11，langgraph 1.2.11，pydantic 2.13.4），SiliconFlow API |
| 运行时间 | 2026-08-30（完整一次运行约 35 分钟，含 6 次模型调用链 × 4 研究任务） |
| 运行命令 | `scripts/run_full_workflow_live.py --paper-json ... --max-rounds 1 --max-concurrency 1` |
| 关键提交 | `fae5a99`（+ 未提交的收尾 JSON 围栏剥离修复 `research_task.py`） |

## 各阶段结果汇总

| 阶段 | 结果 |
| --- | --- |
| ① 查新点提取 | ✅ 2 条（比 R1 的 3 条去重更好，无重叠） |
| ② 协调器规划 | ✅ 4 个检索任务（2 点 × 中/英） |
| ③ 检索计划（planner） | ✅ 4 份计划，表达式 DSL 校验全部通过 |
| ④ 研究循环 | ✅ 3/4 任务 completed（各产 1 张卡），1/4 partial（工具预算耗尽） |
| ⑤ 证据构建 | ✅ 3 张高质量卡（均指向 Museformer 原文 arXiv:2210.10349） |
| ⑥ 证据验证 | ❌ 3/3 被拒："缺少原文摘录或原文位置"（**locator 恒为 null 的系统缺陷**，见下文） |
| ⑦ 评审 + 报告 | ✅ 完整报告生成（结论 insufficient + 缺失基线清单） |

## ① 查新点（完整收录）

来源：`outputs/MG19333vrw/novelty-points.json`（DeepSeek-Flash 提取）

### NP-1：Museformer 注意力机制

- **claim**：提出Museformer模型，一种结合细粒度和粗粒度注意力的Transformer变体，用于音乐生成中的长序列建模和音乐结构建模。
- **claim_en**：Proposes Museformer, a Transformer model with a novel fine- and coarse-grained attention, for long sequence and music structure modeling in music generation.
- **technical_features**：
  - 细粒度注意力机制：每个token直接关注与音乐结构最相关的小节的所有token
  - 粗粒度注意力机制：每个token只关注其他小节的总结信息，减少计算成本
  - 结合两种注意力，同时捕获音乐结构相关信息和上下文信息
- **technical_features_en**：Fine-grained attention: a token of a specific bar directly attends to all the tokens of the bars most relevant to music structures / Coarse-grained attention: a token only attends to the summarization of the other bars rather than each token of them / Combining the two attention mechanisms...
- **source_locations**：`论文摘要`（⚠️ 泛化来源，非原文精确句）

### NP-2：相似度统计确定结构相关小节

- **claim**：提出使用相似度统计的方法探究音乐结构，并据此确定与音乐结构最相关的小节（如之前的第1、2、4、8小节），用于细粒度注意力机制。
- **claim_en**：Proposes to use similarity statistics to explore the structures of music, and based on the results to determine the structure-related bars (e.g., the previous 1st, 2nd, 4th and 8th bars), which are used in the fine-grained attention.
- **technical_features**：使用相似度统计方法分析音乐中的重复结构 / 根据相似度统计结果确定结构相关小节（前1、2、4、8小节）/ 将确定的结构相关小节作为细粒度注意力机制中每个token直接关注的对象
- **source_locations**：`论文摘要`

## ② 协调器规划

4 个检索任务（每个查新点 × 中文/英文各一）：

| 任务 | 查新点 | 语言 | 描述 |
| --- | --- | --- | --- |
| T-1 | NP-1 | zh | 针对该查新点执行中文文献检索。 |
| T-2 | NP-1 | en | 针对该查新点执行英文文献检索。 |
| T-1 | NP-2 | zh | 针对该查新点执行中文文献检索。 |
| T-2 | NP-2 | en | 针对该查新点执行英文文献检索。 |

## ③ 检索策略（完整收录）

来源：`outputs/MG19333vrw/retrieval-plans.json`（每任务一个 SearchPlan，DSL 校验全部通过）

### NP-1 / T-1（中文）——6 概念

| 概念 | 角色 | 词项（terms） | 别名（alias） | 重要性 |
| --- | --- | --- | --- | --- |
| C1 Museformer模型 | object | Museformer模型 | Museformer | 3 |
| C2 细粒度注意力 | method | 细粒度注意力、粗粒度注意力 | fine-grained attention、coarse-grained attention | 3 |
| C3 Transformer变体 | method | Transformer变体 | Transformer模型 | 2 |
| C4 音乐生成 | setting | 音乐生成 | 音乐创作、自动作曲 | 2 |
| C5 长序列建模 | feature | 长序列建模 | 长序列处理 | 2 |
| C6 音乐结构建模 | feature | 音乐结构建模 | 音乐结构分析 | 2 |

| 策略 | 表达式 | 描述 |
| --- | --- | --- |
| S1 strict | `C1 AND C2 AND C3` | Museformer模型 AND 细粒度注意力 AND Transformer变体 |
| S2 medium | `C1 AND C2 AND C4` | Museformer模型 AND 细粒度注意力 AND 音乐生成 |
| S3 broad | `C4 OR C5 OR C6` | 音乐生成 OR 长序列建模 OR 音乐结构建模 |

### NP-1 / T-2（英文）——6 概念

| 概念 | 角色 | 词项 | 别名 | 重要性 |
| --- | --- | --- | --- | --- |
| C1 Museformer | object | Museformer | — | 3 |
| C2 fine-grained attention | method | fine-grained attention、coarse-grained attention | fine and coarse attention、hybrid attention | 3 |
| C3 Transformer model | method | Transformer model | Transformer architecture、Transformer variant | 2 |
| C4 long sequence modeling | feature | long sequence modeling | long-range modeling、long-context modeling | 2 |
| C5 music structure modeling | feature | music structure modeling | musical structure modeling、structure-aware music generation | 2 |
| C6 music generation | setting | music generation | symbolic music generation、automatic music composition | 1 |

| 策略 | 表达式 |
| --- | --- |
| S1 strict | `C1 AND C2 AND C3` |
| S2 medium | `C1 AND C2 AND C4 AND C5` |
| S3 broad | `C2 OR C4 OR C5 OR C6` |

### NP-2 / T-1（中文）——4 概念

| 概念 | 角色 | 词项 | 别名 | 重要性 |
| --- | --- | --- | --- | --- |
| C1 相似度统计 | method | 相似度统计、相似度分析、重复结构分析 | similarity statistics、similarity measure、repetition detection | 3 |
| C2 音乐结构 | object | 音乐结构、乐曲结构、歌曲结构 | music structure、song structure、musical form | 2 |
| C3 结构相关小节 | feature | 结构相关小节、关键小节、重复小节 | structure-related bars、salient bars、repeated bars | 3 |
| C4 细粒度注意力 | method | 细粒度注意力、细粒度注意力机制、局部注意力 | fine-grained attention、token-level attention、local attention（exclude: 全局注意力、多头注意力） | 3 |

| 策略 | 表达式 |
| --- | --- |
| S1 strict | `C1 AND C2 AND C3 AND C4` |
| S2 medium | `C1 AND C2 AND C4` |
| S3 broad | `C1 OR C2` |

### NP-2 / T-2（英文）——5 概念

| 概念 | 角色 | 词项 | 别名 | 重要性 |
| --- | --- | --- | --- | --- |
| C1 similarity statistics | method | similarity statistics、repetition structure analysis | similarity measure、structural similarity | 3 |
| C2 music structure | object | music structure、musical form | song structure、piece structure | 2 |
| C3 structure-related bars | feature | structure-related bars、structural bars | salient bars、key bars | 3 |
| C4 fine-grained attention | method | fine-grained attention、token-level attention | fine-grained attention mechanism、token-wise attention | 3 |
| C5 music generation | setting | music generation、music composition | symbolic music、score generation | 1 |

| 策略 | 表达式 |
| --- | --- |
| S1 strict | `C1 AND C3 AND C4` |
| S2 medium | `C1 AND C2 AND C3 AND C4` |
| S3 broad | `C1 OR C2 OR C3 OR C4 OR C5` |

### 实际执行查询与命中情况

每个策略在 arXiv 执行时自动附带放宽变体（`S*-fb1`，零命中放宽链），中文任务额外执行 null_catalog（测试目录）。

**命中统计**：

| 任务 | 关键命中 |
| --- | --- |
| NP-1/T-1（zh，arXiv） | S2-fb1 命中 1 条（Museformer 原文）；S1/S3 及变体 0 命中 |
| NP-1/T-2（en，arXiv） | S1-fb1 命中 1 条；S3 命中 8 条（含 Museformer 原文等） |
| NP-2/T-1（zh，arXiv） | S2-fb1 命中 1 条；S3 命中 7 条（partial） |
| NP-2/T-2（en，arXiv） | S3 命中 8 条 |

**示例执行查询**（NP-1/T-2，完整清单见 `outputs/MG19333vrw/retrieval-plans.json`）：

```
# S1 strict（0 命中）→ S1-fb1（命中 1 条：Museformer 原文）
ti:"Museformer" AND (abs:"fine-grained attention" OR abs:"coarse-grained attention") AND abs:"Transformer model"
ti:"Museformer" AND (abs:"fine-grained attention" OR abs:"coarse-grained attention")

# S3 broad（命中 8 条）
(abs:"fine-grained attention" OR abs:"coarse-grained attention" OR abs:fine AND abs:and AND abs:coarse AND abs:attention OR abs:"hybrid attention")
OR (abs:"long sequence modeling" OR abs:"long-range modeling" OR abs:"long-context modeling")
OR (abs:"music structure modeling" OR abs:"musical structure modeling" OR abs:"structure-aware music generation")
OR (abs:"music generation" OR abs:"symbolic music generation" OR abs:"automatic music composition")
```

⚠️ 查询质量观察：adapter 把别名 "fine and coarse attention" 按空格 token 化后生成了 `abs:fine AND abs:and AND abs:coarse AND abs:attention` 这类噪声片段（S2/S3 查询中），不影响正确性但降低检索精度。

## ④ 研究循环（逐任务）

| 任务 | 状态 | 步数 | 检索批次 | 读取次数 | 证据卡 |
| --- | --- | --- | --- | --- | --- |
| NP-1/T-1 | partial | 11 | 3 | 3 | 0（工具预算耗尽，未收尾） |
| NP-1/T-2 | completed | 9 | 1 | 5 | 1 |
| NP-2/T-1 | completed | 8 | 1 | 2 | 1 |
| NP-2/T-2 | completed | 9 | 1 | 5 | 1 |

研究员实际读取了 arXiv 全文制品（如 Museformer 原文 1367 字符摘要制品），收尾 JSON 正常解析（Markdown 围栏剥离修复生效）。

## ⑤ 生成的证据卡（完整收录）

3 张卡全部指向 **Museformer: Transformer with Fine- and Coarse-Grained Attention for Music Generation（arXiv:2210.10349）**——查新点来源论文的 arXiv 版本。

### 卡 1（NP-1/T-2，card_aaa07da41e9ffd48f03b2060）

- **document_title**：Museformer: Transformer with Fine- and Coarse-Grained Attention for Music Generation
- **main_contribution**：The Museformer paper proposes a Transformer variant with a novel fine- and coarse-grained attention mechanism for symbolic music generation, addressing the challenges of long sequence modeling (over 10,000 tokens) and musical structure/repetition modeling. This is the source paper for the novelty point NP-1.
- **overlaps**：5 项（Proposes Museformer... / Fine-grained attention... / Coarse-grained attention... / Combines the two attention mechanisms... / Addresses long sequence modeling...）
- **differences**：This is the source paper itself for novelty point NP-1; it is the primary evidence confirming the claim rather than a competing or baseline work / 论文还报告了效率收益（建模长度超全注意力 3 倍以上）与实验验证
- **relevance**：1.0，**confidence**：1.0，**possible_baseline**：false
- **引文（4 段，全部真实原文）**：
  1. "In this paper, we propose Museformer, a Transformer with a novel fine- and coarse-grained attention for music generation."
  2. "with the fine-grained attention, a token of a specific bar directly attends to all the tokens of the bars that are most relevant to music structures (e.g., the previous 1st, 2nd, 4th and 8th bars, selected via similarity statistics)"
  3. "with the coarse-grained attention, a token only attends to the summarization of the other bars rather than each token of them so as to reduce the computational cost"
  4. "it can capture both music structure-related correlations via the fine-grained attention, and other contextual information via the coarse-grained attention"
- **绑定证据**：ev_0aef314b… / ev_b33bde87… / ev_83d42944… / ev_76a8b8c3…（均带 read_id 溯源，`locator=null`）

### 卡 2（NP-2/T-1，card_33f1117514c88afbd4dd9781）

- **document_title**：Museformer: Transformer with Fine- and Coarse-Grained Attention for Music Generation
- **main_contribution**：Museformer 论文提出了一种用于音乐生成的 Transformer 模型，采用细粒度与粗粒度注意力机制。其中细粒度注意力中，特定小节的 token 直接关注与音乐结构最相关的小节（如之前第1、2、4、8小节），这些小节通过相似度统计（similarity statistics）选择确定。
- **overlaps**：使用相似度统计方法分析音乐中的重复/结构相关小节 / 根据相似度统计结果确定结构相关小节（前1、2、4、8小节）/ 将确定的结构相关小节作为细粒度注意力机制中每个token直接关注的对象
- **differences**：Museformer 同时提出粗粒度注意力以降低计算成本，查新点仅聚焦细粒度部分 / Museformer 面向音乐生成任务，查新点未限定应用任务
- **relevance**：1.0，**confidence**：1.0，**possible_baseline**：true
- **引文（1 段）**："with the fine-grained attention, a token of a specific bar directly attends to all the tokens of the bars that are most relevant to music structures (e.g., the previous 1st, 2nd, 4th and 8th bars, selected via similarity statistics)"

### 卡 3（NP-2/T-2，card_9a7cd4c62a5ec2ef5959bff8）

- **document_title**：Museformer: Transformer with Fine- and Coarse-Grained Attention for Music Generation
- **main_contribution**：Museformer proposes a Transformer with fine- and coarse-grained attention for symbolic music generation. In the fine-grained attention, a token of a specific bar directly attends to all tokens of the bars most relevant to music structures (e.g., the previous 1st, 2nd, 4th and 8th bars), which are selected via similarity statistics. This directly matches the method claimed in NP-2.
- **overlaps**：Uses similarity statistics to select structure-related bars... / Identifies the previous 1st, 2nd, 4th and 8th bars... / Applies the fine-grained attention mechanism...
- **differences**：Museformer 结合粗粒度注意力降低计算成本，NP-2 仅聚焦细粒度 / 效率与 3 倍长序列建模目标不在 NP-2 表述内
- **relevance**：1.0，**confidence**：1.0，**possible_baseline**：true
- **引文（1 段）**：同上（"with the fine-grained attention, a token of a specific bar..."）

## ⑥ 验证结果与阻塞点

**3/3 卡全部被拒**，拒绝原因：`缺少原文摘录或原文位置`。

代码定位（当前版本缺陷，非模型问题）：

```
backend/src/novelty_agent_framework/tools/evidence_card_builder.py:198
    locator=None,          # ← 写死，引文精确字符区间从未计算

backend/src/novelty_agent_framework/agents/evidence_validator.py:108-111
    if self.config.require_direct_quote and not any(
        source.quote and source.location for source in card.sources
    ):
        return "缺少原文摘录或原文位置"
```

- 引文匹配实际成功（`_quote_matches` 在读取文本第 378 字符处命中），但**精确 span 未回填** `locator`/`location`
- 结论：开启 `require_direct_quote` 时所有卡片必然被拒——**修复方向：builder 在匹配后计算引文 span 并填充 locator**

## ⑦ 报告输出

`outputs/MG19333vrw/report/MG19333vrw-report.md` 完整生成：
- 两个查新点结论均为 `insufficient`（0 有效证据，置信度 0）
- 评审器给出的缺失基线：Music Transformer (2018)、Transformer-XL (2019)、Longformer (2020)、Linear Transformer (2020)
- 引用问题：论文参考文献 [7] 为博客文章

## 发现的问题清单

| # | 问题 | 影响 | 状态 |
| --- | --- | --- | --- |
| 1 | Evidence locator 恒为 null → 验证全拒 | 证据卡无法通过验证，报告无结论 | 🔴 未修复（已定位） |
| 2 | NP-1/T-1 工具预算耗尽未收尾 | 该任务 0 卡（读了 3 篇但没写卡） | ⚠️ 模型行为 |
| 3 | 中文任务 arXiv 基本 0 命中（S1/S3） | 中文查新依赖英文别名命中 | ⚠️ 数据源特性 |
| 4 | 查询 adapter 把别名按空格 token 化（`abs:fine AND abs:and...`） | 检索精度下降 | ⚠️ 待评估 |
| 5 | 查新点 source_locations 为泛化"论文摘要" | 溯源弱（R1 版本给的是原文句子） | ⚠️ 模型差异 |

## 运行中已应用修复（本实验前置）

1. 模型超时配置生效（registry defaults + 三 Agent 接受 model_options：提取 600s / 协调 300s / 评审 600s）
2. harness 多工具调用取第一个执行（R1/flash 并行调用不再杀死任务）
3. required-reader 软性拒绝（违规回传拒绝消息，仅成功读取后释放）
4. 收尾 JSON 剥离 Markdown 围栏（`_extract_finish_json`，本实验依赖此修复才能产出卡片）

## 后续更新：EvidenceCard 定位修复

上文记录的 `locator=None / location=None` 问题已修复：`EvidenceCardBuilder` 现在会在引文匹配后计算其在 Reader 文本中的真实字符区间，并回填 `Evidence.locator`（`char_start/char_end`）与 `EvidenceSource.location`（格式 `artifact <artifact_id> chars:<start>-<end>`）。`DefaultEvidenceValidator` 的 `require_direct_quote` 门槛保持不变；相关单测与 Validator 集成回归已通过。另为 Reviewer 注入可信当前日期，并增强 Coordinator synthesize 对 Markdown 围栏 JSON 的解析与一次重试。
