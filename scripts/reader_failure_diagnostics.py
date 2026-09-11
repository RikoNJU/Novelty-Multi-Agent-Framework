#!/usr/bin/env python3
"""只读诊断：解释一次运行里 reader 为什么读不出正文。

针对 ``unknown artifact_id`` 这一类失败，脚本按下列判据归因：

``WRONG_NAMESPACE``
    记录来自**旧契约**（``ReaderArguments`` 曾暴露 ``namespace``），id 存在于
    另一个命名空间的 manifest 里 —— 也就是调用方选错了命名空间。新契约下
    ``ReaderArguments`` 不再暴露 ``namespace``，工具会按制品归属自动判定，
    因此新记录的未知 id 只会被归为下面两类（若仍出现 ``WRONG_NAMESPACE``
    说明自动判定契约被破坏了）。
``LOST_MANIFEST_ENTRY``
    id 不在任何 manifest 里，但磁盘上确实存在对应正文文件 —— 典型的
    manifest 并发「读-改-写」丢更新：文件与 id 都产生了，登记被覆盖。
``NEVER_PERSISTED``
    id 既不在 manifest、磁盘上也没有文件 —— 该 id 从未落盘，或由模型臆造。

其它错误（sha256 不匹配、media_type 不可读、UTF-8 解码失败、字节区间越界等）
归入 ``OTHER``。

脚本只读，不写入任何文件，也不输出正文或引文。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "src"))

RESEARCH = "research_reference"
SUBJECT = "subject_reference"

_NAMESPACE_DIRS = {RESEARCH: "references", SUBJECT: "subject_references"}


def _load_json(path: Path, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.name}: {type(exc).__name__}: {exc}")
        return None


def _artifact_ids(manifest: dict[str, Any] | None) -> set[str]:
    if not manifest:
        return set()
    return {
        str(item.get("artifact_id"))
        for item in manifest.get("artifacts", [])
        if item.get("artifact_id")
    }


def _document_ids(workspace: Path, namespace_dir: str) -> set[str]:
    stem_dir = workspace / namespace_dir / "documents"
    return {path.stem for path in stem_dir.glob("*/*.txt")}


def _reader_calls(run_dir: Path, errors: list[str]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for path in sorted((run_dir / "tools").glob("*.json")):
        record = _load_json(path, errors)
        if not isinstance(record, dict) or record.get("tool_name") != "reader":
            continue
        arguments = record.get("resolved_arguments") or record.get("agent_arguments") or {}
        error = record.get("error")
        calls.append(
            {
                "run_id": run_dir.name,
                "tool_call_id": record.get("tool_call_id"),
                "stage_name": record.get("stage_name"),
                "execution_status": record.get("execution_status"),
                "namespace": arguments.get("namespace"),
                "artifact_id": arguments.get("artifact_id"),
                "char_start": arguments.get("char_start"),
                "max_chars": arguments.get("max_chars"),
                "error_type": (error or {}).get("type") if isinstance(error, dict) else None,
                "error_message": (error or {}).get("message") if isinstance(error, dict) else None,
            }
        )
    return calls


def _classify(
    call: dict[str, Any],
    *,
    manifests: dict[str, set[str]],
    documents: dict[str, set[str]],
) -> str:
    message = call.get("error_message") or ""
    if "unknown artifact_id" not in message:
        return "OTHER" if call.get("execution_status") == "FAILED" else "SUCCEEDED"
    artifact_id = call.get("artifact_id")
    namespace = call.get("namespace")
    if namespace is None:
        # 新契约：ReaderArguments 不再暴露 namespace，工具会同时搜索两个语料，
        # 因此「选错命名空间」已不可能发生；未知 id 只可能是没登记或从未落盘。
        if any(artifact_id in ids for ids in manifests.values()):
            # 制品在某个 Manifest 里却仍报未知 id —— 契约被破坏，值得单独标记
            return "WRONG_NAMESPACE"
        if any(artifact_id in ids for ids in documents.values()):
            return "LOST_MANIFEST_ENTRY"
        return "NEVER_PERSISTED"
    # 旧契约（记录里带 namespace）：按请求的命名空间与实际归属对比
    other = SUBJECT if namespace == RESEARCH else RESEARCH
    if artifact_id in manifests.get(other, set()):
        return "WRONG_NAMESPACE"
    if artifact_id in documents.get(namespace, set()) or artifact_id in documents.get(other, set()):
        return "LOST_MANIFEST_ENTRY"
    return "NEVER_PERSISTED"


def inspect_workspace(workspace: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    manifests = {
        namespace: _artifact_ids(_load_json(workspace / directory / "list.json", errors))
        for namespace, directory in _NAMESPACE_DIRS.items()
    }
    documents = {
        namespace: _document_ids(workspace, directory)
        for namespace, directory in _NAMESPACE_DIRS.items()
    }

    runtime_root = workspace / "runtime"
    run_dirs = sorted(path for path in runtime_root.glob("*") if path.is_dir())
    if not run_dirs:
        warnings.append(
            "no runtime runs found; enable runtime_debug to record reader tool calls"
        )

    calls: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        calls.extend(_reader_calls(run_dir, errors))

    for call in calls:
        call["classification"] = _classify(
            call, manifests=manifests, documents=documents
        )

    counts: dict[str, int] = {}
    for call in calls:
        key = call["classification"]
        counts[key] = counts.get(key, 0) + 1

    failures = [call for call in calls if call["classification"] not in {"SUCCEEDED"}]
    verdict = _verdict(counts)

    return {
        "workspace": str(workspace),
        "ok": not errors,
        "counts": {
            "runtime_runs": len(run_dirs),
            "reader_calls": len(calls),
            "reader_failures": len(failures),
            "research_artifacts": len(manifests[RESEARCH]),
            "subject_artifacts": len(manifests[SUBJECT]),
            "research_documents_on_disk": len(documents[RESEARCH]),
            "subject_documents_on_disk": len(documents[SUBJECT]),
        },
        "classification_counts": counts,
        "verdict": verdict,
        "failures": failures,
        "errors": errors,
        "warnings": warnings,
    }


def _verdict(counts: dict[str, int]) -> str:
    if counts.get("LOST_MANIFEST_ENTRY"):
        return (
            "manifest 并发丢更新：制品文件与 id 都已产生，但登记被其它并发任务的"
            "整份覆盖抹掉（候选 A）"
        )
    if counts.get("WRONG_NAMESPACE"):
        return (
            "命名空间选错：id 实际存在于另一个 namespace，调用方按错误的 namespace"
            "去读（候选 B）"
        )
    if counts.get("NEVER_PERSISTED"):
        return "存在从未落盘的 artifact_id：id 可能是臆造的，或写文件阶段就失败了"
    if counts.get("OTHER"):
        return "存在非命名空间类读取失败，请查看 failures 中的 error_message"
    return "未发现读取失败"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path, help="outputs/<paper_id> 目录")
    parser.add_argument("--compact", action="store_true", help="输出单行 JSON")
    args = parser.parse_args()

    report = inspect_workspace(args.workspace)
    print(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=None if args.compact else 2,
            sort_keys=True,
        )
    )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
