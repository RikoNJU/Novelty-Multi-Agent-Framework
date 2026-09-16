# 论文查新框架扩展层

该目录参考睿文智评对后端资源进行分类。Multi-Agent 核心位于 `backend/src/novelty_agent_framework/`，并在包内继续拆分 Agent、模型、工作流、接口和适配器。

```powershell
conda activate langgraph
cd D:\novelty-multi-agent-framework
pip install -e ".[web]"
python -m novelty_agent_framework.main
```

- API 文档：`http://localhost:8010/docs`
- 健康检查：`GET /api/novelty/health`
- 提交结构化任务：`POST /api/novelty/runs`
- 上传论文 PDF：`POST /api/novelty/runs/files`（multipart `paper`）
- 查询任务：`GET /api/novelty/runs/{task_id}`
- 读取报告：`GET /api/novelty/runs/{task_id}/report`

Web 服务默认使用真实工作流；缺少模型凭据时健康检查返回 `degraded`，提交接口返回 503，不会静默回退 Demo。开发测试可显式设置 `NOVELTY_WORKFLOW_MODE=demo`。可通过 `.env.example` 修改监听地址、端口、CORS、任务目录及 30 MB 上传限额。

当前只接收一篇主论文 PDF。参考文献上传字段会返回 `references_not_supported`；前端保留禁用入口。文件通过扩展名、MIME、空文件、大小和 PDF 签名校验后保存到 `outputs/web-runs/<task_id>/`，工作流输出与 Markdown 报告按任务隔离。

任务状态暂时保存在进程内，服务重启后不可恢复；当前适用于单机首版，不适用于多实例生产部署。真实运行还需要模型凭据、访问模型与 arXiv 的网络权限，以及论文内容外发授权。
