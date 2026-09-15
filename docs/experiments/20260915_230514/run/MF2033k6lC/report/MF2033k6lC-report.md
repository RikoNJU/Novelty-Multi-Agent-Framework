# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-15T23:30:44+08:00 |
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

- 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩图快照、图自编码器训练节点表征并结合循环神经网络学习时序依赖，实现高效生成大规模时序图的高质量表征。
- 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，领导节点利用基于边分割的图流划分算法划分原图，工作节点执行基于图摘要的小批量训练并通过注意力层返回结果，领导节点汇总梯度并同步更新所有节点模型，加速GNN训练并提升链路预测F1分数。
- 提出了一种基于图摘要的大规模图压缩技术，通过构建摘要图对原始图进行有效压缩，在保留关键结构信息的同时显著降低图的规模，从而减少图神经网络训练所需的计算和存储开销，可作为高效训练的基础技术。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩图快照、图自编码器训练节点表征并结合循环神经网络学习时序依赖，实现高效生成大规模时序图的高质量表征。 | Propose a large-scale sequential graph representation learning method GSAERU based on graph summarization, which compresses graph snapshots via graph summarization, trains node representations with a graph autoencoder, and integrates a recurrent neural network to learn temporal dependencies, efficiently generating high-quality representations of large-scale sequential graphs. |
| NP-2 | 提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，领导节点利用基于边分割的图流划分算法划分原图，工作节点执行基于图摘要的小批量训练并通过注意力层返回结果，领导节点汇总梯度并同步更新所有节点模型，加速GNN训练并提升链路预测F1分数。 | Propose a distributed graph neural network optimization training algorithm DSGNN based on graph summarization, which adopts a leader-worker mode. The leader partitions the original graph using an edge-based graph streaming partitioning algorithm, workers perform mini-batch training based on graph summarization and return results through an attention layer, and the leader aggregates gradients and synchronously updates all node models, accelerating GNN training and improving link prediction F1 score. |
| NP-3 | 提出了一种基于图摘要的大规模图压缩技术，通过构建摘要图对原始图进行有效压缩，在保留关键结构信息的同时显著降低图的规模，从而减少图神经网络训练所需的计算和存储开销，可作为高效训练的基础技术。 | Propose a large-scale graph compression technique based on graph summarization, which constructs a summarized graph to effectively compress the original graph while retaining key structural information, significantly reducing the graph scale and thereby decreasing computational and storage overhead for graph neural network training, serving as a foundation for efficient training. |

---

## 四、查新范围要求

检索范围围绕各查新点的中英文表述及技术特征展开。

---

## 五、文献检索范围及检索策略

### 5.1 检索来源

