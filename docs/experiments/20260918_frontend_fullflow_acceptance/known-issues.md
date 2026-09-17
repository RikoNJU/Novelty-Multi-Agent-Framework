# Known issues and limits

1. The previous Reviewer acceptance still contains possible absence-to-contradiction overclaims on the S1 graph partitioning case. This integration patch does not alter those model judgments or declare them correct.
2. The page's `/api/novelty` task store is in memory; a backend restart invalidates its task IDs. The separate `/api/runs` persistent stack is not the current page contract.
3. The page shows aggregate progress and report but has no `/api/novelty` stage-artifact detail endpoint. No stage business content was verified in the product page. The separate `/api/runs/.../artifacts` endpoint cannot be assumed compatible.
4. The historical browser replay used an explicit test route intercept. The connected browser + real backend run, normal PDF parsing, retrieval, Reviewer and final report were not exercised.
5. The optional Web model budget covers requests through the shared model client. MinerU's local subprocess and any external parser pricing have not been established; model usage estimates are not invoices. A live trial requires an explicit new budget and parser-cost decision.
6. On ambiguous POST failure, the current page blocks another submit until navigation; it cannot recover the task ID after a lost first response. The backend idempotency key prevents duplicate execution only when the same ID is reused during the same service lifetime.
7. The candidate demo computer, production same-origin proxy, backend restart behavior under a paid run, and live browser download were not tested. Cached Chromium plus temporary shared libraries enabled local test-browser preflight only.

8. Automatic approval rejected the first browser observer launch before any POST. It requires explicit consent for PDF-derived text sent to SiliconFlow and enabled retrieval services; no alternative route was attempted.

## 单次真实运行后增补

9. 本轮已获一次 PDF 实际调用与必要外部传输授权，run `feabea311a0d4014bd4c9015491caf1b` 已执行并失败；上文第 4、5、7、8 项的“尚未执行/等待授权”仅描述预检当时状态，以 [report.md](report.md) 的终态为准。
10. Coordinator 报告合成两次响应都在 4096 内容 token 边界截断，合法 JSON 未生成；`render_report` 未运行。不能用已落盘的 Reviewer 中间结果代替正式报告。
11. 本轮 Springer 查询有 5 次 HTTP 404，计划表另有 25 条 `not_run`；不得并作“零命中”。
12. 页面失败态准确，但仅给通用 `workflow_failed` 信息；真实异常仅在 Runtime 中可见。页面阶段字段为聚合 `render_report`，实际失败节点是 `synthesize_report`。
13. 模型 usage 费用仅为本地估算，服务商账单未核对；本地 MinerU 未观察到额外收费解析请求，外部解析费用未证明为零。
