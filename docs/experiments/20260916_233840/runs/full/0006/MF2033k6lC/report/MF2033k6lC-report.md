# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T23:34:54+08:00 |
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
- 提出一种基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，领导节点负责图划分与模型同步更新，工作者节点基于图摘要进行小批量训练，并通过注意力层返回结果。
- 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间查询和负载均衡的子图划分。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图压缩为固定规模的新图，解决GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。 | Propose a large-scale sequential graph representation learning method GSAERU based on graph summarization, which compresses dynamic sequential graphs into fixed-size new graphs via graph summarization, solving the problem that GNN outputs cannot be directly fed into RNN, and uses graph autoencoder and recurrent neural network to learn temporal features. |
| NP-2 | 提出一种基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，领导节点负责图划分与模型同步更新，工作者节点基于图摘要进行小批量训练，并通过注意力层返回结果。 | Propose a distributed graph neural network optimization training framework DSGNN based on graph summarization, adopting a leader-worker mode where the leader performs graph partitioning and synchronous model updates, and workers conduct mini-batch training based on graph summarization and return results through an attention layer. |
| NP-3 | 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间查询和负载均衡的子图划分。 | Propose an edge-segmentation-based graph stream partitioning algorithm Sketch-DBH, which uses Count-Min Sketch to store node degree information and a min-heap to maintain high-frequency node information, enabling constant-time queries and load-balanced subgraph partitioning. |

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
  - `ti:sequential AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:graph autoencoder] OR CONCEPT[C4:recurrent neural network])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:graph autoencoder] OR CONCEPT[C4:recurrent neural network])`（null_catalog；零命中）
  - `"sequential graph representation learning" AND "graph summarization"`（springer；执行失败）
  - `"sequential graph representation learning" AND "graph summarization"`（springer；执行失败）
  - `"sequential graph representation learning" AND "graph summarization"`（springer；执行失败）
  - `"sequential graph representation learning" AND "graph summarization"`（springer；执行失败）
  - `"sequential graph representation learning" AND "graph summarization"`（springer；执行失败）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:leader-worker mode] OR CONCEPT[C4:graph partitioning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:leader-worker mode] OR CONCEPT[C4:graph partitioning])`（null_catalog；零命中）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:mini-batch training] OR CONCEPT[C4:attention layer])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:mini-batch training] OR CONCEPT[C4:attention layer])`（null_catalog；零命中）
