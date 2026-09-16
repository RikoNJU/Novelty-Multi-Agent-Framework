# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T21:18:16+08:00 |
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

- 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩原始图并利用图自编码器与循环神经网络学习时序图的高质量表征，在保持性能的同时显著降低内存消耗和训练时间。
- 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，结合基于边分割的图流划分与图摘要小批量训练，并通过注意力层汇总梯度，加速大规模图流数据的GNN训练并提升链路预测性能。
- 提出一种基于边分割的图流划分算法，用于在大规模图数据中高效划分子图并分配给分布式计算节点，支持后续图神经网络训练。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩原始图并利用图自编码器与循环神经网络学习时序图的高质量表征，在保持性能的同时显著降低内存消耗和训练时间。 | Proposed GSAERU, a large-scale sequential graph representation learning method based on graph summarization, which compresses the original graph via graph summarization and learns high-quality representations of sequential graphs using a graph autoencoder and a recurrent neural network, significantly reducing memory consumption and training time while maintaining performance. |
| NP-2 | 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，结合基于边分割的图流划分与图摘要小批量训练，并通过注意力层汇总梯度，加速大规模图流数据的GNN训练并提升链路预测性能。 | Proposed DSGNN, a distributed graph neural network optimization training algorithm based on graph summarization, which adopts a leader-worker mode, combines edge-partition-based graph streaming partitioning with graph summarization based mini-batch training, and aggregates gradients through an attention layer, accelerating GNN training on large-scale graph streaming data and improving link prediction performance. |
| NP-3 | 提出一种基于边分割的图流划分算法，用于在大规模图数据中高效划分子图并分配给分布式计算节点，支持后续图神经网络训练。 | Proposed an edge-segmentation-based graph streaming partitioning algorithm for efficiently partitioning large-scale graphs into subgraphs and assigning them to distributed computing nodes, supporting subsequent graph neural network training. |

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
  - `abs:"graph summarization" AND abs:"graph autoencoder" AND abs:"recurrent neural network" AND ti:sequential AND ti:graph AND ti:representation AND ti:learning`（arxiv；零命中）
  - `abs:"graph summarization" AND abs:"graph autoencoder" AND abs:"recurrent neural network"`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening") AND (abs:"graph autoencoder" OR abs:"graph auto-encoder" OR abs:"GAE") AND (abs:"recurrent neural network" OR abs:"RNN" OR abs:"recurrent network") AND (ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"temporal graph embedding" OR ti:dynamic AND ti:graph AND ti:representation AND ti:learning) AND (abs:"large-scale graphs" OR abs:"large graphs" OR abs:"big graphs")`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening") AND (abs:"graph autoencoder" OR abs:"graph auto-encoder" OR abs:"GAE") AND (abs:"recurrent neural network" OR abs:"RNN" OR abs:"recurrent network") AND (ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"temporal graph embedding" OR ti:dynamic AND ti:graph AND ti:representation AND ti:learning)`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening") OR (abs:"graph autoencoder" OR abs:"graph auto-encoder" OR abs:"GAE") OR (abs:"recurrent neural network" OR abs:"RNN" OR abs:"recurrent network") OR (ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"temporal graph embedding" OR ti:dynamic AND ti:graph AND ti:representation AND ti:learning) OR (abs:"large-scale graphs" OR abs:"large graphs" OR abs:"big graphs") OR (all:"graph neural network" OR all:"GNN")`（arxiv；有命中）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
  - `"distributed graph neural network training" AND "graph summarization"`（springer；执行失败）
  - `"distributed graph neural network training" AND "graph summarization"`（springer；执行失败）
  - `"distributed graph neural network training" AND "graph summarization"`（springer；执行失败）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
