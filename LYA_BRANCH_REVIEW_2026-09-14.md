# `lya` 远程分支相对当前代码的更新审查

审查时间：2026-09-14
当前分支：`hyl` @ `bdba9c5`（feat: add scripts/run_single_research_task.py for Researcher-level diagnosis，2026-09-12 02:14）
对比目标：`origin/lya` @ `7e624ff`（docs(audit): record ARXIV-ACCESS-01 diagnostics，2026-09-14 14:48）

---

## 0. 摘要（先看这里）

| 项目 | 结论 |
|---|---|
| 领先提交数 | **31 个提交**（`git rev-list --count HEAD..origin/lya`） |
| 落后提交数 | **0**（当前 `hyl` 是 `lya` 的祖先，merge-base = `bdba9c5`） |
| 合并方式 | **fast-forward，无文本冲突**（`git merge-base --is-ancestor HEAD origin/lya` 退出码 0） |
| 代码改动 | 72 个文件，+4852 / −545 行（backend 35、tests 29、scripts 7） |
| 归档产物 | 383 个新增文件，约 7.06 MB（`outputs/` 293、`docs/experiments/` 72、`fixtures/` 3） |
| 本地文件冲突 | 无。383 个新增路径在你磁盘上均不存在，合并不会覆盖任何本地文件 |
| 主要方向 | ① arXiv 检索鲁棒性 ② Reviewer/报告权威性 ③ 运行时身份与诊断 ④ Run A–D 审计归档 |

> **重要前提修正**：你本地的 `origin/lya` 引用此前是**过期**的（停在 `00ea628`，2026-09-07）。
> 原因是 `git fetch` 走 HTTP/2 时连接 github.com 失败（`Failed to connect ... after 21s`），
> 而同一台机器上 HTTP/1.1 完全正常。已用下面命令取回真实引用：
>
> ```powershell
> git -c http.version=HTTP/1.1 fetch origin --prune
> ```
>
> 本次 fetch 同时更新了 `origin/sdq`（`bd5e795` → `82c609a`）。
> 如需长期生效：`git config http.version HTTP/1.1`。

---

## 1. 31 个提交（旧 → 新）

| # | Commit | 时间 | 主题 |
|---|---|---|---|
| 1 | `20e0827` | 09-13 21:14 | chore: date experiment output directory |
| 2 | `64f1ba6` | 09-13 21:30 | merge: integrate origin/hyl into lya（把 hyl 合进 lya） |
| 3 | `3c0ffc1` | 09-14 01:29 | feat(runtime): unify entrypoint debug lifecycle and diagnostics |
| 4 | `4e8eea3` | 09-14 01:32 | docs(runtime): add diagnostic artifact sample |
| 5 | `0b3c266` | 09-14 02:03 | chore(experiment): freeze paper-input baseline for run-a |
| 6 | `44a9fb8` | 09-14 02:43 | docs(debug): establish run-a failure baseline and repair backlog |
| 7 | `430ac9b` | 09-14 03:03 | fix(workflow): require reviewer for standard full pipelines |
| 8 | `1158131` | 09-14 04:07 | fix(search): propagate database execution failures to tool status |
| 9 | `f800449` | 09-14 05:05 | fix(report): bind reviewer verdicts into final report |
| 10 | `c9a5fab` | 09-14 06:45 | docs(audit): record phase 3 run B closure |
| 11 | `a8f89da` | 09-14 07:59 | chore(git): track runtime audit archives |
| 12 | `83a37c8` | 09-14 08:00 | docs(experiment): archive MG19333vrw DeepSeek run |
| 13 | `caddf21` | 09-14 08:03 | docs(runtime): archive previously ignored audit artifacts |
| 14 | `4433d6c` | 09-14 08:15 | docs(runtime): audit failed database search timeline |
| 15 | `3f8b326` | 09-14 11:39 | fix(search): move sync retrieval io off event loop |
| 16 | `672ea75` | 09-14 11:40 | fix(search): stop query fallback on provider failure |
| 17 | `0f239b9` | 09-14 11:46 | fix(arxiv): bound retries and add circuit breaker |
| 18 | `d479ad8` | 09-14 12:28 | docs(perf): record arxiv retrieval regression validation |
| 19 | `621dcea` | 09-14 12:45 | docs(runtime): upload PERF-001 Run C debug artifacts |
| 20 | `9726a35` | 09-14 13:17 | fix(planner): enforce model options and fail on missing search plans |
| 21 | `9dda3fb` | 09-14 13:28 | fix(entrypoint): isolate numbered runs and require reference bootstrap |
| 22 | `a0b0b75` | 09-14 13:29 | fix(harness): keep serial tool-call history protocol-valid |
| 23 | `b55e488` | 09-14 14:03 | docs(audit): record run D retrieval evidence funnel |
| 24 | `ca351b9` | 09-14 14:05 | docs(runtime): upload Run D debug artifacts |
| 25 | `beef156` | 09-14 14:24 | fix(arxiv): serialize provider search lifecycles |
| 26 | `9117eba` | 09-14 14:26 | fix(bootstrap): offload synchronous provider calls |
| 27 | `d6f5596` | 09-14 14:32 | test(arxiv): add layered access and recall smoke |
| 28 | `479402c` | 09-14 14:32 | docs(audit): record ARXIV-RATE-01 smoke outcome |
| 29 | `3ff1495` | 09-14 14:34 | fix(arxiv): share request gate across provider capabilities |
| 30 | `d8503d9` | 09-14 14:46 | fix(smoke): use id_list for known arxiv ids |
| 31 | `7e624ff` | 09-14 14:48 | docs(audit): record ARXIV-ACCESS-01 diagnostics |

