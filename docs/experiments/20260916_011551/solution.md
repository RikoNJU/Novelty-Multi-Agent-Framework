# 带参考文献缓存的完整工作流实验

## 结论

完整运行成功，报告生成及完整性校验通过。开始时间 2026-09-16 01:10:47，
结束时间 **2026-09-16 01:15:51**（Asia/Shanghai），耗时 **314.06 秒**。
最终保留 **4 张卡**，全部引用本次复用的参考文献缓存；NP-1 仍证据不足。

本次验证了真实运行中的批量 Reader、按卡并行 Reviewer、按查新点汇总与报告落盘。
未修改生产代码，未提交；运行所用工作区修改保存在 `source.patch`，基准提交见 `base_commit.txt`。

## 配置与缓存

- 样例：`examples/MF2033k6lC.pdf`，复用已有 PaperInput，未调用 MinerU。
- 仅英文检索；arXiv、Springer Nature 开启；WebSearch 开启；Browser 关闭。
- 最多 2 轮，工作流并发数 4；沿用扩大后的工具预算。
- 原稳定目录是上次清空后的空缓存，本次从
  `docs/experiments/20260915_224229/input/MF2033k6lC/subject_references`
  复制历史缓存到实验隔离目录。91 条参考文献引导记录与当前 PaperInput 匹配，
  其中 9 篇有可读 Artifact，文件 SHA-256 全部通过验证。
- `force=False`，没有重新抓取参考文献缓存；没有导入历史 Evidence、Card 或 Review。
- 初次启动曾被自动审批拦截，用户明确允许向 SiliconFlow 发送本样例及文献片段，
  并调用数据库和 WebSearch 后，本次成功启动。`preflight.md` 仅为启动前历史记录。

## 运行结果

| 查新点 | 研究任务数 | 检索执行记录 | 不重复 source/query | 可信读取片段 | 最终 Card | 最终判定 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| NP-1 | 2 | 19 | 6 | 6 | 0 | 证据不足 |
| NP-2 | 1 | 8 | 2 | 3 | 2 | 部分新颖 |
| NP-3 | 1 | 8 | 2 | 9 | 2 | 部分新颖 |

以上判定是工作流模型的输出，不代表覆盖充分；NP-2、NP-3 的文献均仅部分相关。
三个查新点的全部执行记录均进入报告检索式部分，包含失败标记。

- Researcher 共取得 18 段可信读取：13 段来自参考文献缓存，5 段来自本轮数据库制品。
  Reviewer 另有 6 段成功回读。合计读取缓存中的 8 个不同 Artifact。
- 4 张卡对应 TGAT、TGN、AGL、AliGraph；5 条 Evidence 均可追溯至缓存文献。
- 本轮外部资料库新增 8 个 Work、9 个 Artifact、8 条数据库来源记录；
  WebSearch 另保存 10 条 `source_kind=web_supplement` 记录。
- WebSearch（千帆）1 次 HTTP 200，工具可用。网页标题没有列入报告，
  没有产生网页 Evidence/Card。本次数据库已检到论文，因此未验证“完全检索不到论文时写入网页建议”的条件分支。
- Reader 总计 21 次工具调用，12 次使用批量形式（5 次两段、7 次一段）；
  其中 Researcher 14 次、Reviewer 7 次。5 次两段请求各合并了一次单段工具调用，
  不能直接把这理解为端到端节省了固定数量的模型调用。
- 数据库结果复用命中 0 次：本轮所有可用的 Springer 工具结果仍包含部分成功执行，
  不符合“整次完整成功才缓存”的条件；其他调用失败。本次没有成功结果可复用的实测样本。

## 耗时与并行证据

| 阶段 | 墙钟耗时 |
| --- | ---: |
| 查新点提取 | 19.79 秒 |
| 首轮研究，三个任务并行 | 最慢任务 88.71 秒 |
| 首轮按卡审查及汇总 | 40.35 秒 |
| NP-1 第二轮补检 | 66.65 秒 |
| 第二轮按卡审查及汇总 | 43.98 秒 |
| 报告综合 | 31.37 秒 |

首轮 4 个单卡请求在约 1.2 毫秒内启动；运行中检查点同时记录 4 个 running，
验证每卡并行确实发生。两轮共 8 次单卡评审、4 次查新点汇总；模型调用分别为
17 次单卡调用和 4 次汇总调用，单卡可能包含回读或格式修复。每个有卡的查新点
每轮只进行一次汇总模型调用。最终检查点索引为 1–4，全部 completed。

总模型调用 98 次，报告 usage 累计 1,071,911 tokens。`stage_timings.json` 中并行
任务的累加时间不能当成端到端墙钟时间；Reviewer 墙钟时间以 runtime stage meta 为准。

