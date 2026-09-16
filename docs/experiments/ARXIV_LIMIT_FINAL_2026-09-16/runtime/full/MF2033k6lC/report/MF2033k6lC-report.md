# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T12:32:21+08:00 |
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

- 提出一种基于图摘要技术的大规模时序图表示学习方法GSAERU，通过图摘要压缩原图并输入图自编码器学习节点表征，再利用循环神经网络建模时间维度依赖，显著降低内存消耗和训练时间。
- 提出基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，通过基于边分割的图流划分算法分配子图，工作节点基于图摘要进行小批量训练，并通过注意力层将结果返回给领导节点，领导节点汇总后计算梯度并同步更新模型，加速训练并提升链路预测性能。
- 提出一种基于边分割的图流划分算法，用于分布式图神经网络训练中的子图划分，由领导节点执行，能够针对大规模图流数据进行高效划分。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要技术的大规模时序图表示学习方法GSAERU，通过图摘要压缩原图并输入图自编码器学习节点表征，再利用循环神经网络建模时间维度依赖，显著降低内存消耗和训练时间。 | Propose a large-scale sequential graph representation learning method GSAERU based on graph summarization, which compresses the original graph via graph summarization, inputs the compressed graph into a graph autoencoder to learn node representations, and then uses a recurrent neural network to model temporal dependencies, significantly reducing memory consumption and training time. |
| NP-2 | 提出基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，通过基于边分割的图流划分算法分配子图，工作节点基于图摘要进行小批量训练，并通过注意力层将结果返回给领导节点，领导节点汇总后计算梯度并同步更新模型，加速训练并提升链路预测性能。 | Propose a distributed graph neural network optimization training algorithm DSGNN based on graph summarization, which adopts the leader-worker mode, distributes subgraphs via a graph flow partition algorithm based on edge segmentation, workers perform mini-batch training based on graph summarization and return results to the leader through an attention layer, the leader aggregates results to compute gradients and synchronously updates all models, accelerating training and improving link prediction performance. |
| NP-3 | 提出一种基于边分割的图流划分算法，用于分布式图神经网络训练中的子图划分，由领导节点执行，能够针对大规模图流数据进行高效划分。 | Propose a graph flow partition algorithm based on edge segmentation, which is used for subgraph partitioning in distributed graph neural network training, executed by the leader node, capable of efficiently partitioning large-scale graph streaming data. |

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
  - `(ti:"large-scale sequential graph" OR ti:"dynamic graph" OR ti:"temporal graph") AND (abs:"graph summarization" OR abs:"graph compression") AND (abs:"graph autoencoder" OR abs:"graph representation learning") AND (abs:"recurrent neural network" OR abs:"temporal dependency modeling")`（arxiv；零命中）
  - `(ti:"large-scale sequential graph" OR ti:"dynamic graph" OR ti:"temporal graph") AND (abs:"graph summarization" OR abs:"graph compression") AND (abs:"graph autoencoder" OR abs:"graph representation learning")`（arxiv；零命中）
  - `(ti:"large-scale sequential graph" OR ti:"dynamic graph" OR ti:"temporal graph" OR ti:"dynamic networks" OR ti:"time-evolving graphs") AND (abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening" OR abs:"graph reduction") AND (abs:"graph autoencoder" OR abs:"graph representation learning" OR abs:"graph neural network" OR abs:"node embedding")`（arxiv；有命中）
  - `(ti:"large-scale sequential graph" OR ti:"dynamic graph" OR ti:"temporal graph" OR ti:"dynamic networks" OR ti:"time-evolving graphs") OR (abs:"graph autoencoder" OR abs:"graph representation learning" OR abs:"graph neural network" OR abs:"node embedding")`（arxiv；部分成功）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
