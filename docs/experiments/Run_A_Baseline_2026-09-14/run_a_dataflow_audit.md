# Run A：数据链完整性审计

## Chain A：Point → Task

结果：`PASS`。

- 2 个 NoveltyPoint，各产生 zh/en 两个 Research Task，共 4 个。
- 每个 task 的 `novelty_point_id` 均能回溯到对应 point。
- 无孤立 task、无漏掉的 point。
- 注意 `task_id` 只在 point 内唯一，跨 point 的 T-1/T-2 会重复。

## Chain B：Task → Search → Artifact → Reader

结果：`PARTIAL`。

- 四个任务均从 reference_search 得到过候选；7 次非空 reference_search 均返回 8 条。
- 9 次 database_search 均对 Agent 表现为 EMPTY；5 次 arXiv 调用内部 30 次执行全部失败。
- 当前两个 namespace manifest 均可验证，0 文件完整性失败。
- 14 次 Reader 全部成功，且实际读取的 artifact namespace 可从结果识别。
- 6 条最终 Evidence 全部来自 `subject_reference`；数据库链没有贡献任何 Run A Evidence。
- 两个中文任务最终零 Evidence，故此链不是全量闭合。

## Chain C：Artifact → EvidenceCard

结果：`PASS（仅对已生成 Evidence）`。

- 6 条 Evidence 对应 6 张 EvidenceCard。
- 6 个 evidence binding 均能解析到 manifest 中的 subject-reference artifact。
- Gate A 接受 6/6 卡，0 rejected，未发现“有卡但来源断裂”。
- 两个中文任务没有卡，属于上游覆盖缺口，不是已有 Card 的引用闭包错误。

## Chain D：EvidenceCard → Reviewer

结果：`PARTIAL`。

- review stage 保留全部 6 张卡，point 覆盖为 2/2，无重复或意外 point。
- 但 Reviewer 在冻结配置中 disabled；输出是每 point 一条 `insufficient_evidence` 占位 review。
- 两条 review 的 verdict/reason/confidence 均为 null，highly_relevant_works 为空，因而没有 Card/Evidence 业务引用可审计。
- reviewer diagnostic 为 WARNING，提示 supplement_request 不控制 V0 路由。

## Chain E：Reviewer → Final Report → Renderer

结果：`FAIL（语义链未闭合）`。

| Point | Review | Final report | Rendered report |
|---|---|---|---|
| NP-1 | `insufficient_evidence`, verdict null | `strong`, confidence 0.80 | 展示 strong 结论 |
| NP-2 | `insufficient_evidence`, verdict null | `strong`, confidence 0.75 | 展示 strong 结论 |

Runtime state 在 synthesize stage input 中包含 `novelty_reviews`，但 `NoveltyWorkflow._synthesize_report()` 调用 `Coordinator.synthesize()` 时只传 paper、brief、evidence、rejected_evidence、insufficient_final_evidence_points，没有传 novelty_reviews。Renderer 的 workspace 输入包含 paper/evidence/report，不读取 `novelty-reviews.json`。

因此 Gate B 的 Card 引用完整性虽然 PASS，仍不能保证 Reviewer 业务语义进入最终报告。Run A 实际证明“报告成功”与“裁定链闭合”是两件事。

## 总结

| Chain | Result |
|---|---|
| Point → Task | PASS |
| Task → Search → Artifact → Reader | PARTIAL |
| Artifact → EvidenceCard | PASS（对已有 Evidence） |
| EvidenceCard → Reviewer | PARTIAL |
| Reviewer → Final Report → Renderer | FAIL |
