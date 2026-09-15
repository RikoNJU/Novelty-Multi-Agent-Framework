# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-15T21:55:05+08:00 |
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

- 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩图快照，结合图自编码器与循环神经网络，高效生成动态时序图的低维表征。
- 提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导者-工作者模式，通过边分割图流划分算法划分图，各工作节点进行基于图摘要的小批量训练，并通过注意力层聚合结果，实现大规模图流数据的快速训练。
- 提出了一种基于边分割的图流划分算法，用于大规模图流数据的分布式划分，该算法利用图的边信息进行分割，能够适应图数据的不规则性，实现高效且均衡的子图划分。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩图快照，结合图自编码器与循环神经网络，高效生成动态时序图的低维表征。 | Proposed GSAERU, a large-scale sequential graph representation learning method based on graph summarization, which compresses graph snapshots, combines graph autoencoder and recurrent neural network to efficiently generate low-dimensional representations of dynamic sequential graphs. |
| NP-2 | 提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导者-工作者模式，通过边分割图流划分算法划分图，各工作节点进行基于图摘要的小批量训练，并通过注意力层聚合结果，实现大规模图流数据的快速训练。 | Proposed DSGNN, a distributed graph neural network optimization training algorithm based on graph summarization, which adopts leader-worker mode, partitions the graph with an edge-based graph flow partitioning algorithm, performs graph summarization-based mini-batch training on workers, and aggregates results through an attention layer, enabling efficient training on large-scale graph streaming data. |
| NP-3 | 提出了一种基于边分割的图流划分算法，用于大规模图流数据的分布式划分，该算法利用图的边信息进行分割，能够适应图数据的不规则性，实现高效且均衡的子图划分。 | Proposed an edge-based graph flow partitioning algorithm for distributed partitioning of large-scale graph streaming data, which utilizes graph edge information for segmentation, adapts to the irregularity of graph data, and enables efficient and balanced subgraph partitioning. |

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
  - `("dynamic sequential graph" OR "temporal graph" OR "dynamic graph") AND ("graph summarization" OR "graph compression")`
- **NP-2**
  - 无
- **NP-3**
  - `("edge-based graph partitioning" OR "edge-based graph stream partitioning" OR "edge-cut partitioning")`

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 6 张原始证据卡；通过 6 张，拒绝 0 张。

### 6.2 相关文献

### card_fa58976d87c718a7d5817694 · Inductive Representation Learning on Temporal Graphs

- 查新点：NP-1
- 主要贡献：Temporal Graph Attention (TGAT) layer for inductive representation learning on temporal graphs, using self-attention and a functional time encoding technique.
- 相关性：0.60
- 置信度：0.85
- 来源：
  - Inductive Representation Learning on Temporal Graphs：https://arxiv.org/pdf/2002.07962
    - 引文：We propose the temporal graph attention (TGAT) layer to efficiently aggregate temporal-topological neighborhood features as well as to learn the time-feature interactions.
    - 位置：artifact art_b8b821043e4485fda0b8527c chars:516-687

### card_d3ae4ea3ad208a4f19e5be7c · Temporal Graph Networks for Deep Learning on Dynamic Graphs

- 查新点：NP-1
- 主要贡献：Temporal Graph Networks (TGNs): a generic, efficient framework for deep learning on dynamic graphs represented as sequences of timed events, combining memory modules and graph-based operators.
- 相关性：0.60
- 置信度：0.85
- 来源：
  - Temporal Graph Networks for Deep Learning on Dynamic Graphs：https://arxiv.org/pdf/2006.10637
    - 引文：we present Temporal Graph Networks (TGNs), a generic, efficient framework for deep learning on dynamic graphs represented as sequences of timed events. Thanks to a novel combination of memory modules and graph-based operators
    - 位置：artifact art_ea01d9c5f48ad68092a07bf7 chars:520-745

### card_1800ebe9811ad96dfd604571 · AGL: a Scalable System for Industrial-purpose Graph Machine Learning

- 查新点：NP-2
- 主要贡献：AGL is a scalable, fault-tolerant and integrated system for distributed GNN training and inference using parameter servers and k-hop neighborhood subgraphs.
- 相关性：0.55
- 置信度：0.85
- 来源：
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：we design AGL, a scalable, fault-tolerance and integrated system, with fully-functional training and inference for GNNs.
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1021-1141

### card_396b3a2c53a363562c5987e7 · AliGraph: A Comprehensive Graph Neural Network Platform

