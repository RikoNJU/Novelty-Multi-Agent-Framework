# Run D：Retrieval → Reader → Evidence Funnel 审计

日期：2026-09-14
任务书：`task/Part1_Next_Four_Phases_Planner_Bootstrap_Harness_RunD_Taskbook_2026-09-14.md`

## 1. 结论

Run D 的执行完整性与运行隔离均通过：`3 NoveltyPoint → 6 ResearchTask → 6 SearchPlan → 6 run_research_task`，没有 SearchPlanner 静默丢 Task，也没有 Harness 协议 HTTP 400。Runtime、PaperInput、SubjectReference、研究产物、Report 和 Renderer 全部位于 `outputs/runs/0004/`。

业务证据闭环未形成，但丢失位置已经确定：**6 个 ResearchTask 均在 retrieval hit 层归零**。`reference_search` 的当前 Run namespace 正确，但 bootstrap 的 85 条引用全部因 arXiv provider 故障未解析，故 19 次调用全部 `SUCCESS + EMPTY`；`database_search` 的 9 次真实 arXiv outer call 全部失败，另有 6 次模型选择的 `null_catalog` 调用成功但为空。最终没有 Artifact，Reader 没有可读输入，EvidenceCard 和 Reviewer 可用证据均为 0。

这里的“归零”是漏斗计数，不是 arXiv 零召回结论。Run D 中 arXiv successful search executions 为 0，观测到的是 `429 / ReadTimeout / CircuitOpen`，没有稳定的 `HTTP 200 + EMPTY`；因此 provider access failure 已确认，而 query recall 尚未得到有效测量。

因此本轮判定如下：

- Run D 完整性、隔离性、可审计性：`PASS`；
- PLAN-001 的静默丢任务问题：`CLOSED`；
- PAPERINPUT-REF-01 的入口/namespace/snapshot 合同：`CLOSED`；
- HARNESS-001：本轮 `0 × HTTP 400`，修复的多调用分支由 Phase 3 单测覆盖；
- PERF-001 结构性条件：保持 `PASS`，失败 outer call 没有恢复为 6 次 fallback timeout，熔断后能毫秒级 fast-fail；
- Retrieval 业务结果：`BLOCKED BY PROVIDER / EMPTY CORPUS`；
- Reader 与 Evidence 生成：本轮没有输入，**不得判为自身故障**。

Workflow 的 `SUCCESS` 表示流程完成；报告内三个创新点均明确为 `insufficient_evidence`，与中间故障事实一致，并非“已有充分证据”的业务成功。

## 2. Run 身份与隔离

| 项目 | 值 |
|---|---|
| 逻辑实验 | Run D |
| Run number / 目录 | `4` / `outputs/runs/0004/` |
| Paper ID | `MG19333vrw-debug-full-20260907` |
| Runtime Run ID | `run-2e6371011e074b6a95fe1d7cfbb79afe` |
| 入口 | `paper_input` |
| PaperInput SHA-256 | `183b58191547b78b92ec264d24c1abc5429d1637fbd74bbf7af8f40678cc69f4` |
| Git commit | `a0b0b75714bf3795732618fee228acb42c4a86a7` |
| 模型 | `openai_compatible / deepseek-v4-flash` |
| 最大轮数 / 并发 | `1` / `4` |
| 开始（UTC） | `2026-09-14T05:53:01.847695+00:00` |
| 结束（UTC） | `2026-09-14T05:55:41.454154+00:00` |
| CLI wall-clock | `159.606461 s` |
| Runtime duration | `159,511 ms` |
| Run status | `SUCCESS` |

编号目录只存在本轮新建的 `0004`；固定输入保留在旧 workspace，本轮 PaperInput 和 SubjectReference 均复制为独立快照。当前 Run 的以下路径一致指向 `outputs/runs/0004`：

```text
outputs/runs/0004/run.json
outputs/runs/0004/result.json
outputs/runs/0004/MG19333vrw-debug-full-20260907/paper-input/
outputs/runs/0004/MG19333vrw-debug-full-20260907/subject_references/
outputs/runs/0004/MG19333vrw-debug-full-20260907/references/
outputs/runs/0004/MG19333vrw-debug-full-20260907/research-runs/
outputs/runs/0004/MG19333vrw-debug-full-20260907/runtime/run-2e6371011e074b6a95fe1d7cfbb79afe/
outputs/runs/0004/MG19333vrw-debug-full-20260907/report/
```

## 3. 完整性 Gate

