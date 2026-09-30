# 03｜Runtime、Token、错误码与 Reviewer：当前项目核查

核查日期：2026-09-30；源码 `3bd1d7f282e61fb2b3b599c4f37ca586da1e8238`。对应 [任务 03](../../task/2026-09-27/分卷/03_Runtime_Token_错误码与Reviewer.md)。仅静态分析、阅读既有产物；未执行测试或补充实验。

## 已处理部分与边界

- **usage 在业务响应解析前记录。** [model_client.py](../../backend/env/model_client.py)第 433–437 行发出携带原始 usage 的 RESPONSE_PARSED，随后才解析 choices/tool_calls（第 450–460 行）。取消后线程晚到结果使用同 call_id（第 529–575 行）；[test_usage_accounting_closure.py](../../tests/test_usage_accounting_closure.py)包含解析失败、取消和修复两次请求的断言。本轮只读测试，未复跑。
- **未定价总成本不再显示为确定的零。** [runtime_artifacts.py](../../backend/src/novelty_agent_framework/core/runtime_artifacts.py)第 1352–1357、1425–1433 行区分 Unknown 与 priced subtotal；[llm_usage.py](../../backend/src/novelty_agent_framework/diagnostics/llm_usage.py)第 69–78 行处理 usage 缺失/不全。token 缺边仍用数值零聚合，但有 completeness 标志；cached/reasoning 缺失的零不能解释为实际没有缓存/推理消耗。本地资源成本仍未测量。
- **Reviewer 空输入、旧 read_id/空读取、特征冲突已有明确路径。** [evidence_reviewer.py](../../backend/src/novelty_agent_framework/agents/evidence_reviewer.py)第 223–228、962–995、1135–1171 行分别短路、拒绝非法回读、拦截欠支持的 not_novel。同一 Work 全特征 supported 且有引用才通过该门控；它检查模型自身矩阵一致性，不判断引用语义真伪。
- **错误目录和有界恢复已存在。** [failures.py](../../backend/src/novelty_agent_framework/schemas/failures.py)、[failure_classification.py](../../backend/src/novelty_agent_framework/core/failure_classification.py)、[recovery_policy.py](../../backend/src/novelty_agent_framework/core/recovery_policy.py)已区分 Provider、模型、材料、预算等；不能再说路由完全只数卡。406 分类为 protocol 并保留“根因未定”，而非权限拒绝或零命中。

## R-01：namespace 误报和批读缺口仍存在（P1，代码确认）

位置：[reference_namespace_diagnostics.py](../../scripts/reference_namespace_diagnostics.py)第 72–80、186–208 行；[workspace_diagnostics.py](../../backend/src/novelty_agent_framework/diagnostics/workspace_diagnostics.py)第 62–73 行确认 Runtime 仍调用该脚本。

请求的 resolved_arguments 来自 Harness 的 schema 校验（[tool_call_harness.py](../../backend/src/novelty_agent_framework/core/tool_call_harness.py)第 318–335 行），并非 Reader 执行时解析的真实地址；[reader.py](../../backend/src/novelty_agent_framework/tools/reader.py)第 117–133 行才按 manifest 定位 namespace。诊断仍把请求缺省 namespace 与结果 namespace 比较，再将缺省值转枚举，所以成功自动定位会继续生成 mismatch/invalid namespace。`_read_result` 只识别单个 read_result，未展开 read_results；批读成功可能被误报，子项也没有完整逐项核对。

结论：历史 32 条误报的解释成立，**不能根据后续阶段总结中笼统的“诊断修复”认定这个具体入口已经修复**。当前 [测试](../../tests/test_reference_namespace_diagnostics.py)主要使用显式 namespace 的单读 fixture，未覆盖该缺省地址/批读条件。

## R-02：卡数达标会跳过 Reviewer 技术失败的恢复决策（P1，代码及历史事实确认）

位置：`recovery_policy.py` 第 28–33、54–59 行。

当 valid card count 达到门槛、review.incomplete_reason 为 technical_error 或 budget_exhausted，semantic_gap=false；第 32 行直接 continue，后面的技术错误 STOP/恢复说明分支不会执行。增加 max_rounds 也不会修复这个前置筛选问题。

