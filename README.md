# 论文查新 Multi-Agent 框架

这是一个基于 LangGraph 的论文查新后端原型。系统将论文解析、查新点提取、检索规划、数据库查询编译、候选文献召回、证据分析、质量门控、补检和报告生成拆成职责独立的组件，并保留每一阶段的可审计产物。

当前版本已经使用真实 PDF、SiliconFlow 模型和 arXiv 完成两轮端到端实验。它是可运行的研究原型，不是可以直接替代人工科技查新的生产系统。

## 当前工作流

```text
PaperInput
  ↓
PointExtractor                     从论文提取“查什么”
  ↓
Coordinator.plan                   把查新点拆成中英文 ResearchTask
  ↓
SearchPlanner                      生成数据库无关 SearchPlan
  ↓
QueryAdapter                       编译为具体数据库语法
  ↓
SearchTool                         执行真实检索并返回 SearchHit
  ↓
Researcher                         逐篇阅读候选并生成 EvidenceCard
  ↓
EvidenceValidator                  证据质量门控与去重
  ↓
Coverage Assessment
  ├─ 证据不足 → Coordinator.plan_supplement → 重新经过完整检索链
  └─ 达到轮次上限或覆盖充分
  ↓
Coordinator.synthesize             生成结构化 NoveltyReport
  ↓
Renderer                           生成 Markdown 报告
```

LangGraph 节点：

```text
START
→ extract_points
→ plan
→ plan_search
→ retrieve_candidates
→ parallel_research
→ validate_evidence
→ assess_coverage
  ├─ plan_supplement → plan_search → ...
  └─ synthesize_report → render_report
→ END
```

## 关键架构边界

- Coordinator 只负责任务拆分、补检规划和全局汇总，不生成数据库查询；
- SearchPlanner 只生成 Concept、term 和布尔策略，不包含 `all:` 等数据库语法；
- QueryAdapter 是无 LLM、无网络副作用的确定性编译器；
- SearchTool 只执行已经编译的查询；
- Researcher 不再检索，只分析上游传入的 `NoveltyPoint + SearchHit[]`；
- Workflow 负责串联、由紧到松执行查询、候选去重、补检和终止控制；
- Task 的工作流身份是 `(novelty_point_id, task_id)`，因为 `task_id` 只在单个查新点内唯一。

数据源通过 `RetrievalSourceRegistry` 注册并由 `retrieval.active_source` 选择，Workflow、Agent 与领域 Schema 不包含数据库分支。

生产/实验数据源：

- arXiv

测试数据源：

- `null_catalog`（离线 Null Object，永远返回空结果）

`null_catalog` 只验证数据源注册、配置选择、QueryAdapter/SearchTool 替换和空结果处理；它不模拟真实文献数据库，不验证 FullTextTool、MetadataTool 的跨来源兼容性，也不用于正式查新。用户自制本地数据库导入仍是 `experiments/` 下未实现、未接入工作流的探索功能。

## 项目结构

```text
backend/env/                              统一模型客户端、模型注册表和 PromptLibrary
backend/src/novelty_agent_framework/
├── agents/                              Coordinator、PointExtractor、SearchPlanner、Researcher、Validator、Demo
├── config/                              配置加载和真实工作流组合根
├── ports/                               可替换能力接口
├── processing/                          PDF 文本层解析、OCR 兜底、章节与标题提取
├── prompts/                             版本化 Agent 提示词
├── schemas/                             Pydantic 数据契约
├── tools/                               Adapter、arXiv 工具、Renderer 等
├── workflows/                           LangGraph 状态和主工作流
├── persistence.py                       按 paper 隔离的本地产物持久化
└── main.py                              FastAPI 入口
docs/                                    架构、进度和实验记录
examples/                                示例论文和 JSON 输入
outputs/                                 本地运行产物，具体生成文件不提交
tests/                                   离线与 live 测试
```

