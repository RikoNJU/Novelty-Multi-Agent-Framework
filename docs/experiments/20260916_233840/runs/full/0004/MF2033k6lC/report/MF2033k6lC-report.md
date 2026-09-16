# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T23:17:54+08:00 |
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
- 提出基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，领导节点负责图划分与参数同步更新，工作者节点基于图摘要进行小批量训练，并通过注意力层返回结果。
- 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch概率数据结构存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图压缩为固定规模的新图，解决GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。 | Propose a large-scale sequential graph representation learning method GSAERU based on graph summarization, which compresses dynamic sequential graphs into fixed-size new graphs via graph summarization, addressing the issue that GNN outputs cannot be directly fed into RNN, and uses graph autoencoder and recurrent neural network to learn temporal features. |
| NP-2 | 提出基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，领导节点负责图划分与参数同步更新，工作者节点基于图摘要进行小批量训练，并通过注意力层返回结果。 | Propose a distributed graph neural network optimization training framework DSGNN based on graph summarization, adopting a leader-worker mode where the leader handles graph partitioning and synchronous parameter updates, and workers perform mini-batch training based on graph summarization and return results via an attention layer. |
| NP-3 | 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch概率数据结构存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。 | Propose an edge-segmentation-based graph stream partitioning algorithm Sketch-DBH, which uses Count-Min Sketch probabilistic data structure to store node degree information and a min-heap to maintain high-frequency node information, enabling constant-time query results and generating subgraph IDs, ensuring load balancing. |

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
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening") AND (ti:"sequential graph" OR ti:"dynamic graph" OR ti:"temporal graph") AND (abs:"graph autoencoder" OR abs:"graph representation learning") AND (abs:"recurrent neural network" OR abs:"temporal feature learning")`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening") AND (ti:"sequential graph" OR ti:"dynamic graph" OR ti:"temporal graph") AND (abs:"graph autoencoder" OR abs:"graph representation learning")`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening" OR abs:"graph summary" OR abs:"graph reduction") AND (ti:"sequential graph" OR ti:"dynamic graph" OR ti:"temporal graph" OR ti:"time-evolving graph" OR ti:"graph sequence") AND (abs:"graph autoencoder" OR abs:"graph representation learning" OR abs:"graph neural network" OR abs:"GNN")`（arxiv；有命中）
  - `(ti:"sequential graph" OR ti:"dynamic graph" OR ti:"temporal graph" OR ti:"time-evolving graph" OR ti:"graph sequence") OR (abs:"graph autoencoder" OR abs:"graph representation learning" OR abs:"graph neural network" OR abs:"GNN") OR (abs:"recurrent neural network" OR abs:"temporal feature learning" OR abs:"RNN" OR abs:"sequence learning")`（arxiv；部分成功）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening") AND (ti:"sequential graph" OR ti:"dynamic graph" OR ti:"temporal graph") AND (abs:"graph autoencoder" OR abs:"graph representation learning") AND (abs:"recurrent neural network" OR abs:"temporal feature learning")`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening") AND (ti:"sequential graph" OR ti:"dynamic graph" OR ti:"temporal graph") AND (abs:"graph autoencoder" OR abs:"graph representation learning")`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening" OR abs:"graph summary" OR abs:"graph reduction") AND (ti:"sequential graph" OR ti:"dynamic graph" OR ti:"temporal graph" OR ti:"time-evolving graph" OR ti:"graph sequence") AND (abs:"graph autoencoder" OR abs:"graph representation learning" OR abs:"graph neural network" OR abs:"GNN")`（arxiv；有命中）
  - `(ti:"sequential graph" OR ti:"dynamic graph" OR ti:"temporal graph" OR ti:"time-evolving graph" OR ti:"graph sequence") OR (abs:"graph autoencoder" OR abs:"graph representation learning" OR abs:"graph neural network" OR abs:"GNN") OR (abs:"recurrent neural network" OR abs:"temporal feature learning" OR abs:"RNN" OR abs:"sequence learning")`（arxiv；部分成功）
  - `("graph summarization" OR "graph compression" OR "graph coarsening") AND ("sequential graph" OR "dynamic graph" OR "temporal graph") AND ("graph autoencoder" OR "graph representation learning") AND ("recurrent neural network" OR "temporal feature learning")`（springer；有命中）
  - `NULL_QUERY(CONCEPT[C1:graph summarization|graph compression|graph coarsening] AND CONCEPT[C2:sequential graph|dynamic graph|temporal graph] AND CONCEPT[C3:graph autoencoder|graph representation learning] AND CONCEPT[C4:recurrent neural network|temporal feature learning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph summarization|graph compression|graph coarsening] AND CONCEPT[C2:sequential graph|dynamic graph|temporal graph] AND CONCEPT[C3:graph autoencoder|graph representation learning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph summarization|graph compression|graph coarsening] AND CONCEPT[C2:sequential graph|dynamic graph|temporal graph] AND CONCEPT[C3:graph autoencoder|graph representation learning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:sequential graph|dynamic graph|temporal graph] AND CONCEPT[C3:graph autoencoder|graph representation learning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:sequential graph|dynamic graph|temporal graph] OR CONCEPT[C3:graph autoencoder|graph representation learning] OR CONCEPT[C4:recurrent neural network|temporal feature learning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:sequential graph|dynamic graph|temporal graph] OR CONCEPT[C3:graph autoencoder|graph representation learning] OR CONCEPT[C4:recurrent neural network|temporal feature learning])`（null_catalog；零命中）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:leader-worker architecture] OR CONCEPT[C4:mini-batch training])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:leader-worker architecture] OR CONCEPT[C4:mini-batch training])`（null_catalog；零命中）
- **NP-3**
  - `(abs:"graph stream partitioning" OR abs:"edge-based partitioning" OR abs:"stream partitioning algorithm") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"degree estimation") AND (abs:"min-heap" OR abs:"high-frequency node maintenance")`（arxiv；零命中）
  - `(abs:"graph stream partitioning" OR abs:"edge-based partitioning" OR abs:"stream partitioning algorithm") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"degree estimation")`（arxiv；零命中）
  - `(abs:"graph stream partitioning" OR abs:"edge-based partitioning" OR abs:"stream partitioning algorithm" OR abs:"graph partitioning" OR abs:"graph stream partition") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"degree estimation" OR abs:"CMS" OR abs:"count-min sketch") AND (abs:"constant-time query" OR abs:"subgraph ID generation" OR abs:"load balancing" OR abs:"O(1) query" OR abs:"subgraph assignment")`（arxiv；零命中）
  - `(abs:"graph stream partitioning" OR abs:"edge-based partitioning" OR abs:"stream partitioning algorithm" OR abs:"graph partitioning" OR abs:"graph stream partition") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"degree estimation" OR abs:"CMS" OR abs:"count-min sketch")`（arxiv；零命中）
  - `(abs:"graph stream partitioning" OR abs:"edge-based partitioning" OR abs:"stream partitioning algorithm" OR abs:"graph partitioning" OR abs:"graph stream partition") OR (abs:"large-scale graph data" OR abs:"graph stream" OR abs:"big graph" OR abs:"streaming graph")`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|edge-based partitioning|stream partitioning algorithm] AND CONCEPT[C2:Count-Min Sketch|probabilistic data structure|degree estimation] AND CONCEPT[C3:min-heap|high-frequency node maintenance])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|edge-based partitioning|stream partitioning algorithm] AND CONCEPT[C2:Count-Min Sketch|probabilistic data structure|degree estimation])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|edge-based partitioning|stream partitioning algorithm] AND CONCEPT[C2:Count-Min Sketch|probabilistic data structure|degree estimation] AND CONCEPT[C4:constant-time query|subgraph ID generation|load balancing])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|edge-based partitioning|stream partitioning algorithm] AND CONCEPT[C2:Count-Min Sketch|probabilistic data structure|degree estimation])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|edge-based partitioning|stream partitioning algorithm] OR CONCEPT[C5:large-scale graph data|graph stream])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|edge-based partitioning|stream partitioning algorithm] OR CONCEPT[C5:large-scale graph data|graph stream])`（null_catalog；零命中）
  - `("graph stream partitioning" OR "edge-based partitioning" OR "stream partitioning algorithm") AND ("Count-Min Sketch" OR "probabilistic data structure" OR "degree estimation") AND ("min-heap" OR "high-frequency node maintenance")`（springer；执行失败）
  - `("graph stream partitioning" OR "edge-based partitioning" OR "stream partitioning algorithm") AND ("Count-Min Sketch" OR "probabilistic data structure" OR "degree estimation") AND ("min-heap" OR "high-frequency node maintenance")`（springer；执行失败）
  - `("graph stream partitioning" OR "edge-based partitioning" OR "stream partitioning algorithm") AND ("Count-Min Sketch" OR "probabilistic data structure" OR "degree estimation") AND ("min-heap" OR "high-frequency node maintenance")`（springer；执行失败）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 4 张原始证据卡；通过 4 张，拒绝 0 张。

