# V3 Attempt 2 补充预实验报告

## 实验信息

- 实验：V3 Attempt 2 Supplemental Pretest
- 变体：Prompt-Controlled Single-Pass Acquisition
- 脚本基线：`7d6a873389baf1f7f724517cf7c6b16c02592743`
- 输入：persisted MinerU PaperInput、persisted NoveltyPoint、6 个既有 ResearchTask
- 生产代码修改：无
- 生产 Prompt 修改：无
- 临时包装目标：`research/native_tool_loop`

## 总结

```text
Behavior Path: FAIL (0/6)
Acquisition: FAIL (0/6)
Card Path Proven: NO
Prompt behavior control: PARTIAL
Prompt card-quality control: INCONCLUSIVE
```

Prompt 明显改变了工具行为：原 Attempt 2 的多个同轮 tool calls 降为 0，并且 6/6 Task
都从 WebSearch 进入了 Browser 尝试。但它没有稳定执行“一次且仅一次”的约束：3/6 仍重复
WebSearch，5/6 在 Browser 失败后重复 Browser，最终触发 Browser per-tool budget。

全部 16 次 Browser 执行均因同一个 Playwright `TargetClosedError` 失败，因此没有 Artifact、
ReaderResult 或 Card。这一一致性基础设施故障使 Reader 与 Card 质量边界无法在本轮得到验证。

## Behavior

| 指标 | 结果 |
| --- | ---: |
| Tasks | 6 |
| Exact sequence compliant | 0 |
| Exact sequence compliance rate | 0% |
| Repeated-search violations | 3 |
| Browser skips | 0 |
| Reader skips | 6 |
| Extra-tool violations | 0 |
| Multiple-tool-call events | 0 |

工具总量：

```text
WebSearch: attempted/executed = 10/10
Browser: attempted/executed = 21/16
Reader: attempted/executed = 0/0
```

最后一次 Browser attempt 被 Harness 正确拒绝的 Task 有 5 个；预算违规为 0。

## Acquisition

| 指标 | 结果 |
| --- | ---: |
| SourceRecord selected | 6 |
| Browser success | 0 |
| Artifact created | 0 |
| Reader success | 0 |
| Trusted Read created | 0 |
| Trusted read chars | 0 |

Browser 的 16 次失败完全一致：

```text
TargetClosedError: BrowserType.launch:
Target page, context or browser has been closed
```

因此本轮只能证明 Prompt 能推动模型选择 SourceRecord 并调用 Browser，不能证明后续
Acquisition → Reading 路径。

## Finish 与 Card

| 指标 | 结果 |
| --- | ---: |
| Valid finish drafts | 1 |
| No-evidence finishes | 1 |
| Draft cards | 0 |
| Builder success | 1 |
| Builder rejection | 0 |
| Ungrounded quote failures | 0 |
| Evidence | 0 |
| EvidenceCard | 0 |

唯一正常 Finish 的 Task 为 `NP-3/T-1`。模型在一次 Browser 失败后遵守单次限制，明确以
`cards=[]` 和具体 `no_evidence_reason` 结束，说明“没有 Reader 材料时不要造 Card”的边界
在该样本上有效。但由于没有任何 Task 获得 Reader 文本，无法判断“材料弱/可用时是否正确
产 Card”，所以 Card-quality control 总体判为 **INCONCLUSIVE**，而不是 STRONG。

## Token 对比

| 指标 | 原 Attempt 2 | Single-pass pretest | 变化 |
| --- | ---: | ---: | ---: |
| WebSearch executed | 6 | 10 | +4 |
| Browser executed | 0 | 16 | +16 |
| Reader executed | 0 | 0 | 0 |
| Trusted Reads | 0 | 0 | 0 |
| EvidenceCards | 0 | 0 | 0 |
| Researcher tokens | 112292 | 206113 | +93821 (+83.6%) |

Token 没有下降。主要原因是 5 个 Task 在 Browser 持续失败后反复调用到 per-tool budget，
失败 observation 不断进入上下文；这不是 single-pass 成功路径的 token 表现。

## 任务书问题逐项回答

1. Prompt 是否改变 Tool sequence？**是**，消除了 multiple-tool-call，并让 6/6 进入 Browser。
2. 多少严格遵守单轮路径？**0/6**。
3. 是否仍重复 Search？**是，3/6**。
4. 是否仍出现 multiple tool calls？**否，0 次**。
5. Browser 是否真正执行？**是，16 次执行；全部失败**。
6. Artifact 是否真正产生？**否，0**。
7. Reader 是否真正执行？**否，0**。
8. Trusted Read 是否真正产生？**否，0**。
9. 有多少 Draft Card？**0**。
10. 有多少 Draft Card 被 Builder 接受？**0**。
11. 最终生成多少 Card？**0**。
12. 材料不足时是否正确不给 Card？**唯一正常 Finish 样本是；其余未 Finish**。
13. Prompt 对行为控制是否有效？**PARTIAL**。
14. Prompt 对 Card 质量边界是否有效？**INCONCLUSIVE**。
15. Token 是否下降？**否，增加 83.6%**。
16. 是否证明 Card path 可达？**NO**。

## 结论与后续决策依据

本预实验没有解决问题，也没有证明 Card path。它提供了两个清晰结论：

1. 明确 Prompt 对“同轮只调用一个工具”和“从 Search 进入 Browser”有效。
2. Prompt 对失败恢复策略控制不足；面对 Browser 工具失败，模型大多违反 single-pass 规则并
   重试至预算耗尽。

在讨论 Prompt、Skill、Progress 或 Harness 强约束前，应先把本轮一致出现的 Playwright
启动失败作为独立基础设施问题诊断；否则无法公平评价 Browser → Reader → Finish 行为。

## 产物

完整 JSON、六份 append-only trace 和 manifest snapshot 位于：

```text
outputs/experiments/mf2033k6lc-v3-attempt2-single-pass-prompt-pretest/
```

## Browser Runtime 修复后复跑（2026-08-27）

在零模型 Browser preflight、backend smoke、Browser → Artifact → Reader smoke
全部通过后，使用相同实验 Prompt 原样复跑。结果如下：

| 指标 | 修复前 | 修复后 |
|---|---:|---:|
| 严格单次序列 | 0/6 | 2/6 |
| Browser success | 0/6 | 4/6 |
| Artifact tasks | 0/6 | 4/6 |
| Trusted Read tasks | 0/6 | 4/6 |
| Trusted Read chars | 0 | 22,865 |
| Grounded EvidenceCard | 0 | 0 |
| Researcher tokens | 206,113 | 242,037 |

获取层由 FAIL 变为 **PASS**，证明 Browser runtime 修复有效，不再是统一的 Chromium
启动失败。行为路径仍为 **FAIL**：4 个任务重复 Search 或 Reader，`NP-3/T-1` 遇到
模型调用失败，`NP-3/T-2` 的目标页面导航超时。唯一草稿 Card 的 quote 不是 Reader
原文逐字摘录，被 EvidenceCardBuilder 正确拒绝，因此 card path 仍未证明。

本次尝试没有完整跑通，不继续全栈复跑；按既定安排，待 reviewer 接入后再做完整 demo。
详细基础设施结论见 `docs/experiments/Browser_Runtime_Repair/report.md`。