- **NP-3**
  - `(abs:graph AND abs:flow AND abs:partition AND abs:algorithm OR abs:edge AND abs:segmentation AND abs:based AND abs:partitioning) AND ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training`（arxiv；零命中）
  - `(abs:graph AND abs:flow AND abs:partition AND abs:algorithm OR abs:edge AND abs:segmentation AND abs:based AND abs:partitioning)`（arxiv；零命中）
  - `(abs:graph AND abs:flow AND abs:partition AND abs:algorithm OR abs:edge AND abs:segmentation AND abs:based AND abs:partitioning OR abs:"edge-based graph partitioning" OR abs:"streaming graph partition") AND (ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"distributed graph learning") AND (abs:large-scale AND abs:graph AND abs:streaming AND abs:data OR abs:"streaming graphs" OR abs:"graph streams")`（arxiv；零命中）
  - `(abs:graph AND abs:flow AND abs:partition AND abs:algorithm OR abs:edge AND abs:segmentation AND abs:based AND abs:partitioning OR abs:"edge-based graph partitioning" OR abs:"streaming graph partition") AND (ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"distributed graph learning")`（arxiv；零命中）
  - `(abs:graph AND abs:flow AND abs:partition AND abs:algorithm OR abs:edge AND abs:segmentation AND abs:based AND abs:partitioning OR abs:"edge-based graph partitioning" OR abs:"streaming graph partition") OR (ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"distributed graph learning") OR (abs:large-scale AND abs:graph AND abs:streaming AND abs:data OR abs:"streaming graphs" OR abs:"graph streams") OR (abs:"leader node" OR abs:"subgraph assignment" OR abs:"worker nodes" OR abs:"coordinator node" OR abs:"master node")`（arxiv；零命中）
  - `(abs:graph AND abs:flow AND abs:partition AND abs:algorithm OR abs:edge AND abs:segmentation AND abs:based AND abs:partitioning OR abs:"edge-based graph partitioning" OR abs:"streaming graph partition") OR (ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"distributed graph learning") OR (abs:large-scale AND abs:graph AND abs:streaming AND abs:data OR abs:"streaming graphs" OR abs:"graph streams") OR (abs:"leader node" OR abs:"subgraph assignment" OR abs:"worker nodes" OR abs:"coordinator node" OR abs:"master node")`（arxiv；零命中）
  - `(abs:"edge segmentation" OR abs:"edge partitioning" OR abs:"edge-cut partitioning") AND (ti:"graph stream partitioning" OR ti:"graph streaming partitioning" OR ti:"streaming graph partition") AND (abs:distributed AND abs:graph AND abs:neural AND abs:network AND abs:training OR abs:"distributed GNN training")`（arxiv；零命中）
  - `(abs:"edge segmentation" OR abs:"edge partitioning" OR abs:"edge-cut partitioning") AND (ti:"graph stream partitioning" OR ti:"graph streaming partitioning" OR ti:"streaming graph partition")`（arxiv；有命中）
  - `(abs:"edge segmentation" OR abs:"edge partitioning" OR abs:"edge-cut partitioning" OR abs:"edge-based partitioning" OR abs:"edge splitting") AND (ti:"graph stream partitioning" OR ti:"graph streaming partitioning" OR ti:"streaming graph partition" OR ti:"graph stream partition" OR ti:"streaming graph partitioning") AND (abs:distributed AND abs:graph AND abs:neural AND abs:network AND abs:training OR abs:"distributed GNN training" OR abs:distributed AND abs:graph AND abs:neural AND abs:network OR abs:"distributed GNN") AND (abs:"subgraph partitioning" OR abs:"subgraph partition" OR abs:"subgraph division" OR abs:"subgraph assignment")`（arxiv；零命中）
  - `(abs:"edge segmentation" OR abs:"edge partitioning" OR abs:"edge-cut partitioning" OR abs:"edge-based partitioning" OR abs:"edge splitting") AND (ti:"graph stream partitioning" OR ti:"graph streaming partitioning" OR ti:"streaming graph partition" OR ti:"graph stream partition" OR ti:"streaming graph partitioning") AND (abs:"subgraph partitioning" OR abs:"subgraph partition" OR abs:"subgraph division" OR abs:"subgraph assignment")`（arxiv；零命中）
  - `(abs:"edge segmentation" OR abs:"edge partitioning" OR abs:"edge-cut partitioning" OR abs:"edge-based partitioning" OR abs:"edge splitting") OR (ti:"graph stream partitioning" OR ti:"graph streaming partitioning" OR ti:"streaming graph partition" OR ti:"graph stream partition" OR ti:"streaming graph partitioning") OR (abs:distributed AND abs:graph AND abs:neural AND abs:network AND abs:training OR abs:"distributed GNN training" OR abs:distributed AND abs:graph AND abs:neural AND abs:network OR abs:"distributed GNN") OR (abs:"subgraph partitioning" OR abs:"subgraph partition" OR abs:"subgraph division" OR abs:"subgraph assignment") OR (abs:"leader node" OR abs:"coordinator node" OR abs:"master node" OR abs:"central node") OR (ti:large-scale AND ti:graph AND ti:streaming AND ti:data OR ti:"large-scale graph stream" OR ti:"big graph stream" OR ti:"massive graph streaming")`（arxiv；执行失败）
  - `(abs:"edge segmentation" OR abs:"edge partitioning" OR abs:"edge-cut partitioning") AND (ti:"graph stream partitioning" OR ti:"graph streaming partitioning" OR ti:"streaming graph partition") AND (abs:distributed AND abs:graph AND abs:neural AND abs:network AND abs:training OR abs:"distributed GNN training")`（arxiv；零命中）
  - `(abs:"edge segmentation" OR abs:"edge partitioning" OR abs:"edge-cut partitioning") AND (ti:"graph stream partitioning" OR ti:"graph streaming partitioning" OR ti:"streaming graph partition")`（arxiv；有命中）
  - `(abs:"edge segmentation" OR abs:"edge partitioning" OR abs:"edge-cut partitioning" OR abs:"edge-based partitioning" OR abs:"edge splitting") AND (ti:"graph stream partitioning" OR ti:"graph streaming partitioning" OR ti:"streaming graph partition" OR ti:"graph stream partition" OR ti:"streaming graph partitioning") AND (abs:distributed AND abs:graph AND abs:neural AND abs:network AND abs:training OR abs:"distributed GNN training" OR abs:distributed AND abs:graph AND abs:neural AND abs:network OR abs:"distributed GNN") AND (abs:"subgraph partitioning" OR abs:"subgraph partition" OR abs:"subgraph division" OR abs:"subgraph assignment")`（arxiv；零命中）
  - `(abs:"edge segmentation" OR abs:"edge partitioning" OR abs:"edge-cut partitioning" OR abs:"edge-based partitioning" OR abs:"edge splitting") AND (ti:"graph stream partitioning" OR ti:"graph streaming partitioning" OR ti:"streaming graph partition" OR ti:"graph stream partition" OR ti:"streaming graph partitioning") AND (abs:"subgraph partitioning" OR abs:"subgraph partition" OR abs:"subgraph division" OR abs:"subgraph assignment")`（arxiv；零命中）
  - `(abs:"edge segmentation" OR abs:"edge partitioning" OR abs:"edge-cut partitioning" OR abs:"edge-based partitioning" OR abs:"edge splitting") OR (ti:"graph stream partitioning" OR ti:"graph streaming partitioning" OR ti:"streaming graph partition" OR ti:"graph stream partition" OR ti:"streaming graph partitioning") OR (abs:distributed AND abs:graph AND abs:neural AND abs:network AND abs:training OR abs:"distributed GNN training" OR abs:distributed AND abs:graph AND abs:neural AND abs:network OR abs:"distributed GNN") OR (abs:"subgraph partitioning" OR abs:"subgraph partition" OR abs:"subgraph division" OR abs:"subgraph assignment") OR (abs:"leader node" OR abs:"coordinator node" OR abs:"master node" OR abs:"central node") OR (ti:large-scale AND ti:graph AND ti:streaming AND ti:data OR ti:"large-scale graph stream" OR ti:"big graph stream" OR ti:"massive graph streaming")`（arxiv；执行失败）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 3 张原始证据卡；通过 3 张，拒绝 0 张。

