# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-18T01:26:40+08:00 |
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

- 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
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

共执行 1 轮检索计划，生成 2 张原始证据卡；通过 2 张，拒绝 0 张。

### 6.2 相关文献

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
| NP-3 | 2 | 有证据 |

---

## 七、查新结论

### NP-3 · 新颖

提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。

**Reviewer 裁定：** 新颖  
**裁定理由：** 两篇单卡文献均未公开查新点声称的完整技术组合。2PS 采用两阶段流式聚类机制，WStream 采用窗口边割机制，均未提及 Count-Min Sketch 度数存储、最小堆高频节点维护、常数时间查询或基于度数生成子图编号。两篇文献仅部分支持负载均衡目标（F5），不构成对组合的预期。但 F1-F4 在 2PS 中因摘要未提及而属未知，WStream 中因机制不同而判定为矛盾，均未确认采用；多篇分别覆盖部分特征不等于单篇公开完整组合，故新颖性成立，置信度中等。  
**置信度：** 0.60  
**报告摘要：** 两篇单卡文献均未公开查新点声称的完整技术组合。2PS 采用两阶段流式聚类机制，WStream 采用窗口边割机制，均未提及 Count-Min Sketch 度数存储、最小堆高频节点维护、常数时间查询或基于度数生成子图编号。两篇文献仅部分支持负载均衡目标（F5），不构成对组合的预期。但 F1-F4 在 2PS 中因摘要未提及而属未知，WStream 中因机制不同而判定为矛盾，均未确认采用；多篇分别覆盖部分特征不等于单篇公开完整组合，故新颖性成立，置信度中等。  
**未完成原因：** —  
**高度相关 Work：**
  - wrk_b77f32398f578aa48e68b57c：同属图流边划分领域，共享负载均衡目标，但采用两阶段聚类机制，与查新点的 CMS+最小堆+常数时间查询机制不同，属部分相关文献。 (cards: card_055dcd710a45194158c1d5ba)
  - wrk_dd602dc2d2b07d7e69e6724c：同属流式图划分领域，确认负载均衡目标，但采用窗口边割机制，未覆盖查新点的 CMS+最小堆+常数时间查询+度数子图编号组合。 (cards: card_927caf724042beff967b2231)

**原文核验证据：**
  - rev_ev_e2663c36430ee389173dee14 · wrk_b77f32398f578aa48e68b57c · art_082358a7cb0efe62d471f7fb [0, 1397): Graph partitioning is an important preprocessing step to distributed graph processing. In edge partitioning, the edge set of a given graph is split into $k$ equally-sized partitions, such that the replication of vertices across partitions is minimized. Streaming is a viable approach to partition graphs that exceed the memory capacities of a single server. The graph is ingested as a stream of edges, and one edge at a time is immediately and irrevocably assigned to a partition based on a scoring function. However, streaming partitioning suffers from the uninformed assignment problem: At the time of partitioning early edges in the stream, there is no information available about the rest of the edges. As a consequence, edge assignments are often driven by balancing considerations, and the achieved replication factor is comparably high. In this paper, we propose 2PS, a novel two-phase streaming algorithm for high-quality edge partitioning. In the first phase, vertices are separated into clusters by a lightweight streaming clustering algorithm. In the second phase, the graph is re-streamed and edge partitioning is performed while taking into account the clustering of the vertices from the first phase. Our evaluations show that 2PS can achieve a replication factor that is comparable to heavy-weight random access partitioners while inducing orders of magnitude lower memory overhead.
  - rev_ev_7daecd55b2287ae3abed1eb9 · wrk_b77f32398f578aa48e68b57c · art_082358a7cb0efe62d471f7fb [844, 1244): In this paper, we propose 2PS, a novel two-phase streaming algorithm for high-quality edge partitioning. In the first phase, vertices are separated into clusters by a lightweight streaming clustering algorithm. In the second phase, the graph is re-streamed and edge partitioning is performed while taking into account the clustering of the vertices from the first phase. Our evaluations show that 2PS
  - rev_ev_85c15c242fd26ca9a070ecbf · wrk_dd602dc2d2b07d7e69e6724c · art_044b624240993e16c40f3537 [0, 1313): In the recent years, the scale of graph datasets has increased to such a degree that a single machine is not capable of efficiently processing large graphs. Thereby, efficient graph partitioning is necessary for those large graph applications. Traditional graph partitioning generally loads the whole graph data into the memory before performing partitioning; this is not only a time consuming task but it also creates memory bottlenecks. These issues of memory limitation and enormous time complexity can be resolved using stream-based graph partitioning. A streaming graph partitioning algorithm reads vertices once and assigns that vertex to a partition accordingly. This is also called an one-pass algorithm. This paper proposes an efficient window-based streaming graph partitioning algorithm called WStream. The WStream algorithm is an edge-cut partitioning algorithm, which distributes a vertex among the partitions. Our results suggest that the WStream algorithm is able to partition large graph data efficiently while keeping the load balanced across different partitions, and communication to a minimum. Evaluation results with real workloads also prove the effectiveness of our proposed algorithm, and it achieves a significant reduction in load imbalance and edge-cut with different ranges of dataset.

---

## 八、报告局限

- 本文件仅演示固定 NP-3 Reviewer-only 结果的本地报告绑定；没有重跑完整工作流。
- 最终技术关系仍需核对单卡引用的原文语境。

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
