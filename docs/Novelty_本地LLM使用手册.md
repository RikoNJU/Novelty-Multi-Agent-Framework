# Novelty 本地 LLM 使用手册

> 当前状态：开发 / 调试 / 实验用 Baseline\
> 当前模型：Qwen2.5-7B-Instruct\
> 推理服务：vLLM / OpenAI-compatible API\
> 更新日期：2026-09-25

这份文档解决一个问题：

> **在自己的电脑上运行 Novelty，但让 LLM 推理使用实验室服务器的 GPU。**

你**不需要在自己电脑上下载模型**。

------------------------------------------------------------------------

# 一、第一次使用

只需要配置一次。

## 1. 获取服务器登录信息

向组内成员获取：

-   服务器地址
-   SSH 用户名
-   SSH 端口（如果不是 22）
-   登录方式

这些信息不要提交到 GitHub。

## 2. 配置 SSH Alias

以下命令都在你自己的 WSL 中执行。

``` bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/config
```

加入：

``` text
Host lab-novelty
    HostName <服务器地址>
    User <用户名>
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

如果有指定端口，再加：

``` text
    Port <端口>
```

如果使用 SSH Key：

``` text
    IdentityFile ~/.ssh/<PRIVATE_KEY>
```

保存后设置权限：

``` bash
chmod 600 ~/.ssh/config
```

测试：

``` bash
ssh lab-novelty
```

能进入服务器就说明配置完成。

退出：

``` bash
exit
```

以后统一使用
`lab-novelty`，不需要在日常命令、脚本和项目配置中重复填写服务器真实地址。

------------------------------------------------------------------------

# 二、每次使用模型

## 第 1 步：确认服务器模型已经启动

登录服务器：

``` bash
ssh lab-novelty
```

执行：

``` bash
cd ~/llm-service
./status.sh
```

### 如果模型已经运行

看到类似：

``` text
RUNNING: novelty-llm
API OK
```

直接：

``` bash
exit
```

进入第 2 步。

### 如果模型没有运行

先执行：

``` bash
nvidia-smi
```

**确认目标 GPU 当前没有其他人的任务。**

然后：

``` bash
cd ~/llm-service
./start.sh
```

等待约 30～60 秒。

检查：

``` bash
./status.sh
```

直到出现：

``` text
API OK
```

然后：

``` bash
exit
```

## 第 2 步：在自己电脑上建立连接

在本地 WSL：

``` bash
ssh -N \
  -L 8000:127.0.0.1:8000 \
  -o ExitOnForwardFailure=yes \
  lab-novelty
```

运行以后终端会停在那里。

**这是正常的，不要关闭这个窗口。**

这个窗口就是连接服务器模型的 SSH Tunnel。

## 第 3 步：测试连接

重新打开一个 WSL 窗口。

执行：

``` bash
curl http://127.0.0.1:8000/v1/models
```

如果输出中出现：

``` text
qwen2.5-7b-instruct
```

说明连接成功。

现在：

``` text
你电脑的 localhost:8000
```

就是实验室服务器上的 LLM API。

## 第 4 步：让 Novelty 使用服务器模型

进入你本地的 Novelty 项目：

``` bash
cd <你的 Novelty-Multi-Agent-Framework 路径>
```

切换到包含本地模型配置的版本：

``` bash
git switch experiment/local-llm-baseline
```

设置：

``` bash
export LOCAL_VLLM_API_KEY=local
```

当前分支的默认配置会让 PointExtractor、Coordinator、SearchPlanner、
Researcher 和 Reviewer 使用实验室服务器上的 Qwen2.5-7B。

如果需要临时覆盖某个 Agent 的模型，可使用对应的
`NOVELTY_<ROLE>_MODEL` 环境变量，例如：

``` bash
export NOVELTY_SEARCH_PLANNER_MODEL=local-qwen2.5-7b
```

不需要修改 Python 代码。

------------------------------------------------------------------------

# 三、快速检查

如果你只想确认"现在到底能不能用"，依次执行：

## 服务器

``` bash
ssh lab-novelty
cd ~/llm-service
./status.sh
```

应该看到：

``` text
RUNNING: novelty-llm
API OK
```

## 本地

SSH Tunnel 保持运行：

``` bash
ssh -N \
  -L 8000:127.0.0.1:8000 \
  -o ExitOnForwardFailure=yes \
  lab-novelty
```

另开终端：

``` bash
curl http://127.0.0.1:8000/v1/models
```

能看到：

``` text
qwen2.5-7b-instruct
```

就能用。

------------------------------------------------------------------------

# 四、不用了怎么办

## 只是不想继续在自己电脑上使用

到运行 SSH Tunnel 的窗口按：

``` text
Ctrl+C
```

这只会断开你电脑和服务器之间的连接，**不会停止服务器上的模型**。

即：

``` text
SSH Tunnel 生命周期 ≠ LLM Service 生命周期
```

## 确认整个组现在都不用模型，需要释放 GPU

登录服务器：

``` bash
ssh lab-novelty
```

执行：

``` bash
cd ~/llm-service
./stop.sh
```

然后：

``` bash
nvidia-smi
```

确认显存已经释放。

------------------------------------------------------------------------

# 五、最常用的命令

服务器模型状态：

``` bash
cd ~/llm-service
./status.sh
```

启动：

``` bash
./start.sh
```

停止：

``` bash
./stop.sh
```

查看 GPU：

``` bash
nvidia-smi
```

查看模型日志：

``` bash
tmux capture-pane -pt novelty-llm | tail -50
```

本地建立连接：

``` bash
ssh -N \
  -L 8000:127.0.0.1:8000 \
  -o ExitOnForwardFailure=yes \
  lab-novelty
