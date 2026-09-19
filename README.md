# 论文查新 Multi-Agent 框架

基于 LangGraph 的论文查新辅助系统。输入一篇论文，系统提取查新点、规划检索任务、并行调研文献、对证据做确定性校验与门控，最终产出一份可回溯到原文的查新报告。

本系统为研究原型与辅助工具，**不能替代正式科技查新机构**。

## 项目结构

```text
backend/env/                              统一模型客户端、模型注册表和 PromptLibrary
backend/src/novelty_agent_framework/
├── agents/                               Coordinator、PointExtractor、SearchPlanner、Researcher、Validator、Reviewer
├── config/                               配置加载、模型注册与工作流组合根
├── core/                                 完整性门、格式修复、工具调用 Harness、报告字段绑定
├── diagnostics/                          LLM usage 归一化与 RMB 计费
├── ports/                                可替换能力接口
├── processing/                           PDF 解析（MinerU / 文本层 / OCR）、章节与标题提取
├── prompts/                              版本化 Agent 提示词
├── schemas/                              Pydantic 数据契约
├── skills/                               数据库调研、Web 补充、Reviewer 裁决技能
├── tools/                                Adapter、arXiv 工具、阅读器、Renderer 等
├── web/                                  后端运行器与报告资源管理
├── workflows/                            LangGraph 状态、主工作流与任务子图
├── persistence.py                        按 paper 隔离的本地产物持久化
└── main.py                               FastAPI 入口
frontend/                                 React + TypeScript + Vite 前端
docs/                                     架构与设计文档
scripts/mineru_worker.py                  MinerU 解析工作进程
assets/                                   工作流示意图
```

## 环境配置

### Python 环境

项目使用已创建的 `Novelty` Conda 环境：

```bash
conda activate Novelty
pip install -e ".[dev,web,browser]"
python -m playwright install chromium
```

### PDF 解析环境（MinerU）

PDF 解析默认优先使用 MinerU（独立环境，Python API 桥接）：

```bash
conda create -n mineru python=3.11 -y
conda activate mineru
pip install -U "mineru[core]==3.4.5"
```

MinerU 不可用或解析质量不足时，自动回退到文本层抽取 + DeepSeek-OCR。

### 模型密钥

真实模型调用使用 `backend/.env` 或进程环境变量：

```dotenv
SILICONFLOW_API_KEY=...
```

`backend/.env` 已被 Git 忽略。不要把真实 Key 写入 `.env.example`、代码或提交历史。

### 模型与角色配置

- `backend/src/novelty_agent_framework/config/models.example.json`：登记模型别名（provider、base_url、model、api_key_env、context_window、supported_params、defaults）；
- `config/settings.example.json`：为每个角色指定模型别名、温度与提示词文件；
- 按角色覆盖模型：`NOVELTY_COORDINATOR_MODEL`、`NOVELTY_RESEARCH_MODEL`、`NOVELTY_SEARCH_PLANNER_MODEL`；
- 厂商私有参数（如 `enable_thinking`）经 `supported_params` 白名单过滤后透传，换模型不会因多余参数失败；
- 逐次调用的用量与费用按 `config/llm_pricing.json` 的单价表计算，未知单价标记为 `UNPRICED`。


### 前端环境

需要 Node.js 22.12+ 与 pnpm 11。

## 使用方式

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

解析产物写入 `outputs/<paper_id>/paper-input/`：全文 Markdown、内容清单（图片、表格、公式的结构化 JSON）、图片文件与论文元数据。

### 2. 离线 Demo

使用确定性的 DemoTaskResearcher 跑通任务 fan-out、校验、补检与汇总，不访问网络：

```bash
novelty-demo --input <paper.json> --output <result.json>
```

输入为 `PaperInput` JSON，必填字段仅 `paper_id`、`title`、`full_text`：

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

### 4. 后端 API

```bash
# 默认装配真实工作流；缺少模型凭据时健康检查为 degraded，提交返回 503
python -m novelty_agent_framework.main
```

- `POST /api/novelty/runs/files`：接收 multipart 单篇 PDF，校验扩展名、MIME、空文件、大小上限（默认 30 MB，可用 `NOVELTY_MAX_UPLOAD_MB` 调整）与 PDF 签名；同一提交意图携带 `X-Submission-Id`，重复提交返回原任务而不重复调度；
- `GET /api/novelty/runs/<run_id>`：返回任务状态与六阶段真实进度（`queued/running/succeeded/failed`），终态停止轮询；
- 报告资源只接受同源 `/api/novelty/` URL 与白名单 MIME，支持 Markdown 预览与同源下载。

### 5. 前端

```bash
cd frontend
pnpm install
pnpm dev          # 开发服务器，将 /api 代理到 http://localhost:8010
pnpm build        # 类型检查 + 生产构建，输出 dist/
pnpm preview      # 预览静态产物，不代理后端
```

## 产物与进度

```text
outputs/<paper_id>/
├── paper-input/                     full.md、content-list.json、images/、others/paper.json
├── references/                      list.json、documents/<work_id>/
├── novelty-points.json
├── retrieval-plans.json             research_tasks、search_plans、executed_queries
├── evidence-cards.json
├── report.json
└── report/<paper_id>-report.md
```

开启 `runtime_debug` 时，每次生产模型调用写入 `outputs/<paper_id>/runtime/<run_id>/llm_calls/`，单次记录包含模型、阶段、耗时、输入/缓存输入/输出/推理 token、单价档与 RMB 金额；`summary.json`、`summary.md` 提供按模型和整次运行的汇总。

前端按六个阶段显示真实进度：`parse_paper`、`extract_points`、`plan_research`、`research`、`validate_evidence`、`render_report`。

## 部署

后端直接以 `python -m novelty_agent_framework.main` 启动，由同源代理统一处理鉴权。

前端生产部署需将 `dist/` 作为静态目录，并将同源 `/api/novelty/` 反向代理到后端；不得将未知路径或 API 错误回退为 `index.html`。报告跨域地址被拒绝，不在浏览器存储中保存令牌或论文内容。
