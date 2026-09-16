# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-17T00:49:34+08:00 |
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
- 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，由领导节点进行图划分，工作节点基于图摘要进行小批量训练，并通过注意力层返回结果，实现分布式训练加速。
- 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch概率数据结构存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图压缩为固定规模的新图，解决GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。 | Propose a large-scale sequential graph representation learning method GSAERU based on graph summarization, which compresses dynamic sequential graphs into fixed-size new graphs via graph summarization, addressing the issue that GNN outputs cannot be directly fed into RNN training, and uses a graph autoencoder and a recurrent neural network to learn temporal features. |
| NP-2 | 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，由领导节点进行图划分，工作节点基于图摘要进行小批量训练，并通过注意力层返回结果，实现分布式训练加速。 | Propose a distributed graph neural network optimization training algorithm DSGNN based on graph summarization, adopting a leader-worker mode where the leader partitions the graph, workers perform mini-batch training based on graph summarization, and results are returned through an attention layer, accelerating distributed training. |
| NP-3 | 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch概率数据结构存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。 | Propose a graph flow partition algorithm Sketch-DBH based on edge segmentation, which uses the Count-Min Sketch probabilistic data structure to store node degree information and a min-heap to maintain high-frequency node information, enabling constant-time query results and generating subgraph IDs while ensuring load balance. |

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
  - `ti:sequential AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder" AND abs:"recurrent neural network"`（arxiv；零命中）
  - `ti:sequential AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"recurrent neural network"`（arxiv；零命中）
  - `(ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:temporal AND ti:graph AND ti:representation AND ti:learning) AND (abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening")`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening")`（arxiv；有命中）
  - `"sequential graph representation learning" AND "graph summarization" AND "graph autoencoder" AND "recurrent neural network"`（springer；执行失败）
  - `"sequential graph representation learning" AND "graph summarization" AND "graph autoencoder" AND "recurrent neural network"`（springer；执行失败）
  - `"sequential graph representation learning" AND "graph summarization" AND "graph autoencoder" AND "recurrent neural network"`（springer；执行失败）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"leader worker mode" AND abs:"mini batch training" AND abs:"attention layer"`（arxiv；零命中）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"mini batch training" AND abs:"attention layer"`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"distributed graph learning") AND (abs:"graph summarization" OR abs:"graph summary" OR abs:"graph condensation")`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph summary" OR abs:"graph condensation")`（arxiv；有命中）
  - `"distributed graph neural network training" AND "graph summarization" AND "leader worker mode" AND "mini batch training" AND "attention layer"`（springer；执行失败）
  - `"distributed graph neural network training" AND "graph summarization" AND "leader worker mode" AND "mini batch training" AND "attention layer"`（springer；执行失败）
  - `"distributed graph neural network training" AND "graph summarization" AND "leader worker mode" AND "mini batch training" AND "attention layer"`（springer；执行失败）
- **NP-3**
  - `(abs:graph AND abs:stream AND abs:partitioning AND abs:algorithm OR abs:"edge-based partitioning" OR abs:"graph partitioning") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"frequency estimation") AND (abs:"min-heap" OR abs:"priority queue" OR abs:"high-frequency node maintenance")`（arxiv；零命中）
  - `(abs:graph AND abs:stream AND abs:partitioning AND abs:algorithm OR abs:"edge-based partitioning" OR abs:"graph partitioning") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"frequency estimation")`（arxiv；零命中）
  - `(abs:graph AND abs:stream AND abs:partitioning AND abs:algorithm OR abs:"edge-based partitioning" OR abs:"graph partitioning" OR abs:"graph stream partition" OR abs:"edge-cut partitioning") AND (abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"frequency estimation" OR abs:"CMS" OR abs:"count-min sketch")`（arxiv；零命中）
  - `(abs:"Count-Min Sketch" OR abs:"probabilistic data structure" OR abs:"frequency estimation" OR abs:"CMS" OR abs:"count-min sketch")`（arxiv；有命中）
  - `("graph stream partitioning algorithm" OR "edge-based partitioning" OR "graph partitioning") AND ("Count-Min Sketch" OR "probabilistic data structure" OR "frequency estimation") AND ("min-heap" OR "priority queue" OR "high-frequency node maintenance")`（springer；有命中）
  - `("graph stream partitioning algorithm" OR "edge-based partitioning" OR "graph partitioning" OR "graph stream partition" OR "edge-cut partitioning") AND ("Count-Min Sketch" OR "probabilistic data structure" OR "frequency estimation" OR "CMS" OR "count-min sketch")`（springer；部分成功）
  - `("graph stream partitioning algorithm" OR "edge-based partitioning" OR "graph partitioning") AND ("Count-Min Sketch" OR "probabilistic data structure" OR "frequency estimation") AND ("min-heap" OR "priority queue" OR "high-frequency node maintenance")`（springer；有命中）
  - `("graph stream partitioning algorithm" OR "edge-based partitioning" OR "graph partitioning" OR "graph stream partition" OR "edge-cut partitioning") AND ("Count-Min Sketch" OR "probabilistic data structure" OR "frequency estimation" OR "CMS" OR "count-min sketch")`（springer；部分成功）
  - `ti:"graph stream partitioning" AND abs:"Count-Min Sketch" AND abs:"degree-based hashing"`（arxiv；零命中）
  - `abs:"Count-Min Sketch" AND abs:"degree-based hashing"`（arxiv；零命中）
  - `(ti:"graph stream partitioning" OR ti:"graph stream partition" OR ti:"streaming graph partitioning") AND (abs:"Count-Min Sketch" OR abs:"CMS" OR abs:"count-min sketch")`（arxiv；零命中）
  - `(abs:"Count-Min Sketch" OR abs:"CMS" OR abs:"count-min sketch")`（arxiv；有命中）
  - `"graph stream partitioning" AND "Count-Min Sketch" AND "degree-based hashing"`（springer；执行失败）
  - `"graph stream partitioning" AND "Count-Min Sketch" AND "degree-based hashing"`（springer；执行失败）
  - `"graph stream partitioning" AND "Count-Min Sketch" AND "degree-based hashing"`（springer；执行失败）
  - `"graph stream partitioning" AND "Count-Min Sketch" AND "degree-based hashing"`（springer；执行失败）
  - `"graph stream partitioning" AND "Count-Min Sketch" AND "degree-based hashing"`（springer；执行失败）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 2 张原始证据卡；通过 2 张，拒绝 0 张。

