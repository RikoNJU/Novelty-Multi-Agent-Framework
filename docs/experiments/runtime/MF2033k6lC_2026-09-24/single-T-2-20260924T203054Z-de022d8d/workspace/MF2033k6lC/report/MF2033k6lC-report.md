# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-14T06:07:15+08:00 |
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

- 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，该方法将动态时序图建模为各时刻的图快照序列，利用图摘要技术压缩原图后输入图自编码器学习节点表征，再通过循环神经网络捕获时间维度上的特征依赖，从而高效生成大规模时序图的低维表征。
- 提出了基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，由领导节点基于边分割的图流划分算法划分原图，工作节点执行基于图摘要技术的小批量训练，并通过注意力层返回结果，领导节点汇总计算梯度并同步更新所有节点模型，显著加速GNN训练并提升链路预测性能。
- 提出了一种面向大规模动态图的图神经网络优化机制，该机制通过图摘要技术对图数据进行压缩，并分别结合时序学习模块和分布式训练框架，实现了在大规模时序图上的高效表示学习和分布式场景下的快速模型训练，有效解决了现有GNN在处理大规模动态图时训练效率低下的问题。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，该方法将动态时序图建模为各时刻的图快照序列，利用图摘要技术压缩原图后输入图自编码器学习节点表征，再通过循环神经网络捕获时间维度上的特征依赖，从而高效生成大规模时序图的低维表征。 | Proposed a large-scale sequential graph representation learning method GSAERU based on graph summarization, which models dynamic sequential graphs as a sequence of graph snapshots, uses graph summarization to compress the original graph and feeds it into a graph autoencoder to learn node representations, then employs a recurrent neural network to capture temporal dependencies, thereby efficiently generating low-dimensional representations of large-scale sequential graphs. |
| NP-2 | 提出了基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，由领导节点基于边分割的图流划分算法划分原图，工作节点执行基于图摘要技术的小批量训练，并通过注意力层返回结果，领导节点汇总计算梯度并同步更新所有节点模型，显著加速GNN训练并提升链路预测性能。 | Proposed a distributed graph neural network optimization training algorithm DSGNN based on graph summarization, which adopts a leader-worker mode, where the leader divides the original graph using a graph flow partition algorithm based on edge segmentation, workers perform mini-batch training based on graph summarization, and an attention layer is used to return results, then the leader aggregates results, computes gradients, and synchronously updates all model replicas, greatly accelerating GNN training and improving link prediction performance. |
| NP-3 | 提出了一种面向大规模动态图的图神经网络优化机制，该机制通过图摘要技术对图数据进行压缩，并分别结合时序学习模块和分布式训练框架，实现了在大规模时序图上的高效表示学习和分布式场景下的快速模型训练，有效解决了现有GNN在处理大规模动态图时训练效率低下的问题。 | Proposed an optimization mechanism for graph neural networks on large-scale dynamic graphs, which compresses graph data via graph summarization and combines with sequence learning and distributed training frameworks to achieve efficient representation learning on large-scale sequential graphs and fast model training in distributed scenarios, effectively addressing the low training efficiency of existing GNNs on large-scale dynamic graphs. |

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
  - `NULL_QUERY(CONCEPT[C1:大规模时序图|动态图|时序图] AND CONCEPT[C2:图摘要|图压缩|图概括])`
  - `NULL_QUERY(CONCEPT[C2:图摘要|图压缩|图概括])`
  - `NULL_QUERY(CONCEPT[C1:大规模时序图|动态图|时序图] OR CONCEPT[C2:图摘要|图压缩|图概括] OR CONCEPT[C3:图自编码器|图自动编码器] OR CONCEPT[C4:循环神经网络|递归神经网络])`
  - `(ti:"大规模时序图" OR ti:"动态图" OR ti:"时序图") AND (abs:"图摘要" OR abs:"图压缩" OR abs:"图概括")`
  - `(abs:"图摘要" OR abs:"图压缩" OR abs:"图概括")`
  - `(ti:"大规模时序图" OR ti:"动态图" OR ti:"时序图" OR ti:"动态网络" OR ti:"时序网络") AND (abs:"图摘要" OR abs:"图压缩" OR abs:"图概括" OR abs:"graph summarization" OR abs:"图概要")`
  - `(abs:"图摘要" OR abs:"图压缩" OR abs:"图概括" OR abs:"graph summarization" OR abs:"图概要")`
  - `(ti:"大规模时序图" OR ti:"动态图" OR ti:"时序图" OR ti:"动态网络" OR ti:"时序网络") OR (abs:"图摘要" OR abs:"图压缩" OR abs:"图概括" OR abs:"graph summarization" OR abs:"图概要") OR (abs:"图自编码器" OR abs:"图自动编码器" OR abs:"graph autoencoder" OR abs:"GAE") OR (abs:"循环神经网络" OR abs:"递归神经网络" OR abs:"RNN" OR abs:"循环网络")`
  - `NULL_QUERY(CONCEPT[C1:large-scale temporal graph|sequential graph|dynamic graph] AND CONCEPT[C2:graph summarization|graph summarization technique])`
  - `NULL_QUERY(CONCEPT[C2:graph summarization|graph summarization technique])`
  - `NULL_QUERY(CONCEPT[C1:large-scale temporal graph|sequential graph|dynamic graph] OR CONCEPT[C2:graph summarization|graph summarization technique] OR CONCEPT[C3:graph autoencoder|graph auto-encoder] OR CONCEPT[C4:recurrent neural network|RNN])`