## Paper 工作目录

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
└── report/<paper_id>-report.md
```

真实实验还可额外写出 `run-metrics.json`，记录墙钟时间和逐次模型 usage。

`retrieval-plans.json` 按查新点保存 `research_tasks`、数据库无关 `search_plans`、真正执行的 `executed_queries`，以及供现有 Renderer 使用的 `query_plan.queries`。

## 环境和安装

项目使用已经创建的 `Novelty` Conda 环境：

```bash
conda activate Novelty
pip install -e ".[dev,web]"
```

真实模型调用使用 `backend/.env` 或进程环境变量：

```dotenv
SILICONFLOW_API_KEY=...
```

`backend/.env` 已被 Git 忽略。不要把真实 Key 写入 `.env.example`、代码、文档或提交历史。

## 运行方式

### 离线 Demo

离线 Demo 会经过 SearchPlanner、Adapter、SearchTool 和 Researcher 的完整数据流，但使用确定性实现，不访问网络：

```bash
novelty-demo --input examples/paper.json --output /tmp/novelty-result.json
```

### PDF 处理

```bash
python -m novelty_agent_framework.processing.cli \
  --input examples/MF2033k6lC.pdf \
  --output outputs
```

### 配置驱动的真实工作流

```python
from novelty_agent_framework.config import build_workflow, load_config
from novelty_agent_framework.schemas import PaperInput

config = load_config()
config["retrieval"]["sources"]["arxiv"]["enabled"] = True
workflow = build_workflow(config)
result = workflow.run(PaperInput.model_validate(paper_data))
```

当前示例配置中的 `Pro/zai-org/GLM-4.7` 在第一次原型实验时被 SiliconFlow 返回 `Model disabled`。真实运行前应把 Coordinator 配置为当前可用模型；实验使用 `deepseek-flash` 临时替代。

### Renderer 与 API

```python
from novelty_agent_framework.tools import render_report

path = render_report(output_format="markdown", paper_name="paper-id")
```

```bash
python -m novelty_agent_framework.main
```

## 测试状态

当前共收集 166 个测试，其中 6 个是默认跳过的 live 测试。

- 54 个 Workflow、Factory、Adapter、SearchPlanner、Researcher、Persistence 和 Renderer 核心测试通过；
- 78 个 Agent、模型客户端、Prompt、arXiv 工具、PointExtractor 和旧 retrieval 辅助测试通过；
- 26 个 PDF/OCR、章节、文本层和标题处理测试通过；
- 已确认 158 个非 live 测试通过；
- `pytest --collect-only` 正常；
- 全量运行仍会在 `tests/test_api.py` 的首个 TestClient 生命周期测试处挂起，需要单独修复。

```bash
pytest
pytest -m live tests/test_live_arxiv_tools.py -s
```

## 第一次真实原型实验

`examples/MF2033k6lC.pdf` 已完成一次成功的两轮真实流程：

| 指标 | 结果 |
| --- | ---: |
| 总耗时 | 1,076.034 秒（约 17 分 56 秒） |
| 模型调用 | 19 次 |
| 输入 / 输出 / 总 Token | 145,566 / 93,509 / 239,075 |
| 理论模型费用 | 约 ¥0.33 |
| 原始 / 接受 / 拒绝证据 | 11 / 6 / 5 |
| 最终覆盖 | NP-1 partial；NP-2、NP-3 insufficient |

详细记录见：[第一次原型机实验测试结果](docs/issues/第一次原型机实验测试结果.md)。

## 当前限制

- 只有 arXiv，中文文献覆盖不足；
- SearchPlanner 偶尔输出非法 Strategy ID，重试一次仍可能失败；
- Agent 内部使用同步模型 HTTP 调用，异步节点实际接近串行；
- Coordinator 补检和汇总上下文过大，是主要输入 Token 来源；
- V4-Flash reasoning token 较高；
- 默认 Coordinator 模型当前不可用；
- 第二轮 EvidenceValidator issue 会重复累计；
- FastAPI TestClient 生命周期测试仍会挂起；
- 本地 JSON 和进程内任务存储仍是原型实现。

## 文档

- [代码框架说明](docs/code-framework.md)
- [代码框架详细说明](docs/code-framework-detailed.md)
- [框架演进总结](docs/框架演进总结.md)
- [开发进度](docs/开发进度.md)
- [第一次原型机实验测试结果](docs/issues/第一次原型机实验测试结果.md)
