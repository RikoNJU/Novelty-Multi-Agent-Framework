# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T20:40:25+08:00 |
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

- 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩原图并利用图自编码器与循环神经网络学习时序依赖，显著降低内存消耗和训练时间。
- 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，通过基于边分割的图流划分算法和基于图摘要的小批量训练，加速GNN训练并提升链路预测性能。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩原图并利用图自编码器与循环神经网络学习时序依赖，显著降低内存消耗和训练时间。 | Propose a large-scale sequential graph representation learning method GSAERU based on graph summarization, which compresses the original graph via graph summarization and uses a graph autoencoder and a recurrent neural network to learn temporal dependencies, significantly reducing memory consumption and training time. |
| NP-2 | 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，通过基于边分割的图流划分算法和基于图摘要的小批量训练，加速GNN训练并提升链路预测性能。 | Propose a distributed graph neural network optimization training algorithm DSGNN based on graph summarization, which adopts a leader-worker mode, uses an edge-segmentation-based graph stream partitioning algorithm and graph-summarization-based mini-batch training to accelerate GNN training and improve link prediction performance. |

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
  - `(abs:"graph summarization" OR abs:"graph autoencoder" OR abs:"recurrent neural network") AND (ti:"sequential graph" OR ti:"temporal graph" OR ti:"dynamic graph")`（arxiv；有命中）
  - `("graph summarization" OR "graph autoencoder" OR "recurrent neural network") AND ("sequential graph" OR "temporal graph" OR "dynamic graph")`（springer；有命中）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
  - `"distributed graph neural network" AND "graph summarization"`（springer；执行失败）
  - `"distributed graph neural network" AND "graph summarization"`（springer；执行失败）

---

## 六、检索结果

### 6.1 检索概况

共执行 1 轮检索计划，生成 5 张原始证据卡；通过 5 张，拒绝 0 张。

### 6.2 相关文献

### card_62cce85b10e07492d6d66e87 · Efficient Learning-based Graph Simulation for Temporal Graphs

- 查新点：NP-1
- 主要贡献：Proposes TGAE, an efficient learning-based temporal graph autoencoder for generating graph snapshots that reproduce structural and temporal properties of real-life temporal graphs.
- 相关性：0.40
- 置信度：0.60
- 来源：
  - Efficient Learning-based Graph Simulation for Temporal Graphs：10.1109/ICDE65448.2025.00026
    - 引文：we propose an efficient learning-based approach to generate graph snapshots, namely temporal graph autoencoder (TGAE).
    - 位置：artifact art_532328167974ec703a74ac56 chars:847-965

### card_1952fdeff8470d8ef6c188bd · Enhancing Distance-Based Graph Autoencoders with Structural Penalties for Dynamic Graph Embedding

- 查新点：NP-1
- 主要贡献：Proposes three distance-based graph autoencoder (GAE) variants with structural penalties (hub penalty and NC-LID-based regularization) for learning representations of dynamic graphs.
- 相关性：0.50
- 置信度：0.70
- 来源：
  - Enhancing Distance-Based Graph Autoencoders with Structural Penalties for Dynamic Graph Embedding：https://arxiv.org/pdf/2608.18762
    - 引文：Graph autoencoders (GAEs) are widely used for learning representations of dynamic graphs. However, their optimisation objectives typically do not take structural heterogeneity across nodes into account.
    - 位置：artifact art_af706d0f964352d23dd6c6fb chars:0-202

### card_59213b74260b971e4ef67509 · ReInc: Scaling Training of Dynamic Graph Neural Networks

- 查新点：NP-1
- 主要贡献：Presents ReInc, a system enabling efficient and scalable training of Dynamic Graph Neural Networks (DGNNs) on large-scale graphs by combining GNN and RNN components with incremental aggregation and caching.
- 相关性：0.50
- 置信度：0.70
- 来源：
  - ReInc: Scaling Training of Dynamic Graph Neural Networks：https://arxiv.org/pdf/2501.15348
    - 引文：ReInc introduces key innovations that capitalize on the unique combination of Graph Neural Networks (GNNs) and Recurrent Neural Networks (RNNs) inherent in DGNNs.
    - 位置：artifact art_6624d129a77360ef6e6e0a55 chars:336-498

