# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T21:04:56+08:00 |
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

- 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩原图并利用图自编码器与循环神经网络学习时序依赖，实现大规模动态图的高效表征学习。
- 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，通过基于边分割的图流划分算法和基于图摘要的小批量训练，实现大规模图流数据场景下的高效分布式GNN训练。
- 提出一种基于图摘要的时序图表示学习方法，通过将动态时序图建模为快照序列并结合图自编码器与循环神经网络，在四个真实世界大规模图数据集上实现平均内存消耗仅为传统图神经网络算法的9.86%、平均训练时长仅为13.27%，且与性能最优算法在大部分指标上的差距不超过3.5%。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩原图并利用图自编码器与循环神经网络学习时序依赖，实现大规模动态图的高效表征学习。 | Propose a large-scale sequential graph representation learning method GSAERU based on graph summarization, which compresses the original graph via graph summarization and learns temporal dependencies using a graph autoencoder and a recurrent neural network, enabling efficient representation learning on large-scale dynamic graphs. |
| NP-2 | 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，通过基于边分割的图流划分算法和基于图摘要的小批量训练，实现大规模图流数据场景下的高效分布式GNN训练。 | Propose a distributed graph neural network optimization training algorithm DSGNN based on graph summarization, which adopts a leader-worker mode, uses an edge-segmentation-based graph flow partition algorithm and graph-summarization-based mini-batch training to achieve efficient distributed GNN training in large-scale graph streaming data scenarios. |
| NP-3 | 提出一种基于图摘要的时序图表示学习方法，通过将动态时序图建模为快照序列并结合图自编码器与循环神经网络，在四个真实世界大规模图数据集上实现平均内存消耗仅为传统图神经网络算法的9.86%、平均训练时长仅为13.27%，且与性能最优算法在大部分指标上的差距不超过3.5%。 | Propose a sequential graph representation learning method based on graph summarization, which models dynamic sequential graphs as snapshot sequences and combines a graph autoencoder with a recurrent neural network, achieving average memory consumption of only 9.86% and average training time of only 13.27% compared to traditional graph neural network algorithms on four real-world large-scale graph datasets, with performance gaps not exceeding 3.5% on most metrics against the best-performing algorithm. |

---

## 四、查新范围要求

检索范围围绕各查新点的中英文表述及技术特征展开。

---

## 五、文献检索范围及检索策略

### 5.1 检索来源

- link.springer.com
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
  - `(ti:"large-scale dynamic graphs" OR ti:"sequential graphs" OR ti:"temporal graphs") AND (abs:"graph summarization" OR abs:"graph compression") AND (abs:"graph autoencoder" OR abs:"graph representation learning") AND (abs:"recurrent neural network" OR abs:"temporal dependency learning")`（arxiv；零命中）
  - `(ti:"large-scale dynamic graphs" OR ti:"sequential graphs" OR ti:"temporal graphs") AND (abs:"graph summarization" OR abs:"graph compression") AND (abs:"graph autoencoder" OR abs:"graph representation learning")`（arxiv；零命中）
  - `(ti:"large-scale dynamic graphs" OR ti:"sequential graphs" OR ti:"temporal graphs" OR ti:"dynamic network" OR ti:"time-evolving graph") AND (abs:"graph summarization" OR abs:"graph compression" OR abs:"graph summary" OR abs:"graph coarsening") AND (abs:"graph autoencoder" OR abs:"graph representation learning" OR abs:"graph neural network" OR abs:"GNN") AND (abs:"recurrent neural network" OR abs:"temporal dependency learning" OR abs:"RNN" OR abs:"sequence learning") AND (abs:"node representation" OR abs:"graph embedding" OR abs:"node embedding" OR abs:"graph representation")`（arxiv；零命中）
  - `(ti:"large-scale dynamic graphs" OR ti:"sequential graphs" OR ti:"temporal graphs" OR ti:"dynamic network" OR ti:"time-evolving graph") AND (abs:"graph summarization" OR abs:"graph compression" OR abs:"graph summary" OR abs:"graph coarsening") AND (abs:"graph autoencoder" OR abs:"graph representation learning" OR abs:"graph neural network" OR abs:"GNN") AND (abs:"node representation" OR abs:"graph embedding" OR abs:"node embedding" OR abs:"graph representation")`（arxiv；零命中）
  - `(ti:"large-scale dynamic graphs" OR ti:"sequential graphs" OR ti:"temporal graphs" OR ti:"dynamic network" OR ti:"time-evolving graph") OR (abs:"graph summarization" OR abs:"graph compression" OR abs:"graph summary" OR abs:"graph coarsening") OR (abs:"graph autoencoder" OR abs:"graph representation learning" OR abs:"graph neural network" OR abs:"GNN") OR (abs:"recurrent neural network" OR abs:"temporal dependency learning" OR abs:"RNN" OR abs:"sequence learning") OR (abs:"node representation" OR abs:"graph embedding" OR abs:"node embedding" OR abs:"graph representation") OR (abs:"large-scale" OR abs:"scalability" OR abs:"efficient")`（arxiv；有命中）
  - `("large-scale dynamic graphs" OR "sequential graphs" OR "temporal graphs") AND ("graph summarization" OR "graph compression") AND ("graph autoencoder" OR "graph representation learning") AND ("recurrent neural network" OR "temporal dependency learning")`（springer；有命中）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
  - `"distributed graph neural network training" AND "graph summarization"`（springer；执行失败）
