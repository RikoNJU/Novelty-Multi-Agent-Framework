# MF2033k6lC V3 全链路集成实验报告

## 1. 实验目标与结论

目标是从 `examples/MF2033k6lC.pdf` 开始，连续验证 MinerU → PaperDocument/PaperInput → 正式 NoveltyWorkflow → Native Researcher → EvidenceCardBuilder → fan-in/report。

最终状态：**FAIL（前置环境阻塞）**。V2 备份完整成功，但强制要求的 MinerU 独立环境不存在。依据任务书，本次没有执行 text-layer/OCR fallback，也没有继续调用 PointExtractor、Coordinator 或 Researcher，因此不能宣称 V3 full workflow 已验证。

当前代码基线：`4d70b6e`。

## 2. V2 备份

- 路径：`backups/MF2033k6lC/v2`
- 源/备份文件数：61 / 61
- 源/备份总字节：1,497,839 / 1,497,839
- 逐文件 SHA-256 tree：一致
- 可解析 JSON：15 个；关键 paper/content-list/points/evidence/report/retrieval audit 均存在
- `backup_ok=true` 后才删除旧 `outputs/MF2033k6lC`
- 删除后备份仍为 61 文件、1,497,839 字节

## 3. V3 Processing / MinerU

- 原 PDF：`examples/MF2033k6lC.pdf`，2,046,268 字节，可读
- 配置：parser=`mineru`，env=`mineru`，backend=`pipeline`，method=`auto`
- Worker：`scripts/mineru_worker.py`，存在
- MinerU conda 环境：缺失（`conda env list` 无 `mineru`）
- MinerU / magic-pdf executable：缺失
- actual_parser：未产生
- fallback：未执行
- pages/chars/references/images/tables/equations/warnings：未产生，不以 0 冒充解析结果
- processing elapsed：0 ms（仅前置检查，不含解析）

因此 PaperDocument.source 无法验证为 `mineru`，PaperDocument → PaperInput 结构保持也尚未执行。

## 4. Planning、Researcher、Builder 与 Workflow

强制 MinerU 层失败后按任务书停止：

- 真实 PointExtractor / Coordinator：未调用
- NoveltyPoint / ResearchTask：未产生
- TaskResearcher / Harness / WebSearch / Browser / Reader：未调用
- multi-tool-call rejection：0（没有模型调用，不代表稳定性验证通过）
- Builder：未调用；Evidence/Card：0/0
- fan-out/fan-in、persistence、report rendering：未执行
- validator_mode：`not_started`；production validator migrated=false
- reviewer_enabled=false；reviewer_migrated=false
- Token：0；Task/Workflow 耗时：不适用

## 5. 分层判定

- Layer 1 — Backup：**PASS**
- Layer 2 — MinerU：**FAIL**
- Layer 3 — PaperInput Contract：**FAIL / NOT RUN**
- Layer 4 — Planning：**FAIL / NOT RUN**
- Layer 5 — Researcher：**FAIL / NOT RUN**
- Layer 6 — Builder：**FAIL / NOT RUN**
- Layer 7 — Workflow fan-in / report：**FAIL / NOT RUN**
- Overall：**FAIL**

## 6. 数据缺口与已知限制

- 缺少 MinerU 版本、实际 backend/method、页面及结构化块统计，因为 worker 无可用运行环境。
- 没有 V3 trace、token、外部页面失败或 Task isolation 数据，因为正确地在前置检查阶段停止。
- V2 目录在本次 V3 开始前后计数和字节一致；尚未保存独立的带时间戳签名清单。
- `outputs/MF2033k6lC` 当前不存在，这是经校验备份后的预期状态，不是数据丢失；可从 V2 备份恢复。

## 7. 恢复条件与下一步

需要先提供符合项目配置的 MinerU 3.4.5 独立环境（默认 conda env 名 `mineru`，或在 processing 配置中给出有效 `mineru_python`）。环境可用后，应从同一原 PDF 重跑本任务，不使用 V2 中间产物。

是否可以进入 Validator contract adaptation：**NO**。必须先取得 MinerU=PASS，且 Researcher 至少 PASS 或可解释 PARTIAL、Workflow=PASS。
