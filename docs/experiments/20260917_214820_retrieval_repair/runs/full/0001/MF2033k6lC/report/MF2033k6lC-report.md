# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-17T22:41:39+08:00 |
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

- 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图压缩为固定规模的新图，解决GNN输出无法直接输入RNN的问题，并利用图自编码器与循环神经网络学习时序特征。
- 提出一种基于图摘要的分布式图神经网络训练框架DSGNN，采用“领导-工作者”模式，领导节点负责图划分和模型同步更新，工作节点基于图摘要技术进行小批量训练，并通过注意力层返回结果。
- 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图压缩为固定规模的新图，解决GNN输出无法直接输入RNN的问题，并利用图自编码器与循环神经网络学习时序特征。 | Propose a large-scale sequential graph representation learning method GSAERU based on graph summarization, which compresses dynamic sequential graphs into fixed-size new graphs via graph summarization to solve the problem that GNN outputs cannot be directly fed into RNN, and uses graph autoencoder and recurrent neural network to learn temporal features. |
| NP-2 | 提出一种基于图摘要的分布式图神经网络训练框架DSGNN，采用“领导-工作者”模式，领导节点负责图划分和模型同步更新，工作节点基于图摘要技术进行小批量训练，并通过注意力层返回结果。 | Propose a distributed graph neural network training framework DSGNN based on graph summarization, adopting a leader-worker mode where the leader node performs graph partitioning and synchronous model updates, and worker nodes conduct mini-batch training based on graph summarization and return results via an attention layer. |
| NP-3 | 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。 | Propose an edge-segmentation-based graph stream partitioning algorithm Sketch-DBH, which uses Count-Min Sketch to store node degree information and a min-heap to maintain high-frequency node information, enabling constant-time query results and generating subgraph IDs to ensure load balancing. |

---

## 四、查新范围要求

检索范围围绕各查新点的中英文表述及技术特征展开。

---

## 五、文献检索范围及检索策略

### 5.1 检索来源

- arxiv.org

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
  - `(ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:"temporal graph learning") AND (abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening")`（arxiv；零命中）
  - `(ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:"temporal graph learning")`（arxiv；有命中）
  - `ti:sequential AND ti:graph AND ti:representation AND ti:learning`（arxiv；有命中）
  - `(ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:"temporal graph learning")`（arxiv；有命中）
  - `"sequential graph representation learning" AND "graph summarization"`（springer；执行失败）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning") AND ("graph summarization" OR "graph compression" OR "graph coarsening")`（springer；not_run）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning")`（springer；not_run）
  - `"sequential graph representation learning"`（springer；not_run）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning")`（springer；not_run）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning")`（springer；not_run）
  - `"sequential graph representation learning" AND "graph summarization"`（springer；执行失败）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning") AND ("graph summarization" OR "graph compression" OR "graph coarsening")`（springer；not_run）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning")`（springer；not_run）
  - `"sequential graph representation learning"`（springer；not_run）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning")`（springer；not_run）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning")`（springer；not_run）
  - `"sequential graph representation learning" AND "graph summarization"`（springer；执行失败）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning") AND ("graph summarization" OR "graph compression" OR "graph coarsening")`（springer；not_run）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning")`（springer；not_run）
  - `"sequential graph representation learning"`（springer；not_run）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning")`（springer；not_run）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning")`（springer；not_run）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework AND abs:"graph summarization" AND abs:"leader-worker mode" AND abs:"attention layer"`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework OR ti:"DSGNN" OR ti:"distributed GNN training") AND (abs:"graph summarization" OR abs:"graph summary" OR abs:"graph summarization technique")`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework OR ti:"DSGNN" OR ti:"distributed GNN training")`（arxiv；有命中）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework AND abs:"graph summarization" AND abs:"attention layer"`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework OR ti:"DSGNN" OR ti:"distributed GNN training")`（arxiv；有命中）