- 查新点：NP-2
- 主要贡献：AliGraph is a comprehensive distributed graph neural network platform providing distributed graph storage, optimized sampling operators and runtime to support GNN training at scale.
- 相关性：0.60
- 置信度：0.85
- 来源：
  - AliGraph: A Comprehensive Graph Neural Network Platform：https://arxiv.org/pdf/1902.08730
    - 引文：we present a comprehensive graph neural network system, namely AliGraph, which consists of distributed graph storage, optimized sampling operators and runtime to efficiently support not only existing popular GNNs but also a series of in-house developed ones for different scenarios.
    - 位置：artifact art_d88778158223021b818fdd97 chars:649-931

### card_ea7d9077219f8d5b4a3b1383 · GraphSAINT: Graph Sampling Based Inductive Learning Method

- 查新点：NP-2
- 主要贡献：GraphSAINT is a graph sampling based inductive learning method that constructs mini-batches by sampling the training graph, improving training efficiency and accuracy for GNNs.
- 相关性：0.50
- 置信度：0.85
- 来源：
  - GraphSAINT: Graph Sampling Based Inductive Learning Method：https://arxiv.org/pdf/1907.04931
    - 引文：We propose GraphSAINT, a graph sampling based inductive learning method that improves training efficiency and accuracy in a fundamentally different way. By changing perspective, GraphSAINT constructs minibatches by sampling the training graph, rather than the nodes or edges across GCN layers.
    - 位置：artifact art_4144023700aceff174c81183 chars:274-567

### card_05fe604814671131d009b01e · Scalability and performance in distributed graph databases

- 查新点：NP-3
- 主要贡献：This paper presents a comparative analysis of four graph partitioning strategies (Random Vertex, Metis-based, Random Edge, and HDRF) spanning both edge-cut and vertex-cut paradigms for distributed graph databases, evaluating them on metrics including edge cut, replication factor, load balance, latency, and throughput. It shows HDRF provides superior performance and scalability for dynamic, power-law networks.
- 相关性：0.70
- 置信度：0.80
- 来源：
  - Scalability and performance in distributed graph databases：10.1007/s10586-026-06406-0
    - 引文：This paper presents a comparative analysis of four partitioning strategies Random Vertex, Metis-based, Random Edge, and HDRF spanning both edge-cut and vertex-cut paradigms.
    - 位置：artifact art_dc41a5a066be129dd98d34d0 chars:161-334
  - Scalability and performance in distributed graph databases：10.1007/s10586-026-06406-0
    - 引文：Results show that while Metis achieves optimal partition quality for static, balanced graphs, HDRF provides superior performance and scalability for dynamic, power-law networks.
    - 位置：artifact art_dc41a5a066be129dd98d34d0 chars:600-777
  - Scalability and performance in distributed graph databases：10.1007/s10586-026-06406-0
    - 引文：Graph partitioning is a critical enabler of scalability in distributed graph databases, impacting load balancing, communication overhead, and query performance.
    - 位置：artifact art_dc41a5a066be129dd98d34d0 chars:0-160

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 2 | 有证据 |
| NP-2 | 3 | 有证据 |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩图快照，结合图自编码器与循环神经网络，高效生成动态时序图的低维表征。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 现有两条证据（TGAT、TGN）均表明时序图表示学习领域已有相关工作，但均未采用“图摘要压缩+图自编码器+循环神经网络”的技术组合，故未构成直接冲突。然而Reviewer因证据覆盖和解析问题未能完成完整判定，需要补充检索以确认该组合是否已被公开披露，因此维持证据不足状态。  
**高度相关 Work：**
  - 无

### NP-2 · 新颖

提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导者-工作者模式，通过边分割图流划分算法划分图，各工作节点进行基于图摘要的小批量训练，并通过注意力层聚合结果，实现大规模图流数据的快速训练。

