# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-15T18:44:17+08:00 |
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

- 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，将动态时序图建模为时间快照序列，通过图摘要压缩原图并输入图自编码器学习节点表征，再利用循环神经网络捕捉时间维度特征与依赖关系，从而高效生成大规模时序图表征，与传统的图神经网络算法相比，平均内存消耗和平均训练时长仅为其9.86%与13.27%，性能差距不超过3.5%。
- 提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，领导节点利用基于边分割的图流划分算法对原图进行划分，工作节点执行基于图摘要技术的小批量训练，并通过注意力层返回训练结果，领导节点汇总结果计算梯度并同步更新所有计算节点上的模型，从而显著加速GNN训练，在链路预测任务上的F1分数显著高于其他分布式图神经网络模型。
- 提出了一种基于边分割的图流划分算法，用于分布式图神经网络训练中对大规模图流数据进行有效划分，能够将原图划分为多个子图并分配给工作节点，从而支持高效的分布式训练。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，将动态时序图建模为时间快照序列，通过图摘要压缩原图并输入图自编码器学习节点表征，再利用循环神经网络捕捉时间维度特征与依赖关系，从而高效生成大规模时序图表征，与传统的图神经网络算法相比，平均内存消耗和平均训练时长仅为其9.86%与13.27%，性能差距不超过3.5%。 | Proposed a large-scale sequential graph representation learning method GSAERU based on graph summarization, which models dynamic sequential graphs as a sequence of snapshots, compresses the original graph via graph summarization into a graph autoencoder to learn node representations, and then uses a recurrent neural network to capture temporal features and dependencies, efficiently generating representations of large-scale temporal graphs. Compared with traditional graph neural network algorithms, its average memory consumption and average training time are only 9.86% and 13.27%, respectively, and the performance gap is within 3.5% on most metrics. |
| NP-2 | 提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，领导节点利用基于边分割的图流划分算法对原图进行划分，工作节点执行基于图摘要技术的小批量训练，并通过注意力层返回训练结果，领导节点汇总结果计算梯度并同步更新所有计算节点上的模型，从而显著加速GNN训练，在链路预测任务上的F1分数显著高于其他分布式图神经网络模型。 | Proposed a distributed graph neural network optimization training algorithm DSGNN based on graph summarization, which adopts a leader-worker mode. The leader node partitions the original graph using an edge segmentation based graph flow partition algorithm, workers perform mini-batch training based on graph summarization technology, and return training results through an attention layer. The leader summarizes results, computes gradients, and synchronously updates models on all computing nodes, significantly accelerating GNN training with F1 score on link prediction significantly higher than other distributed GNN models. |
| NP-3 | 提出了一种基于边分割的图流划分算法，用于分布式图神经网络训练中对大规模图流数据进行有效划分，能够将原图划分为多个子图并分配给工作节点，从而支持高效的分布式训练。 | Proposed an edge-based graph streaming partition algorithm for distributed graph neural network training, which effectively partitions large-scale graph streaming data into subgraphs and assigns them to worker nodes, thereby supporting efficient distributed training. |

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
  - `("large-scale temporal graph" OR "dynamic graph" OR "sequential graph") AND ("graph summarization" OR "graph compression") AND ("graph autoencoder" OR "graph representation learning") AND ("recurrent neural network" OR "temporal dependency modeling")`
- **NP-2**
  - 无
- **NP-3**
  - `("edge-based graph partitioning" OR "edge-cut partitioning" OR "graph stream partitioning")`

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 2 张原始证据卡；通过 2 张，拒绝 0 张。

### 6.2 相关文献

### card_2830f41a06e51171423649cd · AliGraph: A Comprehensive Graph Neural Network Platform