### 6.2 相关文献

### card_eb9701e9ca820e30cd228af4 · DTFormer: A Transformer-Based Method for Discrete-Time Dynamic Graph Representation Learning

- 查新点：NP-1
- 主要贡献：DTFormer introduces a Transformer-based representation learning method for Discrete-Time Dynamic Graphs (DTDGs), pivoting from the traditional GNN+RNN framework to address its limitations including scaling to large graph sizes.
- 相关性：0.65
- 置信度：0.75
- 来源：
  - DTFormer: A Transformer-Based Method for Discrete-Time Dynamic Graph Representation Learning：https://arxiv.org/pdf/2407.18523
    - 引文：GNN+RNN architectures also grapple with scaling to large graph sizes and long sequences.
    - 位置：artifact art_5d2a5d231b0a81e0637a2646 chars:735-823
  - DTFormer: A Transformer-Based Method for Discrete-Time Dynamic Graph Representation Learning：https://arxiv.org/pdf/2407.18523
    - 引文：static graph neural networks, such as GNNs (17) and Graph Convolutional Networks (GCNs) (18), are used to process static snapshots of the graph to capture topological relationships.
    - 位置：artifact art_d74cd5fe4fb7f8f30bcb1d3b chars:7063-7244

### card_2b4864cb12d4a361c38ca4e9 · EvolveGCN: Evolving Graph Convolutional Networks for Dynamic Graphs

