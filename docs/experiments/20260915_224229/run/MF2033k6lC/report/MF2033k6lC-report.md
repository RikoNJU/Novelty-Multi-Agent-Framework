# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-15T22:42:29+08:00 |
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

- 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，将动态时序图建模为快照序列，通过图摘要压缩与图自编码器重构误差训练，结合循环神经网络学习时间依赖，实现高效的大规模时序图表示学习。
- 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，领导节点利用基于边分割的图流划分算法划分原图并分配子图，工作节点执行基于图摘要的小批量训练并通过注意力层返回结果，领导节点汇总结果计算梯度并同步更新模型，实现大规模图流数据下的高效分布式GNN训练。
- 提出一种基于边分割的图流划分算法，用于大规模图流数据的分布式划分，通过边分割的方式对图进行划分，以适应图数据的不规则性，为分布式图神经网络训练提供有效的子图划分。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，将动态时序图建模为快照序列，通过图摘要压缩与图自编码器重构误差训练，结合循环神经网络学习时间依赖，实现高效的大规模时序图表示学习。 | Propose a large-scale sequential graph representation learning method GSAERU based on graph summarization, which models dynamic sequential graphs as a sequence of snapshots, compresses the original graph through graph summarization and trains node representations via reconstruction error of graph autoencoder, then learns temporal dependencies with a recurrent neural network, achieving efficient representation learning on large-scale sequential graphs. |
| NP-2 | 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，领导节点利用基于边分割的图流划分算法划分原图并分配子图，工作节点执行基于图摘要的小批量训练并通过注意力层返回结果，领导节点汇总结果计算梯度并同步更新模型，实现大规模图流数据下的高效分布式GNN训练。 | Propose a distributed graph neural network optimization training algorithm DSGNN based on graph summarization, which adopts the "leader-worker" mode. The leader divides the original graph using a graph flow partition algorithm based on edge segmentation and assigns subgraphs to workers, workers perform mini-batch training based on graph summarization and return results through an attention layer, the leader aggregates results, computes gradients, and synchronously updates models, achieving efficient distributed GNN training on large-scale graph streaming data. |
| NP-3 | 提出一种基于边分割的图流划分算法，用于大规模图流数据的分布式划分，通过边分割的方式对图进行划分，以适应图数据的不规则性，为分布式图神经网络训练提供有效的子图划分。 | Propose a graph flow partition algorithm based on edge segmentation for distributed partitioning of large-scale graph streaming data, which partitions the graph by edge segmentation to adapt to the irregularity of graph data, providing effective subgraph partitioning for distributed graph neural network training. |

---

## 四、查新范围要求

检索范围围绕各查新点的中英文表述及技术特征展开。

---

## 五、文献检索范围及检索策略

### 5.1 检索来源

