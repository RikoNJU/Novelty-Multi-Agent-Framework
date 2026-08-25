# 科技查新报告

## 项目信息

| 项目 | 内容 |
| --- | --- |
| 项目名称 | 面向大规模动态图的图神经网络优化机制研究 |
| 英文名称 | — |
| 报告生成时间 | 2026-08-18T12:16:43+08:00 |
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

- 提出了一种基于图摘要技术的大规模时序图表示学习方法，称为GSAERU模型。
- 提出了一种基于图摘要技术的分布式图神经网络优化训练算法，称为DSGNN模型。
- 提出的GSAERU模型在大规模时序图表示学习中，相比传统方法具有更高的效率和性能。

---

## 三、查新点

| 序号 | 中文查新点 | 英文查新点 |
| --- | --- | --- |
| NP-1 | 提出了一种基于图摘要技术的大规模时序图表示学习方法，称为GSAERU模型。 | Proposes a large-scale sequential graph representation learning method based on graph summarization, named GSAERU model. |
| NP-2 | 提出了一种基于图摘要技术的分布式图神经网络优化训练算法，称为DSGNN模型。 | Proposes a distributed graph neural network optimization training algorithm based on graph summaries, named DSGNN model. |
| NP-3 | 提出的GSAERU模型在大规模时序图表示学习中，相比传统方法具有更高的效率和性能。 | The proposed GSAERU model achieves higher efficiency and performance in large-scale sequential graph representation learning compared to traditional methods. |

---

## 四、查新范围要求

检索范围围绕各查新点的中英文表述及技术特征展开。

---

## 五、文献检索范围及检索策略

### 5.1 检索来源

