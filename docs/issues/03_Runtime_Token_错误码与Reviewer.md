# 03｜Runtime、Token、错误码与 Reviewer：当前项目核查

> **补测更新（2026-09-30）**：用户已授权离线、真实本地模型及 arXiv/Springer 实验，最新结果见文末“授权补测”及[实验总表](../experiments/20260930_issue_audit_live/README.md)。下方原正文保留第一阶段静态核查记录，其中“未测试/需另行询问”仅描述当时状态。

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

## 2026-09-30 授权补测结果

[确定性反例](../experiments/20260930_issue_audit_live/boundary-results.json) 已复现：自动 namespace 成功读取却报 mismatch/invalid，批读漏展开；卡数达标的 Reviewer 技术失败无 recovery decision，而数量不足对照有 STOP；全部单卡技术失败汇总丢 model.transport 事件。完整真实链路也出现 6 个成功 Reader 调用被 namespace 诊断报 12 个错误；NP-3 一卡达标且技术失败，最终恢复列表没有该点，point execution_issues 为空。

[真实 context 400](../experiments/20260930_issue_audit_live/local-context-results.json) 被 `_execution_failure` 归 model.transport；enforce 拒绝归 model.context_limit，但仍占 Runtime 次数。离线事件对照显示 Runtime 保留 10 input + 2 output usage，Web ledger 忽略 RESPONSE_PARSED，随后业务解析异常仍记 failed_billing_unknown；本地未定价模型被 Web budget 拒绝。没有云模型或实付实验。

[独立 Provider 探针](../experiments/20260930_issue_audit_live/provider-results.json) 实测 arXiv 全文 1 次 HTTP / 2 次预算预留；本次 API/Web 检索均成功，历史 406 不能继续当作当前状态。Springer 普通检索成功；显式 OA 条件查询返回 403、公开 DOI 的 OA 请求返回 404。仅记录状态，不推定无权限、限额或论文不存在为唯一根因。

### R-06：未提及特征被当作矛盾，且引用修复仍不闭合（P1，真实模型复现）

位置：[evidence_reviewer.py](../../backend/src/novelty_agent_framework/agents/evidence_reviewer.py) 的单卡解析/引用注册、`_validate_verdict_coverage` 附近（第 303–305、1135–1171 行）；数据结构 [domain.py](../../backend/src/novelty_agent_framework/schemas/domain.py) 第 329–336 行。

完整链路 NP-2 的四条 feature_comparisons 以 does not mention / different approach 等理由给 contradicted。这些理由只能证明所给片段未建立支持，不能自动证明机制矛盾。结构模型允许合法枚举和已绑定 evidence ID，覆盖门控主要约束 not_novel，未核实 relation 与引文语义。

[修正后的固定材料对照](../experiments/20260930_issue_audit_live/semantic-controls-v2/results.json) 使用当天获取的《Attention Is All You Need》全文和真实 Reader 溯源，三类关系各重复两次：明确支持和明确矛盾共四次均因引用未读 read_id 变技术失败；材料未涉及的蛋白质定位评估两次均判 contradicted，并在 summary 保留。0/6 符合预声明关系标准；这是小样本契约/语义反例，不是总体模型准确率。四次失败的 coverage/引用拒绝发挥了保守保护，不能称错误最终裁定已经发布。

### R-07：跨 Provider 的物理请求统计不完整（P1，新发现）

位置：[common.py](../../backend/src/novelty_agent_framework/tools/database_search/providers/common.py) 第 116–137 行，[runtime_artifacts.py](../../backend/src/novelty_agent_framework/core/runtime_artifacts.py) 第 1287–1316 行。

通用鉴权数据库客户端只 reserve `authenticated_database`，没有与 arXiv 一致的 physical_request 事件。真实完整链路预算为 arxiv_web=21、authenticated_database=6、arxiv_auxiliary=3，而 provider_requests 摘要仅 arXiv 21。Springer 六次成功检索在业务记录中可见，但物理事件摘要不计入；不能拿 21 或 30 当全部外部实际请求数。详见 [对账](../experiments/20260930_issue_audit_live/workflow-analysis.json)。

### R-08：Springer 冷实例无法解析自身检索产出的裸 DOI（P2，新发现）

位置：[springer.py](../../backend/src/novelty_agent_framework/tools/database_search/providers/springer.py) 第 104–116、350 附近和 433–439 行。搜索结果 document_id 取裸 DOI；同实例依赖 `_records` 取回 doi，缓存未持久化；冷实例 `_doi_from_identifier` 只接收 doi: 或 URL 前缀。

[实测](../experiments/20260930_issue_audit_live/springer-identifier-results.json)：裸 DOI 零 HTTP 直接 None；同值添加 doi: 才真正请求，收到 404。该对照证明地址处理不一致，不证明该 DOI 全文应可得。重建适配器后的已保存裸 DOI 存在获取被静默跳过风险；尚未运行完整进程重启恢复场景。