作者均为 `lya3106643285`；`hyl` 侧作者为 `Vazriat`。**`lya` 已把 `hyl` 全部合入（第 2 条），所以不存在「lya 缺少当前代码内容」的情况，只有单向领先。**

---

## 2. 代码更新明细

### 2.1 arXiv / 数据库检索鲁棒性（9 个提交）

| 提交 | 旧行为 | 新行为 |
|---|---|---|
| `3f8b326` | `structured_retrieval._resolve()` 里同步 provider 的阻塞 I/O 直接跑在 event loop 线程上 | 改为 `_invoke_provider()`：协程在 loop 上 await，同步函数走 `asyncio.to_thread`（search / metadata / full_text 三处） |
| `9117eba` | `reference_bootstrap._await()` 同样把同步 `resolve_identifier` / `search_known_item` 压在 loop 上 | 复用 `_invoke_provider()`，bootstrap 不再阻塞事件循环 |
| `672ea75` | provider 抛错后只记一条 FAILED，继续跑完整条 query 放宽链 | 捕获异常即 `provider_failed = True; break`，失败的外层调用只产生 1 条 FAILED `SearchExecution` |
| `0f239b9` | 无熔断、无总预算；传输异常（ReadTimeout/ConnectError）**不重试**直接抛；Retry-After 上限 60 s | 新增 `ArxivCircuitOpenError` / `ArxivRetryBudgetExceeded`、可重试传输异常集合、`_retry_delay(..., max_delay=)`、线程安全熔断器（half-open 探针）；`_get` 用 `deadline` 统一约束重试预算 |
| `1158131` | 内部 search execution 全失败时，外层工具仍返回 `succeeded=true` + 空结果，Runtime 记为 `SUCCESS/EMPTY` | 新增 `_summarize_search_executions()`；`all_failed` / `no_execution` → `succeeded=False` 并带 `error`；degraded 时追加 warning；`researcher_registry` 对 failed+payload 观测改用工具 projector，保留 `execution_summary` |
| `beef156` | 多个 `ArxivSearchTool` 实例可同时在途 | 新增进程级 `_REQUEST_GATE`，整个 `_get`（熔断检查 → 限速 → HTTP → backoff → 重试）独占 gate |
| `3ff1495` | Metadata / FullText 的 HTTP 绕过限速 | 两者也进同一 gate（Search 持整条重试生命周期，Metadata/FullText 各持单次 HTTP） |
| `d6f5596` / `d8503d9` | 无分层 smoke；Case A 用 `search_query=id:1706.03762` | 新增 `experiments/arxiv_rate_smoke.py` + `scripts/arxiv_rate_smoke.py`，分层判定 HTTP → Atom → entry → 命中；Case A 改用官方 `id_list` |

新增配置项（`config/factory.py` + `researcher.example.json`）：
`max_retry_delay_seconds=5`、`retry_budget_seconds=45`、`circuit_failure_threshold=2`、`circuit_cooldown_seconds=60`；
legacy 适配里 `max_retries` 默认 **2 → 1**，example 配置 `4 → 1`。
效果（PERF-001 Run C）：失败 outer call 的 6 次 fallback timeout 消失，熔断后毫秒级 fast-fail，总时长 `1362.5 s → 183.2 s`（−86.6%）。