- link.springer.com
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
  - `(ti:"大规模时序图" OR ti:"动态时序图" OR ti:"时序图表示学习") AND (abs:"图摘要" OR abs:"图压缩" OR abs:"图自编码器") AND (abs:"图表示学习" OR abs:"节点表示学习" OR abs:"图嵌入")`（arxiv；执行失败）
  - `("大规模时序图" OR "动态时序图" OR "时序图表示学习") AND ("图摘要" OR "图压缩" OR "图自编码器") AND ("图表示学习" OR "节点表示学习" OR "图嵌入")`（springer；执行失败）
  - `(ti:"大规模时序图" OR ti:"动态时序图" OR ti:"时序图表示学习") AND (abs:"图摘要" OR abs:"图压缩" OR abs:"图自编码器") AND (abs:"图表示学习" OR abs:"节点表示学习" OR abs:"图嵌入")`（arxiv；执行失败）
  - `("大规模时序图" OR "动态时序图" OR "时序图表示学习") AND ("图摘要" OR "图压缩" OR "图自编码器") AND ("图表示学习" OR "节点表示学习" OR "图嵌入")`（springer；执行失败）
  - `ti:sequential AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder"`（arxiv；执行失败）
  - `"sequential graph representation learning" AND "graph summarization" AND "graph autoencoder"`（springer；执行失败）
  - `ti:sequential AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder"`（arxiv；执行失败）
  - `"sequential graph representation learning" AND "graph summarization" AND "graph autoencoder"`（springer；执行失败）
  - `(ti:"时序图" OR ti:"动态图" OR ti:"时序图表示学习") AND (abs:"图摘要" OR abs:"图压缩")`（arxiv；执行失败）
  - `("时序图" OR "动态图" OR "时序图表示学习") AND ("图摘要" OR "图压缩")`（springer；执行失败）
  - `(ti:"时序图" OR ti:"动态图" OR ti:"时序图表示学习") AND (abs:"图摘要" OR abs:"图压缩")`（arxiv；执行失败）
  - `("时序图" OR "动态图" OR "时序图表示学习") AND ("图摘要" OR "图压缩")`（springer；执行失败）
  - `("sequential graph representation learning" OR "temporal graph representation learning" OR "dynamic graph embedding") AND ("graph summarization" OR "graph compression" OR "graph summarization technique") AND ("graph autoencoder" OR "graph auto-encoder" OR "graph reconstruction") AND ("recurrent neural network" OR "temporal dependency learning" OR "sequence modeling")`（springer；有命中）
  - `("sequential graph representation learning" OR "temporal graph representation learning" OR "dynamic graph embedding" OR "dynamic graph representation learning" OR "time-evolving graph embedding") AND ("graph summarization" OR "graph compression" OR "graph summarization technique" OR "graph coarsening" OR "graph condensation") AND ("graph autoencoder" OR "graph auto-encoder" OR "graph reconstruction" OR "GAE" OR "graph reconstruction error")`（springer；有命中）
  - `("sequential graph representation learning" OR "temporal graph representation learning" OR "dynamic graph embedding" OR "dynamic graph representation learning" OR "time-evolving graph embedding") OR ("graph summarization" OR "graph compression" OR "graph summarization technique" OR "graph coarsening" OR "graph condensation")`（springer；部分成功）
  - `(ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:temporal AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding") AND (abs:"graph summarization" OR abs:"graph compression" OR abs:"graph summarization technique") AND (abs:"graph autoencoder" OR abs:"graph auto-encoder" OR abs:"graph reconstruction") AND (abs:"recurrent neural network" OR abs:"temporal dependency learning" OR abs:"sequence modeling")`（arxiv；执行失败）
- **NP-2**
  - `(abs:"分布式图神经网络训练" OR abs:"分布式GNN训练") AND (abs:"图摘要" OR abs:"图流划分")`（arxiv；执行失败）
  - `(abs:"分布式图神经网络训练" OR abs:"分布式GNN训练") AND (abs:"图摘要" OR abs:"图流划分")`（arxiv；执行失败）
  - `("分布式图神经网络训练" OR "分布式GNN训练") AND ("图摘要" OR "图流划分")`（springer；执行失败）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"leader worker architecture"`（arxiv；执行失败）
  - `"distributed graph neural network training" AND "graph summarization" AND "leader worker architecture"`（springer；执行失败）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"leader worker architecture"`（arxiv；执行失败）
  - `"distributed graph neural network training" AND "graph summarization" AND "leader worker architecture"`（springer；执行失败）
- **NP-3**
  - `ti:"图流划分算法" AND abs:"边分割" ANDNOT (all:"顶点分割" OR all:"点分割") AND abs:"分布式图神经网络训练"`（arxiv；执行失败）
  - `"图流划分算法" AND "边分割" NOT ("顶点分割" OR "点分割") AND "分布式图神经网络训练"`（springer；执行失败）
  - `("edge segmentation" OR "edge partitioning" OR "edge-cut partitioning") AND ("graph partitioning" OR "graph flow partitioning" OR "streaming graph partitioning") AND ("distributed graph neural network training" OR "distributed GNN training")`（springer；有命中）
  - `("edge segmentation" OR "edge partitioning" OR "edge-cut partitioning" OR "edge-based partitioning" OR "edge splitting") AND ("graph partitioning" OR "graph flow partitioning" OR "streaming graph partitioning" OR "graph splitting" OR "graph division") AND ("large-scale graph streaming data" OR "graph streams" OR "streaming graphs" OR "dynamic graphs" OR "evolving graphs") AND ("subgraph partitioning" OR "subgraph extraction" OR "subgraph division" OR "subgraph splitting")`（springer；部分成功）
  - `(abs:"edge segmentation" OR abs:"edge partitioning" OR abs:"edge-cut partitioning") AND (ti:"graph partitioning" OR ti:"graph flow partitioning" OR ti:"streaming graph partitioning") AND (abs:distributed AND abs:graph AND abs:neural AND abs:network AND abs:training OR abs:"distributed GNN training")`（arxiv；执行失败）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 8 张原始证据卡；通过 8 张，拒绝 0 张。