- 查新点：NP-1
- 主要贡献：EvolveGCN adapts the graph convolutional network (GCN) along the temporal dimension by using an RNN to evolve the GCN parameters, capturing the dynamism of graph sequences without relying on node embeddings.
- 相关性：0.70
- 置信度：0.80
- 来源：
  - EvolveGCN: Evolving Graph Convolutional Networks for Dynamic Graphs：https://arxiv.org/pdf/1902.10191
    - 引文：The proposed approach captures the dynamism of the graph sequence through using an RNN to evolve the GCN parameters.
    - 位置：artifact art_0e0b76110b06e28d52d3110d chars:2783-2899
  - EvolveGCN: Evolving Graph Convolutional Networks for Dynamic Graphs：https://arxiv.org/pdf/1902.10191
    - 引文：These methods use GNNs as a feature extractor and RNNs for sequence learning from the extracted features (node embeddings).
    - 位置：artifact art_0e0b76110b06e28d52d3110d chars:6614-6737

### card_2831f90cbd08b9ebb74d0c5d · ADWISE: Adaptive Window-based Streaming Edge Partitioning for High-Speed Graph Processing

- 查新点：NP-3
- 主要贡献：ADWISE proposes a window-based streaming edge partitioning algorithm that assigns individual graph edges to partitions in a streaming manner, dynamically adapting window size to balance partitioning latency and partitioning quality for large graphs.
- 相关性：0.60
- 置信度：0.70
- 来源：
  - ADWISE: Adaptive Window-based Streaming Edge Partitioning for High-Speed Graph Processing：https://arxiv.org/pdf/1712.08367
    - 引文：Existing graph partitioning algorithms minimize partitioning latency by assigning individual graph edges to partitions in a streaming manner --- at the cost of reduced partitioning quality.
    - 位置：artifact art_e96f0ff1bfe649c77e9b8343 chars:155-344

