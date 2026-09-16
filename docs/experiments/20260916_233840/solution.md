# MF2033k6lC 查新点覆盖与证据边界实验

## 结论

本次依照 `task/Novelty_查新点覆盖与证据充分性修复_Prompt优化任务书_2026-09-16.md`，复用现有 `scripts/run_full_workflow_live.py` 从固定 PaperInput 运行，不含 MinerU。最终提取策略在固定样本上 **5/5 次输出 GSAERU、DSGNN、Sketch-DBH 三个独立查新点**；合成反例没有把一个方法的三个性能指标拆为三个点，也没有把仅有两个方法的输入强凑成三点。三次最终版本完整运行（4、5、6）都保留三个查新点及其报告条目，Reviewer 对缺少决定性差异引文的点均保留 `insufficient_evidence`。

**总体质量尚未验收通过。** NP-2 在最终三次运行中均有实际数据库检索，却没有形成最终证据卡；NP-3 在运行 6 也没有卡片。现有检索式从过严直接退到过宽，候选相关性不稳定。运行 1 和 3 的旧 Reviewer 曾把“摘要未提及”写成“文献未采用”，运行 3 甚至给出 `novel`；新增的有限守卫在最终三次运行中阻止了这种无依据的强裁定，但它不能替代逐项的语义核验。三次最终运行的墙钟中位数为 **384.88 秒**，总 token 中位数为 **1,174,049**；这些不是与旧版固定候选配对的因果性能对照。

## 输入、版本与复现

- PaperInput：`input/paper.json`，SHA256 `89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66`。复用同一输入和参考文献缓存；`input/settings.effective.json`、`input/researcher.effective.json` 是脱敏的实际设置。三个贡献的原文依据与人工边界见 `quality_review.md`。
- 完整运行入口：`scripts/run_full_workflow_live.py --paper-json outputs/MF2033k6lC/paper-input/others/paper.json --runs-root <本目录>/runs/full --run-number N --max-rounds 2 --max-concurrency 4`，N=1…6。仅运行时临时启用 Springer Nature、WebSearch、Browser 和运行归档目录；配置文件在脚本退出时恢复。arXiv API 一直启用，英语检索，模型为 SiliconFlow 上的 `deepseek-ai/DeepSeek-V4-Flash`，`enable_thinking=false`。无新的完整工作流脚本。
- 运行 1 是初始冒烟；运行 2、3 用第一版证据守卫；**运行 4、5、6 才是相同最终代码和配置的可比重复**。`run.json` 的 `git_commit=68dcaad` 仅标识已提交基线；当时的增量代码尚未提交，完整差异见 `implementation.patch`。模型随机输出、在线数据库状态及参考文献缓存仍会使三次输出不同。
- 计时采用各 `run.json` 的外层单调时钟 `duration`，包含输入加载、完整工作流、落盘和渲染。Runtime Debug 的阶段累计耗时有并发重叠，不可直接相加当作总墙钟。模型费用使用归档计价口径，cached/reasoning token 是总 token 的子类，不重复相加。更完整的参数与提示词哈希见 `baseline_manifest.json`。

## 分层实验结果

| 层级 | 结果 | 证据位置 |
|---|---|---|
| 提取基线 5 次 | 0/5 恰为三点；均把 GSAERU 的图摘要步骤额外拆出 | `runs/extractor/` |
| 仅第一轮提示词收紧 5 次 | 4/5 恰为三点 | `runs/extractor_v4/` |
| 第二个示例提示词 5 次 | 2/5 恰为三点，已回退 | `runs/extractor_v5/` |
| 最终提示词 + 有界作者贡献段去重 5 次 | **5/5 恰为三点**，没有强制数量规则 | `runs/extractor_v6/` |
| 合成提取 E04/E05 | 同一方法的三项性能为 1 点；两个独立方法为 2 点 | `runs/synthetic_extractor/` |
| 固定合成 Reviewer V01/V02/V03 | 摘要缺口为不足；明确否定引文保留有限裁定；两篇局部公开没有拼成单篇完整公开 | `runs/synthetic_reviewer/` |
| 真实全文链路 | 运行 3 中模型主动请求 4 篇 arXiv 全文并由 Reader 读取；独立合法记录按需获取与 Reader 片段读取成功 | `runs/full/0003/`、`runs/manual_fulltext/` |
| 确定性回归 | 提取、Reviewer、工作流、Renderer 等目标测试 **103 通过** | 本文“测试”节 |

原生完整工作流的核心结果如下。括号内卡片顺序为 NP-1/NP-2/NP-3；`—` 表示无肯定裁定，不是零命中。