| Gate | 预期 | 实际 | 判定 |
|---|---:|---:|---|
| NoveltyPoints | 3 | 3 | PASS |
| ResearchTasks | 6 | 6 | PASS |
| SearchPlans | 6 | 6 | PASS |
| `run_research_task` stages | 6 | 6 | PASS |
| SearchPlanner silent drop | 0 | 0 | PASS |
| Harness protocol HTTP 400 | 0 | 0 | PASS |
| synthesis/report integrity | PASS | PASS | PASS |

本次 live 输出没有出现多 `tool_calls`，所以没有 dropped-call Runtime 事实；Phase 3 的 0/1/2/3 tool-call 单测负责覆盖 `SERIAL_FIRST_CALL` 分支。Run D 能证明的是 6 条真实研究对话均未再触发 `insufficient tool messages following tool_calls message` 或其他 HTTP 400。

## 4. SearchPlanner 审计

| NP / Task | 语言 | Attempts | Completion tokens | Reasoning tokens | Stage duration |
|---|---|---:|---:|---:|---:|
| NP-1 / T-1 | zh | 1 | 1,888 | 1,587 | 9.029 s |
| NP-1 / T-2 | en | 2 | 3,263 | 2,993 | 16.939 s |
| NP-2 / T-1 | zh | 1 | 1,524 | 1,198 | 6.159 s |
| NP-2 / T-2 | en | 2 | 3,107 | 2,798 | 14.116 s |
| NP-3 / T-1 | zh | 2 | 2,817 | 2,477 | 14.359 s |
| NP-3 / T-2 | en | 3 | 4,418 | 4,096 | 22.816 s |
| **合计** | - | **11** | **17,017** | **15,149** | **83.462 s wall-clock** |

结果为 6/6 SearchPlan，retry 后没有缺项。配置快照显示 `supported_params=["enable_thinking"]` 且 SearchPlanner 的 `enable_thinking=false`，Phase 1 payload-level 测试也证明 `False` 会进入最终请求；但 live provider 仍返回 15,149 reasoning tokens，其中多次达到单次 2,048 token 上限。结论是“本地透传缺失”已修复，但 `deepseek-v4-flash` 没有稳定遵守该开关，不能把任务书中“reasoning 不再大量占用”的验收项判为完全通过。

由于 fail-closed 完整性检查已启用，如果未来重试后仍少于 6 Plan，workflow 会明确失败，不会再把缺项伪装成 SUCCESS。

## 5. SubjectReference Bootstrap

| 指标 | 实际 |
|---|---:|
| 输入引用 | 85 |
| references digest | `0097511bcf5da04e388169034257e71200e2d2fd1bd4d0f30bf5aa89f169112d` |
| terminal entries | 85 |
| resolved / ambiguous / not found / failed | 0 / 0 / 0 / 85 |
| bootstrap attempts | 103 |
| `known_item` / `arxiv_exact` | 85 / 18 |
| HTTP 429 / circuit-open | 2 / 101 |
| snapshot works / source records / artifacts | 0 / 0 / 0 |

入口在 workflow 前完成 cache 身份检查，并把与当前 paper/digest 匹配的 bootstrap 现场复制到 `0004`。namespace diagnostic 明确读取：

```text
outputs/runs/0004/MG19333vrw-debug-full-20260907/subject_references/list.json
```

因此 PAPERINPUT-REF-01 的“未 bootstrap、误读旧 namespace”已经关闭。不过“bootstrap 已执行并处于可复用终态”不等于“语料已成功建立”：首次请求遭遇 429 后 circuit 打开，85 条引用最终全部 failed，形成真实但空的当前 Run 快照。这解释了随后所有 `reference_search` 的 EMPTY。

另发现输入清洗问题：第 85 条 reference 把“简历与科研成果/出版授权书”等论文尾页内容并入引用并误解析标题。它不是本轮 0 命中的主因，但应进入 bootstrap parser backlog。

## 6. 按 NP / Task 的检索审计

`Ref` 格式为 calls / hit / EMPTY / FAILED；`DB outer` 为 outer calls / success-empty / failed；`Exec` 为 SearchExecution 总数 / success-empty / failed。

