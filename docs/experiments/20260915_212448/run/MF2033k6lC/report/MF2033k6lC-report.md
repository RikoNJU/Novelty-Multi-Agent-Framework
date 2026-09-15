# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-15T21:24:48+08:00 |
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

- GNN如何分布式?中科院综述《图神经网络分布式训练》：[https://zhuanlan.zhihu.com/p/584132986](https://zhuanlan.zhihu.com/p/584132986)
- 【荐读IEEE TPAMI】图神经网络的并行与分布式执行:深入并发性分析：[https://mp.weixin.qq.com/s?__biz=MzU0NjgzMDIxMQ==&mid=2247618736&idx=3&sn=1ddd2df434b0167f36550d151b740d9e&chksm=fa06eb2abee8069f01302c139f1c8fb406a5f11d0f69400e3b17ec8c94840d3052240af2c30a&scene=27](https://mp.weixin.qq.com/s?__biz=MzU0NjgzMDIxMQ==&mid=2247618736&idx=3&sn=1ddd2df434b0167f36550d151b740d9e&chksm=fa06eb2abee8069f01302c139f1c8fb406a5f11d0f69400e3b17ec8c94840d3052240af2c30a&scene=27)
- 图神经网络,这到底是个什么?：[https://zhuanlan.zhihu.com/p/353692130](https://zhuanlan.zhihu.com/p/353692130)
- 图神经网络GNN综述:《Graph Neural Networks: A Review of Methods and Applications》：[https://zhuanlan.zhihu.com/p/616305627](https://zhuanlan.zhihu.com/p/616305627)
- 关于图神经网络(Graph Neural Networks,GNN)基础知识汇总1.0：[https://cloud.tencent.com/developer/article/2334518](https://cloud.tencent.com/developer/article/2334518)
- 【2021届】计算机科学方向毕业设计(论文)阶段性汇报：[https://zhiyuan.sjtu.edu.cn/html/zhiyuan/announcement_view.php?id=3943](https://zhiyuan.sjtu.edu.cn/html/zhiyuan/announcement_view.php?id=3943)
- 一文带你了解图神经网络：[https://www.cnblogs.com/huaweiyun/p/13169055.html](https://www.cnblogs.com/huaweiyun/p/13169055.html)
- 大模型学习路线图:小白也能轻松入门并收藏这份系统知识体系!：[https://zhuanlan.zhihu.com/p/2031025273404139366](https://zhuanlan.zhihu.com/p/2031025273404139366)
- 探索图神经网络的网络架构和训练方法：[https://www.cnblogs.com/huaweiyun/p/14455228.html](https://www.cnblogs.com/huaweiyun/p/14455228.html)
- 图神经网络实战(三)：[https://blog.csdn.net/wizardforcel/article/details/151660781](https://blog.csdn.net/wizardforcel/article/details/151660781)
- Temporal Graph Classification Based on Fast and Exact Transitive Reduction Strategy：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37673-2_25](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37673-2_25)
- Part-GNN: A Partitioning-Based Graph Neural Network for Efficient Memory Large Scale Data Classification：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-2597-2_39](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-2597-2_39)
- Design of a Query Expression for Multi-Dimensional Graph Warehousing：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-32726-0_4](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-32726-0_4)
- Temporal and linguistic enrichment for abstractive text summarization using transformer models：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s44163-026-01710-5](http://link.springer.com/openurl/pdf?id=doi:10.1007/s44163-026-01710-5)
- A line graph-based metric learning framework for robust link prediction in complex networks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-026-08645-9](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-026-08645-9)
- Collaborative APT detection through cloud-edge synergy of graph transformer and lightweight clustering：[https://www.biomedcentral.com/openurl/pdf?id=doi:10.1186/s13677-026-00940-3](https://www.biomedcentral.com/openurl/pdf?id=doi:10.1186/s13677-026-00940-3)
- Networked data science: a unified network modeling framework：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s10115-026-02784-4](http://link.springer.com/openurl/pdf?id=doi:10.1007/s10115-026-02784-4)
- BotEvo: LLM-Driven social bot detection via behavioral evolution modeling and cross-modal fusion：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s44443-026-00814-3](http://link.springer.com/openurl/pdf?id=doi:10.1007/s44443-026-00814-3)
- 图深度学习——卷积神经网络&循环神经网络&自编码器：[https://blog.csdn.net/qq_34539676/article/details/125464137](https://blog.csdn.net/qq_34539676/article/details/125464137)
- 深度学习基础入门篇-序列模型\[11\]:循环神经网络 RNN、长短时记忆网络LSTM、门控循环单元GRU原理和应用详解：[https://developer.aliyun.com/article/1225691](https://developer.aliyun.com/article/1225691)
- 【机器学习-无监督学习】自编码器：[https://cloud.tencent.com/developer/article/2490757](https://cloud.tencent.com/developer/article/2490757)
- 深度学习时代的图模型,清华发文综述图网络：[https://www.163.com/dy/article/E3SMUOM10511AQHO.html](https://www.163.com/dy/article/E3SMUOM10511AQHO.html)
- 【深度学习】 自编码器(AutoEncoder)：[https://zhuanlan.zhihu.com/p/133207206](https://zhuanlan.zhihu.com/p/133207206)
- 图上的深度学习新篇章:图自编码器深度解析：[https://developer.baidu.com/article/details/3325840](https://developer.baidu.com/article/details/3325840)
- 9、深度学习基础与时间序列数据建模解析：[https://blog.csdn.net/g8f9d0s1a2/article/details/152389630](https://blog.csdn.net/g8f9d0s1a2/article/details/152389630)
- 图表示学习经典方法 —— GCN&GAE：[https://zhuanlan.zhihu.com/p/662218765](https://zhuanlan.zhihu.com/p/662218765)
- 自编码器综述论文:概念、图解和应用：[https://zhuanlan.zhihu.com/p/475171509](https://zhuanlan.zhihu.com/p/475171509)
- 自编码器解密:深入了解神经网络的学习过程：[https://blog.csdn.net/universsky2015/article/details/135799509](https://blog.csdn.net/universsky2015/article/details/135799509)
- 图神经网络,强大在哪里?：[https://baijiahao.baidu.com/s?id=1738150068142893396&wfr=spider&for=pc](https://baijiahao.baidu.com/s?id=1738150068142893396&wfr=spider&for=pc)
- 深度学习-TOP 10神经网络(动图讲解)\_神经网络动图-CSDN博客：[https://blog.csdn.net/qq_35054151/article/details/151871089](https://blog.csdn.net/qq_35054151/article/details/151871089)
- 深入理解自编码器 (Autoencoder):从神经网络原理到图像压缩与异常检测实战\_自动编码(autoencoder)器异常检测(outlier detection)实战-CSDN博客：[https://blog.csdn.net/SUEJESDA/article/details/158691148](https://blog.csdn.net/SUEJESDA/article/details/158691148)
- 可视化解释11种基本神经网络架构：[https://www.163.com/dy/article/H0CF3HEU051193U6.html](https://www.163.com/dy/article/H0CF3HEU051193U6.html)
- 【译】图上的深度学习综述 五、图自编码器：[https://cloud.tencent.com/developer/article/1994792](https://cloud.tencent.com/developer/article/1994792)
- Graph Neural Network(GNN)图神经网络：[https://zhuanlan.zhihu.com/p/610036768](https://zhuanlan.zhihu.com/p/610036768)
- 【阅读】Distributed Graph Neural Network Training: A Survey——翻译：[https://cloud.tencent.com/developer/article/2230138](https://cloud.tencent.com/developer/article/2230138)
- GNN如何分布式?中科院综述《图神经网络分布式训练》：[https://cloud.tencent.com/developer/article/2226265](https://cloud.tencent.com/developer/article/2226265)
- Graph Coarsening via Convolution Matching for Scalable Graph Neural Network Training：[https://arxiv.org/pdf/2312.15520](https://arxiv.org/pdf/2312.15520)
- 【阅读】2021 OSDI——P3: Distributed Deep Graph Learning at Scale 论文翻译：[https://zhuanlan.zhihu.com/p/583757684](https://zhuanlan.zhihu.com/p/583757684)
- 论文笔记:ICLR'22 Learn Locally, Correct Globally A Distributed Algorithm for Training GNNs：[https://zhuanlan.zhihu.com/p/536158540](https://zhuanlan.zhihu.com/p/536158540)
- 《DistDGL: Distributed Graph Neural Network Training for Billion-Scale Graphs》论文阅读：[https://zhuanlan.zhihu.com/p/509265666](https://zhuanlan.zhihu.com/p/509265666)
- AutoDL教程:分布式gnn训练及数据集整理：[https://blog.csdn.net/penzidaxian/article/details/132550751](https://blog.csdn.net/penzidaxian/article/details/132550751)
- 浅谈LLM之分布式训练：[https://bbs.huaweicloud.com/blogs/435338](https://bbs.huaweicloud.com/blogs/435338)
- 论文阅读:P3: Distributed Deep Graph Learning at Scale \[OSDI21\]：[https://zhuanlan.zhihu.com/p/406589553](https://zhuanlan.zhihu.com/p/406589553)
- \[ICLR 2024\] VQGraph: 重新审视图表示学习,将Graph空间Token化：[https://hub.baai.ac.cn/view/36109](https://hub.baai.ac.cn/view/36109)
- 图流划分算法综述：[https://zhuanlan.zhihu.com/p/152221150](https://zhuanlan.zhihu.com/p/152221150)
- 图解六种负载均衡算法:从原理到实践的全面解析：[https://cloud.baidu.com/article/3709681](https://cloud.baidu.com/article/3709681)
- 十张图解析负载均衡:从原理到实践的全流程指南：[https://cloud.baidu.com/article/3835671](https://cloud.baidu.com/article/3835671)
- 几张图带你了解负载均衡:原理、架构与实践指南：[https://cloud.baidu.com/article/3836300](https://cloud.baidu.com/article/3836300)
- 揭秘GES超大规模图计算引擎HyG:图切分：[https://zhuanlan.zhihu.com/p/533662210](https://zhuanlan.zhihu.com/p/533662210)
- 几张图看懂负载均衡:架构、算法与实战指南：[https://cloud.baidu.com/article/3835817](https://cloud.baidu.com/article/3835817)
- 动态图划分复制算法:Leopard：[https://zhuanlan.zhihu.com/p/324383730](https://zhuanlan.zhihu.com/p/324383730)
- 几张图带你了解负载均衡:从原理到实践的全面解析：[https://cloud.baidu.com/article/3835803](https://cloud.baidu.com/article/3835803)
- 几张图带你全面解析负载均衡:从原理到实践：[https://cloud.baidu.com/article/3910166](https://cloud.baidu.com/article/3910166)
- 几张图带你了解负载均衡:从原理到实践的全解析：[https://cloud.baidu.com/article/3835750](https://cloud.baidu.com/article/3835750)
- 图变分编码器：[https://blog.csdn.net/my_lamado/article/details/143814097](https://blog.csdn.net/my_lamado/article/details/143814097)
- 项目实战 | 当Graphs与建筑(Architecture)相遇:探索图神经网络在 3D 建筑设计中的应用 - 智源社区：[https://hub.baai.ac.cn/view/49464](https://hub.baai.ac.cn/view/49464)
- 深度解析:图变分自编码器与图对抗生成网络的奥秘：[https://developer.baidu.com/article/details/3325698](https://developer.baidu.com/article/details/3325698)
- ​WSDM 2023 | S2GAE: 简单而有效的自监督图自动编码器框架：[https://m.sohu.com/sa/653023487_121119001](https://m.sohu.com/sa/653023487_121119001)
- PyG应用: 教程(六) 图自编码器与变分图自编码器：[https://zhuanlan.zhihu.com/p/485054342](https://zhuanlan.zhihu.com/p/485054342)
- GAE (graph autoencoder)：[https://zhuanlan.zhihu.com/p/696005030](https://zhuanlan.zhihu.com/p/696005030)
- GraphMAE:将MAE的方法应用到图中使图的生成式自监督学习超越了对比学习：[https://cloud.tencent.com/developer/article/2160113](https://cloud.tencent.com/developer/article/2160113)
- 图自编码器GAEpytorch代码：[https://blog.51cto.com/u_16213700/14045777](https://blog.51cto.com/u_16213700/14045777)
- Where to Mask: Structure-Guided Masking for Graph Masked Autoencoders---论文总结：[https://blog.csdn.net/m0_64920871/article/details/155054214](https://blog.csdn.net/m0_64920871/article/details/155054214)
- 图分割Graph Partitioning技术总结：[https://zhuanlan.zhihu.com/p/446152634](https://zhuanlan.zhihu.com/p/446152634)
- 【论文阅读(综述)】(超)图分区的更近期的发展 - More Recent Advances in (Hyper)Graph Partitioning：[https://zhuanlan.zhihu.com/p/654840232](https://zhuanlan.zhihu.com/p/654840232)
- 论文导读 | 分布式图模拟：[https://blog.csdn.net/weixin_48167662/article/details/125739519](https://blog.csdn.net/weixin_48167662/article/details/125739519)
- 应用图深度学习(一)：[https://blog.csdn.net/wizardforcel/article/details/149246217](https://blog.csdn.net/wizardforcel/article/details/149246217)
- 论文分享与解析|逼近极限:单遍流式算法中最大有向割的1/2近似比突破：[https://blog.csdn.net/AladdinEdu/article/details/156895904](https://blog.csdn.net/AladdinEdu/article/details/156895904)
- https://new.qq.com/rain/a/20231101A051WY00：[https://new.qq.com/rain/a/20231101A051WY00](https://new.qq.com/rain/a/20231101A051WY00)
- 大规模场景分块建图论文笔记：[https://blog.csdn.net/qq_45372239/article/details/143467704](https://blog.csdn.net/qq_45372239/article/details/143467704)
- A Workload‑Adaptive Streaming Partitioner for Distributed Graph Stores(2021)：[https://blog.csdn.net/weixin_43856668/article/details/136784744](https://blog.csdn.net/weixin_43856668/article/details/136784744)
- 机器学习实战:GNN(图神经网络)加速器的FPGA解决方案：[https://www.pcachina.com/article/3000123638](https://www.pcachina.com/article/3000123638)
- 项目实战 | 绘制未来:GNN 如何解锁城市韧性(Urban Resilience)：[https://hub.baai.ac.cn/view/44486](https://hub.baai.ac.cn/view/44486)
- WWW'23:更少的内存,更快的速度,更高的准确度——GNN大图训练暨工具包发布：[https://mp.weixin.qq.com/s?__biz=MzA5OTQ5MDE0Mw==&mid=2651136483&idx=1&sn=4e78e2048235e9111aa301357e244dc9&chksm=8a0d61b63cd8fea329a9d7243a93a9cdb5931cd885c78ef62a91817772f0a9f3fc6cd319ed00&scene=27](https://mp.weixin.qq.com/s?__biz=MzA5OTQ5MDE0Mw==&mid=2651136483&idx=1&sn=4e78e2048235e9111aa301357e244dc9&chksm=8a0d61b63cd8fea329a9d7243a93a9cdb5931cd885c78ef62a91817772f0a9f3fc6cd319ed00&scene=27)
- 中国科大提出新型核外大规模图神经网络训练系统：[https://news.ustc.edu.cn/info/1055/90608.htm](https://news.ustc.edu.cn/info/1055/90608.htm)
- Hybrid Transformer-GNN Model for Multi-Document Summarization：[http://ieeexplore.ieee.org/document/11294438/](http://ieeexplore.ieee.org/document/11294438/)
- 图神经网络研究综述(GNN),非常详细收藏我这一篇就够了!：[https://blog.csdn.net/2401_84495872/article/details/143767861](https://blog.csdn.net/2401_84495872/article/details/143767861)
- DNN in GPU/CPU Clusters：[https://blog.csdn.net/zj_18706809267/article/details/127652263](https://blog.csdn.net/zj_18706809267/article/details/127652263)
- Network Representation Learning：[https://www.sciencedirect.com/topics/computer-science/network-representation-learning](https://www.sciencedirect.com/topics/computer-science/network-representation-learning)
- 论文阅读 Dynamic Graph Representation Learning Via Self-Attention Networks - 落悠 - 博客园：[https://www.cnblogs.com/luoyoucode/p/16226886.html](https://www.cnblogs.com/luoyoucode/p/16226886.html)
- Dynamic graph link prediction based on multi⁃view contrastive learning：[https://jns.nju.edu.cn/EN/10.13232/j.cnki.jnju.2024.03.003](https://jns.nju.edu.cn/EN/10.13232/j.cnki.jnju.2024.03.003)
- Graph Robustness：[https://mn.cs.tsinghua.edu.cn/autogl/documentation/docfile/tutorial/t_robust.html](https://mn.cs.tsinghua.edu.cn/autogl/documentation/docfile/tutorial/t_robust.html)
- SIGIR'22 推荐系统论文之图网络篇：[https://cloud.tencent.com/developer/article/2064446](https://cloud.tencent.com/developer/article/2064446)
- 自动编码器在生成式社交网络分析中的作用：[https://blog.csdn.net/universsky2015/article/details/135806495](https://blog.csdn.net/universsky2015/article/details/135806495)
- 论文阅读:Towards Faster Deep Graph Clustering via Efficient Graph Auto-Encoder：[https://blog.csdn.net/dundunmm/article/details/144835209](https://blog.csdn.net/dundunmm/article/details/144835209)
- ICLR 2021 | GSL:通过可控的解耦表征学习模拟人脑想象力：[https://blog.csdn.net/amusi1994/article/details/116036444](https://blog.csdn.net/amusi1994/article/details/116036444)
- Hybrid Edge Partitioner: Partitioning Large Power-Law Graphs under Memory Constraints：[https://arxiv.org/pdf/2103.12594v1](https://arxiv.org/pdf/2103.12594v1)
- A Note on Edge-based Graph Partitioning and its Linear Algebraic Structure：[http://link.springer.com/10.1007/s10852-011-9154-4](http://link.springer.com/10.1007/s10852-011-9154-4)
- Gemini: A Computation-Centric Distributed Graph Processing System：[https://pacman.cs.tsinghua.edu.cn/~cwg/publication/osdi16/osdi16.pdf](https://pacman.cs.tsinghua.edu.cn/~cwg/publication/osdi16/osdi16.pdf)
- 【论文推荐】GNN for Communication Networks最新论文-2025年7月：[https://zhuanlan.zhihu.com/p/1934270506699317552](https://zhuanlan.zhihu.com/p/1934270506699317552)
- 机器学习学术速递\[2022.9.30\]：[https://zhuanlan.zhihu.com/p/569623375](https://zhuanlan.zhihu.com/p/569623375)
- 1Introduction：[https://arxiv.org/html/2402.16442v3](https://arxiv.org/html/2402.16442v3)
- Optimizing Graph-based Approximate Nearest Neighbor Search: Stronger and Smarter：[https://nicsefc.ee.tsinghua.edu.cn/%2Fnics_file%2Fpdf%2Fdacb55cd-fe0a-4b00-9fa0-8f32e3243930.pdf](https://nicsefc.ee.tsinghua.edu.cn/%2Fnics_file%2Fpdf%2Fdacb55cd-fe0a-4b00-9fa0-8f32e3243930.pdf)
- 基本信息：[https://people.ucas.ac.cn/~kejiang](https://people.ucas.ac.cn/~kejiang)
- 2021-2023年部分高质量论文：[https://scs.nuist.edu.cn/2024/0606/c5895a246386/page.htm](https://scs.nuist.edu.cn/2024/0606/c5895a246386/page.htm)
- 论文导读 | 图流的分割和摘要：[https://zhuanlan.zhihu.com/p/666621059](https://zhuanlan.zhihu.com/p/666621059)
- 应用图深度学习-全-：[https://www.cnblogs.com/apachecn/p/18976581](https://www.cnblogs.com/apachecn/p/18976581)
- 路网高效分区实战:从METIS算法到工程优化：[https://blog.csdn.net/weixin_30432579/article/details/95474958](https://blog.csdn.net/weixin_30432579/article/details/95474958)
- ||基于ArcGIS的流域分割：[https://zhuanlan.zhihu.com/p/457729549](https://zhuanlan.zhihu.com/p/457729549)
- 【阅读】Distributed Graph Neural Network Training: A Survey——翻译：[https://article.juejin.cn/post/7235965352202272824](https://article.juejin.cn/post/7235965352202272824)
- 从串行到并行:最小割/最大流算法在计算机视觉中的演进与实战：[https://blog.csdn.net/weixin_31236101/article/details/161330776](https://blog.csdn.net/weixin_31236101/article/details/161330776)
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
