# `database_search` 失败调用时间轴调查

## 范围与结论

- Run ID：`run-269799e73e0d4e60b84543f854691c6b`
- 时间均为 UTC。
- 本 Run 共 9 个 `database_search` outer call，其中 5 个失败；每个失败 outer call 均包含 6 个 `SearchExecution`，合计 30 次。
- 30 次子执行严格串行，前一次结束后下一次才开始，没有并发重叠。
- 错误分布：`ReadTimeout` 27 次，`HTTPStatusError` 3 次；3 次 HTTP 错误均为 arXiv `429`。
- 5 个 outer call 最终都被归类为 `ToolExecutionError: all 6 search executions failed`。
- `tool_0011` 与 `tool_0023` 的 NP-2/T-1 六条 query 完全相同，是同一检索序列的再次调用，不是同一个 outer call 内的重试。

## Outer call 汇总

| Outer call | 任务 | 开始 | 结束 | 时长 | 子执行错误 |
|---|---|---|---|---:|---|
| `tool_0008` | NP-1/T-1 | `2026-09-13T23:35:46.557951Z` | `2026-09-13T23:40:19.972978Z` | 273.413 s | 6 × `ReadTimeout` |
| `tool_0009` | NP-2/T-2 | `2026-09-13T23:40:19.977460Z` | `2026-09-13T23:43:59.949020Z` | 219.969 s | 5 × `ReadTimeout`; 1 × HTTP 429 |
| `tool_0010` | NP-3/T-1 | `2026-09-13T23:43:59.954510Z` | `2026-09-13T23:49:55.596243Z` | 355.639 s | 4 × `ReadTimeout`; 2 × HTTP 429 |
| `tool_0011` | NP-2/T-1 | `2026-09-13T23:49:55.599725Z` | `2026-09-13T23:52:32.848701Z` | 157.246 s | 6 × `ReadTimeout` |
| `tool_0023` | NP-2/T-1 | `2026-09-13T23:52:38.020595Z` | `2026-09-13T23:56:15.430229Z` | 217.408 s | 6 × `ReadTimeout` |

## `tool_0008`：NP-1/T-1

Outer：`2026-09-13T23:35:46.557951Z` → `2026-09-13T23:40:19.972978Z`，`ToolExecutionError`。

1. S1，`2026-09-13T23:35:46.559730Z` → `2026-09-13T23:36:39.115706Z`（52.556 s）
   Query：`(ti:"音乐生成" OR ti:"music generation") AND (ti:"Museformer" OR ti:"Transformer 变体模型" OR ti:"音乐生成模型") AND (abs:"细粒度注意力" OR abs:"fine-grained attention") ANDNOT (all:"细粒度分类") AND (abs:"粗粒度注意力" OR abs:"coarse-grained attention") ANDNOT (all:"图像超分辨率")`
   错误：`ReadTimeout: The read operation timed out`
2. S1-fb1，`2026-09-13T23:36:39.116031Z` → `2026-09-13T23:37:17.560038Z`（38.444 s）
   Query：`(ti:"Museformer" OR ti:"Transformer 变体模型" OR ti:"音乐生成模型") AND (abs:"细粒度注意力" OR abs:"fine-grained attention") ANDNOT (all:"细粒度分类") AND (abs:"粗粒度注意力" OR abs:"coarse-grained attention") ANDNOT (all:"图像超分辨率")`
   错误：`ReadTimeout: The read operation timed out`
3. S2，`2026-09-13T23:37:17.560402Z` → `2026-09-13T23:38:40.895728Z`（83.335 s）
   Query：`(ti:"音乐生成" OR ti:"music generation" OR ti:"乐曲生成" OR ti:"符号音乐生成") AND (ti:"Museformer" OR ti:"Transformer 变体模型" OR ti:"音乐生成模型" OR ti:Transformer AND ti:variant AND ti:for AND ti:music AND ti:generation OR ti:"音乐 Transformer") AND (abs:"细粒度注意力" OR abs:"fine-grained attention" OR abs:"token 级注意力" OR abs:"细粒度注意力机制") ANDNOT (all:"细粒度分类") AND (abs:"粗粒度注意力" OR abs:"coarse-grained attention" OR abs:"小节级总结注意力" OR abs:"粗粒度注意力机制") ANDNOT (all:"图像超分辨率") AND (abs:"小节级注意力" OR abs:"bar-level attention" OR abs:"总结 token 序列" OR abs:"summary token" OR abs:"音乐结构建模" OR abs:"小节总结信息")`
   错误：`ReadTimeout: The read operation timed out`
