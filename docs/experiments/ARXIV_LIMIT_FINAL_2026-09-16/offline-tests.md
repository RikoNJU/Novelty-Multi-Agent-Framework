# 离线验收

Python: `/home/lya3106643285/miniconda3/envs/Novelty/bin/python`。默认不运行 live marker。

- 最新 arXiv / retrieval / runtime 定向测试：**154 passed**，结果见 [offline-targeted.log](offline-targeted.log)。覆盖 API 多线程 search、search/metadata 混合、batch/dedup、429、Retry-After、timeout、budget、OPEN、半开成功/失败；Web 200有/无结果、403/429/503、timeout/connect error、retry、共享gate、共享circuit、半开并发、重定向每跳与全文调度；retrieval 停止故障 fallback、保留真实 zero fallback、Runtime 落盘。
- 最终全仓库离线回归：**830 passed, 6 skipped, 1 failed**，见 [offline-full-final.log](offline-full-final.log)。首次广泛检查为 825 passed。失败为 `test_reader_uses_canonical_arguments_and_legacy_alias`；在未修改的 `43ba4fb` 导出目录单独运行亦失败，见 [基线复核](offline-baseline.log)。属于 lya 既有 Reader schema 断言过期，本任务未修改 Reader。
- 首次在受限沙箱内，asyncio 线程完成后事件循环没有被唤醒。取得 faulthandler 栈后终止，切换沙箱外执行相同 mock 测试通过；不是通过真实 arXiv 网络替代离线测试。
- 最终代码提交：`9222d37`；测试/smoke 提交：`674c7ff`。