### 6.2 相关文献

### card_7a049fd9d35cd2e205956ff7 · DGC: Training Dynamic Graphs with Spatio-Temporal Non-Uniformity using Graph Partitioning by Chunks

- 查新点：NP-1
- 主要贡献：DGC proposes a distributed DGNN training system that partitions dynamic graphs into chunks using graph coarsening, modeling dynamic graphs as snapshots with structure encoders (GCN) and time encoders (RNN/GRU), achieving significant training speedup.
- 相关性：0.60
- 置信度：0.70
- 来源：
  - DGC: Training Dynamic Graphs with Spatio-Temporal Non-Uniformity using Graph Partitioning by Chunks：https://arxiv.org/pdf/2309.03523
    - 引文：a dynamic graph is divided into a number of snapshots, each of which represents the graph at a specific time. These snapshots are fed to structure encoders (e.g., GCN), respectively, followed by time encoders (e.g., RNN) to exploit temporal relationship across snapshots.
    - 位置：artifact art_2b963a61ae0d71cc1b4c5842 chars:4781-5052
  - DGC: Training Dynamic Graphs with Spatio-Temporal Non-Uniformity using Graph Partitioning by Chunks：https://arxiv.org/pdf/2309.03523
    - 引文：This partitioning algorithm is based on graph coarsening, which can run very fast on large graphs.
    - 位置：artifact art_1858acd5aca7680aec2f1bc7 chars:1124-1222
  - DGC: Training Dynamic Graphs with Spatio-Temporal Non-Uniformity using Graph Partitioning by Chunks：https://arxiv.org/pdf/2309.03523
    - 引文：T-GCN (Zhao et al., 2019) uses three 2-layer GCN (Kipf and Welling, 2016) as the structure encoder, and a 1-layer GRU (Cho et al., 2014) model as the time encoder.
    - 位置：artifact art_2b963a61ae0d71cc1b4c5842 chars:14204-14367