### 2.2 工作流 / 报告 / Reviewer / Planner（3 个提交）

- **`f800449` 报告绑定（新增 `core/report_binding.py`）**：`bind_reviews_to_report()` 用 Reviewer 的实际裁定覆写每个 point 的 5 个判定字段（`review_status` / `verdict` / `verdict_reason` / `confidence` / `highly_relevant_works`），保留 `summary` 与卡片引用。覆盖不齐（missing / duplicate / unknown review|conclusion）直接抛 `ValueError`，被包成 `WorkflowExecutionError` —— **裁定缺失是致命失败，不再静默降级**。`evidence_cards` 参数目前预留未实现。
  - `schemas/domain.py`：`ConclusionLevel` 枚举**被删除**（当前 HEAD 有 15 处引用，lya 上为 0）；`NoveltyConclusion` 改为携带 `review_status`（必填）+ 可选 `verdict/verdict_reason/confidence` + 新增 `highly_relevant_works`。
  - `core/integrity_gates.py`：`validate_report_integrity()` 新增**必填** `novelty_reviews`；`ReportIntegrityResult` 新增 5 个无默认值字段（`review_count/conclusion_count/matched_count/mismatch_count/mismatched_point_ids`）；逐字段比对，漂移会产生 `review/conclusion mismatch: <id> fields=...`。
  - `tools/renderer.py`：结论标签由 `strong/partial/weak/insufficient` 换成 `novel/partially_novel/not_novel` +「证据不足，无法裁定」，新增「裁定理由 / 置信度 / 高度相关 Work」区块。
- **`430ac9b` 标准入口强制 Reviewer**：`ReviewerConfig.enabled` 默认 **False → True**；新增 `ReviewerRequiredError`（`code="reviewer_required"`）与 `config.factory.build_standard_full_workflow()`，对 `run_full_workflow_live.py` 与 `run_full_pipeline_experiment.py` 三个分支 fail-fast（配置缺失 / `enabled=false` / 装配出 None），且发生在 MinerU 与 bootstrap **之前**。旧的 `build_workflow()` 不强制。
- **`9726a35` Planner fail-closed**：新增 `SearchPlannerExhaustedError`（带 `audit` dict 与 `failure_category`）；`_require_complete_search_plans()` 在 fan-out 前校验 SearchPlan 完整性，缺失/多余/重复 → `WorkflowExecutionError`，run manifest 记 FAILED；不再静默丢 Task。
  - 注意：提交标题里的 “enforce model options” **没有对应校验代码改动**；实际改动是新增模型 profile `deepseek-official-flash`（`https://api.deepseek.com`，`deepseek-v4-flash`，`DEEPSEEK_API_KEY`，`supported_params: ["enable_thinking"]`），使 `enable_thinking` 能通过白名单过滤进入 payload。

### 2.3 运行时 / 入口 / 诊断 / Harness（4 个提交）

- **`core/run_identity.py`（新增）**：`file_run_identity(entrypoint, paper_json, ...)` 输出 `{entrypoint, input_identity:{paper_json(仓库相对), paper_sha256, point/task/search_plan id}}`，写进 manifest / summary / summary.md，用于回答「这次跑的是哪个入口、哪份输入、输入是否被改过」。
- **运行隔离**：`scripts/run_full_workflow_live.py::allocate_run_directory` 用原子 `mkdir(exist_ok=False)` 预留 `outputs/runs/NNNN`；`run_single_research_task.py::new_run_id` 由 `single-{language}-{epoch秒}`（同秒会撞目录）改为 `single-<task>-<UTC>-<uuid8>`，且 request 与 runtime 使用同一 run_id。
- **`processing/paper_input_bootstrap.py`（新增）**：校验 / 刷新共享稳定引用缓存（条件：paper_id + `references_digest` + 条目数 + `bootstrap_ready`），失败抛 `PaperInputReferenceBootstrapError`；随后把稳定缓存**快照**进 run 目录并复验（缓存共享、运行隔离）。唯一生产调用点是 `run_full_workflow_live.py`。
- **`core/tool_call_harness.py`（`a0b0b75`）**：旧代码先把带**全部** tool_calls 的 assistant 消息写进 history，再截断为只执行第一个 → 下一轮请求里 `call_2..N` 没有对应 tool 响应，OpenAI 兼容端 400。新代码在构造 assistant 消息**之前**截断，被丢弃的 id 只留在 `SERIAL_FIRST_CALL` 审计事件里。
- **诊断**：新增 `diagnostics/{contracts,reader_failures,workspace_diagnostics}.py`；`finish_run` 自动产出 `diagnostics/{reader,reference_namespace,reviewer}.json`（状态词表 `OK/WARNING/ERROR/INCOMPLETE`），诊断异常**绝不改变业务终态**；`scripts/reader_failure_diagnostics.py` 由自带分类逻辑的大脚本（−207 行）变薄为 CLI 包装，报告改为 per-run，三个诊断 CLI 新增 `--run-id`。
  - 注意：`git grep '"--debug"' origin/lya` **无命中** —— 并不存在 `--debug` 开关，生命周期由 `runtime_debug.enabled`（默认 True）驱动。

