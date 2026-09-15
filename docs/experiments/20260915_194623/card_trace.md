# 逐篇候选→读取→证据卡追踪

本附件仅回放已有产物，无模型/API请求。未读取不等于不相关；没有逐篇理由的地方明确标记未知。

## 01_arxiv

```json
{
  "database_candidates": 0,
  "database_read": 0,
  "database_fulltext_acquired": 0,
  "database_fulltext_read": 0,
  "database_reason_counts": {},
  "partial_tasks": 8,
  "reads_in_partial_tasks": 22,
  "raw_cards": 3,
  "validator_rejected": 0,
  "final_cards": 3,
  "final_database_cards": 0,
  "final_subject_reference_cards": 3,
  "web_sources": 0,
  "web_artifacts": 0
}
```

### 数据库文献逐篇记录

| 文献 | 有全文 | 读取次数 | 卡片数 | 原因 |
|---|---|---:|---:|---|

### 任务记录

| 查新点 / 任务 | 状态 | 读取 | 卡片 | 原因 |
|---|---|---:|---:|---|
| [NP-1 / T-1](../20260915_184612/01_arxiv/MF2033k6lC/research-runs/NP-1/T-1/attempt-1.json) | partial | 3 | 0 | native tool harness failed: reference_search tool-call budget exhausted |
| [NP-1 / T-2](../20260915_184612/01_arxiv/MF2033k6lC/research-runs/NP-1/T-2/attempt-1.json) | completed | 6 | 3 | 正常产卡 |
| [NP-2 / T-1](../20260915_184612/01_arxiv/MF2033k6lC/research-runs/NP-2/T-1/attempt-1.json) | partial | 2 | 0 | native tool harness failed: reference_search tool-call budget exhausted |
| [NP-2 / T-2](../20260915_184612/01_arxiv/MF2033k6lC/research-runs/NP-2/T-2/attempt-1.json) | partial | 2 | 0 | native tool harness failed: database_search tool-call budget exhausted |
| [NP-2 / T-R2-1](../20260915_184612/01_arxiv/MF2033k6lC/research-runs/NP-2/T-R2-1/attempt-2.json) | partial | 2 | 0 | native tool harness failed: reference_search tool-call budget exhausted |
| [NP-2 / T-R2-2](../20260915_184612/01_arxiv/MF2033k6lC/research-runs/NP-2/T-R2-2/attempt-2.json) | partial | 2 | 0 | native tool harness failed: database_search tool-call budget exhausted |
| [NP-3 / T-1](../20260915_184612/01_arxiv/MF2033k6lC/research-runs/NP-3/T-1/attempt-1.json) | completed | 4 | 0 | no evidence: 在可用的参考文献池中检索了分布式图神经网络训练、注意力机制、结果融合、图摘要、链路预测等相关关键词，并读取了最相关的候选文献（AliGraph、AGL、Graph Attention Networks、GraphSAINT）的全文摘要。这些文献分别涉及分布式GNN平台、基于k-hop子图的分布式GNN系统、图注意力网络架构、图采样小批量训练等主题，但均未描述'工作节点将基于图摘要的小批量训练结果通过注意力层输出、领导节点依据注意力权重汇总各工作节点结果并计算梯度'这一具体技术方案。数据库检索（arxiv）多次执行失败，且当前工具集中无web_search工具可用，无法进一步扩大中文文献检索范围。因此，未找到与查新点NP-3（基于注意力层的工作节点结果融合方法用于分布式图神经网络训练及链路预测）完全匹配的现有文献证据。 |
| [NP-3 / T-2](../20260915_184612/01_arxiv/MF2033k6lC/research-runs/NP-3/T-2/attempt-1.json) | partial | 4 | 0 | native tool harness failed: reference_search tool-call budget exhausted |
| [NP-3 / T-R2-1](../20260915_184612/01_arxiv/MF2033k6lC/research-runs/NP-3/T-R2-1/attempt-2.json) | partial | 3 | 0 | native tool harness failed: reference_search tool-call budget exhausted |
| [NP-3 / T-R2-2](../20260915_184612/01_arxiv/MF2033k6lC/research-runs/NP-3/T-R2-2/attempt-2.json) | partial | 4 | 0 | native tool harness failed: database_search tool-call budget exhausted |

## 02_arxiv_springer

```json
{
  "database_candidates": 16,
  "database_read": 6,
  "database_fulltext_acquired": 4,
  "database_fulltext_read": 1,
  "database_reason_counts": {
    "not_read": 10,
    "only_read_in_aborted_tasks_no_builder": 3,
    "builder_rejected_modified_quote": 1,
    "card_produced": 1,
    "read_but_not_selected_no_per_work_reason": 1
  },
  "partial_tasks": 5,
  "reads_in_partial_tasks": 20,
  "raw_cards": 3,
  "validator_rejected": 0,
  "final_cards": 3,
  "final_database_cards": 1,
  "final_subject_reference_cards": 2,
  "web_sources": 0,
  "web_artifacts": 0
}
```

### 数据库文献逐篇记录