### card_927caf724042beff967b2231 · Window-based Streaming Graph Partitioning Algorithm

- 查新点：NP-3
- 主要贡献：WStream is a window-based streaming graph partitioning algorithm (edge-cut) that partitions large graph data in a one-pass manner while keeping load balanced across partitions and minimizing communication.
- 相关性：0.55
- 置信度：0.70
- 来源：
  - Window-based Streaming Graph Partitioning Algorithm：10.1145/3290688.3290711
    - 引文：Our results suggest that the WStream algorithm is able to partition large graph data efficiently while keeping the load balanced across different partitions, and communication to a minimum.
    - 位置：artifact art_044b624240993e16c40f3537 chars:924-1113

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 2 | 有证据 |
| NP-2 | 0 | 0 Card |
| NP-3 | 2 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图压缩为固定规模的新图，解决GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - wrk_0e7a55685030127620af7c00：该文献提及GNN+RNN架构在大规模图上的扩展性问题，与查新点声称的解决GNN输出无法直接输入RNN的问题存在局部相关性，但未核验其是否采用图摘要技术，需进一步核验原文。 (cards: card_eb9701e9ca820e30cd228af4)

### NP-2 · 证据不足，无法裁定

提出基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，领导节点负责图划分与参数同步更新，工作者节点基于图摘要进行小批量训练，并通过注意力层返回结果。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - 无

### NP-3 · 证据不足，无法裁定

提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch概率数据结构存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - wrk_07b61d6672c4287867079716：该文献与查新点存在局部相关性；具体技术差异尚待原文核验。 (cards: card_2831f90cbd08b9ebb74d0c5d)
  - wrk_dd602dc2d2b07d7e69e6724c：WStream 是流式图划分算法，目标为大规模图数据负载均衡划分，与查新点目标重合；但摘要证实其为顶点分配（edge-cut）算法，与查新点的边分割机制存在结构性差异，且未提及 Count-Min Sketch 与最小堆机制。 (cards: card_927caf724042beff967b2231)

---

## 八、报告局限

- 本次查新未提供各检索源的执行状态、覆盖范围和命中记录详情，检索覆盖程度未知，无法区分检索失败、成功零命中与有命中但未通过证据门控等情形。
- 对于NP-2，无任何有效EvidenceCard，但无法由此推断是检索零命中还是候选文献未达证据门槛，也不能断言“未见报道”。
- 对于NP-1和NP-3，虽存在有效EvidenceCard，但关键区别特征（如是否采用图摘要、Count-Min Sketch、最小堆等）在现有证据中未被充分核验，证据不足以支撑新颖性裁定，属于证据不充分而非明确检索零命中。
- 未提供被拒绝证据列表，因此无技术性质疑或格式性拒绝信息可写入。

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