- **NP-3**
  - `abs:"edge-based graph partitioning" AND abs:"graph streaming partitioning" AND ti:"large-scale graph"`（arxiv；零命中）
  - `abs:"edge-based graph partitioning" AND abs:"graph streaming partitioning"`（arxiv；零命中）
  - `(abs:"edge-based graph partitioning" OR abs:"edge-cut partitioning" OR abs:"edge segmentation partitioning") AND (abs:"graph streaming partitioning" OR abs:"streaming graph partition" OR abs:"online graph partitioning") AND (ti:"large-scale graph" OR ti:"big graph" OR ti:"massive graph") AND (abs:"distributed computing" OR abs:"distributed processing" OR abs:"parallel computing")`（arxiv；零命中）
  - `(abs:"edge-based graph partitioning" OR abs:"edge-cut partitioning" OR abs:"edge segmentation partitioning") AND (abs:"graph streaming partitioning" OR abs:"streaming graph partition" OR abs:"online graph partitioning") AND (abs:"distributed computing" OR abs:"distributed processing" OR abs:"parallel computing")`（arxiv；零命中）
  - `(abs:"edge-based graph partitioning" OR abs:"edge-cut partitioning" OR abs:"edge segmentation partitioning") OR (abs:"graph streaming partitioning" OR abs:"streaming graph partition" OR abs:"online graph partitioning") OR (ti:"large-scale graph" OR ti:"big graph" OR ti:"massive graph") OR (abs:"distributed computing" OR abs:"distributed processing" OR abs:"parallel computing") OR (abs:graph AND abs:neural AND abs:network AND abs:training OR abs:"GNN training" OR abs:"graph deep learning")`（arxiv；有命中）
  - `"edge-based graph partitioning" AND "graph streaming partitioning" AND "large-scale graph"`（springer；执行失败）
  - `"edge-based graph partitioning" AND "graph streaming partitioning" AND "large-scale graph"`（springer；执行失败）
  - `"edge-based graph partitioning" AND "graph streaming partitioning" AND "large-scale graph"`（springer；执行失败）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 7 张原始证据卡；通过 6 张，拒绝 1 张。

### 6.2 相关文献

### card_d3ae4ea3ad208a4f19e5be7c · Temporal Graph Networks for Deep Learning on Dynamic Graphs

- 查新点：NP-1
- 主要贡献：TGN (Temporal Graph Networks) proposes a generic framework for deep learning on dynamic graphs represented as sequences of timed events, combining memory modules and graph-based operators for efficient temporal graph representation learning.
- 相关性：0.40
- 置信度：0.70
- 来源：
  - Temporal Graph Networks for Deep Learning on Dynamic Graphs：https://arxiv.org/pdf/2006.10637
    - 引文：we present Temporal Graph Networks (TGNs), a generic, efficient framework for deep learning on dynamic graphs represented as sequences of timed events. Thanks to a novel combination of memory modules and graph-based operators, TGNs are able to significantly outperform previous approaches being at the same time more computationally efficient.
    - 位置：artifact art_ea01d9c5f48ad68092a07bf7 chars:520-863

### card_55686841fd4b42a31dadffda · AGL: a Scalable System for Industrial-purpose Graph Machine Learning

- 查新点：NP-2
- 主要贡献：Presents AGL, a scalable, fault-tolerant, and integrated system for GNN training and inference on large-scale graphs.
- 相关性：0.60
- 置信度：0.80
- 来源：
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：we design AGL, a scalable, fault-tolerance and integrated system, with fully-functional training and inference for GNNs
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1021-1140

### card_a26fed6b4e4dc766c41e615b · AliGraph: A Comprehensive Graph Neural Network Platform

- 查新点：NP-2
- 主要贡献：Presents AliGraph, a comprehensive distributed graph neural network platform with distributed graph storage, optimized sampling operators, and runtime to support GNN training at scale.
- 相关性：0.60
- 置信度：0.80
- 来源：
  - AliGraph: A Comprehensive Graph Neural Network Platform：https://arxiv.org/pdf/1902.08730
    - 引文：we present a comprehensive graph neural network system, namely AliGraph, which consists of distributed graph storage, optimized sampling operators and runtime to efficiently support not only existing popular GNNs but also a series of in-house developed ones for different scenarios.
    - 位置：artifact art_d88778158223021b818fdd97 chars:649-931

### card_65f5c414f816399ee6798635 · CGS: Configurable Graph Summarization with Bounded Neighborhood Loss and Query Support

- 查新点：NP-2
- 主要贡献：Presents CGS, a configurable graph summarization framework that generates compact summary graphs supporting multiple graph queries.
- 相关性：0.40
- 置信度：0.80
- 来源：
  - CGS: Configurable Graph Summarization with Bounded Neighborhood Loss and Query Support：https://arxiv.org/pdf/2607.10969
    - 引文：Given a large graph, how to generate a compact summary graph that is configurable by the user and supports multiple graph queries with either no loss or with high accuracy?
    - 位置：artifact art_8cfe012f091285d469fc0d05 chars:3383-3555

### card_995831471e543f92580d798c · GraphSAINT: Graph Sampling Based Inductive Learning Method

