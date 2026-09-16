# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T22:58:20+08:00 |
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

- 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图压缩为固定规模的新图，解决GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。
- 提出基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，领导节点负责图划分与模型同步更新，工作节点基于图摘要技术进行小批量训练，并通过注意力层返回结果。
- 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch概率数据结构存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间查询和负载均衡的子图划分。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图压缩为固定规模的新图，解决GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。 | Propose a large-scale sequential graph representation learning method GSAERU based on graph summarization, which compresses dynamic sequential graphs into fixed-size new graphs via graph summarization to address the issue that GNN outputs cannot be directly fed into RNN training, and employs a graph autoencoder and a recurrent neural network to learn temporal features. |
| NP-2 | 提出基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，领导节点负责图划分与模型同步更新，工作节点基于图摘要技术进行小批量训练，并通过注意力层返回结果。 | Propose a distributed graph neural network optimization training framework DSGNN based on graph summarization, adopting a leader-worker mode where the leader node handles graph partitioning and synchronous model updates, and worker nodes perform mini-batch training based on graph summarization and return results via an attention layer. |
| NP-3 | 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch概率数据结构存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间查询和负载均衡的子图划分。 | Propose an edge-segmentation-based graph stream partitioning algorithm Sketch-DBH, which uses the Count-Min Sketch probabilistic data structure to store node degree information and a min-heap to maintain high-frequency node information, enabling constant-time queries and load-balanced subgraph partitioning. |

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
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening") AND (ti:"temporal graph" OR ti:"dynamic graph" OR ti:"sequential graph") AND (abs:"graph autoencoder" OR abs:"graph neural network" OR abs:"recurrent neural network")`（arxiv；有命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening" OR abs:"graph summary" OR abs:"graph reduction") AND (ti:"temporal graph" OR ti:"dynamic graph" OR ti:"sequential graph" OR ti:"time-evolving graph" OR ti:"time series graph") AND (abs:"graph representation learning" OR abs:"node embedding" OR abs:"graph embedding" OR abs:"network representation learning")`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening" OR abs:"graph summary" OR abs:"graph reduction") AND (ti:"temporal graph" OR ti:"dynamic graph" OR ti:"sequential graph" OR ti:"time-evolving graph" OR ti:"time series graph")`（arxiv；有命中）
  - `(ti:"temporal graph" OR ti:"dynamic graph" OR ti:"sequential graph" OR ti:"time-evolving graph" OR ti:"time series graph") OR (abs:"graph representation learning" OR abs:"node embedding" OR abs:"graph embedding" OR abs:"network representation learning")`（arxiv；部分成功）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening") AND (ti:"temporal graph" OR ti:"dynamic graph" OR ti:"sequential graph") AND (abs:"graph autoencoder" OR abs:"graph neural network" OR abs:"recurrent neural network")`（arxiv；有命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening" OR abs:"graph summary" OR abs:"graph reduction") AND (ti:"temporal graph" OR ti:"dynamic graph" OR ti:"sequential graph" OR ti:"time-evolving graph" OR ti:"time series graph") AND (abs:"graph representation learning" OR abs:"node embedding" OR abs:"graph embedding" OR abs:"network representation learning")`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening" OR abs:"graph summary" OR abs:"graph reduction") AND (ti:"temporal graph" OR ti:"dynamic graph" OR ti:"sequential graph" OR ti:"time-evolving graph" OR ti:"time series graph")`（arxiv；有命中）
  - `(ti:"temporal graph" OR ti:"dynamic graph" OR ti:"sequential graph" OR ti:"time-evolving graph" OR ti:"time series graph") OR (abs:"graph representation learning" OR abs:"node embedding" OR abs:"graph embedding" OR abs:"network representation learning")`（arxiv；部分成功）
  - `("graph summarization" OR "graph compression" OR "graph coarsening") AND ("temporal graph" OR "dynamic graph" OR "sequential graph") AND ("graph autoencoder" OR "graph neural network" OR "recurrent neural network")`（springer；有命中）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework AND abs:"graph summarization" AND abs:"leader-worker mode"`（arxiv；零命中）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework AND abs:"graph summarization"`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework OR ti:"distributed GNN training" OR ti:distributed AND ti:graph AND ti:learning AND ti:system) AND (abs:"graph summarization" OR abs:"graph summary" OR abs:"graph condensation") AND (abs:"leader-worker mode" OR abs:"master-worker" OR abs:"parameter server architecture") AND (abs:"graph partitioning" OR abs:"graph stream partitioning" OR abs:"edge-based partitioning")`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework OR ti:"distributed GNN training" OR ti:distributed AND ti:graph AND ti:learning AND ti:system) AND (abs:"graph summarization" OR abs:"graph summary" OR abs:"graph condensation") AND (abs:"graph partitioning" OR abs:"graph stream partitioning" OR abs:"edge-based partitioning")`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework OR ti:"distributed GNN training" OR ti:distributed AND ti:graph AND ti:learning AND ti:system) OR (abs:"graph summarization" OR abs:"graph summary" OR abs:"graph condensation") OR (all:"distributed training" OR all:"parallel training" OR all:"scalable training")`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization] AND CONCEPT[C3:leader-worker mode])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization] AND CONCEPT[C3:leader-worker mode] AND CONCEPT[C4:graph partitioning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization] AND CONCEPT[C4:graph partitioning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] OR CONCEPT[C2:graph summarization] OR CONCEPT[C6:distributed training])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] OR CONCEPT[C2:graph summarization] OR CONCEPT[C6:distributed training])`（null_catalog；零命中）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"leader-worker mode" AND abs:"mini-batch training"`（arxiv；零命中）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"mini-batch training"`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"distributed graph learning") AND (abs:"graph summarization" OR abs:"graph summary" OR abs:"graph condensation") AND (abs:"leader-worker mode" OR abs:"master-worker" OR abs:"parameter server") AND (abs:"attention mechanism" OR abs:"attention layer" OR abs:"attention aggregation")`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"distributed graph learning") AND (abs:"graph summarization" OR abs:"graph summary" OR abs:"graph condensation") AND (abs:"attention mechanism" OR abs:"attention layer" OR abs:"attention aggregation")`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"distributed graph learning") OR (abs:"graph summarization" OR abs:"graph summary" OR abs:"graph condensation")`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training] AND CONCEPT[C2:graph summarization] AND CONCEPT[C3:leader-worker mode] AND CONCEPT[C4:mini-batch training])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training] AND CONCEPT[C2:graph summarization] AND CONCEPT[C4:mini-batch training])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training] AND CONCEPT[C2:graph summarization] AND CONCEPT[C3:leader-worker mode] AND CONCEPT[C5:attention mechanism])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training] AND CONCEPT[C2:graph summarization] AND CONCEPT[C5:attention mechanism])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training] OR CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training] OR CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `"distributed graph neural network training" AND "graph summarization" AND "leader-worker mode" AND "mini-batch training"`（springer；执行失败）
  - `"distributed graph neural network training" AND "graph summarization" AND "leader-worker mode" AND "mini-batch training"`（springer；执行失败）
- **NP-3**
  - `(abs:"graph stream partitioning" OR abs:"edge-based partitioning" OR abs:"graph partitioning algorithm") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"degree estimation") AND (abs:"min-heap" OR abs:"high-frequency node maintenance") AND (ti:"Sketch-DBH" OR ti:"DBH algorithm")`（arxiv；零命中）
  - `(abs:"graph stream partitioning" OR abs:"edge-based partitioning" OR abs:"graph partitioning algorithm") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"degree estimation") AND (ti:"Sketch-DBH" OR ti:"DBH algorithm")`（arxiv；零命中）
  - `(abs:"graph stream partitioning" OR abs:"edge-based partitioning" OR abs:"graph partitioning algorithm" OR abs:"stream graph partitioning" OR abs:"edge-cut partitioning") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"degree estimation" OR abs:"CMS" OR abs:"count-min sketch") AND (abs:"constant-time query" OR abs:"load balancing" OR abs:"subgraph assignment" OR abs:"O(1) query" OR abs:"balanced partitioning")`（arxiv；零命中）
  - `(abs:"graph stream partitioning" OR abs:"edge-based partitioning" OR abs:"graph partitioning algorithm" OR abs:"stream graph partitioning" OR abs:"edge-cut partitioning") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"degree estimation" OR abs:"CMS" OR abs:"count-min sketch")`（arxiv；零命中）
  - `(abs:"graph stream partitioning" OR abs:"edge-based partitioning" OR abs:"graph partitioning algorithm" OR abs:"stream graph partitioning" OR abs:"edge-cut partitioning") OR (abs:"constant-time query" OR abs:"load balancing" OR abs:"subgraph assignment" OR abs:"O(1) query" OR abs:"balanced partitioning")`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|edge-based partitioning|graph partitioning algorithm] AND CONCEPT[C2:Count-Min Sketch|probabilistic data structure|degree estimation] AND CONCEPT[C3:min-heap|high-frequency node maintenance] AND CONCEPT[C5:Sketch-DBH|DBH algorithm])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|edge-based partitioning|graph partitioning algorithm] AND CONCEPT[C2:Count-Min Sketch|probabilistic data structure|degree estimation] AND CONCEPT[C5:Sketch-DBH|DBH algorithm])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|edge-based partitioning|graph partitioning algorithm] AND CONCEPT[C2:Count-Min Sketch|probabilistic data structure|degree estimation] AND CONCEPT[C4:constant-time query|load balancing|subgraph assignment])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|edge-based partitioning|graph partitioning algorithm] AND CONCEPT[C2:Count-Min Sketch|probabilistic data structure|degree estimation])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|edge-based partitioning|graph partitioning algorithm] OR CONCEPT[C4:constant-time query|load balancing|subgraph assignment])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|edge-based partitioning|graph partitioning algorithm] OR CONCEPT[C4:constant-time query|load balancing|subgraph assignment])`（null_catalog；零命中）
  - `("graph stream partitioning" OR "edge-based partitioning" OR "graph partitioning algorithm") AND ("Count-Min Sketch" OR "probabilistic data structure" OR "degree estimation") AND ("min-heap" OR "high-frequency node maintenance") AND ("Sketch-DBH" OR "DBH algorithm")`（springer；执行失败）
  - `("graph stream partitioning" OR "edge-based partitioning" OR "graph partitioning algorithm") AND ("Count-Min Sketch" OR "probabilistic data structure" OR "degree estimation") AND ("min-heap" OR "high-frequency node maintenance") AND ("Sketch-DBH" OR "DBH algorithm")`（springer；执行失败）
  - `("graph stream partitioning" OR "edge-based partitioning" OR "graph partitioning algorithm") AND ("Count-Min Sketch" OR "probabilistic data structure" OR "degree estimation") AND ("min-heap" OR "high-frequency node maintenance") AND ("Sketch-DBH" OR "DBH algorithm")`（springer；执行失败）
  - `("graph stream partitioning" OR "edge-based partitioning" OR "graph partitioning algorithm") AND ("Count-Min Sketch" OR "probabilistic data structure" OR "degree estimation") AND ("min-heap" OR "high-frequency node maintenance") AND ("Sketch-DBH" OR "DBH algorithm")`（springer；执行失败）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 4 张原始证据卡；通过 4 张，拒绝 0 张。

