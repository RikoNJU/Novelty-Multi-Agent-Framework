# PaperInput 全流程复测（2026-09-16）

执行完成，但证据覆盖未达标：流程 SUCCESS、引用与报告完整性检查通过，最终 3 张卡全部属于 NP-3；NP-1、NP-2 在补检后仍为 insufficient_evidence。不能将流程成功解释为三个查新点均已充分查新。

## 输入与执行条件

- 代码：`fix/arxiv-rate-limit-final`，运行时 HEAD `35af364b8169704b4351fa710b79f7218aef6306`。本次未修改生产代码。
- PaperInput：`outputs/MF2033k6lC/paper-input/others/paper.json`，SHA256 `89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66`，与上次相同。
- 复用已有 subject-reference 缓存；研究输出使用独立目录，不复用上次研究证据卡；未调用 MinerU。
- 唯一外部论文检索来源：arXiv Web；间隔 8 秒，最大并发配置 4，流程最多 2 轮。保留本地 reference_search 和 Reader。
- 模型：`deepseek-ai/DeepSeek-V4-Flash`，`https://api.siliconflow.cn/v1`。用户在明确列出数据和目的地的授权问题后回复“允许”，本次执行经审批通过。
- 实际时间：北京时间 19:16:09 至 19:34:12，1082.90 秒（18 分 3 秒）。目录名时间为准备时间，不是实际启动时间。

## 结果对比

| 指标 | 上次完整流程 | 本次复测 |
| --- | --- | --- |
| 耗时 | 986.37 秒 | 1082.90 秒 |
| 流程轮数 | 2 | 2 |
| 最终卡数 | 3 | 3 |
| 新 Web 候选卡数 | 2 | 3 |
| 有有效卡的查新点数 | 3/3 | 1/3 |
| 最终证据不足 | 无 | NP-1、NP-2 |
| Web 物理请求 | 39（37×200、2×406） | 36（35×200、1×404） |
| 重试 / 间隔违规 | 0 / 0 | 0 / 0 |

本次最小观测请求间隔 8000.094 毫秒，无 429。该结果支持本次共享节流有效，不能推断所有负载下都不会限流。首轮三个 Research Tasks 启动相差约 14 毫秒。

本次 NP-3 为“图摘要的 GNN 优化机制”这一较宽的综合点；上次 NP-3 为更具体的边分割划分点。点提取、候选和模型输出发生变化，因此这是一组同代码同输入的端到端重复观测，不是固定查新点的受控效果比较。

## 证据与最终判断

| 查新点 | 首轮 | 补检 | 最终判断 |
| --- | --- | --- | --- |
| NP-1 GSAERU | partial，0 卡；Reader 预算耗尽，两次不匹配原文的引文被丢弃 | completed，0 卡 | insufficient_evidence |
| NP-2 DSGNN | partial，0 卡；reference_search 预算耗尽 | completed，0 卡 | insufficient_evidence |
| NP-3 图摘要优化机制 | completed，3 卡 | 未安排补检 | partially_novel，模型置信度 0.72 |

三张最终卡为 Graph Coarsening via Convolution Matching for Scalable Graph Neural Network Training、A Comprehensive Survey on Graph Summarization with Graph Neural Networks、Inference-friendly Graph Compression for Graph Neural Networks。它们均由 `arxiv-web-search` 新候选进入 Reader，再生成证据卡；共 5 条引文按生产 Builder 的引用匹配规则验证通过。报告的 3 个结论与 Reviewer 结果一致，引用完整性检查通过。

这里的部分新颖是本次模型在有限候选和证据上的判断，并不代表全面检索后的独立学术结论。

## 效果问题与后续优先级

1. **补检候选偏泛、重复。** NP-1、NP-2 的补检日志均主要讨论 CGS、COREKG、Causal DAG Summarization、Code-Craft 等泛图摘要候选，缺少围绕时序表示学习或分布式 GNN 的有效补充。应检查规划查询及补检策略能否保留关键领域约束并改变已有候选集。
2. **取证可能过度要求全特征匹配。** 两项补检的 no-evidence 理由均强调没有一篇文献同时覆盖整套技术特征；NP-2 还提到 AGL、AliGraph 等局部相关工作。日志支持优先检查是否将“可用于局部比较的证据”和“完整组合已公开”混为一谈，尚不能仅凭本次运行断言具体代码根因。
3. **预算分配与精确摘录。** NP-1 首轮耗尽 Reader 预算，且两条引文未通过原文匹配；NP-2 耗尽 reference_search 预算。校验器正确阻止了这些不匹配引文进入最终报告，但产卡效率仍需改善。
4. **查新点提取稳定性。** 本次 NP-3 与前两个点存在概括层面的重叠，和上次提取结果也不同。后续应固定点集做检索与取证评估，并单独评估点提取重复性。

未在这次复测中修改提示词、预算、查询策略或生产实现，以免改变待检验条件。121 次模型调用均成功；Runtime 按本地价格配置估算费用约 5.62 元，实际账单以服务商为准。

## 产物与复核

- [查新报告](MF2033k6lC-report.md)：流程直接生成，未人工修饰结论。
- [指标](metrics.json)、[Runtime 摘要](summary.json)、[任务告警](task-warnings.json)。
- [新 Web 卡引用追溯](web-card-provenance.json)、[结果状态](result.json)、[运行清单](run.json)。
- [原始文件哈希清单](raw-manifest.json)：原始数据保存在仓库忽略目录 `outputs/ARXIV_PAPERINPUT_RECHECK_20260916T111244Z/`。
- 复核命令：使用 Novelty 环境 Python 执行本目录 `inspect_run.py`、`archive_run.py`，不触发模型或网络调用。`run.py` 仅用于新运行且要求输出目录不存在；不要对现有目录重复启动。
- 上次对照：[arXiv 最终验收实验](../ARXIV_LIMIT_FINAL_2026-09-16/README.md)。

本次授权仅涵盖指定模型端点的数据传输与完整流程运行；未将该授权扩展为实验材料的远端发布许可。
