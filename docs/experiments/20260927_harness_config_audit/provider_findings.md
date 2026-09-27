# Tool / Provider 审查（2026-09-27）

本轮确认的主要缺口是：Provider 的“已实现”“已注册”“默认开启”“部署中可用”“可读全文”仍被混在一起；Springer 的一种真实零命中响应被误判成技术故障，从而停止确定性放宽链。后者已经局部修复并完成在线、离线验证。本报告不把接口文档、密钥存在或 Mock 测试等同于真实可用。

## 范围与证据边界

- 不调用 LLM、不购买服务、不新增账号、不改变 Provider 默认配置。
- 当前部署条件从已有 `backend/.env` 读取；只记录凭据存在性。所有外部资料访问日期为 **2026-09-27**。价格、配额和授权以正式接入时供应方合同为准。
- 实际探测脚本为 [provider_probe.py](provider_probe.py)，原始脱敏结果为 [修前探测](provider_probe.json) 和 [修后探测](provider_probe_after.json)。普通探测把 timeout 限为 12 秒、关闭自动重试，避免把可用性调查变成持续负载；它不是默认运行模式的性能测试。
- 四个正式数据库 Provider 的实现位于 `backend/src/novelty_agent_framework/tools/database_search/providers/`；registry 在 `database_search/factory.py:19`；生产装配在 `config/factory.py` 的 typed 配置入口。

## Researcher 实际工具能力

| 工具 | 实现与注册 | 当前配置 / 验证 | 模型可见与边界 |
|---|---|---|---|
| `reference_search` | 已实现，typed 入口固定注册 | 本地论文引用库，不等同于外部数据库完整覆盖 | 可见工具描述和 schema；材料仍需 Reader 后形成 Evidence |
| `database_search` | 已实现，至少一个生产来源才可构造 | 本次有效来源为 `arxiv, springer` | 工具 description 动态列出已配置来源；`source_id` schema 仍是任意非空字符串，不是动态 enum，错误来源选择到调用时才被拒绝 |
| `reader` | 已实现、固定注册 | 当前代码支持 `ReaderCallArguments` 批量/单次读取 | 本地 Artifact 可信读取；不是任意 URL 抓取接口 |
| `web_search` | Baidu backend 已实现，可选注册 | 默认禁用；`BAIDU_QIANFAN_API_KEY` 存在，本次未消耗其外部搜索额度 | 禁用时不在工具表中，不能称为“调用权限不足”；密钥存在不证明该 key 有效或账户有额度 |
| `browser` | Playwright backend 已实现，可选注册 | 默认禁用；Novelty-web 环境有 Playwright 包；本次未启动浏览器 | 历史 `docs/experiments/Browser_Runtime_Repair/report.md` 已验证 Chromium、静态/动态页面与 Browser→Artifact→Reader；因此不能沿用“本机缺浏览器所以必失败”的旧配置注释作为当前事实 |
| Reviewer Reader | 单独 reader registry | 只暴露核验读取能力 | 不具有 Researcher 全部检索工具；Reviewer 缺材料不能直接解释为 Provider 权限失败 |

`ResearcherToolRegistry.descriptions()` 实际传出工具的 JSON schema；执行时 Pydantic 校验参数，随后再检查来源存在性与目标论文排除策略。目标论文被排除是 **Harness Policy**，不是数据库拒绝访问。数据库检索本身使用已注入 SearchPlan，LLM 无需重写数据库查询；这些已经收敛的自由度应保留。

## 已实现 Provider 状态矩阵

状态采用多维记录；“默认关闭”可以与“真实验证通过”同时成立。

