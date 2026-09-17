# 真实恢复报告只读接入

任务 `RPT-ACCESS-20260918`。基线 `b4b6623`。本轮业务模型、检索、解析和工作流启动调用均为 0。L1、L2 的真实响应、原失败 Runtime、captured 重组与最终文件均已重新核对；受控发布包和持久化资源保存在本机 `outputs/report-publication-20260918/`，正文与原始模型响应不进入本目录。

本目录包含脱敏索引、接口图、实际后端浏览器验收及边界说明。资源从浏览器使用 `/?report_resource_id=<id>` 打开；页面调用正常后端 GET，不创建成功业务 run。原来源状态仍为 `FAILED`。

参见 [报告](report.md)、[验收台账](acceptance-status.json)、[来源索引](archive/real-source-index.json)、[接口图](api/interface-map.md)。
