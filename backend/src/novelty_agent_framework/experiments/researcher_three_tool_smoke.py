"""Live native tool-calling smoke for WebSearch -> Browser -> Reader."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from backend.env import ChatMessage, ModelCallOptions, ModelClient, ModelResponse
from backend.env.model_client import _load_dev_env

from ..config.factory import build_model_registry, load_config
from ..core import ToolCallHarness, ToolCallHarnessConfig
from ..persistence import ReferenceStore
from ..schemas import NoveltyPoint, ResearchTask, TaskResearchRequest
from ..tools import (
    BaiduSearchBackend,
    BrowserTool,
    PlaywrightBrowserBackend,
    ReaderTool,
    ReferenceArtifactReaderTool,
    ResearcherToolRegistry,
    WebSearchTool,
)

OUTPUT_DIR = Path("outputs/experiments/researcher-three-tool-smoke")
WORKSPACE = OUTPUT_DIR / "workspace"
SUBJECT_ID = "EXP_RESEARCHER_THREE_TOOL"
SYSTEM_PROMPT = """你是 Researcher 三工具纵向链路测试 Agent。必须严格串行完成：
1. 调用 web_search，query 必须是“Python asyncio 官方文档”，max_results=5；
2. 只根据搜索结果选择 Python 官方文档的 source_record_id，调用 browser；browser 参数只能有 source_record_id，禁止传 URL 或 work_id；
3. 从 browser 返回的 extracted_text Artifact 选择 artifact_id，调用 reader，char_start=0，max_chars=2000；
4. 仅根据 reader 返回的正文回答 asyncio 的用途和两类 API。搜索 snippet 不是正文或证据。
每轮只调用一个工具；未完成前三次调用前不得直接回答。"""
USER_TASK = "请按规定链路查阅 Python asyncio 官方文档，并用实际 Reader 正文简要回答。"


@dataclass
class MeasuredModelClient:
    delegate: ModelClient
    model: str
    calls: list[dict[str, Any]] = field(default_factory=list)

    def complete(self, messages, *, options=None) -> ModelResponse:
        return self.delegate.complete(messages, options=options)

    async def acomplete(
        self,
        messages: Sequence[ChatMessage],
        *,
        options: ModelCallOptions | None = None,
    ) -> ModelResponse:
        started = time.perf_counter()
        response = await self.delegate.acomplete(messages, options=options)
        self.calls.append(
            {
                "turn": len(self.calls) + 1,
                "model": self.model,
                "context_roles": [message.role for message in messages],
                "context": [_message_json(message) for message in messages],
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
                "response_tool_calls": [
                    {
                        "id": call.id,
                        "name": call.name,
                        "arguments": dict(call.arguments),
                    }
                    for call in response.tool_calls
                ],
                "usage": dict(response.usage),
            }
        )
        return response


def _message_json(message: ChatMessage) -> dict[str, Any]:
    return {
        "role": message.role,
        "content": message.content,
        "tool_call_id": message.tool_call_id,
        "tool_calls": [
            {"id": call.id, "name": call.name, "arguments": dict(call.arguments)}
            for call in message.tool_calls
        ],
    }


def _scope() -> TaskResearchRequest:
    return TaskResearchRequest(
        subject_paper_id=SUBJECT_ID,
        run_id="researcher-three-tool-smoke",
        novelty_point=NoveltyPoint(
            point_id="NP-three-tool",
            claim="验证三个工具的句柄链",
            technical_features=["native tool calling", "data plane"],
        ),
        research_task=ResearchTask(
            task_id="TASK-three-tool",
            novelty_point_id="NP-three-tool",
            task_type="three_tool_smoke",
            language="zh",
        ),
    )


def _trace_json(sequence: int, event) -> dict[str, Any]:
    record: dict[str, Any] = {"sequence": sequence, "event_type": event.kind}
    if event.message is not None:
        record["message"] = _message_json(event.message)
    if event.tool_call is not None:
        record["tool_call"] = {
            "id": event.tool_call.id,
            "name": event.tool_call.name,
            "arguments": dict(event.tool_call.arguments),
        }
    if event.observation is not None:
        record["full_observation"] = event.observation.model_dump(mode="json")
    if event.detail is not None:
        record["detail"] = event.detail
    return record


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value).union(*(_all_keys(item) for item in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_all_keys(item) for item in value), set())
    return set()


async def run() -> dict[str, Any]:
    _load_dev_env()
    config = load_config()
    alias = config["agents"]["research"]["model"]
    client = build_model_registry(config).client_for(alias)
    measured = MeasuredModelClient(client, client.profile.model)
    store = ReferenceStore(WORKSPACE)
    registry = ResearcherToolRegistry(
        [
            WebSearchTool(BaiduSearchBackend(), store),
            BrowserTool(PlaywrightBrowserBackend(), store),
            ReaderTool(ReferenceArtifactReaderTool(store)),
        ]
    )
    harness = ToolCallHarness(
        measured,
        registry,
        config=ToolCallHarnessConfig(max_turns=5, max_tool_calls=3),
    )
    started = time.perf_counter()
    result = await harness.run(
        system_prompt=SYSTEM_PROMPT,
        initial_user_message=USER_TASK,
        scope=_scope(),
        options=ModelCallOptions(temperature=0.0, max_tokens=1200, tool_choice="auto"),
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    trace = [_trace_json(index, event) for index, event in enumerate(result.trace, 1)]
    tool_events = [event for event in result.trace if event.kind == "tool_result"]
    tool_names = [event.tool_call.name for event in tool_events]
    projections = {
        event.tool_call.name: event.message.content for event in tool_events
    }
    full = {event.tool_call.name: event.observation for event in tool_events}
    calls_aligned = all(
        event.tool_call.id == event.message.tool_call_id for event in tool_events
    )
    web_projection = projections.get("web_search", "")
    browser_projection = projections.get("browser", "")
    reader_projection = projections.get("reader", "")
    browser_projection_keys = (
        _all_keys(json.loads(browser_projection)) if browser_projection else set()
    )
    browser_args = next(
        (event.tool_call.arguments for event in tool_events if event.tool_call.name == "browser"),
        {},
    )
    reader_args = next(
        (event.tool_call.arguments for event in tool_events if event.tool_call.name == "reader"),
        {},
    )
    browser_full = full.get("browser")
    reader_full = full.get("reader")
    web_full = full.get("web_search")
    manifest = store.load_manifest(SUBJECT_ID)
    browser_result = (
        browser_full.payload["browser_result"] if browser_full is not None else {}
    )
    read_result = reader_full.payload["read_result"] if reader_full is not None else {}
    source_id = browser_result.get("source_record_id")
    work_id = browser_result.get("work_id")
    artifact_id = read_result.get("artifact_id")
    traceable = bool(
        source_id
        and work_id
        and artifact_id
        and any(r.source_record_id == source_id and r.work_id == work_id for r in manifest.source_records)
        and any(w.work_id == work_id for w in manifest.works)
        and any(
            a.artifact_id == artifact_id
            and a.work_id == work_id
            and a.source_record_id == source_id
            for a in manifest.artifacts
        )
        and read_result.get("work_id") == work_id
    )
    final = result.final_content or ""
    grounding_terms = [term for term in ("asyncio", "并发", "高层级", "低层级") if term in read_result.get("text", "") and term in final]
    usages = [call["usage"] for call in measured.calls]
    summary = {
        "status": "success" if tool_names == ["web_search", "browser", "reader"] and traceable else "failed",
        "model_alias": alias,
        "model": measured.model,
        "tool_sequence": tool_names,
        "turns_used": result.turns_used,
        "tool_calls_used": result.tool_calls_used,
        "elapsed_ms": elapsed_ms,
        "browser_arguments": dict(browser_args),
        "reader_arguments": dict(reader_args),
        "browser_only_source_record_id": set(browser_args) == {"source_record_id"},
        "reader_uses_browser_artifact": reader_args.get("artifact_id") == artifact_id,
        "tool_call_ids_aligned": calls_aligned,
        "full_observation_in_trace": bool(
            web_full
            and web_full.payload.get("source_records")
            and browser_full
            and browser_full.payload.get("browser_fetch", {}).get("html")
        ),
        "compact_projection_checks": {
            "websearch_has_no_raw_metadata": "raw_metadata" not in web_projection and "source_records" not in web_projection,
            "browser_has_no_html_or_text": not {
                "browser_fetch",
                "html",
                "text",
            }.intersection(browser_projection_keys),
            "reader_contains_text": bool(json.loads(reader_projection).get("read_result", {}).get("text")) if reader_projection else False,
        },
        "projection_characters": {name: len(content) for name, content in projections.items()},
        "prompt_tokens_per_turn": [usage.get("prompt_tokens") for usage in usages],
        "completion_tokens_per_turn": [usage.get("completion_tokens") for usage in usages],
        "total_tokens": sum(usage.get("total_tokens", 0) for usage in usages),
        "source_record_id": source_id,
        "work_id": work_id,
        "artifact_id": artifact_id,
        "read_id": read_result.get("read_id"),
        "traceable_source_work_artifact_read": traceable,
        "final_grounding_terms": grounding_terms,
        "final_answer_based_on_reader": bool(grounding_terms),
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }
    _write(summary, trace, measured.calls, manifest.model_dump(mode="json"), final)
    return summary


def _write(summary, trace, model_calls, manifest, final) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "trace.jsonl").write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in trace),
        encoding="utf-8",
    )
    for name, payload in (
        ("model_calls.json", model_calls),
        ("result.json", summary),
        ("manifest_snapshot.json", manifest),
    ):
        (OUTPUT_DIR / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    (OUTPUT_DIR / "final.txt").write_text(final + "\n", encoding="utf-8")
    checks = summary["compact_projection_checks"]
    report = f"""# Researcher 三工具真实纵向实验