- 查新点：NP-2
- 主要贡献：Presents GraphSAINT, a graph sampling based inductive learning method that constructs minibatches by sampling the training graph for efficient GNN training.
- 相关性：0.50
- 置信度：0.80
- 来源：
  - GraphSAINT: Graph Sampling Based Inductive Learning Method：https://arxiv.org/pdf/1907.04931
    - 引文：GraphSAINT constructs minibatches by sampling the training graph, rather than the nodes or edges across GCN layers.
    - 位置：artifact art_4144023700aceff174c81183 chars:452-567

### card_aa25ed3e8470d10b41e76db6 · AGL: a Scalable System for Industrial-purpose Graph Machine Learning

- 查新点：NP-3
- 主要贡献：AGL proposes a scalable system for industrial-purpose graph machine learning that generates k-hop neighborhood subgraphs for each node and performs distributed GNN training on parameter servers, partitioning the large graph into information-complete subgraphs assigned to worker nodes.
- 相关性：0.45
- 置信度：0.60
- 来源：
  - AGL: a Scalable System for Industrial-purpose Graph Machine Learning：https://arxiv.org/pdf/2003.02454
    - 引文：We design to generate the $k$-hop neighborhood, an information-complete subgraph for each node, as well as do the inference simply by merging values from in-edge neighbors and propagating values to out-edge neighbors via MapReduce.
    - 位置：artifact art_6f98816ebc9005d24844fdfd chars:1232-1463

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 1 | 有证据 |
| NP-2 | 4 | 有证据 |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 部分新颖

提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩原始图并利用图自编码器与循环神经网络学习时序图的高质量表征，在保持性能的同时显著降低内存消耗和训练时间。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 已核验的TGN文献与查新点存在局部重叠：其将动态图建模为时序事件序列并追求计算效率，但未使用图摘要压缩原始图，未采用图自编码器及基于原始图的重构误差训练节点表征，也未显式利用RNN学习时间依赖。因此TGN仅公开了查新点组合中的部分特征，未整体公开'图摘要压缩+图自编码器+重构误差+RNN时序依赖'的完整组合。单篇证据不足以判定该方法已被完整提出，故判定为部分新颖。  
**置信度：** 0.75  
**报告摘要：** 支持证据为TGN文献（card_d3ae4ea3ad208a4f19e5be7c），该文献与查新点部分重叠，但未公开图摘要压缩、图自编码器及重构误差训练等核心组合特征，故判定为部分新颖。  
**高度相关 Work：**
  - wrk_712252459ef2697739d75d40：TGN是动态/时序图表示学习的代表性框架，与查新点目标（时序图表示学习、计算效率）及'时序事件序列'建模思路部分重叠，可作为对比基线，但未涉及图摘要压缩、图自编码器和重构误差机制。 (cards: card_d3ae4ea3ad208a4f19e5be7c)

### NP-2 · 新颖

提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者模式，结合基于边分割的图流划分与图摘要小批量训练，并通过注意力层汇总梯度，加速大规模图流数据的GNN训练并提升链路预测性能。

**Reviewer 裁定：** 新颖  
**裁定理由：** 综合4篇单卡证据：AGL、AliGraph、CGS和GraphSAINT均仅覆盖NP-2的单个或泛化特征（分布式GNN训练、图采样小批量、图摘要），没有任何一篇公开了'领导-工作者模式+基于边分割的图流划分+图摘要小批量训练+注意力层梯度聚合+同步更新'的完整组合。根据规则，多篇分别公开部分特征不能等同于单篇公开完整组合，因此该组合特征未被现有文献公开，本查新点相对于现有证据为novel。但证据覆盖有限，均为部分相关文献，且未发现直接组合的对照文献，置信度中等偏低。单卡AGL的not_novel结论基于其未覆盖核心组合，实际不构成否定性证据；GraphSAINT无work_id无法引用为高度相关文献。  
**置信度：** 0.60  
**报告摘要：** 支持证据为AGL、AliGraph、CGS和GraphSAINT四篇文献，均仅覆盖分布式GNN训练或图摘要等个别特征，未公开'领导-工作者模式+边分割图流划分+图摘要小批量+注意力梯度聚合'的完整组合，故判定为新颖。  
**高度相关 Work：**
  - wrk_ff5aa18cf0cfe7be1ba5e8bd：AGL是面向大规模图GNN训练的可扩展分布式系统，与DSGNN的分布式训练主题相关，但未采用领导-工作者模式、边分割图流划分、图摘要小批量或注意力梯度聚合，仅部分重叠，不覆盖核心组合。 (cards: card_55686841fd4b42a31dadffda)
  - wrk_e59b8b7248dcc080455b8690：AliGraph是综合图神经网络平台，在分布式GNN训练维度部分相关，但未涉及NP-2的领导-工作者、边分割图流划分、图摘要小批量及注意力梯度聚合等特征，不构成组合公开。 (cards: card_a26fed6b4e4dc766c41e615b)
  - wrk_f3889b4c6601b1aba4aab33b：CGS是图摘要框架，仅与'图摘要'概念弱相关，未涉及分布式训练、领导-工作者模式或梯度聚合，非组合基线。 (cards: card_65f5c414f816399ee6798635)