- **NP-3**
  - `(abs:"graph summarization" OR abs:sequential AND abs:graph AND abs:representation AND abs:learning) AND (abs:"graph autoencoder" OR abs:"recurrent neural network") AND (ti:"dynamic graph" OR ti:"temporal graph" OR ti:"snapshot sequence")`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:sequential AND abs:graph AND abs:representation AND abs:learning) AND (abs:"graph autoencoder" OR abs:"recurrent neural network")`（arxiv；有命中）
  - `ti:temporal AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 2 张原始证据卡；通过 2 张，拒绝 0 张。

### 6.2 相关文献

### card_a97fedc0057857de88015883 · A Survey of Link Prediction in Temporal Networks

- 查新点：NP-1
- 主要贡献：A comprehensive survey of temporal link prediction (TLP) that introduces a taxonomy distinguishing representation and inference units, covering snapshot-based (discrete-time dynamic graphs), autoencoder-based, RNN-based, and graph summarisation (DGS) approaches for temporal network representation learning.
- 相关性：0.75
- 置信度：0.85
- 来源：
  - A Survey of Link Prediction in Temporal Networks：10.1007/s42979-025-04639-1
    - 引文：A DTDG simplifies a temporal network into a sequence of timestamped snapshots, converting the continuous temporal space into discrete timestamps.
    - 位置：artifact art_6e0128f41ad58fd336741908 chars:12344-12489
  - A Survey of Link Prediction in Temporal Networks：10.1007/s42979-025-04639-1
    - 引文：EvolveGCN adopts a sequence of discrete snapshots with RNN-based updates of GCN parameters, which is more suitable for gradually evolving networks.
    - 位置：artifact art_6e0128f41ad58fd336741908 chars:4484-4631
  - A Survey of Link Prediction in Temporal Networks：10.1007/s42979-025-04639-1
    - 引文：GNN Graph Neural Network, DGS Dynamic Graph Summarisation, MF Matrix Factorisation, RBM Restricted Boltzmann Machine
    - 位置：artifact art_6e0128f41ad58fd336741908 chars:48139-48255

### card_b3631b654e6dc98339a9f88e · AliGraph: A Comprehensive Graph Neural Network Platform

- 查新点：NP-2
- 主要贡献：AliGraph is a comprehensive distributed graph neural network system that provides distributed graph storage, optimized sampling operators, and a runtime to efficiently support existing and in-house developed GNNs.
- 相关性：0.30
- 置信度：0.70
- 来源：
  - AliGraph: A Comprehensive Graph Neural Network Platform：https://arxiv.org/pdf/1902.08730
    - 引文：we present a comprehensive graph neural network system, namely AliGraph, which consists of distributed graph storage, optimized sampling operators and runtime to efficiently support not only existing popular GNNs but also a series of in-house developed ones for different scenarios.
    - 位置：artifact art_d88778158223021b818fdd97 chars:649-931

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 1 | 有证据 |
| NP-2 | 1 | 有证据 |
| NP-3 | 0 | 0 Card |

---

## 七、查新结论

### NP-1 · 部分新颖

提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩原图并利用图自编码器与循环神经网络学习时序依赖，实现大规模动态图的高效表征学习。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 单篇综述文献（wrk_c0bef0d51bf986df927dc3e6）仅覆盖部分单项特征：快照式时序图建模（特征1）、RNN时序依赖学习（特征4）和动态图摘要DGS（特征2），但未披露将图摘要压缩→图自编码器→RNN整合的统一框架，也未描述以原图重构误差训练原图节点表征（特征3）。因此该文献为部分相关基线，未预见完整组合，支持部分新颖判定。  
**置信度：** 0.70  
**报告摘要：** 现有证据为一篇时序网络链路预测综述，覆盖了快照式时序图建模、RNN时序学习以及动态图摘要等单项技术，但未提出图摘要压缩结合图自编码器与RNN的统一框架，也未覆盖以原图重构误差训练节点表征这一关键特征。基于现有证据，该查新点未被完整预见，判定为部分新颖。  
**高度相关 Work：**
  - wrk_c0bef0d51bf986df927dc3e6：综述覆盖快照式建模（特征1）、RNN时序学习（特征4）与动态图摘要DGS（特征2）等单项技术，作为背景基线相关；但未提出图摘要+图自编码器+RNN的统一方法，未覆盖以原图重构误差训练节点表征（特征3），故为部分相关基线而非完整预见。 (cards: card_a97fedc0057857de88015883)

