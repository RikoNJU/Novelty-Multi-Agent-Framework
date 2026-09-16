# PDF Web API

业务前缀 `/api`；旧 `/api/novelty` JSON Demo 接口为原有联调接口，前端不调用。

| 方法与路径 | 成功响应 |
| --- | --- |
| GET /api/health | 200 `{ "status":"ok", "max_pdf_bytes":26214400 }` |
| POST /api/runs | 202 `{ "run_id":"run-…", "status":"pending 或 running" }` |
| GET /api/runs/{run_id} | 200 运行快照 |
| GET /api/runs/{run_id}/report | 200 `{ "content":"# 查新报告…" }` |
| GET /api/runs/{run_id}/report.md | 200 原始 UTF-8 Markdown，attachment 下载 |
| GET /api/runs/{run_id}/artifacts | 200 `{ "run_id":"…", "artifacts":[{"type":"review","available":true,"revision":123}] }` |
| GET /api/runs/{run_id}/artifacts/{type} | 200 已发布展示 JSON |

创建请求必须是 multipart/form-data，唯一字段为 `file`，只允许一个非空 PDF，最大 25 MiB。重复同名字段、额外字段、多文件均拒绝；超过 multipart 解析器数量限制返回 400。请求总字节超过 26 MiB 返回 413。损坏、加密、需要修复、无页面 PDF 返回 422，不接受仅改扩展名的文件。可解析性最终由已有解析器判断，异步解析失败记入任务。

```
curl -F 'file=@examples/MF2033k6lC.pdf' http://localhost:8010/api/runs
```

该命令会实际调用部署配置的模型和检索服务。不要把离线测试执行器当作生产入口。

运行快照字段：run_id、status（pending/running/completed/failed）、stage、completed（阶段标识数组）、started_at（尚未开始时 null）、updated_at（ISO UTC）、error（null 或 code/message）。状态由后台执行与持久化记录产生，无浏览器超时判失败规则。

业务错误结构：`{"detail":{"code":"report_not_ready","message":"报告尚未生成"}}`。multipart 自身的格式／数量解析错误使用 FastAPI 原有 400 detail 字符串；客户端兼容两种格式。

| HTTP | code | 场景 |
| --- | --- | --- |
| 404 | run_not_found / artifact_unknown | 未知 Run／非白名单成果 |
| 413 | file_too_large | 文件或请求超限 |
| 415 | invalid_type | 非 multipart 或非 PDF 扩展名 |
| 422 | single_pdf_required / invalid_pdf | 输入数量或 PDF 无效 |
| 409 | report_not_ready / artifact_not_ready | 产物未发布 |
| 409 | run_failed | 任务失败，无正式报告 |
| 500 | report_read_failed / artifact_read_failed | 产物不可读取 |

任务 error.code：execution_failed（解析／工作流／报告落盘失败）、interrupted（服务重启发现中断）。错误不包含凭据、原始调试文本；详细异常在服务日志。

成果类型固定 novelty_points、search_results、review。列表只给可用性与 revision；展开时请求单项。novelty_points 包含原条目，search_results 为 raw_evidence_cards、accepted_evidence_cards、rejected_evidence 数量，review 为原 reviews 和 phase。阶段快照不等于最终报告。所有 /api/ 响应 no-store，不提供磁盘路径下载入口。