| 文献 | 有全文 | 读取次数 | 卡片数 | 原因 |
|---|---|---:|---:|---|
| [Networked data science: a unified network modeling framework](../20260915_184612/02_arxiv_springer/MF2033k6lC/references/list.json) | 是 | 0 | 0 | 未读取；无逐篇排除理由 |
| [A Survey of Link Prediction in Temporal Networks](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-1/T-2/attempt-1.json) | 是 | 5 | 0 | 读取后任务中断；未调用Builder |
| [Graph Neural Networks (GNNs)](../20260915_184612/02_arxiv_springer/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [Research on the construction of dynamic knowledge graph and intelligent decision-making for enterprise human resource information based on federated hyper graph neural network](../20260915_184612/02_arxiv_springer/MF2033k6lC/references/list.json) | 是 | 0 | 0 | 未读取；无逐篇排除理由 |
| [Graph neural networks: Historical backgrounds, present revolutions, and conventionalization for the future](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-1/T-2/attempt-1.json) | 否 | 1 | 0 | 读取后任务中断；未调用Builder |
| [GraphXAI: a survey of graph neural networks (GNNs) for explainable AI (XAI)](../20260915_184612/02_arxiv_springer/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [Graph Interpretation, Summarization and Visualization Techniques: A Review and Open Research Issues](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-1/T-2/attempt-1.json) | 否 | 1 | 0 | 读取后任务中断；未调用Builder |
| [Graph Neural Networks for Molecules](../20260915_184612/02_arxiv_springer/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [HGP-IC: graph neural networks via hotness-based partitioning and information compensation](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-3/T-2/attempt-1.json) | 否 | 2 | 0 | 引文被模型改写；Builder拒绝 |
| [A two-phase streaming edge partitioning algorithm for large-scale uncertain graphs](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-3/T-2/attempt-1.json) | 否 | 1 | 1 | 已产卡 |
| [Continuous-time dynamic graph learning based on spatio-temporal random walks](../20260915_184612/02_arxiv_springer/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [LocalDGP: local degree-balanced graph partitioning for lightweight GNNs](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-3/T-2/attempt-1.json) | 否 | 1 | 0 | 读取后未选入卡片；未记录逐篇理由 |
| [PECC: parallel expansion based on clustering coefficient for efficient graph partitioning](../20260915_184612/02_arxiv_springer/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [Directed dynamic attribute graph anomaly detection based on evolved graph attention for blockchain](../20260915_184612/02_arxiv_springer/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [A large-scale data security detection method based on continuous time graph embedding framework](../20260915_184612/02_arxiv_springer/MF2033k6lC/references/list.json) | 是 | 0 | 0 | 未读取；无逐篇排除理由 |
| [WawPart: Workload-Aware Partitioning of Knowledge Graphs](../20260915_184612/02_arxiv_springer/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |

### 任务记录

| 查新点 / 任务 | 状态 | 读取 | 卡片 | 原因 |
|---|---|---:|---:|---|
| [NP-1 / T-1](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-1/T-1/attempt-1.json) | partial | 1 | 0 | native tool harness failed: reference_search tool-call budget exhausted |
| [NP-1 / T-2](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-1/T-2/attempt-1.json) | partial | 9 | 0 | native tool harness failed: total tool-call budget exhausted |
| [NP-1 / T-R2-1](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-1/T-R2-1/attempt-2.json) | partial | 2 | 0 | native tool harness failed: reference_search tool-call budget exhausted |
| [NP-1 / T-R2-2](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-1/T-R2-2/attempt-2.json) | partial | 3 | 0 | native tool harness failed: reference_search tool-call budget exhausted |
| [NP-2 / T-1](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-2/T-1/attempt-1.json) | partial | 5 | 0 | native tool harness failed: reference_search tool-call budget exhausted |
| [NP-2 / T-2](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-2/T-2/attempt-1.json) | completed | 6 | 2 | 正常产卡 |
| [NP-3 / T-1](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-3/T-1/attempt-1.json) | completed | 0 | 0 | no evidence: 无法获取任何可验证的文献证据。原论文参考文献池（reference_search）对'边分割图流划分'、'图流划分'、'分布式图神经网络 子图划分'等关键词均返回0条结果；已配置的两个结构化数据库（springer、arxiv）的database_search执行均持续失败（all search executions failed），未返回任何候选来源或Artifact；且本会话未提供web_search工具，无法按中文文献检索策略补充检索。由于没有任何Reader文本可供逐字引用，依据证据引用规则，不能构造任何EvidenceCard，故返回空卡片列表。 |
| [NP-3 / T-2](../20260915_184612/02_arxiv_springer/MF2033k6lC/research-runs/NP-3/T-2/attempt-1.json) | completed | 6 | 1 | dropped evidence card #1: ValueError: ungrounded quote: 'the "graph partitioning + + local learning" framework splits the global graph into smaller subgraphs for independent training' |

## 03_arxiv_springer_web

```json
{
  "database_candidates": 16,
  "database_read": 3,
  "database_fulltext_acquired": 3,
  "database_fulltext_read": 1,
  "database_reason_counts": {
    "only_read_in_aborted_tasks_no_builder": 1,
    "not_read": 13,
    "card_produced": 1,
    "builder_rejected_modified_quote": 1
  },
  "partial_tasks": 9,
  "reads_in_partial_tasks": 24,
  "raw_cards": 2,
  "validator_rejected": 0,
  "final_cards": 2,
  "final_database_cards": 1,
  "final_subject_reference_cards": 1,
  "web_sources": 227,
  "web_artifacts": 0
}
```

### 数据库文献逐篇记录

| 文献 | 有全文 | 读取次数 | 卡片数 | 原因 |
|---|---|---:|---:|---|
| [A Survey of Link Prediction in Temporal Networks](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-1/T-2/attempt-1.json) | 是 | 2 | 0 | 读取后任务中断；未调用Builder |
| [Graph Neural Networks (GNNs)](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [Graph neural networks: Historical backgrounds, present revolutions, and conventionalization for the future](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [PromptGNN: a prompt-enhanced graph neural network for continual learning on temporal graphs](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [GraphXAI: a survey of graph neural networks (GNNs) for explainable AI (XAI)](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [Data Science in Transportation Networks with Graph Neural Networks: A Review and Outlook](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 是 | 0 | 0 | 未读取；无逐篇排除理由 |
| [Advanced persistent threat detection via mining long-term features in provenance graphs](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [Anomaly Detection Model for Edge Network Infrastructure Based on Time Series](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [Scalability and performance in distributed graph databases](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-3/T-R2-2/attempt-2.json) | 否 | 2 | 1 | 已产卡 |
| [HGP-IC: graph neural networks via hotness-based partitioning and information compensation](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-3/T-R2-2/attempt-2.json) | 否 | 2 | 0 | 引文被模型改写；Builder拒绝 |
| [Assessing the complexity of a path search optimization method based on clustering for a transport graph](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 是 | 0 | 0 | 未读取；无逐篇排除理由 |
| [SCG-tree: shortcut enhanced graph hierarchy tree for efficient spatial queries on massive road networks](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [Continuous-time dynamic graph learning based on spatio-temporal random walks](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [Distributed Temporal Graph Neural Network Learning over Large-Scale Dynamic Graphs](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [A graph partitioning-based hybrid feature selection method in microarray datasets](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |
| [Distributed k-Hop Query Powered by an Asynchronous Framework](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/references/list.json) | 否 | 0 | 0 | 未读取；无逐篇排除理由 |

### 任务记录

| 查新点 / 任务 | 状态 | 读取 | 卡片 | 原因 |
|---|---|---:|---:|---|
| [NP-1 / T-1](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-1/T-1/attempt-1.json) | partial | 4 | 0 | native tool harness failed: total tool-call budget exhausted |
| [NP-1 / T-2](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-1/T-2/attempt-1.json) | partial | 2 | 0 | native tool harness failed: web_search tool-call budget exhausted |
| [NP-1 / T-R2-1](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-1/T-R2-1/attempt-2.json) | partial | 0 | 0 | native tool harness failed: web_search tool-call budget exhausted |
| [NP-1 / T-R2-2](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-1/T-R2-2/attempt-2.json) | partial | 2 | 0 | native tool harness failed: web_search tool-call budget exhausted |
| [NP-2 / T-1](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-2/T-1/attempt-1.json) | partial | 2 | 0 | native tool harness failed: web_search tool-call budget exhausted |
| [NP-2 / T-2](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-2/T-2/attempt-1.json) | partial | 2 | 0 | native tool harness failed: web_search tool-call budget exhausted |
| [NP-2 / T-R2-1](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-2/T-R2-1/attempt-2.json) | partial | 8 | 0 | native tool harness failed: total tool-call budget exhausted |
| [NP-2 / T-R2-2](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-2/T-R2-2/attempt-2.json) | completed | 3 | 1 | 正常产卡 |
| [NP-3 / T-1](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-3/T-1/attempt-1.json) | partial | 2 | 0 | native tool harness failed: reference_search tool-call budget exhausted |
| [NP-3 / T-2](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-3/T-2/attempt-1.json) | partial | 2 | 0 | native tool harness failed: web_search tool-call budget exhausted |
| [NP-3 / T-R2-1](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-3/T-R2-1/attempt-2.json) | completed | 0 | 0 | no evidence: 无法获得可验证的Reader文本。数据库检索(arxiv、springer)多次执行均失败,未返回任何artifact_id;工具集中没有可用的browser工具来获取网页正文。web_search返回的详细片段(如知乎《图流划分算法综述》中关于图流划分、边划分、负载均衡的内容)属于发现元数据而非证据,依据证据引用规则,不能仅凭搜索片段创建证据卡片。因此未能获得任何可逐字引用的Reader观察文本,无法为NP-3(基于边分割的图流划分算法)提供有效证据。 |
| [NP-3 / T-R2-2](../20260915_184612/03_arxiv_springer_web/MF2033k6lC/research-runs/NP-3/T-R2-2/attempt-2.json) | completed | 6 | 1 | dropped evidence card #1: ValueError: ungrounded quote: 'the "graph partitioning + local learning" framework splits the global graph into smaller subgraphs for independent training. Existing graph partitioning methods fall into node and edge partitioning.' |
