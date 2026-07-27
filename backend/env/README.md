# env 目录说明

该目录用于约定团队统一的模型调用方式，避免不同开发者在不同 Agent 中各自拼接 API 请求。

实际可导入代码位于 `backend/env/`：

- `model_client.py`：统一模型配置、消息格式、响应格式和 OpenAI-compatible 调用客户端；
- `__init__.py`：导出公共模型调用对象，便于 Agent 统一引用。

新增真实 Agent 时，应优先通过 `build_model_client()` 获取模型客户端，而不是在 Agent 内部直接读取 API Key 或手写 HTTP 请求。
