# 实验进行中

用户已明确授权数据出站；第一组及 batch 补充探测已完成，第二组正在运行。以下为初始准备记录，最终会以三组真实结果整体替换。

# PaperInput 三组 provider 实验记录（待联网授权）

记录结束时间：2026-09-15T17:28:46+08:00（Asia/Shanghai）。

## 结论

**三次真实实验尚未完成。** 沙箱阻止网络访问，随后自动审批拒绝提升网络权限。当前不能判断真实 429、Springer 检索扩张或 web_search 在线可用性；不能将下表视为三次成功实验。

| 实验 | 配置 | 状态 | 实际结论 |
|---|---|---|---|
| 1 | 仅 arXiv；关闭 web_search | 等待出站授权 | 尚无真实 HTTP 响应；无法判定 batch 在线效果 |
| 2 | arXiv + Springer Nature；关闭 web_search | 等待出站授权 | 尚未启动；无法判定结果扩张 |
| 3 | arXiv + Springer Nature + web_search | 等待出站授权 | 尚未启动；无法判定工具在线可用性 |

## 输入与控制条件

- 样例：`input/MF2033k6lC.pdf`，原文件 `examples/MF2033k6lC.pdf`，90 页。
- PDF SHA-256：`1fa48a8cb5d121220ba897a051b1468c2f0cefa211a0f5311c1d74c47aed8c79`。
- 标题：面向大规模动态图的图神经网络优化机制研究。
- 复用现有 `outputs/MF2033k6lC/paper-input/others/paper.json`，来源为 text_layer，91 条参考文献。标题与 PDF 首页一致；本任务从 PaperInput 后执行，不重新运行 MinerU。
- 输入和参考文献缓存已复制到本目录的 `input/`，不写入原始 outputs 工作区。
- 使用生产 `build_standard_full_workflow`，保持默认 max_rounds=2、max_concurrency=4、Reviewer 与验证器；不做单任务抽样。
- 三组仅改变 provider 开关与 web_search 开关，browser 保持关闭；禁用 null_catalog 及其他数据库。
- arXiv：scheduler/batch 开启，物理 API 间隔 4 秒，batch window=200 ms，batch max size=32。
- 配置见 `planned_configs/`；实际运行时另存 `effective_config.json`。代码版本见 `source_revision.txt`。

## 已完成的验证

运行现有离线测试：

```sh
/home/lya3106643285/miniconda3/envs/Novelty/bin/python -m pytest tests/test_arxiv_scheduler.py tests/test_springer_provider.py tests/test_web_search_core.py -q
```

结果：27 项通过，日志见 `offline_tests.log`。这些使用模拟请求的测试能验证批处理合并、共享调度及错误处理逻辑，不证明真实服务不会返回 429。

## 发现的问题与解决方案

### 1. 网络权限阻断（环境阻塞，未证实为代码 bug）

首次启动停留在参考文献 bootstrap，arXiv 请求记录为 `[Errno 1] Operation not permitted`，HTTP status 为 null。已主动中断，记录保留在 `sandbox_start_failure/`。未完成研究流程，未生成报告。

随后自动审批拒绝联网执行，理由为：

> 该命令会启动真实联网实验，可能将论文内容及衍生数据发送至未明确授权的模型/API目的地；用户授权了实验目标，但未明确授权此敏感数据向这些外部服务的具体出站。

解决方案：待用户明确授权将已解析论文及流程数据发送至已配置的 SiliconFlow 模型 API（`https://api.siliconflow.cn/v1`），并将检索词和文献标识发送至 arXiv、Springer Nature、百度千帆 web_search，再按正规审批路径启动。已发出该确认，未绕过拒绝。

### 2. 历史参考文献缓存需要刷新（兼容性观察）

原 bootstrap.json 仅有 schema_version、subject_paper_id、entries，缺少当前有效性检查需要的 references_digest 与 bootstrap_ready。因此现有 `prepare_paper_input_references` 正确进入重建流程，不能直接声称复用了有效缓存。

解决方案：授权后在实验目录内刷新缓存，再由后续两组复用校验通过的同一快照。应分别记录 bootstrap 与正式研究阶段的 arXiv 统计，避免把缓存冷热差异当作 provider 效果。此次沙箱启动对实验缓存的改动已用原始副本恢复。

### 3. 主工作流与报告生成 bug

尚未执行到研究及报告阶段，**没有足够证据确认这两个阶段存在 bug**。不修改生产代码，也不编造修复结论。

## 联网后执行及验收

`run_trial.py` 为本次实验脚本，工作目录为仓库根目录。分别顺序执行脚本参数 1、2、3，各组日志重定向到对应 console.log；所有结果自动写入脚本所在目录。凭据从已有环境加载，不落盘密钥。

记录包括 run.json、effective_config.json、result.json、模型调用统计、工具调用记录、arXiv scheduler 指标、脱敏 HTTP host/path/status，以及生产工作流报告与 runtime artifacts。

- 实验 1：记录 HTTP 429、重试、逻辑/物理请求数、metadata_batch_ratio、最大 batch size、间隔违规数；出现 batch size>1 才能证明观察到了真实合并，零 429 本身不足以证明补丁消除了限流。
- 实验 2：按 provider 记录候选及独立文献数、错误、全文可读数量、最终证据数；以 DOI/arXiv ID/规范化标题去重。若规划结果不同，另用同一检索计划进行 provider 对比，并明确区分补充探测与主流程统计。
- 实验 3：确认 web_search 实际注册并被调用，记录返回数量、HTTP 状态及来源落盘；若模型未调用工具，应额外做明确标注的真实工具探测，不能把启用开关当作可用证据。
- 每组独立检查 workflow 是否返回、报告是否生成、报告内容是否有可接受证据，以及失败是否被降级掩盖。
- 完成后更新本文件，并将整个目录按最终结束时间重新命名，精确到秒。