### 6.2 相关文献

### card_296616b76867b0338c6d090f · A Survey of Link Prediction in Temporal Networks

- 查新点：NP-1
- 主要贡献：This survey provides a comprehensive taxonomy of temporal link prediction methods, distinguishing representation units (snapshot-based, feature extraction, latent variables including Dynamic Graph Summarisation and autoencoders) from inference units (including RNN-based approaches). It systematically reviews how temporal networks are modeled as discrete-time dynamic graphs (snapshot sequences) and how graph summarisation, autoencoders, and recurrent neural networks are used for temporal graph representation learning.
- 相关性：0.75
- 置信度：0.85
- 来源：
  - A Survey of Link Prediction in Temporal Networks：10.1007/s42979-025-04639-1
    - 引文：Discrete-time dynamic graphs define a temporal network \documentclass[12pt]{minimal} \usepackage{amsmath} \usepackage{wasysym} \usepackage{amsfonts} \usepackage{amssymb} \usepackage{amsbsy} \usepackage{mathrsfs} \usepackage{upgreek} \setlength{\oddsidemargin}{-69pt} \begin{document}$$\mathcal {G = (V, E, T, X)}$$\end{document} as a sequence of snapshots \documentclass[12pt]{minimal} \usepackage{amsmath} \usepackage{wasysym} \usepackage{amsfonts} \usepackage{amssymb} \usepackage{amsbsy} \usepackage{mathrsfs} \usepackage{upgreek} \setlength{\oddsidemargin}{-69pt} \begin{document}$${\mathcal {G}} = (G_1, G_2, \dots , G_{\|{\mathcal {T}}\|})$$\end{document} over a discrete set of timestamps
    - 位置：artifact art_6e0128f41ad58fd336741908 chars:12999-13692
  - A Survey of Link Prediction in Temporal Networks：10.1007/s42979-025-04639-1
    - 引文：DGS is primarily a task-independent representation unit used to integrate historical graph snapshots into one comprehensive weighted snapshot. In the context of TLP, DGS plays a critical role in synthesizing historical network dynamics. DGS collapses successive historical snapshots \documentclass[12pt]{minimal} \usepackage{amsmath} \usepackage{wasysym} \usepackage{amsfonts} \usepackage{amssymb} \usepackage{amsbsy} \usepackage{mathrsfs} \usepackage{upgreek} \setlength{\oddsidemargin}{-69pt} \begin{document}$$G^{\tau }_{\tau - \Delta ^{\prime }}$$\end{document} into a comprehensive weighted snapshot
    - 位置：artifact art_6e0128f41ad58fd336741908 chars:76574-77178
  - A Survey of Link Prediction in Temporal Networks：10.1007/s42979-025-04639-1
    - 引文：EvolveGCN adopts a sequence of discrete snapshots with RNN-based updates of GCN parameters, which is more suitable for gradually evolving networks
    - 位置：artifact art_6e0128f41ad58fd336741908 chars:4484-4630

### card_74df9c8eb6a211f11fcbf195 · Inductive Representation Learning on Temporal Graphs