### card_0bbbbd9ffac0fc04893533cb · AGL: a Scalable System for Industrial-purpose Graph Machine Learning

- 查新点：NP-2
- 主要贡献：AGL is a scalable, fault-tolerant, integrated distributed GNN system that generates k-hop neighborhoods as information-complete subgraphs and performs training on parameter servers.
- 相关性：0.45
- 置信度：0.70
- 来源：
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：the $k$-hop neighborhood contains information-complete subgraphs for each node, thus we simply do the training on parameter servers due to data independency.
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1477-1634

### card_b3631b654e6dc98339a9f88e · AliGraph: A Comprehensive Graph Neural Network Platform

- 查新点：NP-2
- 主要贡献：AliGraph is a comprehensive distributed graph neural network platform with distributed graph storage, optimized sampling operators and runtime to efficiently support GNN training at scale (billions of vertices/edges).
- 相关性：0.50
- 置信度：0.70
- 来源：
  - AliGraph: A Comprehensive Graph Neural Network Platform：https://arxiv.org/pdf/1902.08730
    - 引文：we present a comprehensive graph neural network system, namely AliGraph, which consists of distributed graph storage, optimized sampling operators and runtime to efficiently support not only existing popular GNNs but also a series of in-house developed ones for different scenarios.
    - 位置：artifact art_d88778158223021b818fdd97 chars:649-931

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 3 | 有证据 |
| NP-2 | 2 | 有证据 |

---

## 七、查新结论

### NP-1 · 部分新颖

提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩原图并利用图自编码器与循环神经网络学习时序依赖，显著降低内存消耗和训练时间。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 三篇单卡核验均未发现同时公开图摘要压缩、图自编码器、RNN时序依赖和原图重构误差训练这一完整组合的文献。TGAE仅覆盖快照序列建模与图自编码器，目标为图仿真而非节点表征学习；Enhancing Distance-Based GAEs仅覆盖动态图GAE与重构误差训练，未采用图摘要压缩和RNN；ReInc仅覆盖GNN+RNN时序学习与大规模高效训练目标，未采用图摘要压缩、图自编码器或重构误差训练。因此，现有证据仅显示各文献分别公开部分特征，未构成对NP-1核心组合的预先公开，判定为部分新颖。  
**置信度：** 0.70  
**报告摘要：** 针对NP-1（基于图摘要的大规模时序图表示学习方法GSAERU），本次检索找到三篇相关文献：TGAE（图自编码器与快照序列建模，目标为图仿真）、Enhancing Distance-Based GAEs（动态图GAE与重构误差训练）和ReInc（GNN+RNN时序学习与大规模高效训练）。三篇文献分别覆盖了GSAERU的部分技术特征，但均未同时采用图摘要压缩原图、图自编码器重构误差训练和RNN时序依赖学习这一完整组合，因此现有证据不构成对核心组合的预先公开。结合Reviewer裁定，NP-1为部分新颖。  
**高度相关 Work：**
  - wrk_bd8b204d16e97238a8fc4373：部分相关：TGAE使用时序图自编码器并建模快照序列，与GSAERU的图表征模块部分重叠；但目标为图仿真而非节点表征学习，且未采用图摘要压缩、RNN时序依赖学习及原图重构误差训练，未覆盖查新点核心组合。 (cards: card_62cce85b10e07492d6d66e87)
  - wrk_ebf843af1567659f61669ea5：该文使用图自编码器学习动态图表示并基于重构误差训练节点表征，与GSAERU的GAE+动态图组件重叠；但未采用图摘要压缩、未用RNN学习时序依赖，也未以降低内存/训练时间为目标，仅部分相关。 (cards: card_1952fdeff8470d8ef6c188bd)
  - wrk_61b66721dbe1b05f29512abd：ReInc与GSAERU共享GNN+RNN动态图时序学习方向及大规模图高效训练目标，但未采用图摘要压缩、图自编码器或重构误差训练，属部分相关基线，不覆盖核心组合。 (cards: card_59213b74260b971e4ef67509)

