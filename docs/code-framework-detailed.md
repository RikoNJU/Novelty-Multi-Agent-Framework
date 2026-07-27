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
| `backend/env/` | 模型调用约定说明 | 约束多人开发时统一模型配置和调用方式 |
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
| `agents/` | `coordinator.py`、`research.py`、`demo.py`、`evidence_validator.py` | 存放具体 Agent 或可替换智能能力实现 |
| `config/` | `settings.py`、`settings.example.json` | 管理 API 前缀、端口、CORS 等配置 |
| `core/` | `errors.py` | 存放核心异常和基础公共能力 |
| `data/` | `.gitignore` | 后端运行数据目录占位 |
| `models/` | `schemas.py`、`api.py` | 定义业务数据结构和 API 响应模型 |
| `ports/` | `interfaces.py` | 定义可替换能力接口 |
| `prompts/` | `coordinator/`、`research/` | 存放未来真实 Agent 的 Prompt 模板 |
| `routers/` | `health.py`、`runs.py` | FastAPI 路由入口 |
| `services/` | `workflow_service.py`、`jobs.py` | 管理任务生命周期和运行状态 |
| `web/` | `__init__.py` | Web 相关兼容出口 |
| `workflows/` | `novelty.py`、`state.py` | 定义 LangGraph 工作流、共享状态和固定 Agent 装配 |

### 3.1 目录内容说明

#### `agents/`

该目录存放“真正执行某类智能任务或规则判断”的模块。当前包含真实实现骨架、确定性 Demo 和证据质量门控。

未来真实系统中，论文理解、查新点拆解、补检规划、文献调研和证据对比等 Agent 实现都应放在这里。它们可以调用 LLM、RAG 或外部工具，但对外必须返回 `models/` 中定义的结构化对象。

该目录不应该处理 HTTP 请求，不应该管理任务状态，也不应该决定整体调用顺序。它只回答“某个 Agent 如何完成自己的专业任务”。

#### `config/`

该目录存放后端运行配置。当前 `settings.py` 从环境变量读取应用名、host、port、API 前缀和 CORS；`settings.example.json` 提供示例配置。

未来模型服务地址、检索服务地址、数据库连接信息、日志级别、超时参数、最大并发数等运行参数，都应优先放在配置层，而不是硬编码到 Agent、Router 或 Workflow 中。

该目录不应该保存真实密钥。API Key、数据库密码、Token 等敏感信息应通过环境变量或安全配置系统注入。

#### `core/`

该目录存放框架级公共能力。当前只有 `WorkflowExecutionError`，用于表示工作流执行过程中的框架级失败。

未来如果出现多个目录都要复用的异常类型、日志上下文、运行 ID、通用枚举、基础工具函数，可以放在这里。但只有“全局基础能力”适合进入 `core/`。

具体查新业务逻辑不应放入 `core/`。如果某段代码只服务于证据校验，应放在 `agents/`；如果只服务于任务状态，应放在 `services/`。

#### `data/`

该目录是后端运行数据的占位目录。当前只保留 `.gitignore`，表示目录存在，但默认不提交运行时数据。

未来可临时存放本地缓存、小规模 demo 数据、调试索引、下载的候选文献片段等。生产环境中的向量索引、数据库文件、批量运行结果一般不应提交到 Git。

该目录不应存放源码、Prompt 或正式配置。它主要服务于运行时和调试。

#### `models/`

该目录存放系统最重要的数据结构和校验规则。当前 `schemas.py` 定义论文输入、查新点、调研任务、Evidence Card、查新报告和运行结果；`api.py` 定义健康检查响应；`__init__.py` 统一导出常用模型。

Agent 之间传递的数据必须优先在这里建模。例如新增“引用查证结果”“文献相似度结果”“检索覆盖度报告”，都应先定义 Pydantic 模型，再进入 Workflow 或 Agent。

该目录不应该调用模型接口、数据库或外部服务。它只定义“数据长什么样、哪些字段必须存在、哪些字段不允许乱填”。

#### `ports/`

该目录存放能力接口协议。当前 `interfaces.py` 定义了 `NoveltyCoordinator`、`LiteratureResearchAgent`、`SearchTool`、`FullTextTool`、`MetadataTool` 和 `EvidenceValidator`。

Port 的作用是让 Workflow 只依赖抽象能力，不依赖具体实现。比如 Workflow 只知道需要一个 `SearchTool.search()`，但不关心背后是 Semantic Scholar、Google Scholar、Crossref、学校数据库还是本地索引。

该目录不应该写真实 API 调用代码。真实实现应放在 `agents/`，固定 Agent 装配应放在 `workflows/novelty.py` 的默认构造函数中，并遵守这里定义的输入输出协议。

