# 前端架构与 Phase 0 核查

## 分支与既有目录

2026-09-17 开始时分支为 `lya`，HEAD 为 `00205761c864d1242a6a5685102d291648798a75`。按任务书从该 HEAD 新建 `frontend`。已有后端查新稳定化改动未提交，原样保留；实施期间共享工作区出现提交 `b0a25f4`（Stabilize v0.1 retrieval and archive two release regressions），未重置或覆盖该提交。本任务提交只包含 Web 接入、frontend、测试和文档。

`frontend/` 原来只有“未来交互层预留”README，无可复用脚手架。增量补齐 Vite + 原生 TypeScript，保留 README 中原有联调 API 的说明并澄清其用途。未新增顶级 web/，未嵌套 frontend/。后端已有 `web/__init__.py` 的兼容导出保留。

## 实际接入链路

`main.create_app` 保留 `/api/novelty/*` JSON 联调接口，新增 `/api/runs` PDF 产品接口，并在存在构建目录时托管 `frontend/dist/`。

`web.runner.execute` 调用：

1. `processing.paper_processor.DefaultPaperProcessor.process`：按项目配置装配 MinerU、OCR 与标题模型；复用文本层／OCR 回退。
2. `to_paper_input` 生成现有 PaperInput；无有效文本即失败。
3. `prepare_paper_input_references` 准备独立运行的参考文献快照。
4. `config.factory.build_standard_full_workflow`，强制现有 Reviewer 装配约束。
5. `NoveltyWorkflow.run`，由既有图执行与 Renderer 输出 Markdown。

生产接口从不使用 `NoveltyWorkflow.default()` Demo。离线集成测试明确替换为 Demo agents，并且不等同于真实模型验收。没有修改任何核心 Agent、工作流文件或业务结论。

## 标识与存储

Web Run 使用随机 `run-<uuid hex>`；Paper 使用 PDF SHA256 的前 24 位。重复同一论文的 Paper 标识相同，但 Run 和目录不同。工作流内部另外生成 runtime run_id，`run_identity.web_run_id` 关联外部 Run；内部 ResearchTask 标识不用于 HTTP 查询。

```
outputs/web-runs/<web_run_id>/
  input.pdf                 # 不使用原始文件名
  run.json                  # 原子更新的运行状态
  references/               # 本轮参考文献准备区
  parser/                   # 本轮 MinerU 工作区
  outputs/<paper_id>/        # 现有 persistence 的真实产物
    novelty-points.json
    evidence-cards.json
    novelty-reviews.json
    report/<paper_id>-report.md
    runtime/<internal_run_id>/...
  novelty_points.json       # 节点完成后发布的展示快照
  search_results.json       # 三项证据数量
  review.json               # 原裁定与 phase
  report.md                 # 既有 Renderer 产物的原字节副本
```

报告路径来自 `last_rendered_report_path`，并校验位于本轮目录内。只有工作流返回且报告非空后才标记 completed。预览和下载都读取同一个 `report.md`。解析／执行异常不把内部凭据或路径直接返回浏览器，部署者按 run_id 查看服务日志。

## 状态和发布映射

适配器观察已有 `_record_stage` 包装的节点进入／成功返回，然后复用 `_build_graph` 构造同一套图；没有复制节点或边。该内部接口若变更，需同时维护适配器及离线集成测试。

| 来源 | 展示阶段／发布 |
| --- | --- |
| 上传接收成功 | input 完成 |
| PDF processor 执行 | parse |
| 参考文献准备、规划、检索、补检 | research |
| extract_points | novelty_points；返回后发布 novelty-points.json |
| review_evidence 及证据门控 | review；返回后发布 evidence-cards 数量、novelty-reviews 原裁定 |
| synthesize_report、完整性校验、persist_report、render_report | render |

阶段可回退；completed 表示本轮至少完成过该阶段，并非强制线性进度条。阶段成果以白名单选择字段、原子替换快照，带 revision；绝不直接读取正在写入的内部文件。成果发布失败只记录日志，不阻塞报告。review 中证据不足、告警保持原意。

## 生命周期及边界

一个服务进程、一个线程执行器，按接收顺序串行执行；浏览器断开不影响执行。run.json 跨刷新／重启保留。进程启动时把遗留 pending/running 标记 failed/interrupted，不支持断点续跑。禁止多个 Uvicorn worker 或多个实例共用同一个 Run 根目录。正常停机等待任务退出，强制停机后由下一次启动处理遗留任务。

单 PDF 上限固定 25 MiB；请求总量另限 26 MiB（包含 multipart 开销）。后端验证字段数量、扩展名、PDF 头、PyMuPDF 可打开、非空页、非加密、非修复文件；MIME 不是最终判断依据。深层解析失败在 Run 中报告失败。

部署范围为本机／受控网络单用户工具。公网多用户认证、配额、任务取消、断点续跑、分布式队列均未引入。服务器 HTTPS 需已有访问控制的反向代理，不能将本工具当作无保护公共上传服务。
