# Novelty Harness 与配置管理审查：证据、修复与边界

2026-09-27。依据 [任务书](../../../task/Novelty%20Framework%20Harness%20与配置管理系统审查任务定义.md)。本轮完成代码/历史轨迹调查、局部复现、限定修复、配置实验基础和回归；**没有证明小模型已具备完整查新能力，也没有宣称全部 Harness 缺口已经解决。**

最重要的结论是：本地失败同时包含确定性工程缺口、Provider操作级故障和模型语义错误。它们不能统一解释为权限不足或模型太弱。历史 `SUCCESS` 仅证明流程完成；原本地报告的两个点均无有效最终卡，不能支撑查新裁定。

## 交付索引

- [Harness / Context / usage 审查](harness_findings.md)，[六组历史轨迹逐调用核对](harness_trace_audit.json)。
- [查新点 / Reviewer / Report / 错误与恢复方案](integrity_findings.md)，[逐候选与逐确认点账本](integrity_ledger.json)。
- [工具、现有和候选 Provider 矩阵](provider_findings.md)，含官方资料、授权条件与候选实施顺序。
- [Configuration 审查与使用说明](config_findings.md)，[本地配置Manifest](local-config-manifest.json)，[修前复现](config_before.json)。
- [局部去重协议对照](dedup_local_pair/manifest.json)、[模型连接状态](model-connectivity.json)。
- [修前离线基线](baseline-tests.log)、[最终离线回归](final-tests.log)、[本轮可重建实现patch](implementation.patch)。

## 现象 → 证据 → 结论

| 现象 | 已确认证据 | 归因与边界 |
|---|---|---|
| 查新点由候选4个变为最终2个 | 09-24生成已含Sketch-DBH；去重输出裸 `[2,3,4]`；补核仅恢复DSGNN | 点丢失发生在提取去重，不是ResearchTask或Report丢失。原输入已包含作者贡献段 |
| 大量Read后没有EvidenceCard | 同次NP-1有16个成功Reader，仅3个独立区间，13次重复，随后reader预算耗尽；另一单任务有8次EOF空读 | Reader缺机械状态约束已证实。卡片语义形成仍依赖模型finish，缓存不保证产卡 |
| 模型请求失败 | 历史32,768窗口请求57,360输入+4,096输出；另一8,192窗口请求4,193+4,096 | profile有context_window，但无实际输入准入；是Harness/部署能力契约缺口，不能算语义能力失败 |
| Reviewer失败被描述为关键证据不足 | Workflow的技术异常兜底未设置incomplete_reason；旧接口异常甚至没有Review行 | 技术失败与材料/语义不足混淆，已局部修复；有材料时真正语义核验正确性仍未全部保证 |
| Springer失败后放宽策略未运行 | 历史及本轮同查询404明确表示no matching data | 精确Provider业务响应应为成功零命中；已修复并在线复验，普通404仍失败 |
| arXiv可否用不清楚 | 本轮关键词查询406、known-ID查询200 | 操作级健康不同，406细因Unknown；不可归为认证失败或没有论文 |
| 本地成本显示0、失败请求显示完整计费 | usage缺失时原汇总cost_completeness=COMPLETE；unpriced总价为0 | 原逐调用UNPRICED判断正确，汇总语义有误；现总价null、保留已知小计、标PARTIAL |
| 配置难以解释和冻结 | 安全快照泄漏虚构嵌套key；post-load负预算通过；无统一Profile来源；未知Provider晚发现 | 新增Profile/优先级/预检/脱敏Manifest并接入实际入口；legacy/能力schema仍未全面收敛 |

强弱历史比较使用相同PaperInput/full_text散列，但Prompt、代码与选项并非完全相同。只能提出failure differential假设，不能把历史差额当作本轮Harness改善幅度。没有调用更强云端模型、没有新增云端能力、没有更换论文输入来制造成功。

## 已实施的限定改动及验证口径

| 改动 | 类别 / 解决的Failure Mode | 自由度与实验条件 | 有效性证明 |
|---|---|---|---|
| 删除须提供保留代表和理由；非法映射候选pending_dedup | Harness：无可审计依据的点删除 | 收紧删除动作协议，Prompt v5→v6，必须视为实验变量 | 冻结4候选旧新Qwen各一次；离线拒绝裸删除/非法映射。新协议仍语义错删，**只算审计改善** |
| `reuse_reader_results`：请求缓存、范围/EOF状态、namespace隔离 | Harness：重复I/O与EOF预算浪费 | 默认false，Profile可开；合法其他区间/前段可读；模型turn仍消耗 | 离线固定工具调用序列检查物理读取、字符预算、provenance不变；在线对照无有效样本 |
| Reviewer异常兜底technical_error，每确认点保留Review | Harness/业务状态：技术失败包装为语义结论 | 不修改Evidence或Reviewer核验标准，不将有效语义不足改成技术失败 | 新增异常、旧接口与语义对照回归；报告仍逐点绑定，不改视觉 |
| Springer精确no-data 404识别 | Provider：零命中中断查询放宽 | 不改检索输入/Provider默认开关；只恢复原确定性放宽链 | 同输入关闭修复两项失败，修后相关55项通过；在线404→成功空结果 |
| 失败/未定价成本总额null+known_amount_rmb | Runtime：Unknown被表示为零/完整 | Token与API估价分开，不估造GPU成本 | 对已定价、未定价、usage缺失及混合调用的汇总/显示回归 |
| 批量Reader诊断逐项展开 | Diagnostics：新reads[]被旧诊断误报 | 只更新诊断契约；工具调用数和读取项数分别统计 | 单读兼容、成功batch、部分失败batch回归 |
| Profile、再校验、来源/内容hash、预检与脱敏 | Configuration：隐式覆盖和不可解释实验 | CLI未指定参数现在沿用配置；示例Profile显式固定1轮1并发 | 优先级/字符串false/无效值/密钥与URL脱敏/实际入口快照测试；本地预检零error |

