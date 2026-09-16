# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T22:46:38+08:00 |
| 查新范围 | 图表示学习、深度学习、图神经网络、分布式技术、graph representation learning、deep learning、graph neural network、distributed |

---

## 一、查新目的

由于现实世界中的大多数数据都可以用图表示，因此近年来针对图表示学
习的研究越来越受到关注。通过将高维图数据转化成低维的表征向量，图表示
学习可以有效地对图的信息进行存储并快捷地访问图中实体的关键知识。利用
学习到的图表征数据可以为社交网络行为分析、节点分类、链路预测和聚类等
下游任务提供帮助。随着深度学习的快速发展，研究人员提出了基于图神经网
络的图表示学习方法，其使图中的节点能够同时学习图的结构信息以及邻域节
点的特征信息，从而得到高质量的低维表征。针对图神经网络上的图表示学
习，本文主要关注两个问题：大规模时序图场景下的图表示学习方法和分布式
场景下的大规模图的图神经网络优化训练方法。
真实世界中的图数据规模往往十分庞大且处于动态变化的状态，而现有的
图神经网络要么无法处理动态时序图上的图表征学习，要么面对大规模图数据
集时训练效率低下。为了解决大规模动态图上的图表征学习问题，本文提出了
一种基于图摘要的大规模时序图表示学习方法——GSAERU 模型。GSAERU 模
型由“图表征学习模块”和“时序学习模块”两部分构成。首先将动态时序图
建模为各时刻上原图快照的序列，接着在单时间步上将图快照输入图表征学习
模块。该模块通过图摘要技术对原图进行压缩，并将压缩后的新图输入图自编
码器，利用和原图的重构误差训练原图节点的表征。在获得单时间步上的图表
征后将其输入时序学习模块，并通过一个循环神经网络学习原图在时间维度上
的特征信息与依赖关系，从而得到大规模时序图的高质量表征。基于在四个真
实世界的大规模图数据集上的大量实验表明，GSAERU 模型能够高效生成时序
图的表征。与传统的图神经网络算法相比，其平均内存消耗和平均训练时长只
有其9.86% 与13.27%，且与性能最好的算法在大部分指标下的差距都不超过
3.5%。

ii
使用分布式技术加速神经网络训练也是如今热门的研究课题，因为在处理
大规模数据时，单个设备（如CPU，GPU）有限的内存和计算资源往往会成为
训练瓶颈。而分布式技术可以提供更多的计算资源来提高训练效率。然而由于
图数据的不规则性，传统分布式机器学习方法中的子任务划分和模型训练方法
难以直接应用于图神经网络。针对大规模图流数据场景下的分布式图神经网络
训练优化问题，本文提出了基于图摘要的分布式图神经网络优化训练算法——
DSGNN 模型。DSGNN 模型采用“领导——工作者”工作模式，首先由领导节
点利用一个基于边分割的图流划分算法对原图进行划分并将划分子图分配给各
个工作节点。工作节点随后执行一个基于图摘要技术的小批量训练并将训练结
果通过一个注意力层返回给领导节点，最后由领导节点汇总结果并计算梯度，
并根据梯度同步更新所有计算节点上的模型。基于四个真实世界的大规模图数
据集上的大量实验，结果表明DSGNN 模型可以大大加速GNN 模型的训练，
并且在链路预测任务上的F1 分数显著高于其它分布式图神经网络模型。

---

## 二、项目科学技术要点