### NP-3 · 部分新颖

提出一种基于边分割的图流划分算法，用于在大规模图数据中高效划分子图并分配给分布式计算节点，支持后续图神经网络训练。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 单卡核验（card_aa25ed3e8470d10b41e76db6）表明 AGL 确实覆盖了'划分子图并分配给工作节点用于分布式 GNN 训练'以及'大规模图数据处理'（特征 3、4），但其划分依据为每个节点的 k-hop 邻域子图，而非基于边分割的图流划分；也未描述从流式数据中动态划分原图（特征 1、2）。该单篇文献未公开完整组合，仅部分特征重叠，不足以否定组合新颖性。因此判定为部分新颖，保留该文献作为部分相关引用。  
**置信度：** 0.60  
**报告摘要：** 支持证据为AGL文献（card_aa25ed3e8470d10b41e76db6），其覆盖了划分子图并分配给工作节点用于分布式GNN训练，但未采用边分割流式划分，特征部分重叠，故判定为部分新颖。  
**高度相关 Work：**
  - wrk_ff5aa18cf0cfe7be1ba5e8bd：将大规模图划分为 k-hop 邻域子图并分配至工作节点用于分布式 GNN 训练，覆盖'划分子图+分配工作节点+大规模分布式处理'特征，与查新点部分重叠，但划分方式为 k-hop 而非边分割流式划分。 (cards: card_aa25ed3e8470d10b41e76db6)

---

## 八、报告局限

- 检索覆盖未知：输入未提供检索执行成功与否的明确覆盖事实，无法区分检索失败或成功零命中。证据卡数量不代表来源执行成功，仅能依据现有有效证据卡进行裁定。
- 存在被拒绝证据：证据卡 card_8035bfa49d4ffae6dbe36d9e 因文献相关性低于门槛被拒绝，属于格式性拒绝（证据门控拒绝），并非技术性质疑。
- 有命中但未形成有效证据的说明：部分命中文献（如被拒绝的卡片）未通过证据门控，因其与查新点相关性不足，故未纳入证据支持。该拒绝不改变其余证据卡的有效性。
- 各查新点的证据覆盖均有限：NP-1仅单篇TGN，NP-2有四篇但均为部分相关，NP-3仅单篇AGL，未发现完整组合的直接公开文献。

---

## 九、附件及参考信息

### 缺失参考文献

无。

### 缺失 Baseline

无。

### 引用问题

无。

### 被拒绝证据

- card_8035bfa49d4ffae6dbe36d9e：文献相关性低于门槛

### 检索到的文献