| NP / Task | Ref | DB outer | Exec | arXiv 错误 | Artifact | Reader | EvidenceCard |
|---|---:|---:|---:|---|---:|---:|---:|
| NP-1 / T-1 | 4 / 0 / 4 / 0 | 2 / 1 / 1 | 7 / 6 / 1 | 1 × 429 | 0 | 0 | 0 |
| NP-1 / T-2 | 3 / 0 / 3 / 0 | 2 / 1 / 1 | 7 / 6 / 1 | 1 × 429 | 0 | 0 | 0 |
| NP-2 / T-1 | 2 / 0 / 2 / 0 | 3 / 1 / 2 | 8 / 6 / 2 | 1 × 429；1 × CircuitOpen | 0 | 0 | 0 |
| NP-2 / T-2 | 3 / 0 / 3 / 0 | 3 / 1 / 2 | 8 / 6 / 2 | 1 × ReadTimeout；1 × CircuitOpen | 0 | 0 | 0 |
| NP-3 / T-1 | 4 / 0 / 4 / 0 | 2 / 1 / 1 | 7 / 6 / 1 | 1 × CircuitOpen | 0 | 0 | 0 |
| NP-3 / T-2 | 3 / 0 / 3 / 0 | 3 / 1 / 2 | 8 / 6 / 2 | 2 × CircuitOpen | 0 | 0 | 0 |
| **总计** | **19 / 0 / 19 / 0** | **15 / 6 / 9** | **45 / 36 / 9** | **3 × 429；1 × ReadTimeout；5 × CircuitOpen** | **0** | **0** | **0** |

每个 Task 都额外调用一次 `null_catalog`，每次按 strict/medium/broad 及 fallback 运行 6 个 SearchExecution，均为 `SUCCESS + EMPTY`。它解释了 DB 统计中的 6 个成功 outer 和 36 个成功 execution；这些成功不代表真实数据库召回。

配置中 `null_catalog` 标记为 `testing_only=true`，却仍暴露给 live 模型并被 6/6 Task 选择。它没有构成 transport failure 后的确定性 fallback，但造成表面 `SUCCESS + EMPTY` 和重复 database search，应作为当前最高优先级控制面问题处理。

## 7. arXiv outer call 时间轴与 PERF-001

| Tool | NP / Task | 开始（UTC） | 结束（UTC） | 时长 | 结果 |
|---|---|---|---|---:|---|
| `tool_0005` | NP-2 / T-2 | `05:54:40.030` | `05:55:20.059` | 40.029 s | ReadTimeout |
| `tool_0006` | NP-1 / T-1 | `05:54:40.313` | `05:55:15.371` | 35.058 s | HTTP 429 |
| `tool_0008` | NP-2 / T-1 | `05:54:41.440` | `05:55:12.316` | 30.876 s | HTTP 429 |
| `tool_0009` | NP-1 / T-2 | `05:54:41.442` | `05:55:22.868` | 41.426 s | HTTP 429 |
| `tool_0011` | NP-2 / T-1 | `05:55:15.816` | `05:55:15.820` | ~4 ms | CircuitOpen |
| `tool_0020` | NP-2 / T-2 | `05:55:23.789` | `05:55:23.792` | ~3 ms | CircuitOpen |
| `tool_0021` | NP-3 / T-1 | `05:55:23.850` | `05:55:23.853` | ~3 ms | CircuitOpen |
| `tool_0030` | NP-3 / T-2 | `05:55:27.847` | `05:55:27.850` | ~3 ms | CircuitOpen |
| `tool_0033` | NP-3 / T-2 | `05:55:30.567` | `05:55:30.570` | ~3 ms | CircuitOpen |

前四个长调用跨 Task 重叠，后五个在 circuit 打开后毫秒级失败。每个失败 outer 仅有 1 个 FAILED SearchExecution，没有恢复成问题 Run 的 6 个 transport fallback timeout；PERF-001 的并发、停止 fallback 与 fast-fail 结构均保持成立。

## 8. 完整 Evidence Funnel

| 层级 | Input | Success | Drop | 直接原因 |
|---|---:|---:|---:|---|
| ResearchTask | 6 | 6 | 0 | 六个任务均生成 |
| SearchPlan | 6 | 6 | 0 | Planner retry 后 6/6 |
| 有 retrieval hit 的 Task | 6 | 0 | 6 | subject corpus 空；arXiv 全失败；null_catalog 为空 |
| Artifact produced | 0 hits | 0 | 0 | 无检索结果可物化 |
| Artifact persisted | 0 | 0 | 0 | 无上游输入 |
| Artifact registered | 0 | 0 | 0 | research reference manifest 为 0/0/0 |
| Reader eligible Artifact | 0 | 0 | 0 | 无 Artifact |
| Reader calls / success | 0 | 0 | 0 | 未调用；`artifact_id="none"` 也为 0 |
| Raw evidence span | 0 | 0 | 0 | 无 Reader 内容 |
| Raw EvidenceCard | 0 | 0 | 0 | 无证据输入 |
| Validator accepted | 0 | 0 | 0 | 无 Card 输入 |
| Gate A accepted | 0 | 0 | 0 | 无 Card 输入 |
| Reviewer used | 0 | 0 | 0 | 无可审 Evidence |

