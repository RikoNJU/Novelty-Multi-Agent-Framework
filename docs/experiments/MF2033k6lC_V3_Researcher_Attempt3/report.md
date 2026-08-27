# MF2033k6lC V3 Researcher Attempt 3 实验报告

## 结论

Attempt 3 未成功证明真实 EvidenceCard 路径。唯一真实任务 `NP-1/T-1` 连续执行
3 次 `web_search`，第 4 次调用被生产 Harness 的单工具预算拒绝；没有进入 Browser、
Artifact、Reader、FinishDraft 或 EvidenceCardBuilder。

本次失败属于 **Prompt 行为策略未被遵守**，不是 Browser runtime 故障。实验前的
Browser preflight 全 PASS，零模型 Browser → Artifact → Reader smoke 3/3 PASS。

按照任务书的成本边界，只有“首次任务 Reader 成功但材料确实不足”才允许换 1 个
已有任务。本次没有到达 Reader，因此没有启动第二个真实任务，也没有运行 6 Task 或
完整 Coordinator fan-out。

## 阶段 1：正式 Prompt 修改

正式 `research/native_tool_loop` Prompt 从版本 1 升到版本 2，新增：

1. 默认优先 `database_search` 获取结构化学术来源；候选弱、不可用或无全文时再以
   `web_search` 扩大召回。
2. 中文任务提高 Web 优先级，但不设为 Web-only，DB 仍可补充。
3. Search result/snippet 只属于 discovery metadata，不能作为 evidence。
4. 每轮 WebSearch 后必须选择 SourceRecord，并闭合 Browser → Artifact → Reader，
   Reader 评价完成前不得再次 WebSearch。
5. DB 若直接返回 Artifact，可跳过 Browser 直接 Reader；只有 metadata 时仍需获取正文。
6. 所有 quote 必须逐字复制 Reader 文本，禁止释义、翻译、归一化、改写或重构。
7. 没有精确支持句时允许 `cards=[]`，禁止为了完成任务强制产 Card。

阶段 1 的 Prompt render、Prompt policy、workflow construction、Harness、Config、
Browser、Reader、Builder 等相关确定性测试共 75 项全部通过。扩大测试集时，仓库既有
API 生命周期测试长期无输出，已中止；它不在本次修改路径内。提交钩子随后正常通过并
完成 Prompt 提交。

## 基础设施门禁

| 门禁 | 结果 |
|---|---|
| Playwright import / Chromium launch | PASS / PASS |
| local HTML / public static page | PASS / PASS（HTTP 200） |
| Browser runtime dependency mode | Conda 子进程 fallback |
| 零模型 Browser smoke | 3/3 PASS |
| Browser → Artifact → Reader | PASS |
| 门禁阶段模型 API 调用 | 0 |

因此真实任务没有 Browser 调用，不能归因于动态库、代理或公网基础设施。

## Task 选择

选择 `NP-1/T-1`（中文 `literature_search`）。上一轮该任务曾严格完成
WebSearch → Browser → Reader，读取 8,000 个可信字符并生成 1 张 Draft Card；唯一
失败点是 quote 被模型改写，随后被 Builder 以 `ungrounded quote` 正确拒绝。因此它最能
同时验证中文检索策略、Web 闭环和新 quote grounding 规则。

## 真实执行结果

执行顺序：

```text
attempted: web_search → web_search → web_search → web_search
executed:  web_search → web_search → web_search
```

3 次 WebSearch 均成功，各返回并持久化 10 个候选。模型没有从任何一轮选择
SourceRecord，而是连续改写 query。第 4 次 WebSearch 在执行前被 Harness 拒绝：
`web_search tool-call budget exhausted`。

| 指标 | 结果 |
|---|---:|
| database_search | 0 |
| web_search attempted / executed | 4 / 3 |
| browser | 0 |
| reader | 0 |
| 连续 WebSearch policy violation | 是 |
| Finish reached | 否 |
| Artifact | 0 |
| Trusted Read chars | 0 |
| Draft Card / quote | 0 / 0 |
| Builder called / accepted | 否 / 否 |
| Evidence / EvidenceCard | 0 / 0 |
| Researcher token | 44,097 |
| Search Planner token | 0 |
| 总 token | 44,097 |

中文 Web 优先级确实生效，但过度生效：模型完全跳过默认 DB 优先级，并违反每轮 Web
必须闭合 Browser → Reader 的明确规则。

## 验收层级

| 层级 | 结果 | 原因 |
|---|---|---|
| Level 1 Behavior Policy | FAIL | 出现连续 WebSearch |
| Level 2 Acquisition | FAIL | 无 Browser/Artifact/Reader |
| Level 3 Grounding | FAIL | 无 Reader quote、无 Draft |
| Level 4 Attempt 3 | NOT PROVEN | EvidenceCard = 0 |

本轮没有手写 Card、注入 ReaderResult、使用 fixture、放宽 Builder grounding 或跳过
Builder，不存在伪成功。

## 任务书问题逐项回答

1. Prompt 新增哪些策略？DB 默认优先、中文 Web 提权、Web 闭环、DB Artifact 直读、
   Reader 后评价、逐字 quote 和合法空 Finish。
2. DB/Web 顺序？实际未调用 DB，只连续执行 3 次 Web。
3. 中文策略是否生效？是，但模型将提权执行成 Web-only。
4. 是否连续 Search？是，构成明确 policy violation。
5. WebSearch 是否闭合 Browser → Reader？否，三轮均未闭合。
6. Browser 是否成功？真实任务未调用；前置 smoke 成功。
7. Artifact 是否生成？真实任务没有。
8. Reader 是否成功？真实任务未调用。
9. Trusted Read 字符数？0。
10. 是否生成 Draft Card？否。
11. quote 是否逐字来自 Reader？无 quote，无法验证。
12. Builder 是否接受？未到 Finish，Builder 未调用。
13. Evidence 数？0。
14. EvidenceCard 数？0。
15. 是否得到真实 EvidenceCard？否。
16. 总 token 成本？44,097。
17. 是否需要下一阶段设计？是。单靠 Prompt 不能可靠保证 WebSearch 闭环；下一步应在
    不放宽 grounding 的前提下讨论 Harness 状态约束或显式检索状态机，并在 reviewer
    接入后再决定完整 demo，而不是继续盲目扩大真实任务数量。

## 产物

报告仅保存在 `docs/experiments/MF2033k6lC_V3_Researcher_Attempt3/report.md`。
结构化 summary、task result、trace、manifest、Reader 输出和 token 明细位于：

```text
outputs/experiments/mf2033k6lc-v3-researcher-attempt3/
```