### 6.2 相关文献

### card_d215b0e5a7dd31cc57f586c1 · A Comprehensive Survey on Graph Reduction: Sparsification, Coarsening, and Condensation

- 查新点：NP-1
- 主要贡献：A comprehensive survey on graph reduction methods (sparsification, coarsening, and condensation), establishing a unified framework for simplifying large graphs while preserving essential properties. It systematically reviews technical details of graph reduction algorithms and their applications across diverse scenarios.
- 相关性：0.50
- 置信度：0.80
- 来源：
  - A Comprehensive Survey on Graph Reduction: Sparsification, Coarsening, and Condensation：https://arxiv.org/pdf/2402.03358
    - 引文：graph reduction, or graph summarization, has gained prominence for simplifying large graphs while preserving essential properties
    - 位置：artifact art_b8462b011f5690bfcdcaa3c6 chars:235-364

### card_430dca87eee8908e02934852 · Scaling R-GCN Training with Graph Summarization

- 查新点：NP-2
- 主要贡献：Scaling R-GCN Training with Graph Summarization proposes using graph summarization techniques to compress graphs before training a Relational Graph Convolutional Network, reducing memory requirements and computational overhead, then transferring weights back to the original graph for inference.
- 相关性：0.55
- 置信度：0.80
- 来源：
  - Scaling R-GCN Training with Graph Summarization：10.1145/3487553.3524719
    - 引文：we experiment with the use of graph summarization techniques to compress the graph and hence reduce the amount of memory needed. After training the R-GCN on the graph summary, we transfer the weights back to the original graph and attempt to perform inference on it.
    - 位置：artifact art_5a95e23353233acf80dfb52a chars:265-531

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 1 | 有证据 |
| NP-2 | 1 | 有证据 |
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
  - wrk_f2c870a83b8903ea02a3d5b6：该文献与查新点存在局部相关性；具体技术差异尚待原文核验。 (cards: card_d215b0e5a7dd31cc57f586c1)

### NP-2 · 证据不足，无法裁定

提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，由领导节点进行图划分，工作节点基于图摘要进行小批量训练，并通过注意力层返回结果，实现分布式训练加速。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - wrk_69b3cecda02343b983f9dbc2：该文献与查新点存在局部相关性；具体技术差异尚待原文核验。 (cards: card_430dca87eee8908e02934852)

### NP-3 · 证据不足，无法裁定

提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch概率数据结构存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - 无

---

## 八、报告局限

- NP-1：命中了候选文献并通过证据门控形成有效证据卡，但证据卡仅提供局部相关事实，查新所需的细节特征未在摘要级证据中呈现，reviewer裁定依赖“未采用特征”的断言而证据未直接支持，故证据尚不足以支撑新颖性判断，需进一步核验原文。
- NP-2：命中了候选文献并通过证据门控形成有效证据卡，但证据卡仅提供局部相关事实，查新所需的细节特征未在摘要级证据中呈现，reviewer裁定依赖“未采用特征”的断言而证据未直接支持，故证据尚不足以支撑新颖性判断，需进一步核验原文。
- NP-3：检索执行过补充尝试（T-R2-1），但最终有效证据卡数量为0，未达到系统设定的最低门槛。这一状态既不等同于“检索成功且零命中”，也不等同于“检索失败”，而是表明命中的候选文献未能通过证据门控形成有效证据卡，或未检索到满足门槛的对比文献。因此不能据当前零卡状态推断“未见报道”或“不存在相似工作”，只能认定证据不足。

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

