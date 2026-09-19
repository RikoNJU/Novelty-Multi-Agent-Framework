# 论文查新 Multi-Agent 框架

基于 LangGraph 的论文查新辅助系统。输入一篇论文，系统提取查新点、规划检索任务、并行调研文献、对证据做确定性校验与门控，最终产出一份可回溯到原文的查新报告。

系统将论文解析、查新点提取、检索规划、候选文献召回、证据分析与报告生成拆成可审计的阶段，**模型只负责判断与选择，证据的定位、绑定与门控由确定性组件完成**。

本仓库是可运行代码版本，不含测试、实验归档与开发过程文档。

## 边界声明

- 本系统是研究原型与辅助工具，**不能替代正式科技查新机构**；
- 不使用“世界首创”“绝对原创”等超出检索能力的表述，结论类型为“创新性证据较强 / 部分创新 / 创新性较弱 / 证据不足”；
- 系统不训练、不微调模型，全部推理由外部大模型 API 承担。

## 工作流

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
EvidenceReviewer                   证据复核
  ↓
Provenance Integrity Gate          过滤溯源链不完整的 Card
  ↓
Final Evidence Sufficiency Check   按查新点检查最终有效 Card 数量
  ├─ 数量不足 且轮次未耗尽 → Coordinator.plan_supplement → 重新经过完整检索链
  └─ 数量达标或轮次耗尽
  ↓
Coordinator.synthesize             生成结构化 NoveltyReport
  ↓
Renderer                           生成 Markdown 报告
```

LangGraph 主图节点顺序：

```text
START
→ extract_points
→ plan
→ dispatch_planning_tasks
→ plan_research_task
→ dispatch_research_tasks
→ run_research_task                每个 ResearchTask 运行一个 LangGraph 子图
→ validate_evidence
→ review_evidence
→ validate_synthesis_input
→ check_final_evidence_sufficiency
  ├─ plan_supplement → dispatch_planning_tasks → ...
  └─ synthesize_report → validate_report_integrity → persist_report → render_report
→ END
```

## 关键架构边界

- Coordinator 只负责任务拆分、补检规划和全局汇总，不生成数据库查询；
- SearchPlanner 只生成 Concept、term 和布尔策略，不包含 `all:` 等数据库语法；
- QueryAdapter 是无 LLM、无网络副作用的确定性编译器；
- SearchTool 只执行已经编译的查询；
- 每个 Researcher 只接收一个绑定的 `NoveltyPoint + ResearchTask`，通过模型原生 Tool Calling 调用注册工具，不接收全局任务或最终报告上下文；
- TaskResearcher 子图负责预算、重复调用限制和局部失败隔离；主 Workflow 负责 fan-out/fan-in、Validator、补检和终止控制；
- Task 的工作流身份是 `(novelty_point_id, task_id)`，因为 `task_id` 只在单个查新点内唯一。

### Researcher Harness 核心原则

```text
LLM = Control Plane          # 只提供意图参数并选择持久化句柄
Harness / Tool Runtime = Data Plane
                             # 注入可信 task scope、恢复 URL/Work/存储对象、
                             # 管理基础设施配置与完整审计 Observation，
                             # 把最小投影视图交还模型