| Provider | 代码 / 注册 | 示例默认 → 本机有效 | 离线 / 历史验证 | 本次真实验证 | Evidence 材料与剩余条件 |
|---|---|---|---|---|---|
| arXiv API | QueryAdapter + Search + Metadata + HTML/PDF FullText，已注册 | 开 → 开，`search_transport=api` | Mock 契约；多轮真实历史实验；历史存在 429 / timeout | `all:"graph neural network"` 返回 **406**；known-ID `1706.03762` 返回 **200**，Atom 解析成功 | 具备摘要与全文实现；本次没有证明查询可用，也没有重验全文。406 的成因 Unknown，不能判成认证、无文献或整站断网 |
| arXiv Web | 同一 `arxiv` 来源的可选 transport，不是额外数据库 | 未选中 | 有独立 Mock 与历史 web smoke 轨迹 | 本轮未调用 | HTML 页面/全文路径可能补充 API，但切换 transport 应是实验变量，不应隐式发生 |
| Springer Nature | Meta Search + OA/TDM FullText，已注册 | 关 → 开（已有 `NOVELTY_SPRINGER_ENABLED=true`） | Mock 契约与大量真实历史题录/摘要 | Meta **200 / 1 命中 / 1157 字符摘要**；OA JATS **200 / 44,982 字符全文**；精确 no-data 404 修后返回空列表 | Meta/OA key 均存在。OA 全文真实可用；TDM metric 缺失且专项授权未验证，订阅全文能力只能标“条件不足、未验” |
| ScienceDirect | Search V2 PUT、META_ABS 补齐、FULL 获取，已注册 | 关 → 关 | 离线 HTTP Mock 契约通过；本轮未找到该正式 Provider 的真实成功轨迹 | 未调用：`ELSEVIER_API_KEY` 和 `ELSEVIER_INST_TOKEN` 缺失 | 属于“已实现、默认关闭、仅离线验证、凭据不足”；不是确认服务器拒绝授权。全文仍取决于机构订阅/IP/token/用途授权 |
| IEEE Xplore | Metadata Search + OA FullText，已注册 | 关 → 关 | 离线 HTTP Mock 契约通过；本轮未找到该正式 Provider 的真实成功轨迹 | 未调用：`IEEE_XPLORE_API_KEY` 缺失 | “已实现、默认关闭、仅离线验证、凭据不足”；付费全文 token 流程未实现，不能把普通 key 当作付费全文许可 |
| ChinaXiv | 文件只有预留说明；没有 SearchTool / builder 注册 | 不可启用 | 代码记录 2026-08-14 未确认稳定接口；不是已实现 Provider | 官网页面可访问；本轮没有找到已确认的官方搜索 API 契约 | “预留但未实现”；可补中文预印本，须先确认合作/公开接口与许可 |
| `null_catalog` | 已实现的离线空目录 | 示例开但 `testing_only=true`，生产排除 | 测试用途 | 不执行外部请求 | 不能算数据库覆盖或零命中证据 |

Springer 初次已知 DOI 全文诊断使用裸 DOI，缓存中没有该记录，因此 provider 没有发 HTTP 就返回 `None`。这条结果属于 **诊断输入/句柄形式问题**，不属于权限或全文不可获取。随后按现有契约传 `doi:10.1038/s41586-021-03819-2`，真实 JATS 200 并成功解析全文。生产流程从搜索结果缓存 DOI 元数据，所以这不是本轮已确认的生产缺陷。

## 已确认并修复：Springer 零命中导致放宽链中断

**现象。** 历史 `docs/experiments/20260915_184612/supplementary/compare/result.json` 的 `http_events` 记录 Meta API 返回 404，响应明确表示没有匹配数据。2026-09-27 使用同一中文查询复验，收到同样响应。现有 `raise_for_provider_status()` 将其抛成 `ProviderRequestError`；`StructuredSourceRetrievalTool._search()` 将 `provider_failed` 置为真，之后的策略成为 `not_run`。

**根因。** HTTP 状态和 Provider 业务语义没有在适配器边界完成映射。不是模型能力不足、认证失败，也不是应该自动重试的网络失败。

**修复。** `springer.py::_is_meta_no_match_response()` 只在 Meta Search HTTP 404 且同时匹配以下四项、不存在非空 records 时返回成功空结果：

```json
{
  "status": "Fail",
  "message": "No data was found for the given query.",
  "error": {
    "error": "Not Found",
    "error_description": "No matching data is available for the requested query."
  }
}
```

普通 404、HTML 404、字段缺失、冲突 records，以及 401/403/429/5xx 均保持技术失败。没有修改通用 HTTP 错误处理、全文 404 语义、Evidence 标准或 Provider 默认值。LLM 仍判断检索方向；程序恢复原本就应该运行的确定性放宽链。

