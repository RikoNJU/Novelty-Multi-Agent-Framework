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
from pathlib import Path
from typing import Any, Protocol


def _load_dev_env() -> None:
    """开发环境可选加载 ``backend/.env``；未安装 python-dotenv 时静默跳过。"""

    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    # override=False：真实环境变量优先于 .env，生产部署不受影响
    load_dotenv(env_path, override=False)


_load_dev_env()


class ModelClientError(RuntimeError):
    """模型客户端调用失败。"""


@dataclass(frozen=True)
class ImageContentPart:
    """多模态消息中的图片片段（OpenAI vision 格式）。"""

    image_url: str
    detail: str = "high"


ContentPart = str | ImageContentPart


@dataclass(frozen=True)
class ToolDefinition:
    """Provider-independent function tool definition."""

    name: str
    description: str
    parameters: Mapping[str, Any]


@dataclass(frozen=True)
class ModelToolCall:
    """A model request to invoke one named tool with JSON-object arguments."""

    id: str
    name: str
    arguments: Mapping[str, Any]


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str | Sequence[ContentPart] | None = None
    tool_calls: Sequence[ModelToolCall] = ()
    tool_call_id: str | None = None


@dataclass(frozen=True)
class ModelCallOptions:
    temperature: float | None = None
    max_tokens: int | None = None
    timeout_seconds: float | None = None
    response_format: Mapping[str, Any] | None = None
    top_p: float | None = None
    stop: Sequence[str] | None = None
    tools: Sequence[ToolDefinition] | None = None
    tool_choice: str | Mapping[str, Any] | None = None
    extra_body: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ModelResponse:
    content: str | None
    tool_calls: Sequence[ModelToolCall] = ()
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


@dataclass(frozen=True)
class ModelProfile:
    """单个模型的完整运行描述，供按角色选择不同模型。

    ``supported_params`` 是允许透传给厂商 API 的参数白名单（例如
    ``enable_thinking``、``thinking_budget``、``reasoning_effort``）。
    ``defaults`` 存放模型级默认参数，优先级低于单次调用选项。
    """

    alias: str
    model: str
    base_url: str = "https://api.openai.com/v1"
    api_key: str | None = None
    provider: str = "openai_compatible"
    context_window: int = 128_000
    supported_params: frozenset[str] = frozenset()
    defaults: Mapping[str, Any] = field(default_factory=dict)


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

    def __init__(self, profile: ModelProfile | ModelRuntimeConfig) -> None:
        if isinstance(profile, ModelRuntimeConfig):
            profile = ModelProfile(
                alias="default",
                provider=profile.provider,
                model=profile.model,
                base_url=profile.base_url,
                api_key=profile.api_key,
                defaults={
                    "temperature": profile.default_temperature,
                    "timeout_seconds": profile.default_timeout_seconds,
                },
            )
        self.profile = profile

    def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        options: ModelCallOptions | None = None,
    ) -> ModelResponse:
        if not self.profile.api_key:
            raise ModelClientError("缺少模型 API Key，请配置 NOVELTY_API_KEY 或 LLM_API_KEY")

        call_options = options or ModelCallOptions()
        payload = self._build_payload(messages, call_options)
        endpoint = f"{self.profile.base_url.rstrip('/')}/chat/completions"
        timeout = call_options.timeout_seconds
        if timeout is None:
            timeout = self.profile.defaults.get("timeout_seconds", 60.0)
        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.profile.api_key}",
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
            message = raw["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelClientError(f"模型返回格式不符合 chat completions: {raw}") from exc
        if not isinstance(message, Mapping):
            raise ModelClientError(f"模型返回格式不符合 chat completions: {raw}")

        content = message.get("content")
        if content is not None and not isinstance(content, str):
            raise ModelClientError("模型返回的 message.content 必须是字符串或 null")
        tool_calls = _parse_tool_calls(message.get("tool_calls"))

        return ModelResponse(
            content=content,
            tool_calls=tool_calls,
            raw=raw,
            usage=raw.get("usage", {}),
        )

    def _build_payload(
        self,
        messages: Sequence[ChatMessage],
        options: ModelCallOptions,
    ) -> dict[str, Any]:
        """按“单次调用 > 模型默认”合并参数，并过滤厂商参数白名单。"""

        profile = self.profile
        defaults = dict(profile.defaults or {})
        payload: dict[str, Any] = {
            "model": profile.model,
            "messages": [_serialize_message(message) for message in messages],
            "temperature": (
                options.temperature
                if options.temperature is not None
                else defaults.get("temperature", 0.7)
            ),
        }
        for key in ("max_tokens", "top_p", "stop"):
            value = getattr(options, key, None)
            if value is None:
                value = defaults.get(key)
            if value is not None:
                payload[key] = value
        if options.response_format is not None:
            payload["response_format"] = dict(options.response_format)
        elif "response_format" in defaults:
            payload["response_format"] = dict(defaults["response_format"])
        if options.tools:
            payload["tools"] = [_serialize_tool_definition(tool) for tool in options.tools]
        if options.tool_choice is not None:
            payload["tool_choice"] = (
                dict(options.tool_choice)
                if isinstance(options.tool_choice, Mapping)
                else options.tool_choice
            )

        for key, value in defaults.items():
            if key in (
                "temperature",
                "max_tokens",
                "top_p",
                "stop",
                "timeout_seconds",
                "response_format",
            ):
                continue
            if key in profile.supported_params and key not in payload:
                payload[key] = value
        for key, value in (options.extra_body or {}).items():
            if key in profile.supported_params:
                payload[key] = value
        return payload

    async def acomplete(
        self,
        messages: Sequence[ChatMessage],
        *,
        options: ModelCallOptions | None = None,
    ) -> ModelResponse:
        return await asyncio.to_thread(self.complete, messages, options=options)


def _serialize_message(message: ChatMessage) -> dict[str, Any]:
    """Serialize normal, assistant tool-call, and tool-result messages."""

    serialized: dict[str, Any] = {
        "role": message.role,
        "content": _serialize_content(message.content),
    }
    if message.tool_calls:
        serialized["tool_calls"] = [
            _serialize_model_tool_call(tool_call) for tool_call in message.tool_calls
        ]
    if message.tool_call_id is not None:
        serialized["tool_call_id"] = message.tool_call_id
    return serialized


def _serialize_content(content: str | Sequence[ContentPart] | None) -> Any:
    """把消息内容序列化为 OpenAI chat completions 的 content 字段。"""

    if content is None or isinstance(content, str):
        return content
    parts: list[dict[str, Any]] = []
    for part in content:
        if isinstance(part, str):
            parts.append({"type": "text", "text": part})
        else:
            parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": part.image_url, "detail": part.detail},
                }
            )
    return parts


