# 实施记录

执行：`python scripts/single_point_stability_audit.py --repo . --output <dir>`。

该脚本不导入工作流、Provider 或模型客户端，只读取归档 JSON 并写入新目录。费用：0 模型调用、0 Provider 请求、0 Reader 获取。
