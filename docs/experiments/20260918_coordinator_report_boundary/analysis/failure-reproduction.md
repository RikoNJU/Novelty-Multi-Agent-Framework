# O0：旧报告 JSON 截断的零调用复现

直接读取两份失败 run 的原始 Runtime `llm_calls` 响应正文，逐份用 `json.loads` 检验；四份均不能解析。具体响应路径、SHA、末尾受控摘要、错误位置和原始 usage 见 `original-response-index.json`。原 Runtime 导出没有保存 `finish_reason`，因此该字段为未知，不能写成提供商明确返回 `length`。两份 run 的请求均为 `max_tokens=4096`；各次完成 token 减去所报 reasoning token 恰为 4096。此计算只作为当前供应商响应的截断迹象，不定义跨模型通用计费或终止规则。

新报告路径面对明确 `finish_reason=length` 时直接停止；面对末尾不完整字符串或到限的无标记响应时记录疑似截断并停止同条件盲重试。完整但非法 Draft 才最多做一次使用同一 Draft schema 的纠错。旧原始响应和原账本均未被修改。