```

本地检查 API：

``` bash
curl http://127.0.0.1:8000/v1/models
```

Novelty 使用本地模型：

``` bash
export LOCAL_VLLM_API_KEY=local
```

------------------------------------------------------------------------

# 六、出问题先看这里

## 1. `curl localhost:8000` 连接失败

先看运行 SSH Tunnel 的窗口还在不在。

如果不在，重新：

``` bash
ssh -N \
  -L 8000:127.0.0.1:8000 \
  -o ExitOnForwardFailure=yes \
  lab-novelty
```

如果仍然失败，登录服务器：

``` bash
ssh lab-novelty
cd ~/llm-service
./status.sh
```

## 2. `API NOT READY`

查看模型日志：

``` bash
tmux capture-pane -pt novelty-llm | tail -50
```

再检查 GPU：

``` bash
nvidia-smi
```

## 3. `novelty-llm` 不存在

模型没有启动。

先：

``` bash
nvidia-smi
```

确认 GPU 可以使用。

然后：

``` bash
cd ~/llm-service
./start.sh
```

## 4. 本地 8000 端口被占用

可以临时使用：

``` bash
ssh -N \
  -L 18000:127.0.0.1:8000 \
  -o ExitOnForwardFailure=yes \
  lab-novelty
```

此时本地地址变成：

``` text
http://127.0.0.1:18000/v1
```

当前项目默认 profile 使用 8000，因此最好优先释放本地 8000
端口，而不是长期改端口。

------------------------------------------------------------------------

# 七、共享服务器使用规则

这是共享 GPU 服务器。

启动模型前必须：

``` bash
nvidia-smi
```

不要：

-   杀掉不认识的进程；
-   抢占其他人的 GPU；
-   修改 NVIDIA Driver；
-   修改系统 CUDA；
-   修改其他人的 Conda 环境；
-   把服务器信息提交到 GitHub；
-   把服务器端口直接开放到公网；
-   长期占用 GPU 却不运行实验。

不确定资源是否可以使用时，先问组内成员。

------------------------------------------------------------------------

# 八、维护者：当前部署

普通使用者不需要阅读这一节。

当前服务器部署：

  项目             当前配置
  ---------------- ---------------------
  Model            Qwen2.5-7B-Instruct
  Precision        BF16
  GPU              单张 RTX 3090 24GB
  vLLM             0.8.5.post1
  PyTorch          2.6.0+cu124
  Transformers     4.51.3
  Context Length   32768
  API              OpenAI-compatible
  Port             8000
  Bind             127.0.0.1

模型磁盘大小约 15 GB。

运行时 GPU 显存占用约 21 GB。

约 21 GB 的显存占用不代表模型权重本身需要 21 GB。显存还包括 KV
Cache、CUDA/vLLM Runtime 和 Workspace。

服务器没有直接向外暴露 8000 端口。开发者通过 SSH Tunnel 访问。

------------------------------------------------------------------------

# 九、环境隔离

服务器使用两个独立 Conda 环境。

## `novelty-llm`

负责模型 Serving：

-   PyTorch
-   CUDA Runtime
-   Transformers
-   vLLM

不要随意安装 Novelty Framework 的应用依赖。

## `novelty-app`

负责服务器侧：

-   Novelty Framework
-   LangGraph
-   Pydantic
-   测试
-   集成验证

两边通过 HTTP 通信：

``` text
novelty-app
    ↓
localhost:8000
    ↓
novelty-llm / vLLM
```

这样应用依赖升级不会轻易破坏已经验证稳定的模型 Serving 环境。

------------------------------------------------------------------------

# 十、已知部署问题

## Hugging Face 无法稳定访问

当前服务器已验证：

``` text
Hugging Face direct connection → 不稳定 / 可能超时
ModelScope → 可用
```

模型权重优先通过 ModelScope 获取。

## pip 下载速度慢

优先使用 NJU PyPI Mirror：

``` bash
python -m pip install <PACKAGE> \
  -i https://mirrors.nju.edu.cn/pypi/web/simple
```

## vLLM 出现 Qwen2Tokenizer 属性错误

曾遇到：

``` text
AttributeError:
Qwen2Tokenizer has no attribute all_special_tokens_extended
```

原因是当前 vLLM 0.8.5 与 Transformers 5.x 存在运行时 API 不兼容。

当前验证版本：

``` text
Transformers 4.51.3
```

不要在 `novelty-llm` 环境中随意升级 Transformers。

------------------------------------------------------------------------

# 十一、为什么 Novelty 不需要特殊修改

Novelty 当前调用结构：

``` text
Agent
 ↓
ModelRegistry
 ↓
OpenAICompatibleChatClient
 ↓
Model API
```

本地模型只是一个普通模型配置：

``` text
local-qwen2.5-7b
```

因此商业 API 和实验室 vLLM 对 Agent 来说没有本质区别。

不要在 SearchPlanner、Researcher、Reviewer、Coordinator 等 Agent
内加入针对本地模型的特殊判断。

------------------------------------------------------------------------

# 十二、当前验证范围

已经实际验证：

``` text
服务器加载 Qwen2.5-7B                 ✓
vLLM API                              ✓
OpenAI-compatible Chat Completion     ✓
JSON 输出                             ✓
服务器 SearchPlanner                  ✓
SSH Tunnel                            ✓
本地 PC 调用服务器模型                ✓
本地 SearchPlanner                    ✓
Researcher Tool Calling               ✓
Reviewer                              ✓
Coordinator                           ✓
完整 Novelty Workflow                ✓
```

目前还没有完成的验证：

``` text
多模型 Benchmark
多人并发
正式生产部署
```

所以当前服务用于：

> **项目开发、调试和实验。**

不是正式生产服务。
