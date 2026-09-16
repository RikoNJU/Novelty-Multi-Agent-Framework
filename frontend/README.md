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

## 当前后端边界（务必保留）

本次仅实现前端，没有修改后端工作流，也没有将测试数据接入正式入口。

- 当前后端 `POST /api/novelty/runs` 仅接收 `PaperInput` JSON；前端不会把文件名转换成 JSON 冒充上传。默认关闭文件提交，同时允许本地选择、删除、预览文件。
- `/?run=<任务编号>` 可以查询现有后端任务。轮询使用真实 `queued/running/succeeded/failed` 状态；没有 progress 时只显示排队或正在查新。断线指数退避至 30 秒，页面隐藏时至少间隔 15 秒。终态停止轮询，卸载取消请求。
- 当前成功任务可以预览服务返回的结构化报告，包括结论、研究局限、缺失参考文献、缺失基线和引用问题；它不是后端 Renderer 生成的 Markdown 文件，不提供伪造下载。
- 上传、真实六阶段进度、Markdown/PDF 文件下载需要下述新增契约。尚未完成真实文件链路端到端联调。
- 服务端任务存于内存；404 会提示服务重启导致任务失效，并由用户主动重新开始。

## 后续服务端接入契约

实现并验证以下契约后，复制 `.env.example` 到 `.env.local`，设置 `VITE_FILE_API_ENABLED=true` 并重启/重新构建前端。这个开关不是自动能力探测；未实现接口时不能启用。

1. `POST /api/novelty/runs/files` 接收 multipart：`paper` 单个 PDF、`references` 重复字段；返回 202 和任务快照。服务端负责内容嗅探、签名、解析、限额、文件名和安全校验。
2. `GET /api/novelty/runs/{task_id}` 保留当前字段，可新增以下字段（详见 `src/api/contracts.ts`）：

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

3. 报告资源必须为同源 `/api/novelty/` 下的 URL，携带 `Content-Type: text/markdown`、`text/plain` 或 `application/pdf`，以及含真实文件名的 `Content-Disposition`，推荐 `filename*=UTF-8''...`。下载仅在完整读取并验证报告资源后出现，保留服务端 MIME 和中文文件名。前端不会从后端文件系统路径读取报告。
4. `error` 兼容原有字符串和 `{code,message,retryable}` 对象；原始服务端错误不直接显示，避免泄漏路径、密钥或模型内部信息。

实时进度目前使用轮询，没有依赖尚不存在的 SSE 接口。六个阶段按服务端 progress 显示，不用计时器模拟。阶段节点分组：解析服务→parse_paper；extract_points→extract_points；plan/dispatch_planning_tasks/plan_research_task→plan_research；dispatch_research_tasks/run_research_task→research；validate_evidence/review_evidence/validate_synthesis_input/check_final_evidence_sufficiency/plan_supplement→validate_evidence；synthesize_report/validate_report_integrity/persist_report/render_report→render_report。补检由服务端保持 validate_evidence 并提供 round。

## 文件、隐私与预览

暂定客户端限额统一位于 `src/features/upload/validation.ts`，支持环境变量覆盖：单文件 30 MB、合计 100 MB、参考文献 20 个。**这些是客户端保护值，不是现有服务端承诺**，接通上传前必须与服务端统一。

PDF 用独立 PDF.js worker 渲染为 Canvas，关闭动态求值与注解层，不执行文档脚本；支持翻页和缩放。Markdown 支持 GFM，禁用原始 HTML、危险链接和远程图片请求；外部链接有安全属性。文本按纯文本显示。Blob 下载 URL 用后释放。本地选中文件仅在用户提交后发送，成功提交会清理本地文件引用。

背景图是 `https://box.nju.edu.cn/media/custom/login-bg.jpg`，访问该外部图片会向图片服务发送网络请求。图片失败时回退为深紫色，文字和交互不依赖图片。未将图片下载入库，未引入远程字体。

## 验证范围

- 单元/组件：扩展名、MIME、数量、大小、空文件、阶段映射、退避、错误归一化、文件名清理、缺失论文焦点、键盘和拖放、Markdown 安全。
- 浏览器测试通过测试专用 API 拦截验证创建→轮询→报告→下载、刷新恢复、404/422/500、断网重连和报告加载失败。拦截只存在于 `tests/`，生产页面没有 mock 开关或示例结果。
- 390 / 768 / 1440 像素布局、背景图失败、Reduced Motion 和 axe 基础扫描。

测试使用的模拟响应仅验证前端契约，不代表后端文件接口已经实现。原前端开发指南按任务要求在交付时删除，其接口边界和运行说明保留于本文件。