- link.springer.com

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
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning") AND ("graph summarization" OR "graph autoencoder" OR "recurrent neural network")`（springer；有命中）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning") AND ("graph summarization" OR "graph autoencoder" OR "recurrent neural network")`（springer；有命中）
  - `("sequential graph representation learning" OR "dynamic graph embedding" OR "temporal graph learning") AND ("graph summarization" OR "graph autoencoder" OR "recurrent neural network")`（springer；有命中）
  - `(ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:"temporal graph learning") AND (abs:"graph summarization" OR abs:"graph autoencoder" OR abs:"recurrent neural network")`（arxiv；执行失败）
  - `(ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:"temporal graph learning") AND (abs:"graph summarization" OR abs:"graph autoencoder" OR abs:"recurrent neural network")`（arxiv；执行失败）
  - `(ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:"temporal graph learning") AND (abs:"graph summarization" OR abs:"graph autoencoder" OR abs:"recurrent neural network")`（arxiv；执行失败）
  - `("sequential graph" OR "temporal graph" OR "dynamic graph") AND "graph summarization" AND "graph autoencoder" AND "recurrent neural network"`（springer；有命中）
  - `("sequential graph" OR "temporal graph" OR "dynamic graph" OR "time-evolving graph" OR "graph sequence") AND ("graph summarization" OR "graph summary" OR "graph compression") AND ("graph autoencoder" OR "graph neural network autoencoder" OR "GAE") AND ("recurrent neural network" OR "RNN" OR "temporal dependency learning") AND ("node representation learning" OR "node embedding" OR "graph representation learning")`（springer；有命中）
  - `("sequential graph" OR "temporal graph" OR "dynamic graph" OR "time-evolving graph" OR "graph sequence") OR ("graph summarization" OR "graph summary" OR "graph compression") OR ("graph autoencoder" OR "graph neural network autoencoder" OR "GAE") OR ("recurrent neural network" OR "RNN" OR "temporal dependency learning") OR ("large-scale graph" OR "large graph" OR "big graph") OR ("node representation learning" OR "node embedding" OR "graph representation learning")`（springer；部分成功）
  - `("sequential graph" OR "temporal graph" OR "dynamic graph") AND "graph summarization" AND "graph autoencoder" AND "recurrent neural network"`（springer；有命中）
  - `("sequential graph" OR "temporal graph" OR "dynamic graph" OR "time-evolving graph" OR "graph sequence") AND ("graph summarization" OR "graph summary" OR "graph compression") AND ("graph autoencoder" OR "graph neural network autoencoder" OR "GAE") AND ("recurrent neural network" OR "RNN" OR "temporal dependency learning") AND ("node representation learning" OR "node embedding" OR "graph representation learning")`（springer；有命中）
  - `("sequential graph" OR "temporal graph" OR "dynamic graph" OR "time-evolving graph" OR "graph sequence") OR ("graph summarization" OR "graph summary" OR "graph compression") OR ("graph autoencoder" OR "graph neural network autoencoder" OR "GAE") OR ("recurrent neural network" OR "RNN" OR "temporal dependency learning") OR ("large-scale graph" OR "large graph" OR "big graph") OR ("node representation learning" OR "node embedding" OR "graph representation learning")`（springer；部分成功）
  - `(ti:"sequential graph" OR ti:"temporal graph" OR ti:"dynamic graph") AND abs:"graph summarization" AND abs:"graph autoencoder" AND abs:"recurrent neural network"`（arxiv；执行失败）
  - `(ti:"sequential graph" OR ti:"temporal graph" OR ti:"dynamic graph") AND abs:"graph summarization" AND abs:"graph autoencoder" AND abs:"recurrent neural network"`（arxiv；执行失败）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；执行失败）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；执行失败）
  - `"distributed graph neural network training" AND "graph summarization"`（springer；执行失败）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；执行失败）
  - `"distributed graph neural network training" AND "graph summarization"`（springer；执行失败）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；执行失败）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"leader-worker mode"`（arxiv；执行失败）
  - `"distributed graph neural network training" AND "graph summarization" AND "leader-worker mode"`（springer；执行失败）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"leader-worker mode"`（arxiv；执行失败）
  - `"distributed graph neural network training" AND "graph summarization" AND "leader-worker mode"`（springer；执行失败）
- **NP-3**
  - `("graph summarization" OR "graph compression" OR "summarized graph")`（springer；有命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"summarized graph")`（arxiv；执行失败）
  - `"graph summarization" AND "graph compression"`（springer；有命中）
  - `abs:"graph summarization" AND abs:"graph compression"`（arxiv；执行失败）
  - `abs:"graph summarization" AND abs:"graph compression"`（arxiv；执行失败）
  - `abs:"graph summarization" AND abs:"graph compression"`（arxiv；执行失败）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 1 张原始证据卡；通过 1 张，拒绝 0 张。

### 6.2 相关文献

### card_33d40bba1a6120bc57edcd1c · A lossless graph summarization method for hierarchical and overlapping relational patterns mining

- 查新点：NP-3
- 主要贡献：Lossless graph summarization method for hierarchical and overlapping relational patterns mining, reducing processing time and storage overhead.
- 相关性：0.65
- 置信度：0.70
- 来源：
  - A lossless graph summarization method for hierarchical and overlapping relational patterns mining：10.1007/s10115-025-02482-7
    - 引文：graph summarization techniques, which provide a concise representation of graphs
    - 位置：artifact art_92081fc0a074636dc26e32f6 chars:227-307
  - A lossless graph summarization method for hierarchical and overlapping relational patterns mining：10.1007/s10115-025-02482-7
    - 引文：effective in reducing processing time and minimizing storage overhead
    - 位置：artifact art_92081fc0a074636dc26e32f6 chars:386-455
  - A lossless graph summarization method for hierarchical and overlapping relational patterns mining：10.1007/s10115-025-02482-7
    - 引文：achieves superior compression ratios on most datasets
    - 位置：artifact art_92081fc0a074636dc26e32f6 chars:1030-1083

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 0 | 0 Card |
| NP-2 | 0 | 0 Card |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要压缩图快照、图自编码器训练节点表征并结合循环神经网络学习时序依赖，实现高效生成大规模时序图的高质量表征。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 本查新点主张基于图摘要的大规模时序图表示学习方法（GSAERU），因最终有效证据卡数量为0，无法获得可供可靠性判定的证据，新颖性结论证据不足。本次检索执行覆盖情况不明，未形成有效证据卡，不能据此裁定新颖性或已有相同方法。  
**高度相关 Work：**
  - 无