```

工具之间使用持久化句柄连接，模型只做选择、不承担数据搬运：

```text
WebSearch            → source_record_id
Browser              → artifact_id
Reader               → read_id
EvidenceCardBuilder  → evidence_card
```

### 证据质量约束

- 重要结论必须关联可追溯的文献证据，只有模型判断而没有文献证据的内容不能作为结论；
- 证据的原文引用、所属 Artifact 与字符位置由非 LLM 组件确定性绑定，不采信模型自述的位置；
- 溯源链不完整的 Card 由 Provenance Integrity Gate 直接过滤；
- 证据充分性检查按查新点统计有效 Card 数量，低于 `min_final_evidence_cards_per_point` 时记录 `insufficient_final_evidence` 事实并触发补检回边，只重跑证据不足的查新点；
- 故障语义强制分离：真实接口错误记为 `FAILED` / `PROVIDER_FAILED`，零命中记为 `ZERO_RESULT`，不降级伪装为“无相关工作”。

## 数据源

数据源通过 `RetrievalSourceRegistry` 注册，由 `retrieval.active_source` 选择；Workflow、Agent 与领域 Schema 不包含数据库分支。

| 数据源 | 状态 | 说明 |
| --- | --- | --- |
| arXiv | 默认启用 | 当前能力完整的结构化来源，支持元数据与全文 |
| ScienceDirect | 默认禁用 | 已完成离线 API 契约测试，启用需 Elsevier Key |
| Springer Nature | 默认禁用 | Meta API 检索，开放全文 JATS；TDM 全文需另行授权 |
| IEEE Xplore | 默认禁用 | Metadata API 检索，默认仅尝试 Open Access 全文 |
| null_catalog | 测试源 | 离线 Null Object，永远返回空结果，仅用于验证注册与空结果处理 |

arXiv 的接口限流由进程级共享调度统一处理：所有会话共用闸门，遵守最小间隔与 `Retry-After`，配合有限重试、预算上限与单探测熔断；逻辑请求与物理请求分开计数。接口不可用时可显式配置 Web 通道作为替代检索路径。

新增数据库的 Provider 边界、配置与要求见 [`docs/database-providers.md`](docs/database-providers.md)。

## 项目结构

```text
backend/env/                              统一模型客户端、模型注册表和 PromptLibrary
backend/src/novelty_agent_framework/
├── agents/                              Coordinator、PointExtractor、SearchPlanner、Researcher、Validator、Reviewer
├── config/                              配置加载、模型注册与真实工作流组合根
├── core/                                完整性门、格式修复、工具调用 Harness、报告字段绑定
├── diagnostics/                         LLM usage 归一化与 RMB 计费
├── ports/                               可替换能力接口
├── processing/                          PDF 文本层解析、MinerU、OCR 兜底、章节与标题提取
├── prompts/                             版本化 Agent 提示词
├── schemas/                             Pydantic 数据契约
├── skills/                              数据库调研、Web 补充、Reviewer 裁决技能
├── tools/                               Adapter、arXiv 工具、阅读器、Renderer 等
├── web/                                 后端运行器与报告资源管理
├── workflows/                           LangGraph 状态、主工作流与任务子图
├── persistence.py                       按 paper 隔离的本地产物持久化
└── main.py                              FastAPI 入口
frontend/                                 React + TypeScript + Vite 前端
docs/                                     架构与设计文档
scripts/mineru_worker.py                  MinerU 解析工作进程（PDF 解析依赖）
assets/                                   工作流示意图
```

## 环境与安装

项目使用已创建的 `Novelty` Conda 环境：

```bash
conda activate Novelty
pip install -e ".[dev,web,browser]"
python -m playwright install chromium
```

PDF 解析默认优先使用 MinerU（独立环境，Python API 桥接）；MinerU 不可用或质量不足时自动回退到文本层 + DeepSeek-OCR。

```bash
# 准备 MinerU 独立环境（只需一次）
conda create -n mineru python=3.11 -y
conda activate mineru
pip install -U "mineru[core]==3.4.5"
```

## 配置

真实模型调用使用 `backend/.env` 或进程环境变量：

```dotenv
SILICONFLOW_API_KEY=...
```

`backend/.env` 已被 Git 忽略。不要把真实 Key 写入 `.env.example`、代码或提交历史。

模型与角色绑定通过配置注册：`backend/src/novelty_agent_framework/config/models.example.json` 登记模型别名（provider、base_url、model、api_key_env、context_window、supported_params、defaults），`settings.example.json` 为每个角色指定模型别名、温度与提示词文件。厂商私有参数（如 `enable_thinking`）通过白名单过滤后透传，更换模型不会因多余参数失败。

按角色覆盖模型的环境变量：`NOVELTY_COORDINATOR_MODEL`、`NOVELTY_RESEARCH_MODEL`、`NOVELTY_SEARCH_PLANNER_MODEL`。

逐次调用的用量与费用按 `backend/src/novelty_agent_framework/config/llm_pricing.json` 定义的单价表计算；未知单价标记为 `UNPRICED`，不按 0 元处理。

## 运行方式

### 1. PDF 处理

```bash
# 默认走 MinerU，失败自动回退
python -m novelty_agent_framework.processing.cli \
  --input <你的论文.pdf> \
  --output outputs

