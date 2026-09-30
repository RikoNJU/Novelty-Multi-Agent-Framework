# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-30T15:14:44+08:00 |
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

- 提出了一种新的图表示学习模型——GSAERU，用于大规模时序图数据上的节点表征学习。
- 提出了一种新的基于图摘要的分布式图神经网络训练框架，称为DSGNN，用于分布式场景下的基于图神经网络的图表示学习。
- 提出了一种新的基于边分割的图流划分算法——Sketch-DBH，用于处理大规模图流数据下的子图划分问题。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出了一种新的图表示学习模型——GSAERU，用于大规模时序图数据上的节点表征学习。 | Proposed a new graph representation learning model - GSAERU, for node representation learning on large-scale sequential graphs. |
| NP-2 | 提出了一种新的基于图摘要的分布式图神经网络训练框架，称为DSGNN，用于分布式场景下的基于图神经网络的图表示学习。 | Proposed a new distributed graph neural network training framework based on graph summarization, called DSGNN, for graph representation learning based on graph neural networks in distributed scenarios. |
| NP-3 | 提出了一种新的基于边分割的图流划分算法——Sketch-DBH，用于处理大规模图流数据下的子图划分问题。 | Proposed a new edge-segmentation-based graph stream partitioning algorithm, called Sketch-DBH, for handling subgraph partitioning problems in large-scale graph stream data. |

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
  - `abs:"graph summarization technology" AND abs:graph AND abs:representation AND abs:learning AND abs:model`（arxiv；零命中）
  - `abs:"graph summarization technology" AND (abs:graph AND abs:representation AND abs:learning AND abs:model OR abs:"GSAERU")`（arxiv；零命中）
  - `abs:"graph summarization technology"`（arxiv；零命中）
  - `abs:"graph summarization technology"`（arxiv；零命中）
  - `abs:"graph summarization technology"`（arxiv；零命中）
  - `abs:"graph summarization technology"`（arxiv；零命中）
  - `"graph summarization technology" AND "graph representation learning model"`（springer；零命中）
  - `"graph summarization technology" AND ("graph representation learning model" OR "GSAERU")`（springer；零命中）
  - `"graph summarization technology"`（springer；零命中）
  - `"graph summarization technology"`（springer；零命中）
  - `"graph summarization technology"`（springer；零命中）
  - `"graph summarization technology"`（springer；零命中）
  - `abs:"graph summarization technology" AND abs:graph AND abs:representation AND abs:learning AND abs:model`（arxiv；零命中）
  - `abs:"graph summarization technology" AND (abs:graph AND abs:representation AND abs:learning AND abs:model OR abs:"GRLM")`（arxiv；零命中）
  - `abs:"graph summarization technology"`（arxiv；零命中）
  - `abs:graph AND abs:representation AND abs:learning AND abs:model`（arxiv；部分成功）
  - `(abs:graph AND abs:representation AND abs:learning AND abs:model OR abs:"GRLM")`（arxiv；有命中）
  - `abs:"graph summarization technology"`（arxiv；零命中）
- **NP-2**
  - `abs:distributed AND abs:graph AND abs:neural AND abs:network AND abs:training AND abs:framework`（arxiv；部分成功）
  - `(abs:distributed AND abs:graph AND abs:neural AND abs:network AND abs:training AND abs:framework OR abs:Distributed AND abs:GNN AND abs:Training AND abs:Framework)`（arxiv；部分成功）
  - `(abs:distributed AND abs:graph AND abs:neural AND abs:network AND abs:training AND abs:framework OR abs:Distributed AND abs:GNN AND abs:Training AND abs:Framework)`（arxiv；部分成功）
- **NP-3**
  - `abs:edge-segmentation-based AND abs:graph AND abs:stream AND abs:partitioning AND abs:algorithm`（arxiv；零命中）
  - `(abs:edge-segmentation-based AND abs:graph AND abs:stream AND abs:partitioning AND abs:algorithm OR abs:"Sketch-DBH")`（arxiv；有命中）
  - `(abs:edge-segmentation-based AND abs:graph AND abs:stream AND abs:partitioning AND abs:algorithm OR abs:"Sketch-DBH")`（arxiv；有命中）

---

## 六、检索结果

### 6.1 检索概况

记录 2 轮检索计划，生成 3 张原始证据卡；通过 3 张，拒绝 0 张。