- Graph-Adaptive Horseshoe for Compositional Regression：[https://arxiv.org/pdf/2608.17858](https://arxiv.org/pdf/2608.17858)
- CGS: Configurable Graph Summarization with Bounded Neighborhood Loss and Query Support：[https://arxiv.org/pdf/2607.10969](https://arxiv.org/pdf/2607.10969)
- COREKG: Coreset-Guided Personalized Summarization of Knowledge Graphs：[https://arxiv.org/pdf/2605.14900](https://arxiv.org/pdf/2605.14900)
- Spectral Model eXplainer: a chemically-grounded explainability framework for spectral-based machine learning models：[https://arxiv.org/pdf/2605.02684](https://arxiv.org/pdf/2605.02684)
- A Null Model for Mapper Subtype Claims：[https://arxiv.org/pdf/2604.17395](https://arxiv.org/pdf/2604.17395)
- Explainable Mapper: Charting LLM Embedding Spaces Using Perturbation-Based Explanation and Verification Agents：[https://arxiv.org/pdf/2507.18607](https://arxiv.org/pdf/2507.18607)
- Causal DAG Summarization (Full Version)：[https://arxiv.org/pdf/2504.14937](https://arxiv.org/pdf/2504.14937)
- Code-Craft: Hierarchical Graph-Based Code Summarization for Enhanced Context Retrieval：[https://arxiv.org/pdf/2504.08975](https://arxiv.org/pdf/2504.08975)
- Online Test-Time Adaptation for Generalizable Dynamic Graph Anomaly Detection：[https://arxiv.org/pdf/2608.19858](https://arxiv.org/pdf/2608.19858)
- Learning Sequential Mobility Choice: A Review of Route and Activity Choice through Inverse Reinforcement and Imitation Learning：[https://arxiv.org/pdf/2608.15339](https://arxiv.org/pdf/2608.15339)
- PLAN: Parallel Liquid-Inspired Approximation Network for Efficient Representation Learning in Flexible Job Shop Scheduling：[https://arxiv.org/pdf/2608.03041](https://arxiv.org/pdf/2608.03041)
- Learning Implicit Causal World Models from Multi-Agent Demonstrations：[https://arxiv.org/pdf/2607.26336](https://arxiv.org/pdf/2607.26336)
- Explainable graph attention network for stress recognition (StressGAT) via differential action units：[https://arxiv.org/pdf/2607.20819](https://arxiv.org/pdf/2607.20819)
- Dynamic Neural Graph Encoding of Inference Processes in Deep Weight Space：[https://arxiv.org/pdf/2607.02166](https://arxiv.org/pdf/2607.02166)
- Relational and Sequential Conformal Inference for Energy Time Series over Graphs via Foundation Models：[https://arxiv.org/pdf/2606.31804](https://arxiv.org/pdf/2606.31804)
- POEM: Partial-Order Enhanced Real-Time Sequential Modeling for Recommendation：[https://arxiv.org/pdf/2606.29946](https://arxiv.org/pdf/2606.29946)
- Repurposing Unified Topological Signatures for Graph Representation Learning：[https://arxiv.org/pdf/2609.17061](https://arxiv.org/pdf/2609.17061)
- Structural Negative Transfer in Federated Graph Neural Networks: Diagnosis, Causal Investigation, and the Limits of Divergence-Aware Mitigation：[https://arxiv.org/pdf/2609.16977](https://arxiv.org/pdf/2609.16977)
- Unified Heterogeneous Graph Neural Network solver for Power Flow, Optimal Power Flow and State Estimation：[https://arxiv.org/pdf/2609.16738](https://arxiv.org/pdf/2609.16738)
- Multi-Task Graph Neural Network Predictions of Auger-Electron and X-ray Photoelectron Spectroscopy：[https://arxiv.org/pdf/2609.16339](https://arxiv.org/pdf/2609.16339)
- Complete Suffix Prediction for Recommendation via Latent Retrieval over Process Graphs：[https://arxiv.org/pdf/2609.15692](https://arxiv.org/pdf/2609.15692)
- Benchmarking Machine-Learning Interatomic Potentials for Dynamical Stability in Inorganic Semiconductor Nanocrystals: A CdSe Case Study：[https://arxiv.org/pdf/2609.15299](https://arxiv.org/pdf/2609.15299)
- ProtoGuide: Prototype-Driven Guidance for Class-Conditional Graph Generation：[https://arxiv.org/pdf/2609.15239](https://arxiv.org/pdf/2609.15239)
- LiftGCN: Efficient Energy-Preserving Graph Learning via Joukowski Spectral Lifting for Finite Element Stress Prediction：[https://arxiv.org/pdf/2609.14977](https://arxiv.org/pdf/2609.14977)
- Temporal Graph Networks for Deep Learning on Dynamic Graphs：[https://arxiv.org/pdf/2006.10637](https://arxiv.org/pdf/2006.10637)
- AGL: a Scalable System for Industrial-purpose Graph Machine Learning：[https://arxiv.org/pdf/2003.02454](https://arxiv.org/pdf/2003.02454)
- AliGraph: A Comprehensive Graph Neural Network Platform：[https://arxiv.org/pdf/1902.08730](https://arxiv.org/pdf/1902.08730)
- GraphSAINT: Graph Sampling Based Inductive Learning Method：[https://arxiv.org/pdf/1907.04931](https://arxiv.org/pdf/1907.04931)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