- 未记录有效证据来源

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
  - `{"exact": true, "language": "zh", "search": "(图摘要 OR 图摘要技术 OR 图压缩 OR 图摘要方法) AND (时序图 OR 动态图 OR 时序网络 OR 动态网络) AND (图表示学习 OR 图表征学习 OR 图嵌入) AND (图自编码器 OR 图自动编码器 OR GAE) AND (循环神经网络 OR 递归神经网络 OR RNN) AND (大规模 OR 大型 OR 海量)", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `{"exact": false, "language": null, "search": "(图摘要 OR 图摘要技术 OR 图压缩 OR 图摘要方法) AND (时序图 OR 动态图 OR 时序网络 OR 动态网络) AND (图表示学习 OR 图表征学习 OR 图嵌入) AND ((图自编码器 OR 图自动编码器 OR GAE) OR (循环神经网络 OR 递归神经网络 OR RNN))", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `(all:"时序图表示学习" OR all:"动态图表示学习" OR all:"时序图嵌入" OR all:"动态图嵌入" OR all:"时序图表征学习" OR all:"动态图表征学习" OR all:"大规模时序图表示学习") AND (all:"图摘要" OR all:"图压缩" OR all:"图概要" OR all:"图摘要技术" OR all:"graph summarization")`
  - `((all:"时序图表示学习" OR all:"动态图表示学习" OR all:"时序图嵌入" OR all:"动态图嵌入" OR all:"时序图表征学习" OR all:"动态图表征学习" OR all:"大规模时序图表示学习") AND (all:"图摘要" OR all:"图压缩" OR all:"图概要" OR all:"图摘要技术" OR all:"graph summarization")) OR ((all:"时序图表示学习" OR all:"动态图表示学习" OR all:"时序图嵌入" OR all:"动态图嵌入" OR all:"时序图表征学习" OR all:"动态图表征学习" OR all:"大规模时序图表示学习") AND (all:"图自编码器" OR all:"图自动编码器" OR all:"图自编码模型" OR all:"GAE" OR all:"graph autoencoder") AND (all:"循环神经网络" OR all:"RNN" OR all:"递归神经网络" OR all:"循环神经网络模型" OR all:"recurrent neural network"))`
  - `(all:"时序图表示学习" OR all:"动态图表示学习" OR all:"时序图嵌入" OR all:"动态图嵌入" OR all:"时序图表征学习" OR all:"动态图表征学习" OR all:"大规模时序图表示学习") AND ((all:"图摘要" OR all:"图压缩" OR all:"图概要" OR all:"图摘要技术" OR all:"graph summarization") OR (all:"图自编码器" OR all:"图自动编码器" OR all:"图自编码模型" OR all:"GAE" OR all:"graph autoencoder") OR (all:"循环神经网络" OR all:"RNN" OR all:"递归神经网络" OR all:"循环神经网络模型" OR all:"recurrent neural network"))`
  - `((all:"sequential graph representation learning" OR all:"temporal graph representation learning" OR all:"dynamic graph representation learning" OR all:"time-evolving graph representation learning" OR all:"sequential graph embedding" OR all:"temporal graph embedding" OR all:"dynamic graph embedding" OR all:"large-scale sequential graph representation learning" OR all:"large-scale temporal graph representation learning") AND (all:"graph summarization" OR all:"graph summarization technique" OR all:"graph compression" OR all:"graph summary" OR all:"graph summarization method") AND (all:"graph autoencoder" OR all:"graph auto-encoder" OR all:"GAE" OR all:"graph autoencoding" OR all:"graph autoencoder model") AND (all:"recurrent neural network" OR all:"RNN" OR all:"recurrent network" OR all:"LSTM" OR all:"GRU" OR all:"gated recurrent unit" OR all:"long short-term memory"))`
  - `((all:"sequential graph representation learning" OR all:"temporal graph representation learning" OR all:"dynamic graph representation learning" OR all:"time-evolving graph representation learning" OR all:"sequential graph embedding" OR all:"temporal graph embedding" OR all:"dynamic graph embedding" OR all:"large-scale sequential graph representation learning" OR all:"large-scale temporal graph representation learning") AND (all:"graph summarization" OR all:"graph summarization technique" OR all:"graph compression" OR all:"graph summary" OR all:"graph summarization method") AND ((all:"graph autoencoder" OR all:"graph auto-encoder" OR all:"GAE" OR all:"graph autoencoding" OR all:"graph autoencoder model") OR (all:"recurrent neural network" OR all:"RNN" OR all:"recurrent network" OR all:"LSTM" OR all:"GRU" OR all:"gated recurrent unit" OR all:"long short-term memory")))`
  - `((all:"sequential graph representation learning" OR all:"temporal graph representation learning" OR all:"dynamic graph representation learning" OR all:"time-evolving graph representation learning" OR all:"sequential graph embedding" OR all:"temporal graph embedding" OR all:"dynamic graph embedding" OR all:"large-scale sequential graph representation learning" OR all:"large-scale temporal graph representation learning") AND (all:"graph summarization" OR all:"graph summarization technique" OR all:"graph compression" OR all:"graph summary" OR all:"graph summarization method"))`
  - `{"exact": true, "language": "zh", "search": "(\"temporal graph representation learning\" OR \"dynamic graph representation learning\" OR \"sequential graph representation learning\" OR \"time-evolving graph representation learning\" OR \"temporal graph embedding\" OR \"large-scale temporal graph representation learning\") AND (\"graph summarization\" OR \"graph summary\" OR \"graph compression\" OR \"graph summarization technique\") AND (\"graph autoencoder\" OR \"graph auto-encoder\" OR GAE OR \"graph autoencoder model\") AND (\"recurrent neural network\" OR RNN OR \"recurrent network\" OR \"gated recurrent unit\" OR \"long short-term memory\")", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `{"exact": false, "language": null, "search": "(\"temporal graph representation learning\" OR \"dynamic graph representation learning\" OR \"sequential graph representation learning\" OR \"time-evolving graph representation learning\" OR \"temporal graph embedding\" OR \"large-scale temporal graph representation learning\") AND (\"graph summarization\" OR \"graph summary\" OR \"graph compression\" OR \"graph summarization technique\") AND ((\"graph autoencoder\" OR \"graph auto-encoder\" OR GAE OR \"graph autoencoder model\") OR (\"recurrent neural network\" OR RNN OR \"recurrent network\" OR \"gated recurrent unit\" OR \"long short-term memory\"))", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
- **NP-2**
  - `{"exact": true, "language": "zh", "search": "(图神经网络 OR GNN OR 图神经网络模型) AND (分布式训练 OR 分布式学习 OR 分布式并行训练) AND (图摘要 OR 图概括 OR 图压缩 OR \"graph summarization\") AND (领导工作者模式 OR 领导者工作者模式 OR 主从模式 OR 主从架构 OR leader-worker OR master-worker) AND (图流划分 OR 边分割 OR 图划分 OR 图分割 OR 流划分 OR \"graph stream partition\" OR \"edge segmentation\")", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `{"exact": false, "language": null, "search": "(图神经网络 OR GNN OR 图神经网络模型) AND (分布式训练 OR 分布式学习 OR 分布式并行训练) AND (图摘要 OR 图概括 OR 图压缩 OR \"graph summarization\") AND ((领导工作者模式 OR 领导者工作者模式 OR 主从模式 OR 主从架构 OR leader-worker OR master-worker) OR (图流划分 OR 边分割 OR 图划分 OR 图分割 OR 流划分 OR \"graph stream partition\" OR \"edge segmentation\"))", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `{"exact": false, "language": null, "search": "(图神经网络 OR GNN OR 图神经网络模型) AND (分布式训练 OR 分布式学习 OR 分布式并行训练) AND (图摘要 OR 图概括 OR 图压缩 OR \"graph summarization\")", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `(all:"distributed graph neural network training" OR all:"distributed GNN training" OR all:"distributed graph neural network") AND (all:"graph summarization" OR all:"graph summary" OR all:"graph summarization technique") AND (all:"leader-worker" OR all:"leader worker" OR all:"leader-worker mode") AND (all:"graph stream partitioning" OR all:"graph stream partition" OR all:"edge-based graph stream partitioning" OR all:"edge segmentation graph partition") AND (all:"mini-batch training" OR all:"mini-batch" OR all:"mini-batch learning") AND (all:"attention layer" OR all:"attention mechanism" OR all:"attention")`
  - `(all:"distributed graph neural network training" OR all:"distributed GNN training" OR all:"distributed graph neural network") AND (all:"graph summarization" OR all:"graph summary" OR all:"graph summarization technique") AND ((all:"leader-worker" OR all:"leader worker" OR all:"leader-worker mode") OR (all:"graph stream partitioning" OR all:"graph stream partition" OR all:"edge-based graph stream partitioning" OR all:"edge segmentation graph partition")) AND ((all:"mini-batch training" OR all:"mini-batch" OR all:"mini-batch learning") OR (all:"attention layer" OR all:"attention mechanism" OR all:"attention"))`
  - `(all:"distributed graph neural network training" OR all:"distributed GNN training" OR all:"distributed graph neural network") AND (all:"graph summarization" OR all:"graph summary" OR all:"graph summarization technique")`
  - `{"exact": true, "language": "zh", "search": "((\"distributed graph neural network training\" OR \"distributed GNN training\" OR \"distributed training of graph neural networks\" OR \"distributed graph neural network\") AND (\"graph summarization\" OR \"graph summary\" OR \"graph summarization technique\" OR \"graph summarization method\") AND (leader-worker OR \"leader-worker mode\" OR \"leader-worker architecture\" OR \"leader-worker paradigm\" OR \"leader-worker model\") AND (\"graph flow partition\" OR \"graph flow partitioning\" OR \"edge segmentation\" OR \"edge-based graph partition\" OR \"graph partition based on edge segmentation\") AND (\"mini-batch training\" OR mini-batch OR \"mini-batch learning\" OR \"mini-batch gradient descent\") AND (\"attention layer\" OR \"attention mechanism\" OR attention OR attention-based))", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `{"exact": false, "language": null, "search": "((\"distributed graph neural network training\" OR \"distributed GNN training\" OR \"distributed training of graph neural networks\" OR \"distributed graph neural network\") AND (\"graph summarization\" OR \"graph summary\" OR \"graph summarization technique\" OR \"graph summarization method\") AND (leader-worker OR \"leader-worker mode\" OR \"leader-worker architecture\" OR \"leader-worker paradigm\" OR \"leader-worker model\"))", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `{"exact": false, "language": null, "search": "((\"distributed graph neural network training\" OR \"distributed GNN training\" OR \"distributed training of graph neural networks\" OR \"distributed graph neural network\") AND (\"graph summarization\" OR \"graph summary\" OR \"graph summarization technique\" OR \"graph summarization method\"))", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
- **NP-3**
  - `{"exact": true, "language": "zh", "search": "((GSAERU OR GSAERU模型 OR GSAERU算法) AND (图神经网络 OR GNN OR 图深度学习 OR 图卷积网络 OR 图注意力网络) AND (内存消耗 OR 内存占用 OR 内存使用 OR 存储消耗 OR 内存效率) AND (训练时间 OR 训练时长 OR 训练效率 OR 训练速度 OR 计算时间))", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `{"exact": false, "language": null, "search": "((GSAERU OR GSAERU模型 OR GSAERU算法) AND (图神经网络 OR GNN OR 图深度学习 OR 图卷积网络 OR 图注意力网络) AND ((内存消耗 OR 内存占用 OR 内存使用 OR 存储消耗 OR 内存效率) OR (训练时间 OR 训练时长 OR 训练效率 OR 训练速度 OR 计算时间)))", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `{"exact": false, "language": null, "search": "((GSAERU OR GSAERU模型 OR GSAERU算法) AND ((图神经网络 OR GNN OR 图深度学习 OR 图卷积网络 OR 图注意力网络) OR (内存消耗 OR 内存占用 OR 内存使用 OR 存储消耗 OR 内存效率) OR (训练时间 OR 训练时长 OR 训练效率 OR 训练速度 OR 计算时间)))", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `((all:"GSAERU" OR all:"GSAERU模型") AND (all:"图神经网络" OR all:"GNN" OR all:"图神经网络算法") AND (all:"时序图" OR all:"时间图" OR all:"动态图" OR all:"temporal graph") AND (all:"内存消耗" OR all:"内存占用" OR all:"内存使用") AND (all:"训练时间" OR all:"训练时长" OR all:"训练速度") AND (all:"性能最好的算法" OR all:"最佳算法" OR all:"最优算法" OR all:"性能最优" OR all:"接近最佳"))`
  - `((all:"GSAERU" OR all:"GSAERU模型") AND (all:"图神经网络" OR all:"GNN" OR all:"图神经网络算法") AND (all:"时序图" OR all:"时间图" OR all:"动态图" OR all:"temporal graph") AND ((all:"内存消耗" OR all:"内存占用" OR all:"内存使用") OR (all:"训练时间" OR all:"训练时长" OR all:"训练速度")))`
  - `((all:"GSAERU" OR all:"GSAERU模型") AND (all:"图神经网络" OR all:"GNN" OR all:"图神经网络算法"))`
  - `(all:"GSAERU" OR all:"GSAERU model") AND (all:"temporal graph" OR all:"temporal graph representation" OR all:"temporal graph learning" OR all:"dynamic graph representation") AND (all:"memory consumption" OR all:"training time" OR all:"memory efficiency" OR all:"training efficiency" OR all:"computational efficiency")`
  - `((all:"GSAERU" OR all:"GSAERU model") AND (all:"temporal graph" OR all:"temporal graph representation" OR all:"temporal graph learning" OR all:"dynamic graph representation")) OR ((all:"GSAERU" OR all:"GSAERU model") AND (all:"graph neural network" OR all:"GNN" OR all:"graph neural networks")) OR ((all:"temporal graph" OR all:"temporal graph representation" OR all:"temporal graph learning" OR all:"dynamic graph representation") AND (all:"graph neural network" OR all:"GNN" OR all:"graph neural networks") AND (all:"memory consumption" OR all:"training time" OR all:"memory efficiency" OR all:"training efficiency" OR all:"computational efficiency"))`
  - `{"exact": true, "language": "zh", "search": "((GSAERU OR \"GSAERU model\") AND (\"graph neural network\" OR \"graph neural networks\" OR GNN) AND (\"memory consumption\" OR \"memory usage\" OR \"memory footprint\" OR \"memory cost\") AND (\"training time\" OR \"training duration\" OR \"computation time\" OR \"computational cost\" OR \"training cost\") AND (\"best-performing algorithm\" OR \"state-of-the-art algorithm\" OR \"top-performing algorithm\" OR \"best performance\" OR \"state-of-the-art performance\"))", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `{"exact": false, "language": null, "search": "((GSAERU OR \"GSAERU model\") AND (\"graph neural network\" OR \"graph neural networks\" OR GNN) AND (\"memory consumption\" OR \"memory usage\" OR \"memory footprint\" OR \"memory cost\") AND (\"training time\" OR \"training duration\" OR \"computation time\" OR \"computational cost\" OR \"training cost\"))", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`
  - `{"exact": false, "language": null, "search": "((GSAERU OR \"GSAERU model\") AND (\"graph neural network\" OR \"graph neural networks\" OR GNN) AND ((\"memory consumption\" OR \"memory usage\" OR \"memory footprint\" OR \"memory cost\") OR (\"training time\" OR \"training duration\" OR \"computation time\" OR \"computational cost\" OR \"training cost\")))", "select": "id,doi,display_name,publication_year,publication_date,language,type,authorships,primary_location,locations,best_oa_location,open_access,abstract_inverted_index,cited_by_count,is_retracted,is_paratext"}`

---

## 六、检索结果

### 6.1 检索概况

共执行 1 轮检索计划，生成 0 张原始证据卡；通过 0 张，拒绝 0 张。

### 6.2 相关文献

没有证据卡通过质量校验。

### 6.3 证据覆盖情况

| 查新点 | 有效证据数 | 状态 |
| --- | ---: | --- |
| NP-1 | 0 | 未覆盖 |
| NP-2 | 0 | 未覆盖 |
| NP-3 | 0 | 未覆盖 |

### 6.4 未充分覆盖的内容

- NP-1：证据不足
- NP-2：证据不足
- NP-3：证据不足

---

## 七、查新结论

### NP-1 · 证据不足

提出了一种基于图摘要技术的大规模时序图表示学习方法，称为GSAERU模型。

**结论：** 未检索到有效文献支持该查新点。检索范围包括中英文数据库，但未发现与GSAERU模型（基于图摘要的大规模时序图表示学习方法）完全相同的技术方案。现有文献涉及图摘要、图自编码器、时序图表示学习等，但未发现将图摘要与图自编码器结合用于时序图表示学习并采用循环神经网络学习时间维度的完整方案。证据不足，无法判断其新颖性。  
**置信度：** 0.00

### NP-2 · 证据不足

提出了一种基于图摘要技术的分布式图神经网络优化训练算法，称为DSGNN模型。

**结论：** 未检索到有效文献支持该查新点。检索范围包括中英文数据库，但未发现与DSGNN模型（基于图摘要的分布式图神经网络优化训练算法）完全相同的技术方案。现有文献涉及分布式图神经网络训练、图划分、图摘要等，但未发现采用基于边分割的图流划分算法与基于图摘要的小批量训练结合，并通过注意力层返回结果的完整框架。证据不足，无法判断其新颖性。  
**置信度：** 0.00

### NP-3 · 证据不足

提出的GSAERU模型在大规模时序图表示学习中，相比传统方法具有更高的效率和性能。

**结论：** 未检索到有效文献支持该查新点。该查新点声称GSAERU模型相比传统方法具有更高的效率和性能（平均内存消耗9.86%、平均训练时长13.27%、性能差距不超过3.5%）。由于缺乏外部证据，无法验证这些具体数值的准确性。检索范围内未发现直接对比GSAERU模型与基线方法的独立研究。证据不足，无法判断其新颖性。  
**置信度：** 0.00

---

## 八、报告局限

- 检索范围限于公开的中英文文献数据库，可能遗漏未公开或非中英文文献。
- 由于有效证据为空，所有结论均基于论文自身描述，缺乏外部验证。
- 未检索到与查新点完全匹配的现有技术，但可能存在部分相似或相关的工作未被覆盖。

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

---

> 本报告由 Novelty Multi-Agent Framework 根据论文内容、检索结果及证据分析自动生成。
> 报告中的查新结论应以实际检索到的公开文献为依据。