- **NP-2**
  - `NULL_QUERY(CONCEPT[C1:分布式图神经网络训练|图神经网络优化算法] AND CONCEPT[C2:图摘要技术|图流划分算法] AND CONCEPT[C3:领导-工作者模式])`
  - `NULL_QUERY(CONCEPT[C1:分布式图神经网络训练|图神经网络优化算法] AND CONCEPT[C2:图摘要技术|图流划分算法])`
  - `NULL_QUERY(CONCEPT[C1:分布式图神经网络训练|图神经网络优化算法] AND CONCEPT[C2:图摘要技术|图流划分算法] AND CONCEPT[C4:注意力层])`
  - `NULL_QUERY(CONCEPT[C1:分布式图神经网络训练|图神经网络优化算法] OR CONCEPT[C5:链路预测])`
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`
  - `abs:"graph summarization"`
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training") AND (abs:"graph summarization" OR abs:"graph summary")`
  - `(abs:"graph summarization" OR abs:"graph summary")`
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training") OR (abs:"graph summarization" OR abs:"graph summary") OR (abs:"leader-worker mode" OR abs:"leader-follower" OR abs:"master-worker") OR (abs:graph AND abs:flow AND abs:partition AND abs:algorithm OR abs:"edge-based graph partitioning")`
- **NP-3**
  - `NULL_QUERY(CONCEPT[C1:大规模动态图|时序图|动态图神经网络] AND CONCEPT[C2:图神经网络优化|图摘要|图压缩] AND CONCEPT[C3:时序学习|时间特征捕获|序列建模] AND CONCEPT[C4:分布式训练|并行计算|任务划分])`
  - `NULL_QUERY(CONCEPT[C1:大规模动态图|时序图|动态图神经网络] AND CONCEPT[C2:图神经网络优化|图摘要|图压缩] AND CONCEPT[C4:分布式训练|并行计算|任务划分])`
  - `NULL_QUERY(CONCEPT[C1:大规模动态图|时序图|动态图神经网络] AND CONCEPT[C2:图神经网络优化|图摘要|图压缩] AND CONCEPT[C3:时序学习|时间特征捕获|序列建模])`
  - `NULL_QUERY(CONCEPT[C1:大规模动态图|时序图|动态图神经网络] AND CONCEPT[C2:图神经网络优化|图摘要|图压缩])`
  - `NULL_QUERY(CONCEPT[C1:大规模动态图|时序图|动态图神经网络] OR CONCEPT[C2:图神经网络优化|图摘要|图压缩])`
  - `NULL_QUERY(CONCEPT[C1:large-scale dynamic graphs] AND CONCEPT[C2:graph neural networks])`
  - `NULL_QUERY(CONCEPT[C2:graph neural networks])`
  - `NULL_QUERY(CONCEPT[C1:large-scale dynamic graphs] OR CONCEPT[C2:graph neural networks] OR CONCEPT[C3:graph summarization] OR CONCEPT[C4:temporal learning module])`

