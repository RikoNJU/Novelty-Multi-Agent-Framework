# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-15T18:34:12+08:00 |
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

- 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩图快照并利用图自编码器重构误差训练节点表征，结合循环神经网络学习时间维度依赖，高效生成动态图的高质量低维表征。
- 提出基于图摘要的分布式图神经网络优化训练算法 DSGNN，采用“领导者-工作者”模式，通过基于边分割的图流划分算法划分大规模图数据，工作节点执行基于图摘要的小批量训练，并通过注意力层将训练结果返回领导节点，最终由领导节点汇总计算梯度并同步更新所有计算节点模型，从而加速大规模图上的 GNN 训练并提升链路预测性能。
- 提出一种基于边分割的图流划分算法，用于大规模图流数据场景下将原图划分为多个子图，分配给多个工作节点以实现分布式图神经网络训练，从而克服图数据不规则性带来的训练挑战。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩图快照并利用图自编码器重构误差训练节点表征，结合循环神经网络学习时间维度依赖，高效生成动态图的高质量低维表征。 | Propose GSAERU, a large-scale sequential graph representation learning method based on graph summarization, which compresses graph snapshots via graph summarization and trains node representations using a graph autoencoder with reconstruction error, then employs a recurrent neural network to learn temporal dependencies, efficiently generating high-quality low-dimensional representations for dynamic graphs. |
| NP-2 | 提出基于图摘要的分布式图神经网络优化训练算法 DSGNN，采用“领导者-工作者”模式，通过基于边分割的图流划分算法划分大规模图数据，工作节点执行基于图摘要的小批量训练，并通过注意力层将训练结果返回领导节点，最终由领导节点汇总计算梯度并同步更新所有计算节点模型，从而加速大规模图上的 GNN 训练并提升链路预测性能。 | Propose DSGNN, a distributed graph neural network optimization training algorithm based on graph summarization, which adopts leader-worker mode, partitions large-scale graph data using an edge-based graph stream partitioning algorithm, workers perform mini-batch training based on graph summarization and return results through an attention layer, and the leader aggregates results, computes gradients, and synchronously updates models on all computing nodes, thereby accelerating GNN training on large-scale graphs and improving link prediction performance. |
| NP-3 | 提出一种基于边分割的图流划分算法，用于大规模图流数据场景下将原图划分为多个子图，分配给多个工作节点以实现分布式图神经网络训练，从而克服图数据不规则性带来的训练挑战。 | Propose an edge-based graph stream partitioning algorithm to partition the original graph into subgraphs for multiple workers in large-scale graph streaming scenarios, enabling distributed graph neural network training and overcoming the challenges caused by irregularity of graph data. |

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
  - `("dynamic graph" OR "temporal graph" OR "sequential graph") AND ("graph representation learning" OR "graph embedding" OR "node embedding") AND ("graph summarization" OR "graph compression") AND ("graph autoencoder" OR "reconstruction error") AND ("recurrent neural network" OR "temporal dependency")`
- **NP-2**
  - 无
- **NP-3**
  - `("edge-based graph partitioning" OR "edge partitioning algorithm" OR "graph stream partitioning") AND ("graph neural network" OR "distributed training" OR "graph streaming")`

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 3 张原始证据卡；通过 3 张，拒绝 0 张。

### 6.2 相关文献

### card_1800ebe9811ad96dfd604571 · AGL: a Scalable System for Industrial-purpose Graph Machine Learning

- 查新点：NP-2
- 主要贡献：AGL is a scalable, fault-tolerant, integrated system for industrial-purpose graph machine learning that supports fully-functional training and inference for GNNs using message passing and k-hop neighborhood generation.
- 相关性：0.50
- 置信度：0.80
- 来源：
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：we design AGL, a scalable, fault-tolerance and integrated system, with fully-functional training and inference for GNNs. Our system design follows the message passing scheme underlying the computations of GNNs.
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1021-1231

### card_396b3a2c53a363562c5987e7 · AliGraph: A Comprehensive Graph Neural Network Platform

- 查新点：NP-2
- 主要贡献：AliGraph is a comprehensive distributed graph neural network platform providing distributed graph storage, optimized sampling operators, and runtime to support GNN training on large-scale graphs.
- 相关性：0.50
- 置信度：0.80
- 来源：
  - AliGraph: A Comprehensive Graph Neural Network Platform：https://arxiv.org/pdf/1902.08730
    - 引文：we present a comprehensive graph neural network system, namely AliGraph, which consists of distributed graph storage, optimized sampling operators and runtime to efficiently support not only existing popular GNNs but also a series of in-house developed ones for different scenarios.
    - 位置：artifact art_d88778158223021b818fdd97 chars:649-931

### card_24ffeae0e14ebf065a3d9bed · A two-phase streaming edge partitioning algorithm for large-scale uncertain graphs