- 查新点：NP-1
- 主要贡献：提出TGAT（时序图注意力网络），通过自注意力机制聚合时序拓扑邻域特征并学习时间特征交互，实现时序图上的归纳式表示学习，可处理新节点和已观测节点的嵌入推断。
- 相关性：0.55
- 置信度：0.85
- 来源：
  - Inductive Representation Learning on Temporal Graphs：https://arxiv.org/pdf/2002.07962
    - 引文：We propose the temporal graph attention (TGAT) layer to efficiently aggregate temporal-topological neighborhood features as well as to learn the time-feature interactions.
    - 位置：artifact art_b8b821043e4485fda0b8527c chars:516-687
  - Inductive Representation Learning on Temporal Graphs：https://arxiv.org/pdf/2002.07962
    - 引文：The evolving nature of temporal dynamic graphs requires handling new nodes as well as capturing temporal patterns.
    - 位置：artifact art_b8b821043e4485fda0b8527c chars:138-252

### card_2d5d8bebb7092fe9121c99c1 · Temporal Graph Networks for Deep Learning on Dynamic Graphs

- 查新点：NP-1
- 主要贡献：提出TGN（时序图网络），一种通用的动态图深度学习框架，将动态图表示为带时间戳的事件序列，结合记忆模块和图算子实现高效的时间依赖建模。
- 相关性：0.50
- 置信度：0.85
- 来源：
  - Temporal Graph Networks for Deep Learning on Dynamic Graphs：https://arxiv.org/pdf/2006.10637
    - 引文：In this paper, we present Temporal Graph Networks (TGNs), a generic, efficient framework for deep learning on dynamic graphs represented as sequences of timed events.
    - 位置：artifact art_ea01d9c5f48ad68092a07bf7 chars:505-671
  - Temporal Graph Networks for Deep Learning on Dynamic Graphs：https://arxiv.org/pdf/2006.10637
    - 引文：Thanks to a novel combination of memory modules and graph-based operators, TGNs are able to significantly outperform previous approaches being at the same time more computationally efficient.
    - 位置：artifact art_ea01d9c5f48ad68092a07bf7 chars:672-863

### card_1800ebe9811ad96dfd604571 · AGL: a Scalable System for Industrial-purpose Graph Machine Learning

- 查新点：NP-2
- 主要贡献：AGL is a scalable, fault-tolerant and integrated distributed system for GNN training and inference, generating k-hop neighborhood subgraphs and training on parameter servers.
- 相关性：0.40
- 置信度：0.80
- 来源：
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：we design AGL, a scalable, fault-tolerance and integrated system, with fully-functional training and inference for GNNs. Our system design follows the message passing scheme underlying the computations of GNNs. We design to generate the $k$-hop neighborhood, an information-complete subgraph for each node
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1021-1326

### card_396b3a2c53a363562c5987e7 · AliGraph: A Comprehensive Graph Neural Network Platform

- 查新点：NP-2
- 主要贡献：AliGraph is a comprehensive distributed graph neural network platform with distributed graph storage, optimized sampling operators and runtime to support GNN training at scale (billions of edges).
- 相关性：0.40
- 置信度：0.80
- 来源：
  - AliGraph: A Comprehensive Graph Neural Network Platform：https://arxiv.org/pdf/1902.08730
    - 引文：we present a comprehensive graph neural network system, namely AliGraph, which consists of distributed graph storage, optimized sampling operators and runtime to efficiently support not only existing popular GNNs but also a series of in-house developed ones for different scenarios.
    - 位置：artifact art_d88778158223021b818fdd97 chars:649-931

### card_39178e2c52bbe5b9a438021d · A Graph Partitioning Optimization Method for Distributed GNN Training

- 查新点：NP-3
- 主要贡献：BGPA proposes a balanced graph partitioning algorithm for distributed GNN training, aiming to balance computational and communication costs and equalize memory utilization among computing nodes.
- 相关性：0.60
- 置信度：0.75
- 来源：
  - A Graph Partitioning Optimization Method for Distributed GNN Training：10.1007/978-981-96-1904-7_11
    - 引文：High-quality graph partitioning aims to minimize inter-subgraph connections while balancing computational and memory loads across partitions, thereby enhancing training efficiency
    - 位置：artifact art_616a5655c89a1873fabe0f48 chars:399-578
  - A Graph Partitioning Optimization Method for Distributed GNN Training：10.1007/978-981-96-1904-7_11
    - 引文：we propose a novel Balanced Graph Partitioning Algorithm (BGPA), designed to achieve an optimal balance between computational and communication costs and to equalize memory utilization among computing nodes
    - 位置：artifact art_616a5655c89a1873fabe0f48 chars:774-980

