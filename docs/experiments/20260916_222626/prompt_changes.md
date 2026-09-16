# 提示词与生效位置

| 模板 | 变更 | 生效位置 |
|---|---|---|
| extractor/extract_points | 独立机制、反凑点、JSON 对象 | NoveltyPointExtractorAgent._generate_candidates |
| reviewer/review_points | 技术等价才删除 | NoveltyPointExtractorAgent._review_candidates |
| research/native_tool_loop | 摘要 Reader → 关键未知 → 按需全文 → Reader | Researcher native loop |
| reviewer/review_evidence | 未提及不等于不存在 | NoveltyEvidenceReviewer._render_point_prompt |
| reviewer/review_card（新增） | 单卡中间核验规则 | NoveltyEvidenceReviewer._review_point(card_only=True) |
| reviewer/summarize_reviews（新增） | 局限与截短引文保留 | NoveltyEvidenceReviewer.summarize_reviews |
| search_planner/plan | 核心机制不随放宽丢失 | SearchPlanner |
| coordinator/synthesize | 证据不足的报告表述 | Coordinator synthesize |

哈希见 baseline_manifest.json。Reviewer 公共证据边界在代码中追加到单卡、点级和汇总调用，fallback 与模板共用。