**验证。** [springer_before.log](springer_before.log) 保存首轮失败。最终集成回归使用两个概念、保护核心概念、允许移除次要概念；[springer_ablation_before.log](springer_ablation_before.log) 在相同最终测试输入下只关闭新识别函数，直接空结果测试与放宽链测试都失败。修后 [springer_after.log](springer_after.log) 的 Springer / HTTP 基础设施 / DatabaseSearch / StructuredRetrieval 共 **55 项通过**。测试确认首条零命中被保留为 succeeded+空 results，后续放宽查询实际运行并保存候选；不是跳过失败断言。

真实同查询修前抛错误，修后 **HTTP 404 + 成功空列表**，见两份在线 JSON。旧中文查询没有因修复获得论文；修复只校正其业务含义。没有据此声称全文工作流已成功。

## 故障分类与尚未修复的问题

| 类别 | 已观察或代码证据 | 可恢复动作 / 应保留的事实 |
|---|---|---|
| 认证缺失 / 失败 | ScienceDirect、IEEE 当前无 key；Springer/IEEE HTTP 401 可抛清洁异常 | 缺凭据在 preflight 发现；401 暂停该凭据域并请求修正，不能当无文献 |
| 授权不足 | 各全文 client 将 403 返回 `None` | 保留摘要与部分事实；记录 entitlement/用途许可不足，尝试已授权 OA；不能把所有 403 都称为 key 错误 |
| API 业务语义 / 协议变化 | 本轮 Springer no-data 404 是已确认实例 | 在具体 Provider 解析明确错误体；陌生结构继续技术失败 |
| 网络失败 | 共享 `ResilientHttpClient` 将 `httpx.RequestError` 压成异常类型字符串；历史 arXiv ReadTimeout | 连接/读取/代理/DNS 分类；有界退避，必要时换来源；不能当零结果 |
| 限流 | 历史 arXiv 429；共享 HTTP 支持 429、部分 5xx 有界重试 | 保留 HTTP status / Retry-After / quota 域，跨任务协调节奏 |
| 服务异常 | 共享 HTTP 500/502/503/504 重试；当前无在线服务故障样本 | 退避后 fallback，标检索覆盖未知 |
| 资源不存在 | 普通 metadata/fulltext 404 | 查句柄或替代版本；与明确 no-data search 404 分开 |
| 全文不可获取 | Springer/IEEE/ScienceDirect 403 与 404 均 `None`；arXiv `_try_get` 对 HTTP/transport 异常均 `None` | 当前无法可靠区分未授权、缺文献、网络失败、解析无正文；应返回结构化 `AcquisitionOutcome`，保留局部摘要 |
| Harness Policy | 目标论文排除、预算耗尽、禁用工具 | 由 Runtime 输出允许的后续动作；不归责 Provider |
| 模型参数 / 工具选择 | `source_id` 非空但不在 tools_by_source；Reader schema 迁移旧测试 | 校验前提供真实来源枚举和可用状态；修复参数后再执行，不消耗外部请求 |
| Unknown | 本次 arXiv 查询 406，known-ID 同时 200 | 保留请求操作和脱敏响应事实；没有充分证据判断是请求协商、上游策略还是其他服务条件 |

其他具体风险：

1. `common.py` HTTP 异常缺少结构化 `provider/operation/status/retryable` 字段；所有认证数据库的 Runtime physical request 都记为 `authenticated_database`，不利于分库预算归因。网络异常当前直接抛出，不会像可重试 HTTP status 那样重试。
2. `sciencedirect.py::ScienceDirectSearchTool.search` 的摘要补齐只 catch `httpx.HTTPError, ValueError`，共享 transport 的网络错误已改为 `ProviderRequestError(RuntimeError)`；因此网络失败可能使整个 Search 调用失败而非保留已召回候选。代码路径确认，尚未新增实验/修复。
3. 多个 Provider 用 `payload.get('records', [])` / `get('articles', [])` / `get('results', [])`，某些 HTTP 200 但错误 envelope/协议漂移可能被当空结果；正式扩展前应验证响应 envelope，不能将缺少成功结构等同于 empty。
4. 各来源成功取得候选和成功取得全文是不同能力；当前可用来源列表没有把 search/abstract/OA/subscription capability 与最近故障投影给模型。优先新增 preflight 能力清单和运行态健康状态，避免模型通过重复失败试出事实。
5. 首轮 139 项定向离线测试出现两项旧失败：arXiv Retry-After 30 秒断言与实际 29.999958 秒的计时精度差；Reader 测试仍断言旧 `ReaderArguments` 身份。它们不属于本次 Springer 修复结果，也不能作为真实 Provider 服务失败计数。

