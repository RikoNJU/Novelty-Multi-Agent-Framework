# arXiv 限流收口验收

## 1. 原始问题是什么？

Web 请求失败被吞成正常零命中；连续失败计数没有真正熔断；多实例物理请求节流与 Runtime Debug 完整性没有正式验收。

## 2. 根因是什么？

`search()` 捕获通道异常后返回 `()`，使 fallback 与基础设施故障混淆。旧 Session 只有局部发射时间和错误计数。API 原有逻辑事件及 smoke 线程池的 Runtime 上下文也存在漏记。

## 3. 修改了什么？

基于 `origin/lya@43ba4fb`，仅移植 hyl `67e5560` 的 arXiv Web 能力与配置/夹具。新增进程共享 Web 闸门、有限重试及总预算、Retry-After、CLOSED/OPEN/HALF_OPEN 单探测熔断；Web 全文和重定向每跳同样经过闸门。检索故障抛出并停止伪 fallback，Runtime 区分 ZERO_RESULT/PROVIDER_FAILED。API 补逻辑事件、批次任务标识和熔断诊断。默认仍用 API，Web 默认间隔保留 8 秒。Research Task 并发保持 4；没有改 SearchPlanner、Reviewer、Renderer 或检索词策略。

## 4. 实验结果是什么？

- [离线](offline-tests.md)：154 项定向通过；全仓库 830 passed / 6 skipped / 1 个已在原始 lya 复现的 Reader 旧断言失败。
- [API](api-smoke.md)：17 次逻辑、7 次物理，全部 200；10-ID batch 和四并发逻辑请求通过，0 interval violation。Runtime 17/7 与 scheduler 一致。
- [Web](web-smoke.md)：8/6/4/2 秒各 8 次，共 32/32 命中；0 网络故障、0 retry、0 interval violation。
- [并发](parallel-smoke.md)：四线程 provider smoke 8/8 命中；正式 NP-2 两任务同时运行，16 次物理请求全部 200，最小间隔 8000.10 ms。
- [PaperInput](full-workflow.md)：三轮全部结束；完整工作流 986.37 秒，最终 3 张卡，其中 2 张来自新 Web 候选，完整性检查通过。复用相同 PaperInput 和参考缓存，无 MinerU。

## 5. 当前还剩什么问题？

本次实际 API 可用，但不保证其他时刻出口不会收到 429；故障路径由离线 HTTP 注入验证。32 个重复主题样本不足以证明长期 2 秒安全，因此保留 8 秒默认。前两轮仅缓存参考文献成卡，新 Web 候选的完整成卡链路已由第三轮补证；完整流程中的 2 次 HTTP 406 均正确标记 PROVIDER_FAILED，没有伪装 EMPTY。限流相关工程能力已收口，但不保证服务器永远返回 200。检索相关性和 fallback 质量按任务书留到独立任务。
