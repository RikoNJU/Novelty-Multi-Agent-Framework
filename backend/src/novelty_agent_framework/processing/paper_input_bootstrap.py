"""Prepare a run-scoped subject-reference snapshot for PaperInput workflows."""

from __future__ import annotations

import asyncio
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ..persistence import (
    SubjectReferenceStore,
    persist_workflow_input,
    subject_reference_workspace,
)
from ..schemas import PaperInput, ReferenceBootstrapManifest
from ..schemas import ReferenceBootstrapEntry, ResolutionStatus
from ..tools.database_search.providers.arxiv import build_arxiv_search_tool
from ..tools.database_search.structured_retrieval import (
    StructuredRetrievalAdapter,
)
from .reference_bootstrap import (
    CitationParser,
    ReferenceBootstrapService,
    ReferenceProviderRegistry,
    references_digest,
)


class PaperInputReferenceBootstrapError(RuntimeError):
    """The PaperInput pipeline cannot safely use its subject-reference pool."""


def prepare_paper_input_references(
    paper: PaperInput,
    *,
    stable_output_root: str | Path,
    run_output_root: str | Path,
    force: bool = False,
    max_concurrency: int = 4,
    service: ReferenceBootstrapService | None = None,
    defer_resolution: bool = False,
    arxiv_options: Mapping[str, Any] | None = None,
) -> ReferenceBootstrapManifest:
    """Validate/refresh the stable cache and snapshot it into one isolated run.

    ``defer_resolution=True`` 时只做本地解析（不触网），每个条目记为 SKIPPED，
    联网解析交给工作流在产生查新点后按点挑选。
    """

    stable_root = Path(stable_output_root)
    run_root = Path(run_output_root)
    persist_workflow_input(paper, output_root=run_root)
    if defer_resolution:
        manifest = _parsed_only_manifest(paper)
        SubjectReferenceStore(run_root).persist_bootstrap(
            paper.paper_id, manifest
        )
        return manifest

    stable_store = SubjectReferenceStore(stable_root)
    cached = _load_valid_cache(stable_store, paper)

    if force or cached is None:
        bootstrap = service or ReferenceBootstrapService(
            ReferenceProviderRegistry([build_arxiv_search_tool(arxiv_options)]),
            stable_store,
            max_concurrency=max_concurrency,
        )
        try:
            cached = asyncio.run(
                bootstrap.bootstrap(
                    paper.paper_id,
                    paper.references,
                    force=True,
                )
            )
        except Exception as exc:
            raise PaperInputReferenceBootstrapError(
                f"subject-reference bootstrap failed: {type(exc).__name__}: {exc}"
            ) from exc

    if not _manifest_matches(cached, paper):
        raise PaperInputReferenceBootstrapError(
            "subject-reference bootstrap is not ready for current PaperInput"
        )

    source = subject_reference_workspace(paper, output_root=stable_root)
    destination = subject_reference_workspace(paper, output_root=run_root)
    shutil.copytree(source, destination, dirs_exist_ok=True)
    snapshot = _load_valid_cache(SubjectReferenceStore(run_root), paper)
    if snapshot is None:
        raise PaperInputReferenceBootstrapError(
            "run-scoped subject-reference snapshot failed validation"
        )
    return snapshot


def _parsed_only_manifest(paper: PaperInput) -> ReferenceBootstrapManifest:
    """构造只含本地解析结果的台账：零网络请求，条目状态为 SKIPPED。

    ``bootstrap_ready`` 对 SKIPPED 条目视为已就绪，因此返回的台账可直接快照到
    运行目录；真正联网解析由工作流根据查新点挑选后进行。
    """

    parser = CitationParser()
    adapter = StructuredRetrievalAdapter()
    entries: list[ReferenceBootstrapEntry] = []
    for ordinal, raw in enumerate(paper.references, 1):
        if not raw.strip():
            continue
        entries.append(
            ReferenceBootstrapEntry(
                reference_id=adapter.stable_id(
                    "ref", paper.paper_id, str(ordinal), raw
                ),
                ordinal=ordinal,
                raw_reference=raw,
                parsed=parser.parse(raw),
                resolution_status=ResolutionStatus.SKIPPED,
                attempts=[],
            )
        )
    return ReferenceBootstrapManifest(
        subject_paper_id=paper.paper_id,
        references_digest=references_digest(paper.references),
        entries=entries,
    )


def _load_valid_cache(
    store: SubjectReferenceStore, paper: PaperInput
) -> ReferenceBootstrapManifest | None:
    try:
        manifest = store.load_bootstrap(paper.paper_id)
    except (OSError, ValueError, ValidationError):
        return None
    return manifest if _manifest_matches(manifest, paper) else None


def _manifest_matches(
    manifest: ReferenceBootstrapManifest, paper: PaperInput
) -> bool:
    return (
        manifest.subject_paper_id == paper.paper_id
        and manifest.references_digest == references_digest(paper.references)
        and len(manifest.entries) == len(paper.references)
        and manifest.bootstrap_ready
    )
