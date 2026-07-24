# 论文查新 Multi-Agent 代码框架详细说明

## 1. 框架定位

本项目是论文查新任务的 Multi-Agent 后端框架。它不直接绑定某个大模型、数据库或检索平台，而是先定义稳定的协作流程、数据契约和能力接口。

核心目标是把论文查新拆成三个阶段：

```text
全局规划 → 并行文献调研 → 证据校验与查新报告生成
```

当前实现使用确定性的 Demo Agent 跑通闭环。真实业务中，可以在不重写工作流的前提下，把 Demo Agent 替换为真实 LLM、RAG、学术搜索、全文解析和元数据查证工具。

## 2. 根目录设置逻辑

| 目录或文件 | 存放内容 | 作用 |
|---|---|---|
| `backend/` | 后端工程主体 | 存放正式源码、配置、Prompt 和后端说明 |
| `backend/src/novelty_agent_framework/` | Python 包源码 | Multi-Agent 框架的核心代码 |
| `frontend/` | 前端预留目录 | 后续扩展 Web 界面时使用 |
| `docs/` | 设计文档和代码说明 | 用于汇报、交接和开发参考 |
| `examples/` | 示例输入 | 用于 CLI demo、测试和讲解 |
| `tests/` | 自动化测试 | 验证工作流和 API 行为 |
| `assets/` | 图片资源 | 存放流程图等静态资源 |
| `output/` | 运行输出目录 | 本地 demo 输出结果，默认不提交 |
| `README.md` | 项目首页说明 | 面向仓库访问者的快速介绍 |
| `pyproject.toml` | Python 项目配置 | 定义依赖、包路径、测试配置和命令行入口 |

## 3. 后端包目录设置逻辑

核心源码位于：

```text
backend/src/novelty_agent_framework/
```

| 目录 | 存放文件 | 作用 |
|---|---|---|
| `agents/` | `demo.py`、`evidence_validator.py` | 存放具体 Agent 或可替换智能能力实现 |
| `adapters/` | `workflow_factory.py` | 装配 Agent、工具和 Workflow |
| `config/` | `settings.py`、`settings.example.json` | 管理 API 前缀、端口、CORS 等配置 |
| `core/` | `errors.py` | 存放核心异常和基础公共能力 |
| `data/` | `.gitignore` | 后端运行数据目录占位 |
| `models/` | `schemas.py`、`api.py` | 定义业务数据结构和 API 响应模型 |
| `ports/` | `interfaces.py` | 定义可替换能力接口 |
| `prompts/` | `coordinator/`、`research/` | 存放未来真实 Agent 的 Prompt 模板 |
| `routers/` | `health.py`、`runs.py` | FastAPI 路由入口 |
| `services/` | `workflow_service.py`、`jobs.py` | 管理任务生命周期和运行状态 |
| `web/` | `__init__.py` | Web 相关兼容出口 |
| `workflows/` | `novelty.py`、`state.py` | 定义 LangGraph 工作流和共享状态 |

## 4. Python 文件功能、输入输出与系统作用

### 4.1 包入口

| 文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `__init__.py` | 提供包级轻量出口 | 无直接输入 | 导出 `PaperInput` | 让外部可以快速引用基础输入模型，避免导入包时强制加载 LangGraph |
| `main.py` | 创建 FastAPI 应用 | `NoveltyWebSettings` 或环境变量 | `FastAPI` 实例 | API 服务入口，挂载健康检查和任务接口 |
| `cli.py` | 命令行 demo 入口 | 示例论文 JSON 路径、输出路径 | 查新结果 JSON | 用于本地验证完整查新流程 |

### 4.2 `models/`

| 文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `models/schemas.py` | 定义查新工作流核心数据模型 | 论文、查新点、调研任务、证据卡、报告字段 | Pydantic 模型 | 约束 Agent 之间传递的数据格式，避免输出漂移 |
| `models/api.py` | 定义 API 健康检查响应 | 服务名、版本、状态 | `HealthResponse` | 让 API 返回稳定健康检查结构 |
| `models/__init__.py` | 聚合导出模型 | 无直接输入 | `PaperInput`、`EvidenceCard`、`NoveltyReport` 等 | 统一模型导入路径 |

主要数据流：

```text
PaperInput
→ NoveltyBrief
→ ResearchTask
→ EvidenceCard
→ NoveltyReport
→ NoveltyRunResult
```

### 4.3 `ports/`

| 文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `ports/interfaces.py` | 定义能力接口协议 | 论文、检索 query、文献 ID、证据卡 | `NoveltyBrief`、`EvidenceCard`、`ValidationResult` 等 | 把工作流和具体模型、数据库、工具解耦 |
| `ports/__init__.py` | 聚合导出接口 | 无直接输入 | `NoveltyCoordinator`、`LiteratureResearchAgent` 等 | 给实现方提供统一接口引用 |

