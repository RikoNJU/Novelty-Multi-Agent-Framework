# WebSearch + ToolCallHarness 真实纵向接入实验报告

## 1. 实验目标与结论

本实验验证真实 LLM → `ToolCallHarness` → `ResearcherToolRegistry` → `WebSearchTool` → `BaiduSearchBackend` → 百度 API → `ReferenceManifest` → role=tool → LLM 的完整纵向链路。

结论：实验状态为 **success**。模型主动调用 `web_search`，搜索返回 5 个候选来源，所有 source_record_id 可从 Manifest 恢复，第二轮模型基于真实搜索结果完成候选整理。

## 2. 环境与配置

- 执行时间：2026-08-24T19:01:20.947035+00:00 – 2026-08-24T19:01:30.350841+00:00
- Python：3.11.15
- 平台：Linux-6.18.33.2-microsoft-standard-WSL2-x86_64-with-glibc2.39
- 模型：`deepseek-flash` / `deepseek-ai/DeepSeek-V4-Flash`
- SiliconFlow Key：configured（值未记录）
- Baidu Key：configured（值未记录）
- Subject paper：`EXP_WEBSEARCH_HARNESS`
- 生产代码修改：无

## 3. 临时 Prompt 与任务

System Prompt：

> 你是一个网页搜索工具调用测试 Agent。
> 
> 当用户要求搜索网络信息时，必须调用 web_search 工具获取真实搜索结果，不得凭记忆
> 编造搜索结果。web_search 返回的是候选来源信息，不是已验证证据。你可以根据 title、
> url、snippet 和 source_name 对候选来源做简要整理，但不得声称已经阅读网页正文，也不
> 得把 snippet 当作正式证据。获得工具结果后，直接基于实际返回的搜索结果回答用户。

User Task：

> 请搜索“多智能体 科技查新 论文”，获取最多 5 个网页候选来源，然后根据
> 搜索结果列出其中 3 个候选来源的标题、来源网站和简短摘要。不要声称已经阅读网页正文。

## 4. ToolDefinition

LLM 收到的工具名称为 `web_search`，description 明确搜索结果不是证据；参数 properties 只有 `query` 与 `max_results`，与 `WebSearchArguments.model_json_schema()` 一致：**True**。模型不可见 backend、provider、API Key、subject_paper_id 或 source_id。

## 5. 第一轮 Tool Call 与参数保真

- Tool Call ID：`01a035261fdf14249c0758ee11a2975e`
- 模型参数：`{"query": "多智能体 科技查新 论文", "max_results": 5}`
- Backend 实收参数：`{"query": "多智能体 科技查新 论文", "max_results": 5}`
- 参数完全一致：**True**

Harness 与 Registry 未静默修改 query/max_results，也未注入百度参数。subject_paper_id 仅由可信 scope 进入 WebSearchTool。

## 6. 百度搜索与持久化

- WebSearchItem：5
- 首次 Manifest SourceRecord：5
- 所有 ID 可恢复：True
- SourceRecord 关键字段有效：True
- 重复执行 stable ID：True
- Manifest 未重复膨胀：True
- 来源域名：`baijiahao.baidu.com` × 3、`mp.weixin.qq.com` × 1、`blog.csdn.net` × 1

snippet 与 provider content 仅是候选来源发现材料，没有生成 Artifact 或 Evidence。

## 7. 原生消息轨迹

第二轮 Context roles：`['system', 'user', 'assistant', 'tool']`，符合 system → user → assistant → tool：**True**。assistant Tool Call 与 role=tool 的 call ID 对齐：**True**。

Trace 共 6 条事件，包含 initial_user_message、assistant_response、tool_call、tool_result、assistant_response 与 finish。

## 8. 最终回答与语义边界

最终回答：