#### `backend/env/`

该目录位于 `backend/env/`，不放在 `backend/src/novelty_agent_framework/` 内部。当前 `model_client.py` 定义 `ModelRuntimeConfig`、`ChatMessage`、`ModelCallOptions`、`ModelResponse` 和 `OpenAICompatibleChatClient`，用于规范真实 Agent 调用大模型时的配置读取、消息格式、超时参数和响应结构。

多人开发时，Agent 不应各自读取 API Key、拼接 HTTP 请求或自定义返回结构，而应优先通过 `build_model_client()` 获取模型客户端。这样可以保证同一项目内不同 Agent 使用一致的模型供应商、模型名、base_url、温度和超时规则。

该目录不应该放 Prompt、不应该写论文查新业务判断，也不应该保存真实密钥。业务 Prompt 仍放在 `prompts/`，专业判断仍放在 `agents/`，密钥通过环境变量或安全配置注入。

#### `prompts/`

该目录存放 Prompt 模板和 Prompt 管理说明。当前按照 `coordinator/` 和 `research/` 拆分，分别对应主 Agent 和文献调研 Agent。

未来真实 Agent 的系统提示词、任务提示词、输出 JSON 约束、失败重试提示词、补充检索提示词，都应集中放在这里，便于版本管理、评审和调参。

该目录不应该保存业务运行结果，也不应该把 Prompt 分散写进 `routers/` 或 `workflows/`。这样做可以避免后期难以追踪“某次输出变化到底来自代码还是 Prompt”。

#### `routers/`

该目录存放 FastAPI 路由。当前 `health.py` 提供健康检查接口，`runs.py` 提供查新任务提交和查询接口。

Router 的职责是处理 HTTP 层问题，例如请求体校验、依赖注入、状态码、错误响应和返回模型。它把外部请求转交给 `services/`，不直接调 Agent。

该目录不应该写 Multi-Agent 调度逻辑，不应该直接访问模型 SDK，也不应该直接操作底层存储。否则 API 层会和业务流程耦合。

#### `services/`

该目录存放应用服务和任务生命周期管理。当前 `workflow_service.py` 负责创建任务、调用 Workflow、记录成功或失败；`jobs.py` 提供进程内任务状态存储。

Service 是 Router 和 Workflow 之间的中间层。它知道“某个请求对应哪个任务、任务现在是什么状态、结果在哪里”，但不关心每个 Agent 内部如何推理。

当前 `InMemoryRunStore` 只适合 demo 和单进程开发。未来如果系统上线，应在该层替换为 Redis、数据库、消息队列或后台任务系统。

#### `web/`

该目录当前只保留 Web 相关兼容出口，用于导出任务状态相关类，减少旧代码迁移时的导入断裂。

随着框架稳定，新的 Web 任务管理逻辑应优先放入 `services/` 和 `routers/`。`web/` 不应继续膨胀成另一个业务层。

如果未来确认没有兼容需求，可以逐步移除该目录，或只保留非常薄的对外导出。

#### `workflows/`

该目录存放 Multi-Agent 协作流程。当前 `novelty.py` 定义 LangGraph 节点、路由和默认 Agent 装配方式，`state.py` 定义共享状态、配置和依赖容器。

Workflow 负责回答“Agent 之间如何协作”：先由 Coordinator 规划，再并行调用 Research Agent，随后进行证据校验和覆盖度判断，必要时补充检索，最后生成报告。

该目录不应该直接写具体模型调用、数据库查询或长 Prompt。它应依赖 `ports/` 中的抽象接口，并使用 `models/` 中的数据结构来保证流程稳定。

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
| `agents/coordinator.py` | 查新主 Agent | `PaperInput`、已有证据、证据缺口、轮次 | `NoveltyBrief`、`NoveltyReport` | 组织论文理解、查新点拆解、补检规划、模型 JSON 调用和 Pydantic 输出校验 |
| `agents/research.py` | 文献调研 Agent 骨架 | `ResearchTask`、`PaperInput`、检索/全文/元数据工具 | `EvidenceCard` 列表 | 后续实现检索、阅读、重合点和差异点抽取 |
| `agents/demo.py` | 提供确定性 Demo Agent | `PaperInput`、`ResearchTask`、证据列表 | `NoveltyBrief`、`EvidenceCard`、`NoveltyReport` | 在没有真实 LLM 和数据库时跑通框架 |
| `agents/evidence_validator.py` | 证据质量门控 | 候选 `EvidenceCard`、`ResearchTask` | `ValidationResult` | 拒绝无来源、低相关性、低置信度、重复或任务不匹配的证据 |
| `agents/__init__.py` | 聚合导出 Agent | 无直接输入 | 真实 Agent 骨架、Demo Agent 和验证器类 | 统一 Agent 导入路径 |

