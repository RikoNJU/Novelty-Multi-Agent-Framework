# Formal Researcher Workflow Live Smoke

## 目标与最终结论

验证真实 `NoveltyWorkflow.arun()` 的正式 Researcher 数据路径。结论：**success**。新 TaskResearcher 已使用 ToolCallHarness → WebSearch → Browser → Reader → ResearchFinishDraft → EvidenceCardBuilder。

## 基线与图路径

- 第一阶段 commit：`2cff585d4cb90a0cb7883e0dbabd425a8629f615`
- 第二阶段 commit：见包含本报告的提交
- 节点序列：`['extract_points', 'plan', 'dispatch_research_tasks', 'run_research_task', 'validate_evidence', 'assess_coverage', 'synthesize_report', 'render_report']`
- dispatch task 数：1
- Task 身份：`TASK-formal` / `NP-formal`

## Tool Calling 与 Finish

- 工具序列：`['web_search', 'browser', 'reader']`
- 参数：`[{'name': 'web_search', 'arguments': {'query': 'Python asyncio official documentation event loop coroutines', 'max_results': 10}}, {'name': 'browser', 'arguments': {'source_record_id': 'src_0222fd3b18413e28fca44edd'}}, {'name': 'reader', 'arguments': {'artifact_id': 'art_0bc534293c31bed7e07056c6', 'char_start': 0, 'max_chars': 8000}}]`
- Browser 只接收 source_record_id；Reader 使用 Browser 返回的 artifact_id：见完整 trace
- finish JSON：`{"cards": [{"main_contribution": "Python 官方文档（3.5 版 asyncio 章节）明确说明 asyncio 模块为使用协程编写单线程并发代码提供基础设施，通过可插拔的事件循环（pluggable event loop）复用/多路复用 I/O 访问，并基于 yield from（PEP 380）提供协程与任务，直接支持“Python asyncio 使用事件循环协调并发协程与异步 I/O”这一主张。", "quotes": [{"quote": "This module provides infrastructure for writing single-threaded concurrent code using coroutines, multiplexing I/O access over sockets and other resources, running network clients and servers, and other related primitives.", "interpretation": "官方文档将 asyncio 定义为使用协程编写单线程并发代码的基础设施，并复用（multiplexing）套接字等资源的 I/O 访问，印证了“并发协程 + 异步 I/O”的核心描述。", "confidence": 0.98}, {"quote": "a pluggable event loop with various system-specific implementations;", "interpretation": "官方文档将事件循环列为 asyncio 包内容的首要组件，说明事件循环是 asyncio 协调机制的核心，且可针对不同系统实现。", "confidence": 0.97}, {"quote": "coroutines and tasks based on yield from (PEP 380), to help write concurrent code in a sequential fashion;", "interpretation": "官方文档说明协程与任务基于 yield from（PEP 380），用于以顺序方式编写并发代码，佐证事件循环调度下协程并发执行的机制。", "confidence": 0.96}], "overlaps": ["主张中的技术特征“事件循环”“协程”“异步 I/O”均出现在官方文档正文中", "官方文档将事件循环列为 asyncio 包内容的首要组件，与主张中“事件循环协调”一致", "官方文档描述协程用于编写并发代码，与主张中“并发协程”一致"], "differences": ["官方文档将事件循环描述为“可插拔的、具有多种系统特定实现”，主张未提及该细节", "官方文档基于 Python 3.5 版本（yield from/PEP 380 语法），主张为一般性概括，未限定版本", "官方文档还列举了传输/协议、Future、取消支持等更多组件，主张仅聚焦事件循环、协程与异步 I/O"], "possible_baseline": false, "relevance": 1.0, "confidence": 0.97}], "no_evidence_reason": null}`
- finish 禁止 provenance handle：`[]`
- trusted reads：1

## Builder、绑定与 fan-in

- Builder 调用：`[{'elapsed_ms': 0.592, 'evidence_count': 3, 'card_count': 1}]`；Evidence/Card：3/1
- 一文献一卡及 task/point binding：通过 schema 校验
- fan-in 完整：True
- 四组件共享 ReferenceStore：True
- 旧路径调用：`{'NoveltyResearchAgent.decide': 0, 'StructuredSourceRetrievalTool': 0, 'StructuredRetrievalResearcherTool': 0, 'compile_evidence_drafts': 0}`
- persistence：Task result、audit、evidence cards、report 均由正式图写入；实验另存快照