### 2.4 归档文档与产物（14 个提交，含 1 个 merge）

- 新增 383 个文件 / 约 7.06 MB：`outputs/runs` 176 个（3.53 MB）、`outputs/MG19333vrw-debug-full-20260907` 117 个（3.00 MB）、`docs/experiments` 72 个（0.47 MB）、`fixtures/experiments/run_a` 3 个。
- `.gitignore` 变化：**取消**忽略 `docs/experiments/runtime/`（改为归档精简 Runtime 审计产物），完整过程文件仍留在被忽略的 `outputs/<paper_id>/`；`outputs/` 下的产物是 `git add -f` 强制加入的。
- 主要审计文档：`docs/experiments/Run_A_Baseline_2026-09-14/`（6 篇）、`Run_B_Phase3_Closure_2026-09-14/`、`PERF001_arXiv_Search_Performance_2026-09-14/`、`Run_D_Retrieval_Evidence_Funnel_2026-09-14/`、`ARXIV_RATE_01_2026-09-14/`、`ARXIV_ACCESS_01_2026-09-14/`、`Runtime_Debug_Diagnostics_Sample_20260913/`、`Run_A_PaperInput_Fixture_2026-09-13.md`。

---

## 3. 审计结论链（文档自述结论）

| 实验 | 结论 |
|---|---|
| Run A 基线 | 30 个内部 search execution（25 timeout + 5 × HTTP 429）；**CONFIRMED**：内部全失败时外层工具仍报 `SUCCESS/EMPTY`；`reference_search` 每任务上限 4 被耗尽；Reviewer 因 `reviewer.enabled=false` 完全未执行（占位 `insufficient_evidence`）→ 形成 BUG-001/002/003 与 Phase 2 Backlog |
| Run B（Phase 3 P0 闭环） | **PASS**：Reviewer 真实执行、`database_search` 状态真实、Reviewer 裁定完整进入 Final Report 且 Renderer 只依据 Final Report；最终阶段 `render_report`，Integrity Gate 无裁定漂移；耗时约 53 分 17 秒 |
| Run C（PERF-001） | **PASS（结构性关闭）**：同步 I/O 移出 loop、失败不再触发语义 fallback、重试有界且熔断能 fast-fail；总时长下降 86.56% |
| Run D（检索→Reader→证据漏斗） | 完整性与隔离性 **PASS**（3 Point → 6 Task → 6 SearchPlan → 6 run_research_task，无静默丢任务、0 次 Harness HTTP 400）；业务证据闭环 **BLOCKED BY PROVIDER / EMPTY CORPUS**：6 个任务全部在 retrieval hit 层归零，arXiv 成功检索 0 次（`429 / ReadTimeout / CircuitOpen`），0 Artifact → 0 EvidenceCard。明确「归零是漏斗计数，不是 arXiv 零召回结论」 |
| ARXIV-RATE-01 | provider access = FAIL；structured query recall = NOT_MEASURED；query 层修复 NOT ALLOWED；Run E NOT RUN |
| ARXIV-ACCESS-01 | 排除环境代理问题与底层网络问题（httpx/curl、默认代理/强制直连、普通页面与 known-ID export API 均 200）；**服务端限流 YES**（观测到 429）；known-ID access PASS；exact-title access FAIL（ReadTimeout）；structured-query recall NOT_MEASURED；Run E NOT ALLOWED |

净结论：**当前系统的证据瓶颈在 arXiv provider 访问（限流/超时），不在 Reader 与 Evidence 生成**；代码侧的检索鲁棒性、运行隔离、裁定权威性、诊断能力均已落地并有审计归档。

