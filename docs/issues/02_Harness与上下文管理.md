# 02｜Harness 与上下文管理：当前项目核查

> **补测更新（2026-09-30）**：用户已授权离线、真实本地模型及 arXiv/Springer 实验，最新结果见文末“授权补测”及[实验总表](../experiments/20260930_issue_audit_live/README.md)。下方原正文保留第一阶段静态核查记录，其中“未测试/需另行询问”仅描述当时状态。

核查日期：2026-09-30；源码 `3bd1d7f282e61fb2b3b599c4f37ca586da1e8238`。对应 [任务 02](../../task/2026-09-27/分卷/02_Harness与上下文管理.md)。仅静态分析和既有记录阅读，未执行测试或补充实验。

## 逐项核对

| 项目 | 当前状态 | 位置与原因 |
| --- | --- | --- |
| 中途提交有效卡片 | 部分已处理 | [research_task.py](../../backend/src/novelty_agent_framework/workflows/research_task.py)第 111–134 行接入可选 checkpoint；[evidence_checkpoint.py](../../backend/src/novelty_agent_framework/tools/evidence_checkpoint.py)第 76–98 行先走原 Builder 再持久化，第 117–178 行合并/显式恢复。仍依赖模型主动调用 submit_evidence，不是每候选强制处理状态机。 |
| 默认启用候选治理 | 尚未实现 | `research_task.py` 第 69–71 行 Reader 重用、checkpoint、状态投影默认 false；[schemas.py](../../backend/src/novelty_agent_framework/config/schemas.py)第 66–68 行同样。guarded/closure profiles 可以开启，不能把“功能存在”写成“任意默认入口均生效”。 |
| Reader 去重、EOF | 部分已处理 | [tool_call_harness.py](../../backend/src/novelty_agent_framework/core/tool_call_harness.py)第 579–626 行有请求重用和 EOF；但不是按已读区间求增量。详见下文。 |
| 状态投影与历史压缩 | 前者已实现，后者未实现 | `tool_call_harness.py` 第 672–684 行仍追加全部消息；第 712–716 行仅额外插入一份机械状态，原 trace 保留。不能把它称为上下文压缩。 |
| 请求前上下文准入 | 已实现但有配置条件 | [context_admission.py](../../backend/env/context_admission.py)第 21–27、79–139 行实现精确计数及输入+输出检查；默认 off，observe 也允许越界请求；enforce 才拒绝。没有自动缩减/恢复超限任务。 |
| 多工具调用 | 旧缺口仍在 | `tool_call_harness.py` 第 284–305 行明确 SERIAL_FIRST_CALL，丢弃后续调用，仅记 error trace。不是执行完整列表。没有本轮证据表明它导致某次历史失败。 |
| 能力与阶段一致 | 部分实现 | 实际 registry 限制工具，RecoveryToolRegistry 限定恢复动作；但普通研究阶段仍可自由选择已注册工具。`research_task.py` 第 299–304 行无条件加载两个 skill 文本，未建立任务书所提统一 CapabilityManifest。 |
| 抽取覆盖 | 已有保守去重和账本，全文覆盖未验证 | 具体限制见 [01](01_实验复盘与总判断.md)；不能用多输出几个点替代必要特征覆盖。 |

## H-01：相同结果仍重复进入模型历史（P1，代码确认）

位置：`tool_call_harness.py` 第 345–362、611–614、672–684 行。

触发：启用 `reuse_reader_results` 后再次提交完全相同的 Reader 参数。缓存返回 `previous` 的完整 model_context，随后序列化成新的 tool message 并加入 log；下一次模型请求同时包含原结果和重放正文。因此该功能减少物理读取和阅读预算消耗，却未减少重复正文 token。连续重放仍消耗模型轮次，也没有任务书建议的连续无新增区间阈值触发分类/提交。

