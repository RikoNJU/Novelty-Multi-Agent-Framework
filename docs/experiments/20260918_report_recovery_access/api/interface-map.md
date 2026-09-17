# 实际接口图

前端使用 `/?report_resource_id=<opaque-id>`。Vite 的 `/api` 代理指向 `http://localhost:8010`；实际后端绑定 `127.0.0.1:8010`。`NoveltyWebSettings.api_prefix` 为 `/api/novelty`。已从运行中的 `/openapi.json` 确认：

| 方法 | 路径 | 内容 |
|---|---|---|
| GET | `/api/novelty/report-artifacts/{resource_id}` | 来源、原状态、恢复范围、文件哈希和点状态 |
| GET | `/api/novelty/report-artifacts/{resource_id}/content` | 原样 Markdown，inline |
| GET | `/api/novelty/report-artifacts/{resource_id}/download` | 同一 Markdown 字节，attachment |
| GET | `/api/novelty/report-artifacts/{resource_id}/provenance` | 脱敏来源 JSON |

资源路由使用独立 `ReportResourceStore`，不依赖旧 `/api/novelty/runs/{task_id}` 所需的 `NoveltyWorkflowService`。旧业务 run 没有被创建或改写。浏览器请求只含 GET；没有路由拦截、MSW 或客户端固定报告正文。后端每次读取校验哈希，文件缺失为 404，完整性或索引损坏为 409。
