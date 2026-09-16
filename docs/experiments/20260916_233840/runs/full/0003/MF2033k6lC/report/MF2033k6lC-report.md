# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-09-16T23:08:14+08:00 |
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

- 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图映射为固定规模的新图，解决了GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。
- 提出了一种基于图摘要的分布式图神经网络训练框架DSGNN，采用“领导-工作者”模式，领导节点负责图划分和模型同步更新，工作者节点基于图摘要技术进行小批量训练，并通过注意力层返回结果。
- 提出了一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图映射为固定规模的新图，解决了GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。 | Proposed a large-scale sequential graph representation learning method GSAERU based on graph summarization, which maps dynamic sequential graphs to fixed-size new graphs via graph summarization, solving the problem that GNN outputs cannot be directly fed into RNN, and uses graph autoencoder and recurrent neural network to learn temporal features. |
| NP-2 | 提出了一种基于图摘要的分布式图神经网络训练框架DSGNN，采用“领导-工作者”模式，领导节点负责图划分和模型同步更新，工作者节点基于图摘要技术进行小批量训练，并通过注意力层返回结果。 | Proposed a distributed graph neural network training framework DSGNN based on graph summarization, adopting a leader-worker mode where the leader performs graph partitioning and synchronous model updates, and workers perform mini-batch training based on graph summarization and return results via an attention layer. |
| NP-3 | 提出了一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。 | Proposed an edge-segmentation-based graph stream partitioning algorithm Sketch-DBH, which uses Count-Min Sketch to store node degree information and a min-heap to maintain high-frequency node information, enabling constant-time query results and generating subgraph IDs, ensuring load balancing. |

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
  - `abs:"graph summarization" AND abs:"graph autoencoder" AND abs:"recurrent neural network"`（arxiv；零命中）
  - `(ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:"temporal graph learning") AND (abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening") AND (abs:"graph autoencoder" OR abs:"graph auto-encoder" OR abs:"GAE") AND (abs:"recurrent neural network" OR abs:"RNN" OR abs:"recurrent network") AND (abs:"temporal features" OR abs:"time-series features" OR abs:"sequential features")`（arxiv；零命中）
  - `(ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:"temporal graph learning") AND (abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening") AND (abs:"graph autoencoder" OR abs:"graph auto-encoder" OR abs:"GAE") AND (abs:"recurrent neural network" OR abs:"RNN" OR abs:"recurrent network")`（arxiv；零命中）
  - `(ti:sequential AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:"temporal graph learning") OR (abs:"graph summarization" OR abs:"graph compression" OR abs:"graph coarsening") OR (abs:"graph autoencoder" OR abs:"graph auto-encoder" OR abs:"GAE") OR (abs:"recurrent neural network" OR abs:"RNN" OR abs:"recurrent network") OR (abs:"temporal features" OR abs:"time-series features" OR abs:"sequential features") OR (abs:"large-scale graphs" OR abs:"big graphs" OR abs:"large graphs")`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] AND CONCEPT[C2:graph summarization] AND CONCEPT[C3:graph autoencoder] AND CONCEPT[C4:recurrent neural network])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization] AND CONCEPT[C3:graph autoencoder] AND CONCEPT[C4:recurrent neural network])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] AND CONCEPT[C2:graph summarization] AND CONCEPT[C3:graph autoencoder] AND CONCEPT[C4:recurrent neural network] AND CONCEPT[C5:temporal features])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] AND CONCEPT[C2:graph summarization] AND CONCEPT[C3:graph autoencoder] AND CONCEPT[C4:recurrent neural network])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:graph autoencoder] OR CONCEPT[C4:recurrent neural network] OR CONCEPT[C5:temporal features] OR CONCEPT[C6:large-scale graphs])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:sequential graph representation learning] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:graph autoencoder] OR CONCEPT[C4:recurrent neural network] OR CONCEPT[C5:temporal features] OR CONCEPT[C6:large-scale graphs])`（null_catalog；零命中）
  - `"sequential graph representation learning" AND "graph summarization" AND "graph autoencoder" AND "recurrent neural network"`（springer；执行失败）
  - `"sequential graph representation learning" AND "graph summarization" AND "graph autoencoder" AND "recurrent neural network"`（springer；执行失败）
  - `"sequential graph representation learning" AND "graph summarization" AND "graph autoencoder" AND "recurrent neural network"`（springer；执行失败）
  - `"sequential graph representation learning" AND "graph summarization" AND "graph autoencoder" AND "recurrent neural network"`（springer；执行失败）
  - `"sequential graph representation learning" AND "graph summarization" AND "graph autoencoder" AND "recurrent neural network"`（springer；执行失败）
  - `abs:"graph summarization" AND ti:temporal AND ti:graph AND ti:representation AND ti:learning AND abs:"graph autoencoder" AND abs:"recurrent neural network"`（arxiv；零命中）
  - `abs:"graph summarization" AND ti:temporal AND ti:graph AND ti:representation AND ti:learning AND abs:"recurrent neural network"`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph summary" OR abs:"graph compression") AND (ti:temporal AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:"sequential graph learning") AND (abs:"fixed-size graph representation" OR abs:"fixed-size graph embedding" OR abs:"fixed-scale graph representation")`（arxiv；零命中）
  - `(abs:"graph summarization" OR abs:"graph summary" OR abs:"graph compression") AND (ti:temporal AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:"sequential graph learning")`（arxiv；零命中）
  - `(ti:temporal AND ti:graph AND ti:representation AND ti:learning OR ti:"dynamic graph embedding" OR ti:"sequential graph learning") OR (abs:"graph autoencoder" OR abs:"graph auto-encoder" OR abs:"GAE") OR (abs:"recurrent neural network" OR abs:"RNN" OR abs:"recurrent network")`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:graph summarization] AND CONCEPT[C2:temporal graph representation learning] AND CONCEPT[C3:graph autoencoder] AND CONCEPT[C4:recurrent neural network])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph summarization] AND CONCEPT[C2:temporal graph representation learning] AND CONCEPT[C4:recurrent neural network])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph summarization] AND CONCEPT[C2:temporal graph representation learning] AND CONCEPT[C5:fixed-size graph representation])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph summarization] AND CONCEPT[C2:temporal graph representation learning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:temporal graph representation learning] OR CONCEPT[C3:graph autoencoder] OR CONCEPT[C4:recurrent neural network])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:temporal graph representation learning] OR CONCEPT[C3:graph autoencoder] OR CONCEPT[C4:recurrent neural network])`（null_catalog；零命中）
  - `"graph summarization" AND "temporal graph representation learning" AND "graph autoencoder" AND "recurrent neural network"`（springer；执行失败）
  - `"graph summarization" AND "temporal graph representation learning" AND "graph autoencoder" AND "recurrent neural network"`（springer；执行失败）
  - `"graph summarization" AND "temporal graph representation learning" AND "graph autoencoder" AND "recurrent neural network"`（springer；执行失败）
  - `"graph summarization" AND "temporal graph representation learning" AND "graph autoencoder" AND "recurrent neural network"`（springer；执行失败）
- **NP-2**
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND ti:framework AND abs:"graph summarization"`（arxiv；零命中）
  - `abs:"graph summarization"`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:leader-worker mode] OR CONCEPT[C4:graph partitioning])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training framework] OR CONCEPT[C2:graph summarization] OR CONCEPT[C3:leader-worker mode] OR CONCEPT[C4:graph partitioning])`（null_catalog；零命中）
  - `"distributed graph neural network training framework" AND "graph summarization"`（springer；执行失败）
  - `"distributed graph neural network training framework" AND "graph summarization"`（springer；执行失败）
  - `"distributed graph neural network training framework" AND "graph summarization"`（springer；执行失败）
  - `"distributed graph neural network training framework" AND "graph summarization"`（springer；执行失败）
  - `"distributed graph neural network training framework" AND "graph summarization"`（springer；执行失败）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"mini-batch training"`（arxiv；零命中）
  - `ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"distributed graph learning") AND (abs:"graph summarization" OR abs:"graph summary" OR abs:"graph condensation") AND (abs:"leader-worker mode" OR abs:"leader-follower" OR abs:"master-worker")`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"distributed graph learning") AND (abs:"graph summarization" OR abs:"graph summary" OR abs:"graph condensation")`（arxiv；零命中）
  - `(ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training OR ti:"distributed GNN training" OR ti:"distributed graph learning") OR (abs:"attention mechanism" OR abs:"attention layer" OR abs:"attention")`（arxiv；有命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training] AND CONCEPT[C2:graph summarization] AND CONCEPT[C3:mini-batch training])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training] AND CONCEPT[C2:graph summarization] AND CONCEPT[C4:leader-worker mode])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training] AND CONCEPT[C2:graph summarization])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training] OR CONCEPT[C5:attention mechanism])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:distributed graph neural network training] OR CONCEPT[C5:attention mechanism])`（null_catalog；零命中）