另一缺口：缓存键为完整参数 JSON。相同 artifact、char_start=0，先读 max_chars=8,000 再读 16,000，若全文实际上只有 1,205 字符，两次有效范围相同，但参数不同且起点不在 EOF 后，第 611、620 行均不匹配，仍会物理重读。显式/省略 namespace、批次组合变化也不能普遍归一为同一有效区间。

缓存保存了 sha256，但请求重放路径不重新检查当前 hash；其安全边界依赖单次 invocation 内资产不变。此处是限定条件，未证明真实运行发生资产替换。

## H-02：准入守卫不能解决长轨迹的产证据问题（P1，代码及历史记录确认）

原文引文和 trace 保留是正确的审计需求，但目前持久证据与模型工作记忆没有分开。全历史 + 重放正文 + 机械状态共同增长；enforce 可以拒绝请求，无法自动转为候选级短上下文继续完成。关闭或 observe 时仍可发出超限请求。

[既有在线实验](../experiments/20260928_arxiv_local_live/README.md)记录 33,437 输入 + 4,096 输出超出 32,768，配置未启用严格准入。这是历史证据，不是本轮重现；不能宣称 guard 已覆盖所有部署配置，也不能把累计 token 当单请求长度。

## H-03：Researcher 的“预留收尾”实际上未预留（P2，代码确认）

位置：`research_task.py` 第 96–108 行；`tool_call_harness.py` 第 86、124–185、222 行。

Researcher 固定 `finalize_on_budget=True`，却未传 `reserve_final_turn`，其默认 false。max_steps 可全部用于探索，之后再追加一次 finalization；格式修复、卡片纠正又在 Harness 外各最多一次（`research_task.py` 第 175–179、205–212 行）。因此 `max_steps` 不能解释为该任务所有模型请求的总上限；全局模型预算临近耗尽时，所谓收尾可能没有剩余额度。Reviewer 单卡路径显式开启 reserve_final_turn，二者策略不同。

## 现有保护及剩余验证

检查点恢复会重读并核对资产、原始切片和 Builder 约束；它保存的是已提交成果，不是整个进程的模型/工具预算账本。默认关闭时，终态格式失败仍可能只有 reads 而无 cards。

已有 [Reader 重复实验](../experiments/20260927_harness_config_closure/reader_repeated_local.md)和 [上下文投影记录](../experiments/20260927_harness_config_closure/context_projection.md)不能证明稳定自主成证或长上下文净改善。当前无需实验即可定位上述分支；若以后要验证重复参数变体、收尾预算或长轨迹收益，应先取得用户同意，再做离线用例或受控模型对照。本轮未运行。

## 2026-09-30 授权补测：上下文和收尾边界

[边界结果](../experiments/20260930_issue_audit_live/boundary-results.json) 使用真实 ReferenceStore/Reader 与脚本化模型驱动，未模拟被测 Reader 行为：

- 完全相同读取参数：物理读取 1 次，复用标记 true，但最终模型输入中正文仍出现 2 次；复用解决 I/O，未消除重复上下文。
- 同一短文改 max_chars 1000→2000：实际读取范围和正文相同，仍物理读取 2 次，未复用。
- max_turns=2、finalize_on_budget=true：reserve_final_turn=false 实际调用 3 次，true 时 2 次。确认 H-03 的收尾超额；这是调用次序对照，不是模型能力实验。

[真实上下文实验](../experiments/20260930_issue_audit_live/local-context-results.json)：32768 窗口收到 34030 input + 3 reserved output 时，关闭准入的服务端请求返回 400；enforce 使用真实 /tokenize 在 chat 前拒绝。两种情况下 cap=1 的下一次短请求均被预算阻断，证明本地拒绝也占一次 Runtime 额度。debug=false 的两个短请求都返回 finish_reason=length 和成功 ModelResponse，证明适配层不将截断独立拒绝；不据此推断所有上层组件都忽略 length。

完整真实链路在开启复用/checkpoint/投影/enforce 后仍调用 46 次并全点无法裁定；没有与禁用版进行同输入随机性控制，不能将结果解释成这些机制毫无作用，也不能宣称压缩收益已验证。