`DemoCoordinator` 负责模拟查新主 Agent：理解论文、生成查新点、规划补充检索、生成报告。  
`DemoResearchAgent` 负责模拟文献调研子 Agent：根据任务返回合成证据卡。  
`DefaultEvidenceValidator` 负责把模型生成内容变成可审计证据，而不是让模型结论直接进入报告。

`NoveltyCoordinatorAgent` 是后续接真实模型时的主 Agent 入口。它已经预留 `plan`、`plan_supplement` 和 `synthesize` 三个核心方法，并统一通过 `backend/env/model_client.py` 调用模型。每次模型返回后都会进行 JSON 解析和 Pydantic 校验，防止自由文本直接进入工作流。

### 4.5 `backend/env/`

| 文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `backend/env/model_client.py` | 统一模型调用协议和 OpenAI-compatible 客户端 | 环境变量、`ChatMessage` 列表、调用参数 | `ModelResponse` | 让不同 Agent 使用一致的模型配置和调用方式 |
| `backend/env/__init__.py` | 聚合导出模型调用对象 | 无直接输入 | `ModelRuntimeConfig`、`build_model_client` 等 | 给真实 Agent 提供统一导入路径 |

模型配置优先读取 `NOVELTY_*`，并回退到通用 `LLM_*`。例如 `NOVELTY_MODEL`、`NOVELTY_BASE_URL`、`NOVELTY_API_KEY`、`NOVELTY_TEMPERATURE` 和 `NOVELTY_TIMEOUT_SECONDS`。

### 4.6 `workflows/`

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

### 4.7 `workflows/novelty.py` 中的默认装配

| 文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `workflows/novelty.py` | 编排查新流程并装配默认工作流依赖 | 无直接业务输入 | `NoveltyWorkflow` | 指定当前固定使用的 Agent，并给 service 层提供统一构造入口 |

当前 `NoveltyWorkflow.default()` 位于 `novelty.py`，装配的是 `DemoCoordinator` 和 `DemoResearchAgent`。因为本项目假设 Agent 组合相对固定，所以默认装配逻辑直接并入主工作流类，不再单独保留独立装配文件。

### 4.8 `services/`

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

### 4.9 `routers/`

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

### 4.10 `config/`

| 文件 | 功能 | 输入 | 输出 | 系统作用 |
|---|---|---|---|---|
| `config/settings.py` | 读取 Web 配置 | 环境变量 | `NoveltyWebSettings` | 控制应用名、host、port、API 前缀、CORS |
| `config/settings.example.json` | 示例配置 | 无 | JSON 示例 | 给部署和联调提供参考 |
| `config/__init__.py` | 聚合导出配置 | 无直接输入 | `NoveltyWebSettings` | 统一配置导入路径 |

### 4.11 `core/`、`web/`、`prompts/`、`data/`

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
→ workflows/novelty.py
→ agents/demo.py 或真实 Agent
→ backend/env/model_client.py 统一真实模型调用
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
2. 新外部能力必须先在 `ports/` 定义接口，再在 `agents/` 中实现，并在 `workflows/novelty.py` 中装配。
3. `workflows/` 只负责流程编排，不直接写具体模型 SDK、数据库连接或复杂 Prompt。
4. `agents/` 负责专业判断和结构化输出，不处理 HTTP 请求和任务状态。
5. `routers/` 只做请求校验、依赖注入和响应返回，不写业务流程。
6. `services/` 负责任务生命周期，不直接实现查新逻辑。
7. `workflows/novelty.py` 同时负责固定 Agent 组合装配和流程编排，调整默认运行能力时应修改其中的 `NoveltyWorkflow.default()`。
8. Prompt 放在 `prompts/`，需要版本化、可追踪，不要散落到多个 Python 文件中。
9. 真实 Agent 调用模型时统一使用 `backend/env/model_client.py`，不要在 Agent 内部重复拼接模型 HTTP 请求。
10. 所有 Agent 输出必须经过 Pydantic 模型校验，不能让自由文本直接进入后续流程。
11. 证据型结论必须保留来源、位置、URL 或 DOI，不能只依赖模型判断。
12. 本地运行输出、缓存、索引和 `.egg-info` 不提交到 Git。
13. 中文文档和源码统一使用 UTF-8 编码。
14. 新增功能要补充最小测试，至少覆盖正常路径和一个失败/降级路径。
15. 生产环境密钥必须通过环境变量或安全配置注入，禁止写入仓库。

## 7. 后续扩展建议

优先替换以下位置：

```text
workflows/novelty.py
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
