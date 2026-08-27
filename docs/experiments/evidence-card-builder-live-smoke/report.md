# EvidenceCardBuilder 真实纵向实验报告

## 1. 目标与结论

验证真实 LLM 完成 WebSearch → Browser → Reader 后只提交无 provenance handle 的语义 `ResearchFinishDraft`，再由 Workflow-style post-processing 从 Harness trace 提取 trusted reads，交给确定性 Builder 恢复来源并生成 Evidence/Card。结论：**success**。

首次尝试记录：`[{'attempt': 1, 'status': 'failed', 'reason': 'response_format=json_object was applied to intermediate native tool-calling turns; the model stopped before browser and the post-check found no browser event'}]`。首次把 JSON-only response format 错误施加到中间原生 Tool Calling 轮次，模型在 Browser 前结束；本次移除该实验选项后进行任务书允许的一次重跑。没有加入 JSON 修复逻辑。

## 2. 环境与生产修改

- 代码基线 commit：`cc022cdbda352c31ee7f35d94681ed4578be81d6`
- 模型：`deepseek-flash` / `deepseek-ai/DeepSeek-V4-Flash`
- 时间：2026-08-25T03:23:30.001521+00:00 – 2026-08-25T03:24:38.612193+00:00
- 生产修改：新增 `EvidenceCardBuilder` 及 schema contract；未修改 Harness、三工具、Validator、Reviewer、Coordinator 或正式 Workflow

## 3. Tool Calling

- 轨迹：`['web_search', 'browser', 'reader']`
- 参数：`{'web_search': {'query': 'Python asyncio 官方文档', 'max_results': 5}, 'browser': {'source_record_id': 'src_fdee106b1e978830af30329b'}, 'reader': {'artifact_id': 'art_e6e8b1aab20bb0c7c373b21f', 'char_start': 0, 'max_chars': 2000}}`
- Browser 仅 source_record_id：True
- Reader 使用 Browser artifact：True
- tool_call_id 全部对齐：True

## 4. 模型 Finish 与可信 Read

模型原始 JSON：

```json
{"cards":[{"main_contribution":"Python 官方文档将 asyncio 定义为使用 async/await 语法编写并发代码的库，并指出它常是构建 IO 密集型与高层级结构化网络代码的最佳选择，同时提供高层级 API（并发运行协程、网络 IO/IPC、子进程、队列分布式任务、同步并发代码）与面向库/框架开发者的低层级 API（事件循环、transports、回调桥接）。","overlaps":[],"differences":[],"quotes":[{"quote":"asyncio 是用来编写 并发 代码的库，使用 async/await 语法。","interpretation":"官方文档对 asyncio 的核心定位：它是一个以 async/await 语法编写并发代码的标准库，这构成了其全部高层级与低层级 API 设计的基础。","confidence":0.97}],"possible_baseline":false,"relevance":0.95,"confidence":0.9}],"no_evidence_reason":null}
```

- 严格解析 ResearchFinishDraft：True
- 禁止的 provenance keys：`[]`
- Trusted read 数量：1
- quote → read / Work 候选与交集结果：`[{'quote': 'asyncio 是用来编写 并发 代码的库，使用 async/await 语法。', 'matched_read_ids': ['read_a5499710002f73ed22de78ae'], 'candidate_work_ids': ['wrk_86600422c9a12affdfaa7ea1']}]` → final `['wrk_86600422c9a12affdfaa7ea1']`
- ambiguity/cross-work：无

## 5. Builder 恢复与输出

- Builder 自动恢复 work_id：`['wrk_86600422c9a12affdfaa7ea1']`
- Builder 自动恢复 artifact_id：`['art_e6e8b1aab20bb0c7c373b21f']`
- Builder 自动恢复 source_record_id：`['src_fdee106b1e978830af30329b']`
- Work title：`asyncio --- 异步 I/O — Python 3.13.15 文档`，来自 Manifest Work
- URL：`https://docs.python.org/zh-cn/3.13/library/asyncio.html`，来自 Manifest SourceRecord
- DOI：`None`，仅从 Manifest identifiers 恢复；本来源没有则为 None
- card_id：`card_8f1462954bb63c711797abdb`
- evidence_ids：`['ev_c718c3adcf128c06cf7a6bf4']`
- Evidence 数 / Card 数：1 / 1
- locator 全为 None：True
- EvidenceSource.location 全为 None：True
- 一文献一卡：True
- IDs 重复构建稳定：True

重复 read 的确定性选择顺序为 `artifact_id, char_start, char_end, read_id`。Quote 只允许原始 exact substring 或仅 whitespace normalization 后的 exact substring；不做 LLM、embedding、编辑距离或语义模糊匹配。

## 6. 完整追踪链与边界

- SourceRecord → Work → Artifact → Read → Evidence → Card 闭合：True
- Evidence.provenance.read_id 来自真实 Harness trace
- Builder 调用 LLM：False（必须 False）
- Builder 注册为 Agent Tool：False（必须 False）
- 当前 EvidenceCard schema 校验：通过；字段保持 Reviewer 输入所需的 sources/evidence_ids/语义评分结构
- Validator compatibility probe：not executed; Validator migration is out of scope

## 7. Token 与耗时

- 每轮 token：`[{'turn': 1, 'prompt_tokens': 1017, 'completion_tokens': 164, 'reasoning_tokens': 98, 'total_tokens': 1181}, {'turn': 2, 'prompt_tokens': 4215, 'completion_tokens': 96, 'reasoning_tokens': 38, 'total_tokens': 4311}, {'turn': 3, 'prompt_tokens': 4417, 'completion_tokens': 98, 'reasoning_tokens': 0, 'total_tokens': 4515}, {'turn': 4, 'prompt_tokens': 5661, 'completion_tokens': 422, 'reasoning_tokens': 209, 'total_tokens': 6083}]`
- 总 token：16090
- Harness 总耗时：62701.517 ms
- 模型调用耗时：`[3520.929, 4779.175, 2429.451, 39762.909]` ms
- 工具耗时：`{'web_search': 614, 'browser': 11591, 'reader': 0}` ms
- Builder 自身耗时：0.518 ms

## 8. 已知限制与下一步

本次只使用一个稳定官方网页和一张 Card；共同来源解析成功不代表多文献检索质量。Whitespace normalization 不产生统一 locator，因此 v1 明确保留 `locator=None`、`location=None`。当前 Validator 可能仍要求 location，这是后续迁移项，不是 Builder 失败。本任务未迁移正式 Researcher Workflow、Validator 或 Reviewer。

核心成功标准全部满足，**可以进入 Validator / Reviewer 迁移设计**；在此之前还需要把 Workflow finish 后处理显式接到 Builder。