- **NP-3**
  - `ti:"graph stream partitioning" AND abs:"edge segmentation" AND abs:"Count-Min Sketch" AND abs:"min-heap"`（arxiv；零命中）
  - `ti:"graph stream partitioning" AND abs:"edge segmentation" AND abs:"Count-Min Sketch"`（arxiv；零命中）
  - `(ti:"graph stream partitioning" OR ti:"graph partitioning" OR ti:"streaming graph partitioning") AND (abs:"edge segmentation" OR abs:"edge-based partitioning" OR abs:"edge cut partitioning") AND (abs:"Count-Min Sketch" OR abs:"CMS" OR abs:"count-min sketch") AND (abs:"min-heap" OR abs:"minimum heap" OR abs:"priority queue") AND (abs:"load balancing" OR abs:"balanced partitioning" OR abs:"load-balanced")`（arxiv；零命中）
  - `(ti:"graph stream partitioning" OR ti:"graph partitioning" OR ti:"streaming graph partitioning") AND (abs:"edge segmentation" OR abs:"edge-based partitioning" OR abs:"edge cut partitioning") AND (abs:"Count-Min Sketch" OR abs:"CMS" OR abs:"count-min sketch") AND (abs:"load balancing" OR abs:"balanced partitioning" OR abs:"load-balanced")`（arxiv；零命中）
  - `(ti:"graph stream partitioning" OR ti:"graph partitioning" OR ti:"streaming graph partitioning") OR (abs:"edge segmentation" OR abs:"edge-based partitioning" OR abs:"edge cut partitioning") OR (abs:"Count-Min Sketch" OR abs:"CMS" OR abs:"count-min sketch") OR (abs:"min-heap" OR abs:"minimum heap" OR abs:"priority queue") OR (abs:"load balancing" OR abs:"balanced partitioning" OR abs:"load-balanced") OR (all:graph AND all:neural AND all:network AND all:training OR all:"GNN training" OR all:"model training")`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] AND CONCEPT[C2:edge segmentation] AND CONCEPT[C3:Count-Min Sketch] AND CONCEPT[C4:min-heap])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] AND CONCEPT[C2:edge segmentation] AND CONCEPT[C3:Count-Min Sketch])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] AND CONCEPT[C2:edge segmentation] AND CONCEPT[C3:Count-Min Sketch] AND CONCEPT[C4:min-heap] AND CONCEPT[C5:load balancing])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] AND CONCEPT[C2:edge segmentation] AND CONCEPT[C3:Count-Min Sketch] AND CONCEPT[C5:load balancing])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] OR CONCEPT[C2:edge segmentation] OR CONCEPT[C3:Count-Min Sketch] OR CONCEPT[C4:min-heap] OR CONCEPT[C5:load balancing] OR CONCEPT[C6:graph neural network training])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] OR CONCEPT[C2:edge segmentation] OR CONCEPT[C3:Count-Min Sketch] OR CONCEPT[C4:min-heap] OR CONCEPT[C5:load balancing] OR CONCEPT[C6:graph neural network training])`（null_catalog；零命中）
  - `"graph stream partitioning" AND "edge segmentation" AND "Count-Min Sketch" AND "min-heap"`（springer；执行失败）
  - `(ti:"graph stream partitioning" OR ti:"graph partitioning" OR ti:"streaming graph partitioning") AND (abs:"Count-Min Sketch" OR abs:"sketch-based data structure" OR abs:"probabilistic data structure") AND (abs:"degree-based hashing" OR abs:"degree-based partitioning" OR abs:"degree-aware partitioning")`（arxiv；零命中）
  - `(abs:"Count-Min Sketch" OR abs:"sketch-based data structure" OR abs:"probabilistic data structure") AND (abs:"degree-based hashing" OR abs:"degree-based partitioning" OR abs:"degree-aware partitioning")`（arxiv；零命中）
  - `(ti:"graph stream partitioning" OR ti:"graph partitioning" OR ti:"streaming graph partitioning" OR ti:"graph stream clustering" OR ti:"online graph partitioning") AND (abs:"Count-Min Sketch" OR abs:"sketch-based data structure" OR abs:"probabilistic data structure" OR abs:"CMS" OR abs:"count-min sketch") AND (abs:"min-heap" OR abs:"priority queue" OR abs:"heap data structure" OR abs:"minimum heap" OR abs:"min heap") AND (abs:"degree-based hashing" OR abs:"degree-based partitioning" OR abs:"degree-aware partitioning" OR abs:"DBH" OR abs:"degree hashing")`（arxiv；零命中）
  - `(ti:"graph stream partitioning" OR ti:"graph partitioning" OR ti:"streaming graph partitioning" OR ti:"graph stream clustering" OR ti:"online graph partitioning") AND (abs:"Count-Min Sketch" OR abs:"sketch-based data structure" OR abs:"probabilistic data structure" OR abs:"CMS" OR abs:"count-min sketch") AND (abs:"degree-based hashing" OR abs:"degree-based partitioning" OR abs:"degree-aware partitioning" OR abs:"DBH" OR abs:"degree hashing")`（arxiv；零命中）
  - `(ti:"graph stream partitioning" OR ti:"graph partitioning" OR ti:"streaming graph partitioning" OR ti:"graph stream clustering" OR ti:"online graph partitioning") OR (abs:"load balancing" OR abs:"load-balanced partitioning" OR abs:"balanced partitioning" OR abs:"load balance" OR abs:"workload balancing") OR (abs:"graph stream" OR abs:"streaming graph" OR abs:"dynamic graph" OR abs:"graph data stream" OR abs:"evolving graph")`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|graph partitioning|streaming graph partitioning] AND CONCEPT[C2:Count-Min Sketch|sketch-based data structure|probabilistic data structure] AND CONCEPT[C4:degree-based hashing|degree-based partitioning|degree-aware partitioning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:Count-Min Sketch|sketch-based data structure|probabilistic data structure] AND CONCEPT[C4:degree-based hashing|degree-based partitioning|degree-aware partitioning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|graph partitioning|streaming graph partitioning] AND CONCEPT[C2:Count-Min Sketch|sketch-based data structure|probabilistic data structure] AND CONCEPT[C3:min-heap|priority queue|heap data structure] AND CONCEPT[C4:degree-based hashing|degree-based partitioning|degree-aware partitioning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|graph partitioning|streaming graph partitioning] AND CONCEPT[C2:Count-Min Sketch|sketch-based data structure|probabilistic data structure] AND CONCEPT[C4:degree-based hashing|degree-based partitioning|degree-aware partitioning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|graph partitioning|streaming graph partitioning] OR CONCEPT[C5:load balancing|load-balanced partitioning|balanced partitioning] OR CONCEPT[C6:graph stream|streaming graph|dynamic graph])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning|graph partitioning|streaming graph partitioning] OR CONCEPT[C5:load balancing|load-balanced partitioning|balanced partitioning] OR CONCEPT[C6:graph stream|streaming graph|dynamic graph])`（null_catalog；零命中）
  - `("graph stream partitioning" OR "graph partitioning" OR "streaming graph partitioning") AND ("Count-Min Sketch" OR "sketch-based data structure" OR "probabilistic data structure") AND ("degree-based hashing" OR "degree-based partitioning" OR "degree-aware partitioning")`（springer；执行失败）
  - `("graph stream partitioning" OR "graph partitioning" OR "streaming graph partitioning") AND ("Count-Min Sketch" OR "sketch-based data structure" OR "probabilistic data structure") AND ("degree-based hashing" OR "degree-based partitioning" OR "degree-aware partitioning")`（springer；执行失败）
  - `("graph stream partitioning" OR "graph partitioning" OR "streaming graph partitioning") AND ("Count-Min Sketch" OR "sketch-based data structure" OR "probabilistic data structure") AND ("degree-based hashing" OR "degree-based partitioning" OR "degree-aware partitioning")`（springer；执行失败）
  - `("graph stream partitioning" OR "graph partitioning" OR "streaming graph partitioning") AND ("Count-Min Sketch" OR "sketch-based data structure" OR "probabilistic data structure") AND ("degree-based hashing" OR "degree-based partitioning" OR "degree-aware partitioning")`（springer；执行失败）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 4 张原始证据卡；通过 1 张，拒绝 3 张。