### NP-2 · 证据不足，无法裁定

提出一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用“领导-工作者”模式，领导节点利用基于边分割的图流划分算法划分原图，工作节点执行基于图摘要的小批量训练并通过注意力层返回结果，领导节点汇总梯度并同步更新所有节点模型，加速GNN训练并提升链路预测F1分数。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 本查新点主张基于图摘要的分布式图神经网络优化训练算法（DSGNN），因最终有效证据卡数量为0，无法获得可供可靠性判定的证据，新颖性结论证据不足。本次检索执行覆盖情况不明，未形成有效证据卡，不能据此裁定新颖性或已有相同方法。  
**高度相关 Work：**
  - 无

### NP-3 · 部分新颖

提出了一种基于图摘要的大规模图压缩技术，通过构建摘要图对原始图进行有效压缩，在保留关键结构信息的同时显著降低图的规模，从而减少图神经网络训练所需的计算和存储开销，可作为高效训练的基础技术。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 现有证据（单篇图摘要压缩论文）已覆盖查新点特征1（构建摘要图）与特征3（降低规模、减少存储与计算开销），且部分涉及结构信息保留；但其下游目标为关系模式挖掘，而非查新点所主张的'作为图神经网络高效训练的基础、降低GNN训练计算与存储开销'这一核心应用落点。通用图摘要压缩机制为已知技术，而针对GNN训练的应用用途未被现有证据覆盖，故判定为部分新颖。  
**置信度：** 0.60  
**报告摘要：** 现有证据表明通用图摘要压缩机制（构建摘要图、降低规模与存储开销）为该领域已知技术，与查新点特征1和特征3重叠；但该证据的下游任务为关系模式挖掘，未针对'作为图神经网络高效训练基础、降低GNN训练计算与存储开销'这一核心落点，故判定为部分新颖。  
**高度相关 Work：**
  - wrk_046071475a00dcb5f580e93d：该论文明确提出基于图摘要（graph summarization）构建简洁图表示以降低规模、减少处理时间与存储开销并取得优越压缩比，直接对应查新点特征1和特征3；但目标是关系模式挖掘而非GNN训练，未覆盖查新点'作为GNN高效训练基础'的应用落点，故虽相关但仅部分佐证新颖性。 (cards: card_33d40bba1a6120bc57edcd1c)

---

## 八、报告局限

- 本报告仅包含1张有效证据卡，用于NP-3；该卡来源于一篇图摘要压缩论文，覆盖通用图摘要机制，但未覆盖NP-3的核心应用落点（图摘要用于GNN训练）。检索覆盖范围限于该单篇证据，其他来源（如GNN训练与图压缩结合的研究）未获得有效证据卡。
- NP-1与NP-2在本次检索中未获得任何有效证据卡。由于未收到明确的检索执行覆盖信息（如已执行数据库、结果命中等），无法区分检索失败与成功零命中，故不能认定'未检索到相关文献'，仅能说明证据不足。
- 未提供被拒绝证据（rejected_evidence为空），不存在因技术质疑或格式性问题被拒绝的证据卡。

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