## Token、耗时与外部状况

- 每轮 token：`[{'prompt_tokens': 1596, 'completion_tokens': 147, 'total_tokens': 1743, 'completion_tokens_details': {'reasoning_tokens': 78}, 'prompt_tokens_details': {'cached_tokens': 0}, 'prompt_cache_hit_tokens': 0, 'prompt_cache_miss_tokens': 1596}, {'prompt_tokens': 5668, 'completion_tokens': 503, 'total_tokens': 6171, 'completion_tokens_details': {'reasoning_tokens': 444}, 'prompt_tokens_details': {'cached_tokens': 1536}, 'prompt_cache_hit_tokens': 1536, 'prompt_cache_miss_tokens': 4132}, {'prompt_tokens': 5866, 'completion_tokens': 94, 'total_tokens': 5960, 'completion_tokens_details': {'reasoning_tokens': 0}, 'prompt_tokens_details': {'cached_tokens': 0}, 'prompt_cache_hit_tokens': 0, 'prompt_cache_miss_tokens': 5866}, {'prompt_tokens': 8282, 'completion_tokens': 1042, 'total_tokens': 9324, 'completion_tokens_details': {'reasoning_tokens': 471}, 'prompt_tokens_details': {'cached_tokens': 5632}, 'prompt_cache_hit_tokens': 5632, 'prompt_cache_miss_tokens': 2650}]`；总 token：23198
- 各 Task 耗时：`[63816.132]` ms；Workflow 总耗时：63828.171 ms
- 模型耗时：`[4386.698, 27582.487, 2640.392, 20790.908]` ms；工具耗时：`[{'name': 'web_search', 'elapsed_ms': 1049}, {'name': 'browser', 'elapsed_ms': 7362}, {'name': 'reader', 'elapsed_ms': 0}]`
- 外部失败/页面失败：以 trace 中失败 observation 和 warnings 为准

## 数据缺口与实验问题

- 第一次尝试中模型单轮发出多个工具调用，串行 Harness 正确拒绝；第二次在 Prompt 明确单轮单工具后成功。
- 主图当前没有正式节点级 telemetry；节点序列来自已编译图定义，而 Task 请求、结果和 Harness trace 由实验 wrapper 旁路采集。
- “旧路径调用为 0”由正式装配不含旧对象及成功 trace 证明，尚无统一的跨组件调用计数器。
- 模型 usage 仅记录 provider 返回的 token 字段，缺少费用、网络排队时间和首 token 延迟。
- NoveltyRunResult 不公开 raw task results/raw evidence，本实验依赖 wrapper 验证 fan-in；这是一项可观测性缺口。
- persistence 已验证目标文件存在并可解析，但尚未记录逐文件校验和与原子写入指标。
- backend/.env 含 shell 不兼容行，直接 source 会产生警告；项目内部加载器可正确加载，密钥未写入产物。

## 限制与下一步

透传 Validator 只存在于本实验，真实 Validator 尚未适配 Builder v1 的 `locator=None/location=None` contract；Reviewer 尚未迁移。本次仅一个点、一个任务、`max_rounds=1`，不证明多轮质量。若状态为 success，可以进入 Validator + Reviewer 迁移。

## 后续更新：EvidenceCard 定位修复

上文记录的 `locator=None / location=None` 问题已修复：`EvidenceCardBuilder` 现在会在引文匹配后计算其在 Reader 文本中的真实字符区间，并回填 `Evidence.locator`（`char_start/char_end`）与 `EvidenceSource.location`（格式 `artifact <artifact_id> chars:<start>-<end>`）。`DefaultEvidenceValidator` 的 `require_direct_quote` 门槛保持不变；相关单测与 Validator 集成回归已通过。另为 Reviewer 注入可信当前日期，并增强 Coordinator synthesize 对 Markdown 围栏 JSON 的解析与一次重试。
