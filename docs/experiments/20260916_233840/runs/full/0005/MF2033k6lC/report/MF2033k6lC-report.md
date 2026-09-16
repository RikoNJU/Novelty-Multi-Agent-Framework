# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T23:28:28+08:00 |
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

- 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图映射为固定规模的新图，解决GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。
- 提出一种基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，领导节点负责图划分与参数同步更新，工作者节点基于图摘要进行小批量训练，并通过注意力层返回结果。
- 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch概率数据结构存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图映射为固定规模的新图，解决GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。 | Propose a large-scale sequential graph representation learning method GSAERU based on graph summarization, which maps dynamic sequential graphs to fixed-size new graphs via graph summarization, addressing the issue that GNN outputs cannot be directly fed into RNN, and uses graph autoencoder and recurrent neural network to learn temporal features. |
| NP-2 | 提出一种基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，领导节点负责图划分与参数同步更新，工作者节点基于图摘要进行小批量训练，并通过注意力层返回结果。 | Propose a distributed graph neural network optimization training framework DSGNN based on graph summarization, adopting a leader-worker mode where the leader handles graph partitioning and synchronous parameter updates, and workers perform mini-batch training based on graph summarization and return results via an attention layer. |
| NP-3 | 提出一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch概率数据结构存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。 | Propose a graph flow partition algorithm Sketch-DBH based on edge segmentation, which uses Count-Min Sketch probabilistic data structure to store node degree information and a min-heap to maintain high-frequency node information, enabling constant-time query results and generating subgraph IDs for each edge, ensuring load balance. |

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
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"mini-batch training" AND abs:"leader-worker architecture"`（arxiv；零命中）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"leader-worker architecture"`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"parallel GNN training") AND (abs:"graph summarization" OR abs:"graph summary" OR abs:"graph condensation") AND (abs:"attention mechanism" OR abs:"attention layer" OR abs:"attention aggregation")`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"parallel GNN training") AND (abs:"graph summarization" OR abs:"graph summary" OR abs:"graph condensation")`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"parallel GNN training") OR (all:"graph neural network" OR all:"GNN" OR all:"graph deep learning")`（arxiv；有命中）
- **NP-3**
  - `ti:"graph stream partitioning" AND abs:"edge-cut partitioning" AND abs:"Count-Min Sketch" AND abs:"min-heap"`（arxiv；零命中）
  - `ti:"graph stream partitioning" AND abs:"edge-cut partitioning" AND abs:"Count-Min Sketch"`（arxiv；零命中）
  - `(ti:"graph stream partitioning" OR ti:graph AND ti:data AND ti:stream AND ti:partitioning OR ti:"streaming graph partitioning") AND (abs:"edge-cut partitioning" OR abs:"edge segmentation" OR abs:"edge-based partitioning") AND (abs:"Count-Min Sketch" OR abs:"CMS" OR abs:"count-min sketch") AND (abs:"load balancing" OR abs:"load balance" OR abs:"balanced partitioning")`（arxiv；零命中）
  - `(ti:"graph stream partitioning" OR ti:graph AND ti:data AND ti:stream AND ti:partitioning OR ti:"streaming graph partitioning") AND (abs:"edge-cut partitioning" OR abs:"edge segmentation" OR abs:"edge-based partitioning") AND (abs:"Count-Min Sketch" OR abs:"CMS" OR abs:"count-min sketch")`（arxiv；零命中）
  - `(ti:"graph stream partitioning" OR ti:graph AND ti:data AND ti:stream AND ti:partitioning OR ti:"streaming graph partitioning") OR (abs:"edge-cut partitioning" OR abs:"edge segmentation" OR abs:"edge-based partitioning") OR (all:"graph partitioning" OR all:"graph partition" OR all:"graph clustering") ANDNOT (all:"vertex-cut" OR all:"streaming")`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] AND CONCEPT[C2:edge-cut partitioning] AND CONCEPT[C3:Count-Min Sketch] AND CONCEPT[C4:min-heap])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] AND CONCEPT[C2:edge-cut partitioning] AND CONCEPT[C3:Count-Min Sketch])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] AND CONCEPT[C2:edge-cut partitioning] AND CONCEPT[C3:Count-Min Sketch] AND CONCEPT[C5:load balancing])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] AND CONCEPT[C2:edge-cut partitioning] AND CONCEPT[C3:Count-Min Sketch])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] OR CONCEPT[C2:edge-cut partitioning] OR CONCEPT[C6:graph partitioning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] OR CONCEPT[C2:edge-cut partitioning] OR CONCEPT[C6:graph partitioning])`（null_catalog；零命中）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 2 张原始证据卡；通过 2 张，拒绝 0 张。