### NP-2 · 部分新颖

提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，通过基于边分割的图流划分算法和基于图摘要的小批量训练，实现大规模图流数据场景下的高效分布式GNN训练。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 现有证据仅包含 AliGraph 一篇文献，其覆盖分布式 GNN 训练平台这一通用领域，但未公开 DSGNN 的核心特征组合（领导-工作者模式、基于边分割的图流划分、基于图摘要的小批量训练、注意力层返回结果、同步模型更新）。因此，该文献仅部分相关，不能证明完整组合已被公开。由于仅有一篇部分相关文献，且未发现任何单篇公开完整组合或组合证据，故判定为部分新颖，但需注意证据覆盖不足。  
**置信度：** 0.60  
**报告摘要：** 现有证据仅有一篇分布式GNN训练平台文献（AliGraph），其覆盖了通用分布式GNN训练领域，但未涉及领导-工作者模式、边分割图流划分、图摘要小批量训练、注意力层返回及同步更新等具体特征。证据覆盖不足，但现有文献未能预见完整组合，判定为部分新颖。  
**高度相关 Work：**
  - wrk_e59b8b7248dcc080455b8690：AliGraph 是分布式 GNN 训练平台，与 NP-2 在分布式 GNN 训练领域部分重叠，但未覆盖领导-工作者模式、边分割图流划分、图摘要小批量训练、注意力层及同步更新等具体特征，属部分相关文献。 (cards: card_b3631b654e6dc98339a9f88e)

### NP-3 · 证据不足，无法裁定

提出一种基于图摘要的时序图表示学习方法，通过将动态时序图建模为快照序列并结合图自编码器与循环神经网络，在四个真实世界大规模图数据集上实现平均内存消耗仅为传统图神经网络算法的9.86%、平均训练时长仅为13.27%，且与性能最优算法在大部分指标上的差距不超过3.5%。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点（NP-3）缺乏足够的有效证据支持。当前已绑定证据中没有任何通过证据门控的有效EvidenceCard，无法对新颖性作出可靠判定。  
**高度相关 Work：**
  - 无

---

## 八、报告局限

- 本次查新未提供各检索来源的执行覆盖事实，因此无法区分检索失败与检索成功零命中；检索覆盖状态未知，不应由证据卡数量推断来源执行成功。
- 查新点 NP-3 命中了候选文献（论文本身及其参考文献列表中存在相关文献），但未形成任何有效 EvidenceCard。因此既不属于检索失败，也不属于检索成功但零命中，而是属于“有命中但未形成有效证据”的情形。被拒绝证据列表为空，未发现因技术性质疑或格式性拒绝而被排除的证据；该查新点最终因有效证据卡数量为0（低于所需1张门槛）而无法作出判定。
- 查新点 NP-1 和 NP-2 各有少量有效证据，但均仅覆盖部分单项特征或通用领域，未发现完整组合的相同方案；受限于检索覆盖未知，结论应在相应置信度范围内解读，不代表全局穷尽性确认。

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