- 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图映射到固定规模的新图，解决了GNN输出无法直接输入RNN训练的问题。
- 提出了一种基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，在工作节点上基于图摘要技术进行小批量训练，并通过注意力层返回结果给领导节点。
- 提出了一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图映射到固定规模的新图，解决了GNN输出无法直接输入RNN训练的问题。 | Proposed a large-scale sequential graph representation learning method GSAERU based on graph summarization, which maps dynamic sequential graphs to fixed-size new graphs via graph summarization, solving the problem that GNN outputs cannot be directly fed into RNN for training. |
| NP-2 | 提出了一种基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，在工作节点上基于图摘要技术进行小批量训练，并通过注意力层返回结果给领导节点。 | Proposed a distributed graph neural network optimization training framework DSGNN based on graph summarization, adopting a leader-worker mode, where workers perform mini-batch training based on graph summarization and return results to the leader through an attention layer. |
| NP-3 | 提出了一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号。 | Proposed a graph stream partitioning algorithm Sketch-DBH based on edge partitioning, which uses Count-Min Sketch to store node degree information and a min-heap to maintain high-frequency node information, enabling constant-time query results and generating subgraph IDs. |

---

## 四、查新范围要求

检索范围围绕各查新点的中英文表述及技术特征展开。

---

## 五、文献检索范围及检索策略

### 5.1 检索来源

- arxiv.org
- link.springer.com

### 5.2 检索词

- 图表示学习
- 深度学习
- 图神经网络
- 分布式技术
- graph representation learning
- deep learning
- graph neural network
- distributed

### 5.3 检索式