### NP-2 · 部分新颖

提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，通过基于边分割的图流划分算法和基于图摘要的小批量训练，加速GNN训练并提升链路预测性能。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 综合两张单卡核验结果：AGL 和 AliGraph 均属于分布式 GNN 训练系统，与 DSGNN 在分布式训练和加速目标上存在领域重叠，但均未公开 DSGNN 的核心特征组合，即“领导-工作者”模式、基于边分割的图流划分算法、基于图摘要的小批量训练、注意力层结果聚合以及跨节点同步梯度更新。单篇文献均未完整公开该组合，因此不能认定为完全公开。但两篇文献分别公开了分布式训练和加速的宽泛特征，部分覆盖了查新点的共性目标，故判定为部分新颖。  
**置信度：** 0.70  
**报告摘要：** 针对NP-2（基于图摘要的分布式图神经网络优化训练算法DSGNN），本次检索找到两篇分布式GNN系统文献：AGL（参数服务器协调的k-hop邻域生成）和AliGraph（分布式图存储与采样优化）。两篇文献与DSGNN在分布式训练和加速目标上部分重叠，但均未采用“领导-工作者”模式下的边分割图流划分算法、基于图摘要的小批量训练、注意力层结果聚合及跨节点同步梯度更新这一完整特征组合，因此不构成对DSGNN核心组合的公开。结合Reviewer裁定，NP-2为部分新颖。  
**高度相关 Work：**
  - wrk_ff5aa18cf0cfe7be1ba5e8bd：AGL 是分布式 GNN 训练系统，采用参数服务器协调（类似领导-工作者模式），与 DSGNN 在分布式训练领域重叠；但使用 k-hop 邻域而非图摘要小批量训练，无边分割图流划分、注意力层汇总及同步梯度更新，仅部分相关。 (cards: card_0bbbbd9ffac0fc04893533cb)
  - wrk_e59b8b7248dcc080455b8690：AliGraph 是分布式 GNN 训练平台，与 DSGNN 的分布式训练与加速目标部分重叠，但未采用领导-工作者模式、边分割图流划分、图摘要小批量训练、注意力层聚合与同步更新等核心特征，属部分相关文献，予以保留。 (cards: card_b3631b654e6dc98339a9f88e)

---

## 八、报告局限

- 本次检索的覆盖执行状况未在输入数据中明确给出，无法确认所有检索源是否均已成功执行；因此无法区分是检索失败、检索成功零命中或命中后未通过证据门控的情况。
- 当前报告基于有效EvidenceCard生成，未包含被拒绝证据（rejected_evidence为空），故无需说明门控拒绝原因。
- 检索结论仅基于本报告中列出的有效证据卡，若后续补充检索源执行信息或额外证据，可能需要重新评估结论。

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

