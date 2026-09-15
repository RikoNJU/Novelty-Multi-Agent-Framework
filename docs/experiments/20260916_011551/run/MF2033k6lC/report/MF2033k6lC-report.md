# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T01:15:51+08:00 |
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

- 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU中的图表征学习模块，该模块利用图摘要技术对原图快照进行压缩，并将压缩后的新图输入图自编码器，通过重构误差训练原图节点的表征，从而高效处理大规模动态图的表征学习。
- 提出了GSAERU模型中的时序学习模块，该模块在获得单时间步图表征后，采用循环神经网络学习原图在时间维度上的特征信息与依赖关系，从而得到大规模时序图的高质量表征。
- 提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，领导节点基于边分割的图流划分算法划分原图并分配子图给工作节点，工作节点执行基于图摘要的小批量训练，并通过注意力层返回训练结果给领导节点，领导节点汇总结果计算梯度并同步更新所有计算节点上的模型，从而加速大规模图流数据的GNN训练。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU中的图表征学习模块，该模块利用图摘要技术对原图快照进行压缩，并将压缩后的新图输入图自编码器，通过重构误差训练原图节点的表征，从而高效处理大规模动态图的表征学习。 | Proposed a graph representation learning module in GSAERU, a large-scale sequential graph representation learning method based on graph summarization, which compresses the original graph snapshot using graph summarization technology, feeds the compressed graph into a graph autoencoder, and trains node representations via reconstruction error, efficiently handling representation learning on large-scale dynamic graphs. |
| NP-2 | 提出了GSAERU模型中的时序学习模块，该模块在获得单时间步图表征后，采用循环神经网络学习原图在时间维度上的特征信息与依赖关系，从而得到大规模时序图的高质量表征。 | Proposed the time sequence learning module in the GSAERU model, which, after obtaining graph representation at a single time step, uses a recurrent neural network to learn the feature information and dependencies of the original graph along the time dimension, thereby obtaining high-quality representations for large-scale sequential graphs. |
| NP-3 | 提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，领导节点基于边分割的图流划分算法划分原图并分配子图给工作节点，工作节点执行基于图摘要的小批量训练，并通过注意力层返回训练结果给领导节点，领导节点汇总结果计算梯度并同步更新所有计算节点上的模型，从而加速大规模图流数据的GNN训练。 | Proposed a distributed graph neural network optimization training algorithm DSGNN based on graph summarization, which adopts a leader-worker mode. The leader divides the original graph using a graph flow partition algorithm based on edge segmentation, assigns subgraphs to workers; workers perform mini-batch training based on graph summarization, return training results to the leader through an attention layer; the leader aggregates results, computes gradients, and synchronously updates models on all computing nodes, thereby accelerating GNN training on large-scale graph streaming data. |

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
  - `ti:large-scale AND ti:dynamic AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder" AND abs:"reconstruction error"`（arxiv；执行失败）
  - `ti:large-scale AND ti:dynamic AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder" AND abs:"reconstruction error"`（arxiv；执行失败）
  - `"large-scale dynamic graph representation learning" AND "graph summarization" AND "graph autoencoder" AND "reconstruction error"`（springer；执行失败）
  - `ti:large-scale AND ti:dynamic AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder" AND abs:"reconstruction error"`（arxiv；执行失败）
  - `"large-scale dynamic graph representation learning" AND "graph summarization" AND "graph autoencoder" AND "reconstruction error"`（springer；执行失败）
  - `ti:large-scale AND ti:dynamic AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder" AND abs:"reconstruction error"`（arxiv；执行失败）
  - `"large-scale dynamic graph representation learning" AND "graph summarization" AND "graph autoencoder" AND "reconstruction error"`（springer；执行失败）
  - `ti:large-scale AND ti:dynamic AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder" AND abs:"reconstruction error"`（arxiv；执行失败）
  - `"dynamic graph representation learning" AND "graph summarization" AND "graph autoencoder"`（springer；有命中）
  - `("dynamic graph representation learning" OR "dynamic graph embedding" OR "temporal graph embedding") AND ("graph summarization" OR "graph sketching" OR "graph compression") AND ("graph autoencoder" OR "graph auto-encoder" OR "graph neural autoencoder") AND ("reconstruction error" OR "reconstruction loss")`（springer；有命中）
  - `("dynamic graph representation learning" OR "dynamic graph embedding" OR "temporal graph embedding") OR ("graph summarization" OR "graph sketching" OR "graph compression") OR ("graph autoencoder" OR "graph auto-encoder" OR "graph neural autoencoder") OR ("reconstruction error" OR "reconstruction loss") OR ("large-scale graphs" OR "large graphs" OR "scalable graph")`（springer；部分成功）
  - `"dynamic graph representation learning" AND "graph summarization" AND "graph autoencoder"`（springer；有命中）
  - `("dynamic graph representation learning" OR "dynamic graph embedding" OR "temporal graph embedding") AND ("graph summarization" OR "graph sketching" OR "graph compression") AND ("graph autoencoder" OR "graph auto-encoder" OR "graph neural autoencoder") AND ("reconstruction error" OR "reconstruction loss")`（springer；有命中）
  - `("dynamic graph representation learning" OR "dynamic graph embedding" OR "temporal graph embedding") OR ("graph summarization" OR "graph sketching" OR "graph compression") OR ("graph autoencoder" OR "graph auto-encoder" OR "graph neural autoencoder") OR ("reconstruction error" OR "reconstruction loss") OR ("large-scale graphs" OR "large graphs" OR "scalable graph")`（springer；部分成功）
  - `ti:dynamic AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder"`（arxiv；执行失败）
  - `ti:dynamic AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder"`（arxiv；执行失败）
  - `ti:dynamic AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder"`（arxiv；执行失败）
  - `ti:dynamic AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder"`（arxiv；执行失败）
  - `ti:dynamic AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder"`（arxiv；执行失败）
