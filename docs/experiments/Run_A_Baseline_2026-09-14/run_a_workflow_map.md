# Run A：Workflow 运行地图

## 冻结条件

- Run ID：`run-a27befb0e6b445778d8c3422fd4f71f6`
- Git commit：`0b3c266c9c6fcd445fecb1c45cb00e4a90a4e7a9`
- Entrypoint：`paper_input`
- PaperInput：`backups/MF2033k6lC/v2/paper-input/others/paper.json`
- PaperInput SHA-256：`89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66`
- 配置快照：`fixtures/experiments/run_a/effective-config.json`
- 命令：`scripts/run_full_workflow_live.py --paper-json backups/MF2033k6lC/v2/paper-input/others/paper.json --output outputs/MF2033k6lC/run-a-result.json --max-rounds 1 --max-concurrency 1`
- 起止时间：`2026-09-13T18:05:13Z` ～ `2026-09-13T18:32:56Z`
- 总耗时：1,663,184 ms（约 27 分 43 秒）
- 进程退出码：0；Runtime terminal status：`SUCCESS`
- Runtime：`outputs/MF2033k6lC/runtime/run-a27befb0e6b445778d8c3422fd4f71f6/`

Run A 只执行了一次，未调用 MinerU，运行期间未修改代码、Prompt、配置或输入。
冻结元数据中的 `git_commit=4e8eea3...` 表示冻结前的业务代码基线；实际运行
manifest 固定为随后只增加 fixture 元数据的 `0b3c266...`，两者之间没有业务
代码、Prompt 或配置差异。所有 Run A Evidence 以 manifest 的 commit 为准。

## Stage 地图

这里的 `PARTIAL` 是业务语义，不改写 Runtime stage 的 `SUCCESS`：节点正常返回，但其输出明显退化。

| Stage / Check | Result | Runtime evidence / 说明 |
|---|---|---|
| Workflow 正常结束 | PASS | CLI 退出 0，完整返回 `NoveltyRunResult` |
| Runtime terminal status | PASS | `manifest.json` / `summary.json`: `SUCCESS` |
| `extract_points` | PASS | stage_0001，334,813 ms，得到 2 个 point |
| `plan` | PASS | stage_0002，得到 4 个 Research Task |
| `dispatch_planning_tasks` | PASS | stage_0003 |
| `plan_research_task` × 4 | PASS | stage_0004～0007，4 个 SearchPlan 均生成 |
| `dispatch_research_tasks` | PASS | stage_0008 |
| `run_research_task` × 4 | PARTIAL | stage_0009～0012；2 completed、2 partial、2 个任务零证据 |
| `validate_evidence` | PASS | stage_0013；6 张原始卡全部保留 |
| `review_evidence` | PARTIAL | stage_0014；Reviewer disabled，仅生成 2 条 insufficient 占位 review |
| `validate_synthesis_input` | PASS | stage_0015；6/6 卡通过 Gate A，0 拒绝 |
| `check_final_evidence_sufficiency` | PASS | stage_0016；NP-1=2、NP-2=4，cut=1 |
| `plan_supplement` | SKIPPED | `max_rounds=1`，记录为 NOT_RUN |
| `synthesize_report` | PARTIAL | stage_0017；成功生成报告，但未消费 review 裁定 |
| `validate_report_integrity` | PASS | stage_0018；2 个结论、6 个 Card 引用闭包通过 |
| `persist_report` | PASS | stage_0019 |
| `render_report` | PASS | stage_0020；Markdown 已生成 |

最后成功 stage 为 `render_report`；没有失败 stage。Runtime 中有 2 个 Tool/Harness 错误，但均被任务级 partial 结果吸收。

## 业务产物

| Artifact | Result | Path |
|---|---|---|
| PaperInput | PASS | `outputs/MF2033k6lC/paper-input/others/paper.json` |
| `novelty-points.json` | PASS | `outputs/MF2033k6lC/novelty-points.json` |
| `retrieval-plans.json` | PASS | `outputs/MF2033k6lC/retrieval-plans.json` |
| `evidence-cards.json` | PARTIAL | 存在；仅英文任务贡献 6 张卡 |
| `novelty-reviews.json` | PARTIAL | 存在；2 条均为 `insufficient_evidence` 占位结果 |
| `report.json` | PARTIAL | 存在；两个结论均为 `strong`，与 review 占位状态语义冲突 |
| Renderer | PASS | `outputs/MF2033k6lC/report/MF2033k6lC-report.md` |
| CLI result | PASS | `outputs/MF2033k6lC/run-a-result.json` |

## Runtime 完整性与索引哈希

Runtime 目录包含 manifest、summary、20 个已执行 stage、1 个 NOT_RUN stage、39 个 Tool Call、49 个 LLM Call、2 个 error 和 3 个 diagnostics。

| File | SHA-256 |
|---|---|
| `manifest.json` | `b7d4309daacf362abf83c1cc0fa48a0149ddefc762f02a604e864e3a93c267d4` |
| `summary.json` | `dd9198a7045531fab659be89fb9bef0b525852dfc8a1e21412d9269051ecb221` |
| `diagnostics/reader.json` | `9329da69e8d245c7ed826c4e66e40c581f4b8ac768b851e6a4815c8fa719155d` |
| `diagnostics/reference_namespace.json` | `5a975b3387c4bbf11ab52d5bd4272e7bfcbd67b5fe971b6202080045a76c93aa` |
| `diagnostics/reviewer.json` | `e532e89941cbfaa54a6fcb0f9513c764646457c5a331880384c7409a2a2a369f` |
| `run-a-result.json` | `20ec08bb97a5c8a935c56986bde6bf85d2f76ac23a103841a1630d851ac89b71` |

模型调用共 49 次，全部成功；总 token 329,034，记录成本 RMB 0.274869，成本完整性为 `COMPLETE`。