> 根据搜索结果，我获得了 5 个候选来源。以下列出其中 3 个候选来源的标题、来源网站和简短摘要（仅基于搜索结果中的标题与摘要片段整理，未阅读网页正文）：
> 
> **候选来源 1**
> - **标题**：知识图谱+多智能体大模型
> - **来源网站**：腾讯网（微信公众号文章）
> - **简短摘要**：搜索结果摘要显示，该文介绍了一种名为"多图多智能体递归检索"（Multi-Graph Multi-Agent Recursive Retrieval）的新方法，用于处理复杂文档（如法律文本）的检索任务，通过多层次的图结构和多个智能体协同工作，以递归方式处理跨条款、跨文档的依赖关系，提高检索效率与准确性。
> 
> **候选来源 2**
> - **标题**：2025-2026多智能体与AI代理领域10篇顶会论文精选：从协调行为到安全攻防
> - **来源网站**：CSDN软件开发网
> - **简短摘要**：搜索结果摘要显示，该文精选了 2025-2026 年间多智能体与 AI 代理领域的 10 篇论文，涵盖多智能体协调、异构目标跟踪、自我进化技能获取、时间约束执行、软件工程代理优化、提示注入攻击防御、检索增强辩论等前沿方向，并附有论文作者、机构及 arXiv 链接等信息。
> 
> **候选来源 3**
> - **标题**：复旦MOSS团队核心成员发布全新多智能体系统，可自动完成"从文献调研到论文撰写"科研全流程
> - **来源网站**：百家号
> - **简短摘要**：搜索结果摘要显示，该文报道了复旦大学 MOSS 团队核心成员创办的 AI 公司发布的多智能体系统 FARS（Fully Automated Research System），该系统可全自动完成文献调研、假设生成、代码编写、实验执行、论文撰写等科研全流程，由 Ideation、Planning、Experiment、Writing 四个智能体模块构成。
> 
> **说明**：以上内容均来自搜索工具返回的候选来源信息（标题、URL、摘要片段），并非已验证证据，我未阅读这些网页的正文内容。如需进一步核实，建议直接访问对应链接查看原文。

预设越界短语命中：`[]`。模型保持了“搜索结果/候选来源/摘要片段”语义，没有声称已经阅读全文。该检查是 smoke 边界检查，不是事实质量评测。

## 9. 耗时与 Token

- Harness：8823.169 ms
- 模型 Turn 1 / Turn 2：[2507.173, 5768.849] ms
- 百度首次调用 / stable-ID 复验：[539.242, 575.384] ms
- stable-ID 复验整体：579.546 ms
- 实验总耗时：9403.805 ms
- Prompt tokens：5004
- Completion tokens：693
- Reasoning tokens：156
- Total tokens：5697
- Harness turns/tool calls：2 / 1

## 10. 数据质量问题

- 本次 5/5 个候选均来自内容发布平台（`baijiahao.baidu.com` × 3、`mp.weixin.qq.com` × 1、`blog.csdn.net` × 1），没有直接命中论文主页、学术数据库或研究机构页面；即使 query 包含“论文”，结果仍明显偏二手内容，不能据此判断论文真实性或学术质量。
- 当前没有学术来源过滤、语言控制、去重后的来源多样性评分或质量排序，也没有记录排名分数；因此无法计算 precision、recall、MAP、NDCG，亦无法解释 provider 的排序依据。
- title/snippet/provider content 只能用于候选筛选，尚未通过 Browser/Reader 获取正文、发布日期、作者、引用信息或内容哈希，URL 可访问性与摘要准确性也未验证。
- 两轮模型 prompt tokens 为 [590, 4414]；工具观察进入上下文后，第二轮 prompt 明显增大。当前记录能看到成本增长，但尚未拆分 ToolDefinition、历史消息和每条搜索结果各自的 token 占用，无法精确定位上下文膨胀来源。
- 搜索结果数量、排名和内容会随百度服务端索引变化，本次结果只是单次 live smoke，不代表稳定质量基线。

## 11. 未覆盖内容与下一步

本实验未实现 Browser、Reader 串联、EvidenceCardBuilder、并行 Tool Call、Router、fallback 或正式 Researcher Workflow。下一步优先实现 Browser，将 SourceRecord URL 转换成可追溯 Artifact；完整 Toolset 验证后再迁移生产工作流。
