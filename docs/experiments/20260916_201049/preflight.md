# 四工具完整工作流测试：运行前准备与历史耗时核对

## 状态

本次完整运行尚未启动，无新的模型、数据库或浏览器请求。
自动审批两次拒绝启动，第二次在提交既有授权说明后仍认为不足以证明用户允许
本次向 SiliconFlow 发送样例 PaperInput 及参考文献片段。需用户直接明确该项授权。
临时生产配置已从备份恢复，工作流代码和运行脚本均未修改，未新增运行脚本。

## 已准备的运行方式

使用仓库已有 `scripts/run_full_workflow_live.py`，从 PaperInput 后开始：

```bash
PYTHONPATH=backend/src NOVELTY_SPRINGER_ENABLED=true /home/lya3106643285/miniconda3/envs/Novelty/bin/python -u scripts/run_full_workflow_live.py \
  --paper-json <本实验目录>/input/MF2033k6lC/paper-input/others/paper.json \
  --runs-root <本实验目录>/runs --run-number 1 --max-rounds 2 --max-concurrency 4
```

样例保持 MF2033k6lC，复用已验证的 9 篇参考文献缓存，不运行 MinerU。
待运行配置见 researcher-config.json、project-config.json：arXiv、Springer Nature、
WebSearch、Playwright Browser 开启，null_catalog 关闭；仅英文，两轮，并发四。
现有脚本不提供 Web/Browser 开关，因此执行前需临时应用配置快照，载入后恢复。

## 历史耗时事实

以下直接读取已有 runtime stage meta 和 model_calls.json，不是本次新运行结果。

| 历史实验 | 总耗时 | 模型调用 | 两轮 Reviewer 墙钟耗时 | 提取查新点 | 报告综合 |
| --- | ---: | ---: | --- | ---: | ---: |
| 20260915_224229 | 1421.34 秒 | 149 | 167.71 + 715.22 秒 | 85.23 秒 | 23.47 秒 |
| 20260915_230514 | 1460.25 秒 | 106 | 0 + 265.42 秒 | 179.33 秒 | 176.35 秒 |
| 20260916_011551 | 314.06 秒 | 98 | 40.35 + 43.98 秒 | 19.79 秒 | 31.37 秒 |

1. 224229 中 Reviewer 共占约 883 秒（总时长约 62%），是明确主耗时阶段。
   当时存在逐点审查、较多 Reader 回读、工具预算耗尽；第二轮积累了更多卡。
   历史记录中部分 Reviewer 模型调用被归为 unattributed，不能将所有此类调用
   无条件算到 Reviewer。最长已记录模型调用为 177.81、158.94 秒。
2. 230514 虽模型调用数减少，总耗时仍约 24 分钟。模型单次请求明显更慢：
   最长一次 240.93 秒；报告综合 176.35 秒；补检计划模型 155.36 秒；
   一个 Researcher 请求 126.69 秒。不能仅以调用次数解释耗时。
   这些数值证明慢发生在模型请求期间，但日志不足以区分服务端排队、推理和网络等待。
3. 230514 还清空缓存并重新引导 91 条参考文献，随后生成六个研究任务；
   arXiv 重试/熔断、Springer 错误、WebSearch 429 和多次逐段读取增加了等待与往返。
4. 最近 011551 已恢复缓存并启用按卡并行/批量 Reader，只有四个研究任务；
   最长模型调用约 31 秒，整体降至 314 秒。缓存、任务数量、模型响应速度与实现
   同时变化，不能将全部差值归于并行优化。
5. 上述对比实验 Browser 均关闭，历史慢不由 Browser 调用造成。
   本次需另外检查 Browser 是否实际调用、导航耗时及超时，不能只因启用就认定有开销。

授权后应运行上述现有入口一次，再从原生 runtime 的阶段、LLM、工具记录中核对
成功状态、最终报告、真实工具调用次数、失败重试和等待时间；不另写运行器。