## 覆盖缺口与全部候选来源

目前有效外部数据库是 arXiv + Springer；它们不能代表中文期刊/学位论文、全部工程会议、专利、科技成果/科技报告的完整覆盖。仅增加元数据聚合器也不能自动满足 Evidence 所需的原文。推荐按“覆盖缺口 × 可获得材料 × 授权/运行成本”分阶段实施。

| 来源 | 当前状态 | 补充覆盖 / Evidence 能力 | 接入条件与成本（官方资料） | 建议 |
|---|---|---|---|---|
| arXiv | 已实现、实际可用性局部 | 预印本、摘要、HTML/PDF | 无 API key 路线；仍需限速与故障处理 | 先稳定 query/known-ID/全文分项探针，不以 known-ID 200 宣称搜索健康 |
| Springer Nature | 已实现、Meta/OA 本轮验证 | 跨学科题录、摘要、OA JATS | 免费计划当前 500 hits/day、100 hits/min；TDM 是单独许可和配置，升级报价按方案。[订阅](https://dev.springernature.com/subscription/)、[OA API](https://dev.springernature.com/docs/api-endpoints/open-access/)、[TDM](https://dev.springernature.com/docs/api-endpoints/fulltext-api/) | 优先保证已有能力与精确 empty/failure 分离；订阅全文后置 |
| ScienceDirect | 已实现、缺凭据、在线未知 | Elsevier 期刊/图书章节与授权全文 | API key + 机构权益/IP 或 token；学术/公共非商业使用可免费但有限制，商业需许可/订阅。[认证](https://dev.elsevier.com/tecdoc_api_authentication.html)、[方案](https://dev.elsevier.com/sd_apis.html)、[配额](https://dev.elsevier.com/api_key_settings.html) | 先取得已有机构接入条件再做最小 search→abstract→fulltext 验收，不新增代码堆数量 |
| IEEE Xplore | 已实现 OA 部分、缺凭据 | 工程/电子/计算机会议与标准元数据；OA 正文 | key 申请；收费全文须授权 key 换 token，当前不支持。[API](https://developer.ieee.org/docs)、[收费全文](https://developer.ieee.org/Chargeable_Full_Text_Requests) | 针对工程查新有价值；先免费 metadata/OA 验证，订阅全文独立实施 |
| ChinaXiv | 预留未实现 | 中文预印本、首发时间、可用全文 | 官方首页可见检索/下载；本轮未确认公共 API 契约与批量许可，费用 Unknown。[官网](https://www.chinaxiv.org/home.htm) | 优先调查稳定接口；没有接口时记录人工检索覆盖，不伪装已接入 |
| OpenAlex | 完全未接入 | 跨出版社发现、引用图、OA 链接；部分 cached PDF/TEI | 最新文档允许无 key 小规模查询；免费 key 每日 $1 额度。搜索 $1/1000 次、内容下载 $10/1000 次；数据开放不等于 API 无限免费。[认证](https://help.openalex.org/api/authentication/)、[费用](https://help.openalex.org/access/example-costs/) | 第一批候选：元数据发现 + OA 定位；配置预算硬上限，需保留全文授权与 provenance |
| Crossref | 完全未接入 | DOI/出版日期/版本/撤稿等核验，跨出版社元数据；摘要取决于 deposit，链接不是全文本身 | 公共 REST 不需注册；polite pool 使用联系信息；高级保障另行评估。[REST](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)、[全文链接过滤](https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/) | 第一批候选：先做 DOI/元数据核验与去重补全，不把 metadata-only 当技术特征证据 |
| Semantic Scholar | 完全未接入 | 论文/引文图、关联候选与摘要/OA 链接 | 多数端点匿名可用但共享限流；申请 key 初始 1 RPS；具体 API/数据许可用途应确认。[官方 API](https://webflow.semanticscholar.org/product/api)、[教程](https://webflow.semanticscholar.org/product/api/tutorial) | 第二批候选；以增量 recall 与可读原文比例比较 OpenAlex，避免冗余接入 |
| 万方 | 完全未接入 | 中文期刊、学位等目标覆盖应以采购目录确认；正文权利未知 | 官方确有开放平台 API 目录及云 API 网关，但公开页未提供本项目可直接确认的套餐/全文授权。[开放平台](https://apps.wanfangdata.com.cn/open)、[云平台](https://cloud.wanfangdata.com.cn/) | 中文覆盖优先商务/图书馆调查；先拿 API 契约、试用额度和机器处理权限，费用 Unknown |
| 知网 | 完全未接入 | 中文文献/学位论文覆盖候选；具体库和 Evidence 材料需合同确认 | 本轮官方首页跳到海外入口，未找到足够可靠的公开 API/价格文档；不能据此声称不存在 API 或无需许可。[官方入口](https://www.cnki.net/) | 与万方一起做机构合同调查；本轮保持 Unknown，不接未授权爬虫 |
| 学校 / 图书馆 API | 完全未接入，学校与系统未指定 | 本校馆藏、联合发现与合法全文入口，可补学位论文及订阅可获得性 | 例如 Primo hosted Search API 需机构 API key；本地部署使用机构码/guest JWT；搜索授权不等于全文授权。[Primo API](https://developers.exlibrisgroup.com/primo/apis/) | 获取机构名称、系统产品、订阅/TDM 条件后评估；价格/可用性 Unknown |
| 专利：EPO OPS | 完全未接入 | 全球题录、法律事件与可用 claims/description；明显不同于论文覆盖 | OAuth 注册；每周 4 GB 免费，超出当前年费 EUR 2,800；自动查询用 REST。[OPS](https://www.epo.org/en/searching-for-patents/data/web-services/ops)、[使用额度](https://www.epo.org/en/service-support/ordering/fair-use) | 专利方向优先 PoC；先加 publication/application/family/date/claim 类型契约，不能沿用论文标题+摘要全部语义 |
| 专利：中国 CNIPA 数据服务 | 完全未接入 | 中国/多国专利基础数据及专利原文 | 官方答复引导注册知识产权数据资源公共服务系统；这不足以证明存在匿名搜索 API。[官方答复](https://www.cnipa.gov.cn/jact/front/mailpubdetail.do?sysid=12&transactId=496965)、[公共平台](https://ggfw.cnipa.gov.cn/home) | 确认数据目录、下载/接口契约与账户许可；可考虑授权数据本地索引，成本 Unknown |
| 科技成果 / 科技报告：NSTRS 等 | 完全未接入 | 项目技术报告、实施细节和科研产出，补论文外证据 | 国家科技报告系统对公众提供摘要；实名专业人员可在线全文浏览，官网说明不能下载保存全文，公开机器 API 未确认。[官方服务说明](https://www.nstrs.cn/index) | 先作为人工核验来源或获专门许可后接入；不可将在线阅览直接转为可持久化全文 Artifact 权限 |

OpenAlex 的旧博客曾称所有请求必须 key，而最新 Help Center 明确保留匿名预算。本表采用本轮访问的最新官方帮助页，并把认证方式与价格放入未来 Provider profile；不要把历史限额常量写死在业务代码。

## 实施顺序与验收

1. **已有来源可靠性先行**：落地 Provider capability/preflight 清单；`search_result`、`no_match`、`technical_failure`、`partial` 明确分开；全文获取返回结构化 outcome；按真实 provider/operation 统计物理请求和恢复动作。
2. **低成本补覆盖**：Crossref 作为 DOI/出版事实核验、OpenAlex 作为跨出版社发现/OA 定位，先离线契约与固定 known-item 集，再受控在线验收。新增接入必须说明独有召回量、可读取摘要/全文比例、重复率、配额消耗与实际 Evidence 增量。
3. **中文与非论文覆盖**：万方/知网/图书馆先调查现有机构授权；专利先建立特有标识与时间/claim 契约；ChinaXiv/NSTRS 未确认接口的来源保持人工/Unknown 状态。
4. **运行时原则**：技术故障只说明覆盖缺口，不能推导没有相关文献；真实零命中可以触发放宽，但不代表查新结论成立；摘要可保存已证实局部事实，不能被标为全文。

已经验证解决：Springer 精确 no-data 404 的业务映射与后续放宽可执行性。已有真实能力：Springer Meta/OA；arXiv known-ID。仍存在：arXiv 查询 406、全文失败类别丢失、来源健康与能力未完整投影、中文与专利/科技报告覆盖缺口。确认属于模型能力边界：本子任务没有这种结论，因为所有实验都不调用模型。