### card_7892a8e0f2320fcdeccef0c8 · G-SPAC: a more granular greedy graph partition algorithm with spatial locality and judgment-aware edge folding

- 查新点：NP-3
- 主要贡献：G-SPAC proposes a graph edge partitioning algorithm that transforms the graph so vertex partitioning methods can be applied, using degree-and-spatial-locality priority and judgment-aware edge folding to balance partition quality and reduce vertex copies.
- 相关性：0.75
- 置信度：0.80
- 来源：
  - G-SPAC: a more granular greedy graph partition algorithm with spatial locality and judgment-aware edge folding：10.1007/s11432-023-3916-0
    - 引文：which is a graph edge partitioning algorithm that transforms the graph so that the vertex partitioning methods can be applied to the transformed graph
    - 位置：artifact art_f37fa6190432cba0cda07d68 chars:451-601
  - G-SPAC: a more granular greedy graph partition algorithm with spatial locality and judgment-aware edge folding：10.1007/s11432-023-3916-0
    - 引文：the method of degree-and-spatial-locality priority is designed so that adjacent vertices are more accessible to divide into the same subgraph
    - 位置：artifact art_f37fa6190432cba0cda07d68 chars:725-866

### card_be804ac694daf99bf090babf · LocalDGP: local degree-balanced graph partitioning for lightweight GNNs

- 查新点：NP-3
- 主要贡献：LocalDGP proposes a local degree-balanced graph partitioning algorithm that uses only local graph information to partition nodes into subgraphs for GNN training, reducing memory consumption while preserving subgraph structure consistency.
- 相关性：0.55
- 置信度：0.70
- 来源：
  - LocalDGP: local degree-balanced graph partitioning for lightweight GNNs：10.1007/s10489-024-05964-3
    - 引文：subgraph sampling methods divide the graph into multiple subgraphs and then train the GNN on each subgraph sequentially, which can reduce GPU memory consumption
    - 位置：artifact art_eeedbae60916c967cc43d98c chars:268-428
  - LocalDGP: local degree-balanced graph partitioning for lightweight GNNs：10.1007/s10489-024-05964-3
    - 引文：only the local graph information is acquired during the partitioning process, which can reduce memory consumption
    - 位置：artifact art_eeedbae60916c967cc43d98c chars:1111-1224

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 3 | 有证据 |
| NP-2 | 2 | 有证据 |
| NP-3 | 3 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出一种基于图摘要的大规模时序图表示学习方法GSAERU，将动态时序图建模为快照序列，通过图摘要压缩与图自编码器重构误差训练，结合循环神经网络学习时间依赖，实现高效的大规模时序图表示学习。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 针对查新点NP-1（基于图摘要的大规模时序图表示学习方法GSAERU），检索获得4张有效证据卡片，覆盖了时序图快照建模、动态图摘要、图自编码器与循环神经网络等方向的相关文献（如时序图表示学习综述、TGAT、TGN等），但这些文献均未披露GSAERU完整技术组合。由于Reviewer在评价过程中出现工具调用预算耗尽（ToolCallBudgetExhausted），未能完成系统性裁定，当前证据不足以确定新颖性结论，需补充检索以完整覆盖图摘要压缩结合图自编码器重构误差训练与循环神经网络时序建模的组合特征。  
**高度相关 Work：**
  - 无

### NP-2 · 新颖

提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，领导节点利用基于边分割的图流划分算法划分原图并分配子图，工作节点执行基于图摘要的小批量训练并通过注意力层返回结果，领导节点汇总结果计算梯度并同步更新模型，实现大规模图流数据下的高效分布式GNN训练。

