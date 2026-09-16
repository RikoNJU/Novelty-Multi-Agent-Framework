# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T20:10:49+08:00 |
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

- 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，该方法结合图摘要技术和图自编码器，并利用循环神经网络学习时间维度的特征与依赖关系，能够高效生成大规模动态时序图的表征，显著降低内存消耗和训练时间。
- 提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导—工作者”工作模式，通过基于边分割的图流划分算法对原图进行划分，工作节点执行基于图摘要的小批量训练，并通过注意力层将结果汇总至领导节点，实现大规模图流数据上GNN训练的高效加速。
- 在分布式图神经网络训练中，提出了基于边分割的图流划分算法，用于将大规模图数据划分为多个子图并分配给工作者节点，有效解决了图数据不规则性导致的分布式训练难点，提升了训练效率。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，该方法结合图摘要技术和图自编码器，并利用循环神经网络学习时间维度的特征与依赖关系，能够高效生成大规模动态时序图的表征，显著降低内存消耗和训练时间。 | Proposed a large-scale sequential graph representation learning method GSAERU based on graph summarization, which combines graph summarization with graph autoencoder and uses recurrent neural networks to learn temporal features and dependencies, enabling efficient representation generation for large-scale dynamic graphs with significantly reduced memory consumption and training time. |
| NP-2 | 提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导—工作者”工作模式，通过基于边分割的图流划分算法对原图进行划分，工作节点执行基于图摘要的小批量训练，并通过注意力层将结果汇总至领导节点，实现大规模图流数据上GNN训练的高效加速。 | Proposed a distributed graph neural network optimization training algorithm DSGNN based on graph summarization, which adopts a leader-worker mode, partitions the original graph using a graph flow partition algorithm based on edge segmentation, workers perform mini-batch training based on graph summarization, and results are summarized to the leader through an attention layer, enabling efficient acceleration of GNN training on large-scale graph streaming data. |
| NP-3 | 在分布式图神经网络训练中，提出了基于边分割的图流划分算法，用于将大规模图数据划分为多个子图并分配给工作者节点，有效解决了图数据不规则性导致的分布式训练难点，提升了训练效率。 | In distributed graph neural network training, a graph flow partition algorithm based on edge segmentation is proposed to partition large-scale graph data into multiple subgraphs and assign them to worker nodes, effectively addressing the difficulties caused by irregularity of graph data in distributed training and improving training efficiency. |

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
  - `(abs:"graph summarization" OR abs:"graph autoencoder" OR abs:"recurrent neural network") AND (ti:"large-scale dynamic graphs" OR ti:"sequential graphs" OR ti:"temporal graphs")`（arxiv；有命中）
  - `("graph summarization" OR "graph autoencoder" OR "recurrent neural network") AND ("large-scale dynamic graphs" OR "sequential graphs" OR "temporal graphs")`（springer；有命中）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
