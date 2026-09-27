"""Loopback-only production guard probe: one pre-chat rejection, one short chat.

The rejected request is reconstructed unchanged from the archived Reader pair.
The allowed request uses its real Reader schema with a tiny authored instruction.
No tools are executed and no retrieval/provider request is made by this script.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "backend/src")]
from backend.env import (ChatMessage, ContextAdmissionConfig, ModelCallOptions,
    ModelContextAdmissionError, ModelProfile, OpenAICompatibleChatClient, ToolDefinition)
from backend.env.context_admission import payload_fingerprint
from novelty_agent_framework.core import RuntimeArtifactManager, RuntimeDebugConfig

HERE = Path(__file__).resolve().parent
OUT = HERE / "context_guard_local"
# Scope proxy bypass to this short lived loopback probe, after optional .env load.
os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost,::1"


def main():
    if OUT.exists():
        raise SystemExit("Refusing to overwrite previous live guard observations")
    OUT.mkdir()
    source = sorted((HERE / "reader_local_pair_restarted/state_off").glob("MF*/runtime/*/llm_calls/*.json"))[0]
    archived = json.loads(source.read_text())["request_payload"]
    tools = [ToolDefinition(item["function"]["name"], item["function"]["description"], item["function"]["parameters"])
             for item in archived["tools"]]
    config = ContextAdmissionConfig(mode="enforce", counter="vllm", on_unavailable="reject",
        timeout_seconds=8, vllm_tools_mode="v0_8_5_kwargs")
    base = ModelProfile(alias="local-context-guard", model=archived["model"],
        base_url="http://127.0.0.1:8000/v1", api_key="local-placeholder", context_window=32768,
        context_admission=config)
    outcomes = []
    for name in ("reject_archived", "allow_short"):
        if name == "reject_archived":
            selected = replace(base, context_window=100)
            messages = [ChatMessage(item["role"], item.get("content")) for item in archived["messages"]]
            options = ModelCallOptions(max_tokens=archived["max_tokens"], temperature=archived["temperature"],
                tools=tools, tool_choice=archived["tool_choice"], timeout_seconds=30)
        else:
            selected = replace(base, context_window=40000)
            messages = [ChatMessage("system", "This is a token accounting probe. Reply with OK only. Do not invoke any tools."),
                ChatMessage("user", "Confirm by replying OK.")]
            options = ModelCallOptions(max_tokens=32, temperature=0, tools=tools, tool_choice="auto", timeout_seconds=30)
        client = OpenAICompatibleChatClient(selected)
        payload = client._build_payload(messages, options)
        if name == "reject_archived":
            assert payload == archived, "archived request reconstruction is not exact"
        manager = RuntimeArtifactManager("context-admission", run_id=name,
            config=RuntimeDebugConfig(output_root=OUT, archive_root=OUT / "archive", max_model_calls=1),
            runtime_config={"context_admission": asdict(config), "context_window": selected.context_window})
        manager.activate()
        row = {"probe": name, "profile_window": selected.context_window,
            "request_sha256": payload_fingerprint(payload), "fixture": str(source.relative_to(ROOT)) if name == "reject_archived" else "authored_short_instruction_with_archived_reader_schema"}
        status = "FAILED"
        try:
            result = client.complete(messages, options=options)
            row.update(result="chat_completed", content=result.content, provider_usage=dict(result.usage))
            status = "SUCCESS"
        except ModelContextAdmissionError as exc:
            row.update(result="pre_chat_rejected", code=exc.code, admission=exc.admission)
            if name == "reject_archived" and exc.code == "CONTEXT_LIMIT_EXCEEDED":
                status = "SUCCESS"
        except Exception as exc:
            row.update(result="unexpected_failure", error_type=type(exc).__name__, error=str(exc))
        finally:
            manager.finish_run(status)
            manager.deactivate()
        record = json.loads(next((manager.run_dir / "llm_calls").glob("*.json")).read_text())
        row.update(runtime=str(manager.run_dir.relative_to(ROOT)), admission=record.get("context_admission"),
            verification=record.get("context_measurement_verification"),
            chat_transport_invoked=record.get("chat_transport_invoked"),
            context_measurement_requests=record.get("context_measurement_requests"),
            physical_requests_by_kind={kind: sum(event.get("kind") == kind and event["phase"] == "CONTEXT_MEASUREMENT_REQUEST"
                for event in record["timeline"]) for kind in ("schema", "version", "tokenize")})
        outcomes.append(row)
        (OUT / "outcome.json").write_text(json.dumps({"endpoint": base.base_url, "retrieval_calls": 0,
            "tokenize_is_not_chat_usage": True, "outcomes": outcomes}, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"probe": name, "result": row["result"], "chat_transport_invoked": row["chat_transport_invoked"],
            "measurement": row["admission"]["input_tokens"], "verification": row["verification"]}, ensure_ascii=False), flush=True)
    assert outcomes[0]["result"] == "pre_chat_rejected" and not outcomes[0]["chat_transport_invoked"]
    assert outcomes[1]["result"] == "chat_completed" and outcomes[1]["verification"]["status"] == "matched"


if __name__ == "__main__":
    main()