def _serialize_tool_definition(tool: ToolDefinition) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": dict(tool.parameters),
        },
    }


def _serialize_model_tool_call(tool_call: ModelToolCall) -> dict[str, Any]:
    return {
        "id": tool_call.id,
        "type": "function",
        "function": {
            "name": tool_call.name,
            "arguments": json.dumps(tool_call.arguments, ensure_ascii=False),
        },
    }


def _parse_tool_calls(value: Any) -> tuple[ModelToolCall, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ModelClientError("模型返回的 message.tool_calls 必须是数组")

    parsed: list[ModelToolCall] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ModelClientError(f"模型返回的 tool_calls[{index}] 必须是对象")
        call_id = item.get("id")
        function = item.get("function")
        if not isinstance(call_id, str) or not call_id:
            raise ModelClientError(f"模型返回的 tool_calls[{index}] 缺少 id")
        if not isinstance(function, Mapping):
            raise ModelClientError(f"模型返回的 tool_calls[{index}] 缺少 function")
        name = function.get("name")
        if not isinstance(name, str) or not name:
            raise ModelClientError(f"模型返回的 tool_calls[{index}] 缺少 function.name")
        raw_arguments = function.get("arguments")
        if not isinstance(raw_arguments, str):
            raise ModelClientError(
                f"模型返回的 tool_calls[{index}].function.arguments 必须是 JSON 字符串"
            )
        try:
            arguments = json.loads(raw_arguments)
        except json.JSONDecodeError as exc:
            raise ModelClientError(
                f"模型返回的 tool_calls[{index}].function.arguments 不是合法 JSON"
            ) from exc
        if not isinstance(arguments, dict):
            raise ModelClientError(
                f"模型返回的 tool_calls[{index}].function.arguments 必须是 JSON object"
            )
        parsed.append(ModelToolCall(id=call_id, name=name, arguments=arguments))
    return tuple(parsed)


class ModelRegistry:
    """按业务别名注册模型 profile，并为每个别名提供独立的 ModelClient。"""

    def __init__(self, profiles: Mapping[str, ModelProfile]) -> None:
        self._profiles = dict(profiles)
        self._clients: dict[str, ModelClient] = {}

    def client_for(self, alias: str) -> ModelClient:
        profile = self._profiles.get(alias)
        if profile is None:
            raise ModelClientError(f"未注册模型别名: {alias}")
        if alias not in self._clients:
            self._clients[alias] = OpenAICompatibleChatClient(profile)
        return self._clients[alias]

    @property
    def aliases(self) -> tuple[str, ...]:
        return tuple(self._profiles)


def build_model_client(
    config: ModelRuntimeConfig | None = None,
    *, 
    prefix: str = "NOVELTY",
) -> ModelClient:
    runtime_config = config or ModelRuntimeConfig.from_env(prefix)
    if runtime_config.provider != "openai_compatible":
        raise ModelClientError(f"暂不支持模型供应商: {runtime_config.provider}")
    return OpenAICompatibleChatClient(runtime_config)