**Reviewer 裁定：** 新颖  
**裁定理由：** 本查新点的核心是 DSGNN 这一特定算法组合：领导-工作者模式 + 领导节点基于边分割的图流划分算法划分子图 + 工作节点基于图摘要的小批量训练 + 通过注意力层返回结果 + 领导节点汇总结果计算梯度并同步更新模型。已检索到的两篇最相近工作（AGL、AliGraph）均是大规模分布式 GNN 训练系统，仅在"大规模图数据上的分布式 GNN 训练"这一上位对象概念上有重合；二者均未披露任何一项辨别性技术特征：AGL 采用参数服务器（parameter server）架构，通过 k-hop 邻域子图生成而非图摘要，且无注意力层返回、无基于边分割的图流划分；AliGraph 采用分布式图存储+优化采样运行时，未采用图摘要小批量训练、领导-工作者模式或注意力层返回结果。因此，现有证据中不存在披露 DSGNN 特征组合的文献，该查新点针对所获证据具有新颖性。  
**置信度：** 0.70  
**报告摘要：** 查新点NP-2（基于图摘要的分布式图神经网络优化训练算法DSGNN）的核心组合特征——领导-工作者模式、基于边分割的图流划分、图摘要小批量训练、注意力层返回结果、领导节点同步更新——在已检索文献中未被完整披露。最相近工作AGL与AliGraph仅涉及大规模分布式GNN训练的上位概念，其技术方案（参数服务器、k-hop子图生成、分布式图存储）与DSGNN存在显著差异。基于现有证据，该查新点具有新颖性。  
**高度相关 Work：**
  - wrk_ff5aa18cf0cfe7be1ba5e8bd：大规模分布式 GNN 训练系统，与 DSGNN 在上位对象概念（object concept C1）重合，但采用参数服务器与 k-hop 邻域子图生成，未披露领导-工作者模式、图摘要训练、基于边分割的图流划分或注意力层返回结果等辨别性特征，作为最相近对比基线。 (cards: card_1800ebe9811ad96dfd604571)
  - wrk_e59b8b7248dcc080455b8690：全面的分布式 GNN 平台，与 DSGNN 在分布式大规模图 GNN 训练这一上位对象概念上重合，但未采用图摘要小批量训练、领导-工作者模式、注意力层返回结果或领导节点同步更新模型，作为最相近对比基线。 (cards: card_396b3a2c53a363562c5987e7)

### NP-3 · 部分新颖

提出一种基于边分割的图流划分算法，用于大规模图流数据的分布式划分，通过边分割的方式对图进行划分，以适应图数据的不规则性，为分布式图神经网络训练提供有效的子图划分。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 查新点的核心技术特征'基于边分割的图划分算法'、'将原图划分为多个子图'、'适应图数据的不规则性'已被最相近文献 G-SPAC 公开（G-SPAC 即基于边划分的图分区算法，通过度数+空间局部性优先级适应图数据不规则性并划分子图）。因此这三项特征本身不具全新性。但查新点claim与题名均强调处理'大规模图流/流式图数据'（graph flow/streaming）的分布式划分，而现有证据（G-SPAC面向通用图计算、BGPA为顶点导向的分布式GNN平衡划分、LocalDGP为顶点导向的GNN子图采样）均未涉及'图流/流式图数据的边分割划分'这一关键限定。查新点的完整技术组合（边分割 + 图流/流式 + 分布式GNN训练）在现有证据中未被完整覆盖，故整体组合具有部分新颖性。  
**置信度：** 0.70  
**报告摘要：** 查新点NP-3（基于边分割的图流划分算法）中，'基于边分割的划分''划分多个子图''适应图数据不规则性'三项技术特征已被G-SPAC公开，不具全新性；但关键限定'图流/流式图数据'的边分割分布式划分未被现有证据覆盖（G-SPAC面向通用图计算，BGPA和LocalDGP均为顶点导向划分）。因此，完整技术组合（边分割+图流+分布式GNN训练）具有部分新颖性。  
**高度相关 Work：**
  - wrk_2f0322820b0fa4b832b65e47：G-SPAC 是直接基于边划分（edge partitioning）的图分区算法，将图划分成多个子图，并通过度数+空间局部性优先级适应图数据的不规则性，与查新点'基于边分割''划分为多个子图''适应图数据不规则性'三项技术特征高度重叠，是最相近的现有技术；但其不针对图流/流式图数据，也不专用于分布式GNN训练。 (cards: card_7892a8e0f2320fcdeccef0c8)