- **NP-3**
  - `(abs:"graph stream partitioning" OR abs:"edge partitioning" OR abs:"graph partitioning") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure") AND (abs:"min-heap" OR abs:"priority queue")`（arxiv；零命中）
  - `(abs:"graph stream partitioning" OR abs:"edge partitioning" OR abs:"graph partitioning" OR abs:"graph stream partition" OR abs:"edge-cut partitioning") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"CMS" OR abs:"count-min sketch")`（arxiv；零命中）
  - `(abs:"graph stream partitioning" OR abs:"edge partitioning" OR abs:"graph partitioning" OR abs:"graph stream partition" OR abs:"edge-cut partitioning")`（arxiv；有命中）
  - `(abs:"graph stream partitioning" OR abs:"edge partitioning" OR abs:"graph partitioning") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure")`（arxiv；零命中）
  - `(abs:"graph stream partitioning" OR abs:"edge partitioning" OR abs:"graph partitioning" OR abs:"graph stream partition" OR abs:"edge-cut partitioning")`（arxiv；有命中）
  - `("graph stream partitioning" OR "edge partitioning" OR "graph partitioning") AND ("Count-Min Sketch" OR "probabilistic data structure") AND ("min-heap" OR "priority queue")`（springer；执行失败）
  - `("graph stream partitioning" OR "edge partitioning" OR "graph partitioning" OR "graph stream partition" OR "edge-cut partitioning") AND ("Count-Min Sketch" OR "probabilistic data structure" OR "CMS" OR "count-min sketch")`（springer；not_run）
  - `("graph stream partitioning" OR "edge partitioning" OR "graph partitioning" OR "graph stream partition" OR "edge-cut partitioning")`（springer；not_run）
  - `("graph stream partitioning" OR "edge partitioning" OR "graph partitioning") AND ("Count-Min Sketch" OR "probabilistic data structure")`（springer；not_run）
  - `("graph stream partitioning" OR "edge partitioning" OR "graph partitioning" OR "graph stream partition" OR "edge-cut partitioning")`（springer；not_run）
  - `("graph stream partitioning" OR "edge partitioning" OR "graph partitioning" OR "graph stream partition" OR "edge-cut partitioning")`（springer；not_run）

---

## 六、检索结果

### 6.1 检索概况

共执行 1 轮检索计划，生成 5 张原始证据卡；通过 5 张，拒绝 0 张。

### 6.2 相关文献

### card_e0f18431d0e8ab03ad5ce4a0 · Learning Dual Dynamic Representations on Time-Sliced User-Item Interaction Graphs for Sequential Recommendation

- 查新点：NP-1
- 主要贡献：DRL-SRe models dynamic user-item interaction graphs as time-sliced snapshots and learns user/item representations via time-sliced graph neural networks, with an auxiliary temporal prediction task based on temporal point process for sequential recommendation.
- 相关性：0.45
- 置信度：0.80
- 来源：
  - Learning Dual Dynamic Representations on Time-Sliced User-Item Interaction Graphs for Sequential Recommendation：https://arxiv.org/pdf/2109.11790
    - 引文：the proposed model builds a global user-item interaction graph for each time slice and exploits time-sliced graph neural networks to learn user and item representations
    - 位置：artifact art_ac6571cb2ce9e7e48a24e192 chars:797-965

### card_018e754c5aefa7a7078c1414 · ABC: Aggregation before Communication, a Communication Reduction Framework for Distributed Graph Neural Network Training and Effective Partition

- 查新点：NP-2
- 主要贡献：ABC proposes a lossless communication reduction method (Aggregation before Communication) for distributed GNN training, exploiting the permutation-invariant property of GNN layers and introducing a vertex-cut partition paradigm.
- 相关性：0.35
- 置信度：0.70
- 来源：
  - ABC: Aggregation before Communication, a Communication Reduction Framework for Distributed Graph Neural Network Training and Effective Partition：https://arxiv.org/pdf/2212.05410
    - 引文：we study the communication complexity during distributed GNNs training and propose a simple lossless communication reduction method, termed the Aggregation before Communication (ABC) method.
    - 位置：artifact art_00ea5d4bffcc0be9ca49ba34 chars:589-779
  - ABC: Aggregation before Communication, a Communication Reduction Framework for Distributed Graph Neural Network Training and Effective Partition：https://arxiv.org/pdf/2212.05410
    - 引文：ABC method exploits the permutation-invariant property of the GNNs layer and leads to a paradigm where vertex-cut is proved to admit a superior communication performance than the currently popular paradigm (edge-cut).
    - 位置：artifact art_00ea5d4bffcc0be9ca49ba34 chars:780-997