- Does Graph Compression Preserve Signal Propagation?：[https://arxiv.org/pdf/2607.23338](https://arxiv.org/pdf/2607.23338)
- A Comprehensive Survey on Graph Reduction: Sparsification, Coarsening, and Condensation：[https://arxiv.org/pdf/2402.03358](https://arxiv.org/pdf/2402.03358)
- Are Edge Weights in Summary Graphs Useful? -- A Comparative Study：[https://arxiv.org/pdf/2203.15212](https://arxiv.org/pdf/2203.15212)
- Personalized Graph Summarization: Formulation, Scalable Algorithms, and Applications：[https://arxiv.org/pdf/2203.14755](https://arxiv.org/pdf/2203.14755)
- SLUGGER: Lossless Hierarchical Summarization of Massive Graphs：[https://arxiv.org/pdf/2112.05374](https://arxiv.org/pdf/2112.05374)
- Graph Coarsening with Preserved Spectral Properties：[https://arxiv.org/pdf/1802.04447](https://arxiv.org/pdf/1802.04447)
- SSumM: Sparse Summarization of Massive Graphs：[https://arxiv.org/pdf/2006.01060](https://arxiv.org/pdf/2006.01060)
- Bridging Training and Execution via Dynamic Directed Graph-Based Communication in Cooperative Multi-Agent Systems：[https://arxiv.org/pdf/2408.07397](https://arxiv.org/pdf/2408.07397)
- Buffered Count-Min Sketch on SSD: Theory and Experiments：[https://arxiv.org/pdf/1804.10673](https://arxiv.org/pdf/1804.10673)
- Count-Min sketches for Telemetry: analysis of performance in P4 implementations：[https://arxiv.org/pdf/2406.12586](https://arxiv.org/pdf/2406.12586)
- Optimized Learned Count-Min Sketch：[https://arxiv.org/pdf/2512.12252](https://arxiv.org/pdf/2512.12252)
- Count-Min-Log sketch: Approximately counting with approximate counters：[https://arxiv.org/pdf/1502.04885](https://arxiv.org/pdf/1502.04885)
- Count-Min Tree Sketch: Approximate counting for NLP：[https://arxiv.org/pdf/1604.05492](https://arxiv.org/pdf/1604.05492)
- These are not the k-mers you are looking for: efficient online k-mer counting using a probabilistic data structure：[https://arxiv.org/pdf/1309.2975](https://arxiv.org/pdf/1309.2975)
- Memory-efficient Sketch Acceleration for Handling Large Network Flows on FPGAs：[https://arxiv.org/pdf/2504.16896](https://arxiv.org/pdf/2504.16896)
- A Formal Analysis of the Count-Min Sketch with Conservative Updates：[https://arxiv.org/pdf/2203.14549](https://arxiv.org/pdf/2203.14549)
- Scaling R-GCN Training with Graph Summarization：[https://arxiv.org/pdf/2203.02622](https://arxiv.org/pdf/2203.02622)
- Utility-Based Graph Summarization: New and Improved：[https://arxiv.org/pdf/2006.08949](https://arxiv.org/pdf/2006.08949)
- Graph Summarization with Graph Neural Networks：[https://arxiv.org/pdf/2203.05919](https://arxiv.org/pdf/2203.05919)
- FLUID: A Common Model for Semantic Structural Graph Summaries Based on Equivalence Relations：[https://arxiv.org/pdf/1908.01528](https://arxiv.org/pdf/1908.01528)
- A Comprehensive Survey on Graph Summarization with Graph Neural Networks：[https://arxiv.org/pdf/2302.06114](https://arxiv.org/pdf/2302.06114)
- Time and Memory Efficient Parallel Algorithm for Structural Graph Summaries and two Extensions to Incremental Summarization and $k$-Bisimulation for Long $k$-Chaining：[https://arxiv.org/pdf/2111.12493](https://arxiv.org/pdf/2111.12493)
- Balancing Summarization and Change Detection in Graph Streams：[https://arxiv.org/pdf/2311.18694](https://arxiv.org/pdf/2311.18694)
- Electrical Engineering：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-1-4613-0393-0_12](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-1-4613-0393-0_12)
- Electrical Engineering：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-1-4615-1969-0_12](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-1-4615-1969-0_12)
- Evolving digital skill demands before and after generative AI: a global network analysis via upwork data：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10618-026-01271-2](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10618-026-01271-2)
- A hybrid OpenMP/MPI parallel automated multilevel substructuring method for finite element modal analysis：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00466-026-02771-0](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00466-026-02771-0)
- A novel framework for network null models: bridging optimal transport theory and complex networks：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s11135-026-02919-3](http://link.springer.com/openurl/pdf?id=doi:10.1007/s11135-026-02919-3)
- Graph-Based modeling and decomposition of hierarchical optimization problems：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s12532-026-00315-4](http://link.springer.com/openurl/pdf?id=doi:10.1007/s12532-026-00315-4)
- A Community Structure-Based GMCR Framework for Power-Asymmetric Conflict Resolution Under Linguistic Distribution Information：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10726-026-09972-1](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10726-026-09972-1)
- Clustering and Spectral Analysis of the Infinite Cucker–Smale Model：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10114-026-5431-z](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10114-026-5431-z)
- Count-Min Sketch with Conservative Updates: Worst-Case Analysis：[https://arxiv.org/pdf/2405.12034](https://arxiv.org/pdf/2405.12034)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
