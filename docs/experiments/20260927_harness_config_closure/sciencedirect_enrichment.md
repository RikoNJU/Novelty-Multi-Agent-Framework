# ScienceDirect 摘要补齐失败保留已召回候选

日期：2026-09-28。仅离线 MockTransport 故障注入；没有真实 Elsevier 请求，没有模型调用，没有启用新 Provider 或改变默认配置。

旧 Provider 审查定位的问题仍在：`ScienceDirectSearchTool.search` 先由 Search V2 获得 retained hits，再对前若干条请求 META_ABS。共享 transport 把 `httpx.RequestError` 转成 `ProviderRequestError(RuntimeError)`，但补齐循环仅捕获 `httpx.HTTPError/ValueError`；因此一次可选摘要网络失败会使整次 search 抛错，已召回候选无法返回。

先新增回归，修前 **3 failed / 11 passed**，见 [sciencedirect_before.log](sciencedirect_before.log)：ReadTimeout、ConnectError 均复现候选整体丢失；既有 HTTP503 捕获虽保留候选，但没有显式补齐失败元数据。

最小修改只在该 Provider 的可选 enrichment 边界：补充捕获 `ProviderRequestError`，保留原 SearchHit 的标识、标题、DOI 和 discovery metadata，继续处理后续候选。失败候选仍无补齐摘要，不伪造材料，也不写进 article cache 当成“资源不存在”。原 abstract_enrichment_limit 继续约束请求数，不增加自动重试。

`raw_metadata.abstract_enrichment` 保存 `status=failed`、异常类型、共享 transport 的已知网络异常类型、已知 HTTP 状态。没有保存异常全文、URL、headers 或 body；该字段是候选补齐状态，不声称搜索本身失败或文献不存在。成功搜索与失败补齐是不同操作。

首个 Search V2 的 transport 失败仍然向上抛 `ProviderRequestError`，不能返回空列表伪装零命中；物理 Provider 预算异常、其他 RuntimeError 同样保留，不被补齐降级捕获。这条变更不接管原 403/404→None 的其他语义，也不修改全文获取契约。

定向及相邻回归 **49 passed**（包含 14 项 ScienceDirect），见 [sciencedirect_after.log](sciencedirect_after.log)、[JUnit](sciencedirect_tests.xml)、[验证清单](sciencedirect_validation.json)。主要断言：

- 三候选、前两条允许补齐时，第一条网络失败，三条 discovery metadata 都保留；第二条摘要成功，第三条未额外请求。
- 真实共享 transport 转换异常的路径得到验证，不是直接 mock search 返回成功。
- 失败仅记录安全状态，不复制异常细节；瞬时网络失败不缓存为无材料。
- 首搜索失败、硬预算异常及未预期程序异常继续传播。

这项修复只关闭已经定位的候选损失路径；没有证明 Elsevier 凭据/机构权益或在线摘要/全文可用。新增 raw_metadata 状态保留事实，但不单独宣称所有恢复/报告消费者都已消费这个局部字段；统一业务事件整合以主任务恢复报告为准。