### card_0bbbbd9ffac0fc04893533cb · AGL: a Scalable System for Industrial-purpose Graph Machine Learning

- 查新点：NP-2
- 主要贡献：AGL is a scalable, fault-tolerant, and integrated system for distributed GNN training and inference, using parameter servers and k-hop neighborhood subgraphs to achieve data independence for training.
- 相关性：0.40
- 置信度：0.70
- 来源：
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：we design AGL, a scalable, fault-tolerance and integrated system, with fully-functional training and inference for GNNs
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1021-1140
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：we simply do the training on parameter servers due to data independency
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1562-1633

### card_ede76afb2b96bb4d6c8f2297 · Window-based Streaming Graph Partitioning Algorithm

- 查新点：NP-3
- 主要贡献：Proposes WStream, a window-based streaming graph partitioning algorithm that uses edge-cut partitioning to partition large graph data efficiently while balancing load across partitions and minimizing communication.
- 相关性：0.50
- 置信度：0.60
- 来源：
  - Window-based Streaming Graph Partitioning Algorithm：10.1145/3290688.3290711
    - 引文：This paper proposes an efficient window-based streaming graph partitioning algorithm called WStream. The WStream algorithm is an edge-cut partitioning algorithm, which distributes a vertex among the partitions.
    - 位置：artifact art_044b624240993e16c40f3537 chars:713-923
  - Window-based Streaming Graph Partitioning Algorithm：10.1145/3290688.3290711
    - 引文：Our results suggest that the WStream algorithm is able to partition large graph data efficiently while keeping the load balanced across different partitions, and communication to a minimum.
    - 位置：artifact art_044b624240993e16c40f3537 chars:924-1113

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 1 | 有证据 |
| NP-2 | 1 | 有证据 |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 部分新颖