- **NP-2**
  - `abs:time AND abs:sequence AND abs:learning AND abs:module AND abs:"recurrent neural network" AND ti:"graph representation" AND ti:"sequential graph"`（arxiv；执行失败）
  - `"time sequence learning module" AND "recurrent neural network" AND "graph representation" AND "sequential graph"`（springer；执行失败）
  - `abs:time AND abs:sequence AND abs:learning AND abs:module AND abs:"recurrent neural network" AND ti:"graph representation" AND ti:"sequential graph"`（arxiv；执行失败）
  - `"time sequence learning module" AND "recurrent neural network" AND "graph representation" AND "sequential graph"`（springer；执行失败）
  - `abs:time AND abs:sequence AND abs:learning AND abs:module AND abs:"recurrent neural network" AND ti:"graph representation" AND ti:"sequential graph"`（arxiv；执行失败）
  - `"time sequence learning module" AND "recurrent neural network" AND "graph representation" AND "sequential graph"`（springer；执行失败）
  - `abs:time AND abs:sequence AND abs:learning AND abs:module AND abs:"recurrent neural network" AND ti:"graph representation" AND ti:"sequential graph"`（arxiv；执行失败）
  - `"time sequence learning module" AND "recurrent neural network" AND "graph representation" AND "sequential graph"`（springer；执行失败）
- **NP-3**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；执行失败）
  - `"distributed graph neural network training" AND "graph summarization"`（springer；执行失败）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；执行失败）
  - `"distributed graph neural network training" AND "graph summarization"`（springer；执行失败）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；执行失败）
  - `"distributed graph neural network training" AND "graph summarization"`（springer；执行失败）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；执行失败）
  - `"distributed graph neural network training" AND "graph summarization"`（springer；执行失败）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 4 张原始证据卡；通过 4 张，拒绝 0 张。

### 6.2 相关文献

### card_cf28e0a52ecc91e4ad9f7fce · Inductive Representation Learning on Temporal Graphs

- 查新点：NP-2
- 主要贡献：The TGAT (Temporal Graph Attention) paper proposes a temporal graph attention layer for inductive representation learning on temporal graphs, capturing temporal patterns and time-feature interactions in dynamic networks.
- 相关性：0.60
- 置信度：0.80
- 来源：
  - Inductive Representation Learning on Temporal Graphs：https://arxiv.org/pdf/2002.07962
    - 引文：The evolving nature of temporal dynamic graphs requires handling new nodes as well as capturing temporal patterns.
    - 位置：artifact art_b8b821043e4485fda0b8527c chars:138-252
  - Inductive Representation Learning on Temporal Graphs：https://arxiv.org/pdf/2002.07962
    - 引文：node and topological features can be temporal as well, whose patterns the node embeddings should also capture.
    - 位置：artifact art_b8b821043e4485fda0b8527c chars:405-515

### card_d945c1184970a3ae1a99577c · Temporal Graph Networks for Deep Learning on Dynamic Graphs