**Reviewer 裁定：** 新颖  
**裁定理由：** 查新点NP-2主张DSGNN将四要素组合：领导-工作者分布式架构、基于边分割的图流划分、基于图摘要的小批量训练、经注意力层的领导侧聚合与同步更新。已检索证据（AGL、AliGraph、GraphSAINT）虽覆盖分布式GNN训练与大图小批量训练等孤立侧面，但均未呈现该组合：AGL采用参数服务器架构与k-hop邻域子图而非领导-工作者+注意力聚合，且未用图摘要；AliGraph依赖分布式存储与采样算子而非图摘要小批量训练；GraphSAINT仅单机、用图采样而非图摘要、无注意力聚合。按原文对具体判断的支撑程度审查，三条证据均仅能佐证分布式训练与小批量图采样为已有方向，均未能构成对'图摘要+领导-工作者注意力聚合+边分割图流划分+同步更新'组合的完整公开，故判定该组合相对现有证据具备新颖性。  
**置信度：** 0.70  
**报告摘要：** 现有证据（AGL、AliGraph、GraphSAINT）仅覆盖分布式GNN训练、图采样或小批量训练等孤立侧面，未披露DSGNN的完整组合（图摘要+领导-工作者注意力聚合+边分割图流划分），因此判定为新颖。  
**高度相关 Work：**
  - wrk_ff5aa18cf0cfe7be1ba5e8bd：AGL可佐证分布式GNN训练为已有方向，但其用参数服务器架构与k-hop子图，而非本查新点的领导-工作者+注意力聚合+图摘要组合，故为基线而非冲突证据。 (cards: card_1800ebe9811ad96dfd604571)
  - wrk_e59b8b7248dcc080455b8690：AliGraph佐证大规模分布式GNN训练为已有研究领域，但依赖分布式存储与采样算子，不采用图摘要小批量训练或领导-工作者注意力聚合，为基线对比文献。 (cards: card_396b3a2c53a363562c5987e7)
  - wrk_9567984f4fecd1cfc596ae3b：GraphSAINT用小批量图采样提升效率，与本查新点的小批量训练侧面相关，但为单机、用采样而非图摘要、无注意力聚合，仅覆盖孤立侧面而非完整组合。 (cards: card_ea7d9077219f8d5b4a3b1383)

### NP-3 · 部分新颖

提出了一种基于边分割的图流划分算法，用于大规模图流数据的分布式划分，该算法利用图的边信息进行分割，能够适应图数据的不规则性，实现高效且均衡的子图划分。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 查新点NP-3声称提出了一种基于边分割的图流划分算法，其四个技术特征为：基于边分割的划分策略、针对图流数据的动态划分、适应图数据的不规则性、用于分布式场景中的子图分配。当前唯一证据（wrk_df8c0752cb7bc7b40b51da06，《Scalability and performance in distributed graph databases》）是一篇对现有四种划分策略（Random Vertex、Metis、Random Edge、HDRF）在边切与顶点切范式下针对分布式图数据库的性能对比评测。经核对原文，该文献直接展示了基于边分割的划分策略（Random Edge、HDRF）、适应图数据的动态/不规则性（'dynamic, power-law networks'）以及分布式场景下的子图划分与负载均衡——四个技术特征在该文献中均以既有技术形式出现，尤其是HDRF作为流式边分配策略，已在分布式动态不规则图上被验证。因此查新点声称的四个技术特征并非全新，现有技术已对各项特征给出实质覆盖。但该文献为对比基准评测而非提出查新点所指的具体新型图流划分算法，未直接披露与应用方完全相同的特定算法实现，故判定为部分新颖。  
**置信度：** 0.62  
**报告摘要：** 已有文献对比了Random Edge、HDRF等基于边分割的划分策略在分布式动态/不规则图上的性能，实质覆盖了本查新点的技术特征（边分割、动态图流、不规则性、分布式子图划分），因此该查新点不具备完全新颖性；但现有文献未披露与本查新点完全相同的特定新型算法，故为部分新颖。  
**高度相关 Work：**
  - wrk_df8c0752cb7bc7b40b51da06：该文献对比评测了Random Edge与HDRF等基于边分割的划分策略，明确评估了其在分布式环境中针对动态幂律（不规则）图网络的性能、可扩展性与负载均衡。其四个技术特征（基于边分割策略、动态/流式边分配、适应图数据不规则性、分布式子图划分）与查新点NP-3的四个技术特征高度吻合，构成对查新点主要技术特征的现有技术实质覆盖。虽为对比基准评测而非提出特定新型算法，仍是判定查新点新颖性最相关、最关键的对比文献。 (cards: card_05fe604814671131d009b01e)

---

## 八、报告局限

