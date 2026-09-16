# 提示词及调用点变更

本轮最终版本相对 `68dcaad` 增量如下；前序实施补丁由 `11d2f89`、`1a38342`、`68dcaad` 承载，详见这些提交与 `docs/experiments/20260916_222626/solution.md`。

| 文件 / 实际调用点 | 变更 | 验证 |
|---|---|---|
| `prompts/extractor/extract_points.md`，`NoveltyPointExtractor._generate_candidates` | v3→v4：只把原文明确给出独立算法、目标与机制的子模块拆为独立点；普通框架步骤归入框架。没有加入本样本答案。 | 固定 PaperDigest 五次最终提取、E04/E05 合成反例、提取器单元测试。 |
| `prompts/reviewer/review_points.md`，`NoveltyPointExtractor._review_candidates` | v3→v5：去重见到有界作者贡献段，按技术目标和机制等价判断；普通实现步骤不另立点。 | 最终 5/5 三点；单元测试确认供给范围有界。 |
| `NoveltyEvidenceReviewer._review_point` / `summarize_reviews` | 模型输出完成来源校验后，局部守卫拒绝没有直接否定引文支撑的强“未采用/未披露”裁定，并中和相关文献原因中的不安全措辞。 | 单元测试、运行 3 的真实输出回放、运行 4 起原生完整工作流。 |

中间尝试 `extractor_v4`（仅第一版提示词）为 4/5 三点；`extractor_v5`（再加示例）退化为 2/5，已回退。`extractor_v6` 是最终版本 5/5。版本号是提示词内容版本，不是运行目录编号。中间尝试均保留原始输出，避免只展示成功结果。