结论：**{summary['status']}**。原生轨迹为 `{summary['tool_sequence']}`，正式 Researcher Workflow 未迁移。

- 模型：`{summary['model_alias']}` / `{summary['model']}`
- 总耗时：{summary['elapsed_ms']} ms
- 每轮 prompt tokens：{summary['prompt_tokens_per_turn']}
- 每轮 completion tokens：{summary['completion_tokens_per_turn']}
- 总 tokens：{summary['total_tokens']}
- 投影字符数：{summary['projection_characters']}
- Browser 参数仅 source_record_id：{summary['browser_only_source_record_id']}
- Reader 使用 Browser artifact_id：{summary['reader_uses_browser_artifact']}
- 全部 tool_call_id 对齐：{summary['tool_call_ids_aligned']}
- 完整 Observation 保存在 trace：{summary['full_observation_in_trace']}
- WebSearch raw_metadata 未进入上下文：{checks['websearch_has_no_raw_metadata']}
- Browser HTML/text 未进入上下文：{checks['browser_has_no_html_or_text']}
- Reader text 进入上下文：{checks['reader_contains_text']}
- SourceRecord→Work→Artifact→Read 可追踪：{summary['traceable_source_work_artifact_read']}
- 最终回答与 Reader 正文共同关键词：{summary['final_grounding_terms']}

## 数据缺口

这是单次 live smoke，没有同任务的“完整 Observation 直接入上下文”A/B，因此只记录投影字符数和逐轮 token，不宣称严格节省比例。搜索排序、网页内容和模型决策会随外部服务变化；Reader 的正文相关性只以共同关键词作最低限度 smoke 检查，不构成事实正确性评测。Browser v1 尚无登录、反爬、CAPTCHA、代理或多页 session。

## 最终回答

{final}
"""
    (OUTPUT_DIR / "report.md").write_text(report, encoding="utf-8")


def main() -> None:
    summary = asyncio.run(run())
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"outputs: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