### 6.2 相关文献

### card_bf391e8faabbbad19c9037e5 · BandPC: Learning Residual-Band Preconditioner Combinations for Flexible Conjugate Gradient Solvers

- 查新点：NP-2
- 主要贡献：Proposed a new distributed graph neural network training framework based on graph summarization, called DSGNN, for graph representation learning based on graph neural networks in distributed scenarios.
- 相关性：0.80
- 置信度：0.80
- 来源：
  - BandPC: Learning Residual-Band Preconditioner Combinations for Flexible Conjugate Gradient Solvers：https://arxiv.org/pdf/2609.37140
    - 引文：The conjugate gradient (CG) method is a classical iterative solver for sparse symmetric positive definite (SPD) linear systems, but its convergence strongly depends on the spectral properties of the system matrix.
    - 位置：artifact art_0446bb46fbcfea78eb5f5c57 chars:0-213
  - BandPC: Learning Residual-Band Preconditioner Combinations for Flexible Conjugate Gradient Solvers：https://arxiv.org/pdf/2609.37140
    - 引文：We propose BandPC (Band Preconditioner Combinations, where "Band" denotes residual-norm bands), a data-driven framework that leverages graph neural networks (GNNs) to predict multi-stage preconditioning strategies for the flexible conjugate gradient (FCG) method.
    - 位置：artifact art_0446bb46fbcfea78eb5f5c57 chars:379-642

### card_5f340eac084149c20c484d9b · ScaGNN: a Graph Neural Network for Multiple Scattering Simulations

- 查新点：NP-2
- 主要贡献：Proposed a new learning-based approach for simulating Multiple Scattering phenomena using the BEM framework in which a GNN is leveraged as a surrogate model for replacing the BIE solver, leading to a reduction of the simulation runtime by two orders of magnitude.
- 相关性：0.90
- 置信度：0.90
- 来源：
  - ScaGNN: a Graph Neural Network for Multiple Scattering Simulations：https://arxiv.org/pdf/2609.37509
    - 引文：We present a novel learning-based approach for simulating Multiple Scattering phenomena using the BEM framework in which a GNN is leveraged as a surrogate model for replacing the BIE solver. This leads to a reduction of the simulation runtime by two orders of magnitude.
    - 位置：artifact art_7a8f7ee2ba744847bdfb3edb chars:9004-9274

### card_8ba33651c1b41b8432c27c59 · EvoFormer: Learning Dynamic Graph-Level Representations with Structural and Temporal Bias Correction

- 查新点：NP-3
- 主要贡献：Proposed a new edge-segmentation-based graph stream partitioning algorithm, called Sketch-DBH, for handling subgraph partitioning problems in large-scale graph stream data.
- 相关性：0.80
- 置信度：0.90
- 来源：
  - EvoFormer: Learning Dynamic Graph-Level Representations with Structural and Temporal Bias Correction：10.1145/3746252.3761134
    - 引文：To overcome these challenges, we propose EvoFormer, an evolution-aware Transformer framework tailored for dynamic graph-level representation learning.
    - 位置：artifact art_ebfbc362d98aa3c6b0b68878 chars:566-716

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 0 | 0 Card |
| NP-2 | 2 | 有证据 |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 核验未完成，无法裁定

提出了一种新的图表示学习模型——GSAERU，用于大规模时序图数据上的节点表征学习。

**Reviewer 裁定：** 核验未完成，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** Reviewer 核验未完成，尚不能作出新颖性裁定。  
**未完成原因：** material_unavailable  
**高度相关 Work：**
  - 无

**原文核验证据：**
  - 无

### NP-2 · 证据不足，无法裁定

提出了一种新的基于图摘要的分布式图神经网络训练框架，称为DSGNN，用于分布式场景下的基于图神经网络的图表示学习。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**未完成原因：** semantic_evidence  
**高度相关 Work：**
  - wrk_6139004dcb0d88886d32c9d6：The evidence directly contradicts the claimed technical features by focusing on a different problem and approach. (cards: card_bf391e8faabbbad19c9037e5)
  - wrk_09214cbbc59fe401d9d390c5：The work focuses on using GNN as a surrogate model for BIE solver in BEM framework, which is different from the proposed DSGNN framework. (cards: card_5f340eac084149c20c484d9b)