4. S2-fb1，`2026-09-13T23:38:40.896298Z` → `2026-09-13T23:39:38.966793Z`（58.070 s）
   Query：`(ti:"Museformer" OR ti:"Transformer 变体模型" OR ti:"音乐生成模型" OR ti:Transformer AND ti:variant AND ti:for AND ti:music AND ti:generation OR ti:"音乐 Transformer") AND (abs:"细粒度注意力" OR abs:"fine-grained attention" OR abs:"token 级注意力" OR abs:"细粒度注意力机制") ANDNOT (all:"细粒度分类") AND (abs:"粗粒度注意力" OR abs:"coarse-grained attention" OR abs:"小节级总结注意力" OR abs:"粗粒度注意力机制") ANDNOT (all:"图像超分辨率") AND (abs:"小节级注意力" OR abs:"bar-level attention" OR abs:"总结 token 序列" OR abs:"summary token" OR abs:"音乐结构建模" OR abs:"小节总结信息")`
   错误：`ReadTimeout: The read operation timed out`
5. S3，`2026-09-13T23:39:38.967021Z` → `2026-09-13T23:39:59.467270Z`（20.500 s）
   Query：`(ti:"Museformer" OR ti:"Transformer 变体模型" OR ti:"音乐生成模型" OR ti:Transformer AND ti:variant AND ti:for AND ti:music AND ti:generation OR ti:"音乐 Transformer") OR (abs:"细粒度注意力" OR abs:"fine-grained attention" OR abs:"token 级注意力" OR abs:"细粒度注意力机制") ANDNOT (all:"细粒度分类") OR (abs:"粗粒度注意力" OR abs:"coarse-grained attention" OR abs:"小节级总结注意力" OR abs:"粗粒度注意力机制") ANDNOT (all:"图像超分辨率")`
   错误：`ReadTimeout: The read operation timed out`
6. S3-fb1，`2026-09-13T23:39:59.467591Z` → `2026-09-13T23:40:19.959961Z`（20.492 s）
   Query：`(ti:"Museformer" OR ti:"Transformer 变体模型" OR ti:"音乐生成模型" OR ti:Transformer AND ti:variant AND ti:for AND ti:music AND ti:generation OR ti:"音乐 Transformer") OR (abs:"细粒度注意力" OR abs:"fine-grained attention" OR abs:"token 级注意力" OR abs:"细粒度注意力机制") OR (abs:"粗粒度注意力" OR abs:"coarse-grained attention" OR abs:"小节级总结注意力" OR abs:"粗粒度注意力机制")`
   错误：`ReadTimeout: The read operation timed out`

## `tool_0009`：NP-2/T-2

Outer：`2026-09-13T23:40:19.977460Z` → `2026-09-13T23:43:59.949020Z`，`ToolExecutionError`。

1. S1，`2026-09-13T23:40:19.979739Z` → `2026-09-13T23:41:26.328975Z`（66.349 s）
   Query：`(ti:"music structure analysis" OR ti:"musical structure" OR ti:"music repetition structure") AND (abs:"self-similarity matrix" OR abs:"similarity statistics" OR abs:"similarity distribution") ANDNOT (all:"image similarity") AND (abs:"structure-related bar selection" OR abs:"music bar selection" OR abs:"bar-level structure identification") AND (abs:"attention computation" OR abs:"attention mechanism" OR abs:"self-attention")`
   错误：`ReadTimeout: The read operation timed out`
