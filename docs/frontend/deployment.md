# 开发与部署

从仓库根目录操作。Python >=3.11；构建机使用 Node.js 22.16+ 和 npm。Node 只用于构建，最终使用者无需安装。

```bash
python -m pip install -e '.[web,dev]'
cd frontend
npm ci
npm run build
cd ..
python -m novelty_agent_framework.main
```

访问 `http://localhost:8010/`。前端构建目录必须在服务启动前存在；缺少构建目录时 API 仍可使用。原有 README 的 `/api/novelty` 是 JSON 联调接口，新产品使用 `/api/runs`。multipart 上传依赖 `python-multipart`，已加入 web extra（[FastAPI 文件上传说明](https://fastapi.tiangolo.com/tutorial/request-files/)）。

模型、检索、MinerU 环境沿用后端现有配置与 `.env`。不新增网页配置中心。务必先完成现有后端运行环境设置；安装 Web 依赖不会自动安装 MinerU 模型。解析参数与项目 processing 配置一致，运行产物隔离到各自目录。

开发时后端照常启动，再执行：

```bash
cd frontend
npm run dev
```

Vite 默认把 `/api` 代理到 `http://localhost:8010`。需要改目标时，在 `frontend/.env.local` 设置 `NOVELTY_API_TARGET`。地址只属于开发配置，前端业务代码全部使用同源路径。

生产使用单个 Uvicorn worker，必须从仓库根目录启动，或设置两个绝对路径：

- `NOVELTY_FRONTEND_DIST`：构建目录，默认 frontend/dist。
- `NOVELTY_WEB_RUNS`：持久化 Run 根目录，默认 outputs/web-runs。
- `NOVELTY_HOST` / `NOVELTY_PORT`：沿用现有后端设置；本地使用建议 NOVELTY_HOST=127.0.0.1。

不要使用多个进程共同管理一个 Run 根目录。任务在单进程线程池串行执行，不依赖浏览器；服务重启不能续跑，会把遗留任务标为中断。

服务器使用 HTTPS 反向代理同源转发根路径及 /api，上传请求限制至少 26 MiB。首版仅支持站点根路径；未实现任意子路径部署。服务器必须处于受控访问范围，公网认证／多用户权限不在本次范围内。正式页面不需要 Vite 或 Express。

## PWA

安装清单唯一来源为 public/manifest.webmanifest；图标为 192/512 PNG。Vite 插件在构建时生成带内容版本的 sw.js，仅缓存明确列出的静态界面文件，不缓存 /api、论文、报告或状态。离线可打开界面，但不能运行后端或查看未在线获取的报告。

Chrome／Edge 在 localhost 或 HTTPS 上可按浏览器提供的安装入口操作；普通局域网 HTTP 不算安装验收通过。安装不会安装或启动 Python 服务。

更新：重新 `npm ci && npm run build`，原子替换完整 dist，然后按部署方式重启服务。页面检测到 waiting Service Worker 后显示更新按钮；由用户点击更新，上传期间不执行更新。run_id 在 URL 中，因此更新后可继续观察原任务。

## 验证

```bash
python -m pytest tests/test_pdf_web.py tests/test_api.py
cd frontend
npm test
npm run build
cd ..
python scripts/check_frontend_browser.py --report /path/to/existing-report.md
```

浏览器脚本使用本地 stub executor、已有报告样本与真实 PDF 上传，验证 UI，不调用模型／检索服务。需要 Playwright Chromium 与系统动态库。真实模型 HTTP 运行是独立验收项，不可用该脚本替代。

实现参照：[Vite 文档](https://vite.dev/guide/)、[markdown-it 文档](https://github.com/markdown-it/markdown-it)。Markdown 禁用原始 HTML 和图片；支持表格、列表、引用与代码，不额外支持公式或本地相对资源。