---

## 六、检索结果

### 6.1 检索概况

共执行 1 轮检索计划，生成 3 张原始证据卡；通过 3 张，拒绝 0 张。

### 6.2 相关文献

### card_9c6f4b2f073c0de7c36c8956 · AGL: a Scalable System for Industrial-purpose Graph Machine Learning

- 查新点：NP-3
- 主要贡献：AGL is a scalable, fault-tolerant, integrated system for industrial-purpose graph machine learning that enables GNN training and inference on graphs with billions of nodes and hundred billions of edges using MapReduce and parameter servers.
- 相关性：0.50
- 置信度：0.85
- 来源：
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：In this paper, we design AGL, a scalable, fault-tolerance and integrated system, with fully-functional training and inference for GNNs. Our system design follows the message passing scheme underlying the computations of GNNs. We design to generate the $k$-hop neighborhood, an information-complete subgraph for each node, as well as do the inference simply by merging values from in-edge neighbors and propagating values to out-edge neighbors via MapReduce.
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1006-1463
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：Our system AGL, implemented on mature infrastructures, can finish the training of a 2-layer graph attention network on a graph with billions of nodes and hundred billions of edges in 14 hours, and complete the inference in 1.2 hour.
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1635-1867

### card_1d3f6b1a0f44ed58a3bef721 · AliGraph: A Comprehensive Graph Neural Network Platform

- 查新点：NP-3
- 主要贡献：AliGraph is a comprehensive graph neural network platform consisting of distributed graph storage, optimized sampling operators and runtime to efficiently support GNN training on large-scale graphs.
- 相关性：0.45
- 置信度：0.85
- 来源：
  - AliGraph: A Comprehensive Graph Neural Network Platform：https://arxiv.org/pdf/1902.08730
    - 引文：In this paper, we present a comprehensive graph neural network system, namely AliGraph, which consists of distributed graph storage, optimized sampling operators and runtime to efficiently support not only existing popular GNNs but also a series of in-house developed ones for different scenarios.
    - 位置：artifact art_d88778158223021b818fdd97 chars:634-931

### card_777a0ea7b97f353ecebca8f1 · Temporal Graph Networks for Deep Learning on Dynamic Graphs

- 查新点：NP-3
- 主要贡献：Temporal Graph Networks (TGNs) is a generic, efficient framework for deep learning on dynamic graphs represented as sequences of timed events, combining memory modules and graph-based operators for temporal representation learning.
- 相关性：0.50
- 置信度：0.85
- 来源：
  - Temporal Graph Networks for Deep Learning on Dynamic Graphs：https://arxiv.org/pdf/2006.10637
    - 引文：In this paper, we present Temporal Graph Networks (TGNs), a generic, efficient framework for deep learning on dynamic graphs represented as sequences of timed events. Thanks to a novel combination of memory modules and graph-based operators, TGNs are able to significantly outperform previous approaches being at the same time more computationally efficient.
    - 位置：artifact art_ea01d9c5f48ad68092a07bf7 chars:505-863

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 0 | 0 Card |
| NP-2 | 0 | 0 Card |
| NP-3 | 3 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，该方法将动态时序图建模为各时刻的图快照序列，利用图摘要技术压缩原图后输入图自编码器学习节点表征，再通过循环神经网络捕获时间维度上的特征依赖，从而高效生成大规模时序图的低维表征。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 最终证据不足：针对该查新点（基于图摘要的大规模时序图表示学习方法GSAERU）的中英文文献检索均未获得任何有效证据卡，无法形成可支持新颖性判定的证据基础。当前检索范围内未发现直接描述“图摘要+图自编码器+循环神经网络”组合用于大规模时序图的文献，但0 Card仅表示证据不足，不代表已检索到否定性文献。  
**高度相关 Work：**
  - 无

### NP-2 · 证据不足，无法裁定