### 6.2 相关文献

### card_10bf4a1cd67adae0cdc2f773 · DyGCN: Dynamic Graph Embedding with Graph Convolutional Network

- 查新点：NP-1
- 主要贡献：Proposes DyGCN, an efficient dynamic graph embedding approach that extends GCN-based methods to the dynamic setting by propagating changes along the graph to update node embeddings in a time-saving and performance-preserving way.
- 相关性：0.40
- 置信度：0.80
- 来源：
  - DyGCN: Dynamic Graph Embedding with Graph Convolutional Network：https://arxiv.org/pdf/2104.02962
    - 引文：we propose an efficient dynamic graph embedding approach, Dynamic Graph Convolutional Network (DyGCN), which is an extension of GCN-based methods.
    - 位置：artifact art_68763c9fc8e1a6822c68c6e7 chars:380-526

### card_f0704c5c4d7ebbf69043c5f2 · DyGSSM: Multi-view Dynamic Graph Embeddings with State Space Model Gradient Update

- 查新点：NP-1
- 主要贡献：Proposes DyGSSM, a multi-view dynamic graph embedding method that divides dynamic graphs into discrete snapshots and uses GCN plus random walk with Gated Recurrent Unit (GRU) for feature extraction in each snapshot, integrating local and global features via cross-attention and using an SSM based on HiPPO for long-term temporal dependencies.
- 相关性：0.60
- 置信度：0.80
- 来源：
  - DyGSSM: Multi-view Dynamic Graph Embeddings with State Space Model Gradient Update：https://arxiv.org/pdf/2505.09017
    - 引文：Most of the dynamic graph representation learning methods involve dividing a dynamic graph into discrete snapshots to capture the evolving behavior of nodes over time.
    - 位置：artifact art_4b536afdb5974c3b16f2016a chars:0-167
  - DyGSSM: Multi-view Dynamic Graph Embeddings with State Space Model Gradient Update：https://arxiv.org/pdf/2505.09017
    - 引文：Our approach combines Graph Convolution Networks (GCN) for local feature extraction and random walk with Gated Recurrent Unit (GRU) for global feature extraction in each snapshot.
    - 位置：artifact art_4b536afdb5974c3b16f2016a chars:1184-1363

