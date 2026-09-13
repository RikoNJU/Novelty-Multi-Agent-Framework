# Reviewer #11 / #12 阶段性工作报告

日期：2026-09-13。开发分支： `sdq`。

## 结论

#11 的配置接线和回归验证已完成。#12 已完成固定真实来源样例、候选判定标准、可运行的评测工具与离线验证；**尚未完成验收**：缺少可用模型凭据，真实误判数据未产生；样例标签由开发代理逐例检查，仍待人工复核。没有把离线测试或预设标签报告为真实模型准确率。

## 基线选择

通过 GitHub API 读取最新分支 SHA，并执行 `git fetch origin lya database`：

| 分支 | 核实的最新 SHA | 判定 |
|---|---|---|
| lya | `00ea628130fe00a30764fba73d16eb910281cc1f` | `frontend` 只有 README；正文明确“当前尚未实现前端” |
| database | `bfae677d9e49bea6bf2b3cbb6fcb09f1874c6854` | 按用户备选条件选作开发基线 |

因此创建本地 `sdq`，从 `bfae677` 开始开发。远端 `sdq` 未改动。前端不是 #11/#12 后端开发的必要依赖；此处按用户给定的前端条件选择基线，并未扩展为前端建设任务。

## #11：配置注入

验收来源：[GitHub issue #11](https://github.com/RikoNJU/Novelty-Multi-Agent-Framework/issues/11)。

原有代码已经通过统一 ModelCallOptions 注入 temperature、max_tokens、timeout_seconds；剩余缺口是 typed config 的 prompt 未被消费。

- `EvidenceReviewerConfig` 新增 `prompt_name`，默认值兼容现有调用，并拒绝空白名称。
- typed 与 compatibility 两条 Composition Root 都传入配置的 prompt。
- Reviewer 渲染时读取 `self.config.prompt_name`。
- 新测试从配置一路验证到实际 prompt 渲染入口和 `complete(options=...)` 参数，覆盖非默认 temperature/max_tokens/timeout_seconds。
- 两条工厂路径均验证 enabled=false 返回 None、enabled=true 构造 Reviewer；既有 Workflow 测试验证关闭后的证据透传。
- 生产 Reviewer prompt、判定/解析逻辑及 EvidenceCard schema 未改变。

| #11 验收项 | 状态 |
|---|---|
| prompt 来自 typed config | PASS |
| ModelCallOptions 来自 typed config | PASS |
| enabled=false 透传 | PASS |
| enabled=true 构造 | PASS |
| temperature/max_tokens/timeout_seconds 单测 | PASS |
| 不修改 Reviewer 判断语义 | PASS |

## #12：固定样例与评测

验收来源：[GitHub issue #12](https://github.com/RikoNJU/Novelty-Multi-Agent-Framework/issues/12)。

固定文件：`tests/fixtures/reviewer/benchmark.json`。包含 12 例，由仓库已存档的两篇真实论文文本构造受控卡片：

- *Retrofitting Temporal Graph Neural Networks with Transformer*，arXiv 2409.05477。
- *Efficient Neural Common Neighbor for Temporal Graph Link Prediction*，arXiv 2406.07926。

来源标题、URL 对照仓库存档 `backups/MF2033k6lC/v2/references/list.json`；quote 在对应存档文本中逐字匹配，记录字符位置与文本 SHA-256。卡片为评测用途人工可读的受控改写，不宣称全部来自此前 Researcher 的自然输出。无需重新检索，避免召回变化干扰 Reviewer 评测。

| 分类 | 编号 | 数量 | 拟议标签依据 |
|---|---|---:|---|
| 有效证据、限定范围摘要 | A1–A3 | 3 | 贡献和范围均获 quote 支持 |
| 原文反证、无关、内部冲突 | R1–R4 | 4 | 有明确冲突或语义目标不符 |
| 可补证、无依据差异、摘要夸大 | N1–N3 | 3 | 缺少支撑，尚不能以缺失认定事实为假 |
| provenance/location 不足 | V1–V2 | 2 | 确定性规则拦截，不调用 Reviewer |

标签状态为 `agent_reviewed_pending_human`，逐例 rationale 固定在 fixture。特别是 N1/N3 中“夸大结论应补证还是直接拒绝”的边界需要人工认可；当前候选标准区分明确反证与仅缺少支持。

候选 prompt：`reviewer/review_evidence_candidate`，明确 accept/reject/needs_more 的顺序、摘要的可接受范围、元数据无法核验与已证伪的区别，以及 reviewed_confidence 的含义。候选文件不作为默认生产 prompt；真实基线/候选对照之前，不宣称优化已有效。

评测入口：`novelty_agent_framework.experiments.reviewer_benchmark`。

- 默认仅执行 fixture 和 Validator 检查，不调用模型。
- `--live` 使用正式 Reviewer、typed config 与既有模型客户端。
- `--repeats` 对固定样例重复运行，记录逐例重复判决一致性。
- `--prompt-name` 可切换候选 prompt；其他模型参数保持一致。
- 保存逐例输入、判决、issue、confidence、原始模型消息和响应、usage、耗时及配置/fixture/prompt 指纹。
- 统计三分类混淆矩阵、与拟议标签一致率、误拒绝、漏拒绝、错误接受、confidence 范围偏离。
- 误拒绝率分母为成功得到语义判决的预期 accept 卡；漏拒绝率分母为成功得到语义判决的预期 reject 卡，实际 accept 或 needs_more 都计入漏拒绝；另单列错误 accept。
- 超时、解析错误、缺失判决独立计入 runtime_errors；不会伪装成语义 reject。未完成全部语义判决的 live 运行返回非零退出码。
- 模型密钥不写入实验产物；输出目录必须是新目录，防止覆盖以前实验。

## 当前实验数据与限制

离线产物见 `fixtures-v1/summary.json`、`fixtures-v1/cases.json` 与 `fixtures-v1/report.md`：

| 指标 | 实测结果 |
|---|---:|
| 固定案例 | 12 |
| Validator 接受 | 10 |
| Validator 拒绝 | 2 |
| 已成功调用真实模型 | 0 |
| 三分类准确率/误拒绝率/漏拒绝率 | 未测，不是 0% |

真实运行尝试记录为 `live-attempt/blocked.json`：配置模型 `deepseek-flash`，凭据 `SILICONFLOW_API_KEY` 缺失；当前没有 `backend/.env`，也没有可用 NOVELTY_API_KEY/LLM_API_KEY 回退。未发送模型请求。

两篇论文、少量受控改写仅适合初步回归，不代表真实流量、多领域质量。没有人工 gold 标签，因此后续首次 live 数值也只能称为“与拟议标签的一致性”，待人工复核后才能称人工标注基准结果。confidence 范围是待复核的支持程度约束，不是概率校准证明。

## Validator 与 Reviewer 职责

V1/V2 无需语义模型即可识别，由 DefaultEvidenceValidator 拦截。R1–R4 都保留合法来源、位置、ID 和高输入评分，能够通过 Validator；后续应由 Reviewer 检出语义冲突或无关性。N1–N3 则考察能否区别缺证与反证。评分职责有局部交集：Validator 执行最低输入评分阈值，Reviewer 判断评分是否符合实际支撑程度。

本轮不改变 EvidenceCard 主数据契约，也不为 Reviewer 新增全文检索能力。现有 quote 只能验证给定证据与卡片解释的关系；更广原文核验仍受输入范围限制。

## 验证

已运行相关配置、Reviewer、Workflow、Builder、完整性门控、PromptLibrary 与新增 benchmark 测试：**103 passed**；仅有已有 PyMuPDF/SWIG 弃用提示。`git diff --check` 通过。

```sh
./.venv/bin/pytest tests/test_reviewer_config_injection.py tests/test_reviewer_benchmark.py tests/test_evidence_reviewer.py tests/test_workflow_reviewer.py tests/test_factory.py tests/test_config_loader.py tests/test_runtime_config_injection.py tests/test_workflow.py tests/test_integrity_gates.py tests/test_evidence_card_builder.py tests/test_prompt_library.py
```

| #12 验收项 | 状态 |
|---|---|
| 固定 Reviewer benchmark | 已实现；人工标签复核待完成 |
| 三种 verdict 有可解释标准 | 已提供候选标准及逐例理由 |
| 误拒绝/漏拒绝有真实实验数据 | BLOCKED：模型凭据缺失 |
| 不大改数据契约 | PASS |
| 输出实验报告 | 本报告及离线产物已完成；真实对照结论待补 |

## 恢复步骤

在本机 `backend/.env` 配置 SILICONFLOW_API_KEY；无需在对话或报告中传递密钥。人工复核 fixture 的拟议标签并记录确认者、日期、修改理由，再执行基线/候选各两次：

```sh
PYTHONPATH=backend/src:. ./.venv/bin/python -m novelty_agent_framework.experiments.reviewer_benchmark --output docs/experiments/Reviewer_Issue11_12/baseline-live --live --repeats 2
PYTHONPATH=backend/src:. ./.venv/bin/python -m novelty_agent_framework.experiments.reviewer_benchmark --output docs/experiments/Reviewer_Issue11_12/candidate-live --live --repeats 2 --prompt-name reviewer/review_evidence_candidate
```

检查分歧、confidence 与重复运行结果，补齐人工标签后的真实指标，再决定是否启用候选 prompt。#12 尚不应关闭。
