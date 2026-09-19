# 演示说明：从零搭建并在浏览器中使用

本说明用于在一台干净的机器上把系统跑起来并打开网页完成一次演示。按顺序执行即可，全部命令已在 Windows + Anaconda 环境下验证。

## 一、准备清单

| 项目 | 要求 | 检查命令 |
| --- | --- | --- |
| Anaconda / Miniconda | 已安装 | `conda --version` |
| Python | 3.11 及以上 | — |
| Node.js | 22.12 及以上 | `node -v` |
| pnpm | 11.x | `pnpm -v` |
| 模型 API Key | 硅基流动或其他 OpenAI 兼容服务 | — |
| 演示用论文 | PDF 格式，不超过 30 MB | — |

后续命令中，**conda 相关命令在 Anaconda Prompt 中执行**，路径一律以项目根目录为基准。

## 二、获取代码

任选一种：

```bash
# 方式一：下载分支压缩包（仓库为公开仓库，无需登录）
# 浏览器打开后自动下载
https://github.com/RikoNJU/Novelty-Multi-Agent-Framework/archive/refs/heads/0919v1.zip

# 方式二：命令行下载
curl -L -o novelty-0919v1.zip "https://github.com/RikoNJU/Novelty-Multi-Agent-Framework/archive/refs/heads/0919v1.zip"

# 方式三：浅克隆（便于后续更新）
git clone --depth 1 -b 0919v1 https://github.com/RikoNJU/Novelty-Multi-Agent-Framework.git
```

解压后进入项目根目录（以下所有命令都在此目录执行）：

```bash
cd Novelty-Multi-Agent-Framework-0919v1
```

## 三、搭建后端

### 3.1 创建并激活 Python 环境

若已有 `Novelty` 环境可直接激活：

```bash
conda activate Novelty
```

否则新建：

```bash
conda create -n Novelty python=3.11 -y
conda activate Novelty
```

### 3.2 安装依赖

```bash
pip install -e ".[dev,web,browser]"
```

这一步会装入 LangGraph、Pydantic、FastAPI、uvicorn、python-multipart、playwright 等运行依赖。**三个 extras 都要带**：省略 `web` 会导致后端启动时直接抛 `Form data requires "python-multipart" to be installed`。

### 3.3 配置模型密钥

在 `backend/` 下创建 `.env`（该文件已被 Git 忽略）：

```dotenv
SILICONFLOW_API_KEY=你的密钥
```

也可以用系统环境变量代替。`.env` 会被自动加载，真实环境变量优先级更高。

### 3.4 安装 MinerU（强烈建议）

PDF 解析默认走 MinerU。不安装时会回退到文本层 + DeepSeek-OCR，OCR 依赖模型调用，速度慢且可能失败。建议提前装好：

```bash
conda create -n mineru python=3.11 -y
conda activate mineru
pip install -U "mineru[core]==3.4.5"
```

默认配置已指向名为 `mineru` 的环境（`processing.mineru_env`）与 `scripts/mineru_worker.py`，无需额外配置。首次运行 MinerU 会下载模型权重，建议提前预热一次。

### 3.5 启动后端

```bash
python -m novelty_agent_framework.main
```

默认监听 `0.0.0.0:8010`。**启动时的工作目录必须是项目根目录**，否则运行产物会写到别处（`outputs/` 等路径均为相对路径）。

### 3.6 验证后端

浏览器打开或在另一个终端执行：

```bash
curl http://localhost:8010/api/novelty/health
```

正常返回：

```json
{"status":"ready","application":"论文查新 Multi-Agent","workflow":"real"}
```

`status` 必须是 `ready`。若为 `degraded`，说明模型凭据没配好，前端提交会返回 503。

## 四、搭建前端

### 4.1 安装 pnpm

```bash
npm install -g pnpm
```

### 4.2 安装依赖并启动

```bash
cd frontend
pnpm install
pnpm dev
```

终端会输出本地访问地址，通常是：

```text
http://127.0.0.1:5173
```

### 4.3 打开网页

浏览器访问 `http://127.0.0.1:5173`，即可看到上传页面。

开发服务器会把 `/api` 请求代理到 `http://localhost:8010`，因此**后端必须先启动**，否则页面能打开但提交会失败。

## 五、演示操作流程

1. 在首页选择或拖入一篇 PDF（不超过 30 MB，需为有效 PDF 文件）；
2. 点击提交，页面进入任务轮询；
3. 观察六个阶段的真实进度：解析论文 → 提取查新点 → 规划检索 → 文献调研 → 证据校验与补检 → 生成报告；
4. 完成后进入报告页，可在线预览 Markdown 报告，也可点击下载；
5. 若部分查新点因证据不足未完成，完成页会显示范围限制说明。

命令行侧可以核对产物：

```text
outputs/<paper_id>/novelty-points.json      查新点
outputs/<paper_id>/evidence-cards.json      证据卡
outputs/<paper_id>/report/<paper_id>-report.md   最终报告
outputs/<paper_id>/runtime/<run_id>/llm_calls/   逐次模型调用与计费
```

## 六、常见问题

**后端启动即崩溃，报 `Form data requires "python-multipart"`**
依赖没装齐。执行 `pip install -e ".[dev,web,browser]"` 或单独 `pip install python-multipart`。

**健康检查返回 `degraded`**
模型凭据缺失或无效。检查 `backend/.env` 中的 Key 名称是否为 `SILICONFLOW_API_KEY`，并确认后端是在写入 `.env` 之后启动的。

**前端提交返回 503**
后端未装配真实工作流，通常与上一条同因。

**PDF 解析长时间无响应或失败**
MinerU 环境未装好或首次运行正在下载权重。可先单独验证解析：

```bash
python -m novelty_agent_framework.processing.cli --input <论文.pdf> --output outputs
```

若输出了 `outputs/<paper_id>/paper-input/full.md`，说明解析链路正常。

**端口被占用**
8010 被占用时后端起不来，5173 被占用时前端会换端口（换端口后 CORS 白名单可能不匹配，建议释放原端口）。

**页面能打开但接口全部失败**
后端没启动，或后端端口不是 8010（`frontend/vite.config.ts` 中的代理目标写死为 `http://localhost:8010`）。

**Windows 路径过长导致 checkout 或解析失败**
在项目目录执行 `git config core.longpaths true`。

**暂无模型 Key 时如何演示界面**
可显式设置 `NOVELTY_WORKFLOW_MODE=demo` 启动后端，走确定性的离线研究者，用于展示界面与流程。该模式不产生真实文献结论，且未在本次验证中实测，正式演示请使用默认的 `real` 模式。

## 七、演示节奏建议

- 提前用演示用论文完整跑一遍，确认环境无问题，并保留好产物；
- 真实运行的耗时参考：单篇论文端到端约 180 秒（77 次模型调用、约 96.8 万 token）；
- 若演示时间紧张，可先用已解析过的论文缩短解析阶段；
- 报告页建议展示证据卡与报告原文的对应关系，这是系统区别于普通文献综述的核心。