- 查新点：NP-3
- 主要贡献：Proposes TPEP (Two-Phase Edge Partitioning), a streaming edge partitioning algorithm to partition large-scale uncertain graphs, formulated as an optimization problem minimizing replicated vertices and balancing partition load.
- 相关性：0.75
- 置信度：0.85
- 来源：
  - A two-phase streaming edge partitioning algorithm for large-scale uncertain graphs：10.1007/s10586-025-05338-5
    - 引文：This paper presents a streaming edge partitioning algorithm TPEP (Two-Phase Edge Partitioning) to partition the large-scale uncertain graphs.
    - 位置：artifact art_9d54d3bdcacef19c820b8340 chars:552-693
  - A two-phase streaming edge partitioning algorithm for large-scale uncertain graphs：10.1007/s10586-025-05338-5
    - 引文：TPEP uses a score function to guide the streaming partitioning process
    - 位置：artifact art_9d54d3bdcacef19c820b8340 chars:889-959

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 0 | 0 Card |
| NP-2 | 2 | 有证据 |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩图快照并利用图自编码器重构误差训练节点表征，结合循环神经网络学习时间维度依赖，高效生成动态图的高质量低维表征。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 针对GSAERU基于图摘要的大规模时序图表示学习方法，当前没有有效证据卡可支撑判定，最终证据不足。检索范围内未找到与图摘要压缩快照+图自编码器重构+RNN时序学习这一特征组合直接相关且可用的文献证据。  
**高度相关 Work：**
  - 无

### NP-2 · 新颖

提出基于图摘要的分布式图神经网络优化训练算法 DSGNN，采用“领导者-工作者”模式，通过基于边分割的图流划分算法划分大规模图数据，工作节点执行基于图摘要的小批量训练，并通过注意力层将训练结果返回领导节点，最终由领导节点汇总计算梯度并同步更新所有计算节点模型，从而加速大规模图上的 GNN 训练并提升链路预测性能。

**Reviewer 裁定：** 新颖  
**裁定理由：** 查新点DSGNN主张的技术链包含5个特异性特征：leader-worker分布式模式、基于边分割的图流划分算法、工作节点执行图摘要小批量训练、训练结果经注意力层返回领导节点、领导节点汇总梯度同步更新所有计算节点模型。已获两条证据（AGL、AliGraph）均为大规模图GNN训练的工业级系统，它们在宽泛的训练目标（加速大规模图上GNN训练）上与查新点存在部分重叠，可视为基线相关工作；但两条证据的技术路线分别采用message passing+k-hop邻域生成+MapReduce（AGL）和分布式图存储+采样算子（AliGraph），均未披露或结合查新点所主张的'边分割图流划分+图摘要小批量训练+注意力层回传结果+领导者集中计算梯度同步更新'这一完整特征组合。尤其leader-worker结构下的边分割图流划分与基于图摘要的小批量训练结合注意力层回传，在现有证据中完全未被预见。该特征组合特异性高，现有文献不能覆盖或否定其新颖性，故判定为新颖。  
**置信度：** 0.75  
**报告摘要：** 经Reviewer裁定，DSGNN方案的5个核心特征组合（leader-worker模式、边分割图流划分、图摘要小批量训练、注意力层回传、领导者集中更新）在AGL和AliGraph两条基线证据中均未覆盖或暗示，故新颖性判定为novel。  
**高度相关 Work：**
  - wrk_e59b8b7248dcc080455b8690：AliGraph为综合分布式GNN训练平台，在'大规模图GNN分布式训练'这一查新点目标上与DSGNN重叠，可作为基线系统参考；但其采用分布式图存储与采样算子，未覆盖查新点'图摘要、leader-worker边分割划分、注意力层回传'等核心区别特征。 (cards: card_396b3a2c53a363562c5987e7)
  - wrk_ff5aa18cf0cfe7be1ba5e8bd：AGL为工业级可扩展分布式GNN训练系统，与DSGNN在加速大规模图GNN训练的目标上重叠，可作为基线；但其基于message passing+k-hop邻域生成+MapReduce，未采用查新点的图摘要训练、leader-worker边分割划分及注意力层回传机制。 (cards: card_1800ebe9811ad96dfd604571)

### NP-3 · 证据不足，无法裁定

提出一种基于边分割的图流划分算法，用于大规模图流数据场景下将原图划分为多个子图，分配给多个工作节点以实现分布式图神经网络训练，从而克服图数据不规则性带来的训练挑战。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 针对基于边分割的图流划分算法查新点，存在1张有效证据卡（TPEP）但Reviewer因技术原因未能完成判定，最终证据不足。该卡虽涉及边分割图流划分，但未明确针对GNN分布式训练场景，且Reviewer未给出有效结论。  
**高度相关 Work：**
  - 无

---

## 八、报告局限

- NP-1查新点未获得任何有效证据卡，仅能认定为最终证据不足，不代表已检索到相关文献。
- NP-3查新点虽有一张有效证据卡（TPEP），但Reviewer在解析时出现JSON格式错误（无法完成判定），故该查新点按证据不足处理，需要补充检索或修复Reviewer输入后才能给出结论。
- 所有结论均严格依据Reviewer裁定和可追溯的证据卡，未引入外部臆断。

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