---

## 4. 合并前必读：破坏性与行为变更

1. **CLI 破坏——`scripts/run_full_workflow_live.py`**：`--output` 被删除，新增 `--runs-root`（默认 `outputs/runs`）/`--run-number`/`--force-reference-bootstrap`；产物从 `outputs/<paper_id>/…`（就地覆盖）变为 `outputs/runs/NNNN/<paper_id>/…`，结果写入 `run_dir/result.json`，并生成 `run.json`（RUNNING → SUCCESS/FAILED/INTERRUPTED）。旧的 `--output` 调用会直接 argparse 退出。
2. **CLI 破坏——`scripts/run_single_research_task.py`**：`--paper-id` / `--language` 删除，改为必需 `--paper-json` / `--point-id` / `--task-id`（point、task、SearchPlan 必须各精确匹配一次）；退出码语义新增 1/2。
3. **CLI 破坏——`scripts/reader_failure_diagnostics.py`**：`inspect_workspace()` 返回值由顶层 `counts/classification_counts/verdict(字符串)/failures/status` 变为 `{workspace, ok, runs:[...]}`；`classification → reason_code`、`verdict` 变 dict、`counts.reader_failures → counts.failed`、`classification_counts` 不再含 `SUCCEEDED`；私有 helper `_load_json/_artifact_ids/_document_ids/_reader_calls/_verdict` 已删除。
4. **Python API 破坏**：`ConclusionLevel` 枚举删除；`NoveltyConclusion` 字段改写；`Coordinator.synthesize()` / `DemoCoordinator.synthesize()` 新增必填关键字 `novelty_reviews`；`validate_report_integrity()` 新增必填关键字 `novelty_reviews`，`ReportIntegrityResult` 新增 5 个无默认值字段；自定义 `ReportRenderer` 子类必须接受第 4 个参数 `output_root`。
5. **装配语义变化**：`ReviewerConfig.enabled` 默认变 `True`（默认装配会真的调用 Reviewer，增加 LLM 调用与耗时）；标准完整入口必须走 `build_standard_full_workflow()`，否则会在 MinerU/bootstrap 之前抛 `ReviewerRequiredError(code="reviewer_required")`。
6. **产物根目录变化**：业务产物（points / research results / reviews / report / render）现在跟随 `runtime_debug.output_root`（`NoveltyWorkflow(output_root=...)`），不再固定写 `outputs/`；配置了非默认 `output_root` 的调用方产物会换目录。
7. **检索语义变化**：`max_retries` 默认 2→1；Retry-After 上限 60 s→5 s（服务端返回 `Retry-After: 30` 时新代码只等 5 s 就重试，可能延长 429，但 2 次失败即熔断 60 s）；provider 失败不再继续 query 放宽链；「0 个 search execution」由空成功变为**工具失败**（`no_search_execution`）。
8. **私有 API 变化**：`_MAX_RETRY_DELAY_SECONDS` 删除；`_retry_delay(response, attempt)` 现需 `max_delay=`；`ArxivSearchTool._throttle()` 现需 `deadline=`；`processing/reference_bootstrap.py` 跨模块依赖 `structured_retrieval._invoke_provider`（私有）。
9. **其他注意点**：`_REQUEST_GATE` 非重入且无获取超时（gate 内再调 `_get`/`_try_get` 会死锁，当前三处调用点已核对互不嵌套）；熔断器是**实例级**而 gate/throttle 是**进程级**（不要误读为全局熔断）；4xx 会被计为「provider 健康」并清零失败计数；`docs/experiments/Runtime_Debug_Diagnostics_Sample_20260913/sample-fixed/` 是早于 `3c0ffc1` 的样例（里面 `reader_failures`/`WARN`/`PARTIAL` 与现行代码 `reader`/`WARNING`/无 `PARTIAL` 不一致，且全仓无引用）。

---

## 5. 合并安全检查（已实测）

- `git merge-base --is-ancestor HEAD origin/lya` → 0：**可 fast-forward，无冲突**。
- 383 个新增路径在你磁盘上**均不存在**（`Test-Path` 逐个核对），因此不会覆盖本地文件。
- 你现有的 7 个未跟踪目录（`docs/experiments/*FullPipelineLive*`）与 lya 新增路径**零交集**。
- 附带实测提醒：git 在 fast-forward 时**会静默覆盖**已存在的被忽略文件（如 `outputs/` 下的本地结果）；本次因无同路径文件，无风险。合并前若要保险，可先提交或备份 `outputs/`。