### card_58c0e0c4a03fadb1bdde433f · Scaling R-GCN Training with Graph Summarization

- 查新点：NP-2
- 主要贡献：Proposes using graph summarization techniques to compress large graphs before training Relational Graph Convolutional Networks (R-GCN), reducing memory requirements and computational overhead, then transferring weights back to the original graph for inference.
- 相关性：0.50
- 置信度：0.80
- 来源：
  - Scaling R-GCN Training with Graph Summarization：10.1145/3487553.3524719
    - 引文：we experiment with the use of graph summarization techniques to compress the graph and hence reduce the amount of memory needed. After training the R-GCN on the graph summary, we transfer the weights back to the original graph and attempt to perform inference on it.
    - 位置：artifact art_5a95e23353233acf80dfb52a chars:265-531

### card_927caf724042beff967b2231 · Window-based Streaming Graph Partitioning Algorithm

- 查新点：NP-3
- 主要贡献：Proposes WStream, a window-based streaming graph partitioning algorithm that performs edge-cut partitioning to distribute vertices across partitions while keeping load balanced and communication (edge-cut) to a minimum.
- 相关性：0.70
- 置信度：0.80
- 来源：
  - Window-based Streaming Graph Partitioning Algorithm：10.1145/3290688.3290711
    - 引文：This paper proposes an efficient window-based streaming graph partitioning algorithm called WStream. The WStream algorithm is an edge-cut partitioning algorithm, which distributes a vertex among the partitions. Our results suggest that the WStream algorithm is able to partition large graph data efficiently while keeping the load balanced across different partitions, and communication to a minimum.
    - 位置：artifact art_044b624240993e16c40f3537 chars:713-1113
  - Window-based Streaming Graph Partitioning Algorithm：10.1145/3290688.3290711
    - 引文：The key idea of this algorithm is that the window-based stream of graph data has more information on vertex allocation because usual single-pass graph partitioning only uses the presence of a vertex to determine the partition for that vertex.
    - 位置：artifact art_239d9f203a9c73612f1cbbaa chars:5808-6050

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 2 | 有证据 |
| NP-2 | 1 | 有证据 |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图压缩为固定规模的新图，解决GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - wrk_722f08a590cd28a5b4a37fb9：该文献与查新点总体目标（动态/时序图表示学习）部分重合，但采用传播式增量更新机制，未覆盖图摘要、图自编码器、RNN等声称特征，属于部分相关文献。 (cards: card_10bf4a1cd67adae0cdc2f773)
  - wrk_308a5e5dbf0375b348f9a095：DyGSSM 与查新点共享快照序列建模和 RNN 时序特征学习两个特征，但未采用图摘要压缩和图自编码器重构训练，属于部分相关文献，用于确认查新点核心特征未被覆盖。 (cards: card_f0704c5c4d7ebbf69043c5f2)