- Streaming Graph Partitioning in the Planted Partition Model：[https://arxiv.org/pdf/1406.7570](https://arxiv.org/pdf/1406.7570)
- Window-based Streaming Graph Partitioning Algorithm：[https://arxiv.org/pdf/1902.01543](https://arxiv.org/pdf/1902.01543)
- Play like a Vertex: A Stackelberg Game Approach for Streaming Graph Partitioning：[https://arxiv.org/pdf/2402.18304](https://arxiv.org/pdf/2402.18304)
- A Feasible Graph Partition Framework for Random Walks Implemented by Parallel Computing in Big Graph：[https://arxiv.org/pdf/1501.00067](https://arxiv.org/pdf/1501.00067)
- ADWISE: Adaptive Window-based Streaming Edge Partitioning for High-Speed Graph Processing：[https://arxiv.org/pdf/1712.08367](https://arxiv.org/pdf/1712.08367)
- SDT-GNN: Streaming-based Distributed Training Framework for Graph Neural Networks：[https://arxiv.org/pdf/2404.02300](https://arxiv.org/pdf/2404.02300)
- Practice of Streaming Processing of Dynamic Graphs: Concepts, Models, and Systems：[https://arxiv.org/pdf/1912.12740](https://arxiv.org/pdf/1912.12740)
- Evaluating Complex Queries on Streaming Graphs：[https://arxiv.org/pdf/2101.12305](https://arxiv.org/pdf/2101.12305)
- Balancing Summarization and Change Detection in Graph Streams：[https://arxiv.org/pdf/2311.18694](https://arxiv.org/pdf/2311.18694)
- Utility-Based Graph Summarization: New and Improved：[https://arxiv.org/pdf/2006.08949](https://arxiv.org/pdf/2006.08949)
- Promise and Limitations of Supervised Optimal Transport-Based Graph Summarization via Information Theoretic Measures：[https://arxiv.org/pdf/2305.07138](https://arxiv.org/pdf/2305.07138)
- Causal DAG Summarization (Full Version)：[https://arxiv.org/pdf/2504.14937](https://arxiv.org/pdf/2504.14937)
- Improving Question Answering over Knowledge Graphs Using Graph Summarization：[https://arxiv.org/pdf/2203.13570](https://arxiv.org/pdf/2203.13570)
- Multi-relation Graph Summarization：[https://arxiv.org/pdf/2112.15488](https://arxiv.org/pdf/2112.15488)
- Graph Summarization：[https://arxiv.org/pdf/2004.14794](https://arxiv.org/pdf/2004.14794)
- kMatrix: A Space Efficient Streaming Graph Summarization Technique：[https://arxiv.org/pdf/2105.05503](https://arxiv.org/pdf/2105.05503)
- DGC: Training Dynamic Graphs with Spatio-Temporal Non-Uniformity using Graph Partitioning by Chunks：[https://arxiv.org/pdf/2309.03523](https://arxiv.org/pdf/2309.03523)
- Spectral Temporal Graph Neural Network for massive MIMO CSI Prediction：[https://arxiv.org/pdf/2312.02159](https://arxiv.org/pdf/2312.02159)
- Dynamic Graph Representation Learning via Edge Temporal States Modeling and Structure-reinforced Transformer：[https://arxiv.org/pdf/2304.10079](https://arxiv.org/pdf/2304.10079)
- EvolveGCN: Evolving Graph Convolutional Networks for Dynamic Graphs：[https://arxiv.org/pdf/1902.10191](https://arxiv.org/pdf/1902.10191)
- INFLECT-DGNN: Influencer Prediction with Dynamic Graph Neural Networks：[https://arxiv.org/pdf/2307.08131](https://arxiv.org/pdf/2307.08131)
- DTFormer: A Transformer-Based Method for Discrete-Time Dynamic Graph Representation Learning：[https://arxiv.org/pdf/2407.18523](https://arxiv.org/pdf/2407.18523)
- Learning to Evolve on Dynamic Graphs：[https://arxiv.org/pdf/2111.07032](https://arxiv.org/pdf/2111.07032)
- ReInc: Scaling Training of Dynamic Graph Neural Networks：[https://arxiv.org/pdf/2501.15348](https://arxiv.org/pdf/2501.15348)
- Intelligent scheduling and resource allocation for urban air mobility networks based on graph neural networks：[https://www.nature.com/articles/s41598-026-48143-9.pdf](https://www.nature.com/articles/s41598-026-48143-9.pdf)
- A Survey of Link Prediction in Temporal Networks：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s42979-025-04639-1](http://link.springer.com/openurl/pdf?id=doi:10.1007/s42979-025-04639-1)
- Graph Neural Networks (GNNs)：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-95-6091-2_7](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-95-6091-2_7)
- Graph neural networks: Historical backgrounds, present revolutions, and conventionalization for the future：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s41060-025-00797-w](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s41060-025-00797-w)
- PromptGNN: a prompt-enhanced graph neural network for continual learning on temporal graphs：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10489-025-06888-2](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10489-025-06888-2)
- GraphXAI: a survey of graph neural networks (GNNs) for explainable AI (XAI)：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00521-025-11054-3](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00521-025-11054-3)
- Data Science in Transportation Networks with Graph Neural Networks: A Review and Outlook：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s42421-025-00124-6](http://link.springer.com/openurl/pdf?id=doi:10.1007/s42421-025-00124-6)
- Advanced persistent threat detection via mining long-term features in provenance graphs：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11704-024-40610-8](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11704-024-40610-8)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