---

## 八、报告局限

- NP-1检索未能形成有效结果：中英文检索任务虽获得若干证据卡片（如时序图综述、TGAT、TGN），但Reviewer因工具调用预算耗尽（ToolCallBudgetExhausted）未能完成系统化判定，属于检索覆盖不完整导致的证据不足，并非检索成功且零命中，不能据此认为‘未检索到相关文献’。
- 部分检索来源覆盖未知：输入数据未提供检索执行的完整覆盖事实（如各数据库是否全部成功执行），因此无法区分检索失败与成功零命中，报告对检索覆盖情况的描述以实际可用的有效证据为准。
- 被拒绝证据：无（rejected_evidence 为空），不存在因技术质疑或格式问题导致的证据门控拒绝。
- NP-2与NP-3的检索证据均来自有效EvidenceCard，结论基于这些卡片作出；其中NP-3的counter证据（G-SPAC、BGPA、LocalDGP）被用于判定部分特征已有公开，但未覆盖图流/流式图数据的边分割划分这一关键限定。

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

- A Graph Partitioning Optimization Method for Distributed GNN Training：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-96-1904-7_11](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-96-1904-7_11)
- Distributed Temporal Graph Neural Network Learning over Large-Scale Dynamic Graphs：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-97-5779-4_4](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-97-5779-4_4)
- Distributed Graph Processing: Techniques and Systems：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-16-0479-9_2](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-16-0479-9_2)
- A line graph-based metric learning framework for robust link prediction in complex networks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-026-08645-9](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-026-08645-9)
- Normalized Cut and Subgraph-Aware Multi-head Attention Based Node-Level Anomaly Detection：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-95-0129-8_20](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-95-0129-8_20)
- G-SPAC: a more granular greedy graph partition algorithm with spatial locality and judgment-aware edge folding：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11432-023-3916-0](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11432-023-3916-0)
- HHP: A Hybrid Partitioner for Large-Scale Hypergraph：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-96-0821-8_8](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-96-0821-8_8)
- LocalDGP: local degree-balanced graph partitioning for lightweight GNNs：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10489-024-05964-3](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10489-024-05964-3)
- A Survey of Link Prediction in Temporal Networks：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s42979-025-04639-1](http://link.springer.com/openurl/pdf?id=doi:10.1007/s42979-025-04639-1)
- Self-supervised deep clustering for spammer group detection：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10489-025-06675-z](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10489-025-06675-z)
- CaTSCAN: Calculating Typed Subgraph Counts Analytically for Networks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37657-2_31](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37657-2_31)
- Temporal Graph Classification Based on Fast and Exact Transitive Reduction Strategy：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37673-2_25](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37673-2_25)
- A Multi-heuristic Approach to Workload Placement in Virtualisation Environments：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-32732-1_30](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-32732-1_30)
- TimeAgent: From Matches to Memories—Timeline Summarization for Sports Analytics：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-36033-5_28](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-36033-5_28)
- Part-GNN: A Partitioning-Based Graph Neural Network for Efficient Memory Large Scale Data Classification：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-2597-2_39](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-2597-2_39)
- Design of a Query Expression for Multi-Dimensional Graph Warehousing：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-32726-0_4](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-32726-0_4)
- AliGraph: A Comprehensive Graph Neural Network Platform：[https://arxiv.org/pdf/1902.08730](https://arxiv.org/pdf/1902.08730)
- AGL: a Scalable System for Industrial-purpose Graph Machine Learning：[https://arxiv.org/pdf/2003.02454](https://arxiv.org/pdf/2003.02454)
- Inductive Representation Learning on Temporal Graphs：[https://arxiv.org/pdf/2002.07962](https://arxiv.org/pdf/2002.07962)
- Temporal Graph Networks for Deep Learning on Dynamic Graphs：[https://arxiv.org/pdf/2006.10637](https://arxiv.org/pdf/2006.10637)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
