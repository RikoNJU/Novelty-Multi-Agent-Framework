# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-15T18:21:48+08:00 |
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

- 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，该方法将动态图建模为快照序列，通过图摘要压缩图并利用图自编码器学习节点表征，结合循环神经网络捕捉时间依赖，显著降低内存消耗和训练时间，性能与传统GNN差距不超过3.5%。
- 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用"领导-工作者"工作模式，通过基于边分割的图流划分算法将原图划分为子图分配给各工作节点，工作节点执行基于图摘要的小批量训练，并由领导节点汇总结果计算梯度，同步更新所有计算节点上的模型，从而大幅加速GNN训练。
- 在分布式图神经网络训练中，提出基于注意力层的工作节点结果融合方法，工作节点将基于图摘要的小批量训练输出通过注意力层进行加权整合，由领导节点依据注意力权重汇总，有效利用各子图的特征信息，显著提升链路预测任务的F1分数。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，该方法将动态图建模为快照序列，通过图摘要压缩图并利用图自编码器学习节点表征，结合循环神经网络捕捉时间依赖，显著降低内存消耗和训练时间，性能与传统GNN差距不超过3.5%。 | Propose GSAERU, a large-scale sequential graph representation learning method based on graph summarization, which models dynamic graphs as sequences of snapshots, compresses graphs via graph summarization, learns node representations using a graph autoencoder, and captures temporal dependencies with a recurrent neural network, significantly reducing memory consumption and training time with performance gap to traditional GNNs within 3.5%. |
| NP-2 | 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用"领导-工作者"工作模式，通过基于边分割的图流划分算法将原图划分为子图分配给各工作节点，工作节点执行基于图摘要的小批量训练，并由领导节点汇总结果计算梯度，同步更新所有计算节点上的模型，从而大幅加速GNN训练。 | Propose DSGNN, a distributed graph neural network optimization training algorithm based on graph summarization, which adopts a "leader-worker" mode, uses a graph flow partition algorithm based on edge segmentation to divide the original graph into subgraphs assigned to workers, workers perform mini-batch training based on graph summarization, and the leader summarizes results to compute gradients and synchronously update models on all computing nodes, greatly accelerating GNN training. |
| NP-3 | 在分布式图神经网络训练中，提出基于注意力层的工作节点结果融合方法，工作节点将基于图摘要的小批量训练输出通过注意力层进行加权整合，由领导节点依据注意力权重汇总，有效利用各子图的特征信息，显著提升链路预测任务的F1分数。 | In distributed graph neural network training, propose an attention layer-based method for fusing results from worker nodes. Workers output mini-batch training results based on graph summarization through an attention layer, and the leader node aggregates them according to attention weights, effectively utilizing feature information from each subgraph and significantly improving F1 score on link prediction. |

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
  - 无
- **NP-2**
  - 无
- **NP-3**
  - 无

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 3 张原始证据卡；通过 3 张，拒绝 0 张。

### 6.2 相关文献

### card_ec28518f39562e1ae1ff5275 · AGL: a Scalable System for Industrial-purpose Graph Machine Learning

- 查新点：NP-1
- 主要贡献：AGL is a scalable, fault-tolerant, and integrated system for GNN training and inference on large-scale graphs, using k-hop neighborhood generation and MapReduce-based message passing.
- 相关性：0.50
- 置信度：0.80
- 来源：
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：we design AGL, a scalable, fault-tolerance and integrated system, with fully-functional training and inference for GNNs.
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1021-1141

### card_da4eec814d7a76c6cac45f56 · Inductive Representation Learning on Temporal Graphs

- 查新点：NP-1
- 主要贡献：Temporal Graph Attention (TGAT) layer for inductive representation learning on temporal graphs, using self-attention to aggregate temporal-topological neighborhood features and functional time encoding.
- 相关性：0.60
- 置信度：0.80
- 来源：
  - Inductive Representation Learning on Temporal Graphs：https://arxiv.org/pdf/2002.07962
    - 引文：We propose the temporal graph attention (TGAT) layer to efficiently aggregate temporal-topological neighborhood features as well as to learn the time-feature interactions.
    - 位置：artifact art_b8b821043e4485fda0b8527c chars:516-687

### card_f3114ca5ef189c024aff2fda · Temporal Graph Networks for Deep Learning on Dynamic Graphs