### 6.2 相关文献

### card_fc5433010f3a4c0f77b19d8c · Balancing Summarization and Change Detection in Graph Streams

- 查新点：NP-1
- 主要贡献：Proposes a quantitative methodology to balance graph summarization and change detection in graph streams, using a hierarchical latent variable model and MDL principle to design parameterized summary graphs for temporal/streaming graphs.
- 相关性：0.35
- 置信度：0.70
- 来源：
  - Balancing Summarization and Change Detection in Graph Streams：https://arxiv.org/pdf/2311.18694
    - 引文：Graph summarization compresses large-scale graphs into a smaller scale. However, the question remains: To what extent should the original graph be compressed? This problem is solved from the perspective of graph change detection, aiming to detect statistically significant changes using a stream of summary graphs.
    - 位置：artifact art_a4b03ccff6df4518c3399802 chars:92-406
  - Balancing Summarization and Change Detection in Graph Streams：https://arxiv.org/pdf/2311.18694
    - 引文：We introduce a probabilistic structure of hierarchical latent variable model into a graph, thereby designing a parameterized summary graph on the basis of the minimum description length principle.
    - 位置：artifact art_a4b03ccff6df4518c3399802 chars:846-1042

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 1 | 有证据 |
| NP-2 | 0 | 0 Card |
| NP-3 | 0 | 0 Card |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图压缩为固定规模的新图，解决GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - wrk_07b78e912a5c299d4357e161：该文献公开了图摘要压缩大规模图的技术，与查新点的图摘要压缩特征部分重合，但未涉及图自编码器、RNN及固定规模新图等关键差异，需进一步核验。 (cards: card_fc5433010f3a4c0f77b19d8c)

### NP-2 · 证据不足，无法裁定

提出一种基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，领导节点负责图划分与模型同步更新，工作者节点基于图摘要进行小批量训练，并通过注意力层返回结果。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - 无

### NP-3 · 证据不足，无法裁定

提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间查询和负载均衡的子图划分。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - 无

---

## 八、报告局限

- 检索覆盖未知：本次输入未提供各检索源的执行状态，无法区分检索失败与成功零命中。
- 存在被拒绝证据：有3条候选文献因相关性低于门槛被拒绝（card_5d3837693d1275a61d133ba0、card_78f7c82eb88e2baec65b1db4、card_57585d5188048ad4d1c7392），属于技术性质疑（相关性不足），而非格式性拒绝。
- NP-2和NP-3虽执行了补充检索，但未形成有效证据卡，不能据此推断相关文献不存在。
- NP-1仅有1张有效证据卡，但Reviewer判定证据不足，待核验关键差异后需补充检索或原文验证。

---

## 九、附件及参考信息

