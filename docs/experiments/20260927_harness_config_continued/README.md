# Harness 与配置管理审查：服务恢复后的续查

**任务状态更正：整份任务尚未完成验收。** 本文汇总的是两轮阶段性交付；请以[任务书逐项复核](task_acceptance.md)判断完成情况。其中另记录了本次复核发现的取消/解析失败usage和Reviewer工具失败分类缺口。

日期：2026-09-27。延续[任务书](../../../task/Novelty%20Framework%20Harness%20与配置管理系统审查任务定义.md)与[首轮审查](../20260927_harness_config_audit/README.md)。服务恢复后完成本地 Reader 对照、用户明确授权范围内的一轮 arXiv 整流程，以及新工程保护机制的验证。未更换更强模型，未新增云端模型能力，未降低 Evidence/Reviewer 标准，正式报告视觉排版保持原样。

**运行完成不等于查新成功。** 本次整流程 20 次模型请求都使用本地 Qwen，4 次物理 arXiv 搜索全部 HTTP406，最终 0 Card、4 点均无法裁定。Harness 修复改善了可观测性、失败前拦截与成果保存；尚未证明小模型可自主稳定完成查新。

## 交付索引

- [完整在线复核、逐点生命周期、预算与模型/域名核对](live_validation.md)，[机器指标及来源散列](live_metrics.json)，[另存的检索限制修订报告](amended-report/MF2033k6lC-report.md)。
- [上下文准入与实际服务计数](context_admission.md)，[16 次请求的 tokenizer/usage 对账](vllm_tokenization_comparison.json)。
- [Evidence 检查点、故障保留与显式恢复](evidence_checkpoint.md)。
- [Reviewer 诊断修复与汇总恢复边界](reviewer_diagnostics.md)。
- [实际 Prompt 绑定、增强 Profile 和使用说明](configuration.md)，[预检快照](guarded-config-manifest.json)。
- [全套离线回归](final-tests.log)、[机器测试结果](final-tests.xml)、[本轮末代码累计补丁](implementation.patch)、[已知密钥扫描](secret_scan.json)。

## 新的真实实验事实

| 实验 | 实际观察 | 可以证明 / 不能证明 |
|---|---|---|
| 固定 Reader 输入 off/on，各一次 | 模型调用 10→6、物理 Reader 8→4、输入 token 75,976→35,386；独立覆盖字符均 3,026；两组 0 replay、0 Card；耗时 23.571→34.573 秒 | 状态开启样本重复读取较少；不能归因于缓存命中、不能称提速或证据质量提高，更不能声称稳定性 |
| 同原论文一轮整流程 | 20 次本地模型调用、4 次 arXiv HTTP406、0 Reader、0 Card；4 点都有 Task/Plan/Review/Report | 逐点下游没有静默遗漏；本轮无法评价真实证据与 Reviewer 语义能力；HTTP406 根因未知 |
| 提取去重链审计 | 非法 `3→2` 因代表也被删除而拒绝，Sketch-DBH保留为 pending；形式合法的 `2→1` 仍错删 DSGNN 框架机制 | 恢复 Sketch-DBH 后续核验机会；点数变多不代表贡献完整；语义等价验证仍缺失 |
| 上下文计数对账 | 本机 vLLM 0.8.5.post1 下，16 份真实历史请求的测量输入 token 与 provider usage 逐条一致 | 支持显式、版本受限的工具模板兼容；另一个超限探针 0 chat，允许探针 580 输入与 usage 一致；不能推广到任意模型/服务/多模态请求 |
| 检查点本地链路探针 | 固定既有合成材料、两次人工约束工具选择；Reader→submit 经原 Builder 保存，随后注入故障；PARTIAL 的 1 张卡可恢复 | 验证保存/恢复链路；不是原论文自主研究产卡，也未执行 Reviewer |

整流程使用已准备的 `full_live_profile.json`，1 轮、1 并发，限 40 次模型调用与 12 次物理检索请求。实际只向 `export.arxiv.org/api/query` 发出 4 次检索；其余 reference_search 是本地查询，未发现 web/browser 或其他 Provider 请求。用户已明确授权这一 arXiv 内容和目的地址范围。此前自动审批因缺少明确外发授权拒绝了一次启动；当时未执行，授权后才运行。

本次三份主要样本（整流程与 Reader 两组）共 36 次本地模型调用，188,116 total token。该数不含后续专门的上下文与检查点探针，不能用作全部审查活动总用量。未知 API 报价与本地算力成本保持 UNPRICED/PARTIAL，不解释为免费。

## 本轮新增工程改动