- 查新点：NP-2
- 主要贡献：The TGN (Temporal Graph Networks) paper presents a generic framework for deep learning on dynamic graphs represented as sequences of timed events, using memory modules and graph-based operators.
- 相关性：0.55
- 置信度：0.75
- 来源：
  - Temporal Graph Networks for Deep Learning on Dynamic Graphs：https://arxiv.org/pdf/2006.10637
    - 引文：few approaches have been proposed thus far for dealing with graphs that present some sort of dynamic nature (e.g. evolving features or connectivity over time).
    - 位置：artifact art_ea01d9c5f48ad68092a07bf7 chars:345-504

### card_aa25ed3e8470d10b41e76db6 · AGL: a Scalable System for Industrial-purpose Graph Machine Learning

- 查新点：NP-3
- 主要贡献：AGL is a scalable, fault-tolerant, integrated system for GNN training and inference on billion-scale graphs, using k-hop neighborhood generation and parameter server-based training.
- 相关性：0.40
- 置信度：0.85
- 来源：
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：we simply do the training on parameter servers due to data independency
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1562-1633

### card_3b8f1788e9b7c9f0a58b17d3 · AliGraph: A Comprehensive Graph Neural Network Platform

- 查新点：NP-3
- 主要贡献：AliGraph is a comprehensive distributed graph neural network platform with distributed graph storage, optimized sampling operators and runtime to support GNN training on large-scale graph data (billions of edges).
- 相关性：0.45
- 置信度：0.85
- 来源：
  - AliGraph: A Comprehensive Graph Neural Network Platform：https://arxiv.org/pdf/1902.08730
    - 引文：we present a comprehensive graph neural network system, namely AliGraph, which consists of distributed graph storage, optimized sampling operators and runtime to efficiently support not only existing popular GNNs but also a series of in-house developed ones for different scenarios.
    - 位置：artifact art_d88778158223021b818fdd97 chars:649-931

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 0 | 0 Card |
| NP-2 | 2 | 有证据 |
| NP-3 | 2 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出了一种基于图摘要的大规模时序图表示学习方法GSAERU中的图表征学习模块，该模块利用图摘要技术对原图快照进行压缩，并将压缩后的新图输入图自编码器，通过重构误差训练原图节点的表征，从而高效处理大规模动态图的表征学习。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 当前查新点未绑定任何有效证据卡，未能形成可靠的新颖性判定。检索覆盖执行事实未提供，无法区分是检索失败、成功零命中还是证据门控拒绝。需要补充针对图摘要压缩动态图快照并配合图自编码器训练的相关文献检索。  
**高度相关 Work：**
  - 无

### NP-2 · 部分新颖

提出了GSAERU模型中的时序学习模块，该模块在获得单时间步图表征后，采用循环神经网络学习原图在时间维度上的特征信息与依赖关系，从而得到大规模时序图的高质量表征。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 综合两篇已核验文献（TGAT 与 TGN）的判定，二者均与查新点同属时序图表示学习领域，在目标层面（捕捉时间模式与依赖）存在重叠，但都未公开查新点的核心组合特征——将单时间步图表征输入循环神经网络（RNN）形成时序学习模块。TGAT 采用自注意力+函数式时间编码，TGN 采用记忆模块与图算子，均非 RNN 时序学习路径，故不能视为单篇公开完整组合。两篇文献仅分别公开了目标相关部分，未覆盖完整技术组合，因此判定为部分新颖。需进一步补检采用 RNN/LSTM/GRU 的时序图模型（如 DynAERNN、EvolveGCN、DySAT、GCRN）以确认是否存在完整公开。  
**置信度：** 0.70  
**报告摘要：** 有两篇部分相关的时序图表征学习文献（TGAT、TGN），均捕捉了时序图的时间模式，但未采用“将单时间步图表征输入循环神经网络”的时序学习模块，也未覆盖该完整技术组合。因此查新点整体具有部分新颖性，但需进一步检索RNN类时序图模型以排除潜在完整公开。  
**高度相关 Work：**
  - wrk_b6b76b1dae1837f54a226290：TGAT 处理时序图表征学习，目标重叠，但采用自注意力/函数时间编码，未采用 RNN 时序学习模块，故为部分相关基线。 (cards: card_cf28e0a52ecc91e4ad9f7fce)
  - wrk_712252459ef2697739d75d40：TGN 提出动态图深度学习框架，目标相关，但采用记忆模块与图算子，未采用单时间步图表征输入 RNN 的路径。 (cards: card_d945c1184970a3ae1a99577c)

### NP-3 · 部分新颖