### 缺失参考文献

无。

### 缺失 Baseline

无。

### 引用问题

无。

### 被拒绝证据

- card_5d3837693d1275a61d133ba0：文献相关性低于门槛
- card_78f7c82eb88e2baec65b1db4：文献相关性低于门槛
- card_57585d804b5188ad4d1c7392：文献相关性低于门槛

### 检索到的文献

- Balancing Summarization and Change Detection in Graph Streams：[https://arxiv.org/pdf/2311.18694](https://arxiv.org/pdf/2311.18694)
- Utility-Based Graph Summarization: New and Improved：[https://arxiv.org/pdf/2006.08949](https://arxiv.org/pdf/2006.08949)
- Promise and Limitations of Supervised Optimal Transport-Based Graph Summarization via Information Theoretic Measures：[https://arxiv.org/pdf/2305.07138](https://arxiv.org/pdf/2305.07138)
- Causal DAG Summarization (Full Version)：[https://arxiv.org/pdf/2504.14937](https://arxiv.org/pdf/2504.14937)
- Improving Question Answering over Knowledge Graphs Using Graph Summarization：[https://arxiv.org/pdf/2203.13570](https://arxiv.org/pdf/2203.13570)
- Multi-relation Graph Summarization：[https://arxiv.org/pdf/2112.15488](https://arxiv.org/pdf/2112.15488)
- Graph Summarization：[https://arxiv.org/pdf/2004.14794](https://arxiv.org/pdf/2004.14794)
- kMatrix: A Space Efficient Streaming Graph Summarization Technique：[https://arxiv.org/pdf/2105.05503](https://arxiv.org/pdf/2105.05503)
- Graph Neural Network Training Systems: A Performance Comparison of Full-Graph and Mini-Batch：[https://arxiv.org/pdf/2406.00552](https://arxiv.org/pdf/2406.00552)
- Graph Ladling: Shockingly Simple Parallel GNN Training without Intermediate Communication：[https://arxiv.org/pdf/2306.10466](https://arxiv.org/pdf/2306.10466)
- BiFeat: Supercharge GNN Training via Graph Feature Quantization：[https://arxiv.org/pdf/2207.14696](https://arxiv.org/pdf/2207.14696)
- Fast and Deep Graph Neural Networks：[https://arxiv.org/pdf/1911.08941](https://arxiv.org/pdf/1911.08941)
- Disttack: Graph Adversarial Attacks Toward Distributed GNN Training：[https://arxiv.org/pdf/2405.06247](https://arxiv.org/pdf/2405.06247)
- Characterizing and Understanding Distributed GNN Training on GPUs：[https://arxiv.org/pdf/2204.08150](https://arxiv.org/pdf/2204.08150)
- Adaptive Message Quantization and Parallelization for Distributed Full-graph GNN Training：[https://arxiv.org/pdf/2306.01381](https://arxiv.org/pdf/2306.01381)
- BGL: GPU-Efficient GNN Training by Optimizing Graph Data I/O and Preprocessing：[https://arxiv.org/pdf/2112.08541](https://arxiv.org/pdf/2112.08541)
- Window-based Streaming Graph Partitioning Algorithm：[https://arxiv.org/pdf/1902.01543](https://arxiv.org/pdf/1902.01543)
- Streaming Graph Partitioning in the Planted Partition Model：[https://arxiv.org/pdf/1406.7570](https://arxiv.org/pdf/1406.7570)
- Scalable Coverage Path Planning of Multi-Robot Teams for Monitoring Non-Convex Areas：[https://arxiv.org/pdf/2103.14709](https://arxiv.org/pdf/2103.14709)
- A Programming Model for GPU Load Balancing：[https://arxiv.org/pdf/2301.04792](https://arxiv.org/pdf/2301.04792)
- BuffCut: Prioritized Buffered Streaming Graph Partitioning：[https://arxiv.org/pdf/2602.21248](https://arxiv.org/pdf/2602.21248)
- Scalable Multi-GPU Simulation of 3D Multicellular Growth with RNN-Based Workload Balancing：[https://arxiv.org/pdf/2608.25890](https://arxiv.org/pdf/2608.25890)
- Play like a Vertex: A Stackelberg Game Approach for Streaming Graph Partitioning：[https://arxiv.org/pdf/2402.18304](https://arxiv.org/pdf/2402.18304)
- GPU Load Balancing：[https://arxiv.org/pdf/2212.08964](https://arxiv.org/pdf/2212.08964)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
