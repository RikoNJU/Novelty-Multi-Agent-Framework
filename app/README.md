# 论文查新框架扩展层

该目录参考睿文智评对 Prompt、配置、适配器和接口资源进行分类。Multi-Agent 核心位于 `src/novelty_agent_framework/`，这里提供可选的 FastAPI 调用方式。

```powershell
conda activate langgraph
cd D:\novelty-multi-agent-framework
pip install -e ".[web]"
python -m app.backend.main
```

- API 文档：`http://localhost:8010/docs`
- 健康检查：`GET /api/novelty/health`
- 提交任务：`POST /api/novelty/runs`
- 查询任务：`GET /api/novelty/runs/{task_id}`

该接口只用于框架联调。可通过 `.env.example` 修改监听地址、端口和 CORS；任务状态暂时保存在进程内。