### card_76436aaa84bd83613d169b2a · SDT-GNN: Streaming-based Distributed Training Framework for Graph Neural Networks

- 查新点：NP-2
- 主要贡献：SDT-GNN proposes a streaming-based distributed GNN training framework that takes a stream of edges as input for graph partitioning (SPRING algorithm) to reduce memory requirements, enabling distributed GNN training on large graphs.
- 相关性：0.40
- 置信度：0.70
- 来源：
  - SDT-GNN: Streaming-based Distributed Training Framework for Graph Neural Networks：https://arxiv.org/pdf/2404.02300
    - 引文：we propose SDT-GNN, a streaming-based distributed GNN training framework. Unlike the existing frameworks that load the entire graph in memory, it takes a stream of edges as input for graph partitioning to reduce the memory requirement for partitioning.
    - 位置：artifact art_54da6e025cc0ed386d08e5d1 chars:361-613
  - SDT-GNN: Streaming-based Distributed Training Framework for Graph Neural Networks：https://arxiv.org/pdf/2404.02300
    - 引文：to improve the quality of partitioning, we propose SPRING, a novel streaming partitioning algorithm for distributed GNN training.
    - 位置：artifact art_54da6e025cc0ed386d08e5d1 chars:769-898

### card_055dcd710a45194158c1d5ba · 2PS: High-Quality Edge Partitioning with Two-Phase Streaming

- 查新点：NP-3
- 主要贡献：Proposes 2PS, a two-phase streaming edge partitioning algorithm that separates vertices into clusters in the first phase and performs edge partitioning in the second phase, achieving low replication factor with low memory overhead.
- 相关性：0.60
- 置信度：0.80
- 来源：
  - 2PS: High-Quality Edge Partitioning with Two-Phase Streaming：https://arxiv.org/pdf/2001.07086
    - 引文：In this paper, we propose 2PS, a novel two-phase streaming algorithm for high-quality edge partitioning. In the first phase, vertices are separated into clusters by a lightweight streaming clustering algorithm. In the second phase, the graph is re-streamed and edge partitioning is performed while taking into account the clustering of the vertices from the first phase.
    - 位置：artifact art_082358a7cb0efe62d471f7fb chars:844-1214

### card_927caf724042beff967b2231 · Window-based Streaming Graph Partitioning Algorithm

- 查新点：NP-3
- 主要贡献：Proposes WStream, a window-based streaming graph partitioning algorithm (edge-cut partitioning) that partitions large graph data while keeping load balanced across partitions and minimizing communication.
- 相关性：0.60
- 置信度：0.80
- 来源：
  - Window-based Streaming Graph Partitioning Algorithm：10.1145/3290688.3290711
    - 引文：This paper proposes an efficient window-based streaming graph partitioning algorithm called WStream. The WStream algorithm is an edge-cut partitioning algorithm, which distributes a vertex among the partitions. Our results suggest that the WStream algorithm is able to partition large graph data efficiently while keeping the load balanced across different partitions, and communication to a minimum.
    - 位置：artifact art_044b624240993e16c40f3537 chars:713-1113

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 1 | 有证据 |
| NP-2 | 2 | 有证据 |
| NP-3 | 2 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图压缩为固定规模的新图，解决GNN输出无法直接输入RNN的问题，并利用图自编码器与循环神经网络学习时序特征。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - wrk_0816eb289770aba763747fae：该文献与查新点存在局部相关性；具体技术差异尚待原文核验。 (cards: card_e0f18431d0e8ab03ad5ce4a0)

### NP-2 · 证据不足，无法裁定

提出一种基于图摘要的分布式图神经网络训练框架DSGNN，采用“领导-工作者”模式，领导节点负责图划分和模型同步更新，工作节点基于图摘要技术进行小批量训练，并通过注意力层返回结果。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - wrk_e5865fd0794a0b6b82d47144：该文献与查新点存在局部相关性；具体技术差异尚待原文核验。 (cards: card_018e754c5aefa7a7078c1414)
  - wrk_0c0af5018413ad476ba2d09d：该文献与查新点存在局部相关性；具体技术差异尚待原文核验。 (cards: card_76436aaa84bd83613d169b2a)

