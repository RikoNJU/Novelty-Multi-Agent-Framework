# Coordinator 报告节点修补实验报告

## 结论

实现与离线节点验证通过；真实模型报告节点 L1／L2 未运行，故局部真实恢复和生产页面展示仍待验收。原两份端到端运行保持 `FAILED`。本轮没有重新解析 PDF、检索或调用 Reviewer，也没有新业务模型费用。

## 原因与输出边界

两份历史运行的四个 Coordinator 原始响应均在 JSON 字符串内结束，`json.loads` 无法解析；旧请求输出上限为 4096。原 Runtime 没有保存 `finish_reason`，所以“提供商明确按长度结束”无法从旧记录确认。响应尾部、错误位置、usage 和哈希见 `analysis/original-response-index.json`；截断判断与字段重复负担之间的因果解释仍为设计推断。

修补后实际生产请求使用 `ReportNarrativeDraft` schema，只要求每点短综述、卡片 ID 分组和有限局限。正常、fallback 与纠错路径均不要求模型再输出 Reviewer 裁定或原文对象。实际请求捕获见 `analysis/output-shape-comparison.json`：L1 请求 226,492 字节，L2 为 190,368 字节；输出上限仍为 4096，输入语义没有为本轮压缩。Draft 限制新写文本，不截短源证据。

## 确定性组装与离线回放

组装器先校验全点、卡片身份和作用域，再把原 Reviewer 八类权威字段注入最终对象。1／3／8 点、重排、长摘录、不同状态及非法引用的测试通过。L1、L2 冻结的实际阶段输入分别在独立恢复目录通过 `synthesize_report → validate_report_integrity → persist_report → render_report`，每份使用一次**离线脚本模型**响应；全部三点保留。字段逐项比较见 `analysis/authority-binding-checks.json`，原文只保留于本机受控输出。该结果证明机械路径可运行，不证明真实模型表达正确。

最新离线结果保存在 `outputs/report-node-recovery-20260918/L1-offline-final/` 与 `L2-offline-final/`；索引见 `tests/offline-node-results.log`。后续再以新目录做过来源完整性门禁复核，两份均通过。脚本没有上游执行入口。恢复对象独立记录 `source_run_id`、`recovery_id`、实际重算节点和原 run 失败状态。

## 真实调用与费用

本轮真实调用 **0 次、已知新增模型费用 0 元**。任务书的 1 元只是建议，且明确不是授权。以当前本地标准费率保守预留，L1 首次请求约 0.71634 元，L2 约 0.607968 元；两次首次请求合计约 1.324308 元，超过 1 元。四次调用按首次请求大小估算约 2.648616 元，纠错上下文会增加输入。建议本轮单一总上限 4 元、最多 4 次物理请求、每来源 240 秒，先 L1 成功再 L2；实际调用仍需用户批准向 SiliconFlow 发送被冻结的 PDF 派生报告节点输入。脚本不会重跑上游；预算用同一账本，不因来源切换重置。

## 页面

Playwright Chromium 测试使用离线 Renderer Markdown 的 API 拦截读取。页面显示“基于历史失败 run 的报告节点离线替身恢复；非完整查新成功”，包含原未完成点；下载字节与源文件一致，刷新和下载没有业务 POST。截图和记录见 `display/`。这只验证展示机制，尚不是实际模型报告的生产读取验收。

## 限制

L1 的 NP-1 仍是 Reviewer 技术错误；其他点的语义风险没有重新评审。Springer 404、阶段详情接口与端到端稳定性不在本次修补的证明范围。真实节点未调用，不能声称报告节点实际恢复成功。两份历史来源都是已见过的回归材料，不能推论跨论文可靠性。详见 `analysis/known-issues.md`。