**原文核验证据：**
  - 无

### NP-3 · 核验未完成，无法裁定

提出了一种新的基于边分割的图流划分算法——Sketch-DBH，用于处理大规模图流数据下的子图划分问题。

**Reviewer 裁定：** 核验未完成，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** Reviewer 核验未完成，尚不能作出新颖性裁定。  
**未完成原因：** technical_error  
**高度相关 Work：**
  - 无

**原文核验证据：**
  - 无

---

## 八、报告局限

- NP-1：Reviewer 核验未完成；原因：material_unavailable。
- NP-1：Reviewer 提出补查请求；原始请求保留在来源 Review，本报告节点未执行补查。
- NP-2：Reviewer 核验未完成；原因：semantic_evidence。
- NP-2：Reviewer 提出补查请求；原始请求保留在来源 Review，本报告节点未执行补查。
- NP-3：Reviewer 核验未完成；原因：technical_error。
- NP-3：Reviewer 提出补查请求；原始请求保留在来源 Review，本报告节点未执行补查。
- NP-1：已记录检索执行：arxiv 成功 11 次、失败 0 次、未执行 0 项、部分成功 1 次；springer 成功 6 次、失败 0 次、未执行 0 项。以上仅为已记录的执行范围，不代表完整检索或新颖性裁定。
- NP-2：已记录检索执行：arxiv 成功 0 次、失败 0 次、未执行 0 项、部分成功 3 次。以上仅为已记录的执行范围，不代表完整检索或新颖性裁定。
- NP-3：已记录检索执行：arxiv 成功 3 次、失败 0 次、未执行 0 项。以上仅为已记录的执行范围，不代表完整检索或新颖性裁定。
- 查新候选已保留供逐点研究；保留不代表其独立贡献已确认。特征保留账本不代表作者贡献已获语义确认，提取范围仍待核查。
- 部分单卡核验已保存，但查新点汇总未完成；局部核验不能替代最终裁定。
- NP-1 恢复停止：Configured round limit reached; unresolved evidence remains unresolved.
- NP-2 恢复停止：Configured round limit reached; unresolved evidence remains unresolved.

---

## 九、附件及参考信息

### 缺失参考文献

本节点输入未记录该类条目；不代表已核实为无。

### 缺失 Baseline

本节点输入未记录该类条目；不代表已核实为无。

### 引用问题

本节点输入未记录该类条目；不代表已核实为无。

### 被拒绝证据

本节点输入未记录该类条目；不代表已核实为无。

### 检索到的文献

- ScaGNN: a Graph Neural Network for Multiple Scattering Simulations：[https://arxiv.org/pdf/2609.37509](https://arxiv.org/pdf/2609.37509)
- BandPC: Learning Residual-Band Preconditioner Combinations for Flexible Conjugate Gradient Solvers：[https://arxiv.org/pdf/2609.37140](https://arxiv.org/pdf/2609.37140)
- Spectral Reversal: Counteracting Singular Value Bias for Graph Prompting：[https://arxiv.org/pdf/2609.32143](https://arxiv.org/pdf/2609.32143)
- Hard-Constrained Probabilistic Factor Graph Neural Network for Distribution System State Estimation under Non-Gaussian Uncertainty：[https://arxiv.org/pdf/2609.35246](https://arxiv.org/pdf/2609.35246)
- EvoFormer: Learning Dynamic Graph-Level Representations with Structural and Temporal Bias Correction：[https://arxiv.org/pdf/2508.15378](https://arxiv.org/pdf/2508.15378)
- A shape-similarity latent space for fluid interfaces: invertible reduced-order modelling of droplet morphology：[https://arxiv.org/pdf/2609.37947](https://arxiv.org/pdf/2609.37947)
- GRFBrain: Graph-Structured Rectified Flows for EEG Dynamic Modeling：[https://arxiv.org/pdf/2609.37934](https://arxiv.org/pdf/2609.37934)
- TopoEmbedX: A General Framework for Representation Learning on Topological Domains：[https://arxiv.org/pdf/2609.37884](https://arxiv.org/pdf/2609.37884)
- RLX: A Unified Multi-Backend Tensor Compiler and Distributed Runtime in Rust：[https://arxiv.org/pdf/2609.37916](https://arxiv.org/pdf/2609.37916)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