关键接口：

| 接口 | 输入 | 输出 | 作用 |
|---|---|---|---|
| `NoveltyCoordinator.plan` | `PaperInput`、已有证据、证据缺口、轮次 | `NoveltyBrief` | 生成查新点和调研任务 |
| `NoveltyCoordinator.plan_supplement` | 论文、当前 brief、已有证据、缺口 | `NoveltyBrief` | 为证据不足的查新点补充任务 |
| `NoveltyCoordinator.synthesize` | 论文、brief、有效证据、被拒证据、缺口 | `NoveltyReport` | 汇总最终查新报告 |
| `LiteratureResearchAgent.research` | `ResearchTask`、论文、检索工具 | `EvidenceCard` 列表 | 执行单个文献调研任务 |
| `SearchTool.search` | query、limit | `SearchHit` 列表 | 检索候选文献 |
| `FullTextTool.fetch` | document_id | `FullText` 或 `None` | 获取摘要或全文 |
| `MetadataTool.resolve` | document_id | `EvidenceSource` 或 `None` | 校验 DOI、URL、引用来源 |
| `EvidenceValidator.validate` | 候选证据卡、任务列表 | `ValidationResult` | 过滤低质量或不可追溯证据 |

### 4.4 `agents/`

| 文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `agents/demo.py` | 提供确定性 Demo Agent | `PaperInput`、`ResearchTask`、证据列表 | `NoveltyBrief`、`EvidenceCard`、`NoveltyReport` | 在没有真实 LLM 和数据库时跑通框架 |
| `agents/evidence_validator.py` | 证据质量门控 | 候选 `EvidenceCard`、`ResearchTask` | `ValidationResult` | 拒绝无来源、低相关性、低置信度、重复或任务不匹配的证据 |
| `agents/__init__.py` | 聚合导出 Agent | 无直接输入 | Demo Agent 和验证器类 | 统一 Agent 导入路径 |

`DemoCoordinator` 负责模拟查新主 Agent：理解论文、生成查新点、规划补充检索、生成报告。  
`DemoResearchAgent` 负责模拟文献调研子 Agent：根据任务返回合成证据卡。  
`DefaultEvidenceValidator` 负责把模型生成内容变成可审计证据，而不是让模型结论直接进入报告。

### 4.5 `workflows/`

| 文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `workflows/state.py` | 定义共享状态、配置和依赖容器 | Agent、工具、工作流参数 | `NoveltyState`、`NoveltyWorkflowConfig`、`NoveltyWorkflowServices` | 规定各节点共享哪些字段、注入哪些能力 |
| `workflows/novelty.py` | 定义 LangGraph 查新流程 | `PaperInput` 或 dict | `NoveltyRunResult` | 系统核心编排层，控制规划、并行调研、验证、补检和汇总 |
| `workflows/__init__.py` | 聚合导出工作流 | 无直接输入 | `NoveltyWorkflow` 等 | 统一工作流导入路径 |

`NoveltyWorkflow` 的节点逻辑：

```text
plan
→ parallel_research
→ validate_evidence
→ assess_coverage
→ plan_supplement 或 synthesize_report
```

重要输入输出：

| 方法 | 输入 | 输出 | 作用 |
|---|---|---|---|
| `arun` | `PaperInput` 或 dict | `NoveltyRunResult` | 异步执行完整工作流 |
| `run` | `PaperInput` 或 dict | `NoveltyRunResult` | 同步执行完整工作流 |
| `_plan` | `NoveltyState` | brief 和 research tasks | 生成初始查新计划 |
| `_parallel_research` | research tasks | raw evidence cards 和 issues | 并行执行文献调研 |
| `_validate_evidence` | raw evidence cards | accepted/rejected evidence | 进行证据门控 |
| `_assess_coverage` | brief 和有效证据 | coverage gaps | 判断每个查新点证据是否足够 |
| `_plan_supplement` | coverage gaps | 补充 research tasks | 针对缺口追加检索 |
| `_synthesize_report` | 全部有效证据和缺口 | `NoveltyReport` | 形成最终查新结论 |

### 4.6 `adapters/`

| 文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `adapters/workflow_factory.py` | 装配工作流依赖 | 无直接业务输入 | `NoveltyWorkflow` | 决定当前使用 Demo 实现还是真实实现 |
| `adapters/__init__.py` | 导出 factory | 无直接输入 | `build_novelty_workflow` | 给 service 层提供统一构造入口 |

当前 `build_novelty_workflow` 装配的是 `DemoCoordinator` 和 `DemoResearchAgent`。生产环境应在这里替换为真实 LLM Agent、搜索工具、全文工具和元数据工具。

### 4.7 `services/`

