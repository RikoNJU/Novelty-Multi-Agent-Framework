# 睿文查新前端

React + TypeScript + Vite 单任务工作区。首页、文件选择/本地预览、提交反馈、任务轮询、完成/失败状态和报告阅读器已实现。页面采用南大背景图与紫色主题，支持移动端、键盘操作和减少动态效果设置。

## 启动

需要 Node.js 22.12+ 和 pnpm 11。首次运行：

```bash
cd frontend
pnpm install
pnpm dev
```

打开 http://127.0.0.1:5173。开发服务器将 `/api` 代理至 `http://localhost:8010`。后端启动方式仍为仓库根目录下的 `python -m novelty_agent_framework.main`。

```bash
pnpm build         # 类型检查 + 生产构建，输出 dist/
pnpm preview       # 仅预览静态产物；不代理后端
pnpm test          # 单元和组件测试
pnpm exec playwright install chromium
pnpm test:e2e      # 自动启动专用测试服务器，使用测试内的接口拦截
```

若已安装 Chrome，可设置 `PLAYWRIGHT_CHROMIUM_EXECUTABLE` 为其可执行文件绝对路径。端到端测试应在没有其他服务占用 5187 端口时运行。

生产部署需要将 `dist/` 作为静态目录，并将同源 `/api/novelty/` 反向代理至后端；不得将未知路径或 API 错误回退为 `index.html`。鉴权应由同源代理统一处理。报告跨域地址被拒绝，不保存令牌或论文内容到浏览器存储。

## 当前后端边界

- `POST /api/novelty/runs/files` 接收 multipart `paper` 单个 PDF，校验扩展名、MIME、空文件、30 MB 限额和 PDF 签名；参考文献字段尚未开放。同一提交意图携带 `X-Submission-Id`，服务端对相同文件返回原任务，不再次调度。响应丢失时页面保持“提交状态待确认”，阻止再次点击提交。
- 前端不渲染参考文献上传框；相关接口契约保留，后端收到 `references` 会返回 `references_not_supported`，不会静默忽略。
- `/?run=<任务编号>` 轮询真实 `queued/running/succeeded/failed` 和六阶段进度。断线指数退避至 30 秒，页面隐藏时至少间隔 15 秒，终态停止轮询。
- 成功任务优先读取后端 Renderer 生成的 Markdown 报告，并提供同源下载；旧任务仍可回退展示结构化报告。部分点因技术原因未完成时，完成页会显示范围限制；语义证据不足与运行未完成分开显示。
- 服务端默认装配真实工作流。缺少模型凭据时健康检查为 `degraded`，提交返回 503，不会回退 Demo。
- 任务状态仍存于内存，服务重启后任务编号失效；这是单机首版边界。

任务查询响应字段如下（详见 `src/api/contracts.ts`）：

```ts
progress?: {
  stage: 'parse_paper' | 'extract_points' | 'plan_research' |
         'research' | 'validate_evidence' | 'render_report';
  round?: number | null;
} | null;
report?: {
  available_formats: ('md' | 'pdf')[];
  preview_url: string;
  downloads: { md?: string; pdf?: string };
} | null;
```

报告资源只接受同源 `/api/novelty/` URL及白名单 MIME；下载文件名经过清理。`error` 兼容原有字符串和 `{code,message,retryable}`，原始服务端异常不直接显示。

实时进度目前使用轮询，没有依赖尚不存在的 SSE 接口。六个阶段按服务端 progress 显示，不用计时器模拟。阶段节点分组：解析服务→parse_paper；extract_points→extract_points；plan/dispatch_planning_tasks/plan_research_task→plan_research；dispatch_research_tasks/run_research_task→research；validate_evidence/review_evidence/validate_synthesis_input/check_final_evidence_sufficiency/plan_supplement→validate_evidence；synthesize_report/validate_report_integrity/persist_report/render_report→render_report。补检由服务端保持 validate_evidence 并提供 round。

## 文件、隐私与预览

客户端与服务端主论文限额均默认为 30 MB，可分别通过构建变量和 `NOVELTY_MAX_UPLOAD_MB` 调整；部署时必须保持一致。

PDF 用独立 PDF.js worker 渲染为 Canvas，关闭动态求值与注解层，不执行文档脚本；支持翻页和缩放。Markdown 支持 GFM，禁用原始 HTML、危险链接和远程图片请求；外部链接有安全属性。文本按纯文本显示。Blob 下载 URL 用后释放。本地选中文件仅在用户提交后发送，成功提交会清理本地文件引用。

背景图是 `https://box.nju.edu.cn/media/custom/login-bg.jpg`，访问该外部图片会向图片服务发送网络请求。图片失败时回退为深紫色，文字和交互不依赖图片。未将图片下载入库，未引入远程字体。

## 验证范围

- 单元/组件：扩展名、MIME、数量、大小、空文件、阶段映射、退避、错误归一化、文件名清理、缺失论文焦点、键盘和拖放、Markdown 安全。
- 浏览器测试通过测试专用 API 拦截验证创建→轮询→报告→下载、刷新恢复、404/422/500、断网重连和报告加载失败。拦截只存在于 `tests/`，生产页面没有 mock 开关或示例结果。
- 390 / 768 / 1440 像素布局、背景图失败、Reduced Motion 和 axe 基础扫描。

浏览器测试仍使用接口拦截，不调用收费模型。后端文件接口另有离线 API 测试；真实网络与模型验收需要显式凭据、授权和预算。