### NP-3 · 证据不足，无法裁定

提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - wrk_b77f32398f578aa48e68b57c：该文献提出两阶段流式边分割算法，与查新点同属边分割图流划分领域，但未展示是否采用Count-Min Sketch或最小堆，需核验原文以确认技术差异。 (cards: card_055dcd710a45194158c1d5ba)
  - wrk_dd602dc2d2b07d7e69e6724c：该文献提出基于窗口的流式图划分算法，强调负载均衡，与查新点目标相关，但未展示是否采用Count-Min Sketch或最小堆，需核验原文以确认技术差异。 (cards: card_927caf724042beff967b2231)

---

## 八、报告局限

- 本次检索命中相关候选文献，但Reviewer裁定各查新点均属证据不足：现有引文未能直接否定关键特征被采用，需核验原文完整技术细节后方可判断新颖性。
- 检索覆盖范围：仅执行英文文献检索，未明确覆盖中文数据库、专利及非公开文献，检索覆盖程度未知。
- 由于未获得检索执行的成功/失败事实，无法区分检索失败与零命中；当前状态为“有命中但未形成充分证据”。
- 未有被拒绝的证据（rejected_evidence为空），不存在技术性/格式性拒绝情形。

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

- Seq-HGNN: Learning Sequential Node Representation on Heterogeneous Graph：[https://arxiv.org/pdf/2305.10771](https://arxiv.org/pdf/2305.10771)
- End-to-End Graph-Sequential Representation Learning for Accurate Recommendations：[https://arxiv.org/pdf/2403.00895](https://arxiv.org/pdf/2403.00895)
- Knowledge Representation via Joint Learning of Sequential Text and Knowledge Graphs：[https://arxiv.org/pdf/1609.07075](https://arxiv.org/pdf/1609.07075)
- Beyond Flat Netlist: Hierarchical Graph Representation Learning for Scalable Analysis of Sequential Circuits：[https://arxiv.org/pdf/2608.28188](https://arxiv.org/pdf/2608.28188)
- Learning Dual Dynamic Representations on Time-Sliced User-Item Interaction Graphs for Sequential Recommendation：[https://arxiv.org/pdf/2109.11790](https://arxiv.org/pdf/2109.11790)
- SDT-GNN: Streaming-based Distributed Training Framework for Graph Neural Networks：[https://arxiv.org/pdf/2404.02300](https://arxiv.org/pdf/2404.02300)
- ABC: Aggregation before Communication, a Communication Reduction Framework for Distributed Graph Neural Network Training and Effective Partition：[https://arxiv.org/pdf/2212.05410](https://arxiv.org/pdf/2212.05410)
- Window-based Streaming Graph Partitioning Algorithm：[https://arxiv.org/pdf/1902.01543](https://arxiv.org/pdf/1902.01543)
- An Experimental Comparison of Partitioning Strategies for Distributed Graph Neural Network Training：[https://arxiv.org/pdf/2308.15602](https://arxiv.org/pdf/2308.15602)
- Time-Efficient and High-Quality Graph Partitioning for Graph Dynamic Scaling：[https://arxiv.org/pdf/2101.07026](https://arxiv.org/pdf/2101.07026)
- KaHIP v3.00 -- Karlsruhe High Quality Partitioning -- User Guide：[https://arxiv.org/pdf/1311.1714](https://arxiv.org/pdf/1311.1714)
- Out-of-Core Edge Partitioning at Linear Run-Time：[https://arxiv.org/pdf/2203.12721](https://arxiv.org/pdf/2203.12721)
- Scalable Edge Partitioning：[https://arxiv.org/pdf/1808.06411](https://arxiv.org/pdf/1808.06411)
- 2PS: High-Quality Edge Partitioning with Two-Phase Streaming：[https://arxiv.org/pdf/2001.07086](https://arxiv.org/pdf/2001.07086)
- WindGP: Efficient Graph Partitioning on Heterogenous Machines：[https://arxiv.org/pdf/2403.00331](https://arxiv.org/pdf/2403.00331)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
