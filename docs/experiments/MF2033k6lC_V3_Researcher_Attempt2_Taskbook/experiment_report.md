# MF2033k6lC V3 Researcher Attempt 2 实验报告

- 实验时间：2026-08-27
- 基线 SHA：`32fa172090c9b4c795bc6b6002a6a3d7ec9ae30f`
- 起点：`persisted_mineru`
- PointExtractor：`persisted_checkpoint`
- Validator：`experimental_passthrough`
- Reviewer：未启用

## 结论

**Pipeline PASS。** 6 个计划任务全部派发并全部返回 `TaskResearchResult`，fan-in 完成，
Coordinator synthesize 成功，`workflow_result.json` 已落盘，预算违规为 0。

机械工作流已经能够在正式 typed config 与 Harness budget 下受控地完整返回，故判定：

```text
Infrastructure Ready = YES
Ready for Progress = YES
Full-stack rerun = DEFERRED_UNTIL_REVIEWER
```

按照任务书的最新停止条件，本次达到 `PIPELINE PASS` 后已停止，未继续执行 MinerU、
PointExtractor 起点的全栈复跑。完整 Demo 等 Reviewer 接入后另立任务执行。

## Preflight

```text
45 passed
0 failed
```

Config loader、typed factory、四工具注册、total/per-tool/Reader budget、SearchPlanner 配置、
checkpoint 和 API key 环境检查均通过；API key 值未打印或写入产物。

## 正式运行

第一次运行已经完成 Researcher fan-in，但 Coordinator `synthesize_report` 请求发生 Provider
读取超时。依据任务书允许的“明确 Provider 短时网络异常”重跑规则，实验测量客户端加入
一次仅限 Coordinator 网络失败的原请求重试后进行受控重跑。未修改生产代码、Prompt、
Researcher budget 或工具策略。

受控重跑结果：

| 指标 | 结果 |
| --- | ---: |
| planned tasks | 6 |
| dispatched tasks | 6 |
| results | 6 |
| completed | 0 |
| partial | 6 |
| failed | 0 |
| empty evidence | 6 |
| fan-in | complete |
| synthesize | complete |
| workflow elapsed | 387252.399 ms |

`PARTIAL` 不影响 Pipeline PASS，但表明 Researcher 行为效果不足。

## 工具与预算

| Tool | Attempted | Executed | Rejected |
| --- | ---: | ---: | ---: |
| web_search | 12 | 6 | 6 |
| database_search | 2 | 0 | 2 |
| browser | 0 | 0 | 0 |
| reader | 0 | 0 | 0 |
| 合计 | 14 | 6 | 8 |

- 串行协议拒绝：3 个 Task；模型同一轮返回多个 tool calls。
- WebSearch per-tool budget 拒绝：2 个 Task，共 2 次。
- 模型调用失败：1 个 Task。
- Reader 字符预算拒绝：0。
- Budget violation：0。

预算耗尽属于正确拒绝，不属于违规。由于没有 Reader 调用，可信读取字符数为 0。

## Evidence

```text
trusted reads: 0
actual read chars: 0
evidence: 0
evidence cards: 0
```

这次结果证明 Harness 和 NoveltyWorkflow 的失败隔离、fan-in 与最终汇总链路可用，但也明确
显示正式 Researcher 容易并行请求多个工具或重复 WebSearch，没有进入 Browser/Reader，
因此下一阶段需要通过 Progress / Skill / Prompt Engineering 改善行为与效率。

## Token

| 角色 | Tokens |
| --- | ---: |
| Coordinator | 78062 |
| PointExtractor | 0 |
| Researcher | 112292 |
| SearchPlanner | 0 |
| Grand total | 190354 |

PointExtractor 使用 checkpoint；DatabaseSearch 没有实际执行，因此 SearchPlanner 调用为 0。

## 产物

原始实验产物位于：

```text
outputs/experiments/mf2033k6lc-v3-researcher-attempt2/
```

包含 effective config、metadata、processing/point/task/workflow/token summaries、六份 append-only
trace、manifest/evidence/evidence-card snapshots、workflow result 与 raw experiment result。

## 最终判定

```text
Pipeline: PASS
Researcher behavior: INSUFFICIENT
Infrastructure ready: YES
Ready for Progress: YES
Full-stack rerun: DEFERRED_UNTIL_REVIEWER
```