报告排版冻结。修改只涉及报告的数据/失败状态绑定；Runtime调试摘要的Unknown成本显示不属于正式报告版式重构。

## 最终回归与实际入口检查

完整离线回归 **1,020 passed / 6 live deselected**，22.79秒；仅有既有Starlette弃用提示。修前基线957通过、3失败；其中两个测试断言/桩仍依赖旧契约，另一个使用假浏览器却调用了真实系统库检查。本轮更新测试契约和隔离，不把这些离线测试的通过声称为真实Chromium运行验收。

真实PaperInput入口 `--check-config` 状态为 `PREFLIGHT_PASSED`，无网络请求；[入口run](entry-preflight-run.json)、[配置Manifest](entry-preflight-experiment-manifest.json)和[预检结果](entry-preflight-preflight.json)齐全。原始输入未改，启用Reader缓存的配置已到达实际入口；这不等于整流程运行通过。

`git diff --check`与实现patch的反向`--check`均通过。新增实验包对已有四个真实secret值进行只报告匹配计数的扫描，未命中，见 [secret_scan.json](secret_scan.json)。这项扫描覆盖当前已知密钥，脱敏回归另覆盖虚构嵌套key、Authorization、URL userinfo、sig和配置异常输入。

## 在线实验与失败说明

开始时 `http://127.0.0.1:8000/v1/models` 返回 `qwen2.5-7b-instruct`、`max_model_len=32768`。固定候选去重两次真实调用成功：共4,846输入、77输出、4,923 Total Token，API价格/本地计算成本未知。

**新协议反例仍存在**：Qwen把DSGNN框架映射成Sketch-DBH算法的重复项，理由抄写模板。映射形式有效不代表技术等价。这不足以确认“剩余只是小模型能力边界”，因为源文本支持与合并后特征覆盖仍缺充分约束。

随后Reader缓存开/关两组首请求均HTTP502，0 usage、0工具调用；绕过代理的有界复验也连接失败。当前执行环境的8000无监听、无既有SSH隧道进程，direct loopback连接超时。**服务器模型本身状态未知，已向用户报告。** 失败目录保留，没有覆盖成成功；没有继续无限重试或换云端模型。本轮没有有效Reader在线效益估计，也没有修改后的整流程成功声明。

独立Provider验证成功：Springer Meta200+摘要，OA JATS200+44,982字符正文；ScienceDirect/IEEE缺凭据，仅离线契约，不声称真实可用。

## 验收状态

**已验证解决（限定场景）**：Reviewer技术兜底原因遗漏、Springer特定no-data误分类、失败usage/未知价格成本汇总、配置已复现的嵌套secret快照问题、CLI显式覆盖再校验、批量Reader旧诊断误报、缓存启用时的重复物理读取和已知EOF越界读取。

**有所改善但仍存在**：查新点删除可审计，但语义错合并及特征丢失仍存在；Reader状态可见，但模型仍可能耗完turn且不产卡；Profile与Manifest可用，但并非所有部署/legacy入口已使用完整preflight，角色Prompt绑定和模型能力表达尚未统一。

**确认属于模型能力边界**：本轮没有足够受控证据确认任何剩余问题纯粹属于这一类。新协议对照展示具体语义错误，不能排除Harness仍未提供充分约束/恢复的影响。

**仍然无法确定或未完成**：arXiv406根因；模型连接中途失效的远端原因；缓存对真实有效Evidence和Reviewer质量的净改善；同输入重复全流程稳定性；精确上下文准入/压缩策略；原文支持的点合并核验；已确认局部事实在Reviewer汇总失败后的点级保留；跨Provider细分授权与全文失败分类；统一缺口驱动恢复调度。

## 下一阶段可执行顺序

1. 恢复已有模型连接后，用保留的固定Reader输入重新进行缓存off/on对照；比较物理I/O、模型动作、EOF、唯一读取区间、最终有效卡、Reviewer绑定和Token，而不是只比较SUCCESS。现有失败观察不能覆写。
2. 优先实现调用级Context准入：读取实际服务窗口/Tokenizer，计入系统Prompt、工具schema、历史与输出预留；超限时保留结构化机械状态和Evidence provenance，采用已验证的按需原文/任务切分；无法保证时明确拒绝并保存可恢复状态。不能简单截断引用文本。
3. 给PointExtractor增加作者声明/特征→候选→合并代表覆盖账本；源文本等价未核实的删除保留待核验。用本次DSGNN→Sketch-DBH反例作冻结holdout，不通过凑点数验收。
4. 把工具事实、Evidence草稿/已验证卡、Reviewer局部核验结果持久化为可恢复状态；在汇总超时后仅重跑汇总。语义结论仍由模型给出，经确定性绑定和引用校验后发布。
5. 逐边界落地分项报告中的错误事件结构与恢复动作，再扩展Provider。先评估Crossref的DOI核验、OpenAlex的跨出版社发现/OA定位；中文/专利/科技成果依据机构授权和数据契约立项。
6. 统一遗留角色Prompt选择、transport/env解析与模型能力schema；给所有正式入口接入同一preflight，并补充依赖/模型服务版本冻结。

后续每项都需保留相同输入、源代码/Prompt/配置hash、逐调用结果及失败状态，不把未知改写成无相关文献。
