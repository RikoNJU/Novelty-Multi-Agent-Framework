# Browser Playwright 真实实验报告

Playwright 1.62.0；仅安装 Chromium。本实验不使用 LLM。

运行环境数据缺口：`playwright install chromium` 只下载浏览器二进制，宿主最初缺少 NSPR、NSS、ALSA 动态库且没有免密 sudo；本次改为在 Novelty Conda 环境安装 `nspr`、`nss`、`alsa-lib`，运行时通过该环境的 library path 启动。部署文档仍需明确系统依赖安装步骤。

| case | status | requested_url | final_url | HTML 长度 | text 长度 | Work ID | Artifact ID | Reader | 耗时 ms | warnings/error |
|---|---|---|---|---:|---:|---|---|---|---:|---|
| public_static | success | https://example.com/ | https://example.com/ | 559 | 129 | wrk_5270d9ad6ef1d79925051349 | art_5b769512c6abf2564ba20d2f | yes | 6168.921 | — |
| javascript_rendered | success | https://quotes.toscrape.com/js/ | https://quotes.toscrape.com/js/ | 8940 | 1499 | wrk_3534a181ed1a2ccc9e49d7f4 | art_508e100e52c49eba3fdbc850 | yes | 7866.177 | — |
| websearch_source | success | https://docs.python.org/zh-cn/3.13/library/asyncio.html | https://docs.python.org/zh-cn/3.13/library/asyncio.html | 25906 | 2620 | wrk_86600422c9a12affdfaa7ea1 | art_83b7c54a418f3dac1bbd334b | yes | 12207.578 | — |

成功 3 项，失败 0 项。WebSearch 候选页面遇到反爬、跳转或导航失败时按真实失败记录，不伪造成功。Reader 仅通过 Browser 返回的 `artifact_id` 读取持久化文本，没有复制 Browser 正文作为输入。
