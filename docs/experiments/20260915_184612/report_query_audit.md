# 检索式遗漏审计与实际查询恢复

以下来自原始运行日志，未重新调用模型或检索API。失败记录表示已进入数据库检索执行层，不表示请求一定发送上网（熔断可能本地拒绝）。Web调用另列，不伪装为数据库检索式。原始三份报告保持不变。

## 01_arxiv

| 查新点 | 语义计划数 | 报告检索式数 | 日志数据库执行记录 | 其中失败 |
|---|---:|---:|---:|---:|
| NP-1 | 2 | 0 | 6 | 6 |
| NP-2 | 4 | 0 | 14 | 14 |
| NP-3 | 4 | 0 | 12 | 12 |

### NP-1

- **arxiv / failed**；日志出现 4 次；任务：T-2
  - 检索式：`(ti:"dynamic graph" OR ti:"temporal graph" OR ti:"sequential graph") AND abs:"graph summarization"`
  - [原始记录](01_arxiv/MF2033k6lC/runtime/run-f763eb9102b0460a925ffcd8ff9f169a/tools/0006_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **arxiv / failed**；日志出现 2 次；任务：T-1
  - 检索式：`(abs:"图摘要" OR abs:"图压缩" OR abs:"图自编码器") AND (abs:"时序图表示学习" OR abs:"动态图表示学习" OR abs:"图神经网络")`
  - [原始记录](01_arxiv/MF2033k6lC/runtime/run-f763eb9102b0460a925ffcd8ff9f169a/tools/0007_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures

### NP-2

- **arxiv / failed**；日志出现 2 次；任务：T-1
  - 检索式：`(abs:"分布式图神经网络训练" OR abs:"图神经网络优化训练算法") AND (abs:"图摘要" OR abs:"图摘要技术") AND (abs:"领导-工作者模式" OR abs:"领导节点") AND abs:"边分割图流划分算法"`
  - [原始记录](01_arxiv/MF2033k6lC/runtime/run-f763eb9102b0460a925ffcd8ff9f169a/tools/0005_database_search.json)
  - 错误：ReadTimeout: The read operation timed out
- **arxiv / failed**；日志出现 4 次；任务：T-2
  - 检索式：`ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"leader-worker mode"`
  - [原始记录](01_arxiv/MF2033k6lC/runtime/run-f763eb9102b0460a925ffcd8ff9f169a/tools/0008_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **arxiv / failed**；日志出现 4 次；任务：T-R2-2
  - 检索式：`ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization" AND abs:"graph partitioning"`
  - [原始记录](01_arxiv/MF2033k6lC/runtime/run-f763eb9102b0460a925ffcd8ff9f169a/tools/0078_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **arxiv / failed**；日志出现 4 次；任务：T-R2-1
  - 检索式：`(ti:"分布式图神经网络" OR ti:"分布式GNN训练") AND (abs:"图摘要" OR abs:"图压缩") AND abs:"领导-工作者模式"`
  - [原始记录](01_arxiv/MF2033k6lC/runtime/run-f763eb9102b0460a925ffcd8ff9f169a/tools/0079_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures

### NP-3

- **arxiv / failed**；日志出现 3 次；任务：T-1
  - 检索式：`ti:"分布式图神经网络训练" AND abs:"注意力机制"`
  - [原始记录](01_arxiv/MF2033k6lC/runtime/run-f763eb9102b0460a925ffcd8ff9f169a/tools/0032_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **arxiv / failed**；日志出现 2 次；任务：T-2
  - 检索式：`ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"attention layer"`
  - [原始记录](01_arxiv/MF2033k6lC/runtime/run-f763eb9102b0460a925ffcd8ff9f169a/tools/0049_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **arxiv / failed**；日志出现 3 次；任务：T-R2-1
  - 检索式：`(abs:"注意力机制" OR abs:"注意力层" OR abs:"加权融合") AND (abs:"分布式图神经网络" OR abs:"分布式GNN训练" OR abs:"工作节点结果融合")`
  - [原始记录](01_arxiv/MF2033k6lC/runtime/run-f763eb9102b0460a925ffcd8ff9f169a/tools/0074_database_search.json)
  - 错误：HTTPStatusError: Client error '429 Too Many Requests' for url 'https://export.arxiv.org/api/query?search_query=%28abs%3A%22%E6%B3%A8%E6%84%8F%E5%8A%9B%E6%9C%BA%E5%88%B6%22+OR+abs%3A%22%E6%B3%A8%E6%84%8F%E5%8A%9B%E5%B1%82%22+OR+abs%3A%22%E5%8A%A0%E6%9D%83%E8%9E%8D%E5%90%88%22%29+AND+%28abs%3A%22%E5%8
- **arxiv / failed**；日志出现 4 次；任务：T-R2-2
  - 检索式：`(abs:"attention mechanism" OR abs:"attention layer" OR abs:"attention-based aggregation") AND (abs:distributed AND abs:graph AND abs:neural AND abs:network AND abs:training OR abs:"distributed GNN training") AND (abs:worker AND abs:node AND abs:result AND abs:aggregation OR abs:"worker result fusion" OR abs:"result aggregation")`
  - [原始记录](01_arxiv/MF2033k6lC/runtime/run-f763eb9102b0460a925ffcd8ff9f169a/tools/0076_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures

## 02_arxiv_springer

| 查新点 | 语义计划数 | 报告检索式数 | 日志数据库执行记录 | 其中失败 |
|---|---:|---:|---:|---:|
| NP-1 | 4 | 1 | 16 | 14 |
| NP-2 | 2 | 0 | 6 | 6 |
| NP-3 | 2 | 1 | 7 | 6 |

### NP-1

- **springer / failed**；日志出现 2 次；任务：T-1
  - 检索式：`("图摘要" OR "图压缩" OR "图快照压缩") AND ("图自编码器" OR "图自动编码器" OR "重构误差") AND ("循环神经网络" OR "时间依赖建模" OR "时序图学习") AND ("动态图" OR "时序图" OR "图快照序列")`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0009_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404
- **arxiv / failed**；日志出现 2 次；任务：T-2
  - 检索式：`(ti:"dynamic graph" OR ti:"temporal graph" OR ti:"sequential graph") AND (abs:"graph representation learning" OR abs:"graph embedding" OR abs:"node embedding") AND (abs:"graph summarization" OR abs:"graph compression") AND (abs:"graph autoencoder" OR abs:"reconstruction error") AND (abs:"recurrent neural network" OR abs:"temporal dependency")`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0011_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **arxiv / failed**；日志出现 2 次；任务：T-1
  - 检索式：`(abs:"图摘要" OR abs:"图压缩" OR abs:"图快照压缩") AND (abs:"图自编码器" OR abs:"图自动编码器" OR abs:"重构误差") AND (abs:"循环神经网络" OR abs:"时间依赖建模" OR abs:"时序图学习") AND (ti:"动态图" OR ti:"时序图" OR ti:"图快照序列")`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0012_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **springer / succeeded**；日志出现 2 次；任务：T-2
  - 检索式：`("dynamic graph" OR "temporal graph" OR "sequential graph") AND ("graph representation learning" OR "graph embedding" OR "node embedding") AND ("graph summarization" OR "graph compression") AND ("graph autoencoder" OR "reconstruction error") AND ("recurrent neural network" OR "temporal dependency")`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0026_database_search.json)
- **arxiv / failed**；日志出现 2 次；任务：T-R2-2
  - 检索式：`ti:sequential AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder"`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0079_database_search.json)
  - 错误：ReadTimeout: The read operation timed out
- **arxiv / failed**；日志出现 2 次；任务：T-R2-1
  - 检索式：`(abs:"图摘要" OR abs:"图压缩" OR abs:"图概括") AND (abs:"图自编码器" OR abs:"图自动编码器" OR abs:"图重构") AND (abs:"循环神经网络" OR abs:"递归神经网络") AND (ti:"时序图" OR ti:"动态图" OR ti:"时间演化图") AND (ti:"图表示学习" OR ti:"节点表征" OR ti:"网络嵌入")`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0080_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **springer / failed**；日志出现 2 次；任务：T-R2-1
  - 检索式：`("图摘要" OR "图压缩" OR "图概括") AND ("图自编码器" OR "图自动编码器" OR "图重构") AND ("循环神经网络" OR "递归神经网络") AND ("时序图" OR "动态图" OR "时间演化图") AND ("图表示学习" OR "节点表征" OR "网络嵌入")`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0081_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404
- **springer / failed**；日志出现 2 次；任务：T-R2-2
  - 检索式：`"sequential graph representation learning" AND "graph summarization" AND "graph autoencoder"`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0082_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404

### NP-2

- **arxiv / failed**；日志出现 1 次；任务：T-1
  - 检索式：`(ti:"分布式图神经网络训练" OR ti:"分布式GNN训练") AND (abs:"图摘要" OR abs:"图流划分")`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0008_database_search.json)
  - 错误：ReadTimeout: The read operation timed out
- **arxiv / failed**；日志出现 2 次；任务：T-2
  - 检索式：`ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0010_database_search.json)
  - 错误：ReadTimeout: The read operation timed out
- **springer / failed**；日志出现 1 次；任务：T-1
  - 检索式：`("分布式图神经网络训练" OR "分布式GNN训练") AND ("图摘要" OR "图流划分")`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0013_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404
- **springer / failed**；日志出现 2 次；任务：T-2
  - 检索式：`"distributed graph neural network training" AND "graph summarization"`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0028_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404

### NP-3

- **springer / failed**；日志出现 2 次；任务：T-1
  - 检索式：`"边分割图流划分算法" AND "图流数据" AND "分布式图神经网络训练"`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0024_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404
- **arxiv / failed**；日志出现 2 次；任务：T-1
  - 检索式：`abs:"边分割图流划分算法" AND ti:"图流数据" AND abs:"分布式图神经网络训练"`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0025_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **arxiv / failed**；日志出现 2 次；任务：T-2
  - 检索式：`(abs:"edge-based graph partitioning" OR abs:"edge partitioning algorithm" OR abs:"graph stream partitioning") AND (ti:"graph neural network" OR ti:"distributed training" OR ti:"graph streaming")`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0046_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **springer / succeeded**；日志出现 1 次；任务：T-2
  - 检索式：`("edge-based graph partitioning" OR "edge partitioning algorithm" OR "graph stream partitioning") AND ("graph neural network" OR "distributed training" OR "graph streaming")`
  - [原始记录](02_arxiv_springer/MF2033k6lC/runtime/run-cb9a3ecc9c4a4a57896cf12fa7b62706/tools/0049_database_search.json)

## 03_arxiv_springer_web

| 查新点 | 语义计划数 | 报告检索式数 | 日志数据库执行记录 | 其中失败 |
|---|---:|---:|---:|---:|
| NP-1 | 4 | 1 | 8 | 7 |
| NP-2 | 4 | 0 | 11 | 11 |
| NP-3 | 4 | 1 | 13 | 12 |

### NP-1

- **arxiv / failed**；日志出现 2 次；任务：T-1
  - 检索式：`(abs:"图摘要" OR abs:"图压缩" OR abs:"图自编码器") AND (abs:"时序图表示学习" OR abs:"动态图表示学习" OR abs:"图神经网络") AND (abs:"循环神经网络" OR abs:"时间依赖建模" OR abs:"时间特征提取")`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0004_database_search.json)
  - 错误：HTTPStatusError: Client error '429 Unknown Error' for url 'https://export.arxiv.org/api/query?search_query=%28abs%3A%22%E5%9B%BE%E6%91%98%E8%A6%81%22+OR+abs%3A%22%E5%9B%BE%E5%8E%8B%E7%BC%A9%22+OR+abs%3A%22%E5%9B%BE%E8%87%AA%E7%BC%96%E7%A0%81%E5%99%A8%22%29+AND+%28abs%3A%22%E6%97%B6%E5%BA%8F%E5%9B%BE
- **arxiv / failed**；日志出现 1 次；任务：T-2
  - 检索式：`(ti:"large-scale temporal graph" OR ti:"dynamic graph" OR ti:"sequential graph") AND (abs:"graph summarization" OR abs:"graph compression") AND (abs:"graph autoencoder" OR abs:"graph representation learning") AND (abs:"recurrent neural network" OR abs:"temporal dependency modeling")`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0010_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **springer / failed**；日志出现 2 次；任务：T-1
  - 检索式：`("图摘要" OR "图压缩" OR "图自编码器") AND ("时序图表示学习" OR "动态图表示学习" OR "图神经网络") AND ("循环神经网络" OR "时间依赖建模" OR "时间特征提取")`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0013_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404
- **springer / succeeded**；日志出现 1 次；任务：T-2
  - 检索式：`("large-scale temporal graph" OR "dynamic graph" OR "sequential graph") AND ("graph summarization" OR "graph compression") AND ("graph autoencoder" OR "graph representation learning") AND ("recurrent neural network" OR "temporal dependency modeling")`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0018_database_search.json)
- **springer / failed**；日志出现 1 次；任务：T-R2-2
  - 检索式：`"large-scale temporal graph representation learning" AND "graph summarization" AND "graph autoencoder" AND "recurrent neural network on graphs"`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0089_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404
- **arxiv / failed**；日志出现 1 次；任务：T-R2-2
  - 检索式：`ti:large-scale AND ti:temporal AND ti:graph AND ti:representation AND ti:learning AND abs:"graph summarization" AND abs:"graph autoencoder" AND abs:recurrent AND abs:neural AND abs:network AND abs:on AND abs:graphs`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0091_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures

### NP-2

- **arxiv / failed**；日志出现 1 次；任务：T-2
  - 检索式：`ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:graph AND abs:summarization AND abs:based AND abs:mini-batch AND abs:training`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0006_database_search.json)
  - 错误：ReadTimeout: The read operation timed out
- **arxiv / failed**；日志出现 1 次；任务：T-1
  - 检索式：`(ti:"分布式图神经网络" OR ti:"分布式GNN训练") AND (abs:"图摘要" OR abs:"图流划分" OR abs:"边分割") AND (abs:"领导-工作者模式" OR abs:"小批量训练" OR abs:"注意力层")`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0012_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **springer / failed**；日志出现 1 次；任务：T-2
  - 检索式：`"distributed graph neural network training" AND "graph summarization based mini-batch training"`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0019_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404
- **springer / failed**；日志出现 1 次；任务：T-1
  - 检索式：`("分布式图神经网络" OR "分布式GNN训练") AND ("图摘要" OR "图流划分" OR "边分割") AND ("领导-工作者模式" OR "小批量训练" OR "注意力层")`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0020_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404
- **arxiv / failed**；日志出现 2 次；任务：T-R2-1
  - 检索式：`(ti:"分布式图神经网络" OR ti:"分布式GNN训练") AND (abs:"图摘要" OR abs:"图流划分" OR abs:"边分割") AND (abs:"小批量训练" OR abs:"注意力层" OR abs:"领导-工作者模式")`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0087_database_search.json)
  - 错误：ReadTimeout: The read operation timed out
- **arxiv / failed**；日志出现 2 次；任务：T-R2-2
  - 检索式：`ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training AND abs:"graph summarization"`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0088_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **springer / failed**；日志出现 2 次；任务：T-R2-2
  - 检索式：`"distributed graph neural network training" AND "graph summarization"`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0099_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404
- **springer / failed**；日志出现 1 次；任务：T-R2-1
  - 检索式：`("分布式图神经网络" OR "分布式GNN训练") AND ("图摘要" OR "图流划分" OR "边分割") AND ("小批量训练" OR "注意力层" OR "领导-工作者模式")`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0108_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404

### NP-3

- **arxiv / failed**；日志出现 2 次；任务：T-2
  - 检索式：`abs:"edge-based graph partitioning" AND abs:graph AND abs:streaming AND abs:partition AND abs:algorithm AND ti:distributed AND ti:graph AND ti:neural AND ti:network AND ti:training`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0059_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **springer / failed**；日志出现 1 次；任务：T-2
  - 检索式：`"edge-based graph partitioning" AND "graph streaming partition algorithm" AND "distributed graph neural network training"`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0061_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404
- **arxiv / failed**；日志出现 2 次；任务：T-1
  - 检索式：`(abs:"边分割" OR abs:"边划分" OR abs:"图分割") AND (abs:"图划分算法" OR abs:"图分割算法" OR abs:"图分区算法")`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0065_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **springer / failed**；日志出现 2 次；任务：T-1
  - 检索式：`("边分割" OR "边划分" OR "图分割") AND ("图划分算法" OR "图分割算法" OR "图分区算法")`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0066_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404
- **arxiv / failed**；日志出现 3 次；任务：T-R2-1
  - 检索式：`ti:"图流划分算法" AND abs:"边分割" AND abs:"分布式图神经网络训练"`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0101_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **springer / failed**；日志出现 1 次；任务：T-R2-1
  - 检索式：`"图流划分算法" AND "边分割" AND "分布式图神经网络训练"`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0111_database_search.json)
  - 错误：ProviderRequestError: Springer Nature API returned HTTP 404
- **arxiv / failed**；日志出现 1 次；任务：T-R2-2
  - 检索式：`(abs:"edge-based graph partitioning" OR abs:"edge-cut partitioning" OR abs:"graph stream partitioning")`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0137_database_search.json)
  - 错误：ArxivCircuitOpenError: arxiv circuit is open after consecutive provider failures
- **springer / succeeded**；日志出现 1 次；任务：T-R2-2
  - 检索式：`("edge-based graph partitioning" OR "edge-cut partitioning" OR "graph stream partitioning")`
  - [原始记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0138_database_search.json)

### Web 查询（按调用记录，含本地拒绝）

- SUCCESS：`DSGNN 分布式图神经网络 图摘要 领导-工作者 链路预测`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0008_web_search.json)
- SUCCESS：`DSGNN 图摘要 分布式图神经网络 训练 领导节点 工作节点`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0011_web_search.json)
- SUCCESS：`GSAERU 图摘要 时序图表示学习 图自编码器 循环神经网络`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0014_web_search.json)
- SUCCESS：`图摘要 时序图 表示学习 大规模 图自编码器 循环神经网络 论文`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0016_web_search.json)
- SUCCESS：`GSAERU 图摘要 时序图 表示学习`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0022_web_search.json)
- FAILED：`DSGNN distributed graph neural network graph summarization leader worker training`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0023_web_search.json)
- SUCCESS：`DSGNN distributed graph neural network graph summarization`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0025_web_search.json)
- SUCCESS：`DSGNN 图摘要 分布式图神经网络 链路预测 F1`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0026_web_search.json)
- FAILED：`GSAERU graph summarization temporal graph representation learning autoencoder`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0028_web_search.json)
- SUCCESS：`DSGNN graph summarization distributed GNN link prediction F1`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0029_web_search.json)
- SUCCESS：`GSAERU graph summarization temporal graph representation`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0030_web_search.json)
- SUCCESS：`"DSGNN" distributed graph neural network summarization`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0032_web_search.json)
- SUCCESS：`DSGNN graph summarization distributed GNN training paper`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0033_web_search.json)
- SUCCESS：`GSAERU 图摘要 时序图 表示学习 自编码器`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0034_web_search.json)
- SUCCESS：`GSAERU 图摘要 大规模时序图 表示学习`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0038_web_search.json)
- SUCCESS：`Distributed Graph Neural Network Training: A Survey arxiv`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0039_web_search.json)
- SUCCESS：`"GSAERU" 时序图 表示学习`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0042_web_search.json)
- FAILED：`graph summarization based temporal graph representation learning autoencoder RNN large-scale`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0046_web_search.json)
- SUCCESS：`DSGNN 图摘要 分布式 图神经网络 训练 算法 论文`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0048_web_search.json)
- FAILED：`DSGNN graph summarization distributed GNN training leader worker edge partition attention`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0051_web_search.json)
- FAILED：`"图摘要" 分布式图神经网络 领导 工作节点 注意力 链路预测 训练`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0055_web_search.json)
- SUCCESS：`边分割 图流划分算法 分布式图神经网络训练 子图划分`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0062_web_search.json)
- FAILED：`edge-based graph streaming partition algorithm distributed graph neural network training`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0063_web_search.json)
- SUCCESS：`edge-based graph streaming partition distributed GNN training`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0064_web_search.json)
- FAILED：`streaming edge partitioning algorithm distributed GNN training subgraph worker`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0067_web_search.json)
- SUCCESS：`streaming edge partitioning distributed GNN training`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0069_web_search.json)
- FAILED：`edge partitioning streaming graph partition algorithm distributed GNN training subgraph worker`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0071_web_search.json)
- SUCCESS：`边分割 图流划分 分布式图神经网络 子图分配`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0072_web_search.json)
- SUCCESS：`edge-based streaming graph partition algorithm distributed GNN training`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0078_web_search.json)
- FAILED：`edge-cut streaming graph partitioning distributed GNN subgraph worker nodes`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0079_web_search.json)
- FAILED：`edge-cut streaming graph partitioning distributed GNN`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0080_web_search.json)
- SUCCESS：`GSAERU 图摘要 时序图表示学习 图自编码器 循环神经网络`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0086_web_search.json)
- SUCCESS：`GSAERU 图摘要 大规模时序图 表示学习`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0090_web_search.json)
- SUCCESS：`图摘要 动态图 表示学习 图自编码器 循环神经网络 大规模`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0092_web_search.json)
- SUCCESS：`GSAERU 图摘要 时序图 表示学习 论文`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0093_web_search.json)
- SUCCESS：`图摘要 图压缩 动态图 表示学习 图自编码器 循环神经网络 综述`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0094_web_search.json)
- FAILED：`图摘要 图自编码器 循环神经网络 动态图 表示学习 大规模`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0095_web_search.json)
- SUCCESS：`图流划分算法 边分割 分布式图神经网络训练 负载均衡`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0097_web_search.json)
- SUCCESS：`分布式图神经网络 图摘要 小批量训练 链路预测`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0098_web_search.json)
- FAILED：`large-scale temporal graph representation learning graph summarization graph autoencoder recurrent neural network`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0100_web_search.json)
- SUCCESS：`temporal graph representation learning graph summarization autoencoder`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0102_web_search.json)
- SUCCESS：`图流划分算法综述 边分割 负载均衡 知乎`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0103_web_search.json)
- SUCCESS：`distributed graph neural network training graph summarization mini-batch`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0105_web_search.json)
- SUCCESS：`图流划分算法综述 边分割 流式 知乎 zhuanlan`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0106_web_search.json)
- SUCCESS：`graph summarization dynamic graph embedding autoencoder RNN snapshots`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0107_web_search.json)
- SUCCESS：`DSGNN 分布式图神经网络 图摘要 链路预测`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0112_web_search.json)
- FAILED：`graph summarization distributed GNN training leader worker attention aggregation link prediction`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0113_web_search.json)
- SUCCESS：`graph summarization distributed GNN training`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0115_web_search.json)
- FAILED：`graph summarization temporal graph neural network large scale representation learning`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0123_web_search.json)
- SUCCESS：`Sketch-DBH 图流划分 边分割 Count-Min Sketch 分布式图神经网络`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0124_web_search.json)
- SUCCESS：`graph summarization temporal graph representation learning`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0125_web_search.json)
- FAILED：`GSE Graph Summarization Embedding model hypergraph skip-gram`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0130_web_search.json)
- SUCCESS：`distributed GNN training graph summarization leader worker attention`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0135_web_search.json)
- FAILED：`edge-based graph streaming partition algorithm distributed GNN training HDRF`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0143_web_search.json)
- SUCCESS：`edge-based graph streaming partition distributed GNN training`；[记录](03_arxiv_springer_web/MF2033k6lC/runtime/run-c64223762d494aaf8c5112bda571430a/tools/0144_web_search.json)
