# Browser 基础设施诊断报告

## 结论

Browser 失败的主因不是 LLM、Researcher、Prompt、BrowserTool contract 或 Chromium 二进制损坏，
而是 **Chromium 子进程的运行环境不完整**：

1. Playwright Chromium 找不到仅安装在 Novelty conda 环境中的 NSPR/NSS/ALSA 动态库。
2. 补齐动态库后，Chromium 仍不会自动使用当前 shell 的 HTTP(S) 代理；生产
   `PlaywrightBrowserBackend` 没有向 `chromium.launch()` 显式传入代理。

在非受限执行环境中同时补齐动态库路径和 Playwright proxy 后，Chromium 成功启动并访问
公开网页，返回 HTTP 200、正确标题与正文。因此基础设施具备可修复性。

本次诊断的模型 API 调用次数：**0**。

## 与 Single-Pass Pretest 的关系

Single-Pass Pretest 的 16 次 Browser 失败均在 `BrowserType.launch` 阶段出现
`TargetClosedError`。本次直接启动测试拿到了被 Playwright 包装前的子进程错误：

```text
chrome-headless-shell: error while loading shared libraries:
libnspr4.so: cannot open shared object file: No such file or directory
```

这证明当时没有真正进入页面导航，候选 URL 质量不是 16 次失败的原因。

## 环境清单

```text
Python: 3.11.15
Playwright: 1.62.0
Chromium revision: 1234
Novelty env: /home/lya3106643285/miniconda3/envs/Novelty
```

磁盘和共享内存均充足：`/tmp` 约 899 GiB 可用，`/dev/shm` 约 7.7 GiB 可用，排除空间不足。

### 动态库

在普通运行环境中对 headless shell 执行 `ldd`：

| Library | 默认解析 | Novelty env 内存在 |
| --- | --- | --- |
| `libnspr4.so` | not found | yes |
| `libnss3.so` | not found | yes |
| `libnssutil3.so` | not found | yes |
| `libasound.so.2` | not found | yes |

完整 Chromium 还缺少 `libsmime3.so`。当前 Playwright 默认使用 headless shell，所以首个可见错误
是 `libnspr4.so`。

`conda run -n Novelty` 只设置 `CONDA_PREFIX` 和 `PATH`，没有设置 `LD_LIBRARY_PATH`；使用
conda 环境的 Python 可执行文件也不会自动让 Chromium 子进程发现 `$CONDA_PREFIX/lib`。

## 分层对照结果

| 层级 | 条件 | 结果 |
| --- | --- | --- |
| Chromium launch | 默认环境 | FAIL：缺少 `libnspr4.so`，exit 127 |
| Chromium launch | 加 conda library path，受限诊断沙箱 | FAIL：权限限制，SIGTRAP |
| Chromium + local HTML | 加 conda library path，非沙箱 | PASS |
| HTTP connectivity | curl 使用环境 proxy | PASS，HTTP 200 |
| 生产 BrowserBackend 外网导航 | 加 library path，但无显式 Playwright proxy | FAIL/悬挂 |
| Playwright 外网导航 | library path + 显式 proxy | PASS，HTTP 200 |

本地 HTML 成功结果：

```json
{
  "launch_with_library_path": "PASS",
  "title": "local-ok",
  "text": "browser infrastructure local test"
}
```

显式代理的外网结果：

```json
{
  "explicit_proxy_navigation": "PASS",
  "status": 200,
  "title": "Example Domain",
  "url": "https://example.com/",
  "text_chars": 129
}
```

## 根因分类

### Root Cause 1：动态库发现失败（已证实）

Chromium 是 Playwright 启动的独立子进程，不会因为调用方 Python 位于 conda env 就自动搜索
该 env 的 `lib/`。缺失库确实存在，但动态链接器搜索路径中没有它们。

这是 Single-Pass Pretest 16 次 `TargetClosedError` 的直接原因。

### Root Cause 2：代理未传递（已证实）

当前网络依赖本地 HTTP 代理。`curl` 自动读取 `HTTP_PROXY/HTTPS_PROXY` 并能访问外网；
Chromium 不自动采用这些变量。生产实现当前为：

```python
playwright.chromium.launch(headless=True)
```

没有 `proxy={"server": ...}`。显式传入同一个代理后外网页面立即成功。

### Diagnostic Constraint：受限执行沙箱（非生产根因）

在受限诊断沙箱内，即使补齐库，Chromium 会因 `Operation not permitted` 被 SIGTRAP 终止；
相同命令在获准的非沙箱环境中成功。因此该项是执行器限制，不是此前缺库错误的解释，也不应
通过向生产代码追加不安全 Chromium flags 来规避。

## 建议修复顺序

1. **优先安装 Playwright 官方系统依赖**，让 Chromium 使用系统动态库：

   ```text
   playwright install-deps chromium
   ```

   或由系统包管理器显式安装 NSPR、NSS、ALSA 等依赖。这比全局设置
   `LD_LIBRARY_PATH` 更稳定。

2. 若部署环境不能安装系统包，只对 Chromium 子进程设置受控 library path。不要在整个 shell
   全局覆盖，因为本次测试已观察到 conda `libtinfo` 与系统 bash 的版本警告。

3. 给 `PlaywrightBrowserBackend` 增加明确的代理装配策略：从 typed config 或经过允许的环境变量
   解析 proxy，并显式传给 `chromium.launch(proxy=...)`。报告和日志不得泄露代理凭据。

4. 增加 Browser preflight，至少检查：

   ```text
   Chromium dynamic dependencies
   Chromium local launch
   local HTML render
   configured proxy connectivity
   one public static-page fetch
   ```

5. 修复后先重跑无模型 `browser-playwright-smoke`，确认：

   ```text
   Browser → Artifact → Reader
   ```

   再重跑 Prompt pretest。不要在 Browser 基础设施尚未通过时评价 Reader/Card 路径。

## 本次未做事项

- 未调用任何模型 API。
- 未加载或打印 API key。
- 未修改生产代码、Config、Prompt、Harness 或 BrowserTool。
- 未将受限诊断沙箱问题误当成需要加入 Chromium 绕过参数的生产需求。

原始结构化结论见 [diagnostic_results.json](./diagnostic_results.json)。
