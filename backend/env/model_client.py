"""统一模型调用入口。

该模块只负责模型运行配置和通用调用协议，不放具体查新业务逻辑。
"""

from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.request
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol


class ModelClientError(RuntimeError):
    """模型客户端调用失败。"""


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ModelCallOptions:
    temperature: float | None = None
    max_tokens: int | None = None
    timeout_seconds: float | None = None
    response_format: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class ModelResponse:
    content: str
    raw: Mapping[str, Any] = field(default_factory=dict)
    usage: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ModelRuntimeConfig:
    provider: str = "openai_compatible"
    model: str = "gpt-4.1-mini"
    base_url: str = "https://api.openai.com/v1"
    api_key: str | None = None
    default_temperature: float = 0.2
    default_timeout_seconds: float = 60.0

    @classmethod
    def from_env(cls, prefix: str = "NOVELTY") -> "ModelRuntimeConfig":
        """从项目专属环境变量读取配置，并回退到通用 LLM_* 配置。"""

        def read(name: str, default: str | None = None) -> str | None:
            return os.getenv(f"{prefix}_{name}") or os.getenv(f"LLM_{name}") or default

        temperature = read("TEMPERATURE")
        timeout = read("TIMEOUT_SECONDS")
        return cls(
            provider=read("PROVIDER", cls.provider) or cls.provider,
            model=read("MODEL", cls.model) or cls.model,
            base_url=read("BASE_URL", cls.base_url) or cls.base_url,
            api_key=read("API_KEY"),
            default_temperature=(
                float(temperature) if temperature else cls.default_temperature
            ),
            default_timeout_seconds=(
                float(timeout) if timeout else cls.default_timeout_seconds
            ),
        )


class ModelClient(Protocol):
    def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        options: ModelCallOptions | None = None,
    ) -> ModelResponse:
        ...

    async def acomplete(
        self,
        messages: Sequence[ChatMessage],
        *,
        options: ModelCallOptions | None = None,
    ) -> ModelResponse:
        ...


class OpenAICompatibleChatClient:
    """兼容 OpenAI chat completions 格式的模型客户端。"""

    def __init__(self, config: ModelRuntimeConfig) -> None:
        self.config = config

    def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        options: ModelCallOptions | None = None,
    ) -> ModelResponse:
        if not self.config.api_key:
            raise ModelClientError("缺少模型 API Key，请配置 NOVELTY_API_KEY 或 LLM_API_KEY")

        call_options = options or ModelCallOptions()
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            "temperature": (
                call_options.temperature
                if call_options.temperature is not None
                else self.config.default_temperature
            ),
        }
        if call_options.max_tokens is not None:
            payload["max_tokens"] = call_options.max_tokens
        if call_options.response_format is not None:
            payload["response_format"] = dict(call_options.response_format)

        endpoint = f"{self.config.base_url.rstrip('/')}/chat/completions"
        timeout = (
            call_options.timeout_seconds
            if call_options.timeout_seconds is not None
            else self.config.default_timeout_seconds
        )
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ModelClientError(f"模型 HTTP 调用失败: {exc.code} {detail}") from exc
        except OSError as exc:
            raise ModelClientError(f"模型网络调用失败: {exc}") from exc

        try:
            content = raw["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelClientError(f"模型返回格式不符合 chat completions: {raw}") from exc

        return ModelResponse(
            content=content,
            raw=raw,
            usage=raw.get("usage", {}),
        )

    async def acomplete(
        self,
        messages: Sequence[ChatMessage],
        *,
        options: ModelCallOptions | None = None,
    ) -> ModelResponse:
        return await asyncio.to_thread(self.complete, messages, options=options)


def build_model_client(
    config: ModelRuntimeConfig | None = None,
    *,
    prefix: str = "NOVELTY",
) -> ModelClient:
    runtime_config = config or ModelRuntimeConfig.from_env(prefix)
    if runtime_config.provider != "openai_compatible":
        raise ModelClientError(f"暂不支持模型供应商: {runtime_config.provider}")
    return OpenAICompatibleChatClient(runtime_config)
