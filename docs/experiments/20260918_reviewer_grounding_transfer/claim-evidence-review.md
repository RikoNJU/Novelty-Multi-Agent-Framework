# Historical claim and evidence comparison

This is the **already seen L1 diagnostic output**, not a new S1 model judgment or a semantic gold standard. The source quote below is the text actually sent in historical S0. Each `relation`, `basis_type`, and `reason` is the old model's claim; support remains unassessed. All seven newly registered reads were absent from that historical summary request. The authorized S1 request did send those seven reads, but timed out without a response, so no new claim can be assessed.

## Card card_055dcd710a45194158c1d5ba

Single-card verdict: `partially_novel`; historical summary verdict: `partially_novel`.

### F1: contradicted

Basis: `direct_statement`; context: `author_method`; cited: `ev_c8d31bd880ce2c28d6c3e196`.

Model reason: 2PS 使用 int[] 度数数组和聚类卷（vol）数组存储顶点信息，未使用 Count-Min Sketch 概率数据结构。

Actual S0 quote (ev_c8d31bd880ce2c28d6c3e196; Work `wrk_b77f32398f578aa48e68b57c`; Artifact `art_082358a7cb0efe62d471f7fb`; truncated=False):

> In this paper, we propose 2PS, a novel two-phase streaming algorithm for high-quality edge partitioning. In the first phase, vertices are separated into clusters by a lightweight streaming clustering algorithm. In the second phase, the graph is re-streamed and edge partitioning is performed while taking into account the clustering of the vertices from the first phase.

### F2: contradicted

Basis: `direct_statement`; context: `author_method`; cited: `ev_c8d31bd880ce2c28d6c3e196`.

Model reason: 2PS 算法使用聚类卷数组和顶点-簇映射，未使用最小堆维护高频节点信息。

Actual S0 quote (ev_c8d31bd880ce2c28d6c3e196; Work `wrk_b77f32398f578aa48e68b57c`; Artifact `art_082358a7cb0efe62d471f7fb`; truncated=False):

> In this paper, we propose 2PS, a novel two-phase streaming algorithm for high-quality edge partitioning. In the first phase, vertices are separated into clusters by a lightweight streaming clustering algorithm. In the second phase, the graph is re-streamed and edge partitioning is performed while taking into account the clustering of the vertices from the first phase.

### F3: contradicted

Basis: `direct_statement`; context: `author_method`; cited: `ev_c8d31bd880ce2c28d6c3e196`.

Model reason: 2PS 未描述基于概率数据结构的常数时间查询机制，其分配基于聚类卷比较。

Actual S0 quote (ev_c8d31bd880ce2c28d6c3e196; Work `wrk_b77f32398f578aa48e68b57c`; Artifact `art_082358a7cb0efe62d471f7fb`; truncated=False):

> In this paper, we propose 2PS, a novel two-phase streaming algorithm for high-quality edge partitioning. In the first phase, vertices are separated into clusters by a lightweight streaming clustering algorithm. In the second phase, the graph is re-streamed and edge partitioning is performed while taking into account the clustering of the vertices from the first phase.

### F4: partially_supported

Basis: `semantic_equivalence`; context: `author_method`; cited: `ev_c8d31bd880ce2c28d6c3e196`.

Model reason: 2PS 在第二阶段根据顶点聚类信息为每条边分配分区，功能上类似生成分配目标，但依据是聚类而非节点度数信息生成子图编号。

Actual S0 quote (ev_c8d31bd880ce2c28d6c3e196; Work `wrk_b77f32398f578aa48e68b57c`; Artifact `art_082358a7cb0efe62d471f7fb`; truncated=False):

> In this paper, we propose 2PS, a novel two-phase streaming algorithm for high-quality edge partitioning. In the first phase, vertices are separated into clusters by a lightweight streaming clustering algorithm. In the second phase, the graph is re-streamed and edge partitioning is performed while taking into account the clustering of the vertices from the first phase.

### F5: partially_supported

Basis: `direct_statement`; context: `author_method`; cited: `ev_c8d31bd880ce2c28d6c3e196`.

Model reason: 2PS 目标为低复制因子和低内存开销的流式边划分，与负载均衡目标部分重合，但未明确描述大规模图流数据的高效划分与负载均衡保证。

Actual S0 quote (ev_c8d31bd880ce2c28d6c3e196; Work `wrk_b77f32398f578aa48e68b57c`; Artifact `art_082358a7cb0efe62d471f7fb`; truncated=False):