- **NP-3**
  - `ti:"graph stream partitioning" AND abs:"edge-based partitioning" ANDNOT (all:"vertex partitioning") AND abs:"Count-Min Sketch"`（arxiv；零命中）
  - `abs:"edge-based partitioning" ANDNOT (all:"vertex partitioning") AND abs:"Count-Min Sketch"`（arxiv；有命中）
  - `(ti:"graph stream partitioning" OR ti:"graph stream partition" OR ti:"streaming graph partitioning") AND (abs:"edge-based partitioning" OR abs:"edge partitioning" OR abs:"edge-cut partitioning") ANDNOT (all:"vertex partitioning") AND (abs:"Count-Min Sketch" OR abs:"CMS" OR abs:"count-min sketch") AND (abs:"min-heap" OR abs:"minimum heap" OR abs:"min heap") AND (abs:"load balancing" OR abs:"load balance" OR abs:"balanced partitioning")`（arxiv；有命中）
  - `(ti:"graph stream partitioning" OR ti:"graph stream partition" OR ti:"streaming graph partitioning") OR (abs:"edge-based partitioning" OR abs:"edge partitioning" OR abs:"edge-cut partitioning") ANDNOT (all:"vertex partitioning") OR (abs:"Count-Min Sketch" OR abs:"CMS" OR abs:"count-min sketch") OR (abs:"min-heap" OR abs:"minimum heap" OR abs:"min heap") OR (abs:"load balancing" OR abs:"load balance" OR abs:"balanced partitioning") OR (abs:"large-scale graph" OR abs:"big graph" OR abs:"massive graph")`（arxiv；部分成功）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] AND CONCEPT[C2:edge-based partitioning] AND CONCEPT[C3:Count-Min Sketch])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C2:edge-based partitioning] AND CONCEPT[C3:Count-Min Sketch])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] AND CONCEPT[C2:edge-based partitioning] AND CONCEPT[C3:Count-Min Sketch] AND CONCEPT[C4:min-heap] AND CONCEPT[C5:load balancing])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] AND CONCEPT[C2:edge-based partitioning] AND CONCEPT[C3:Count-Min Sketch] AND CONCEPT[C5:load balancing])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] OR CONCEPT[C2:edge-based partitioning] OR CONCEPT[C3:Count-Min Sketch] OR CONCEPT[C4:min-heap] OR CONCEPT[C5:load balancing] OR CONCEPT[C6:large-scale graph])`（null_catalog；零命中）
  - `NULL_QUERY(CONCEPT[C1:graph stream partitioning] OR CONCEPT[C2:edge-based partitioning] OR CONCEPT[C3:Count-Min Sketch] OR CONCEPT[C4:min-heap] OR CONCEPT[C5:load balancing] OR CONCEPT[C6:large-scale graph])`（null_catalog；零命中）
  - `"graph stream partitioning" AND "edge-based partitioning" NOT "vertex partitioning" AND "Count-Min Sketch"`（springer；执行失败）
  - `"graph stream partitioning" AND "edge-based partitioning" NOT "vertex partitioning" AND "Count-Min Sketch"`（springer；执行失败）

---

## 六、检索结果

### 6.1 检索概况

共执行 2 轮检索计划，生成 1 张原始证据卡；通过 1 张，拒绝 0 张。

### 6.2 相关文献

### card_927caf724042beff967b2231 · Window-based Streaming Graph Partitioning Algorithm

- 查新点：NP-3
- 主要贡献：WStream proposes a window-based streaming graph partitioning algorithm (edge-cut) that partitions large graph data efficiently while keeping load balanced across partitions and minimizing communication.
- 相关性：0.55
- 置信度：0.80
- 来源：
  - Window-based Streaming Graph Partitioning Algorithm：10.1145/3290688.3290711
    - 引文：This paper proposes an efficient window-based streaming graph partitioning algorithm called WStream. The WStream algorithm is an edge-cut partitioning algorithm, which distributes a vertex among the partitions. Our results suggest that the WStream algorithm is able to partition large graph data efficiently while keeping the load balanced across different partitions, and communication to a minimum.
    - 位置：artifact art_044b624240993e16c40f3537 chars:713-1113

### 6.3 最终有效证据数量

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 0 | 0 Card |
| NP-2 | 0 | 0 Card |
| NP-3 | 1 | 有证据 |

---

## 七、查新结论

### NP-1 · 证据不足，无法裁定

提出了一种基于图摘要的大规模时序图表示学习方法GSAERU，通过图摘要技术将动态时序图映射为固定规模的新图，解决了GNN输出无法直接输入RNN训练的问题，并利用图自编码器与循环神经网络学习时序特征。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - 无

### NP-2 · 证据不足，无法裁定

提出了一种基于图摘要的分布式图神经网络训练框架DSGNN，采用“领导-工作者”模式，领导节点负责图划分和模型同步更新，工作者节点基于图摘要技术进行小批量训练，并通过注意力层返回结果。

**Reviewer 裁定：** 证据不足，无法裁定  
**裁定理由：** —  
**置信度：** —  
**报告摘要：** 该查新点的关键比较证据不足，尚不能作出新颖性裁定。  
**高度相关 Work：**
  - 无

### NP-3 · 新颖

提出了一种基于边分割的图流划分算法Sketch-DBH，利用Count-Min Sketch存储节点度数信息，并使用最小堆维护高频节点信息，实现常数时间内返回查询结果并生成子图编号，确保负载均衡。

**Reviewer 裁定：** 新颖  
**裁定理由：** 单卡核验显示，WStream 与 Sketch-DBH 同属图流划分与负载均衡问题域，但 WStream 采用基于窗口的边割顶点分配机制，其摘要明确描述为 window-based edge-cut 和 distributes a vertex，未披露 Count-Min Sketch 存储节点度数、最小堆维护高频节点、常数时间查询及基于度数生成子图编号等特征组合。该文献仅部分相关，未覆盖 NP-3 的核心技术组合，故相对该文献，NP-3 具有新颖性。  
**置信度：** 0.75  
**报告摘要：** 基于有效证据卡card_927caf724042beff967b2231，查新点NP-3（基于边分割的图流划分算法Sketch-DBH）与WStream文献同属图流划分与负载均衡问题域，但WStream采用窗口式边割顶点分配机制，未披露Count-Min Sketch存储节点度数、最小堆维护高频节点、常数时间查询及基于度数生成子图编号等核心技术特征。该文献仅部分相关，未覆盖Sketch-DBH的核心技术组合，因此相对该文献，NP-3具有新颖性。  
**高度相关 Work：**
  - wrk_dd602dc2d2b07d7e69e6724c：同属流式图划分与负载均衡问题域，但采用窗口式边割顶点分配机制，未披露 Count-Min Sketch、最小堆、常数时间查询及基于度数生成子图编号等 Sketch-DBH 核心技术特征，属部分相关基线文献。 (cards: card_927caf724042beff967b2231)

---

## 八、报告局限

- 本次检索中，NP-1和NP-2没有获得任何有效证据卡（最终有效EvidenceCard数量为0），且输入未提供明确的检索执行事实（如检索是否成功、是否零命中或是否存在被拒绝的证据），因此无法区分检索失败、零命中或有命中但未形成有效证据的情形，检索覆盖情况未知。
- NP-3获得1张有效证据卡，该证据卡已用于结论支持；但该证据卡仅涉及图流划分领域，未覆盖NP-3中其他可能相关的分布式训练框架或图摘要技术方面的文献，因此关于NP-3的结论仅基于该单卡证据，仍需更广泛检索以增强稳健性。
- 输入的rejected_evidence列表为空，表明当前不存在被拒绝的证据，因此无法说明门控拒绝的具体原因。

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
- LaneGraph2Seq: Lane Topology Extraction with Language Model via Vertex-Edge Encoding and Connectivity Enhancement：[https://arxiv.org/pdf/2401.17609](https://arxiv.org/pdf/2401.17609)
- Window-based Streaming Graph Partitioning Algorithm：[https://arxiv.org/pdf/1902.01543](https://arxiv.org/pdf/1902.01543)
- Buffered Streaming Graph Partitioning：[https://arxiv.org/pdf/2102.09384](https://arxiv.org/pdf/2102.09384)
- BuffCut: Prioritized Buffered Streaming Graph Partitioning：[https://arxiv.org/pdf/2602.21248](https://arxiv.org/pdf/2602.21248)
- Streaming Graph Partitioning in the Planted Partition Model：[https://arxiv.org/pdf/1406.7570](https://arxiv.org/pdf/1406.7570)
- Armada: Memory-Efficient Distributed Training of Large-Scale Graph Neural Networks：[https://arxiv.org/pdf/2502.17846](https://arxiv.org/pdf/2502.17846)
- S-PowerGraph: Streaming Graph Partitioning for Natural Graphs by Vertex-Cut：[https://arxiv.org/pdf/1511.02586](https://arxiv.org/pdf/1511.02586)
- Play like a Vertex: A Stackelberg Game Approach for Streaming Graph Partitioning：[https://arxiv.org/pdf/2402.18304](https://arxiv.org/pdf/2402.18304)
- Framing RNN as a kernel method: A neural ODE approach：[https://arxiv.org/pdf/2106.01202](https://arxiv.org/pdf/2106.01202)
- Recurrent Neural Network from Adder's Perspective: Carry-lookahead RNN：[https://arxiv.org/pdf/2106.12901](https://arxiv.org/pdf/2106.12901)
- Learning Contextual Dependencies with Convolutional Hierarchical Recurrent Neural Networks：[https://arxiv.org/pdf/1509.03877](https://arxiv.org/pdf/1509.03877)
- Approximating meta-heuristics with homotopic recurrent neural networks：[https://arxiv.org/pdf/1709.02194](https://arxiv.org/pdf/1709.02194)
- Embedding Graph Auto-Encoder for Graph Clustering：[https://arxiv.org/pdf/2002.08643](https://arxiv.org/pdf/2002.08643)
- Self-supervised Adversarial Purification for Graph Neural Networks：[https://arxiv.org/pdf/2605.23239](https://arxiv.org/pdf/2605.23239)
- Understanding Feature Selection and Feature Memorization in Recurrent Neural Networks：[https://arxiv.org/pdf/1903.00906](https://arxiv.org/pdf/1903.00906)
- Ensemble-Enhanced Graph Autoencoder with GAT and Transformer-Based Encoders for Robust Fault Diagnosis：[https://arxiv.org/pdf/2504.09427](https://arxiv.org/pdf/2504.09427)
- Generating Music with Structure Using Self-Similarity as Attention：[https://arxiv.org/pdf/2406.15647](https://arxiv.org/pdf/2406.15647)
- Fast-FNet: Accelerating Transformer Encoder Models via Efficient Fourier Layers：[https://arxiv.org/pdf/2209.12816](https://arxiv.org/pdf/2209.12816)
- Spectral Conditioning of Attention Improves Transformer Performance：[https://arxiv.org/pdf/2603.07162](https://arxiv.org/pdf/2603.07162)
- Locally Shifted Attention With Early Global Integration：[https://arxiv.org/pdf/2112.05080](https://arxiv.org/pdf/2112.05080)
- Attention Sink Forges Native MoE in Attention Layers: Sink-Aware Training to Address Head Collapse：[https://arxiv.org/pdf/2602.01203](https://arxiv.org/pdf/2602.01203)
- On the Relationship between Self-Attention and Convolutional Layers：[https://arxiv.org/pdf/1911.03584](https://arxiv.org/pdf/1911.03584)
- Beyong Tokens: Item-aware Attention for LLM-based Recommendation：[https://arxiv.org/pdf/2603.19693](https://arxiv.org/pdf/2603.19693)
- Is It Worth the Attention? A Comparative Evaluation of Attention Layers for Argument Unit Segmentation：[https://arxiv.org/pdf/1906.10068](https://arxiv.org/pdf/1906.10068)

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