上次清空缓存实验耗时 1460.25 秒，本次约为其 21.5%，耗时减少约 78.5%。
但两次缓存、任务数量（6 对 4）、外部响应与实现版本均不同，不能将该差值归因于
Reviewer 并行或批量 Reader 的单独加速效果；本次未进行相同冻结输入的串行对照。

## 错误、影响与解决方案

### 1. Reviewer 汇总缺少跨字段格式约束示例

首轮 NP-3 的两个单卡评审成功，但汇总模型同时输出 `status=insufficient_evidence`
和非空 verdict，触发 `insufficient_evidence result cannot have verdict`。
汇总安全降级，未中断流程；第二轮重新审查后恢复为合法结果。

原因：传给模型的 JSON Schema 未表达 Pydantic `model_validator` 的跨字段语义，
汇总 prompt 也未给出对应示例。解决方案：明确写出两个合法分支，例如证据不足时
`{"status":"insufficient_evidence","verdict":null,"supplement_request":{"reason":"..."}}`；
reviewed 则必须提供 verdict、verdict_reason、confidence。可增加确定性的保守格式规范化：
仅当模型明确给出证据不足时清除冲突的 verdict，绝不反向补造肯定裁定。
如需模型修复应单独约定调用预算，不能悄悄突破一次汇总调用的设计。

### 2. 报告综合没有收到已存在的检索执行事实

报告第 5.3 节列出实际执行式，但 NP-1 结论及局限仍写“检索覆盖执行事实未提供”。
`_synthesize_report` 只向 Coordinator 传入 Card、Review 等信息，没有传入已有
`task_research_results.search_executions`。不是没有日志，而是综合输入断链。
报告来源列表也仅显示 arxiv.org，未反映实际查询了 Springer。

解决方案：按查新点传入精简覆盖统计（来源、成功/零命中/部分成功/失败、候选数、
读取数、成卡数），来源列表从实际执行记录生成。区分“有结果但不相关/未成卡”和
“搜索失败”，避免让模型从 Card 数量反推检索成败。

### 3. 补检依据只有卡片数量，审查失败没有专门恢复路径

首轮 NP-3 汇总失败，但有 2 张合法卡，因此未被 `_check_final_evidence_sufficiency`
列入补检。本次因 NP-1 触发第二轮，所有卡又被审查，才间接恢复 NP-3。
同时，两轮审查的 4 个 Card ID 完全相同，说明未变动的卡也重复执行了单卡评审。

解决方案：分开处理“缺 Card”和“审查执行/格式失败”；后者优先重试汇总而非重做检索。
以 point/card/evidence 内容、prompt 和模型配置的指纹复用已完成单卡结果；
只有输入发生变化才重审，失败的汇总按显式预算恢复。本次没有修改这一策略。

### 4. Reader 两类无效请求均受控恢复

- 一次批量读取设置 `char_start=2000`，超出该摘要长度。错误保留在 `read_errors`，
  同批其他片段正常保留。应在 prompt 中要求仅在 `has_more=true` 时从已返回的 char_end 续读。
- 第二轮 Reviewer 一次请求只有 `{"reads":null}`，被参数校验拒绝，随后继续完成评审。
  单读/批读互斥约束当前主要由 Python validator 执行；应在工具 JSON Schema
  中表达互斥且至少一个非空的分支，配合合法调用示例。

### 5. 数据库失败和部分成功仍产生重复调用

HTTP 审计：arXiv 429 共 5 次、网络异常 1 次；Springer 404 共 11 次、200 共 11 次。
NP-1 两轮均耗尽 database_search 调用预算后受控收尾。按本次约定未修改 arXiv 429 策略。

两个可用的 Springer 调用各包含两条成功检索和一条部分成功检索，因此整次调用没有缓存。
这符合当前补丁语义，但会重做其中已经成功的查询。进一步方案是以规范化查询及参数
为粒度复用成功执行，仅重试失败/部分完成项。对于 Springer 404，应保留响应语义并区分
合法无结果和端点/服务错误，不能仅凭状态码当作零命中。

NP-1 读取了部分重叠的综述仍无卡，收尾理由强调未公开完整技术组合。建议进一步检查
Researcher 是否仍将“部分相关可比较”误解为“必须完整覆盖才能成卡”；本次只记录该质量疑点。

## 产物与验证

- `run/MF2033k6lC/report/MF2033k6lC-report.md`：最终报告。
- `run/MF2033k6lC/novelty-reviews.json`：带索引单卡结果及最终汇总。
- `metrics.json`：统计；`audit.json`：本地确定性检查 PASS。
- `run/http_events.jsonl`、`run/model_calls.json`、`run/stage_timings.json`：请求与耗时记录。
- `run/MF2033k6lC/runtime/`：完整阶段、工具与检索审计。
- `run.py`、`summarize.py`、`audit.py`、`progress.py`：复现及核对脚本。

目录按实际运行结束时间归档。历史配置和日志中的原始绝对路径保留，不重写为新目录。