Reader diagnostic 为 `INCOMPLETE` 且 calls=0；这只表示本轮没有 Reader 调用，不能归类为 Reader bug。Reviewer 没有模型调用，工作流为三个 NP 生成了三条 `insufficient_evidence` 结果；Final Evidence Sufficiency 对三个 NP 都是 `0 / required 1`。

## 9. 性能与资源

| 指标 | Run D |
|---|---:|
| total wall-clock | 159.606 s |
| point extraction | 12.710 s |
| planning wall-clock | 83.462 s |
| research wall-clock | 55.751 s |
| single research critical path | 52.373 s |
| synthesis | 7.314 s |
| Reviewer | 0 ms（无证据，未调用模型） |
| Renderer | 2 ms |
| LLM calls | 54 |
| input / cached input tokens | 188,582 / 160,896 |
| output / reasoning tokens | 27,583 / 20,645 |
| total tokens | 216,165 |
| reference_search calls | 19 |
| database_search outer / executions | 15 / 45 |

Run D 实际运行 6 个 ResearchTask，不能只按总时长与仅运行 3 个 Task 的 Run C 做简单回归判断。当前主要时长来自串行 Planner（83.462 s）及四个并发但各自含 retry 的真实 arXiv 调用；research 的 6 个 stage 单项耗时为 44.558、52.373、40.205、49.056、13.329、11.181 秒，但并发后的整体窗口只有 55.751 秒。

## 10. Backlog 重排

1. **RETRIEVAL-PROVIDER / BOOTSTRAP**：解决 arXiv 429、空 bootstrap corpus，区分“bootstrap 已尝试”与“bootstrap 有可检索 works”的业务 readiness。
2. **CTRL-001**：live schema 不应暴露 `testing_only` 的 `null_catalog`；同时收敛每 Task 的重复 database_search。
3. **CFG-LLM-01 follow-up**：对 DeepSeek `enable_thinking=false` 的服务端实际行为做 provider 级验证；不能再归因于本地白名单。
4. **BOOTSTRAP-PARSER**：修复第 85 条引用吞入尾页正文的问题。
5. **BUG-004**：reference_search query/budget 去重；应在 corpus 可用后测真实召回。
6. **BUG-005**：namespace diagnostic 本轮为 OK，降级为持续回归项。
7. **READER / EVIDENCE**：暂不升级；只有真实 Artifact 出现后 Reader 失败，或 Reader 成功后 Card 仍为 0，才进入相应层调查。

## 11. 验收表

| 验收项 | 结果 |
|---|---|
| 0004 独立目录创建 | PASS |
| 旧 Run 未覆盖 | PASS |
| PaperInput snapshot 正确 | PASS |
| bootstrap manifest、identity、snapshot 真实 | PASS |
| bootstrap 获得可检索语料 | FAIL：85/85 provider failed |
| 6 Tasks → 6 Plans → 6 actual tasks | PASS |
| SearchPlanner 最终 payload 透传 false | PASS（Phase 1 payload test） |
| provider 不再产生大量 reasoning | FAIL：仍有 15,149 planner reasoning tokens |
| 0 Harness protocol HTTP 400 | PASS |
| Runtime / references / report 位于当前 Run | PASS |
| Retrieval → Reader → Evidence Funnel 可定位 | PASS |
| Workflow status 与中间事实一致 | PASS：流程 SUCCESS，业务为 insufficient evidence |

## 12. 可追溯产物

Git 中归档 Runtime 摘要：

```text
docs/experiments/runtime/MG19333vrw-debug-full-20260907_2026-09-14/
└── run-2e6371011e074b6a95fe1d7cfbb79afe/
```

关键 SHA-256：

| 产物 | SHA-256 |
|---|---|
| `result.json` | `9fc1cbd57b27ccbe9f5307e5df90ac23243fc8e535f3f6cca2f4df26309cfd78` |
| `run.json` | `fca1bb428d05d099fad11424b98c3b2e664ecf90aa6ac65670e81df3b772acbd` |
| SubjectReference `bootstrap.json` | `8e77961060cb3df3f47128a0b2cec20affc4df8040b7706b15a647b67c91de5f` |
| Runtime `manifest.json` | `eba86ca3720bd2d6cd374c0587c9fdf9d35c12799e6ace27666611556e521ba8` |
| archived `summary.json` | `8b8db8318d3d0a368b0f961d295ae1aff786a9b9fcf4dc0e4455c8b3e52ebb0b` |

API Key 仅通过 `/tmp/deepseek_api_key` 注入本次进程；Run D 完成后该临时文件及临时启动配置已删除。配置、Runtime 和审计产物均未写入 Key。