| 文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `services/workflow_service.py` | 管理一次查新任务的创建、执行和查询 | `PaperInput`、task_id | `RunSnapshot` | 连接 API 层和 Workflow 层 |
| `services/jobs.py` | 进程内任务存储 | task_id、任务结果、错误信息 | `RunSnapshot` | 保存任务状态，支持前端轮询 |
| `services/__init__.py` | 聚合导出服务 | 无直接输入 | `NoveltyWorkflowService` | 统一服务导入路径 |

任务状态流转：

```text
queued → running → succeeded / failed
```

当前使用 `InMemoryRunStore`，只适合开发和 demo。生产环境应替换为 Redis、数据库或任务队列。

### 4.8 `routers/`

| 文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `routers/health.py` | 健康检查接口 | HTTP GET 请求 | `HealthResponse` | 验证 API 服务是否可用 |
| `routers/runs.py` | 查新任务接口 | `PaperInput`、task_id | `RunSnapshot` | 提交任务、查询任务状态和结果 |
| `routers/__init__.py` | 聚合导出路由 | 无直接输入 | `health_router`、`runs_router` | 给 `main.py` 统一挂载路由 |

API 路径：

```text
GET  /api/novelty/health
POST /api/novelty/runs
GET  /api/novelty/runs/{task_id}
```

### 4.9 `config/`

| 文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `config/settings.py` | 读取 Web 配置 | 环境变量 | `NoveltyWebSettings` | 控制应用名、host、port、API 前缀、CORS |
| `config/settings.example.json` | 示例配置 | 无 | JSON 示例 | 给部署和联调提供参考 |
| `config/__init__.py` | 聚合导出配置 | 无直接输入 | `NoveltyWebSettings` | 统一配置导入路径 |

### 4.10 `core/`、`web/`、`prompts/`、`data/`

| 目录或文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `core/errors.py` | 定义 `WorkflowExecutionError` | 错误消息 | 工作流异常 | 区分框架级失败和普通 Python 异常 |
| `web/__init__.py` | Web 兼容出口 | 无直接输入 | 任务状态相关类 | 保留旧导入兼容，后续可弱化 |
| `prompts/README.md` | Prompt 管理说明 | 无 | 文档 | 约束 Prompt 不散落在代码里 |
| `prompts/coordinator/*.md` | Coordinator Prompt 占位 | 论文和证据上下文 | 查新计划、补检计划、报告 | 后续接真实主 Agent |
| `prompts/research/*.md` | Research Agent Prompt 占位 | 调研任务和论文内容 | Evidence Card | 后续接真实文献调研 Agent |
| `data/.gitignore` | 数据目录占位 | 本地数据文件 | 不提交运行数据 | 为缓存、索引、临时文件预留空间 |

## 5. 系统调用关系

```text
HTTP 请求
→ routers/runs.py
→ services/workflow_service.py
→ adapters/workflow_factory.py
→ workflows/novelty.py
→ agents/demo.py 或真实 Agent
→ ports/interfaces.py 约束外部能力
→ models/schemas.py 约束输入输出
```

CLI 调用关系：

```text
examples/paper.json
→ cli.py
→ NoveltyWorkflow
→ NoveltyRunResult
→ output/result.json
```

## 6. 开发规范

1. 新业务数据结构必须先写入 `models/`，不要在 Agent 或路由里临时拼 dict。
2. 新外部能力必须先在 `ports/` 定义接口，再在 `adapters/` 或 `agents/` 中实现。
3. `workflows/` 只负责流程编排，不直接写具体模型 SDK、数据库连接或复杂 Prompt。
4. `agents/` 负责专业判断和结构化输出，不处理 HTTP 请求和任务状态。
5. `routers/` 只做请求校验、依赖注入和响应返回，不写业务流程。
6. `services/` 负责任务生命周期，不直接实现查新逻辑。
7. `adapters/` 负责装配真实能力，是替换 Demo 实现的主要入口。
8. Prompt 放在 `prompts/`，需要版本化、可追踪，不要散落到多个 Python 文件中。
9. 所有 Agent 输出必须经过 Pydantic 模型校验，不能让自由文本直接进入后续流程。
10. 证据型结论必须保留来源、位置、URL 或 DOI，不能只依赖模型判断。
11. 本地运行输出、缓存、索引和 `.egg-info` 不提交到 Git。
12. 中文文档和源码统一使用 UTF-8 编码。
13. 新增功能要补充最小测试，至少覆盖正常路径和一个失败/降级路径。
14. 生产环境密钥必须通过环境变量或安全配置注入，禁止写入仓库。

## 7. 后续扩展建议

优先替换以下位置：

```text
adapters/workflow_factory.py
```

把当前 Demo 实现替换为：

```text
真实 Coordinator Agent
真实 Literature Research Agent
真实 SearchTool
真实 FullTextTool
真实 MetadataTool
生产级任务存储
```

只要这些实现遵守 `ports/` 中的接口，`workflows/` 和 `models/` 通常不需要重写。