- **NP-3**
  - `(abs:graph AND abs:flow AND abs:partition AND abs:algorithm OR abs:"edge-based graph partitioning" OR abs:"graph streaming partition") AND (ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"large-scale graph data")`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"large-scale graph data")`（arxiv；有命中）
  - `("graph flow partition algorithm" OR "edge-based graph partitioning" OR "graph streaming partition") AND ("distributed graph neural network training" OR "distributed GNN training" OR "large-scale graph data")`（springer；有命中）
  - `("graph flow partition algorithm" OR "edge-based graph partitioning" OR "graph streaming partition" OR "graph stream partitioning" OR "edge-cut partitioning") AND ("distributed graph neural network training" OR "distributed GNN training" OR "large-scale graph data" OR "distributed graph learning" OR "scalable GNN training") AND ("worker nodes" OR "subgraph assignment" OR "parallel processing" OR "distributed workers" OR "subgraph allocation")`（springer；有命中）
  - `("graph flow partition algorithm" OR "edge-based graph partitioning" OR "graph streaming partition" OR "graph stream partitioning" OR "edge-cut partitioning") OR ("distributed graph neural network training" OR "distributed GNN training" OR "large-scale graph data" OR "distributed graph learning" OR "scalable GNN training") OR ("worker nodes" OR "subgraph assignment" OR "parallel processing" OR "distributed workers" OR "subgraph allocation") OR ("dynamic graph streaming" OR "graph irregularity" OR "training efficiency" OR "evolving graphs" OR "graph skew")`（springer；部分成功）

---

## 六、检索结果

### 6.1 检索概况

共执行 1 轮检索计划，生成 7 张原始证据卡；通过 7 张，拒绝 0 张。

### 6.2 相关文献

### card_62cce85b10e07492d6d66e87 · Efficient Learning-based Graph Simulation for Temporal Graphs

- 查新点：NP-1
- 主要贡献：TGAE proposes an efficient learning-based approach using a temporal graph autoencoder to generate graph snapshots for temporal graphs, achieving good simulation quality and efficiency.
- 相关性：0.50
- 置信度：0.75
- 来源：
  - Efficient Learning-based Graph Simulation for Temporal Graphs：10.1109/ICDE65448.2025.00026
    - 引文：we propose an efficient learning-based approach to generate graph snapshots, namely temporal graph autoencoder (TGAE)
    - 位置：artifact art_532328167974ec703a74ac56 chars:847-964

### card_3d9d0903795629dfa516c9a7 · Scalable and Efficient Joint Spiking Embedding Predictive Architecture for Large-Scale Dynamic Graphs

- 查新点：NP-1
- 主要贡献：SG-JEPA proposes a joint spiking embedding predictive architecture for large-scale dynamic graph representation learning, achieving superior training efficiency and memory scalability compared with prior self-supervised dynamic graph baselines.
- 相关性：0.70
- 置信度：0.80
- 来源：
  - Scalable and Efficient Joint Spiking Embedding Predictive Architecture for Large-Scale Dynamic Graphs：https://arxiv.org/pdf/2607.18412
    - 引文：we propose SG-JEPA, a joint spiking embedding predictive architecture for large-scale dynamic graphs
    - 位置：artifact art_190612103e0aa1229a4ecb57 chars:2641-2741
  - Scalable and Efficient Joint Spiking Embedding Predictive Architecture for Large-Scale Dynamic Graphs：https://arxiv.org/pdf/2607.18412
    - 引文：SG-JEPA avoids the complex machinery (negative sampling, graph augmentations, edge-level reconstruction, etc.), resulting in superior training efficiency and memory scalability compared with prior self-supervised dynamic graph baselines.
    - 位置：artifact art_190612103e0aa1229a4ecb57 chars:3389-3626

### card_0bbbbd9ffac0fc04893533cb · AGL: a Scalable System for Industrial-purpose Graph Machine Learning

- 查新点：NP-2
- 主要贡献：Designs AGL, a scalable, fault-tolerant, and integrated system for GNN training and inference using MapReduce-based message passing.
- 相关性：0.50
- 置信度：0.80
- 来源：
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：In this paper, we design AGL, a scalable, fault-tolerance and integrated system, with fully-functional training and inference for GNNs.
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1006-1141

### card_b3631b654e6dc98339a9f88e · AliGraph: A Comprehensive Graph Neural Network Platform

- 查新点：NP-2
- 主要贡献：Presents AliGraph, a comprehensive graph neural network system with distributed graph storage, optimized sampling operators, and runtime to support GNN training at scale.
- 相关性：0.50
- 置信度：0.80
- 来源：
  - AliGraph: A Comprehensive Graph Neural Network Platform：https://arxiv.org/pdf/1902.08730
    - 引文：we present a comprehensive graph neural network system, namely AliGraph, which consists of distributed graph storage, optimized sampling operators and runtime to efficiently support not only existing popular GNNs but also a series of in-house developed ones for different scenarios
    - 位置：artifact art_d88778158223021b818fdd97 chars:649-930

### card_cfd4c8d0fd2251cfb98d889b · Graph Attention Networks

- 查新点：NP-2
- 主要贡献：Presents graph attention networks (GATs), novel neural network architectures that leverage masked self-attentional layers for graph-structured data.
- 相关性：0.30
- 置信度：0.80
- 来源：
  - Graph Attention Networks：https://arxiv.org/pdf/1710.10903
    - 引文：We present graph attention networks (GATs), novel neural network architectures that operate on graph-structured data, leveraging masked self-attentional layers
    - 位置：artifact art_646de98cecaee1517f7729c3 chars:0-159

### card_e507ee5ab93c2063b40182b1 · GraphSAINT: Graph Sampling Based Inductive Learning Method

- 查新点：NP-2
- 主要贡献：Proposes GraphSAINT, a graph sampling based inductive learning method that improves training efficiency and accuracy for GCNs.
- 相关性：0.40
- 置信度：0.80
- 来源：
  - GraphSAINT: Graph Sampling Based Inductive Learning Method：https://arxiv.org/pdf/1907.04931
    - 引文：We propose GraphSAINT, a graph sampling based inductive learning method that improves training efficiency and accuracy in a fundamentally different way.
    - 位置：artifact art_4144023700aceff174c81183 chars:274-426

### card_d3a23b3829ff3bd86dd433bf · HGP-IC: graph neural networks via hotness-based partitioning and information compensation

- 查新点：NP-3
- 主要贡献：HGP-IC proposes a refined graph partitioning strategy (HGP) combined with information compensation (IC) for GNN training on large-scale graphs, addressing the challenges of edge partitioning where nodes cannot access all their original neighbors during subgraph training.
- 相关性：0.85
- 置信度：0.90
- 来源：
  - HGP-IC: graph neural networks via hotness-based partitioning and information compensation：10.1007/s11227-025-07880-w
    - 引文：Existing graph partitioning methods fall into node and edge partitioning. Node partitioning drops inter-subgraph edges, causing incomplete information, while edge partitioning, though structure-preserving, introduces two major challenges
    - 位置：artifact art_0bc5a7702aa10720af9a7f2a chars:423-660
  - HGP-IC: graph neural networks via hotness-based partitioning and information compensation：10.1007/s11227-025-07880-w
    - 引文：the "graph partitioning $$ + $$ + local learning" framework splits the global graph into smaller subgraphs for independent training
    - 位置：artifact art_0bc5a7702aa10720af9a7f2a chars:290-421

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 2 | 有证据 |
| NP-2 | 4 | 有证据 |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 部分新颖

提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，该方法结合图摘要技术和图自编码器，并利用循环神经网络学习时间维度的特征与依赖关系，能够高效生成大规模动态时序图的表征，显著降低内存消耗和训练时间。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 综合两张单卡核验结果：card_62cce85b10e07492d6d66e87（TGAE）与 card_3d9d0903795629dfa516c9a7（SG-JEPA）均仅部分重叠，未公开 GSAERU 的完整技术组合（图摘要压缩+图自编码器重构误差+RNN时序模块）。TGAE 使用图自编码器处理快照序列但面向图模拟生成，不含图摘要与RNN；SG-JEPA 面向大规模动态图表示学习但采用脉冲联合嵌入预测架构，明确未使用图摘要、重构误差与独立RNN时序模块。两篇均不能视为单篇完整公开该组合，故不构成先占性公开。但存在关键证据缺口：未核验申请人原始论文（GSAERU 自身）作为对照，且未检索到任何同时组合图摘要+图自编码器+RNN的文献，无法完全排除他人已公开类似组合。因此判定为部分新颖，置信度中等。  
**置信度：** 0.65  
**报告摘要：** 基于提供的有效证据卡，GSAERU 所提出的“图摘要压缩 + 图自编码器重构误差 + 循环神经网络时序模块”完整技术组合在现有检索覆盖内未被任何单篇文献完整公开。检索到的两篇相关文献（TGAE、SG-JEPA）分别涉及图自编码器处理时序图快照和大规模动态图表示学习，但均未同时组合图摘要、自编码器重构误差与独立RNN时序模块，故仅构成部分重叠。由于检索覆盖执行情况未知且申请人原始论文未纳入对照，无法完全排除已有类似公开，因此新颖性判定为部分新颖。  
**高度相关 Work：**
  - wrk_bd8b204d16e97238a8fc4373：与查新点共享图自编码器处理时序快照序列的要素，但用于图模拟生成而非节点表征学习，且不含图摘要与RNN时序模块，属部分重叠文献，需保留以体现部分相关。 (cards: card_62cce85b10e07492d6d66e87)
  - wrk_03f809d7b47d9dc5d4aaf002：同属大规模动态图表示学习领域，共享效率与内存可扩展目标，但未使用图摘要压缩、图自编码器重构误差或RNN时序模块，不覆盖查新点核心技术组合，属部分相关文献。 (cards: card_3d9d0903795629dfa516c9a7)

### NP-2 · 部分新颖

提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导—工作者”工作模式，通过基于边分割的图流划分算法对原图进行划分，工作节点执行基于图摘要的小批量训练，并通过注意力层将结果汇总至领导节点，实现大规模图流数据上GNN训练的高效加速。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 综合核验的3篇文献（AGL、AliGraph、GraphSAINT）均仅部分覆盖DSGNN的某些技术特征，未有任何单篇公开完整组合。AGL覆盖分布式GNN训练但缺少leader-worker、边分割图流划分、图摘要小批量训练和注意力层汇总；AliGraph为工业系统，覆盖分布式训练但未涉及任何核心特征；GraphSAINT覆盖基于子图的小批量训练但非分布式且为图采样而非图摘要，亦无leader-worker、边分割划分和注意力聚合。这些文献分别公开了部分特征，但多篇分别公开不等于单篇完整公开，不能据此否定新颖性。现有证据不足以证实或否定DSGNN四个特征组合的完整公开，故判定为partially_novel，置信度较低。  
**置信度：** 0.55  
**报告摘要：** 基于有效证据卡，DSGNN 的“领导—工作者模式 + 边分割图流划分 + 图摘要小批量训练 + 注意力层结果聚合”完整技术组合未在任何单篇文献中完整公开。检索到的 AGL、AliGraph、GraphSAINT 均仅部分覆盖该框架的个别特征（分别涉及分布式训练、图采样小批量训练等），但都缺少图摘要压缩、leader-worker工作模式及注意力聚合等核心要素，因此无法构成先占性公开。由于检索覆盖执行未知且缺少直接针对该组合的文献，新颖性判定为部分新颖。  
**高度相关 Work：**
  - wrk_ff5aa18cf0cfe7be1ba5e8bd：部分相关：大规模分布式GNN训练系统，但缺少DSGNN四项核心特征（leader-worker、边分割图流划分、图摘要小批量、注意力聚合）。 (cards: card_0bbbbd9ffac0fc04893533cb)
  - wrk_e59b8b7248dcc080455b8690：部分相关：分布式GNN训练平台，覆盖大规模数据场景，但未涉及图摘要、leader-worker、边分割划分及注意力聚合。 (cards: card_b3631b654e6dc98339a9f88e)
  - wrk_9567984f4fecd1cfc596ae3b：部分相关：基于图采样的子图小批量训练，与工作节点小批量训练特征有重叠，但非分布式且无其他核心特征。 (cards: card_e507ee5ab93c2063b40182b1)

### NP-3 · 部分新颖

在分布式图神经网络训练中，提出了基于边分割的图流划分算法，用于将大规模图数据划分为多个子图并分配给工作者节点，有效解决了图数据不规则性导致的分布式训练难点，提升了训练效率。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 单篇文献HGP-IC覆盖了基于边分割的图划分、大规模图划分为子图并分配处理的特征（技术特征1、2），但其划分面向静态图，未涉及图流/流式数据场景，也未实现动态图流下的自适应分区与扩展性提升，与查新点特征3不重合。基于当前单一文献证据，NP-3为部分新颖。  
**置信度：** 0.70  
**报告摘要：** 基于有效证据卡，所提出的基于边分割的图流划分算法（Sketch-DBH）未在现有文献中完整公开。HGP-IC 提出了静态图上的边分割分区策略，并覆盖了大规模图划分为子图以适应资源限制的特征，但其未涉及图流（流式）数据场景下的自适应分区与扩展性提升，因此仅部分重叠。由于检索覆盖未知且缺乏专门针对图流划分与动态图自适应分区的文献，新颖性判定为部分新颖。  
**高度相关 Work：**
  - wrk_41ddb8f3ff7a0fea5ed4c575：该文献提出基于边分割的图划分策略（HGP），覆盖将大规模图划分为子图以缓解内存与不规则性问题的特征，但不涉及图流/流式数据的自适应划分，为部分相关文献。 (cards: card_d3a23b3829ff3bd86dd433bf)

---

## 八、报告局限

- 本次查新未提供检索覆盖执行事实（如各来源是否成功执行、命中记录数等），因此无法区分检索失败与成功零命中，也无法确认全部必要来源均已覆盖；结论基于所提供的有效证据卡，检索完整性未知。
- 所有有效证据卡均通过证据门控，但仅部分覆盖查新点技术特征，未发现同时公开完整技术组合的文献，故各查新点均裁定为部分新颖。
- 未发现被拒绝证据（rejected_evidence 为空），不存在技术性质疑或格式性拒绝。
- 证据卡所依托的文献主要涉及图自编码器、动态图表示学习、分布式 GNN 训练及静态图边分割划分，均未完整涵盖 GSAERU 或 DSGNN 的核心组合；且申请人自身论文未作为对照基线纳入查新，进一步限制了新颖性确认的充分性。

---

## 九、附件及参考信息

### 缺失参考文献

无。

### 缺失 Baseline

- 申请人原始论文（GSAERU 与 DSGNN）未纳入对照检索基线，导致无法直接比对申请人自身的方案与现有工作。

### 引用问题

无。

### 被拒绝证据

无。

### 检索到的文献

- Out-of-Distribution Inverse Design of Elastic Networks with Differentiable Graph Neural Network Molecular Dynamics：[https://arxiv.org/pdf/2609.06655](https://arxiv.org/pdf/2609.06655)
- Assessing the Generalization of Graph Neural Networks for Fault Location Across Increasing Distributed Energy Resource Penetration Levels：[https://arxiv.org/pdf/2607.29293](https://arxiv.org/pdf/2607.29293)
- When does distribution shift break graph neural networks calibration?：[https://arxiv.org/pdf/2607.10804](https://arxiv.org/pdf/2607.10804)
- Robustness of Spatio-temporal Graph Neural Networks for Fault Location in Partially Observable Distribution Grids：[https://arxiv.org/pdf/2604.20403](https://arxiv.org/pdf/2604.20403)
- When Graph Structure Becomes a Liability: A Critical Re-Evaluation of Graph Neural Networks for Bitcoin Fraud Detection under Temporal Distribution Shift：[https://arxiv.org/pdf/2604.19514](https://arxiv.org/pdf/2604.19514)
- Octopus-inspired Distributed Control for Soft Robotic Arms: A Graph Neural Network-Based Attention Policy with Environmental Interaction：[https://arxiv.org/pdf/2603.10198](https://arxiv.org/pdf/2603.10198)
- Quantifying Explanation Quality in Graph Neural Networks using Out-of-Distribution Generalization：[https://arxiv.org/pdf/2602.07708](https://arxiv.org/pdf/2602.07708)
- Fed-Listing: Federated Label Distribution Inference in Graph Neural Networks：[https://arxiv.org/pdf/2602.00407](https://arxiv.org/pdf/2602.00407)
- Scalable and Efficient Joint Spiking Embedding Predictive Architecture for Large-Scale Dynamic Graphs：[https://arxiv.org/pdf/2607.18412](https://arxiv.org/pdf/2607.18412)
- GRExplainer: A Universal Explanation Method for Temporal Graph Neural Networks：[https://arxiv.org/pdf/2512.22772](https://arxiv.org/pdf/2512.22772)
- Efficient Learning-based Graph Simulation for Temporal Graphs：[https://arxiv.org/pdf/2510.05569](https://arxiv.org/pdf/2510.05569)
- GraphComp: Extreme Error-bounded Compression of Scientific Data via Temporal Graph Autoencoders：[https://arxiv.org/pdf/2505.06316](https://arxiv.org/pdf/2505.06316)
- Graph Pruning Based Spatial and Temporal Graph Convolutional Network with Transfer Learning for Traffic Prediction：[https://arxiv.org/pdf/2409.16532](https://arxiv.org/pdf/2409.16532)
- Temporal Graph Neural Network-Powered Paper Recommendation on Dynamic Citation Networks：[https://arxiv.org/pdf/2408.15371](https://arxiv.org/pdf/2408.15371)
- Temporal Graph Learning Recurrent Neural Network for Traffic Forecasting：[https://arxiv.org/pdf/2406.02726](https://arxiv.org/pdf/2406.02726)
- Real-Time Indian Sign Language Recognition Using Hierarchical Windowed Graph Attention Networks with Motion-Gated Inference and Multi-language Support：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31998-2_21](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31998-2_21)
- MinST: Multilevel Enhanced Architecture Search for Spatial-Temporal Forecasting with LLM：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38410-2_33](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38410-2_33)
- Forecasting Financial Variables from Structured Accounting Time Series with Echo State Networks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38404-1_39](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38404-1_39)
- Direction-Aware Heterogeneous Graph Neural Networks with Dual-Conditioned Normalizing Flows for Spatio-Temporal Anomaly Detection：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38407-2_17](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38407-2_17)
- Single-Stream Multi-feature Fusion with Temporal Robustness for Gait Emotion Recognition：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38401-0_41](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38401-0_41)
- Evaluation of Cross-Modal Data Fusion’s Present Situation in Intelligent Transportation Applications：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3566-7_27](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3566-7_27)
- Applications of Large Language Models in Traffic Flow Prediction：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3566-7_22](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3566-7_22)
- Spanish Audio DeepFake Detection：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37438-7_35](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37438-7_35)
- Graph-Adaptive Horseshoe for Compositional Regression：[https://arxiv.org/pdf/2608.17858](https://arxiv.org/pdf/2608.17858)
- CGS: Configurable Graph Summarization with Bounded Neighborhood Loss and Query Support：[https://arxiv.org/pdf/2607.10969](https://arxiv.org/pdf/2607.10969)
- COREKG: Coreset-Guided Personalized Summarization of Knowledge Graphs：[https://arxiv.org/pdf/2605.14900](https://arxiv.org/pdf/2605.14900)
- Spectral Model eXplainer: a chemically-grounded explainability framework for spectral-based machine learning models：[https://arxiv.org/pdf/2605.02684](https://arxiv.org/pdf/2605.02684)
- A Null Model for Mapper Subtype Claims：[https://arxiv.org/pdf/2604.17395](https://arxiv.org/pdf/2604.17395)
- Explainable Mapper: Charting LLM Embedding Spaces Using Perturbation-Based Explanation and Verification Agents：[https://arxiv.org/pdf/2507.18607](https://arxiv.org/pdf/2507.18607)
- Causal DAG Summarization (Full Version)：[https://arxiv.org/pdf/2504.14937](https://arxiv.org/pdf/2504.14937)
- Code-Craft: Hierarchical Graph-Based Code Summarization for Enhanced Context Retrieval：[https://arxiv.org/pdf/2504.08975](https://arxiv.org/pdf/2504.08975)
- HGP-IC: graph neural networks via hotness-based partitioning and information compensation：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-025-07880-w](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-025-07880-w)
- Distributed k-Hop Query Powered by an Asynchronous Framework：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-96-0579-8_22](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-96-0579-8_22)
- Scalable distributed Louvain algorithm for community detection in large graphs：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-021-04224-2](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-021-04224-2)
- Distributed Graph Processing: Techniques and Systems：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-16-0479-9_2](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-16-0479-9_2)
- Survey of external memory large-scale graph processing on a multi-core system：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-019-03023-0](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-019-03023-0)
- A Novel Hybrid Transformer-Based Framework for Reconstruction-Based ECG Anomaly Detection：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31998-2_15](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31998-2_15)
- Digital Integration of Economic Systems of the Full Cycle of the Agro-Industrial Complex While Ensuring Food Security：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-35006-0_1](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-35006-0_1)
- Medical Big Data Analytics: A Conceptual Framework for Data Sources, Tools, ML Algorithms, Challenges, and Opportunities：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31998-2_32](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31998-2_32)
- AliGraph: A Comprehensive Graph Neural Network Platform：[https://arxiv.org/pdf/1902.08730](https://arxiv.org/pdf/1902.08730)
- AGL: a Scalable System for Industrial-purpose Graph Machine Learning：[https://arxiv.org/pdf/2003.02454](https://arxiv.org/pdf/2003.02454)
- GraphSAINT: Graph Sampling Based Inductive Learning Method：[https://arxiv.org/pdf/1907.04931](https://arxiv.org/pdf/1907.04931)
- Graph Attention Networks：[https://arxiv.org/pdf/1710.10903](https://arxiv.org/pdf/1710.10903)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
