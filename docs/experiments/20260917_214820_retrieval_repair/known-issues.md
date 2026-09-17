# 检索稳定性：已确认问题与证据归档

| 项目 | 记录 |
|---|---|
| 归档日期 | 2026-09-17 |
| 仓库 | `RikoNJU/Novelty-Multi-Agent-Framework` |
| 核查分支／提交 | `lya` / `00256091346b641834003957721035f5dfa834e5` |
| 重点对象 | `MF2033k6lC / NP-2 / T-1`，历史 `20260916_233840/runs/full/0004–0006` |
| 归档状态 | 证据整理完成；本文件不表示生产补丁、仓库回归或新真实实验已完成 |

## 1. 结论的范围

已确认的是：当前代码存在可解释、在隔离环境下已复现的概念删除与检索提前终止机制；历史 NP-2 的一条 arXiv 首轮路径与该机制相吻合。

尚未确认的是：这两个机制是否足以解释当前全部论文的篇目波动、零卡以及展示效果不佳；修补后是否改善真实检索与证据质量。不能把“机制存在”登记成“全部根因已确定”。

隔离验证采用函数体副本与内存测试替身，不是仓库内直接导入生产函数的 pytest 验证。后续必须迁入仓库完成直接调用测试。[S1]

## 2. 已确认问题

### R-01：基础计划的保留约束没有延续到 fallback

**状态：** 历史行为可核对＋当前代码静态证据＋隔离复现；待仓库内回归与修补。

**位置：** `agents/search_plan_compiler.py` 的 `build_runtime_plan()`、`_assert_anchor_preserved()`、`build_fallback_chain()`、`_lowest_importance_concept()`。[S2]

基础计划生成时已经选择并检查 anchor；后续 fallback 仍按 `(importance, 概念编号)` 选取待删除概念，没有继承该保留约束。NP-2 中 C1（分布式 GNN 训练对象）与 C2（图摘要）重要性同为3，平局规则删除 C1。历史执行记录明确写出这次删除，实际查询变成 `abs:"graph summarization"`。[S3]

隔离 M1 复现了所有基础策略包含 C1、但第一条 fallback 只剩 C2；M2 仅交换概念编号并重映射引用，保留的语义内容就发生变化。[S1]

**修改目标：** 已选定且显式记录的保留约束在后续主检索路径变换中继续生效。不得新增语义裁判；不得硬编码“永远保护 C1”。没有可安全删除概念时跳过该降级变体并记录，而不是生成空查询或删除受保护概念。独立探索路径可以另有规则，但不能冒充受保护主路径。

**验收边界：** 检查的是系统约束的一致性，不证明所选 anchor 在学术上最优。

### R-02：早期结果填满候选额度，截断尚未执行的检索策略

**状态：** 当前代码静态证据＋隔离复现；历史 NP-2 的执行顺序与之吻合；待修补与效果验证。

**位置：** `tools/database_search/structured_retrieval.py::StructuredSourceRetrievalTool._search()`。[S4]

同一个 `candidate_limit` 被用于单次查询返回上限和整条调用的候选数量停止条件。某一早期查询返回足量不同结果后，后续基础策略不再执行。历史首轮 arXiv 记录为：S1 成功零结果；S1-fb1 返回同一组8篇；该调用中没有后续 S2/S3 执行记录。[S3]

隔离 M3/M4 仅把第一条 fallback 的结果从8篇改成7篇，就分别得到“后续 S2 不执行”和“S2 执行、其结果进入候选集合”。[S1]

**修改目标：** 分开管理请求预算、每查询返回上限、候选合并与最终输出上限。基础方向按照明确调度得到执行机会；达到真实资源预算时可以停止，但必须列出未执行方向，不能用“已有8篇”代替检索覆盖完成。

**验收边界：** 现有截断机制可以解释路径对早期命中数量的敏感性；不证明每个未执行查询都能召回高相关论文。

### R-03：审计报告中的固定结论与查询计数不一致

**状态：** 已读脚本与产物直接支持；待修补。

**位置：** `scripts/single_point_stability_audit.py` 与 `20260917_141500_single_point_stability` 归档。[S5]

三次 C0 策略表达式结构相同：S1/S2 均为 `C1 AND C2`，S3 为 `C1 OR C2 OR C3 OR C4`。脚本却固定写入“C0 策略表达式不同”。

`set(expression)` 得到的2只代表两种表达式字符串，不能取代3条策略；S1/S2 的 `use_alias` 不同，也不能据此合并成同一实际数据库请求。

**修改目标：** 结论由字段差分与实际事件产生；分别记录策略数、DSL 结构数、适配后请求数、执行请求数和去重文献数。保留旧归档原件，通过更正说明和重新生成的报告修正，不覆盖原始证据。

## 3. 为下一次真实实验必须补齐的观测缺口

这些是调试与回放能力的缺口，不单独登记为检索语义失败的根因。

| 编号 | 本次代码核查事实 | 需要补齐 |
|---|---|---|
| D-01 | `ModelCallEvent` 仅有调用身份、时间、消息数量、响应和错误，没有完整请求消息／实际调用选项；`record_model_call()` 主要持久化用量和错误。[S6] | 在模型请求边界增加脱敏的实际请求快照、响应内容、调用关联及失败记录；不能只改最终 JSON 写入器 |
| D-02 | `max_inline_bytes` 默认256000；`_prepare_value()` 对过长字符串及二进制返回大小、哈希和省略说明，没有在该函数中保存可读取的完整内容。[S7] | 完整载荷另存文件，索引含相对路径与哈希；哈希不能代替载荷 |
| D-03 | `RuntimeArtifactManager.finish_run()` 自带归档路径复制 summary 和 diagnostics，不复制所有 stage/tool/LLM 载荷。[S8] | 核实外层归档器；最终导出包必须包含本轮回放需要的全部引用，已有整包归档则复用 |
| D-04 | 当前工具记录已有模型参数、解析后的参数、原始与标准化结果字段。[S6] | 复用这些记录，补工具内部查询链、未执行原因、节点前状态和多任务关联；不重建第二套日志 |

