# 数据库接入简要报告

- 日期：2026-09-07
- 工作分支：`database`
- 基线：`lya` 分支提交 `c861a8b`

## 一、整体思路

项目采用“统一检索流程 + 数据库专属 Provider”的方式接入外部学术数据库：

```text
数据库无关 SearchPlan
    → QueryAdapter（转换为数据库查询语法）
    → SearchTool（搜索并返回统一 SearchHit）
    → Metadata/FullText（补充摘要和可授权全文）
    → SourceRecord / Artifact 持久化
    → Reader 读取原文
    → EvidenceCard 与查新报告
```

工作流、Researcher、Reader 和证据模型保持数据库无关。认证、查询语法、分页、
响应解析和全文权限判断由各 Provider 独立实现。Springer、IEEE Xplore、
ScienceDirect 等数据库可共享 HTTP、重试、限流、缓存和持久化逻辑，但不能共用
具体 API 假设。

## 二、目前已完成

1. 新增外部数据库共享基础设施：
   - API 密钥只从环境变量读取；
   - 支持请求限流；
   - 对 `429` 和常见 `5xx` 响应进行有限重试；
   - 支持 `Retry-After`。
2. 实现 ScienceDirect Provider：
   - 将通用检索计划编译为 Search V2 `qs` 查询；
   - 调用 ScienceDirect Search V2 并将结果统一映射为 `SearchHit`；
   - 使用 PII 调用 Article Retrieval `META_ABS`，为有限数量的候选补齐摘要；
   - 使用 `FULL` 视图尝试获取全文；
   - 对无全文权限或资源不存在的情况安全降级，不把摘要标记为全文；
   - 缓存已获取的文章元数据，减少重复请求。
3. 将 `sciencedirect` 注册到 `RetrievalSourceRegistry`，并支持公共查询编译入口。
4. 增加默认关闭的 ScienceDirect 配置，以及 `ELSEVIER_API_KEY`、
   `ELSEVIER_INST_TOKEN` 环境变量模板。
5. 增加 Provider 接入文档和离线测试：
   - 数据库相关测试 64 项通过；
   - 全仓回归 516 项通过、6 项 live 测试跳过；
   - 另有 2 个既有失败，分别涉及 Chromium 运行库和 Reader 默认 namespace，
     与数据库接入无关。

详细的 Provider 开发约定见 [`database-providers.md`](database-providers.md)。

## 三、待完成工作

1. 编写并运行 ScienceDirect 真实 API 冒烟测试，验证：
   - API Key 和机构令牌；
   - 搜索、摘要及全文响应的真实字段；
   - `401/403/429`、配额和限流行为。
2. 使用真实论文运行 `database_search → reader → EvidenceCard` 端到端测试。
3. 根据真实权限结果，进一步细化 `AUTH_REQUIRED`、`METADATA_ONLY` 和
   `FULL_TEXT_ACQUIRED` 状态记录。
4. 评估多数据库调度策略，避免完全依赖模型临时选择来源；同时验证跨来源 DOI
   去重和来源覆盖率。
5. 按实际需求实现 Springer、IEEE Xplore Provider；Scopus 仅在跨出版社召回不足时
   再评估接入。

## 四、注意事项

- 真实密钥不得写入 JSON、源码、日志、测试数据或 Git 历史，只能保存在本地
  `backend/.env` 或部署环境变量中。
- API Key 不等于全文权限；订阅文章通常还受机构网络、机构令牌或用户授权限制。
- 项目需要保证有效 EvidenceCard 有 Reader 实际读取的可引用原文，但不要求所有
  检索候选都能取得全文。只有摘要时必须保存为 `ABSTRACT` Artifact。
- 每个数据库的查询长度、分页、配额和限流规则不同，应由 Provider 独立校验。
- 全文和摘要的保存、展示及二次使用必须遵守数据库许可与机构订阅协议。
- 未完成真实 API 测试前，只能认定 ScienceDirect 离线契约通过，不能宣称生产环境
  已验证。

## 五、建议的下一步

先在无密钥条件下完成 ScienceDirect 冒烟测试脚本，再由用户在本地配置 API Key，
执行一次小规模真实验证。真实链路稳定后，再决定是否扩展 Springer、IEEE Xplore
或 Scopus，避免同时引入多套未经验证的外部接口。