提出了基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，由领导节点基于边分割的图流划分算法划分原图，工作节点执行基于图摘要技术的小批量训练，并通过注意力层返回结果，领导节点汇总计算梯度并同步更新所有节点模型，显著加速GNN训练并提升链路预测性能。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 最终证据不足：针对该查新点（基于图摘要的分布式图神经网络优化训练算法DSGNN）的中英文文献检索均未获得任何有效证据卡，无法形成可支持新颖性判定的证据基础。当前检索范围内未发现直接描述“图摘要+边分割图流划分+领导-工作者分布式训练+注意力聚合”组合的文献，但0 Card仅表示证据不足，不代表已检索到否定性文献。  
**高度相关 Work：**
  - 无

### NP-3 · 部分新颖

提出了一种面向大规模动态图的图神经网络优化机制，该机制通过图摘要技术对图数据进行压缩，并分别结合时序学习模块和分布式训练框架，实现了在大规模时序图上的高效表示学习和分布式场景下的快速模型训练，有效解决了现有GNN在处理大规模动态图时训练效率低下的问题。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 该查新点由三项技术特征组合而成。证据显示：时序学习模块（TGN，card_777a0ea7b97f353ecebca8f1）与分布式训练框架（AGL，card_9c6f4b2f073c0de7c36c8956；AliGraph，card_1d3f6b1a0f44ed58a3bef721）均已在已有文献中分别公开，其中 AGL/AliGraph 面向大规模图（十亿级节点）的分布式快速训练，TGN 面向动态图的时序表示学习。然而：特征1（图摘要技术压缩图数据）在当前全部中英文检索证据中未获任何覆盖；且没有任何单一文献将图摘要压缩、时序学习模块与分布式训练框架三者集成用于大规模动态图。现有对比文献均属静态图平台或单一维度方案，缺乏整体组合机制。故判定为部分新颖。  
**置信度：** 0.70  
**报告摘要：** 该查新点（面向大规模动态图的图神经网络优化机制，通过图摘要压缩并结合时序学习与分布式训练）在现有证据中呈现部分新颖性。已有文献分别覆盖了时序学习（TGN）和分布式训练（AGL、AliGraph），但图摘要压缩这一核心特征在检索到的中英文文献中均未获覆盖，且不存在将三者集成用于大规模动态图的单一文献。因此，图摘要压缩与整体组合机制未被现有证据否定，属于部分新颖。  
**高度相关 Work：**
  - wrk_712252459ef2697739d75d40：TGN 公开了针对动态图（时间事件序列）的时序学习模块（memory模块+图算子结合），与查新点特征2（时序学习模块捕获时间维度特征）直接对应，是查新点组合中最贴近时序动态图学习侧的先例，但未涉及图摘要压缩与分布式训练，也未面向大规模系统级优化。 (cards: card_777a0ea7b97f353ecebca8f1)
  - wrk_ff5aa18cf0cfe7be1ba5e8bd：AGL 公开了基于 MapReduce 与参数服务器的大规模图（十亿节点/千亿边）分布式训练与快速推理系统，与查新点特征3（分布式训练框架加速模型训练）直接对应，是先例证据；但其面向静态图，未含图摘要压缩与时序模块。 (cards: card_9c6f4b2f073c0de7c36c8956)
  - wrk_e59b8b7248dcc080455b8690：AliGraph 公开了面向大规模图的分布式图存储与运行时平台以高效支持 GNN 训练，与查新点特征3（分布式场景快速训练）部分对应；但面向静态图场景，未含图摘要压缩与时序模块。 (cards: card_1d3f6b1a0f44ed58a3bef721)

---

## 八、报告局限

- NP-1与NP-2在最终有效证据卡数量上均未达到门槛（有效卡片数为0，要求至少1），因此对这两个查新点只能表述为“最终证据不足”。该表述仅表示检索证据不足以支持任何新颖性判定，不排除存在相关文献未被当前检索范围覆盖的可能性。
- NP-3虽有3张有效证据卡，但仅覆盖了时序学习与分布式训练两个维度的部分先例；图摘要压缩特征在现有中英文检索证据中完全缺失，因此整体组合机制的新颖性未能被充分证实或否定。
- 本次查新检索范围与任务规划一致，但受限于已执行的中英文文献检索任务数量，可能存在未覆盖到的数据库或文献类型（如会议论文集、学位论文数据库等），上述结论仅基于当前可追溯的证据卡得出。
- 未存在被拒绝的证据（rejected_evidence为空），故无格式性拒绝或技术性质疑需要额外说明。

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
