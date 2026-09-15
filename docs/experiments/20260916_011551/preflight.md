# 启用参考文献缓存的完整工作流：启动被阻止

## 已完成的准备

- 样例：examples/MF2033k6lC.pdf，使用 outputs 中已有 PaperInput，不运行 MinerU。
- 保留当前英文检索、arXiv / Springer Nature、WebSearch 补充资料配置。
- 使用 docs/experiments/20260915_224229/input/MF2033k6lC/subject_references 缓存。
- 本地验证通过：参考文献引导清单与当前 PaperInput 的 91 条参考文献匹配；
  9 个已缓存 Artifact 的文件均存在，SHA-256 与清单一致。
- run.py 已准备完整运行、缓存复制、HTTP 状态、工具轨迹、模型调用和两阶段 Reviewer 耗时记录。

## 阻塞

完整工作流尚未启动，没有新的外部请求、报告或性能结果。
自动审批拒绝了启动命令：该流程将样例 PaperInput 及所读参考文献片段发送至
SiliconFlow，并调用 arXiv、Springer 和配置的 WebSearch 服务；审批认为用户
尚未明确授权这些数据向具体外部服务发送。需要明确授权后重试，不能绕过拒绝。

准备结束时间：2026-09-16T01:08:16+08:00。
