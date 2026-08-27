# Researcher 三工具真实纵向补充实验报告

## 1. 实验目标与结论

验证真实 LLM 经 `ToolCallHarness` 串行调用 WebSearch、Browser、Reader，并验证 LLM 只控制句柄、可信数据由 Runtime 搬运。结论：**success**；Browser 阶段已完成最终补充验收，正式 Researcher Workflow 仍未迁移。

## 2. 代码与运行配置

- 实验代码基线 commit：`551cbaadc65fef62da132633d0c8ba69842c7407`
- 执行时间：2026-08-25T02:56:47.615229+00:00 – 2026-08-25T02:57:54.949305+00:00
- 模型：`deepseek-flash` / `deepseek-ai/DeepSeek-V4-Flash`
- 真实工具：`WebSearchTool(BaiduSearchBackend)`、`BrowserTool(PlaywrightBrowserBackend)`、`ReaderTool(ReferenceArtifactReaderTool)`
- 生产代码修改：无；仅补充实验脚本观测与报告字段

## 3. 原生 Tool Calling 轨迹与参数

- 顺序：`['web_search', 'browser', 'reader']`
- WebSearch：`{"query": "Python asyncio 官方文档", "max_results": 5}`
- Browser：`{"source_record_id": "src_fdee106b1e978830af30329b"}`
- Reader：`{"artifact_id": "art_e6e8b1aab20bb0c7c373b21f", "char_start": 0, "max_chars": 2000}`
- 三组 call ID：`[{'tool_name': 'web_search', 'assistant_tool_call_id': '01a036d98edc4ee6c0680d0235aa2822', 'tool_result_call_id': '01a036d98edc4ee6c0680d0235aa2822', 'matched': True}, {'tool_name': 'browser', 'assistant_tool_call_id': '01a036d9a48f734758ff7ca94b39961d', 'tool_result_call_id': '01a036d9a48f734758ff7ca94b39961d', 'matched': True}, {'tool_name': 'reader', 'assistant_tool_call_id': '01a036da088cbd3633e55169b6672ecc', 'tool_result_call_id': '01a036da088cbd3633e55169b6672ecc', 'matched': True}]`
- 全部 call ID 对齐：**True**

## 4. Control Plane / Data Plane

- Browser 参数只有 `source_record_id`：**True**
- Manifest 恢复的可信 URL：`https://docs.python.org/zh-cn/3.13/library/asyncio.html`
- Browser 实际 requested URL：`https://docs.python.org/zh-cn/3.13/library/asyncio.html`
- URL 来自 Data Plane 且模型未传 URL：**True**
- Reader 使用 BrowserResult 返回的 artifact_id：**True**

模型没有传 URL、work_id、subject_paper_id、source_id 或 backend，也没有向 Reader 复制 HTML/text。

## 5. Context Projection 边界

- WebSearch projection 保留候选句柄、title、URL、snippet、source_name、published_at；不含 raw_metadata/source_records/provider content：**True**
- Browser projection 保留 source/work/artifact 句柄、role、media_type、content_extent、warnings；不含 browser_fetch、HTML、正文、storage path、sha256 或内部 metadata：**True**
- Reader projection 保留 read/work/artifact 句柄、字符范围、text、has_more；正文正常进入模型上下文：**True**
- Projection 字符数：`{'web_search': 7306, 'browser': 309, 'reader': 2511}`

## 6. 完整审计与持久化闭环

- WebSearch、Browser、Reader 的完整 Observation 均保存在 `trace.jsonl`：**True**
- Browser 完整 Observation 包含 browser_fetch/html/text，但 role=tool projection 不包含这些字段。
- SourceRecord → Work → Artifact → Read 从重新加载的 Manifest 验证闭合：**True**
- 句柄：source `src_fdee106b1e978830af30329b` → work `wrk_86600422c9a12affdfaa7ea1` → artifact `art_e6e8b1aab20bb0c7c373b21f` → read `read_a5499710002f73ed22de78ae`

