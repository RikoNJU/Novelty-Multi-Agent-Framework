# 论文查新 Multi-Agent 框架

本项目是一个面向论文查新任务的 Multi-Agent 后端代码框架，使用 LangGraph 实现“全局规划—并行文献调研—证据校验—报告生成”的总分总流程。

## Multi-Agent 设计简介

Multi-Agent 不是简单顺序调用多个 Prompt，而是把复杂任务拆给多个职责明确的智能体，并设计它们之间的信息共享、任务协作、结果验证和失败恢复机制。

在论文查新任务中，单一模型容易把“论文理解、检索规划、文献对比、证据判断、结论汇总”混在一起，导致输出难追溯、难验证。该框架将任务拆为：

```text
Coordinator 负责全局规划和最终汇总
Research Agent 负责并行文献调研
Evidence Validator 负责证据质量门控
Workflow 负责调度、补检和终止控制
```

这样的设计可以让查新结论基于可追溯证据，而不是只依赖模型的自由判断。

![论文查新流程](assets/workflow.svg)

## 代码框架简介

框架采用后端工程结构：

```text
backend/src/novelty_agent_framework/
```

包内按职责拆分为 Agent、Workflow、Schema、Port、Service、Router 等目录。核心思想是：

- `schemas/` 定义数据长什么样；
- `ports/` 定义系统需要什么能力；
- `agents/` 放具体 Agent 实现；
- `backend/env/` 统一模型配置、消息格式和调用入口；
- `workflows/` 编排 Multi-Agent 协作流程，并提供默认工作流装配入口；
- `services/` 管理任务生命周期；
- `routers/` 提供 API 入口。

这种结构可以让后续开发者在不重写整体流程的前提下，逐步替换真实 LLM、学术检索工具、全文解析工具和元数据查证工具。

## 项目结构

```text
backend/src/novelty_agent_framework/   后端源码，按职责拆分 Agent、模型、工作流、接口和服务
frontend/                              预留前端资源
examples/                      示例论文输入
tests/                         工作流与接口测试
docs/                          设计方案和代码说明
assets/                        流程图
outputs/                       按 paper 隔离的本地运行产物（默认不提交）
```

每篇论文使用独立工作目录：

```text
outputs/<paper_id>/
├── paper-input/
│   ├── full.md
│   ├── content-list.json
│   ├── images/
│   └── others/paper.json
├── novelty-points.json
├── retrieval-plans.json
├── evidence-cards.json
├── report.json
└── report/
    └── <paper_id>-report.md
```

`retrieval-plans.json` 按查新点序号分组，每组同时保留 ResearchTask 和汇总后的 QueryPlan。`report.json` 保存 Coordinator 的结构化汇总输出；工作流末尾的确定性 Renderer 默认使用 `templates/markdown/default.md` 生成 Markdown 报告。后续可继续注册 LaTeX、HTML Renderer。

也可以独立调用 Renderer：

```python
from novelty_agent_framework.tools import render_report

path = render_report(output_format="markdown", paper_name="paper-id")
```

## 运行

```powershell
conda activate langgraph
cd D:\novelty-multi-agent-framework
pip install -e ".[dev,web]"
pytest
novelty-demo --input examples\paper.json --output output\result.json
```

可选接口启动命令：

```powershell
python -m novelty_agent_framework.main
```

- [代码框架说明](docs/code-framework.md)
- [代码框架详细说明](docs/code-framework-detailed.md)
- [V0 设计方案](docs/design-v0.md)

当前默认工作流装配确定性的 Demo Agent，只用于验证框架闭环。