- 查新点：NP-2
- 主要贡献：AliGraph presents a comprehensive distributed graph neural network platform with distributed graph storage, optimized sampling operators, and runtime, achieving significant training speedup and F1 score improvements on large-scale graphs.
- 相关性：0.50
- 置信度：0.70
- 来源：
  - AliGraph: A Comprehensive Graph Neural Network Platform：https://arxiv.org/pdf/1902.08730
    - 引文：we present a comprehensive graph neural network system, namely AliGraph, which consists of distributed graph storage, optimized sampling operators and runtime to efficiently support not only existing popular GNNs but also a series of in-house developed ones for different scenarios
    - 位置：artifact art_d88778158223021b818fdd97 chars:649-930
  - AliGraph: A Comprehensive Graph Neural Network Platform：https://arxiv.org/pdf/1902.08730
    - 引文：At training, AliGraph runs 40%-50% faster with the novel caching strategy and demonstrates around 12 times speed up with the improved runtime.
    - 位置：artifact art_d88778158223021b818fdd97 chars:1392-1534
  - AliGraph: A Comprehensive Graph Neural Network Platform：https://arxiv.org/pdf/1902.08730
    - 引文：our in-house developed GNN models all showcase their statistically significant superiorities in terms of both effectiveness and efficiency (e.g., 4.12%-17.19% lift by F1 scores)
    - 位置：artifact art_d88778158223021b818fdd97 chars:1548-1725

### card_05fe604814671131d009b01e · Scalability and performance in distributed graph databases

- 查新点：NP-3
- 主要贡献：This paper presents a comparative analysis of four graph partitioning strategies (Random Vertex, Metis-based, Random Edge, and HDRF) spanning both edge-cut and vertex-cut paradigms for distributed graph databases, evaluating load balancing, communication overhead, and scalability on dynamic power-law networks.
- 相关性：0.70
- 置信度：0.75
- 来源：
  - Scalability and performance in distributed graph databases：10.1007/s10586-026-06406-0
    - 引文：Graph partitioning is a critical enabler of scalability in distributed graph databases, impacting load balancing, communication overhead, and query performance.
    - 位置：artifact art_dc41a5a066be129dd98d34d0 chars:0-160
  - Scalability and performance in distributed graph databases：10.1007/s10586-026-06406-0
    - 引文：four partitioning strategies Random Vertex, Metis-based, Random Edge, and HDRF spanning both edge-cut and vertex-cut paradigms
    - 位置：artifact art_dc41a5a066be129dd98d34d0 chars:207-333

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 0 | 0 Card |
| NP-2 | 1 | 有证据 |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，将动态时序图建模为时间快照序列，通过图摘要压缩原图并输入图自编码器学习节点表征，再利用循环神经网络捕捉时间维度特征与依赖关系，从而高效生成大规模时序图表征，与传统的图神经网络算法相比，平均内存消耗和平均训练时长仅为其9.86%与13.27%，性能差距不超过3.5%。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 查新点NP-1提出基于图摘要的大规模时序图表示学习方法GSAERU。经检索后，最终没有获得任何有效证据卡，因此无法对该查新点的新颖性作出可靠判定。根据流程，证据不足，不能认定其新颖性或否定其新颖性，结论为证据不足。  
**高度相关 Work：**
  - 无

### NP-2 · 部分新颖