## 4. 暂不下结论的事项

NP-2 的三次完整上游对象并非完全相同；原始 Planner 请求与 Draft 不完整，不能证明同输入下 Planner 行为如何。已核对的一条 arXiv 查询链结果相同，不能推广为所有 Provider 稳定。严格标题限制是否损害召回、阅读选段和成卡触发是否另有问题，仍需局部交叉对照。M1–M4 没有证明修复后的真实召回或报告质量。

不以卡片数量、文献 Jaccard 或一次报告成功单独判定整体稳定性。当前无独立相关性标注，不宣称已测得真实召回率。

## 5. 证据索引

所有代码路径均相对仓库根目录，核查提交为上述 `0025609…`。

- **[S1]** 会话附件 `离线控制流验证_0025609.py`、`离线控制流验证结果_0025609.json`。测试范围与局限见结果中的 `scope`、`limitations`。
- **[S2]** `backend/src/novelty_agent_framework/agents/search_plan_compiler.py`；已记录 blob：`13cc9850f5a60ba817e036fff0ced26cca9752f8`。
- **[S3]** `docs/experiments/20260916_233840/runs/full/0004–0006/MF2033k6lC/research-runs/NP-2/T-1/attempt-1.json`；逐次检查 `producer=structured_source_retrieval:arxiv`、`search_executions`、`fallback_reason`、结果身份。
- **[S4]** `backend/src/novelty_agent_framework/tools/database_search/structured_retrieval.py`；已记录 blob：`9ce6521acda3e245d8e7ce1d0b95768d01951311`。
- **[S5]** `scripts/single_point_stability_audit.py`；`docs/experiments/20260917_141500_single_point_stability/compiler-comparison/P4_C0/`、`P5_C0/`、`P6_C0/`；后续 `20260917_191302_single_point_stability/report.md` 已缩小为材料核对结论。
- **[S6]** `backend/env/model_client.py::ModelCallEvent`、`_emit_model_call()`；`backend/src/novelty_agent_framework/core/runtime_artifacts.py::record_model_call()`、`start_tool_call()`、`finish_tool_call()`。
- **[S7]** 同上 `runtime_artifacts.py::RuntimeDebugConfig`、`_prepare_value()`，尤其大字符串和 bytes 分支。
- **[S8]** 同上 `runtime_artifacts.py::finish_run()`；只证明该函数的内置归档行为，不断言所有外层实验归档均缺失。

### 会话证据文件哈希

| 文件 | SHA-256 |
|---|---|
| `离线控制流验证_0025609.py` | `f4e9216e9c1f282b2801a8ebb74f09665db25d81a8c4c14134b520a877127356` |
| `离线控制流验证结果_0025609.json` | `cd8603a97428d00e2cfa3d37a83babda6ed6b516f14ad34fd45805d203d39448` |

后续每条问题状态依次记录为：`confirmed_mechanism → reproduced_in_repo → patched → mechanism_verified → effect_evaluated`。后两项不得仅凭提交了代码自动更新。

## 本轮实施附记（2026-09-17 21:48 +08:00）

本节为新增记录；上面的原始归档文字保持不变。当前工作树尚未提交，因此没有修复提交号。

| 问题 | 当前状态 | 仓库内证据 | 实际效果 |
|---|---|---|---|
| R-01 | `mechanism_verified`（受测路径） | `tests/test_retrieval_repair.py::test_protected_concept_remains_in_fallback`、`tests/test_fallback_chain.py::test_explicit_anchor_survives_importance_tie_and_renaming`；直接调用生产函数 | 真实检索效果待定 |
| R-02 | `mechanism_verified`（受测路径） | `tests/test_retrieval_repair.py::test_eight_early_hits_do_not_suppress_other_base_directions`、`test_budget_marks_unexecuted_base_queries`；直接调用生产检索器，外部 Provider 用内存替身 | 真实检索效果待定 |
| R-03 | `mechanism_verified`（本地报告） | `tests/test_single_point_stability_audit.py`；新报告在 `analysis/audit-correction/report.md` | 旧归档未覆盖；适配后及执行请求数仍未从历史材料测得 |

上述测试命令与结果见 `tests/targeted-pytest.log`。四变体控制流测试使用同一查询到响应的合成映射，不评价文献相关性。

## 完整运行后的状态更新（2026-09-17）

一次有界 BFE 完整下游运行已完成：`runs/full/0001`，75 次模型调用、27 次物理 Provider 请求、2.0774424 元。真实计划的 F0 fallback 会在 NP-1/2/3 至少一处删去 C1，F1 均保留；R-01 的真实执行链机制已观察。三个点的三个 arXiv 基础策略均执行，但 NP-3 在第三个基础方向才达到 8 篇，故 R-02 的实际增益仍未知。三点 Reviewer 都为 `insufficient_evidence`。Springer HTTP 404、Reader 参数错误和 Harness 顺序拒绝单独记录；不得归为文献不相关。见 `analysis/live-boundary-cross-validation.md`。