# 强制走旧文本层 / OCR
python -m novelty_agent_framework.processing.cli \
  --input <你的论文.pdf> \
  --output outputs --parser text_layer
```

MinerU 解析出的图片、表格、公式以结构化 JSON 保存到 `outputs/<paper_id>/paper-input/others/paper.json` 与 `content-list.json`，图片复制到 `paper-input/images/`。

### 2. 离线 Demo

使用确定性的 DemoTaskResearcher 跑通任务 fan-out、Validator、补检与汇总，不访问网络：

```bash
novelty-demo --input <paper.json> --output <result.json>
```

输入为 `PaperInput` JSON。必填字段仅 `paper_id`、`title`、`full_text`，其余可选：

```json
{
  "paper_id": "my-paper",
  "title": "论文标题",
  "abstract": "中文摘要",
  "english_abstract": "English abstract",
  "full_text": "论文正文全文",
  "references": ["参考文献条目"],
  "claimed_contributions": ["作者声明的主要贡献"],
  "keywords_zh": ["关键词"],
  "keywords_en": ["keyword"],
  "metadata": {}
}
```

若已完成 PDF 处理，可直接使用 `outputs/<paper_id>/paper-input/others/paper.json` 作为输入，无需重新解析。

### 3. 配置驱动的真实工作流

```python
from novelty_agent_framework.config import build_workflow, load_config
from novelty_agent_framework.schemas import PaperInput

config = load_config()
config["retrieval"]["sources"]["arxiv"]["enabled"] = True
workflow = build_workflow(config)
result = workflow.run(PaperInput.model_validate(paper_data))
```

### 4. 后端 API 与前端

```bash
# 后端：默认装配真实工作流，缺少模型凭据时健康检查为 degraded
python -m novelty_agent_framework.main
```

```bash
# 前端
cd frontend
pnpm install
pnpm dev
```

前端为 React + TypeScript + Vite 单任务工作区，开发服务器将 `/api` 代理到 `http://localhost:8010`。主要接口：

- `POST /api/novelty/runs/files`：接收 multipart 单篇 PDF，校验扩展名、MIME、空文件、大小上限（默认 30 MB）与 PDF 签名；同一提交意图携带 `X-Submission-Id`，重复提交返回原任务而不重复调度；
- `GET /api/novelty/runs/<run_id>`：返回任务状态与六阶段真实进度（`queued/running/succeeded/failed`），终态停止轮询；
- 报告资源只接受同源 `/api/novelty/` URL 与白名单 MIME，支持 Markdown 预览与同源下载。

生产部署需将前端 `dist/` 作为静态目录，并将同源 `/api/novelty/` 反向代理到后端；不得将未知路径或 API 错误回退为 `index.html`。

## 产物结构

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

开启 `runtime_debug` 时，每次生产模型调用还会写入 `outputs/<paper_id>/runtime/<run_id>/llm_calls/`：单次记录包含模型、阶段、耗时、输入/缓存输入/输出/推理 token、所用单价档及 RMB 金额；`summary.json` 与 `summary.md` 提供按模型和整次运行的汇总。

`retrieval-plans.json` 按查新点保存 `research_tasks`、数据库无关的 `search_plans`、真正执行的 `executed_queries`，以及供 Renderer 使用的 `query_plan.queries`。

## 已知限制

- 只有 arXiv 是能力完备的数据源，中文文献覆盖不足；
- SearchPlanner 偶尔输出非法 Strategy ID，重试一次仍可能失败；
- Agent 内部使用同步模型 HTTP 调用，异步节点实际接近串行；
- Coordinator 补检和汇总上下文过大，是主要输入 token 来源；
- 任务状态存于内存，服务重启后任务编号失效，是单机首版边界；
- 本地 JSON 持久化仍是原型实现。

## 文档

- [代码框架说明](docs/code-framework.md)
- [代码框架详细说明](docs/code-framework-detailed.md)
- [数据库接入报告](docs/database-integration-report.md)
- [数据源接入规范](docs/database-providers.md)
- [初始设计 V0](docs/design-v0.md)