| 具体故障 | 改动与类别 | 实验条件 / 验证边界 |
|---|---|---|
| `context_window` 只是元数据，超限请求到服务后才失败 | ModelClient 在实际序列化请求上做精确计数准入；有效窗口取配置和服务窗口较小值，包含输出预留；Runtime 分开记录计数请求、拒绝与 chat transport | 默认 off；显式配置 enforce 才拦截。超限不截断引文，测量不可靠则按明确策略拒绝。尚无上下文压缩/自动恢复 |
| 已读材料和局部草稿只能等最终 finish 后变卡 | invocation 隔离的 `submit_evidence`；原 Builder 校验后原子保存；故障时保留 PARTIAL；恢复重验范围/Artifact/hash/原文 | 默认 off；新增工具动作仍消耗预算；Validator/Reviewer 标准不变。不是完整工作流断点续跑 |
| 合法 Reviewer 增量证据被旧诊断索引判缺失 | 诊断按当前 Review 合并合法的 `review_evidence`，校验 origin Card/Work/point，禁止跨 Review 借用或修补原始 Card 缺证 | 真实历史 2 条误报消除；不会把诊断 `ok` 当作语义裁定；生产 Reviewer 汇总恢复未实现 |
| 角色配置列了 Prompt 却实际使用硬编码模板 | Coordinator/PointExtractor 改为按操作名称选择；保存所选版本/hash；自定义旧清单预检报错 | 默认仍选原模板；真实 factory/模型消息构造回归。不是为了让小模型通过而改提示语义 |
| Report 有执行失败记录，却固定宣称无检索事实 | 将已有执行状态确定性绑定到限制说明，保留失败/未执行与已知 HTTP 状态 | 不新增检索、不猜406根因、不改变 Review/verdict；原报告保留，另存离线重绑版本 |

## 验收状态与剩余边界

**已验证的限定修复**：调用级精确上下文预拒绝及记录；局部 Builder 卡的原子保存与显式恢复；Reviewer 增量证据诊断误报；五个命名操作 Prompt 的实际绑定与冻结；已有检索执行事实传入报告。具体证据见各分项，不将离线故障注入等同真实端到端语义能力。

**有所改善**：Reader状态可见后本次少做重复读取；去重动作可审计并保留非法删除候选；用户可以用 Profile 显式切换新机制。Reader 单次样本、没有 replay、没有有效 Card，均不足以证明稳定净收益。

**仍未解决或未知**：arXiv查询HTTP406根因；DSGNN等技术机制被语义错合并；实验结果被补核为无技术特征查新点；真实自主产卡能力与同输入多次运行稳定性；Reviewer汇总失败后的点级事实展示/恢复；通用缺口驱动补检调度；跨服务的通用精确计数和上下文压缩；全部Web/legacy入口统一preflight。没有足够证据把这些剩余问题全部定性为小模型能力边界。

下一步优先处理作者贡献/技术特征→候选→合并代表的覆盖账本，只有来源支持且覆盖保持的删除才能获得完整性确认；同时定位 arXiv 查询层失败。待稳定获得真实可读候选后，才适合做 checkpoint/context 开关的独立多样本消融和完整 Reviewer 质量评估。无需扩大 Provider 数量或替换强模型来掩盖当前缺口。

## 可复核性与工作区

所有失败与成功样本分目录保存，服务中断时的旧失败目录未覆盖。Reader A/B 保留相同输入 hash、起始实现 patch、逐调用及工具记录。full live 保留原始输入 hash、有效配置、dirty commit/源码 fingerprint 和全部 Runtime；没有单独保存其启动时的完整源码 patch，且运行期间其他代理在编辑未启用的新模块。因此最终累计 patch 不能当作该 full live 的精确启动版本，也不将它称为增强 Profile 的端到端验收。

`implementation.patch` 是本轮结束时相对于当前 HEAD 的累计工程改动（包含首轮），不含用户预先修改的本地LLM使用手册。工作区改动尚未提交或推送。报告与运行产物按各自采集时刻解释，不覆盖历史配置来制造统一条件。

最终离线回归 **1,104 passed / 6 live deselected**，24.96 秒，仅有既有 Starlette 弃用警告。第一次整合回归的 1 项失败是旧测试要求 limitations 为空；修正后仅允许真实的覆盖未知提示，并继续禁止 Gate A 内部诊断泄漏到正式报告。修前失败日志已保留。`git diff --check`、累计补丁反向应用检查、48 份源码与导出补丁的一致性均通过，见 [validation.json](validation.json)。已清理两次 pytest 生成的合成 Runtime 目录，真实运行保留。