### NP-2 · 证据不足，无法裁定

提出基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，领导节点负责图划分与模型同步更新，工作节点基于图摘要技术进行小批量训练，并通过注意力层返回结果。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - wrk_69b3cecda02343b983f9dbc2：该文献与DSGNN在'基于图摘要压缩图后进行GNN训练'特征上部分重合，但为单机训练，未采用分布式领导-工作者模式、注意力层聚合或边分割图流划分，属于部分相关文献，不构成对完整查新点的预见。 (cards: card_58c0e0c4a03fadb1bdde433f)

### NP-3 · 证据不足，无法裁定

提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch概率数据结构存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间查询和负载均衡的子图划分。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - wrk_dd602dc2d2b07d7e69e6724c：同为图流划分算法且采用边割策略并追求负载均衡，与查新点在一般图流划分和负载均衡目标上重合，但未采用 Count-Min Sketch、最小堆及常数时间查询等核心技术特征，属于部分相关基线文献。 (cards: card_927caf724042beff967b2231)

---

## 八、报告局限

- 本次检索覆盖范围未知：未提供各来源的实际检索执行状态，无法确认是否所有必要来源均已成功检索。以下结论仅基于现有证据卡片。
- 检索获得了候选文献，但现有证据卡片与查新点仅部分重合，未达到支持新颖性判定的有效门槛，属于有命中但未形成有效证据的情形。当前裁定要求进一步核验原文本中的关键特征，以确认未采用特征的真实性。
- 未被任何被拒绝证据（rejected_evidence 为空），因此无需额外说明证据门控的拒绝原因。

