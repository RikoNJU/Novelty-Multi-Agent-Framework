# Run A：Failure Taxonomy

## 1. Search backend failure：arXiv 全失败

- Count：30 个 internal search execution；25 timeout，5 HTTP 429。
- Affected：NP-1/T-1、NP-1/T-2、NP-2/T-1、NP-2/T-2。
- Representative Tool Call：`tool_0003`。
- Runtime artifact：`tools/0003_database_search.json`。
- Suspected layer：Tool / external backend。
- Root Cause：网络层具体原因 `UNKNOWN`；已确认直接异常为 arXiv ReadTimeout/429。

## 2. Search normalization failure：后端失败被归为 EMPTY

- Count：5 个外层 arXiv database_search Tool Call，内部共 30 个 failed execution。
- Affected：全部 4 个任务。
- Representative Tool Call：`tool_0009`。
- Runtime artifact：`tools/0003_database_search.json`, `tools/0009_database_search.json`, `tools/0018_database_search.json`, `tools/0030_database_search.json`, `tools/0036_database_search.json`。
- Suspected layer：Tool normalization / Harness observation contract。
- Root Cause：CONFIRMED——外层 Tool result 在内部执行全部失败时仍返回 `succeeded=true` 与空 results，Runtime 按外层结果记为 `SUCCESS/EMPTY`。

## 3. Harness policy failure：reference_search 预算耗尽

- Count：2。
- Affected：NP-1/T-1、NP-2/T-1（均为中文任务）。
- Representative Tool Call：`tool_0007`。
- Runtime artifact：`tools/0007_reference_search.json`, `tools/0027_reference_search.json`。
- Suspected layer：Agent / Harness policy。
- Root Cause：CONFIRMED——每任务 `reference_search` 上限为 4，第 5 次调用在 PRE_TOOL 阶段被拒绝；模型为何持续重复搜索为 `UNKNOWN`。

## 4. Reader failure

- Count：0。
- Diagnostic：`diagnostics/reader.json`，status `OK`，14 succeeded / 0 failed。
- Run A 未复现 WRONG_NAMESPACE、LOST_MANIFEST_ENTRY、NEVER_PERSISTED、FILE_NOT_FOUND、PARSE_ERROR。

## 5. Reference diagnostic false positive

- Count：28 条错误（14 个 Reader Call 各两条）。
- Affected：所有 Reader 调用，但不代表业务读取失败。
- Representative Tool Call：`tool_0010`。
- Diagnostic artifact：`diagnostics/reference_namespace.json`。
- Suspected layer：Runtime diagnostic。
- Root Cause：CONFIRMED——新 Reader 请求参数不再包含 namespace，实际 namespace 位于 read result；诊断器仍比较缺失的 request namespace，并尝试将 `None` 转成 ArtifactNamespace。

## 6. Reviewer semantic failure

- Count：2 个 point 无实际裁定。
- Affected：NP-1、NP-2 及最终报告。
- Runtime artifact：`stages/0014_review_evidence/output.json`, `stages/0017_synthesize_report/output.json`。
- Diagnostic artifact：`diagnostics/reviewer.json`。
- Suspected layer：Configuration / Workflow / Schema / Renderer。
- Root Cause：分两层：Reviewer 未执行是冻结配置 `reviewer.enabled=false` 的直接结果；review 结果未进入 synthesis 参数是代码契约已确认事实。两套 verdict/level 语义如何闭合仍为 `UNKNOWN`，不得直接硬编码映射。

## 7. `.txt` artifact 检查

- `research_reference`：39/39 artifacts 为 `.txt` + `text/plain`；22 `extracted_text`，17 `abstract`。
- `subject_reference`：9/9 artifacts 为 `.txt` + `text/plain` + `abstract`。
- 两个 manifest 均 valid，0 integrity failure；6 条最终 Evidence 绑定全部 resolved。
- 结论：Run A 中 `.txt` 与声明的文本化 role/media type 一致，没有证据表明扩展名错误或 Reader 前处理被误当原始文件。KNOWN-04 在本次运行不成立为 bug；原始载荷是否应额外保留属于产品/数据保留策略，Root Cause/Expected 均为 `UNKNOWN`。
