# 修复后的本地 Qwen + arXiv 在线验证

2026-09-28，生产版本 `1457237`。用户明确允许调用本地模型及 arXiv 网络。本阶段只增加隔离实验配置、诊断脚本和记录，不修改生产代码或默认配置。

## 实验设计

- 本地 `/v1/models` 健康检查返回 200，Qwen2.5-7B 服务声明上下文上限 32768。
- 第一轮使用原论文 MF2033k6lC 与旧 full_live_profile 的角色配置，API 通道、40 次模型/12 次 Provider 上限、单并发、单轮；关闭 null_catalog，其他远程检索源及 web_search/browser 均关闭。
- 用第一轮实际失败的两条查询与人工 `all:"graph neural network"`，调用现有 ArxivWebSearchTool 做三次独立网络对照；间隔 8 秒、无重试，原始 HTML 响应及哈希保留。
- 网页对照成功后，第二轮切现有 web 通道，并把每任务全文上限从 0 改为 1；25 次模型/6 次 Provider 上限。其余角色模型与论文相同。

第二轮重新生成查新点与计划，且全文配置和调用预算不同，因此**不是只改变 transport 的严格消融实验**。同查询的通路比较来自三个独立网页探针；两轮流程用于探索检索后续阻断，不用于声称总体效果提升。网页查询由现有适配器翻译，不据此保证与 API 检索语义完全一致。

正式入口冻结源代码、输入、配置和运行身份，见 runs/0001/startup 与 runs/0002/startup。91 条原论文参考文献的既有 bootstrap 缓存校验通过后复用；没有把这些缓存内容计作本轮新召回。两轮 runtime 原目录及自动归档都保留，计数只取 runs 下的规范 runtime，不重复相加。

## 第一轮：API 失败与模型动作错误并存

第一轮 83.36 秒，15 次本地 chat；60182 输入 + 2882 输出 = 63064 tokens。3 次物理 arXiv API 请求全部 406。0 Evidence，两个查新点均 insufficient_evidence。外层 SUCCESS 仅表示执行和报告生成结束，整体验收未通过。

新修的 not_run 关联已进入真实运行，analysis.json 检查直接失败执行、事件 ID 和错误码都能对应。

原始模型响应与同次请求提供的工具 schema 对照显示：

- 第 8 次模型调用为 database_search 输出空全文记录 ID，并添加未定义的 toolbench_rapidapi_key（原值为空，归档自动脱敏）。边界校验拒绝执行。
- 第 10 次模型调用选择未注册、也未向模型提供的 web_search。Harness 拒绝执行，未产生外网网页搜索请求。
- 模型另重复调用失败源：这与 transport 自动重试不同。本轮 API retry_count 为 0，但 task 内发生再次调用。总图 round=1 时的 STOP 不等于 task 内禁止重复调用。

这些是本地模型动作遵从的实测问题；它们不解释早先人工/API 查询的 406，也不能仅凭单模型实验量化模型规模差距。

## 网页通道对照

两条实际查询分别返回 0 和 3 个选取结果，人工查询返回 3 个选取结果；三次 HTTP 均 200。探针 limit=3 不代表页面或 arXiv 全部命中数。记录见 web_probe_results.json 和 web_response_*.body。

说明当前环境中现有网页通道可用于部分实际查询，不代表 API 406 已修复，也不代表所有查询稳定。没有自动改生产默认通道。

## 后续阻断及边界

网页整流程已实际召回候选并触发 Reader。NP-1 一次请求包含 33437 输入 tokens，加 4096 输出预算共 37533，超过服务器 32768，上游返回 400。该实验配置的预检已有 context_input_not_preflighted 警告，输入严格准入未启用。

仓库已有 local-harness-guarded profile 可启用准确准入，但提前拒绝超长请求不能自动解决累积读取轨迹后的成证问题。本阶段保留失败配置与输出，不事后改成开启准入的成功实验。材料可用之后仍应分别检查上下文管理、读取行为与证据提交能力。

所有最终数字见 analysis.json；其统计脚本 analyze.py 验证逐调用 token 账目和跳过项关联。价格未配置，本地成本未知。HTTP 406 外部根因、稳定成证和 Reviewer 充分材料核验仍未完成。

## 第二轮最终结果及补做 Reviewer

第二轮耗时 312.47 秒，25 次实际本地 chat（含一次服务端 400）；5 次实际网页 HTTP 均 200。11 次 Reader 工具调用，形成 1 张卡、2 条引用证据，Validator 与 Gate A 接受该卡。NP-1 上下文超限；NP-2 产卡；NP-3 受检索预算影响；NP-4 未获得模型调用预算。Reviewer 对 NP-2 标记 budget_exhausted，最终 synthesize_report 因模型预算耗尽失败，没有最终报告。

因此 analysis.json 将缺少最终结果记为 final_report_evidence_cards=null，另列 task_cards_produced=1 和 gate_a_accepted_cards=1，不把“没有 result.json”误记为零产卡。

为避免只因人为调用上限而无法观察 Reviewer，另在新目录复用这张卡和原材料，允许最多 8 次本地调用、只开放本地 Reader。实际用了 **1 次** chat，未读取材料，却在返回中引用本轮未生成的 read_id，被 model.output_reference 拒绝。引用来自输入中的既有读取记录，不是本轮 Reviewer 的读取，正是提示明确禁止的行为。结果为 insufficient_evidence / technical_error，不是语义核验成功。

补做脚本在单卡核验完成后的汇总行漏写 index，发生 KeyError；原日志、原脚本 review_saved_card.before.py 和失败 runtime 保留。修正脚本字段后，由 finish_review_summary.py 仅汇总已保存的失败单卡结果，**没有重做单卡推理、没有新增 chat 或网络**；汇总保持失败状态。此脚本错误与模型的错误引用分开记录。

本阶段合计 **41 次实际本地 chat、11 次实际 arXiv HTTP**（API 3 + 网页整流程 5 + 网页对照 3）。另有一次本地 models 健康检查。模型返回已知用量合计 269126 tokens；400 请求没有返回 usage，不能将已知总和冒充所有失败请求的完整计费量。本地算力成本未知。

## 新暴露的工程缺口（本阶段未修）

1. 网页全文双重预算预留：外层 ArxivFullTextTool._try_get 预留 arxiv_auxiliary，内层 ArxivWebSession 又预留 arxiv_web。原始 provider_budget/0004.json 和 0005.json 对应同一次全文请求，因此 6 次预留只有 5 次实际 HTTP；这导致预算提早耗尽，不能声称已实发 6 次。两个方法的确定调用链与物理事件相互印证。
2. 服务端明确上下文超限的 400 当前进入 model.transport，而不是 model.context_limit。此实验 profile 未启用严格上下文准入，预检警告没有阻止发送。准入配置、错误分类与轨迹容量应分别处理。
3. 总图恢复策略之外，Researcher 在同一任务内可以重复调用已经返回 406 的来源。全局 STOP 不自动约束当前任务的每一次工具动作。

这些发现使后续修复对象更明确，但本阶段没有修改生产代码来掩盖实验失败。下一轮应先修预算重复计数与上下文失败分类，再以冻结任务/材料验证上下文管理及 Reviewer 引用约束；增加总调用数本身不足以证明修复。