2. S1-fb1，`2026-09-13T23:41:26.329340Z` → `2026-09-13T23:41:50.350496Z`（24.021 s）
   Query：`(ti:"music structure analysis" OR ti:"musical structure" OR ti:"music repetition structure") AND (abs:"self-similarity matrix" OR abs:"similarity statistics" OR abs:"similarity distribution") ANDNOT (all:"image similarity") AND (abs:"structure-related bar selection" OR abs:"music bar selection" OR abs:"bar-level structure identification")`
   错误：`ReadTimeout: The read operation timed out`
3. S2，`2026-09-13T23:41:50.350879Z` → `2026-09-13T23:42:10.829057Z`（20.478 s）
   Query：`(ti:"music structure analysis" OR ti:"musical structure" OR ti:"music repetition structure" OR ti:"music form analysis" OR ti:"structural segmentation") AND (abs:"self-similarity matrix" OR abs:"similarity statistics" OR abs:"similarity distribution" OR abs:"SSM" OR abs:"recurrence matrix" OR abs:"self-similarity analysis") ANDNOT (all:"image similarity")`
   错误：`ReadTimeout: The read operation timed out`
4. S2-fb1，`2026-09-13T23:42:10.829485Z` → `2026-09-13T23:43:15.407328Z`（64.578 s）
   Query：`(abs:"self-similarity matrix" OR abs:"similarity statistics" OR abs:"similarity distribution" OR abs:"SSM" OR abs:"recurrence matrix" OR abs:"self-similarity analysis") ANDNOT (all:"image similarity")`
   错误：`HTTPStatusError: 429 Too Many Requests`
5. S3，`2026-09-13T23:43:15.407679Z` → `2026-09-13T23:43:39.427873Z`（24.020 s）
   Query：`(ti:"music structure analysis" OR ti:"musical structure" OR ti:"music repetition structure" OR ti:"music form analysis" OR ti:"structural segmentation") OR (abs:"self-similarity matrix" OR abs:"similarity statistics" OR abs:"similarity distribution" OR abs:"SSM" OR abs:"recurrence matrix" OR abs:"self-similarity analysis") ANDNOT (all:"image similarity") OR (abs:"structure-related bar selection" OR abs:"music bar selection" OR abs:"bar-level structure identification" OR abs:"structural bar detection" OR abs:"relevant bar selection") OR (abs:"attention computation" OR abs:"attention mechanism" OR abs:"self-attention" OR abs:"Transformer attention" OR abs:"attention weighting")`
   错误：`ReadTimeout: The read operation timed out`
6. S3-fb1，`2026-09-13T23:43:39.428073Z` → `2026-09-13T23:43:59.936423Z`（20.508 s）
   Query：`(ti:"music structure analysis" OR ti:"musical structure" OR ti:"music repetition structure" OR ti:"music form analysis" OR ti:"structural segmentation") OR (abs:"self-similarity matrix" OR abs:"similarity statistics" OR abs:"similarity distribution" OR abs:"SSM" OR abs:"recurrence matrix" OR abs:"self-similarity analysis") OR (abs:"structure-related bar selection" OR abs:"music bar selection" OR abs:"bar-level structure identification" OR abs:"structural bar detection" OR abs:"relevant bar selection") OR (abs:"attention computation" OR abs:"attention mechanism" OR abs:"self-attention" OR abs:"Transformer attention" OR abs:"attention weighting")`
   错误：`ReadTimeout: The read operation timed out`

## `tool_0010`：NP-3/T-1

Outer：`2026-09-13T23:43:59.954510Z` → `2026-09-13T23:49:55.596243Z`，`ToolExecutionError`。

1. S1，`2026-09-13T23:43:59.956556Z` → `2026-09-13T23:44:23.981805Z`（24.025 s）
   Query：`(abs:"FC-Attention" OR abs:"全连接注意力" OR abs:"高效注意力实现") AND (abs:"区块稀疏" OR abs:"块稀疏注意力" OR abs:"稀疏注意力") AND (ti:"音乐序列建模" OR ti:"长序列建模" OR ti:"音乐生成")`
   错误：`ReadTimeout: The read operation timed out`