提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，领导节点利用基于边分割的图流划分算法对原图进行划分，工作节点执行基于图摘要技术的小批量训练，并通过注意力层返回训练结果，领导节点汇总结果计算梯度并同步更新所有计算节点上的模型，从而显著加速GNN训练，在链路预测任务上的F1分数显著高于其他分布式图神经网络模型。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 查新点DSGNN提出的核心组合特征是：领导-工作者模式+基于边分割的图流划分算法、工作节点基于图摘要技术的小批量训练、以及经注意力层返回训练结果并由领导节点汇总计算梯度同步更新所有节点模型。现有唯一有效证据AliGraph仅证明'分布式GNN训练可显著加速训练并提升F1分数'这一背景性方向（约12倍加速、4.12%-17.19% F1提升），但AliGraph未采用图摘要小批量训练、未采用领导-工作者+边分割图流划分模式、未采用注意力层聚合返回训练结果，且其定位为通用GNN平台而非针对链路预测任务的特定同步更新机制。因此现有证据未披露查新点的任何核心组合技术特征，缺乏对其核心创新的直接对照文献，无法认定'不新颖'；但现有证据数量仅1篇且相关性有限（relevance=0.5），尚不足以对查新点核心特征的绝对新颖性（novel）给予高置信度判定。综合判定为'部分新颖'，需要补充针对核心特征（图摘要、边分割图流划分、注意力层聚合、领导-工作者同步更新）的直接相关文献以进一步提高置信度。  
**置信度：** 0.65  
**报告摘要：** 查新点NP-2提出基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式、边分割图流划分、图摘要小批量训练和注意力层聚合。唯一的有效证据为AliGraph（card_2830f41a06e51171423649cd），该文献只体现了分布式GNN训练可加速并提升F1的背景方向，未涉及查新点的核心组合特征。因此，基于现有证据，判定为部分新颖，但置信度较低，需补充更直接相关的文献。  
**高度相关 Work：**
  - wrk_e59b8b7248dcc080455b8690：AliGraph为分布式GNN训练平台，证明分布式GNN训练可加速训练并提升F1分数，与查新点所属的分布式GNN训练大方向背景一致，但未披露查新点的核心组合技术特征（图摘要小批量训练、边分割图流划分、注意力层聚合返回），仅作为背景性相关工作。 (cards: card_2830f41a06e51171423649cd)

### NP-3 · 部分新颖

提出了一种基于边分割的图流划分算法，用于分布式图神经网络训练中对大规模图流数据进行有效划分，能够将原图划分为多个子图并分配给工作节点，从而支持高效的分布式训练。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 查新点提出一种基于边分割的图流划分算法用于分布式GNN训练。现有证据（card_05fe604814671131d009b01e）证实以下先有技术基线：(1) 边分割（edge-cut）图划分、流式边分割算法（如HDRF）、以及分布式图处理中的负载均衡与可扩展性均为已公开的成熟技术，这与查新点的技术特征1（基于边分割的图流划分算法）和负载均衡目标直接重叠；(2) 图划分与子图分配是分布式图处理中的公认关键使能技术。然而，该证据与查新点存在明显差异：其针对分布式图数据库的OLTP/OLAP查询负载而非分布式GNN训练，且是'对比分析'已有划分策略而非'提出'新的边分割图流划分算法，也未覆盖'将划分子图分配给各工作节点以支持GNN训练'这一具体应用。由于查新点的核心技术手段（基于边分割的图流划分）作为一般性概念已属已知先有技术，但其针对分布式GNN训练的特定算法与工作节点子图分配的具体实现未被现有证据公开，故判定为部分新颖。  
**置信度：** 0.62  
**报告摘要：** 查新点NP-3提出基于边分割的图流划分算法用于分布式GNN训练。现有证据为card_05fe604814671131d009b01e，该文献涉及分布式图数据库中的边分割与流式划分策略（如HDRF），与查新点的'边分割图流划分'技术特征存在重叠，但未针对分布式GNN训练场景提出新算法，也未涉及子图分配机制。因此判定为部分新颖，需补充专门针对GNN训练的分区文献。  
**高度相关 Work：**
  - wrk_df8c0752cb7bc7b40b51da06：该工作公开了HDRF等流式边分割（edge-cut streaming partitioning）算法、分布式图处理中图划分对可扩展性与负载均衡的关键作用，直接构成查新点'基于边分割的图流划分算法'这一技术特征的最接近先有技术基线；但它针对分布式图数据库查询负载而非GNN训练，且是策略对比而非提出新算法，故作为最相关基线纳入。 (cards: card_05fe604814671131d009b01e)

---

## 八、报告局限

- NP-1查新点未获得任何有效证据卡，最终证据不足，无法对该点的新颖性进行可靠评估。
- 本报告中的文献检索范围受限于检索数据库和关键词，可能未覆盖所有相关文献。
- 对于NP-2和NP-3，现有证据数量较少且核心特征重叠有限，判定置信度均为中等偏低。
- 被拒绝证据列表为空（rejected_evidence为空），未发生技术性质疑或格式性拒绝。

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