> In this paper, we propose 2PS, a novel two-phase streaming algorithm for high-quality edge partitioning. In the first phase, vertices are separated into clusters by a lightweight streaming clustering algorithm. In the second phase, the graph is re-streamed and edge partitioning is performed while taking into account the clustering of the vertices from the first phase.

Review limit: the old output often derives absence from non-mention in a limited quote. The quote and reason are juxtaposed for independent review; no semantic support is certified.

## Card card_927caf724042beff967b2231

Single-card verdict: `partially_novel`; historical summary verdict: `partially_novel`.

### F1: contradicted

Basis: `direct_statement`; context: `author_method`; cited: `ev_6c078063949967ee95518dc2`.

Model reason: WStream 使用分布式元数据文件存储已见顶点信息，未提及 Count-Min Sketch 概率数据结构。

Actual S0 quote (ev_6c078063949967ee95518dc2; Work `wrk_dd602dc2d2b07d7e69e6724c`; Artifact `art_044b624240993e16c40f3537`; truncated=False):

> This paper proposes an efficient window-based streaming graph partitioning algorithm called WStream. The WStream algorithm is an edge-cut partitioning algorithm, which distributes a vertex among the partitions. Our results suggest that the WStream algorithm is able to partition large graph data efficiently while keeping the load balanced across different partitions, and communication to a minimum.

### F2: contradicted

Basis: `direct_statement`; context: `author_method`; cited: `ev_6c078063949967ee95518dc2`.

Model reason: WStream 算法描述中未使用最小堆维护高频节点信息，采用窗口机制与元数据文件。

Actual S0 quote (ev_6c078063949967ee95518dc2; Work `wrk_dd602dc2d2b07d7e69e6724c`; Artifact `art_044b624240993e16c40f3537`; truncated=False):

> This paper proposes an efficient window-based streaming graph partitioning algorithm called WStream. The WStream algorithm is an edge-cut partitioning algorithm, which distributes a vertex among the partitions. Our results suggest that the WStream algorithm is able to partition large graph data efficiently while keeping the load balanced across different partitions, and communication to a minimum.

### F3: unknown

Basis: `insufficient`; context: `author_method`; cited: `ev_6c078063949967ee95518dc2`.

Model reason: 摘要与算法描述未提及常数时间查询机制，无法确认或否定。

Actual S0 quote (ev_6c078063949967ee95518dc2; Work `wrk_dd602dc2d2b07d7e69e6724c`; Artifact `art_044b624240993e16c40f3537`; truncated=False):

> This paper proposes an efficient window-based streaming graph partitioning algorithm called WStream. The WStream algorithm is an edge-cut partitioning algorithm, which distributes a vertex among the partitions. Our results suggest that the WStream algorithm is able to partition large graph data efficiently while keeping the load balanced across different partitions, and communication to a minimum.

### F4: contradicted

Basis: `direct_statement`; context: `author_method`; cited: `ev_6c078063949967ee95518dc2`.

Model reason: WStream 基于窗口策略分配顶点到分区，而非根据节点度数信息生成子图编号。

Actual S0 quote (ev_6c078063949967ee95518dc2; Work `wrk_dd602dc2d2b07d7e69e6724c`; Artifact `art_044b624240993e16c40f3537`; truncated=False):

> This paper proposes an efficient window-based streaming graph partitioning algorithm called WStream. The WStream algorithm is an edge-cut partitioning algorithm, which distributes a vertex among the partitions. Our results suggest that the WStream algorithm is able to partition large graph data efficiently while keeping the load balanced across different partitions, and communication to a minimum.

### F5: supported

Basis: `direct_statement`; context: `author_method`; cited: `ev_6c078063949967ee95518dc2`.

Model reason: 摘要明确声明 WStream 能高效划分大规模图数据并保持各分区负载均衡。

Actual S0 quote (ev_6c078063949967ee95518dc2; Work `wrk_dd602dc2d2b07d7e69e6724c`; Artifact `art_044b624240993e16c40f3537`; truncated=False):

> This paper proposes an efficient window-based streaming graph partitioning algorithm called WStream. The WStream algorithm is an edge-cut partitioning algorithm, which distributes a vertex among the partitions. Our results suggest that the WStream algorithm is able to partition large graph data efficiently while keeping the load balanced across different partitions, and communication to a minimum.

Review limit: the old output often derives absence from non-mention in a limited quote. The quote and reason are juxtaposed for independent review; no semantic support is certified.