提出一种基于图摘要技术的大规模时序图表示学习方法GSAERU，通过图摘要压缩原图并输入图自编码器学习节点表征，再利用循环神经网络建模时间维度依赖，显著降低内存消耗和训练时间。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 现有单篇文献DGC（wrk_820bea3aec0826aa27db0b5a）覆盖了特征1（动态图建模为快照序列）、特征2（图粗化/图摘要压缩快照）和特征4（RNN时间建模），但未采用图自编码器及以原图重构误差训练节点表征（特征3缺失）。因此该文献为部分相关，不构成对完整技术组合的公开。需补充检索同一组合的文献。  
**置信度：** 0.72  
**报告摘要：** 本查新点提出GSAERU模型，融合图摘要压缩、图自编码器重构训练和RNN时序建模。根据有效证据，现有文献DGC覆盖了动态图快照建模、图粗化（摘要）和RNN时间建模，但未采用图自编码器及重构误差训练，因此仅部分重叠，核心组合特征未被单篇公开，判定为部分新颖。  
**高度相关 Work：**
  - wrk_820bea3aec0826aa27db0b5a：覆盖特征1/2/4，但未采用图自编码器+重构误差训练节点表征（特征3缺失），为部分相关文献。 (cards: card_7a049fd9d35cd2e205956ff7)

### NP-2 · 部分新颖

提出基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，通过基于边分割的图流划分算法分配子图，工作节点基于图摘要进行小批量训练，并通过注意力层将结果返回给领导节点，领导节点汇总后计算梯度并同步更新模型，加速训练并提升链路预测性能。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 已核验单篇文献（AGL）与查新点部分重叠：同为分布式GNN训练系统，且训练在服务器上完成（对应同步更新模型目标）。但AGL采用参数服务器架构而非领导-工作者模式，使用k-hop邻域子图而非基于边分割的图流划分算法，小批量训练基于信息完备子图而非图摘要技术，未使用注意力层返回结果，且未涉及链路预测性能提升。因此AGL仅覆盖宽泛的分布式GNN训练特征，未覆盖查新点的核心组合特征（图摘要+注意力层+边分割图流划分+领导-工作者+链路预测），属于部分相关基线文献。由于仅核验单篇文献，且该文献未公开上述核心组合，不足以否定组合特征的新颖性，亦不能据此判定完全新颖。综合当前证据，判定为部分新颖，需进一步检索验证组合特征是否完整公开。  
**置信度：** 0.60  
**报告摘要：** 本查新点提出DSGNN框架，结合领导-工作者模式、边分割图流划分、图摘要小批量训练、注意力层结果聚合与同步梯度更新。有效证据中的AGL为分布式GNN训练系统，但架构与核心机制（领导-工作者、图摘要、注意力层、边分割划分、链路预测优化）均不相同，仅部分重叠，判定为部分新颖。  
**高度相关 Work：**
  - wrk_ff5aa18cf0cfe7be1ba5e8bd：分布式GNN训练系统，与查新点目标部分重叠，但架构（参数服务器、k-hop子图）与查新点组合特征（领导-工作者、边分割图流划分、图摘要、注意力层返回、链路预测）均不同，属部分相关基线文献。 (cards: card_0bbbbd9ffac0fc04893533cb)

### NP-3 · 部分新颖

提出一种基于边分割的图流划分算法，用于分布式图神经网络训练中的子图划分，由领导节点执行，能够针对大规模图流数据进行高效划分。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 单卡核验显示，WStream（wrk_dd602dc2d2b07d7e69e6724c）为部分相关文献：它针对大规模图流、基于edge-cut划分、由central graph loader分发，与查新点的'边分割+领导节点+大规模图流'部分重叠，但该算法面向通用图应用而非分布式GNN训练，且采用顶点式划分而非边分割，未明确由领导节点执行，因此未覆盖完整技术组合。多篇文献分别公开部分特征，但未发现单篇公开完整组合，故不能据此否定新颖性。该文献仅构成背景近似，需保留为部分相关。  
**置信度：** 0.55  
**报告摘要：** 本查新点提出基于边分割的图流划分算法，用于分布式GNN训练中的子图分配。有效证据WStream为大规模图流edge-cut划分算法，但面向通用图应用且采用顶点式划分，未明确由领导节点执行，未覆盖边分割+领导节点+GNN训练的组合，判定为部分新颖。  
**高度相关 Work：**
  - wrk_dd602dc2d2b07d7e69e6724c：基于边（edge-cut）的大规模图流划分算法，涉及中央/领导节点分发与负载均衡，与查新点部分重叠；但面向通用图应用且采用顶点式划分，未覆盖边分割+领导节点+GNN训练的组合。 (cards: card_ede76afb2b96bb4d6c8f2297)

