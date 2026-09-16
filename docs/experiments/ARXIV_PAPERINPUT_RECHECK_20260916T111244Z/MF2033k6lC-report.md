# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T19:34:12+08:00 |
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

- 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，该方法通过图摘要技术压缩原图，利用图自编码器学习节点表征，并结合循环神经网络学习时间维度的特征和依赖关系，能够高效生成大规模时序图的低维表征。
- 提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者工作模式，领导节点利用基于边分割的图流划分算法划分图并将子图分配给工作者，工作者执行基于图摘要的小批量训练，通过注意力层返回结果，领导节点汇总计算梯度并同步更新所有模型，显著加速大规模图流的GNN训练。
- 提出了一种基于图摘要的图神经网络优化机制，通过图摘要技术对原始图数据进行压缩，在保留图主要结构和特征信息的同时大幅减少数据规模，从而降低图神经网络训练的内存消耗和计算成本，并可同时应用于大规模动态时序图的表示学习和分布式训练场景，有效提升了图神经网络的可扩展性和训练效率。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，该方法通过图摘要技术压缩原图，利用图自编码器学习节点表征，并结合循环神经网络学习时间维度的特征和依赖关系，能够高效生成大规模时序图的低维表征。 | Proposes a large-scale sequential graph representation learning method based on graph summarization, named GSAERU, which compresses the original graph via graph summarization, uses a graph autoencoder to learn node representations, and incorporates a recurrent neural network to learn temporal features and dependencies, efficiently generating high-quality low-dimensional representations for large-scale dynamic graphs. |
| NP-2 | 提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者工作模式，领导节点利用基于边分割的图流划分算法划分图并将子图分配给工作者，工作者执行基于图摘要的小批量训练，通过注意力层返回结果，领导节点汇总计算梯度并同步更新所有模型，显著加速大规模图流的GNN训练。 | Proposes a distributed graph neural network optimization training algorithm based on graph summarization, named DSGNN, which adopts a leader-worker mode: the leader partitions the graph using an edge-segmentation-based graph streaming algorithm, workers perform graph-summarization-based mini-batch training, results are returned to the leader through an attention layer, the leader aggregates results, computes gradients, and synchronously updates all models, greatly accelerating GNN training on large-scale graph streams. |
| NP-3 | 提出了一种基于图摘要的图神经网络优化机制，通过图摘要技术对原始图数据进行压缩，在保留图主要结构和特征信息的同时大幅减少数据规模，从而降低图神经网络训练的内存消耗和计算成本，并可同时应用于大规模动态时序图的表示学习和分布式训练场景，有效提升了图神经网络的可扩展性和训练效率。 | Proposes a graph neural network optimization mechanism based on graph summarization, which compresses the original graph data using graph summarization, substantially reducing data size while preserving key structure and feature information, thereby lowering memory consumption and computational cost for GNN training. This mechanism is applicable to both representation learning on large-scale dynamic graphs and distributed training scenarios, enhancing scalability and training efficiency of GNNs. |

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
  - `abs:"graph summarization" AND abs:"graph autoencoder"`（arxiv；有命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph summarization technique") AND (abs:"graph autoencoder" OR abs:"graph auto-encoder" OR abs:"GAE")`（arxiv；有命中）
  - `(abs:"graph summarization" OR abs:"graph compression" OR abs:"graph summarization technique") OR (abs:"graph autoencoder" OR abs:"graph auto-encoder" OR abs:"GAE") OR (abs:"recurrent neural network" OR abs:"RNN") OR (ti:"large-scale dynamic graph" OR ti:"large-scale temporal graph" OR ti:"large-scale sequential graph")`（arxiv；部分成功）
  - `ti:dynamic AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
- **NP-3**
  - `ti:"graph neural network" AND abs:"graph summarization"`（arxiv；有命中）
  - `(ti:"graph neural network" OR ti:"GNN" OR ti:"graph neural networks") AND (abs:"graph summarization" OR abs:"graph summarisation" OR abs:"graph compression")`（arxiv；有命中）
  - `(ti:"graph neural network" OR ti:"GNN" OR ti:"graph neural networks") OR (abs:"graph summarization" OR abs:"graph summarisation" OR abs:"graph compression") OR (abs:"compressed graph" OR abs:"summarized graph" OR abs:"graph summary") OR (all:"graph autoencoder" OR all:"graph auto-encoder")`（arxiv；部分成功）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 3 张原始证据卡；通过 3 张，拒绝 0 张。

### 6.2 相关文献

### card_369a02f1d029252af70a4638 · A Comprehensive Survey on Graph Summarization with Graph Neural Networks

- 查新点：NP-3
- 主要贡献：A comprehensive survey of graph summarization with graph neural networks, covering GNN-based summarization approaches including graph autoencoders, and discussing dynamic graphs as a future direction.
- 相关性：0.70
- 置信度：0.85
- 来源：
  - A Comprehensive Survey on Graph Summarization with Graph Neural Networks：https://arxiv.org/pdf/2302.06114
    - 引文：Graph summarization is the process of finding a condensed representation of a graph while preserving its key properties
    - 位置：artifact art_2c3d8467f4da8a33213a0887 chars:5175-5294
  - A Comprehensive Survey on Graph Summarization with Graph Neural Networks：https://arxiv.org/pdf/2302.06114
    - 引文：Our investigation includes a review of the current state-of-the-art approaches, including recurrent GNNs, convolutional GNNs, graph autoencoders, and graph attention networks.
    - 位置：artifact art_2c3d8467f4da8a33213a0887 chars:2818-2993

### card_7eefef982fccf42f4844ad44 · Graph Coarsening via Convolution Matching for Scalable Graph Neural Network Training

- 查新点：NP-3
- 主要贡献：CONVMATCH proposes graph coarsening via convolution matching as a preprocessing technique for scalable GNN training, creating summarized graphs that preserve graph convolution output while significantly reducing graph size.
- 相关性：0.85
- 置信度：0.90
- 来源：
  - Graph Coarsening via Convolution Matching for Scalable Graph Neural Network Training：https://arxiv.org/pdf/2312.15520
    - 引文：Graph summarization as a preprocessing step is an effective and complementary technique for scalable graph neural network (GNN) training. In this work, we propose the Coarsening Via Convolution Matching (CONVMATCH) algorithm and a highly scalable variant, A-CONVMATCH, for creating summarized graphs that preserve the output of graph convolution.
    - 位置：artifact art_bf81f0222bfdcc7d34201822 chars:0-346
  - Graph Coarsening via Convolution Matching for Scalable Graph Neural Network Training：https://arxiv.org/pdf/2312.15520
    - 引文：Notably, CONVMATCH achieves up to 95% of the prediction performance of GNNs on node classification while trained on graphs summarized down to 1% the size of the original graph.
    - 位置：artifact art_bf81f0222bfdcc7d34201822 chars:550-726

### card_02d8fa6f524c989795c96dc9 · Inference-friendly Graph Compression for Graph Neural Networks

- 查新点：NP-3
- 主要贡献：Inference-friendly graph compression (IFGC) proposes a graph compression scheme to accelerate GNN inference by computing a small compressed graph that preserves inference results.
- 相关性：0.60
- 置信度：0.85
- 来源：
  - Inference-friendly Graph Compression for Graph Neural Networks：https://arxiv.org/pdf/2504.13034
    - 引文：This paper proposes inference-friendly graph compression (IFGC), a graph compression scheme to accelerate GNNs inference. Given a graph $G$ and a GNN $M$, an IFGC computes a small compressed graph $G_c$, to best preserve the inference results of $M$ over $G$
    - 位置：artifact art_07ec080e57558783022d62b8 chars:195-453

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 0 | 0 Card |
| NP-2 | 0 | 0 Card |
| NP-3 | 3 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，该方法通过图摘要技术压缩原图，利用图自编码器学习节点表征，并结合循环神经网络学习时间维度的特征和依赖关系，能够高效生成大规模时序图的低维表征。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点（基于图摘要的大规模时序图表示学习方法GSAERU）未获得任何有效证据卡支持，当前证据不足，无法进行新颖性裁定。由于检索覆盖事实未知，不能确认必要来源是否成功执行或是否零命中，亦不能排除相关文献存在的可能；结论应理解为证据不足，而非确证无相关文献。  
**高度相关 Work：**
  - 无

### NP-2 · 证据不足，无法裁定

提出了一种基于图摘要的分布式图神经网络优化训练算法DSGNN，采用领导-工作者工作模式，领导节点利用基于边分割的图流划分算法划分图并将子图分配给工作者，工作者执行基于图摘要的小批量训练，通过注意力层返回结果，领导节点汇总计算梯度并同步更新所有模型，显著加速大规模图流的GNN训练。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点（基于图摘要的分布式图神经网络优化训练算法DSGNN）未获得任何有效证据卡支持，当前证据不足，无法进行新颖性裁定。由于检索覆盖事实未知，不能确认必要来源是否成功执行或是否零命中，亦不能排除相关文献存在的可能；结论应理解为证据不足，而非确证无相关文献。  
**高度相关 Work：**
  - 无

### NP-3 · 部分新颖

提出了一种基于图摘要的图神经网络优化机制，通过图摘要技术对原始图数据进行压缩，在保留图主要结构和特征信息的同时大幅减少数据规模，从而降低图神经网络训练的内存消耗和计算成本，并可同时应用于大规模动态时序图的表示学习和分布式训练场景，有效提升了图神经网络的可扩展性和训练效率。

**Reviewer 裁定：** 部分新颖  
**裁定理由：** 综合三篇单卡证据：综述（card_369a02f1d029252af70a4638）系统梳理了图摘要与GNN类方法（含图自编码器），但未涉及动态/时序图表示学习、分布式训练小批量生成及重构误差质量控制；CONVMATCH（card_7eefef982fccf42f4844ad44）证实图摘要/粗化压缩原始图可大幅降规模并保持预测性能，但仅针对静态图节点分类/链接预测，未覆盖时序图表示学习和分布式训练；IFGC（card_02d8fa6f524c989795c96dc9）使用图压缩加速推理，但未涉及训练效率、时序图、分布式训练及重构误差机制。单篇公开内容均未覆盖完整组合（压缩+时序表示学习+分布式训练+重构质量控制），仅分别覆盖部分特征（特征1、2、5的部分内涵），不构成完整组合的公开。因此判定为部分新颖，完整组合仍有差异化空间。  
**置信度：** 0.72  
**报告摘要：** 基于三篇有效证据卡，判定查新点NP-3（基于图摘要的图神经网络优化机制）为部分新颖。已有工作分别覆盖图摘要压缩保持关键性质（综述）、静态图训练用图摘要/粗化压缩（CONVMATCH）、推理用图压缩（IFGC），但均未覆盖动态时序图表示学习、分布式训练小批量生成及重构误差质量控制等完整组合。单卡证据仅覆盖部分技术特征，不构成完整组合的公开，故完整组合仍具新颖性空间。  
**高度相关 Work：**
  - wrk_3341f9be3e3f75887b9da472：综述系统梳理图摘要（压缩并保持关键性质）及GNN类方法（含图自编码器），与特征1-3部分对应，但未涉及分布式训练小批量生成和重构误差质量控制，属部分相关基线。 (cards: card_369a02f1d029252af70a4638)
  - wrk_f7b8adb9585db0dfc3de41af：CONVMATCH直接证实用图摘要/粗化压缩原始图训练GNN可显著降规模且保持预测性能，覆盖特征1、2、5的部分内涵，但仅限静态图节点分类/链接预测，未覆盖动态时序图表示学习（特征3）和分布式训练小批量（特征4），属部分相关基线。 (cards: card_7eefef982fccf42f4844ad44)
  - wrk_2e51677d82499024e21cfee7：IFGC采用图压缩生成小型压缩图供GNN处理，与特征1重叠，但聚焦推理加速而非训练内存/计算降低，未涉及时序图、分布式训练和重构误差机制，属部分相关基线。 (cards: card_02d8fa6f524c989795c96dc9)

---

## 八、报告局限

- 本次检索的有效证据仅3条，全部绑定NP-3；NP-1和NP-2无有效证据且检索覆盖事实未知。由于未提供各检索源的执行状态与覆盖范围，无法区分检索失败、检索成功零命中或有命中但未形成有效证据三种情形，因此对NP-1和NP-2的结论应理解为证据不足，而非确证相关文献不存在。
- 全部有效证据卡均通过证据门控，无被拒绝证据，因此不涉及门控拒绝原因说明。
- 本次检索范围未明确披露具体数据库、年份或检索式，无法断言检索覆盖的完整性；对NP-3而言，证据虽支持部分新颖的裁定，但完整组合的边界仍需更广泛的检索进一步确认。

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

- Graph-Adaptive Horseshoe for Compositional Regression：[https://arxiv.org/pdf/2608.17858](https://arxiv.org/pdf/2608.17858)
- CGS: Configurable Graph Summarization with Bounded Neighborhood Loss and Query Support：[https://arxiv.org/pdf/2607.10969](https://arxiv.org/pdf/2607.10969)
- COREKG: Coreset-Guided Personalized Summarization of Knowledge Graphs：[https://arxiv.org/pdf/2605.14900](https://arxiv.org/pdf/2605.14900)
- Spectral Model eXplainer: a chemically-grounded explainability framework for spectral-based machine learning models：[https://arxiv.org/pdf/2605.02684](https://arxiv.org/pdf/2605.02684)
- A Null Model for Mapper Subtype Claims：[https://arxiv.org/pdf/2604.17395](https://arxiv.org/pdf/2604.17395)
- Explainable Mapper: Charting LLM Embedding Spaces Using Perturbation-Based Explanation and Verification Agents：[https://arxiv.org/pdf/2507.18607](https://arxiv.org/pdf/2507.18607)
- Causal DAG Summarization (Full Version)：[https://arxiv.org/pdf/2504.14937](https://arxiv.org/pdf/2504.14937)
- Code-Craft: Hierarchical Graph-Based Code Summarization for Enhanced Context Retrieval：[https://arxiv.org/pdf/2504.08975](https://arxiv.org/pdf/2504.08975)
- Graph Coarsening via Convolution Matching for Scalable Graph Neural Network Training：[https://arxiv.org/pdf/2312.15520](https://arxiv.org/pdf/2312.15520)
- A Comprehensive Survey on Graph Summarization with Graph Neural Networks：[https://arxiv.org/pdf/2302.06114](https://arxiv.org/pdf/2302.06114)
- Graph Summarization with Graph Neural Networks：[https://arxiv.org/pdf/2203.05919](https://arxiv.org/pdf/2203.05919)
- Multiplex Graph Neural Network for Extractive Text Summarization：[https://arxiv.org/pdf/2108.12870](https://arxiv.org/pdf/2108.12870)
- Guided Graph Compression for Quantum Graph Neural Networks：[https://arxiv.org/pdf/2506.09862](https://arxiv.org/pdf/2506.09862)
- Inference-friendly Graph Compression for Graph Neural Networks：[https://arxiv.org/pdf/2504.13034](https://arxiv.org/pdf/2504.13034)
- Efficient User Sequence Learning for Online Services via Compressed Graph Neural Networks：[https://arxiv.org/pdf/2406.02979](https://arxiv.org/pdf/2406.02979)
- SEMA-GUARD: Semantic and Graph-Based Vulnerability Detection in Assembly Code：[https://arxiv.org/pdf/2609.17254](https://arxiv.org/pdf/2609.17254)
- Neural Graph Generator: Feature-Conditioned Graph Generation using Latent Diffusion Models：[https://arxiv.org/pdf/2403.01535](https://arxiv.org/pdf/2403.01535)
- Channel-Informed Neural Network for Physical Layer Key Generation：[https://arxiv.org/pdf/2609.16341](https://arxiv.org/pdf/2609.16341)
- Machine Learning in Fish Farming：[https://arxiv.org/pdf/2609.13919](https://arxiv.org/pdf/2609.13919)
- Nuclear mass prediction using bidirectional recurrent neural networks with isotopic and isotonic chain correlations：[https://arxiv.org/pdf/2609.13782](https://arxiv.org/pdf/2609.13782)
- Hardware-Attributed Operator Profiling for PyTorch：[https://arxiv.org/pdf/2609.11938](https://arxiv.org/pdf/2609.11938)
- Combining Synthetic and Real Data for Low-Resource Historical OCR: A Manchu Case Study：[https://arxiv.org/pdf/2609.11495](https://arxiv.org/pdf/2609.11495)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
