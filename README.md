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
dispatch_research_tasks            按任务动态 fan-out
  ↓
TaskResearcherWorkflow             单任务 Researcher 决定检索、阅读或结束
  ├─ structured_source_retrieval   检索并保存 Work/SourceRecord/Artifact
  └─ reference_artifact_reader     按 Manifest 安全读取原文片段
  ↓
Evidence Compiler                  确定性绑定 quote、Artifact 和字符位置
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
→ dispatch_research_tasks
→ run_research_task                每个 ResearchTask 运行一个 LangGraph 子图
→ validate_evidence
→ assess_coverage
  ├─ plan_supplement → dispatch_research_tasks → ...
  └─ synthesize_report → render_report
→ END
```

## 关键架构边界

- Coordinator 只负责任务拆分、补检规划和全局汇总，不生成数据库查询；
- SearchPlanner 只生成 Concept、term 和布尔策略，不包含 `all:` 等数据库语法；
- QueryAdapter 是无 LLM、无网络副作用的确定性编译器；
- SearchTool 只执行已经编译的查询；
- 每个 Researcher 只接收一个绑定的 `NoveltyPoint + ResearchTask`，通过模型原生
  Tool Calling 调用注册工具，不接收全局任务或最终报告上下文；
- TaskResearcher 子图负责预算、重复调用限制和局部失败隔离，主 Workflow 负责
  fan-out/fan-in、Validator、补检和终止控制；
- Task 的工作流身份是 `(novelty_point_id, task_id)`，因为 `task_id` 只在单个查新点内唯一。

### StructuredSourceRetrievalTool

`StructuredSourceRetrievalTool` 接收一个 `NoveltyPoint`、一个对应的
`ResearchTask` 和 `source_id`，确定性执行 `SearchPlanner → RetrievalSource →
Metadata/FullText`，保存 `Work / SourceRecord / Artifact`，并返回 Evidence 为空的
`ResearchBundle`。它不包含 Researcher、EvidenceCard、EvidenceValidator、覆盖度判断
或报告生成。它通过通用 Researcher 工具注册表接入任务子图。

arXiv 是当前能力完整的结构化来源，但 Tool 不假设所有来源都能取得全文。Coordinator
分发任务后，由每个 Researcher Agent 决定是否调用该 Tool。WebSearch、Browser 与
Reader 已分别完成真实 Harness/工具链验证，但尚未迁移到正式 Researcher Workflow。

### Researcher Harness 核心原则

```text
LLM = Control Plane
Harness / Tool Runtime = Data Plane
```

LLM 只提供意图参数并选择持久化句柄；Harness/Runtime 注入可信 task scope，恢复
URL、Work 和存储对象，管理基础设施配置与完整审计 Observation，并把最小投影视图
交还模型：

```text
Intent Arguments                         ← LLM
Trusted Runtime Arguments / Resolved Data
Infrastructure Config                    ← Harness / Runtime
```

工具之间使用持久化句柄连接：

```text
WebSearch          → source_record_id
Browser            → artifact_id
Reader             → read_id
EvidenceCardBuilder → evidence / evidence_card
```

模型通过句柄做决策，不承担工具之间的数据搬运。当前已验证 WebSearch、Reader，
Browser 已实现本地 Playwright 后端；Harness 使用 native Model Tool Calling，并将完整
Observation 留在 trace 中，仅把各工具的 model-context projection 放入 `role=tool`。

数据源通过 `RetrievalSourceRegistry` 注册并由 `retrieval.active_source` 选择，Workflow、Agent 与领域 Schema 不包含数据库分支。

生产/实验数据源：

- arXiv

测试数据源：

- `null_catalog`（离线 Null Object，永远返回空结果）

`null_catalog` 只验证数据源注册、配置选择、QueryAdapter/SearchTool 替换和空结果处理；它不模拟真实文献数据库，不验证 FullTextTool、MetadataTool 的跨来源兼容性，也不用于正式查新。用户自制本地数据库导入仍是 `experiments/` 下未实现、未接入工作流的探索功能。

ChinaXiv 接入状态：暂停，未注册为可用数据源。截至 2026-08-14，官网关键词检索仅验证到 HTML 表单，未发现可稳定直接调用的公开关键词 API；OAI-PMH 候选端点从当前网络返回“无权访问”而非 OAI XML，因而无法验证元数据收割、详情元数据和公开 PDF 契约。项目不会以网页爬虫或未经验证的协议假设冒充正式 ChinaXiv 支持。待取得官方接口文档或可稳定访问的 OAI-PMH 响应后再继续实现。

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
├── references/
│   ├── list.json                    # 参考作品、来源记录与已保存制品清单
│   └── documents/<work_id>/         # PDF、解析文本等实际制品
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
pip install -e ".[dev,web,browser]"
python -m playwright install chromium
```

真实模型调用使用 `backend/.env` 或进程环境变量：

```dotenv
SILICONFLOW_API_KEY=...
```

`backend/.env` 已被 Git 忽略。不要把真实 Key 写入 `.env.example`、代码、文档或提交历史。

## 运行方式

### 离线 Demo

离线 Demo 使用确定性的 `DemoTaskResearcher` 跑通任务 fan-out、Validator、补检和汇总，不访问网络：

```bash
novelty-demo --input examples/paper.json --output /tmp/novelty-result.json
```

### PDF 处理

PDF 解析默认优先使用 MinerU（独立 `mineru` conda 环境，Python API 桥接），
MinerU 不可用或质量不足时自动回退到原有文本层 + DeepSeek-OCR。

```bash
# 先准备 MinerU 独立环境（只需一次）
conda create -n mineru python=3.11 -y
conda activate mineru
pip install -U "mineru[core]==3.4.5"

# 默认走 MinerU，失败自动回退
python -m novelty_agent_framework.processing.cli \
  --input examples/MF2033k6lC.pdf \
  --output outputs

# 强制走旧文本层/OCR
python -m novelty_agent_framework.processing.cli \
  --input examples/MF2033k6lC.pdf \
  --output outputs --parser text_layer
```

MinerU 解析出的图片、表格、公式会以结构化 JSON 保存到
`outputs/<paper_id>/paper-input/others/paper.json` 和
`outputs/<paper_id>/paper-input/content-list.json`：

```json
{
  "images": [
    {"image_id": "image-1-1", "kind": "image", "page": 1, "path": "images/xxx.jpg", "caption": "图 1", "footnote": "", "bbox": []}
  ],
  "tables": [
    {"table_id": "table-1-1", "page": 1, "caption": "表 1", "footnote": "", "body": "<table>...</table>", "body_format": "html", "bbox": []}
  ],
  "equations": [
    {"equation_id": "equation-1-1", "page": 1, "latex": "x = y", "bbox": []}
  ]
}
```

图片文件会复制到 `outputs/<paper_id>/paper-input/images/`，JSON 中的 `path`
是对应 paper 工作区的相对路径（如 `images/000_xxx.jpg`）。

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

已确认 242 个非 live 测试通过（排除已知会在 TestClient 生命周期处挂起的
`tests/test_api.py`），包括任务级 Researcher 子图、通用工具注册表、安全 Artifact
分片读取、动态 fan-out/fan-in、Factory 边界与既有检索回归。
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
