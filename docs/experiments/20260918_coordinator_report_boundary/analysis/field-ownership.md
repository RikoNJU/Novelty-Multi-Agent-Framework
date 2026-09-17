# 报告字段所有权

| 最终字段 | 本轮来源 | 模型 Draft 能否生成 |
|---|---|---|
| `paper_id` | 冻结 PaperInput | 否 |
| 点集合与顺序 | 冻结 NoveltyBrief／NoveltyPoint；与 Reviewer 和 Draft 精确覆盖比对 | 模型只能引用已有 ID |
| `review_status`、`verdict`、`verdict_reason`、`confidence` | 对应原 Reviewer 对象 | 否 |
| `highly_relevant_works`、`review_evidence`、`feature_comparisons`、`incomplete_reason` | 对应原 Reviewer 对象，逐字段复制 | 否 |
| `summary` | Draft；未完成点改用确定性的受限摘要 | 是，长度受限 |
| `supporting_card_ids`、`counter_card_ids` | Draft 选择；组装前按授权卡片 ID 与所属点校验 | 是，仅已有 ID |
| `limitations` | Draft 的有限表达 + 原 Reviewer 未完成／补查状态、被拒绝原因和检索覆盖未知的确定性说明 | 仅表达性部分 |
| `missing_references`、`missing_baselines`、`citation_issues` | 本节点没有受信条目来源，保留空列表，不能解释为已核实为零 | 否 |
| 原 Card、ReviewEvidence 的 quote、位置、哈希、namespace | 冻结输入；组装不改写 | 否 |

Prompt、fallback 和一次纠错使用同一 `ReportNarrativeDraft` schema；schema 的 `$defs` 仅含 `ConclusionNarrativeDraft`，无 `NoveltyConclusion` 或 `ReviewEvidence` 输出结构。