2. S1-fb1，`2026-09-13T23:44:23.982147Z` → `2026-09-13T23:45:48.667113Z`（84.685 s）
   Query：`(abs:"FC-Attention" OR abs:"全连接注意力" OR abs:"高效注意力实现") AND (abs:"区块稀疏" OR abs:"块稀疏注意力" OR abs:"稀疏注意力")`
   错误：`ReadTimeout: The read operation timed out`
3. S2，`2026-09-13T23:45:48.667511Z` → `2026-09-13T23:47:11.791978Z`（83.124 s）
   Query：`(abs:"FC-Attention" OR abs:"全连接注意力" OR abs:"高效注意力实现" OR abs:"Full-connected attention" OR abs:"全连接自注意力" OR abs:"FC 注意力") AND (abs:"区块稀疏" OR abs:"块稀疏注意力" OR abs:"稀疏注意力" OR abs:"block-sparse attention" OR abs:"block sparse" OR abs:"稀疏化注意力")`
   错误：`ReadTimeout: The read operation timed out`
4. S2-fb1，`2026-09-13T23:47:11.792256Z` → `2026-09-13T23:48:46.100449Z`（94.308 s）
   Query：`(abs:"区块稀疏" OR abs:"块稀疏注意力" OR abs:"稀疏注意力" OR abs:"block-sparse attention" OR abs:"block sparse" OR abs:"稀疏化注意力")`
   错误：`HTTPStatusError: 429 Unknown Error`
5. S3，`2026-09-13T23:48:46.100679Z` → `2026-09-13T23:49:35.565299Z`（49.465 s）
   Query：`(abs:"FC-Attention" OR abs:"全连接注意力" OR abs:"高效注意力实现" OR abs:"Full-connected attention" OR abs:"全连接自注意力" OR abs:"FC 注意力") OR (abs:"区块稀疏" OR abs:"块稀疏注意力" OR abs:"稀疏注意力" OR abs:"block-sparse attention" OR abs:"block sparse" OR abs:"稀疏化注意力") OR (ti:"音乐序列建模" OR ti:"长序列建模" OR ti:"音乐生成" OR ti:"长音乐序列" OR ti:"long music sequence" OR ti:"符号音乐生成") OR (abs:"计算复杂度" OR abs:"显存占用" OR abs:"运行时间" OR abs:"存储复杂度" OR abs:"memory consumption" OR abs:"推理速度")`
   错误：`HTTPStatusError: 429 Too Many Requests`
6. S3-fb1，`2026-09-13T23:49:35.565500Z` → `2026-09-13T23:49:55.584783Z`（20.019 s）
   Query：`(abs:"FC-Attention" OR abs:"全连接注意力" OR abs:"高效注意力实现" OR abs:"Full-connected attention" OR abs:"全连接自注意力" OR abs:"FC 注意力") OR (abs:"区块稀疏" OR abs:"块稀疏注意力" OR abs:"稀疏注意力" OR abs:"block-sparse attention" OR abs:"block sparse" OR abs:"稀疏化注意力") OR (ti:"音乐序列建模" OR ti:"长序列建模" OR ti:"音乐生成" OR ti:"长音乐序列" OR ti:"long music sequence" OR ti:"符号音乐生成") OR (abs:"计算复杂度" OR abs:"显存占用" OR abs:"运行时间" OR abs:"存储复杂度" OR abs:"memory consumption" OR abs:"推理速度")`
   错误：`ReadTimeout: The read operation timed out`

## `tool_0011`：NP-2/T-1

Outer：`2026-09-13T23:49:55.599725Z` → `2026-09-13T23:52:32.848701Z`，`ToolExecutionError`。

1. S1，`2026-09-13T23:49:55.601934Z` → `2026-09-13T23:50:16.106036Z`（20.504 s）
   Query：`ti:"音乐结构" AND (abs:"相似度统计" OR abs:"自相似度矩阵") AND abs:"结构相关小节选择" AND abs:"注意力计算"`
   错误：`ReadTimeout: The read operation timed out`