[最新在线归档](../experiments/20260928_arxiv_web_full_workflow.md)已经记录 NP-2 单卡旧 read_id 错误却不在恢复列表。[test_recovery_closure.py](../../tests/test_recovery_closure.py)第 281 行附近的技术错误测试仍提供数量不足输入，不能证明“数量达标+技术失败”被覆盖。

**补充原因丢失：** `evidence_reviewer.py` 第 380–389 行在全部单卡 technical_error/budget_exhausted 时直接返回新的 insufficient review；第 446–453 行的 execution_issues 继承根本没有执行。原单卡错误留在局部记录，但上层 point review 不继承具体事件，恢复和报告中的根因链会不完整。

## R-03：服务端明确上下文越界仍归 transport，截断无独立处置（P1）

位置：`model_client.py` 第 438–440 行统一把 HTTPError 包成 ModelClientError；[research_task.py](../../backend/src/novelty_agent_framework/workflows/research_task.py)第 475–486 行仅识别本地 ModelContextAdmissionError，否则归 MODEL_TRANSPORT；Reviewer 第 803–823 行同样。

因此准入关闭/observe、计数与实际服务不一致时，上游明确返回“maximum context length”的 400 仍不能进入 context_limit 分类。[既有实验](../experiments/20260928_arxiv_local_live/README.md)已记录这一实际情形。

补充：finish_reason 被 Runtime 保存（`runtime_artifacts.py` 第 429 行），但模型适配/Harness/Reviewer 未据 length 建立独立截断状态，当前 FailureCode 也没有专门输出截断码。截断常落到 JSON 修复或泛化错误；若残余文本恰好满足 schema，没有专门的截断拒绝路径。此项为代码风险，未证明本次历史输出发生截断。

## R-04：Web 模型预算与请求准入次序冲突（P1，补充发现）

位置：`model_client.py` 第 318、340–349 行；[model_budget.py](../../backend/src/novelty_agent_framework/services/model_budget.py)第 48–94 行。

START 在上下文准入前发出；RunModelBudget 在 START 就增加次数和人民币预留，而且明确不回收。于是一个被本地准入拒绝、从未发出 chat 的请求，仍消耗预算。与任务书 T15 的“dispatch 前拒绝且未消费调用预算”不符。上下文测量请求本身可有成本，但不能混成已派发 chat 的预算事实。

同一预算器第 56–58 行仍要求有价格，未定价本地模型被拒绝；第 49 行忽略 RESPONSE_PARSED，只有 event.response 才更新费用估算，所以 Runtime 已保留的“usage 到达但业务解析失败”在 Web ledger 仍显示 failed_billing_unknown。预算预留本身不是实际账单，这里是两个观测入口不一致，不能据此断言多扣了实际费用。

## R-05：arXiv 网页全文单次物理请求双重预留（P1，补充发现）

位置：[arxiv.py](../../backend/src/novelty_agent_framework/tools/database_search/providers/arxiv.py)第 429–436 行先 reserve arxiv_auxiliary，再调用注入的 client.get；[arxiv_web.py](../../backend/src/novelty_agent_framework/tools/database_search/providers/arxiv_web.py)第 696–702 行 ArxivWebSession 又 reserve arxiv_web 后才真正 HTTP。网页全文装配复用该 session，导致一次全文尝试占两个 Provider 名额。

[已归档在线实验](../experiments/20260928_arxiv_local_live/README.md)记载 6 次预留/5 次实际 HTTP，与调用链吻合；当前代码仍保留两处预留。预算临界时外层已占名额、内层拒绝，会连一次请求都没发出。预留数不能用于声称物理请求数。

## 裁定发布与验收边界

Reviewer 的一致性门控不替代全文语义、版本/时间、完整组合关系检查。报告 Gate B 仍非阻断，详见 [05](05_报告编辑与输出.md)。执行成功、artifact 合法、业务充分、review 完成仍未统一为任务书提出的四轴运行终态；已有局部状态不能当作统一契约已完成。

本轮不需要补充实验才能定位上述路径。若要验证本地 HTTP、复现模型引用行为或比较恢复效果，需先征得用户同意；没有把历史通过的测试数当作当前新测结果。
