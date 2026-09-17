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

### NP-3 · 部分新颖

提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 两篇单卡文献均属于图流边划分领域，与查新点存在领域重合，但均未公开核心特征组合（Count-Min Sketch存储节点度数、最小堆维护高频节点、常数时间查询）。2PS采用两阶段聚类，WStream采用窗口策略，均未使用CMS或最小堆，也未描述常数时间查询机制。因此，Sketch-DBH的核心技术组合未见公开，判定为部分新颖。  
**置信度：** 0.75  
**报告摘要：** 两篇单卡文献均属于图流边划分领域，与查新点存在领域重合，但均未公开核心特征组合（Count-Min Sketch存储节点度数、最小堆维护高频节点、常数时间查询）。2PS采用两阶段聚类，WStream采用窗口策略，均未使用CMS或最小堆，也未描述常数时间查询机制。因此，Sketch-DBH的核心技术组合未见公开，判定为部分新颖。  
**未完成原因：** —  
**高度相关 Work：**
  - wrk_b77f32398f578aa48e68b57c：同属图流边划分领域，采用流式边分配策略并追求负载均衡与低复制因子，与查新点领域重合，但技术路径（两阶段聚类）与查新点（CMS+最小堆）不同。 (cards: card_055dcd710a45194158c1d5ba)
  - wrk_dd602dc2d2b07d7e69e6724c：同属图流划分领域，以负载均衡为核心目标，但采用窗口边割策略而非Sketch-DBH的Count-Min Sketch+最小堆方案，作为领域相关基线文献。 (cards: card_927caf724042beff967b2231)

**原文核验证据：**
  - rev_ev_e2663c36430ee389173dee14 · wrk_b77f32398f578aa48e68b57c · art_082358a7cb0efe62d471f7fb [0, 1397): Graph partitioning is an important preprocessing step to distributed graph processing. In edge partitioning, the edge set of a given graph is split into $k$ equally-sized partitions, such that the replication of vertices across partitions is minimized. Streaming is a viable approach to partition graphs that exceed the memory capacities of a single server. The graph is ingested as a stream of edges, and one edge at a time is immediately and irrevocably assigned to a partition based on a scoring function. However, streaming partitioning suffers from the uninformed assignment problem: At the time of partitioning early edges in the stream, there is no information available about the rest of the edges. As a consequence, edge assignments are often driven by balancing considerations, and the achieved replication factor is comparably high. In this paper, we propose 2PS, a novel two-phase streaming algorithm for high-quality edge partitioning. In the first phase, vertices are separated into clusters by a lightweight streaming clustering algorithm. In the second phase, the graph is re-streamed and edge partitioning is performed while taking into account the clustering of the vertices from the first phase. Our evaluations show that 2PS can achieve a replication factor that is comparable to heavy-weight random access partitioners while inducing orders of magnitude lower memory overhead.
  - rev_ev_1c9a7ae2fb19ed1d25c1ec50 · wrk_b77f32398f578aa48e68b57c · art_ebc47b0e70f5b363f3d871f2 [0, 2000): 2PS: High-Quality Edge Partitioning with Two-Phase Streaming

      Report GitHub Issue
      ×

      Title:

Content selection saved. Describe the issue below:

      Description:

      Submit without GitHub
      Submit in GitHub

    arXiv is now an independent nonprofit!
    Learn more
    ×

      Back to arXiv

    Why HTML?

      Report Issue

      Back to Abstract

      Download PDF

Abstract

1 Introduction

2 Problem Analysis

2.1 Edge Partitioning Problem

2.2 Streaming Edge Partitioning

2.3 Shortcomings of Streaming Partitioning

3 Two-Phase Streaming Edge Partitioning

3.1 Phase 1: Clustering

3.1.1 Streaming Clustering Algorithm

3.2 Phase 2: Partitioning

3.3 Discussion of Design Choices

4 Theoretical Analysis

4.1 Time Complexity

4.2 Space Complexity

4.3 Replication Factor

5 Evaluations

5.1 Setup

5.2 Performance on Real-World Graphs

Main Observations

5.3 Impact of Power-Law Degree

6 Related Work

7 Conclusions

References

    License: arXiv.org perpetual non-exclusive license

arXiv:2001.07086v1 [cs.DC] 20 Jan 2020

2PS: High-Quality Edge Partitioning with Two-Phase Streaming

Ruben Mayer
††thanks: Both authors contributed equally to this paper.
Affiliation: Technical University of Munich

  
Kamil Orujzade11footnotemark:
          1

Affiliation: Technical University of Munich

  
Hans-Arno Jacobsen

Affiliation: Technical University of Munich

Abstract