## 6. 未验证事项

- **未运行任何测试**：本机仅有 Python 3.14（`C:\Python314`），**未安装 pytest，也未安装本包**，所以 `lya` 的测试套件未执行；文中「PASS/通过」均为文档与提交自述，非本次实测。
- 文档自述存在一个与本次改动无关的既存失败 `tests/test_browser_playwright.py::test_fetch_collects_rendered_content_and_applies_limits`。
- `ArxivRetryBudgetExceeded` 在测试中从未被触发或断言（全仓仅命中定义与 `_budget_error`）。
- 未核对 httpx per-phase timeout 语义与 `asyncio.to_thread` 线程池上限，故「gate 持有时间 ≤ retry_budget_seconds」未严格证明。
- `agents/research.py` 的 `_build_evidence_pack` 仍是同步直调（未走 offload），判断为遗留路径，未验证是否存在仓库外调用者。

## 7. 建议的下一步

```powershell
# 1) 以后 fetch 都带上 HTTP/1.1（或一次性写入配置）
git config http.version HTTP/1.1
git fetch origin --prune

# 2) 因为 hyl ⊂ lya，合并就是 fast-forward
git merge --ff-only origin/lya          # 当前在 hyl 上执行

# 3) 若要让本地 lya 分支跟上（目前落后 48 个提交）
git checkout lya && git merge --ff-only origin/lya
```

合并后若要让标准入口继续可用：确认 `reviewer.enabled=true`（否则 `run_full_workflow_live.py` / `run_full_pipeline_experiment.py` 会立即 fail-fast），并把调用脚本从 `--output` 迁移到 `--runs-root`（必要时 `--run-number`）。

另注：仓库中仍存在一个 2026-08-29 创建的 stash（`stash@{0} On lya: wip: tool_call_harness changes before switching to hyl`），基于很旧的 `6dcf234`，其 `tool_call_harness.py` 改动与 `a0b0b75` 不重叠，本次未处理。

---

## 8. 合并执行记录（已完成）

执行命令与结果：

```powershell
git -c http.version=HTTP/1.1 fetch origin --prune    # origin/lya: 00ea628 -> 7e624ff
git merge --ff-only origin/lya                       # Fast-forward, exit 0
```

| 校验项 | 结果 |
|---|---|
| 合并后 `hyl` | `7e624ff`（= `origin/lya`），`git rev-list --left-right --count hyl...origin/lya` = `0 0` |
| 合并方式 | fast-forward，**无冲突**；回滚点 `bdba9c5`（仍在 `origin/hyl` 上，`git reset --hard bdba9c5` 可撤销） |
| 新增被跟踪文件 | 383 个，磁盘约 7.97 MB |
| 关键新文件落盘 | `core/run_identity.py`、`core/report_binding.py`、`processing/paper_input_bootstrap.py`、`diagnostics/reader_failures.py`、`experiments/arxiv_rate_smoke.py`、`scripts/arxiv_rate_smoke.py` 等均已存在 |
| 工作区状态 | 被跟踪文件无改动（`git status --porcelain -uno` 为空）；原有未跟踪目录 `docs/experiments/*FullPipelineLive*` 未受影响 |
| 本地文件覆盖 | 无（383 个新增路径在合并前均不存在于磁盘） |
| 语法体检 | `python -m compileall -q backend/src scripts tests` → 退出码 0（全部通过） |
| 行尾（CRLF）影响 | `core.autocrlf=true` 且无 `.gitattributes`，新检出的文本文件在磁盘上为 CRLF；但归档产物中 44 处 `path + sha256` 引用**全部是协作者机器的绝对路径**（`/home/lya3106643285/...`），本地可验证的相对引用为 **0**，因此没有破坏任何归档校验值 |

合并后仍待处理：
1. `hyl` 领先 `origin/hyl` 31 个提交，如需发布：`git push origin hyl`（尚未执行）。
2. 本地 `lya` 分支仍是旧的 `00ea628`（落后 `origin/lya` 48 个提交）：`git checkout lya && git merge --ff-only origin/lya`。
3. 本机只有 Python 3.14，未安装 pytest 与项目依赖，**测试套件未运行**；上面的 compileall 只验证语法，不验证行为。
4. 本文件（`LYA_BRANCH_REVIEW_2026-09-14.md`）仍是未跟踪文件，未随合并提交。
