# hyl prompt 整合与 Researcher skills

## 来源和范围

已 fetch 远端 hyl，本次对比基准为 `bbf5c9de9f9e6bc4438b762ea1ee9f875fe4cf5b`。在 lya 上选择性整合 prompt 语义，没有合并 hyl 的其他检索覆盖工程、语言配置、原件存储或历史输出。

- Researcher：吸收 hyl 数据库优先、SearchPlan 内调整查询、取得文本立即读取的规则；保留 lya 的预算整理和严格引文规则。中文任务不再自动走 Web 主路径。
- Coordinator supplement：吸收只生成启用语言的规则；当前接口固定 zh/en，因此以现有语言集合适配，未新增 hyl 语言配置接口。
- Coordinator synthesize：吸收检索失败、成功零命中、命中但无有效证据三类限制说明。当前接口没有 hyl 的 retrieval_coverage 字段，删除无来源占位符；缺少执行事实时明确标为覆盖未知，不允许由卡片数推断。
- Reviewer：根据 Evidence.provenance.evidence_type 区分 database_evidence 与 web_supplement_evidence。Web 默认作为数据库覆盖不足后的辅助证据，明确外部上下文任务作为例外；既不自动拒绝 Web，也不把它视为数据库覆盖证明。

## 两个应用 skill

`skills/database_research/SKILL.md`：Database → source artifact → text → Reader → Evidence。原件优先，但不声称当前工程已经保存完整原件；完整 original artifact 工程留给第三部分。

`skills/web_supplement/SKILL.md`：只在 DATABASE_UNAVAILABLE、DATABASE_EMPTY、FULLTEXT_UNAVAILABLE、DATABASE_EVIDENCE_INSUFFICIENT、TASK_REQUIRES_EXTERNAL_CONTEXT 条件下进入，要求依据工具事实或明确任务说明触发原因。未读候选不能直接证明证据不足；语言不是触发条件。无 acquisition 路径时只有 discovery，不能产原始 Evidence。

两个 skill 均接入正式 Researcher 和无 PromptLibrary 的 fallback 系统上下文。触发条件在本阶段是 prompt/skill 约束，没有增加确定性工作流状态机或工具路由门禁，未用在线模型验证遵循率。

## 最小来源传递

新增 SourceKind.WEB_SUPPLEMENT，保留旧 WEB 枚举兼容归档。WebSearch 保存 source_kind=web_supplement；Browser 的来源记录和 artifact provenance 保留该标记。Builder 由持久化来源绑定 evidence_type 和 source_kind，Web acquisition 优先于文献的数据库身份；未知来源不猜测为数据库证据。Reviewer 输入完整保留 Evidence provenance。

明确标记 content_origin=llm_summary 的 artifact 即使通过 Reader，也不能被 Builder 用作原始 Evidence。未标记文本的自动语义识别不在此阶段；LLM summary、snippet 不能当原始证据的行为规则也写入 prompts/skills。

## 验证

- 完整默认回归：722 项，716 passed，6 skipped，0 errors/failures，见 tests.xml。
- 补充 Reviewer 实际模型消息传递验证后：9 项定向测试通过，覆盖数据库/Web/历史 Web/未知来源、Web acquisition 不升级、LLM summary 拒绝、skills 实际加载、模板与 fallback Reviewer 的类型传递，见 focused.xml。
- git diff --check 通过。
- skill-creator quick_validate 只报告两个名称使用下划线不符合其通用 hyphen-case 规则。按用户明确指定的 database_research、web_supplement 保留名称；这是项目应用 skill，运行时加载已验证。

未运行在线论文实验，未提交或推送。本次完整测试另外生成了一个 demo runtime 目录，保留在工作区。