- 查新点：NP-1
- 主要贡献：Temporal Graph Networks (TGNs) is a generic, efficient framework for deep learning on dynamic graphs represented as sequences of timed events, combining memory modules and graph-based operators to capture temporal dependencies.
- 相关性：0.70
- 置信度：0.85
- 来源：
  - Temporal Graph Networks for Deep Learning on Dynamic Graphs：https://arxiv.org/pdf/2006.10637
    - 引文：we present Temporal Graph Networks (TGNs), a generic, efficient framework for deep learning on dynamic graphs represented as sequences of timed events.
    - 位置：artifact art_ea01d9c5f48ad68092a07bf7 chars:520-671

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 3 | 有证据 |
| NP-2 | 0 | 0 Card |
| NP-3 | 0 | 0 Card |

---

## 七、查新结论

### NP-1 · 新颖

提出一种基于图摘要的大规模时序图表示学习方法GSAERU，该方法将动态图建模为快照序列，通过图摘要压缩图并利用图自编码器学习节点表征，结合循环神经网络捕捉时间依赖，显著降低内存消耗和训练时间，性能与传统GNN差距不超过3.5%。

**Reviewer 裁定：** 新颖  
**裁定理由：** 查新点主张的是「图摘要压缩 → 图自编码器(以与原图重构误差训练节点表征) → RNN 时间依赖」这一四要素组合。现有证据(AGL/TGAT/TGN)均只分别命中某一侧面：AGL 仅回应大规模图降耗动机（用 k-hop 而非图摘要、无自编码器、无时序建模、无 RNN）；TGAT 仅回应时序图表示学习目标（用自注意力而非图摘要+自编码器+RNN）；TGN 虽有'动态图建模为序列'的近似建模，但用记忆模块+图算子而非图摘要压缩，未用图自编码器，未显式用 RNN。没有任何一篇披露该组合式方案，故查新点具备新颖性。  
**置信度：** 0.75  
**报告摘要：** 基于三篇有效证据卡（AGL、TGAT、TGN），本查新点主张的图摘要压缩+图自编码器+RNN组合方案在现有文献中未被披露。三篇对比文献仅部分涉及大规模图降耗、时序图表示学习或动态图建模，均未采用相同技术组合，因此判定为新颖。  
**高度相关 Work：**
  - wrk_712252459ef2697739d75d40：TGN 将动态图建模为事件序列，与查新点'将动态时序图建模为快照序列'的建模方式最接近，是破坏新颖性风险最高的对比基线；但未采用图摘要压缩、图自编码器与 RNN。 (cards: card_f3114ca5ef189c024aff2fda)
  - wrk_b6b76b1dae1837f54a226290：TGAT 面向时序图表示学习并捕捉时间特征交互，与查新点的时序依赖学习目标对齐；但用自注意力机制而非图摘要+自编码器+RNN 组合。 (cards: card_da4eec814d7a76c6cac45f56)

### NP-2 · 证据不足，无法裁定

提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用"领导-工作者"工作模式，通过基于边分割的图流划分算法将原图划分为子图分配给各工作节点，工作节点执行基于图摘要的小批量训练，并由领导节点汇总结果计算梯度，同步更新所有计算节点上的模型，从而大幅加速GNN训练。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 针对NP-2（基于图摘要的分布式图神经网络优化训练算法DSGNN），最终有效证据卡数量为0，未达到系统门槛（至少1张），无法进行新颖性判定。已尝试中文与英文检索，但未获得任何有效证据。  
**高度相关 Work：**
  - 无

### NP-3 · 证据不足，无法裁定

在分布式图神经网络训练中，提出基于注意力层的工作节点结果融合方法，工作节点将基于图摘要的小批量训练输出通过注意力层进行加权整合，由领导节点依据注意力权重汇总，有效利用各子图的特征信息，显著提升链路预测任务的F1分数。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 针对NP-3（基于注意力层的分布式图神经网络工作节点结果融合方法），最终有效证据卡数量为0，未达到系统门槛（至少1张），无法进行新颖性判定。已尝试中文与英文检索，但未获得任何有效证据。  
**高度相关 Work：**
  - 无

---

## 八、报告局限

- NP-2与NP-3的最终有效证据卡数量为0，未达到门槛，检索范围包括中文和英文文献，但未检索到直接相关的有效证据。
- NP-1的中文检索（T-1）未返回任何证据卡，当前仅有三篇英文证据，无法完全排除中文文献中可能披露相似组合方案的情况。

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

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