- **NP-1**
  - `ti:sequential AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:graph autoencoder] OR CONCEPT[C4:recurrent neural network])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:graph autoencoder] OR CONCEPT[C4:recurrent neural network])`（null_catalog；零命中）
  - `"sequential graph representation learning" AND "graph summarization"`（springer；执行失败）
  - `"sequential graph representation learning" AND "graph summarization"`（springer；执行失败）
  - `"sequential graph representation learning" AND "graph summarization"`（springer；执行失败）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework AND abs:"graph summarization" AND abs:"leader-worker mode" AND abs:"mini-batch training" AND abs:"attention layer"`（arxiv；零命中）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework AND abs:"graph summarization" AND abs:"mini-batch training" AND abs:"attention layer"`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework OR ti:"DSGNN" OR ti:"distributed GNN training") AND (abs:"graph summarization" OR abs:"graph summarization technique" OR abs:"graph summary") AND (abs:"leader-worker mode" OR abs:"leader-worker architecture" OR abs:"master-worker")`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework OR ti:"DSGNN" OR ti:"distributed GNN training") AND (abs:"graph summarization" OR abs:"graph summarization technique" OR abs:"graph summary")`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework OR ti:"DSGNN" OR ti:"distributed GNN training") OR (abs:"graph summarization" OR abs:"graph summarization technique" OR abs:"graph summary")`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization] AND CONCEPT[C3:leader-worker mode] AND CONCEPT[C4:mini-batch training] AND CONCEPT[C5:attention layer])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization] AND CONCEPT[C4:mini-batch training] AND CONCEPT[C5:attention layer])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization] AND CONCEPT[C3:leader-worker mode])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] OR CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] OR CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `"distributed graph neural network training framework" AND "graph summarization" AND "leader-worker mode" AND "mini-batch training" AND "attention layer"`（springer；执行失败）
  - `"distributed graph neural network training framework" AND "graph summarization" AND "leader-worker mode" AND "mini-batch training" AND "attention layer"`（springer；执行失败）
- **NP-3**
  - `(abs:"graph stream partitioning" OR abs:"edge partitioning" OR abs:"stream partitioning algorithm") AND (abs:"Count-Min Sketch" OR abs:"min-heap" OR abs:"probabilistic data structure")`（arxiv；零命中）
  - `(abs:"Count-Min Sketch" OR abs:"min-heap" OR abs:"probabilistic data structure")`（arxiv；有命中）
  - `("graph stream partitioning" OR "edge partitioning" OR "stream partitioning algorithm") AND ("Count-Min Sketch" OR "min-heap" OR "probabilistic data structure")`（springer；有命中）
  - `("graph stream partitioning" OR "edge partitioning" OR "stream partitioning algorithm" OR "graph partitioning" OR "edge-cut partitioning") AND ("Count-Min Sketch" OR "min-heap" OR "probabilistic data structure" OR "CMS" OR "sketch" OR "heap") AND ("node degree information" OR "high-frequency node" OR "constant-time query" OR "degree" OR "frequent nodes" OR "O(1) query")`（springer；部分成功）
  - `("graph stream partitioning" OR "edge partitioning" OR "stream partitioning algorithm") AND ("Count-Min Sketch" OR "min-heap" OR "probabilistic data structure")`（springer；有命中）
  - `("graph stream partitioning" OR "edge partitioning" OR "stream partitioning algorithm" OR "graph partitioning" OR "edge-cut partitioning") AND ("Count-Min Sketch" OR "min-heap" OR "probabilistic data structure" OR "CMS" OR "sketch" OR "heap") AND ("node degree information" OR "high-frequency node" OR "constant-time query" OR "degree" OR "frequent nodes" OR "O(1) query")`（springer；部分成功）

---

## 六、检索结果

### 6.1 检索概况

共执行 1 轮检索计划，生成 4 张原始证据卡；通过 4 张，拒绝 0 张。

### 6.2 相关文献

### card_fc5433010f3a4c0f77b19d8c · Balancing Summarization and Change Detection in Graph Streams

- 查新点：NP-1
- 主要贡献：Proposes a quantitative methodology to balance graph summarization and graph change detection in graph streams, using a hierarchical latent variable model and minimum description length principle to design parameterized summary graphs for detecting statistically significant changes in streaming graphs.
- 相关性：0.50
- 置信度：0.80
- 来源：
  - Balancing Summarization and Change Detection in Graph Streams：https://arxiv.org/pdf/2311.18694
    - 引文：Graph summarization compresses large-scale graphs into a smaller scale. However, the question remains: To what extent should the original graph be compressed? This problem is solved from the perspective of graph change detection, aiming to detect statistically significant changes using a stream of summary graphs.
    - 位置：artifact art_a4b03ccff6df4518c3399802 chars:92-406

### card_76436aaa84bd83613d169b2a · SDT-GNN: Streaming-based Distributed Training Framework for Graph Neural Networks

- 查新点：NP-2
- 主要贡献：Proposes SDT-GNN, a streaming-based distributed GNN training framework that takes a stream of edges as input for graph partitioning to reduce memory requirements, enabling distributed GNN training on large graphs.
- 相关性：0.50
- 置信度：0.85
- 来源：
  - SDT-GNN: Streaming-based Distributed Training Framework for Graph Neural Networks：https://arxiv.org/pdf/2404.02300
    - 引文：we propose SDT-GNN, a streaming-based distributed GNN training framework. Unlike the existing frameworks that load the entire graph in memory, it takes a stream of edges as input for graph partitioning to reduce the memory requirement for partitioning.
    - 位置：artifact art_54da6e025cc0ed386d08e5d1 chars:361-613

### card_430dca87eee8908e02934852 · Scaling R-GCN Training with Graph Summarization

- 查新点：NP-2
- 主要贡献：Proposes using graph summarization techniques to compress graphs for training Relational Graph Convolutional Networks (R-GCN), reducing memory requirements, then transferring weights back to the original graph for inference.
- 相关性：0.55
- 置信度：0.85
- 来源：
  - Scaling R-GCN Training with Graph Summarization：10.1145/3487553.3524719
    - 引文：we experiment with the use of graph summarization techniques to compress the graph and hence reduce the amount of memory needed. After training the R-GCN on the graph summary, we transfer the weights back to the original graph and attempt to perform inference on it.
    - 位置：artifact art_5a95e23353233acf80dfb52a chars:265-531

### card_3d7e93f223ec9a0008567f35 · A distributed skewed stream processing system based on scoring high-frequency key perception

- 查新点：NP-3
- 主要贡献：SH-Stream: a distributed skewed stream processing system that identifies high-frequency keys in streams via a scoring probabilistic prediction algorithm and achieves load balancing by splitting identified high-frequency keys.
- 相关性：0.30
- 置信度：0.60
- 来源：
  - A distributed skewed stream processing system based on scoring high-frequency key perception：10.1007/s11227-025-07465-7
    - 引文：To accurately identify high-frequency keys in streams, we introduce a scoring probabilistic prediction algorithm and establish effective maintenance mechanisms for these high-frequency keys. Load balancing is achieved through the judicious splitting of identified high-frequency keys.
    - 位置：artifact art_a20357a3ccfdaf942021e0a5 chars:706-990

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 1 | 有证据 |
| NP-2 | 2 | 有证据 |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 部分新颖

提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图映射到固定规模的新图，解决了GNN输出无法直接输入RNN训练的问题。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 单卡核验显示该文献与查新点存在部分重合：均使用图摘要压缩大规模图并处理图流/动态时序图，对应特征1和特征2的图摘要压缩部分。但该文献核心目标是图流中的变化检测，不涉及表示学习；摘要中未提及图自编码器、重构误差训练节点表征（特征2核心）或RNN学习时间依赖（特征3），也未涉及GNN输出输入RNN的问题。该文献研究目标与查新点完全不同，仅构成宽泛概念层面的部分重合，不足以否定查新点的新颖性。  
**置信度：** 0.80  
**报告摘要：** 查新点提出GSAERU模型，结合图摘要压缩与图自编码器、RNN实现大规模时序图表征学习。经检证据卡片揭示，现有文献中存在使用图摘要处理图流/动态图的工作（card_fc5433010f3a4c0f77b19d8c），但与查新点在目标（变化检测vs表示学习）和核心机制（未使用图自编码器重构误差及RNN时序依赖学习）上存在显著差异，部分重合仅限于宽泛的图摘要压缩概念层面。因此，查新点主张的技术组合在已有证据下未见完整公开，判定为部分新颖。  
**高度相关 Work：**
  - wrk_07b78e912a5c299d4357e161：该文献使用图摘要压缩大规模图并处理图流，与查新点的图摘要压缩和时序图快照建模存在部分重合，但聚焦变化检测而非表示学习，不涉及图自编码器、重构误差或RNN，属于部分相关文献。 (cards: card_fc5433010f3a4c0f77b19d8c)

### NP-2 · 部分新颖

提出了一种基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，在工作节点上基于图摘要技术进行小批量训练，并通过注意力层返回结果给领导节点。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 综合两张单卡核验结果：SDT-GNN（card_76436aaa84bd83613d169b2a）与查新点仅在'分布式GNN训练框架'宽泛层面重合，其核心为流式图划分（SPRING），与'基于图摘要'明确不同；Scaling R-GCN（card_430dca87eee8908e02934852）与查新点共享'基于图摘要进行GNN训练'特征，但明确为单机内存优化方案，未涉及分布式领导-工作者模式、注意力层返回结果或梯度同步。两篇文献均未完整公开查新点的核心组合特征（领导-工作者模式+图摘要小批量训练+注意力层返回+梯度同步更新），故判定为部分新颖。  
**置信度：** 0.80  
**报告摘要：** 查新点提出DSGNN分布式GNN训练框架，采用领导-工作者模式，结合图摘要小批量训练与注意力层返回结果。检索发现的现有工作中，SDT-GNN（card_76436aaa84bd83613d169b2a）同为分布式GNN框架但采用流式图划分而非图摘要，且无领导-工作者模式与注意力层；Scaling R-GCN（card_430dca87eee8908e02934852）使用图摘要压缩训练GNN，但仅限单机内存优化，未涉及分布式架构和注意力层。两文献皆未覆盖查新点的核心组合特征，因此判定为部分新颖。  
**高度相关 Work：**
  - wrk_0c0af5018413ad476ba2d09d：同为分布式GNN训练框架，在'多计算节点分布式训练大图'层面与查新点重合；但采用流式图划分而非图摘要，且无领导-工作者模式与注意力层，未覆盖查新点核心特征。 (cards: card_76436aaa84bd83613d169b2a)
  - wrk_69b3cecda02343b983f9dbc2：该文献与查新点共享'基于图摘要进行GNN训练'特征，但明确为单机内存优化方案，未涉及分布式领导-工作者架构、注意力层或梯度同步，是判定部分新颖的关键对比文献。 (cards: card_430dca87eee8908e02934852)

### NP-3 · 部分新颖

提出了一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 单卡核验显示，SH-Stream（wrk_5ec4827aaf45a178e54f3b64）与查新点存在部分重合：均涉及流数据中高频键/节点的识别维护及通过拆分实现负载均衡。但该文献面向通用分布式流处理系统，而非基于边分割的图流划分；其采用评分概率预测算法识别高频键，未使用Count-Min Sketch存储节点度数，未使用最小堆维护高频节点，也未基于节点度数生成子图编号。摘要明确证实这些差异，故该文献未公开查新点所主张的技术组合（Count-Min Sketch+最小堆+常数时间子图编号生成）。  
**置信度：** 0.70  
**报告摘要：** 查新点提出基于边分割的图流划分算法Sketch-DBH，采用Count-Min Sketch存储节点度数、最小堆维护高频节点。检索发现的SH-Stream（card_3d7e93f223ec9a0008567f35）面向通用流处理系统，采用评分概率预测识别高频键，未使用Count-Min Sketch、最小堆或子图编号生成，仅在负载均衡目标及高频键维护概念上有所重合，未公开查新点的技术组合，故判定为部分新颖。  
**高度相关 Work：**
  - wrk_5ec4827aaf45a178e54f3b64：部分相关：该文献在流数据高频键维护与负载均衡目标上与查新点重合，但领域（通用DSPS而非图流划分）及核心技术（评分概率预测，非Count-Min Sketch+最小堆+子图编号生成）均不同，未公开查新点主张的组合。 (cards: card_3d7e93f223ec9a0008567f35)

---

## 八、报告局限

- 检索覆盖范围：本次查新基于英文文献检索，每个查新点仅执行了一轮检索（attempt=1），且仅通过单卡核验（每点一张或两张证据卡）进行新颖性判断。未补充中文数据库、专利、学位论文等来源，也未执行多轮迭代检索，覆盖范围有限。
- 有效证据卡数量：每个查新点均获得了有效证据卡，但数量较少（NP-1有1张，NP-2有2张，NP-3有1张）。这些卡片足以支撑Reviewer的部分新颖判断，但不足以构成全面的否定性检索结论。
- 检索成功率：输入中未提供各来源检索执行的具体成功/失败信息，因此无法区分检索失败与成功零命中。本次报告仅能基于已有证据卡和Retriever返回的内容进行陈述，检索覆盖的实际完整性未知。

---

## 九、附件及参考信息

### 缺失参考文献

无。

### 缺失 Baseline

无。

### 引用问题

无。

### 被拒绝证据

无。

### 检索到的文献

- Balancing Summarization and Change Detection in Graph Streams：[https://arxiv.org/pdf/2311.18694](https://arxiv.org/pdf/2311.18694)
- Utility-Based Graph Summarization: New and Improved：[https://arxiv.org/pdf/2006.08949](https://arxiv.org/pdf/2006.08949)
- Promise and Limitations of Supervised Optimal Transport-Based Graph Summarization via Information Theoretic Measures：[https://arxiv.org/pdf/2305.07138](https://arxiv.org/pdf/2305.07138)
- Causal DAG Summarization (Full Version)：[https://arxiv.org/pdf/2504.14937](https://arxiv.org/pdf/2504.14937)
- Improving Question Answering over Knowledge Graphs Using Graph Summarization：[https://arxiv.org/pdf/2203.13570](https://arxiv.org/pdf/2203.13570)
- Multi-relation Graph Summarization：[https://arxiv.org/pdf/2112.15488](https://arxiv.org/pdf/2112.15488)
- Graph Summarization：[https://arxiv.org/pdf/2004.14794](https://arxiv.org/pdf/2004.14794)
- kMatrix: A Space Efficient Streaming Graph Summarization Technique：[https://arxiv.org/pdf/2105.05503](https://arxiv.org/pdf/2105.05503)
- These are not the k-mers you are looking for: efficient online k-mer counting using a probabilistic data structure：[https://arxiv.org/pdf/1309.2975](https://arxiv.org/pdf/1309.2975)
- Buffered Count-Min Sketch on SSD: Theory and Experiments：[https://arxiv.org/pdf/1804.10673](https://arxiv.org/pdf/1804.10673)
- Count-Min sketches for Telemetry: analysis of performance in P4 implementations：[https://arxiv.org/pdf/2406.12586](https://arxiv.org/pdf/2406.12586)
- Optimized Learned Count-Min Sketch：[https://arxiv.org/pdf/2512.12252](https://arxiv.org/pdf/2512.12252)
- Count-Min-Log sketch: Approximately counting with approximate counters：[https://arxiv.org/pdf/1502.04885](https://arxiv.org/pdf/1502.04885)
- Memory-efficient Sketch Acceleration for Handling Large Network Flows on FPGAs：[https://arxiv.org/pdf/2504.16896](https://arxiv.org/pdf/2504.16896)
- Count-Min Tree Sketch: Approximate counting for NLP：[https://arxiv.org/pdf/1604.05492](https://arxiv.org/pdf/1604.05492)
- Do You Like What I Like? Similarity Estimation in Proximity-based Mobile Social Networks：[https://arxiv.org/pdf/1805.07651](https://arxiv.org/pdf/1805.07651)
- Scaling R-GCN Training with Graph Summarization：[https://arxiv.org/pdf/2203.02622](https://arxiv.org/pdf/2203.02622)
- A Comprehensive Survey on Graph Summarization with Graph Neural Networks：[https://arxiv.org/pdf/2302.06114](https://arxiv.org/pdf/2302.06114)
- Graph Summarization with Graph Neural Networks：[https://arxiv.org/pdf/2203.05919](https://arxiv.org/pdf/2203.05919)
- FLUID: A Common Model for Semantic Structural Graph Summaries Based on Equivalence Relations：[https://arxiv.org/pdf/1908.01528](https://arxiv.org/pdf/1908.01528)
- SDT-GNN: Streaming-based Distributed Training Framework for Graph Neural Networks：[https://arxiv.org/pdf/2404.02300](https://arxiv.org/pdf/2404.02300)
- A distributed skewed stream processing system based on scoring high-frequency key perception：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-025-07465-7](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-025-07465-7)
- RabbitTClust: enabling fast clustering analysis of millions of bacteria genomes with MinHash sketches：[https://www.biomedcentral.com/openurl/pdf?id=doi:10.1186/s13059-023-02961-6](https://www.biomedcentral.com/openurl/pdf?id=doi:10.1186/s13059-023-02961-6)
- Design and Performance of a Heterogeneous Grid Partitioner：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00453-006-1223-0](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00453-006-1223-0)
- RAGDNet: A Region-Adjacency Graph for Semantic Segmentation of Mechanical Drawings Using Graph Neural Networks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31397-3_9](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31397-3_9)
- Sublinear-Time Algorithms for Diagonally Dominant Systems and Applications to the Friedkin-Johnsen Model：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3309-0_12](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3309-0_12)
- Evolving digital skill demands before and after generative AI: a global network analysis via upwork data：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10618-026-01271-2](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10618-026-01271-2)
- QLOA: A Self-Adaptive Q-Learning-Based Optimization Algorithm with Dynamic Mathematical Formulation Selection：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s42235-026-00961-3](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s42235-026-00961-3)
- Graph and String Parameters: Connections Between Pathwidth, Cutwidth and the Locality Number：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s00453-026-01404-5](http://link.springer.com/openurl/pdf?id=doi:10.1007/s00453-026-01404-5)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
