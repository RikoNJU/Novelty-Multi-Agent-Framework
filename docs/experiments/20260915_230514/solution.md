# 英文单路径与扩大工具预算实验

## 实验设置

- 样例：`examples/MF2033k6lC.pdf`
- 入口：已有 `PaperInput`，未调用 MinerU
- 数据库：arXiv、Springer Nature
- WebSearch：开启，仅作为无论文证据时的补充资料
- Browser：关闭
- 检索语言：仅 `en`
- 工作流：2 轮，并发数 4
- Researcher：28 turns、24 次总工具调用；`reference_search=8`、`database_search=8`、`reader=16`
- Reviewer：14 steps、12 次工具调用、96,000 字符读取预算

运行前清空了 `outputs/MF2033k6lC/references` 的 72 个文件和
`outputs/MF2033k6lC/subject_references` 的 11 个文件。保留已解析 PaperInput，随后使用
`force=True` 从 PaperInput 中的 91 条参考文献重新构建索引。
运行结束后稳定缓存中只留下 3 个新生成的索引/引导清单，没有复用旧文献正文。

## 结果

完整工作流运行成功，耗时 1460.25 秒，报告成功生成。首轮和第二轮均严格生成英文任务：
每轮 NP-1、NP-2、NP-3 各 1 个任务，共 6 个任务；没有中文 ResearchTask 或中文 SearchPlan。
与配置及 Coordinator 相关的 52 项测试全部通过，结果保存在 `tests.xml`。

| 查新点 | 实际数据库执行 | 不重复的 source/query | 状态 | 最终 Card |
|---|---:|---:|---|---:|
| NP-1 | 14 | 6 | 7 成功、2 部分成功、5 失败 | 0 |
| NP-2 | 10 | 4 | 10 失败 | 0 |
| NP-3 | 6 | 4 | 2 成功、4 失败 | 1 |

总计得到 32 个外部 Work、32 个数据库来源记录、35 个 Artifact、29 次可信 Reader 读取和 1 张最终 Card。
报告中三个查新点都列出了实际执行的检索式；NP-2 已正常进入第二轮补检，不再出现“NP-1 补检、NP-2 不补检”导致的数量差距。

## 错误分析

1. 清空缓存后，91 条论文参考文献重新解析结果为 89 条失败、2 条未找到。主要原因是参考文献引导阶段依赖 arXiv，第一次 429/超时后熔断，后续条目没有获得缓存中的 AliGraph、AGL 等可读文献。因此，本实验比复用缓存的运行少了大量参考文献证据。
2. arXiv 仍然不稳定：HTTP 429 共 9 次、网络超时 3 次，后续大量调用被 circuit breaker 拦截。本次按既定要求未修改 arXiv 429 策略。
3. NP-2 的 Springer 查询返回 HTTP 404。当前 Provider 将这个响应记录为执行失败，而不是零命中；两轮 NP-2 查询又都采用严格 AND 组合，因此没有可读候选。NP-2 的“10 次检索”代表真实执行次数，不代表 10 个不同检索式，其中只有 4 个不同的 source/query 组合。
4. 扩大预算后仍有一次 NP-1 第二轮 `reader tool-call budget exhausted`：该任务读取达到新的 16 次上限。它完成了受控收尾，没有中断整个工作流。Reviewer 没有再出现预算耗尽。
5. NP-3 第一轮发生一次 `model call failed`，第二轮恢复；ResearchFinishDraft 的单次格式修复也成功触发。两个候选 Card 因引用片段无法逐字落到 Reader 文本而被拒绝，最终保留 1 张可溯源 Card。
6. WebSearch 共 5 次 HTTP 429，没有产生 web source record，也没有进入相关文献列表。

## 后续方案

- 将 Springer 搜索接口的“合法请求但无结果”明确映射为 `zero_hits`；只有鉴权、协议和服务异常才标为 `failed`。需结合 Springer 响应体判断 404 语义，避免把真实端点错误误判为零命中。
- 在 SearchPlanner/Researcher prompt 中要求失败或零命中后放宽概念组合，避免原样重复严格 AND 查询。当前重复调用会消耗新增预算，却不扩展覆盖面。
- 参考文献引导不应只依赖 arXiv。可以用 DOI/URL 直接获取，并让 Springer 等数据库参与 known-item resolution；缓存全空时尤其重要。
- Reader 预算应按“不同 Artifact”计数或阻止重复读取，比继续提高固定上限更有效。若暂不实现去重，可把 Researcher reader 上限从 16 提至 24 作为实验配置。

## 产物

- `run/run.json`：运行状态与时长
- `run/effective_config.json`：脱敏后的实际配置
- `run/reference_bootstrap.json`：缓存清空后的参考文献重建结果
- `run/metrics.json`：汇总指标
- `run/MF2033k6lC/report/MF2033k6lC-report.md`：最终报告
- `failed_attempt_01/`：实验脚本残留变量导致的启动前失败记录；未发起外部请求