---

## 八、报告局限

- 检索覆盖事实未提供：本次查新未包含明确的检索来源执行细节，因此无法确认检索是否覆盖了所有必要数据库，检索覆盖完整性未知，现有结论仅基于已获得的EvidenceCard作出。
- 已获得部分相关证据但未形成完整覆盖：针对NP-1、NP-2、NP-3，均检索到部分重叠文献，但未发现公开完整技术组合的证据，故Reviewer判定为部分新颖并请求补充检索。此情形不属于检索成功零命中，也不属于检索失败。
- 所有EvidenceCard均通过证据门控，无被拒绝证据，因此未涉及技术性质疑或格式性拒绝。

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

- Graph-Adaptive Horseshoe for Compositional Regression：[https://arxiv.org/pdf/2608.17858](https://arxiv.org/pdf/2608.17858)
- CGS: Configurable Graph Summarization with Bounded Neighborhood Loss and Query Support：[https://arxiv.org/pdf/2607.10969](https://arxiv.org/pdf/2607.10969)
- COREKG: Coreset-Guided Personalized Summarization of Knowledge Graphs：[https://arxiv.org/pdf/2605.14900](https://arxiv.org/pdf/2605.14900)
- Spectral Model eXplainer: a chemically-grounded explainability framework for spectral-based machine learning models：[https://arxiv.org/pdf/2605.02684](https://arxiv.org/pdf/2605.02684)
- A Null Model for Mapper Subtype Claims：[https://arxiv.org/pdf/2604.17395](https://arxiv.org/pdf/2604.17395)
- Explainable Mapper: Charting LLM Embedding Spaces Using Perturbation-Based Explanation and Verification Agents：[https://arxiv.org/pdf/2507.18607](https://arxiv.org/pdf/2507.18607)
- Causal DAG Summarization (Full Version)：[https://arxiv.org/pdf/2504.14937](https://arxiv.org/pdf/2504.14937)
- Code-Craft: Hierarchical Graph-Based Code Summarization for Enhanced Context Retrieval：[https://arxiv.org/pdf/2504.08975](https://arxiv.org/pdf/2504.08975)
- DGC: Training Dynamic Graphs with Spatio-Temporal Non-Uniformity using Graph Partitioning by Chunks：[https://arxiv.org/pdf/2309.03523](https://arxiv.org/pdf/2309.03523)
- Transformer-Based Token Fusion and Dynamic Graph Planning for Audio-Visual Navigation：[https://arxiv.org/pdf/2609.17421](https://arxiv.org/pdf/2609.17421)
- SEMA-GUARD: Semantic and Graph-Based Vulnerability Detection in Assembly Code：[https://arxiv.org/pdf/2609.17254](https://arxiv.org/pdf/2609.17254)
- Intervention problems in the Linear Threshold Model: A general formulation and new results：[https://arxiv.org/pdf/2609.17146](https://arxiv.org/pdf/2609.17146)
- Repurposing Unified Topological Signatures for Graph Representation Learning：[https://arxiv.org/pdf/2609.17061](https://arxiv.org/pdf/2609.17061)
- Structural Negative Transfer in Federated Graph Neural Networks: Diagnosis, Causal Investigation, and the Limits of Divergence-Aware Mitigation：[https://arxiv.org/pdf/2609.16977](https://arxiv.org/pdf/2609.16977)
- Unified Heterogeneous Graph Neural Network solver for Power Flow, Optimal Power Flow and State Estimation：[https://arxiv.org/pdf/2609.16738](https://arxiv.org/pdf/2609.16738)
- ReliGRec: Reliability-Oriented LLM-Based Generative Recommendation via User-Risk-Aware Prompt Routing：[https://arxiv.org/pdf/2609.16560](https://arxiv.org/pdf/2609.16560)
- Window-based Streaming Graph Partitioning Algorithm：[https://arxiv.org/pdf/1902.01543](https://arxiv.org/pdf/1902.01543)
- AGL: a Scalable System for Industrial-purpose Graph Machine Learning：[https://arxiv.org/pdf/2003.02454](https://arxiv.org/pdf/2003.02454)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