- NP-1：虽有2条有效证据卡，但Reviewer判定为证据不足（insufficient_evidence），原因是Reviewer状态解析失败（Invalid JSON），无法给出可靠判定；且中文文献覆盖情况未知，建议补充检索和图摘要+时序GNN的组合文献。现有证据仅能说明动态时序图表示学习为已有方向，但未形成对技术组合的确定性结论。
- NP-2：已获有效证据3条，均支持“分布式GNN训练和小批量采样”为已有技术方向，但未披露DSGNN的组合方案，故裁定为新颖。但检索覆盖不完整：中文检索任务T-1未返回有效证据，中文语域的覆盖缺失，且缺少“图摘要+分布式GNN训练”交叉方向的一手文献，需补检以排除潜在破坏性披露。
- NP-3：仅有一条有效证据，且该证据为对比基准评测（二手/综述性质），非一手算法文献。现有文献已覆盖边分割、动态图流、不规则性、分布式子图划分等技术特征，但未直接披露查新点所指的特定算法实现。为更严谨地支持部分新颖判定，需补检HDRF、Fennel等流式边划分算法的原始提出文献及中文相关文献。检索覆盖仍不完整。
- 所有查新点的被拒绝证据列表均为空，不存在因门控拒绝而被排除的有效证据；未发现技术性质疑或格式性拒绝。

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

- Temporal Graph Classification Based on Fast and Exact Transitive Reduction Strategy：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37673-2_25](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37673-2_25)
- Part-GNN: A Partitioning-Based Graph Neural Network for Efficient Memory Large Scale Data Classification：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-2597-2_39](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-2597-2_39)
- Design of a Query Expression for Multi-Dimensional Graph Warehousing：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-32726-0_4](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-32726-0_4)
- Temporal and linguistic enrichment for abstractive text summarization using transformer models：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s44163-026-01710-5](http://link.springer.com/openurl/pdf?id=doi:10.1007/s44163-026-01710-5)
- A line graph-based metric learning framework for robust link prediction in complex networks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-026-08645-9](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-026-08645-9)
- Collaborative APT detection through cloud-edge synergy of graph transformer and lightweight clustering：[https://www.biomedcentral.com/openurl/pdf?id=doi:10.1186/s13677-026-00940-3](https://www.biomedcentral.com/openurl/pdf?id=doi:10.1186/s13677-026-00940-3)
- Networked data science: a unified network modeling framework：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s10115-026-02784-4](http://link.springer.com/openurl/pdf?id=doi:10.1007/s10115-026-02784-4)
- BotEvo: LLM-Driven social bot detection via behavioral evolution modeling and cross-modal fusion：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s44443-026-00814-3](http://link.springer.com/openurl/pdf?id=doi:10.1007/s44443-026-00814-3)
- Scalability and performance in distributed graph databases：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10586-026-06406-0](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10586-026-06406-0)
- HGP-IC: graph neural networks via hotness-based partitioning and information compensation：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-025-07880-w](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-025-07880-w)
- Assessing the complexity of a path search optimization method based on clustering for a transport graph：[https://www.biomedcentral.com/openurl/pdf?id=doi:10.1140/epjds/s13688-025-00542-0](https://www.biomedcentral.com/openurl/pdf?id=doi:10.1140/epjds/s13688-025-00542-0)
- SCG-tree: shortcut enhanced graph hierarchy tree for efficient spatial queries on massive road networks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11704-024-40459-x](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11704-024-40459-x)
- Continuous-time dynamic graph learning based on spatio-temporal random walks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-024-06881-5](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-024-06881-5)
- Distributed Temporal Graph Neural Network Learning over Large-Scale Dynamic Graphs：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-97-5779-4_4](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-97-5779-4_4)
- A graph partitioning-based hybrid feature selection method in microarray datasets：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10115-024-02292-3](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10115-024-02292-3)
- Distributed k-Hop Query Powered by an Asynchronous Framework：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-96-0579-8_22](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-96-0579-8_22)
- Temporal Graph Networks for Deep Learning on Dynamic Graphs：[https://arxiv.org/pdf/2006.10637](https://arxiv.org/pdf/2006.10637)
- Inductive Representation Learning on Temporal Graphs：[https://arxiv.org/pdf/2002.07962](https://arxiv.org/pdf/2002.07962)
- AliGraph: A Comprehensive Graph Neural Network Platform：[https://arxiv.org/pdf/1902.08730](https://arxiv.org/pdf/1902.08730)
- AGL: a Scalable System for Industrial-purpose Graph Machine Learning：[https://arxiv.org/pdf/2003.02454](https://arxiv.org/pdf/2003.02454)
- GraphSAINT: Graph Sampling Based Inductive Learning Method：[https://arxiv.org/pdf/1907.04931](https://arxiv.org/pdf/1907.04931)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