| 运行 | 版本 | 秒 | 轮次 | 卡片 | Reviewer | 总 token | 估算 RMB | arXiv 429 |
|---:|---|---:|---:|---|---|---:|---:|---:|
| 1 | 初始 | 240.02 | 1 | 1/2/1 | 三点 `partially_novel`，含无依据否定 | 604,907 | 1.845 | 0 |
| 2 | 第一版守卫 | 560.30 | 2 | 2/1/1 | 三点不足；相关文献原因仍含不安全措辞 | 1,040,205 | 3.093 | 0 |
| 3 | 第一版守卫 | 469.46 | 2 | 0/0/1 | NP-3 错误 `novel`，其余不足 | 1,102,717 | 3.186 | 0 |
| **4** | **最终** | **466.53** | **2** | **2/0/2** | **三点不足** | **1,174,049** | **3.261** | **0** |
| **5** | **最终** | **335.61** | **2** | **1/0/1** | **三点不足** | **1,054,949** | **2.942** | **1，重试成功** |
| **6** | **最终** | **384.88** | **2** | **1/0/0** | **三点不足** | **1,390,318** | **4.037** | **0** |

逐次原始数据、实际检索式、工具调用和最终报告在 `runs/full/000N/`；结构化对比见 `comparison.json`。运行 4–6 中位数为 384.88 秒、1,174,049 token、RMB 3.261，范围分别为 335.61–466.53 秒、1,054,949–1,390,318 token。运行 1 的 240 秒不是同等质量基线：仅一轮且 Reviewer 给出无依据裁定，不能据此说新策略“纯粹变慢”。

## 关键发现及处置

1. **提取误拆和漏点：**原模型把 GSAERU 的普通图摘要步骤另立一点，甚至挤掉 Sketch-DBH 的独立机会。最终提示词把普通步骤归入框架；去重时传入有界作者贡献段，使其看到 Sketch-DBH 独立目标和机制。最终 5/5 仅说明此固定输入的初步稳定性，未做结构不同的真实论文保留样本。
2. **Reviewer 越界裁定：**运行 1/3 的摘要级引文不能证明论文没有使用 Count-Min Sketch 或最小堆。新增守卫对无直接否定引文的强缺失措辞降为证据不足，并保留相关文献 ID；运行 3 的原始输出回放在 `runs/replay_np3_guard.json`。V02 的明确“does not use”引文仍能支持有限 `partially_novel`，避免全部一律拒判。守卫是措辞层的保险：引文中的否定句可能针对别的特征，后续仍需特征级语义绑定核验。
3. **NP-2 仍无卡：**最终三次 NP-2 都执行了 arXiv 查询。严格式将 `distributed AND graph AND neural AND network AND training AND framework` 等所有标题词再与摘要特征相与，多为零命中；退到 `abs:"graph summarization"` 时每次虽有 8 个命中，多数是普通图摘要而非分布式 GNN 训练。`candidate-audit.json` 显示有的候选已读但没有合法卡。应在 SearchPlanner 与 arXiv 编译层增加保留“分布式 GNN 训练”核心短语的中间宽度式，图摘要作为可选扩展，记录每档命中与读取原因；对高相关候选按需全文后再判断。不能把 NP-2 目前的无卡写成数据库零命中。
4. **报告局限文字失真：**运行 5 的最终报告第九节声称“检索覆盖事实未明确提供”，并把达到一张卡片门槛的点笼统称为“数量未达门槛”。成因是综合模型收到卡片与 Reviewer，却未收到实际 `SearchExecution`；后续应只从 `task_research_results.search_executions` 生成检索覆盖事实，并在报告绑定层对卡片数量、Reviewer 状态作确定性校验。本轮保留原报告供审计，没有修改历史产物。Renderer 的检索策略节与 `retrieval-plans.json` 则保留了实际查询。
5. **外部工具：**运行 5 的 arXiv 元数据批请求在满足 4 秒间隔时仍收到一次 `429 Rate exceeded.`，遵循 `Retry-After: 2` 后重试成功；批处理减少物理请求但不保证服务端不限制。运行 6 的 Browser 三次调用有两次成功保存 Artifact，一次因页面持续导航失败。WebSearch 在完整运行中被调用，但网页内容未进入论文 Evidence 或相关文献列表。Springer 失败、零命中、Harness 预执行拦截应分开计数，不把失败合并为零命中。

## 测试与未完成项

测试命令：

```bash
PYTHONPATH=backend/src /home/lya3106643285/miniconda3/envs/Novelty/bin/python -m pytest -q tests/test_point_extractor.py tests/test_novelty_point_reviewer.py tests/test_workflow.py tests/test_workflow_reviewer.py tests/test_coordinator_json_robustness.py tests/test_task_researcher_workflow.py tests/test_run_full_workflow_live.py tests/test_renderer.py
```

结果为 103 通过。真实模型结果、合成反例、确定性测试分层列示；没有用合成结果冒充真实论文质量。**尚未完成**：结构不同的真实论文保留样本；任务书要求的 D0/D1 固定候选、三组配对下游对照；NP-2 有效文献证据覆盖；最终卡片对已读全文的可靠引用；报告综合的检索事实注入。Reviewer 语义补检建议仍不会自动控制下一轮路由。因缺少固定候选配对实验，不能把本次成本变化归因于单个提示词或模块；性能可接受性须与质量修复分别判断。