### 6.2 相关文献

### card_3596aaf35e4cea44b566e710 · Improving Question Answering over Knowledge Graphs Using Graph Summarization

- 查新点：NP-1
- 主要贡献：Proposes a graph summarization technique using Recurrent Convolutional Neural Network (RCNN) and Graph Convolutional Network (GCN) to improve Question Answering over Knowledge Graphs (KGQA), addressing the issue of questions with an uncertain number of answers.
- 相关性：0.40
- 置信度：0.70
- 来源：
  - Improving Question Answering over Knowledge Graphs Using Graph Summarization：https://arxiv.org/pdf/2203.13570
    - 引文：we propose a graph summarization technique using Recurrent Convolutional Neural Network (RCNN) and GCN.
    - 位置：artifact art_1ce5122541fb918d925dafcb chars:848-951

### card_c33cb45ae7876c057ddcd743 · Recent Advances in Graph Partitioning

- 查新点：NP-3
- 主要贡献：A comprehensive survey of practical algorithms for balanced graph partitioning, including a section on Streaming Graph Partitioning (SGP) which processes graph input in a data stream on the fly using limited memory.
- 相关性：0.50
- 置信度：0.70
- 来源：
  - Recent Advances in Graph Partitioning：https://arxiv.org/pdf/1311.3144
    - 引文：Streaming data models are among the most popular recent trends in big data processing. In these models the input arrives in a data stream and has to be processed on the fly using much less space than the overall input size. SGP algorithms are very fast.
    - 位置：artifact art_d16e5a81b879c33a5cc5d642 chars:38172-38425

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 1 | 有证据 |
| NP-2 | 0 | 0 Card |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图映射为固定规模的新图，解决GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - wrk_645400a853804090bc37d875：该文献与查新点存在局部相关性；具体技术差异尚待原文核验。 (cards: card_3596aaf35e4cea44b566e710)

### NP-2 · 证据不足，无法裁定

提出一种基于图摘要的分布式图神经网络优化训练框架DSGNN，采用领导-工作者模式，领导节点负责图划分与参数同步更新，工作者节点基于图摘要进行小批量训练，并通过注意力层返回结果。

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
  - wrk_e192ff1ca2fcf3a600c57b16：该文献与查新点存在局部相关性；具体技术差异尚待原文核验。 (cards: card_c33cb45ae7876c057ddcd743)

---

## 八、报告局限

- 本轮检索产生了候选文献，但最终有效证据卡数量未达门槛（NP-2有效卡0张，NP-1和NP-3各1张），且Reviewer指出裁定依赖文献未采用特征的断言，但输入引文没有直接支持该否定，需核验原文。因此无法形成新颖性裁定，属于“有命中但未形成有效证据”的情况，而非检索失败或零命中。
- 检索覆盖事实未明确提供，无法区分检索成功或失败；本次报告仅能基于现有证据卡说明检索到候选文献，但未通过证据门控或需进一步核验。
- 所有查新点的证据均不足以支撑最终结论，建议补充检索或对现有文献进行深度核验。

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