## 7. 最终回答 Grounding

- 最终回答基于 Reader text：**True**
- Reader 正文与最终答案共同核心词：`['asyncio', '并发', '高层级', '低层级']`
- Prompt 明确禁止把搜索 snippet 当正文；模型最终回答声明仅依据 Reader 返回的官方文档正文。

共同关键词仅是最低限度 smoke signal，不是事实正确性 benchmark，也不证明逐句引用对齐。

## 8. Token 与耗时

- 每轮 token：`[{'turn': 1, 'prompt_tokens': 879, 'completion_tokens': 196, 'reasoning_tokens': 119, 'total_tokens': 1075}, {'turn': 2, 'prompt_tokens': 4088, 'completion_tokens': 153, 'reasoning_tokens': 65, 'total_tokens': 4241}, {'turn': 3, 'prompt_tokens': 4320, 'completion_tokens': 120, 'reasoning_tokens': 0, 'total_tokens': 4440}, {'turn': 4, 'prompt_tokens': 5586, 'completion_tokens': 468, 'reasoning_tokens': 159, 'total_tokens': 6054}]`
- 总 token：15810
- 总 Harness 时间：61421.629 ms
- 各模型调用时间：`[11886.504, 4446.075, 10968.51, 20973.239]` ms
- 各工具 Observation 时间：`{'web_search': 643, 'browser': 12501, 'reader': 0}` ms

工具 elapsed 来自现有 Observation，覆盖对应 Tool 的后端调用与持久化；当前没有更细的网络、Chromium launch、DOM 提取、文件写入分项，因此不补造数字。本实验也没有旧版完整 Observation 同任务 A/B，不能宣称节省了特定百分比的 token，只能确认 WebSearch/Browser 大字段未直接进入 Model Context。

## 9. 不稳定因素与环境依赖

百度索引、候选排序、网页内容、导航耗时和模型决策会变化；未来重复运行可能选择不同 SourceRecord。Playwright 1.62.0 只安装 Chromium；当前宿主缺少系统级 NSPR/NSS/ALSA 且无法免密 sudo，本次通过 Novelty Conda 环境安装 `nspr`、`nss`、`alsa-lib`，运行时提供该环境的 library path。

## 10. 未覆盖能力与下一步

本实验未覆盖登录、Cookie profile、CAPTCHA、代理、多页 session、并行 Tool Call、Router、fallback、正式 Researcher Workflow、Validator 或 Reviewer。没有实现 EvidenceCardBuilder。

本次成功标准全部满足，Browser 阶段可以收口，**可以进入 EvidenceCardBuilder 开发**；这不代表 EvidenceCardBuilder 已实现或正式工作流已迁移。

## 11. 最终回答

已按链路完成三次工具调用（web_search → browser → reader），以下回答仅依据 Reader 返回的官方文档正文（art_e6e8b1aab20bb0c7c373b21f，字符 0–2000）。

## 回答

**asyncio 的用途**：asyncio 是用来编写**并发代码**的库，使用 `async/await` 语法；它是多个高性能 Python 异步框架的基础（网络和网站服务、数据库连接库、分布式任务队列等），往往是构建 **IO 密集型和高层级结构化网络代码**的最佳选择。

**两类 API**（官方正文明确区分）：

1. **高层级 API**，用于：
   - 并发地运行 Python 协程并对其执行过程实现完全控制；
   - 执行网络 IO 和 IPC；
   - 控制子进程；
   - 通过队列实现分布式任务；
   - 同步并发代码。

2. **低层级 API**，用于支持库和框架的开发者实现：
   - 创建和管理**事件循环**（提供连接网络、运行子进程、处理 OS 信号等异步 API）；
   - 使用 **transports** 实现高效率协议；
   - 通过 `async/await` 语法**桥接基于回调的库和代码**。

（正文还提到该模块在 WebAssembly 平台上不可用，即 "Availability: not WASI"，以及 asyncio REPL 等附加信息。）