- Direction-Aware Heterogeneous Graph Neural Networks with Dual-Conditioned Normalizing Flows for Spatio-Temporal Anomaly Detection：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38407-2_17](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-38407-2_17)
- Epidemiology-Informed Graph Neural Network for Heterogeneity-Aware Epidemic Forecasting：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37657-2_34](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37657-2_34)
- Utility-Aware Runtime Assessment of Sensor Selection Based on Spatio-Temporal Dynamic Graph Learning：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3994-8_6](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3994-8_6)
- HBPC-GWN: Hierarchical Bayesian Calibration for Graph-Based Traffic Forecasting：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3410-3_21](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3410-3_21)
- A Physics-Informed Spatio-temporal Graph Learning Framework for EV Charging Demand Forecasting：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3551-3_13](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3551-3_13)
- Dynamic Spatiotemporal Graph Learning of EEG for Multi-type Epileptiform Event Detection：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3716-6_21](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3716-6_21)
- UOT-GraphSSM: Unbalanced Optimal Transport Meets Graph State Space Models for Physics-Informed Spatio-temporal Traffic Forecasting：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3384-7_26](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-3384-7_26)
- KESTM: Knowledge-Enhanced Spatio-Temporal Module with Adaptive Gating for Dynamic Node Classification：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-2852-2_1](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-2852-2_1)
- CaTSCAN: Calculating Typed Subgraph Counts Analytically for Networks：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37657-2_31](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37657-2_31)
- Temporal Graph Classification Based on Fast and Exact Transitive Reduction Strategy：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37673-2_25](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-37673-2_25)
- A Multi-heuristic Approach to Workload Placement in Virtualisation Environments：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-32732-1_30](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-32732-1_30)
- TimeAgent: From Matches to Memories—Timeline Summarization for Sports Analytics：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-36033-5_28](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-36033-5_28)
- Part-GNN: A Partitioning-Based Graph Neural Network for Efficient Memory Large Scale Data Classification：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-2597-2_39](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-92-2597-2_39)
- Design of a Query Expression for Multi-Dimensional Graph Warehousing：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-32726-0_4](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-32726-0_4)
- MambaDDI: A Hybrid State Space Framework for Multiclass Drug–Drug Interaction Prediction：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-35390-0_17](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-35390-0_17)
- A Saliency-Driven Graph-Based Metric for fMRI-Based Visual Brain Decoding Evaluation：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31438-3_17](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-31438-3_17)
- A Survey of Link Prediction in Temporal Networks：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s42979-025-04639-1](http://link.springer.com/openurl/pdf?id=doi:10.1007/s42979-025-04639-1)
- Graph Neural Networks (GNNs)：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-95-6091-2_7](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-981-95-6091-2_7)
- Graph neural networks: Historical backgrounds, present revolutions, and conventionalization for the future：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s41060-025-00797-w](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s41060-025-00797-w)
- GraphXAI: a survey of graph neural networks (GNNs) for explainable AI (XAI)：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00521-025-11054-3](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s00521-025-11054-3)
- Graph Interpretation, Summarization and Visualization Techniques: A Review and Open Research Issues：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11042-021-11582-9](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11042-021-11582-9)
- Graph Neural Networks for Molecules：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-031-37196-7_2](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-031-37196-7_2)
- Network representation learning: models, methods and applications：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s42452-019-1044-9](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s42452-019-1044-9)
- Valorization of Low Quality Dates for Syrup Production: Effect of Processing Conditions on Chemical Functional Properties：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-16581-7_121](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-16581-7_121)
- Temporal and linguistic enrichment for abstractive text summarization using transformer models：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s44163-026-01710-5](http://link.springer.com/openurl/pdf?id=doi:10.1007/s44163-026-01710-5)
- Context-aware heterogeneous graph neural networks with attention-based pooling for long-document summarization：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10115-026-02809-y](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10115-026-02809-y)
- Graph Summarization Using Visual Data Mining Techniques：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-20362-5_14](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-20362-5_14)
- Research on Emergency Response Attack Scenario Reconstruction Method Based on Steiner Trees：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-20080-8_11](http://link.springer.com/openurl/fulltext?id=doi:10.1007/978-3-032-20080-8_11)
- GAME+: lossless knowledge-graph compression for improving the efficiency and effectiveness of rule mining：[http://link.springer.com/openurl/pdf?id=doi:10.1007/s41060-025-00911-y](http://link.springer.com/openurl/pdf?id=doi:10.1007/s41060-025-00911-y)
- A lossless graph summarization method for hierarchical and overlapping relational patterns mining：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10115-025-02482-7](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s10115-025-02482-7)
- Mining structure overlaps for efficient graph compression：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s41060-024-00711-w](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s41060-024-00711-w)
- A Summarization-Based Pattern-Aware Matrix Reordering Approach：[http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11390-025-5275-5](http://link.springer.com/openurl/fulltext?id=doi:10.1007/s11390-025-5275-5)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
