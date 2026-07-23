# Prompt 资源

该目录保存生产 Agent 的版本化 Prompt。Prompt 应引用 `novelty_agent_framework.schemas` 中的数据契约，不在路由或 LangGraph 节点中拼接。

- `coordinator/`：初始规划、补充检索和最终汇总；
- `research/`：单个文献调研任务。

当前框架 V0 使用 Demo Agent，因此这些模板尚未接入模型。
