# Minimal integration patch

- File upload now accepts an optional `X-Submission-Id` and binds it to the PDF SHA-256 in the task service. A repeated ID with identical bytes returns the same task without another background workflow; a different file returns 409. The browser sends one random ID per submit intent, disables duplicate clicks, and blocks another submit on an ambiguous network/timeout response.
- The backend explicitly rejects multiple or extra multipart parts; existing extension, MIME, empty file, signature and size checks remain in place.
- The structured report fallback now treats `semantic_evidence` as a completed evidence-insufficient judgment, while budget/technical/material failures remain unfinished. A completed workflow with unfinished point reviews displays that partial state on the completion screen.
- Progress now follows the actual callback stage when a supplement loops to planning/research; the page shows the round on these stages rather than pinning the older validation stage.
- A task-local model budget hook records request hash, maximum output, reserved RMB and later usage estimate before each model transport. It refuses dispatch after the configured cap/attempt limit or when a priced model lacks a finite `max_tokens`. It does not release unknown/cancelled reservations. The real Web service activates it only when `NOVELTY_RUN_MODEL_BUDGET_RMB` is set; no live cap was set in this preflight.
- Added a browser-only historical report replay test using the real archived Markdown. The test explicitly labels the screenshot as a replay and asserts zero new business POSTs; this is not a production archive endpoint.

No prompt, research source, Reviewer semantic rule, sampling parameter or per-paper branch was changed. Local tests and build commands are in `preflight/commands.txt`.

## 真实运行结果（冻结代码未变）

预检后以冻结版本和 15 元 / 80 次请求上限启动了一次模式 A 运行。没有追加产品代码修改。运行至报告合成时，Coordinator 两次 4096 内容 token 截断导致 JSON 解析失败；本轮只归档诊断，不热改 Prompt/输出上限，也不新建第二次付费 run。后续若修此问题，应单列任务、重新估算模型预算，并在新批准范围内验证，不能将本轮失败产物改记为成功。