提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，领导节点基于边分割的图流划分算法划分原图并分配子图给工作节点，工作节点执行基于图摘要的小批量训练，并通过注意力层返回训练结果给领导节点，领导节点汇总结果计算梯度并同步更新所有计算节点上的模型，从而加速大规模图流数据的GNN训练。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 核验的两篇文献（AGL、AliGraph）均仅在大规模分布式GNN训练的目标层面或主从式架构上与查新点部分重叠，未覆盖DSGNN的核心技术组合（基于边分割的图流划分、基于图摘要的小批量训练、注意力层返回结果、面向图流数据）。单篇文献均未完整公开该组合，亦无证据表明该组合已由任何单篇文献整体公开，故查新点整体仍具部分新颖性。因仅核验两篇背景文献且均缺失关键特征，核心组合未被现有证据否定，但证据覆盖有限，需补充检索以确认完整组合的新颖性。  
**置信度：** 0.75  
**报告摘要：** 现有两篇分布式GNN框架文献（AGL、AliGraph）在目标或主从架构上与查新点部分重叠，但均未覆盖DSGNN的核心组合（边分割图流划分、图摘要小批量训练、注意力层返回结果、面向图流数据）。单篇文献均未完整公开该组合，因此查新点具有部分新颖性，但证据覆盖有限，需补充检索确认。  
**高度相关 Work：**
  - wrk_ff5aa18cf0cfe7be1ba5e8bd：部分相关：AGL采用参数服务器（主从式）架构进行大规模图GNN分布式训练，与查新点的领导-工作者模式及同步更新模型存在部分对应；但缺少边分割图流划分、图摘要小批量训练、注意力层返回结果等核心特征，未覆盖查新点的完整组合。 (cards: card_aa25ed3e8470d10b41e76db6)
  - wrk_e59b8b7248dcc080455b8690：部分相关：AliGraph是面向大规模图数据的分布式GNN训练平台，但仅在目标层面重叠；其机制（分布式图存储、优化采样算子、运行时）与查新点的领导-工作者模式、边分割图流划分、图摘要小批量训练、注意力层聚合等特征均无交集，不覆盖核心组合。 (cards: card_3b8f1788e9b7c9f0a58b17d3)

---

## 八、报告局限

- NP-1 当前无有效证据卡，且检索覆盖执行事实未提供，无法判定是检索失败还是成功零命中；本次报告只能判定为证据不足，需补充检索。
- NP-2 与 NP-3 已形成有效证据卡，但相关文献均为部分相关，未完整覆盖查新点技术组合；由于检索覆盖信息不完整，不排除存在更相关文献未检出的可能。
- 被拒绝证据为空，不存在因技术性质疑或格式性拒绝而未通过证据门控的情况。

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

- A Survey of Link Prediction in Temporal Networks：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s42979-025-04639-1](http://link.springer.com/openurl/pdf?id=doi:10.1007/s42979-025-04639-1)
- A Novel Hybrid Transformer-Based Framework for Reconstruction-Based ECG Anomaly Detection：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31998-2_15](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31998-2_15)
- Mean-Field Variational Graph Autoencoders for Data Generation: An Application to Urban Environmental Exposure Data：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38404-1_52](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38404-1_52)
- Persistence Diagram Features for Multivariate Time-Series Anomaly Detection：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38404-1_47](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38404-1_47)
- Inferring Gene Regulatory Networks in Stem Cells: Methods and Applications：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-1-0716-5539-9_1](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-1-0716-5539-9_1)
- Bayesian Uncertainty-Aware Multi-task Learning for Remote Sensing Image-Text Retrieval：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38404-1_45](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38404-1_45)
- Contamination Source Isolation in Water Distribution Networks via Sensor-Only Contrastive Graph Learning：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38404-1_55](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38404-1_55)
- Spike-Transmission Delays Improve the Accuracy–Efficiency Trade-Off for Linear Readouts of Spiking Populations：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38398-3_23](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38398-3_23)
- Inductive Representation Learning on Temporal Graphs：[https://arxiv.org/pdf/2002.07962](https://arxiv.org/pdf/2002.07962)
- Temporal Graph Networks for Deep Learning on Dynamic Graphs：[https://arxiv.org/pdf/2006.10637](https://arxiv.org/pdf/2006.10637)
- AliGraph: A Comprehensive Graph Neural Network Platform：[https://arxiv.org/pdf/1902.08730](https://arxiv.org/pdf/1902.08730)
- AGL: a Scalable System for Industrial-purpose Graph Machine Learning：[https://arxiv.org/pdf/2003.02454](https://arxiv.org/pdf/2003.02454)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