- Enhancing Distance-Based Graph Autoencoders with Structural Penalties for Dynamic Graph Embedding：[https://arxiv.org/pdf/2608.18762](https://arxiv.org/pdf/2608.18762)
- Scalable and Efficient Joint Spiking Embedding Predictive Architecture for Large-Scale Dynamic Graphs：[https://arxiv.org/pdf/2607.18412](https://arxiv.org/pdf/2607.18412)
- Robustness of Spatio-temporal Graph Neural Networks for Fault Location in Partially Observable Distribution Grids：[https://arxiv.org/pdf/2604.20403](https://arxiv.org/pdf/2604.20403)
- GRExplainer: A Universal Explanation Method for Temporal Graph Neural Networks：[https://arxiv.org/pdf/2512.22772](https://arxiv.org/pdf/2512.22772)
- Efficient Learning-based Graph Simulation for Temporal Graphs：[https://arxiv.org/pdf/2510.05569](https://arxiv.org/pdf/2510.05569)
- GraphComp: Extreme Error-bounded Compression of Scientific Data via Temporal Graph Autoencoders：[https://arxiv.org/pdf/2505.06316](https://arxiv.org/pdf/2505.06316)
- ReInc: Scaling Training of Dynamic Graph Neural Networks：[https://arxiv.org/pdf/2501.15348](https://arxiv.org/pdf/2501.15348)
- Mind the truncation gap: challenges of learning on dynamic graphs with recurrent architectures：[https://arxiv.org/pdf/2412.21046](https://arxiv.org/pdf/2412.21046)
- Graph-Adaptive Horseshoe for Compositional Regression：[https://arxiv.org/pdf/2608.17858](https://arxiv.org/pdf/2608.17858)
- CGS: Configurable Graph Summarization with Bounded Neighborhood Loss and Query Support：[https://arxiv.org/pdf/2607.10969](https://arxiv.org/pdf/2607.10969)
- COREKG: Coreset-Guided Personalized Summarization of Knowledge Graphs：[https://arxiv.org/pdf/2605.14900](https://arxiv.org/pdf/2605.14900)
- Spectral Model eXplainer: a chemically-grounded explainability framework for spectral-based machine learning models：[https://arxiv.org/pdf/2605.02684](https://arxiv.org/pdf/2605.02684)
- A Null Model for Mapper Subtype Claims：[https://arxiv.org/pdf/2604.17395](https://arxiv.org/pdf/2604.17395)
- Explainable Mapper: Charting LLM Embedding Spaces Using Perturbation-Based Explanation and Verification Agents：[https://arxiv.org/pdf/2507.18607](https://arxiv.org/pdf/2507.18607)
- Causal DAG Summarization (Full Version)：[https://arxiv.org/pdf/2504.14937](https://arxiv.org/pdf/2504.14937)
- Code-Craft: Hierarchical Graph-Based Code Summarization for Enhanced Context Retrieval：[https://arxiv.org/pdf/2504.08975](https://arxiv.org/pdf/2504.08975)
- Real-Time Indian Sign Language Recognition Using Hierarchical Windowed Graph Attention Networks with Motion-Gated Inference and Multi-language Support：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31998-2_21](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31998-2_21)
- MinST: Multilevel Enhanced Architecture Search for Spatial-Temporal Forecasting with LLM：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38410-2_33](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38410-2_33)
- Graph Structure Learning with Dynamic Channel Fusion for Spatio-Temporal Anomaly Detection：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38410-2_56](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38410-2_56)
- A Multimodal GAN-Based Framework for Battery SOH Estimation Via Image and Signal Fusion：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3574-2_31](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3574-2_31)
- Forecasting Financial Variables from Structured Accounting Time Series with Echo State Networks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38404-1_39](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38404-1_39)
- Direction-Aware Heterogeneous Graph Neural Networks with Dual-Conditioned Normalizing Flows for Spatio-Temporal Anomaly Detection：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38407-2_17](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38407-2_17)
- Single-Stream Multi-feature Fusion with Temporal Robustness for Gait Emotion Recognition：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38401-0_41](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38401-0_41)
- Evaluation of Cross-Modal Data Fusion’s Present Situation in Intelligent Transportation Applications：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3566-7_27](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3566-7_27)
- AliGraph: A Comprehensive Graph Neural Network Platform：[https://arxiv.org/pdf/1902.08730](https://arxiv.org/pdf/1902.08730)
- AGL: a Scalable System for Industrial-purpose Graph Machine Learning：[https://arxiv.org/pdf/2003.02454](https://arxiv.org/pdf/2003.02454)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