- Explainable graph attention network for stress recognition (StressGAT) via differential action units：[https://arxiv.org/pdf/2607.20819](https://arxiv.org/pdf/2607.20819)
- Fairness Attacks on Recommender Systems：[https://arxiv.org/pdf/2606.29064](https://arxiv.org/pdf/2606.29064)
- Benchmark-Ready 3D Anatomical Shape Classification：[https://arxiv.org/pdf/2511.01613](https://arxiv.org/pdf/2511.01613)
- A Deep Generative Model for the Simulation of Discrete Karst Networks：[https://arxiv.org/pdf/2506.09832](https://arxiv.org/pdf/2506.09832)
- Multiway Multislice PHATE: Visualizing Hidden Dynamics of RNNs through Training：[https://arxiv.org/pdf/2406.01969](https://arxiv.org/pdf/2406.01969)
- Structure Embedded Nucleus Classification for Histopathology Images：[https://arxiv.org/pdf/2302.11416](https://arxiv.org/pdf/2302.11416)
- Multi-Behavior Hypergraph-Enhanced Transformer for Sequential Recommendation：[https://arxiv.org/pdf/2207.05584](https://arxiv.org/pdf/2207.05584)
- Reinforcement Learning-enhanced Shared-account Cross-domain Sequential Recommendation：[https://arxiv.org/pdf/2206.08088](https://arxiv.org/pdf/2206.08088)
- Graph-Adaptive Horseshoe for Compositional Regression：[https://arxiv.org/pdf/2608.17858](https://arxiv.org/pdf/2608.17858)
- CGS: Configurable Graph Summarization with Bounded Neighborhood Loss and Query Support：[https://arxiv.org/pdf/2607.10969](https://arxiv.org/pdf/2607.10969)
- COREKG: Coreset-Guided Personalized Summarization of Knowledge Graphs：[https://arxiv.org/pdf/2605.14900](https://arxiv.org/pdf/2605.14900)
- Spectral Model eXplainer: a chemically-grounded explainability framework for spectral-based machine learning models：[https://arxiv.org/pdf/2605.02684](https://arxiv.org/pdf/2605.02684)
- A Null Model for Mapper Subtype Claims：[https://arxiv.org/pdf/2604.17395](https://arxiv.org/pdf/2604.17395)
- Explainable Mapper: Charting LLM Embedding Spaces Using Perturbation-Based Explanation and Verification Agents：[https://arxiv.org/pdf/2507.18607](https://arxiv.org/pdf/2507.18607)
- Causal DAG Summarization (Full Version)：[https://arxiv.org/pdf/2504.14937](https://arxiv.org/pdf/2504.14937)
- Code-Craft: Hierarchical Graph-Based Code Summarization for Enhanced Context Retrieval：[https://arxiv.org/pdf/2504.08975](https://arxiv.org/pdf/2504.08975)
- Vanilla Scotogenic Model at the future Muon Collider：[https://arxiv.org/pdf/2609.17530](https://arxiv.org/pdf/2609.17530)
- You Shall Not Pass into Ring-0! A User Privacy-Friendly Anti-Cheat Architecture for Personal Computers：[https://arxiv.org/pdf/2609.17525](https://arxiv.org/pdf/2609.17525)
- Modality-Autoregressive World-Action Models：[https://arxiv.org/pdf/2609.17524](https://arxiv.org/pdf/2609.17524)
- LACE: Layer-Wise Compression for Dynamic Frame Rate Codecs：[https://arxiv.org/pdf/2609.17509](https://arxiv.org/pdf/2609.17509)
- Beyond Hardware: Adaptive Algorithmic Control by State-Proxy Equalization：[https://arxiv.org/pdf/2609.17497](https://arxiv.org/pdf/2609.17497)
- Hysteresis and trap emission in dc-biased integrated lithium niobate electro-optic modulators：[https://arxiv.org/pdf/2609.17489](https://arxiv.org/pdf/2609.17489)
- Stuffed IBLTs: Optimal Linear Multiset Sketches：[https://arxiv.org/pdf/2609.17487](https://arxiv.org/pdf/2609.17487)
- Bridging the Gap Between Homogeneous and Heterogeneous Asynchronous Optimization Is Surprisingly Difficult：[https://arxiv.org/pdf/2609.17483](https://arxiv.org/pdf/2609.17483)
- A Survey of Link Prediction in Temporal Networks：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s42979-025-04639-1](http://link.springer.com/openurl/pdf?id=doi:10.1007/s42979-025-04639-1)
- Graph Neural Networks (GNNs)：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-95-6091-2_7](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-95-6091-2_7)
- Graph neural networks: Historical backgrounds, present revolutions, and conventionalization for the future：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s41060-025-00797-w](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s41060-025-00797-w)
- PromptGNN: a prompt-enhanced graph neural network for continual learning on temporal graphs：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10489-025-06888-2](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10489-025-06888-2)
- GraphXAI: a survey of graph neural networks (GNNs) for explainable AI (XAI)：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00521-025-11054-3](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00521-025-11054-3)
- Data Science in Transportation Networks with Graph Neural Networks: A Review and Outlook：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s42421-025-00124-6](http://link.springer.com/openurl/pdf?id=doi:10.1007/s42421-025-00124-6)
- Anomaly Detection Model for Edge Network Infrastructure Based on Time Series：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-96-9884-4_31](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-96-9884-4_31)
- Dynamic Neighborhood Selection for Context Aware Temporal Evolution Using Graph Neural Networks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s12559-024-10359-0](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s12559-024-10359-0)
- AliGraph: A Comprehensive Graph Neural Network Platform：[https://arxiv.org/pdf/1902.08730](https://arxiv.org/pdf/1902.08730)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