2. S1-fb1，`2026-09-13T23:50:16.106351Z` → `2026-09-13T23:50:40.128575Z`（24.022 s）
   Query：`ti:"音乐结构" AND (abs:"相似度统计" OR abs:"自相似度矩阵") AND abs:"注意力计算"`
   错误：`ReadTimeout: The read operation timed out`
3. S2，`2026-09-13T23:50:40.128800Z` → `2026-09-13T23:51:00.636737Z`（20.508 s）
   Query：`(ti:"音乐结构" OR ti:"音乐曲式" OR ti:"乐曲结构" OR ti:"musical structure") AND (abs:"相似度统计" OR abs:"自相似度矩阵" OR abs:"相似性度量" OR abs:"相似度分布分析" OR abs:"self-similarity matrix")`
   错误：`ReadTimeout: The read operation timed out`
4. S2-fb1，`2026-09-13T23:51:00.637189Z` → `2026-09-13T23:51:28.980487Z`（28.343 s）
   Query：`(abs:"相似度统计" OR abs:"自相似度矩阵" OR abs:"相似性度量" OR abs:"相似度分布分析" OR abs:"self-similarity matrix")`
   错误：`ReadTimeout: The read operation timed out`
5. S3，`2026-09-13T23:51:28.980685Z` → `2026-09-13T23:52:12.348043Z`（43.367 s）
   Query：`(ti:"音乐结构" OR ti:"音乐曲式" OR ti:"乐曲结构" OR ti:"musical structure") OR (abs:"相似度统计" OR abs:"自相似度矩阵" OR abs:"相似性度量" OR abs:"相似度分布分析" OR abs:"self-similarity matrix") OR (abs:"注意力计算" OR abs:"注意力机制" OR abs:"attention computation" OR abs:"自注意力") OR (abs:"音乐重复结构识别" OR abs:"重复段检测" OR abs:"结构分段" OR abs:"音乐重复片段")`
   错误：`ReadTimeout: The read operation timed out`
6. S3-fb1，`2026-09-13T23:52:12.348266Z` → `2026-09-13T23:52:32.833832Z`（20.486 s）
   Query：`(ti:"音乐结构" OR ti:"音乐曲式" OR ti:"乐曲结构" OR ti:"musical structure") OR (abs:"相似度统计" OR abs:"自相似度矩阵" OR abs:"相似性度量" OR abs:"相似度分布分析" OR abs:"self-similarity matrix") OR (abs:"注意力计算" OR abs:"注意力机制" OR abs:"attention computation" OR abs:"自注意力") OR (abs:"音乐重复结构识别" OR abs:"重复段检测" OR abs:"结构分段" OR abs:"音乐重复片段")`
   错误：`ReadTimeout: The read operation timed out`

## `tool_0023`：NP-2/T-1 再次调用

Outer：`2026-09-13T23:52:38.020595Z` → `2026-09-13T23:56:15.430229Z`，`ToolExecutionError`。

1. S1，`2026-09-13T23:52:38.022230Z` → `2026-09-13T23:52:58.492330Z`（20.470 s）
   Query：`ti:"音乐结构" AND (abs:"相似度统计" OR abs:"自相似度矩阵") AND abs:"结构相关小节选择" AND abs:"注意力计算"`
   错误：`ReadTimeout: The read operation timed out`
2. S1-fb1，`2026-09-13T23:52:58.492673Z` → `2026-09-13T23:54:06.615222Z`（68.123 s）
   Query：`ti:"音乐结构" AND (abs:"相似度统计" OR abs:"自相似度矩阵") AND abs:"注意力计算"`
   错误：`ReadTimeout: The read operation timed out`
3. S2，`2026-09-13T23:54:06.615586Z` → `2026-09-13T23:54:27.073905Z`（20.458 s）
   Query：`(ti:"音乐结构" OR ti:"音乐曲式" OR ti:"乐曲结构" OR ti:"musical structure") AND (abs:"相似度统计" OR abs:"自相似度矩阵" OR abs:"相似性度量" OR abs:"相似度分布分析" OR abs:"self-similarity matrix")`
   错误：`ReadTimeout: The read operation timed out`
