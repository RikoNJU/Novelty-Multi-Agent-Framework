# Prompt 资源

该目录保存生产 Agent 的版本化 Prompt。Prompt 应引用 `novelty_agent_framework.schemas` 中的数据契约，不在路由或 LangGraph 节点中拼接。

- `coordinator/`：任务分配（plan）、补充检索和最终汇总；
- `extractor/`：查新点提取；
- `reviewer/`：查新点审查（去重/合并/补全）；
- `research/`：单个文献调研任务。

每个模板由 front matter（`name` / `version` / `system`）和正文模板组成，
正文通过 `{变量名}` 占位符接收业务数据，schema 由
`NoveltyBrief.model_json_schema()` 等动态注入，保证与 Pydantic 契约同步。

模板由 `backend.env.PromptLibrary` 加载渲染，真实 Agent
（`NoveltyCoordinatorAgent` / `NoveltyResearchAgent`）在装配时注入
PromptLibrary；文件缺失时回退到 Agent 内的默认提示词。
Demo Agent 不读取本目录，仍用于验证工作流闭环。
