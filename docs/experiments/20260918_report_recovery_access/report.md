# 真实恢复归档与生产只读展示验收

## 结果

L1、L2 的来源阶段输入、原失败 Runtime manifest、真实模型响应、captured 重组 JSON 与 Markdown 均按原索引 SHA-256 重新核对通过。独立目录中的受控包再次通过生产报告组装与完整性检查。两份报告已登记为独立只读资源，原业务 run 仍为 `FAILED`；补交的 `run-29fdb…` 是测试流程快照，没有进入真实恢复列表或资源登记。

| 来源 | 只读资源 ID | 原状态 | 验收结果 |
|---|---|---|---|
| L1 | `rr-fa3a297728c2e5b8fdc2454fab080bba` | `FAILED` | 真实后端预览、下载、重启后再读通过；NP-1 技术性未完成保留 |
| L2 | `rr-c451bd658f938152bf5c50031be505a3` | `FAILED` | 真实后端预览、下载、重启后再读通过 |

## 实际核对的材料

每份来源直接读取四个原文件：冻结的 `synthesize_report/input.json`、真实恢复 `llm_calls/0001_deepseek-flash.json`、最终 `report.json`、最终 Markdown，并读取原业务 Runtime manifest 核对 `FAILED` 身份。每个文件的路径、字节数、实际及预期 SHA-256 见 `archive/real-source-index.json`。受控包中的 `audit.json`、真实响应和原文件字节保持在 `outputs/report-publication-20260918/bundles-complete/`，未提交到 Git。迁移到独立临时目录后仍通过 `verify_bundle()`；发布根只复制白名单文件和索引。

报告入口使用生产 `validate_report_integrity()` 检查点、原 Reviewer 八类权威字段与卡片引用，并用保存的真实 Draft 重新确定性组装进行等值比较。L1、L2 各 3 点，原未完成原因与原裁定未改。此前的 `all_fields_match=true` 仅用作对照。零调用测试快照的外层 `SUCCESS` 与其报告完整性失败并存，现标为测试反例，不用于发布。

## 真实接口与浏览器

后端在 `127.0.0.1:8010` 提供 `/api/novelty/report-artifacts/{id}` 及 `/content`、`/download`、`/provenance` 四个 GET；运行中 OpenAPI 已核对。React 使用 `/?report_resource_id=<id>`，通过 Vite 代理访问正常后端，页面没有 `route.fulfill()`、固定报告正文或新业务任务。L1、L2 在 Chromium 中各完成预览、刷新、重新打开和下载，直接下载与页面下载均等于登记 Markdown 哈希。后端进程重启后，两份资源 ID 不变，两项浏览器测试再次通过。测试记录见 `display/`。

原 Markdown 未添加或改写正文；下载文件名明确为 `recovery-report-<id>.md`，另可下载 `provenance.json`。页面直接显示历史恢复范围、原完整流程失败、来源与组装身份，以及所有点的原 Reviewer 状态。该展示没有把资源可用解释为原查新成功。

## 零新增业务调用与费用

本轮模型、检索、文献获取、收费解析和工作流启动调用均为 0。登记和 GET 实现只读本地文件；测试中业务服务初始化失败时资源依然可读。浏览器网络记录与后端访问日志只有资源 GET，没有业务 POST 或新 run。前序真实恢复的 3 次请求及未知账单仍见前序账本，本轮没有重置或改写它。

## 限制

这是两份历史恢复报告的归档与只读访问验收，不是新 PDF 端到端查新。报告的自由综述与原 Reviewer 语义没有独立准确率评估；检索稳定性、Springer 404、阶段详情接口和一般 Workflow 的非阻断门禁仍为独立问题。资源 ID 本身不构成认证，当前只在本机受控服务范围验证。详细见 `known-issues.md`。