4. S2-fb1，`2026-09-13T23:54:27.074165Z` → `2026-09-13T23:55:34.508892Z`（67.435 s）
   Query：`(abs:"相似度统计" OR abs:"自相似度矩阵" OR abs:"相似性度量" OR abs:"相似度分布分析" OR abs:"self-similarity matrix")`
   错误：`ReadTimeout: The read operation timed out`
5. S3，`2026-09-13T23:55:34.509313Z` → `2026-09-13T23:55:54.978969Z`（20.470 s）
   Query：`(ti:"音乐结构" OR ti:"音乐曲式" OR ti:"乐曲结构" OR ti:"musical structure") OR (abs:"相似度统计" OR abs:"自相似度矩阵" OR abs:"相似性度量" OR abs:"相似度分布分析" OR abs:"self-similarity matrix") OR (abs:"注意力计算" OR abs:"注意力机制" OR abs:"attention computation" OR abs:"自注意力") OR (abs:"音乐重复结构识别" OR abs:"重复段检测" OR abs:"结构分段" OR abs:"音乐重复片段")`
   错误：`ReadTimeout: The read operation timed out`
6. S3-fb1，`2026-09-13T23:55:54.979583Z` → `2026-09-13T23:56:15.415921Z`（20.436 s）
   Query：`(ti:"音乐结构" OR ti:"音乐曲式" OR ti:"乐曲结构" OR ti:"musical structure") OR (abs:"相似度统计" OR abs:"自相似度矩阵" OR abs:"相似性度量" OR abs:"相似度分布分析" OR abs:"self-similarity matrix") OR (abs:"注意力计算" OR abs:"注意力机制" OR abs:"attention computation" OR abs:"自注意力") OR (abs:"音乐重复结构识别" OR abs:"重复段检测" OR abs:"结构分段" OR abs:"音乐重复片段")`
   错误：`ReadTimeout: The read operation timed out`

## 调查判断

1. 失败发生在 arXiv 读取层，不是 query 解析失败。所有子执行都已生成合法 query 并进入 `structured_source_retrieval`，随后以网络读取超时或服务端限流结束。
2. 放宽链未对网络故障做短路。每个 outer call 在 S1/S1-fb1/S2/S2-fb1/S3/S3-fb1 上继续串行尝试，因此单个失败调用耗时 157–356 秒。
3. `tool_0010` 在连续长等待后出现两次 429，说明同一调用内的顺序重试仍可能触发 arXiv 限流；429 后也没有专门的退避终止策略。
4. `tool_0011` 失败后，系统仍在约 5.17 秒后以 `tool_0023` 完整重放相同六条 NP-2/T-1 query，额外消耗约 217 秒。这是 outer-call 层面的重复检索成本。
5. Runtime 将 30 次失败准确聚合为 5 个失败 outer call，没有把网络失败伪装成成功空结果；状态传播符合 BUG-003 契约。

## 原始证据

完整字段来自以下 Runtime tool records 的 `raw_result.payload.search_executions`：

- `outputs/MG19333vrw-debug-full-20260907/runtime/run-269799e73e0d4e60b84543f854691c6b/tools/0008_database_search.json`
- `outputs/MG19333vrw-debug-full-20260907/runtime/run-269799e73e0d4e60b84543f854691c6b/tools/0009_database_search.json`
- `outputs/MG19333vrw-debug-full-20260907/runtime/run-269799e73e0d4e60b84543f854691c6b/tools/0010_database_search.json`
- `outputs/MG19333vrw-debug-full-20260907/runtime/run-269799e73e0d4e60b84543f854691c6b/tools/0011_database_search.json`
- `outputs/MG19333vrw-debug-full-20260907/runtime/run-269799e73e0d4e60b84543f854691c6b/tools/0023_database_search.json`