Graph partitioning is an important preprocessing step to distributed graph processing. In edge partitioning, the edge set of a given graph is split into kk equally-sized partitions, such that the replication of vertices across partitions is minimized. Streaming is a viable approach to partition graphs that exceed the memory capacities of a single server. The graph is ingested as a stream of edges, and one edge at a time is immediately and irrevocably assigned to a partition based on a scoring function. However, streaming partitioning suffers from the uninformed assignment problem: At
  - rev_ev_915b523429f70453af896d5c · wrk_b77f32398f578aa48e68b57c · art_ebc47b0e70f5b363f3d871f2 [53687, 55687): 6 Related Work

Graph partitioning is a problem with a long history in research [8]. It has numerous applications in solving optimization problems, e.g., in VLSI design [18] and operator placement in stream processing systems [19]. In this paper, we focus on the edge partitioning problem. In particular, edge partitioning has gained a lot of attention as a preprocessing step for distributed graph processing systems, e.g., PowerGraph [12] and Spark/GraphX [13].

Random-access partitioners [43, 25, 15] require full information about the graph structure, i.e., the complete graph is loaded into memory of either a single machine [43] or a cluster of multiple machines [25, 15] before partitioning is performed. The major shortcoming of such partitioners is that they consume a lot of memory. However, memory is a scarce and expensive resource. While a single machine may not have sufficient memory capacities to keep a large graph, employing a cluster of machines to perform graph partitioning induces a higher monetary cost. Streaming edge partitioning is a common approach to reduce the memory overhead of edge partitioning.

There are a number of approaches to streaming edge partitioning. Besides stateless partitioning based on hashing (e.g., DBH [41]), stateful partitioners have received growing attention. The basic idea is that by gathering state about past assignment decisions, future edges in the stream can be partitioned with a lower replication degree. In this regard, the main differentiation between streaming partitioners so far has been in the formulation of the scoring function. Different such functions have been proposed, e.g., Greedy [12] and HDRF [32]. However, all of these approaches suffer from the uninformed assignment problem. An earlier approach to overcome this problem has been proposed in ADWISE [28], which allows for dynamically re-ordering the edge stream such that the assignment of uninformed edges can be delayed. This way, locality in the edge stream can b
  - rev_ev_0381d59b9f875c77fad7c6a3 · wrk_b77f32398f578aa48e68b57c · art_ebc47b0e70f5b363f3d871f2 [16701, 18701): 3.1.1 Streaming Clustering Algorithm

Algorithm 1  2PS Phase 1: Clustering

                1:

              int[] d ⊳\triangleright vertex degrees

                2:

              int[] vol ⊳\triangleright cluster volumes

                3:

              int[] v2c ⊳\triangleright map of vertex_id to cluster_id

                4:

              int max_vol ⊳\triangleright maximum cluster volume

                5:

              int next_id ←\leftarrow 0 ⊳\triangleright id of next new cluster

                6:

              procedure streamingClustering

                7:

                max_vol ←\leftarrow 2∗|E|k∗0.5\frac{2*|E|}{k}*0.5

                8:

                performStreamingPass() ⊳\triangleright first pass

                9:

                max_vol ←\leftarrow max_vol ∗2*2

                10:

                performStreamingPass() ⊳\triangleright second pass

                11:

              procedure performStreamingPass

                12:

                for each e∈e\in edge_stream do

                13:

                 for each v∈ev\in e do

                14:

                   if v2c[v] = NULL then

                15:

                    v2c[vv] ←\leftarrow next_id

                16:

                    vol[next_id] ←\leftarrow vol[next_id] + d[vv]

                17:

                    next_id ←\leftarrow next_id + 1
        

                18:

                 if vol[v2c[vv]] ≤\leq max_vol ∀v∈e\forall v\in e then

                19:

                   vs←v_{\mathit{s}}\leftarrow vi∈e:v_{i}\in e:vol[v2c[viv_{i}]] ≤\leq vol[v2c[vjv_{j}]], vj∈ev_{j}\in e

                20:

                   vl←v_{\mathit{l}}\leftarrow vj∈e:vj≠vsv_{j}\in e:v_{j}\neq v_{\mathit{s}}

                21:

                   if vol[v2c[vlv_{l}]] ++ d[vsv_{s}] ≤\leq max_vol then

                22:

                    v2c[vsv_{s}] ←\leftarrow v2c[vlv_{l}]

                23:

                    vol[v2c[vlv_{l}]] ←\leftarrow
  - rev_ev_68a6df2fb2bf9b8687fd0a69 · wrk_dd602dc2d2b07d7e69e6724c · art_044b624240993e16c40f3537 [713, 1313): This paper proposes an efficient window-based streaming graph partitioning algorithm called WStream. The WStream algorithm is an edge-cut partitioning algorithm, which distributes a vertex among the partitions. Our results suggest that the WStream algorithm is able to partition large graph data efficiently while keeping the load balanced across different partitions, and communication to a minimum. Evaluation results with real workloads also prove the effectiveness of our proposed algorithm, and it achieves a significant reduction in load imbalance and edge-cut with different ranges of dataset.
  - rev_ev_37363d07e01e1ba87e945b6a · wrk_dd602dc2d2b07d7e69e6724c · art_239d9f203a9c73612f1cbbaa [0, 2000): Window-based Streaming Graph Partitioning Algorithm

      Report GitHub Issue
      ×

      Title:

Content selection saved. Describe the issue below:

      Description:

      Submit without GitHub
      Submit in GitHub

    arXiv is now an independent nonprofit!
    Learn more
    ×

      Back to arXiv

    Why HTML?

      Report Issue

      Back to Abstract

      Download PDF

Abstract

1 Introduction

2 Related Work

2.1 Vertex-cut Partitioning

2.2 Edge-cut Partitioning

3 Proposed Algorithm

3.1 Preliminaries

3.2 System Architecture

3.3 The Streaming Model and Window

3.4 WStream Algorithm

3.5 Greedy Strategy

4 Performance Evaluation

4.1 Experimental Settings

4.2 Dataset

4.3 Performance Metrics

4.4 Evaluation Scenario

5 Results Analysis

5.1 Impact of Stream Window Sizes

5.2 Impact of Balancing Factor

5.3 Performance Comparison

5.3.1 Edge-cut comparison

5.3.2 Load Imbalance Comparison

6 Conclusions and Future Direction

References

    License: arXiv.org perpetual non-exclusive license

arXiv:1902.01543v1 [cs.DS] 05 Feb 2019

Window-based Streaming Graph Partitioning Algorithm

Md Anwarul Kaium Patwary

  
Saurabh Garg, and Byeong Kang

Abstract

In the recent years, the scale of graph datasets has increased to such a degree that a single machine is not capable of efficiently processing large graphs. Thereby, efficient graph partitioning is necessary for those large graph applications. Traditional graph partitioning generally loads the whole graph data into the memory before performing partitioning; this is not only a time consuming task but it also creates memory bottlenecks. These issues of memory limitation and enormous time complexity can be resolved using stream-based graph partitioning. A streaming graph partitioning algorithm reads vertices once and assigns that vertex to a partition accordingly. This is also called an one-pass algorithm. This paper proposes an efficient window-based streaming graph partitioning algorithm called WS
  - rev_ev_db49817e65f54206b7c51223 · wrk_dd602dc2d2b07d7e69e6724c · art_239d9f203a9c73612f1cbbaa [16004, 18004): 3 Proposed Algorithm

3.1 Preliminaries

We consider an undirected graph GG, with a set of edges EE and vertices VV, such that G=(V,E)G=(V,E). A balanced k-way partitioning divides the graph into almost equal subsets. The graph partitioning algorithm uses a balancing constraint to keep all the partitions balanced. The balancing constraint can be defined by Equation (1):

∀i∈{1..k}:|Vi|≤Lm​a​x:=(1+α)⌈|V|/k⌉\forall_{i}\in\{1..k\}:|V_{i}|\leq L_{max}:=(1+\alpha)\lceil|V|/k\rceil

(1)

Where, α\alpha is the imbalanced parameter, and is a non-negative real number. The vertex vv is adjacent to vertex uu given there is an edge {u,v}∈E\{u,v\}\in E. If vertex vv and vertex uu reside in different partitions, this is called the cut edge. Thus, Ei​j:={{u,v}∈E:u∈Vi,v∈Vj}E_{ij}:=\{\{u,v\}\in E:u\in V_{i},v\in V_{j}\} is the set of edge-cuts between partitions. Edge-cut graph partitioning always aims at reducing this cut.

3.2 System Architecture

In our system, we used master machines, which is responsible for reading input, and assign the vertices to the clients. As such partitioning algorithm resides in the master machines. We used a Stream Generator which creates the stream data after receiving the input and then form a stream window. We used a distributed meta data file which has been used to store the information of vertices are already seen in the stream. This information was used to assign the future vertices from stream of data. Figure 1 shows the architecture of the system.

•

Master Machine: Master machine receives the input graph data from the input file. In master machine the Stream Generator, generates the stream data and maintained the stream window before assigning each vertex to the respective partition. It also stores the partitioned vertex information and later this uses for future vertex partition.

•

Partition: Each partition also known as worker machine communicate with master machine to receive the assigned vertex from the master machine. Worker machine al

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
