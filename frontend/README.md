# Novelty 论文查新前端

本目录由原“未来交互层预留”补齐为 Vite + 原生 TypeScript 单页工具。支持单 PDF 上传、阶段观察、Markdown 预览／原文件下载，以及 PWA 静态界面安装。

```bash
npm ci
npm run dev
npm test
npm run build
```

业务请求使用同源 `/api/runs`。后端默认端口仍为 8010；原说明中的 `/api/novelty` 是既有 JSON 联调 API，不是 PDF 上传接口。开发代理目标可通过 NOVELTY_API_TARGET 配置。

构建结果 frontend/dist 由 FastAPI 托管。详见 [部署说明](../docs/frontend/deployment.md)、[接口契约](../docs/frontend/api.md)、[验收记录](../docs/frontend/acceptance.md)。