- Balancing Summarization and Change Detection in Graph Streams：[https://arxiv.org/pdf/2311.18694](https://arxiv.org/pdf/2311.18694)
- Utility-Based Graph Summarization: New and Improved：[https://arxiv.org/pdf/2006.08949](https://arxiv.org/pdf/2006.08949)
- Promise and Limitations of Supervised Optimal Transport-Based Graph Summarization via Information Theoretic Measures：[https://arxiv.org/pdf/2305.07138](https://arxiv.org/pdf/2305.07138)
- Causal DAG Summarization (Full Version)：[https://arxiv.org/pdf/2504.14937](https://arxiv.org/pdf/2504.14937)
- Improving Question Answering over Knowledge Graphs Using Graph Summarization：[https://arxiv.org/pdf/2203.13570](https://arxiv.org/pdf/2203.13570)
- Multi-relation Graph Summarization：[https://arxiv.org/pdf/2112.15488](https://arxiv.org/pdf/2112.15488)
- Graph Summarization：[https://arxiv.org/pdf/2004.14794](https://arxiv.org/pdf/2004.14794)
- kMatrix: A Space Efficient Streaming Graph Summarization Technique：[https://arxiv.org/pdf/2105.05503](https://arxiv.org/pdf/2105.05503)
- Axioms for graph clustering quality functions：[https://arxiv.org/pdf/1308.3383](https://arxiv.org/pdf/1308.3383)
- (Semi-)External Algorithms for Graph Partitioning and Clustering：[https://arxiv.org/pdf/1404.4887](https://arxiv.org/pdf/1404.4887)
- Graph Partitioning with Fujitsu Digital Annealer：[https://arxiv.org/pdf/2311.16559](https://arxiv.org/pdf/2311.16559)
- Recent Advances in Graph Partitioning：[https://arxiv.org/pdf/1311.3144](https://arxiv.org/pdf/1311.3144)
- An exact algorithm for graph partitioning：[https://arxiv.org/pdf/0912.1664](https://arxiv.org/pdf/0912.1664)
- Graph Partitioning Induced Phase Transitions：[https://arxiv.org/pdf/0702417](https://arxiv.org/pdf/0702417)
- Axioms for Distanceless Graph Partitioning：[https://arxiv.org/pdf/2309.09386](https://arxiv.org/pdf/2309.09386)
- Jet: Multilevel Graph Partitioning on Graphics Processing Units：[https://arxiv.org/pdf/2304.13194](https://arxiv.org/pdf/2304.13194)
- CI-GNN: A Granger Causality-Inspired Graph Neural Network for Interpretable Brain Network-Based Psychiatric Diagnosis：[https://arxiv.org/pdf/2301.01642](https://arxiv.org/pdf/2301.01642)
- DAG-GNN: DAG Structure Learning with Graph Neural Networks：[https://arxiv.org/pdf/1904.10098](https://arxiv.org/pdf/1904.10098)
- Proficient Graph Neural Network Design by Accumulating Knowledge on Large Language Models：[https://arxiv.org/pdf/2408.06717](https://arxiv.org/pdf/2408.06717)
- From Stars to Subgraphs: Uplifting Any GNN with Local Structure Awareness：[https://arxiv.org/pdf/2110.03753](https://arxiv.org/pdf/2110.03753)
- Graph neural network for colliding particles with an application to sea ice floe modeling：[https://arxiv.org/pdf/2602.16213](https://arxiv.org/pdf/2602.16213)
- MAG-GNN: Reinforcement Learning Boosted Graph Neural Network：[https://arxiv.org/pdf/2310.19142](https://arxiv.org/pdf/2310.19142)
- GNN-Geo: A Graph Neural Network-based Fine-grained IP geolocation Framework：[https://arxiv.org/pdf/2112.10767](https://arxiv.org/pdf/2112.10767)
- Graph Neural Network Training Systems: A Performance Comparison of Full-Graph and Mini-Batch：[https://arxiv.org/pdf/2406.00552](https://arxiv.org/pdf/2406.00552)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
