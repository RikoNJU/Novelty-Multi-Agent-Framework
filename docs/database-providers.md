# 数据库 Provider 接入

结构化数据库统一通过 `RetrievalSource` 接入。工作流、Researcher、Reader、
Artifact 持久化和 EvidenceCard 构建不包含数据库分支。

## Provider 边界

每个数据库实现一个模块，并提供：

- `QueryAdapter`：把数据库无关 `SearchPlan` 编译为数据库查询；
- `SearchTool`：执行查询并返回统一 `SearchHit`；
- `MetadataTool`：可选，核验标题、DOI 和落地页；
- `FullTextTool`：可选，返回已获授权的可读文本；
- `build_<provider>_source(config)`：组装同一 `source_id` 的能力包。

共享 HTTP 能力位于 `providers/common.py`，负责从环境变量读取密钥、限流和
有限重试。查询语法、认证请求头和响应解析必须保留在具体 Provider 中。

## 新增数据库

1. 在 `providers/` 新建模块，例如 `ieee_xplore.py`；
2. 实现上述能力并统一映射为 `SearchHit` / `FullText`；
3. 在 `database_search/factory.py::build_source_registry` 延迟注册 builder；
4. 在 `researcher.example.json` 的 `tools.database_search.providers` 添加默认禁用配置；
5. 在 `backend/.env.example` 只声明环境变量名，不写真实密钥；
6. 使用 `httpx.MockTransport` 覆盖查询、分页、权限、限流、摘要和全文降级测试。

## ScienceDirect

已提供首个 HTTP Provider 骨架：Search V2 返回候选 PII，Provider 对有限数量的
候选调用 Article Retrieval `META_ABS` 补齐摘要，并通过 `FULL` 视图尝试取得全文。
真实密钥只从 `ELSEVIER_API_KEY` 读取；机构令牌为可选的
`ELSEVIER_INST_TOKEN`。全文无权访问时返回 `None`，由通用检索链保留摘要，绝不把
摘要标记为全文。

## Springer Nature

`springer` Provider 使用 Meta API `meta/v2/json` 检索元数据和摘要。全文模式：

- `disabled`：不调用全文接口；
- `openaccess`（默认）：仅对 Meta API 明确标记为开放获取的候选调用
  Open Access JATS 接口；
- `tdm`：调用 `xmldata/jats`，必须配置 `SPRINGER_NATURE_TDM_API_METRIC`，且必须
  已取得 Springer Nature 的专项 TDM 授权。

API Key 从 `SPRINGER_NATURE_API_KEY` 读取。JATS 会被解析为纯文本和章节映射；
响应 URL 中的 Key 不会写入 Artifact provenance 或错误信息。

## IEEE Xplore

`ieee_xplore` Provider 使用 Metadata Search API 检索题录和摘要，并以 IEEE
`article_number` 作为全文请求标识。`full_text_mode` 支持：

- `disabled`：只保存题录和摘要；
- `openaccess`（默认）：只调用 IEEE Open Access full-text endpoint，订阅内容自动
  降级到摘要。

API Key 从 `IEEE_XPLORE_API_KEY` 读取。IEEE 的付费全文 API 需要另行签约、客户凭据
和短期 token 流程，本 Provider 不会仅凭普通 API Key 尝试下载付费全文；取得正式
接口参数后应另行扩展，而不是复用开放全文模式。

Springer Nature 和 IEEE Xplore 复用相同 HTTP 基础设施，但各自保留查询编译、响应
映射和授权判断，不复用 ScienceDirect 的 API 假设。