---

## 九、附件及参考信息

### 缺失参考文献

无。

### 缺失 Baseline

无。

### 引用问题

- Reviewer 在多个查新点上指出，裁定依赖文献未采用特征的断言，但现有引文摘要未直接支持该否定，需核验原文。建议核验 DyGCN、DyGSSM、Scaling R-GCN Training with Graph Summarization、WStream 等文献的完整内容。

### 被拒绝证据

无。

### 检索到的文献

- DGC: Training Dynamic Graphs with Spatio-Temporal Non-Uniformity using Graph Partitioning by Chunks：[https://arxiv.org/pdf/2309.03523](https://arxiv.org/pdf/2309.03523)
- Finding a Concise, Precise, and Exhaustive Set of Near Bi-Cliques in Dynamic Graphs：[https://arxiv.org/pdf/2110.14875](https://arxiv.org/pdf/2110.14875)
- K-Core based Temporal Graph Convolutional Network for Dynamic Graphs：[https://arxiv.org/pdf/2003.09902](https://arxiv.org/pdf/2003.09902)
- DyGCN: Dynamic Graph Embedding with Graph Convolutional Network：[https://arxiv.org/pdf/2104.02962](https://arxiv.org/pdf/2104.02962)
- Temporal Graph Representation Learning with Adaptive Augmentation Contrastive：[https://arxiv.org/pdf/2311.03897](https://arxiv.org/pdf/2311.03897)
- Local Intrinsic Dimensionality for Dynamic Graph Embeddings：[https://arxiv.org/pdf/2411.16145](https://arxiv.org/pdf/2411.16145)
- Towards Real-Time Temporal Graph Learning：[https://arxiv.org/pdf/2210.04114](https://arxiv.org/pdf/2210.04114)
- DyGSSM: Multi-view Dynamic Graph Embeddings with State Space Model Gradient Update：[https://arxiv.org/pdf/2505.09017](https://arxiv.org/pdf/2505.09017)
- Parallax: Sparsity-aware Data Parallel Training of Deep Neural Networks：[https://arxiv.org/pdf/1808.02621](https://arxiv.org/pdf/1808.02621)
- MergeComp: A Compression Scheduler for Scalable Communication-Efficient Distributed Training：[https://arxiv.org/pdf/2103.15195](https://arxiv.org/pdf/2103.15195)
- Is Network the Bottleneck of Distributed Training?：[https://arxiv.org/pdf/2006.10103](https://arxiv.org/pdf/2006.10103)
- Scalable Training of Language Models using JAX pjit and TPUv4：[https://arxiv.org/pdf/2204.06514](https://arxiv.org/pdf/2204.06514)
- Optimizing DNN Compilation for Distributed Training with Joint OP and Tensor Fusion：[https://arxiv.org/pdf/2209.12769](https://arxiv.org/pdf/2209.12769)
- PGT-I: Scaling Spatiotemporal GNNs with Memory-Efficient Distributed Training：[https://arxiv.org/pdf/2507.11683](https://arxiv.org/pdf/2507.11683)
- TTrace: Lightweight Error Checking and Diagnosis for Distributed Training：[https://arxiv.org/pdf/2506.09280](https://arxiv.org/pdf/2506.09280)
- ModTrans: Translating Real-world Models for Distributed Training Simulator：[https://arxiv.org/pdf/2604.01607](https://arxiv.org/pdf/2604.01607)
- Window-based Streaming Graph Partitioning Algorithm：[https://arxiv.org/pdf/1902.01543](https://arxiv.org/pdf/1902.01543)
- GLISP: A Scalable GNN Learning System by Exploiting Inherent Structural Properties of Graphs：[https://arxiv.org/pdf/2401.03114](https://arxiv.org/pdf/2401.03114)
- Evolutionary Acyclic Graph Partitioning：[https://arxiv.org/pdf/1709.08563](https://arxiv.org/pdf/1709.08563)
- Scalable Multi-GPU Simulation of 3D Multicellular Growth with RNN-Based Workload Balancing：[https://arxiv.org/pdf/2608.25890](https://arxiv.org/pdf/2608.25890)
- Cost Characterization of Vertically Partitioned Federated Knowledge Graphs：[https://arxiv.org/pdf/2609.13664](https://arxiv.org/pdf/2609.13664)
- Probabilistic Stability of Traffic Load Balancing on Wireless Complex Networks：[https://arxiv.org/pdf/1810.07370](https://arxiv.org/pdf/1810.07370)
- A Programming Model for GPU Load Balancing：[https://arxiv.org/pdf/2301.04792](https://arxiv.org/pdf/2301.04792)
- Loom: Query-aware Partitioning of Online Graphs：[https://arxiv.org/pdf/1711.06608](https://arxiv.org/pdf/1711.06608)
- Temporal Graph Classification Based on Fast and Exact Transitive Reduction Strategy：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37673-2_25](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37673-2_25)
- Part-GNN: A Partitioning-Based Graph Neural Network for Efficient Memory Large Scale Data Classification：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-2597-2_39](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-2597-2_39)
- Enhancing 3D shape recognition with multi-view relational transformer networks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00371-026-04716-3](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00371-026-04716-3)
- A line graph-based metric learning framework for robust link prediction in complex networks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-026-08645-9](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11227-026-08645-9)
- Adaptive competitive balance regulation in professional sports leagues via graph attention networks and proximal policy optimization：[https://www.nature.com/articles/s41598-026-57715-8.pdf](https://www.nature.com/articles/s41598-026-57715-8.pdf)
- Collaborative APT detection through cloud-edge synergy of graph transformer and lightweight clustering：[https://www.biomedcentral.com/openurl/pdf?id=doi:10.1186/s13677-026-00940-3](https://www.biomedcentral.com/openurl/pdf?id=doi:10.1186/s13677-026-00940-3)
- Interpretable graph-based models on multimodal biomedical data integration: a technical review and benchmarking：[https://www.nature.com/articles/s41467-026-74126-5.pdf](https://www.nature.com/articles/s41467-026-74126-5.pdf)
- Networked data science: a unified network modeling framework：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s10115-026-02784-4](http://link.springer.com/openurl/pdf?id=doi:10.1007/s10115-026-02784-4)
- Scaling R-GCN Training with Graph Summarization：[https://arxiv.org/pdf/2203.02622](https://arxiv.org/pdf/2203.02622)
- Utility-Based Graph Summarization: New and Improved：[https://arxiv.org/pdf/2006.08949](https://arxiv.org/pdf/2006.08949)
- Graph Summarization with Graph Neural Networks：[https://arxiv.org/pdf/2203.05919](https://arxiv.org/pdf/2203.05919)
- FLUID: A Common Model for Semantic Structural Graph Summaries Based on Equivalence Relations：[https://arxiv.org/pdf/1908.01528](https://arxiv.org/pdf/1908.01528)
- Distributed Graph Neural Network Training: A Survey：[https://arxiv.org/pdf/2211.00216](https://arxiv.org/pdf/2211.00216)
- A Comprehensive Survey on Distributed Training of Graph Neural Networks：[https://arxiv.org/pdf/2211.05368](https://arxiv.org/pdf/2211.05368)
- Scalable Neural Network Training over Distributed Graphs：[https://arxiv.org/pdf/2302.13053](https://arxiv.org/pdf/2302.13053)
- Heta: Distributed Training of Heterogeneous Graph Neural Networks：[https://arxiv.org/pdf/2408.09697](https://arxiv.org/pdf/2408.09697)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
