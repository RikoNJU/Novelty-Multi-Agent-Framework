from __future__ import annotations

import asyncio

import pytest

from novelty_agent_framework.persistence import ReferenceStore, SubjectReferenceStore
from novelty_agent_framework.ports import SearchHit
from novelty_agent_framework.processing.paper_input_bootstrap import (
    PaperInputReferenceBootstrapError,
    prepare_paper_input_references,
)
from novelty_agent_framework.processing.reference_bootstrap import CitationMatcher, CitationParser, ReferenceBootstrapService, ReferenceProviderRegistry, references_digest
from novelty_agent_framework.schemas import ArtifactNamespace, ExternalIdentifier, PaperInput, ParsedCitation, ReferenceBootstrapManifest, ReferenceNamespace, ReferenceSearchArguments, ResolutionStatus
from novelty_agent_framework.tools import ReferenceSearchTool
from novelty_agent_framework.tools.database_search.providers.arxiv import ArxivSearchTool


class FakeProvider:
    source_id = "fake"

    def resolve_identifier(self, identifier):
        if identifier.namespace == "doi" and identifier.value == "10.1000/demo":
            return SearchHit(document_id="demo", title="Deterministic Reference Resolution", abstract="A bootstrap method for citation resolution.", authors=("Alice Zhang",), year=2024, doi=identifier.value, source_id="fake")
        return None

    def search_known_item(self, citation, *, limit=5):
        return []


def test_parser_extracts_identifiers():
    parsed = CitationParser().parse('Alice Zhang. "Deterministic Reference Resolution". 2024. doi:10.1000/demo https://example.test/paper')
    assert parsed.doi == "10.1000/demo"
    assert parsed.year == 2024
    assert parsed.url == "https://example.test/paper"


def test_matcher_is_conservative_for_close_candidates():
    citation = ParsedCitation(title="A Study of Widgets", authors=["A Smith"], year=2020)
    hits = [
        SearchHit("1", "A Study of Widget", authors=("A Smith",), year=2020),
        SearchHit("2", "A Study of Widgets", authors=("A Smith",), year=2021),
    ]
    assert CitationMatcher().match(citation, hits).status == ResolutionStatus.AMBIGUOUS


def test_bootstrap_isolated_incremental_and_searchable(tmp_path):
    subject_store = SubjectReferenceStore(tmp_path)
    service = ReferenceBootstrapService(ReferenceProviderRegistry([FakeProvider()]), subject_store)
    raw = ["Alice Zhang. Deterministic Reference Resolution. 2024. doi:10.1000/demo"]
    result = asyncio.run(service.bootstrap("paper-1", raw))
    assert result.bootstrap_ready
    assert result.entries[0].resolution_status == ResolutionStatus.RESOLVED
    assert subject_store.load_manifest("paper-1").works
    assert not ReferenceStore(tmp_path).load_manifest("paper-1").works

    again = asyncio.run(service.bootstrap("paper-1", raw))
    assert again == result
    found = ReferenceSearchTool(subject_store).search("paper-1", ReferenceSearchArguments(query="bootstrap citation"))
    assert found.results
    assert found.results[0].artifact_handles[0].namespace == ArtifactNamespace.SUBJECT_REFERENCE


def test_failed_item_does_not_block_barrier(tmp_path):
    class Broken:
        source_id = "broken"
        def search_known_item(self, citation, *, limit=5):
            raise TimeoutError("offline")

    result = asyncio.run(ReferenceBootstrapService(ReferenceProviderRegistry([Broken()]), SubjectReferenceStore(tmp_path)).bootstrap("paper-2", ["Unparseable citation"] ))
    assert result.bootstrap_ready
    assert result.entries[0].resolution_status == ResolutionStatus.FAILED


def _arxiv_hit(arxiv_id: str) -> SearchHit:
    return SearchHit(
        document_id=arxiv_id,
        title="Attention Is All You Need",
        abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
        authors=("Ashish Vaswani",),
        year=2017,
        url=f"https://arxiv.org/abs/{arxiv_id}",
        source_id="arxiv",
        external_id=f"{arxiv_id}v2",
    )


def test_real_arxiv_provider_exposes_bootstrap_capabilities():
    """回归守卫：CLI 只注册 ArxivSearchTool，它必须提供 bootstrap 依赖的两个能力。

    历史缺陷：合并时这两个方法被丢弃，ReferenceBootstrapService 通过 getattr
    静默跳过缺失能力，把所有引文判为 NOT_FOUND（实测 0/85、0/91），而
    reference_search 永远返回空；测试因为只注入 FakeProvider 而保持全绿。
    因此这里断言的是**真实 provider** 的能力，而不是 fake。
    """

    registry = ReferenceProviderRegistry([ArxivSearchTool()])
    assert [pid for pid, capability in registry.providers() if getattr(capability, "resolve_identifier", None)] == ["arxiv"]
    assert [pid for pid, capability in registry.providers() if getattr(capability, "search_known_item", None)] == ["arxiv"]


def test_arxiv_resolve_identifier_is_exact_and_namespace_scoped(monkeypatch):
    tool = ArxivSearchTool()
    queries: list[str] = []

    def fake_search(query: str, *, limit: int = 10):
        queries.append(query)
        return [_arxiv_hit("1706.03762")]

    monkeypatch.setattr(tool, "search", fake_search)

    hit = tool.resolve_identifier(ExternalIdentifier(namespace="arxiv", value="1706.03762v2"))
    assert hit is not None and hit.document_id == "1706.03762"
    assert queries == ["id:1706.03762"]

    queries.clear()
    assert tool.resolve_identifier(ExternalIdentifier(namespace="doi", value="10.1000/demo")) is None
    assert queries == []


def test_arxiv_search_known_item_prefers_id_then_title(monkeypatch):
    tool = ArxivSearchTool()
    queries: list[str] = []

    def fake_search(query: str, *, limit: int = 10):
        queries.append(query)
        return [_arxiv_hit("1706.03762")]

    monkeypatch.setattr(tool, "search", fake_search)

    by_id = tool.search_known_item(ParsedCitation(title="Attention Is All You Need", arxiv_id="1706.03762"))
    assert [hit.document_id for hit in by_id] == ["1706.03762"]
    assert queries == ["id:1706.03762"]

    queries.clear()
    tool.search_known_item(ParsedCitation(title="Attention Is All You Need"))
    assert queries == ['ti:"Attention Is All You Need"']

    queries.clear()
    tool.search_known_item(ParsedCitation(title='A "quoted" term'))
    assert queries == ['ti:"A \\"quoted\\" term"']

    queries.clear()
    assert tool.search_known_item(ParsedCitation(title=None)) == []
    assert queries == []


def test_real_arxiv_provider_resolves_citation_through_bootstrap_service(tmp_path, monkeypatch):
    """端到端：真实 provider + 真实 service，只替换网络检索层。"""

    tool = ArxivSearchTool()
    monkeypatch.setattr(tool, "search", lambda query, *, limit=10: [_arxiv_hit("1706.03762")])
    service = ReferenceBootstrapService(ReferenceProviderRegistry([tool]), SubjectReferenceStore(tmp_path))

    result = asyncio.run(service.bootstrap("paper-3", ["Vaswani et al. Attention Is All You Need. 2017. arXiv:1706.03762"]))

    assert result.bootstrap_ready
    assert result.entries[0].resolution_status == ResolutionStatus.RESOLVED
    assert result.entries[0].resolved_work_id
    assert SubjectReferenceStore(tmp_path).load_manifest("paper-3").works


def _paper(references=None):
    return PaperInput(
        paper_id="paper-input-run",
        title="Paper",
        full_text="body",
        references=references
        or ["Alice Zhang. Deterministic Reference Resolution. 2024. doi:10.1000/demo"],
    )


def test_paper_input_bootstrap_refreshes_missing_cache_and_snapshots(tmp_path):
    stable_root = tmp_path / "stable"
    run_root = tmp_path / "runs" / "0001"
    paper = _paper()
    service = ReferenceBootstrapService(
        ReferenceProviderRegistry([FakeProvider()]),
        SubjectReferenceStore(stable_root),
    )

    manifest = prepare_paper_input_references(
        paper,
        stable_output_root=stable_root,
        run_output_root=run_root,
        service=service,
    )

    assert manifest.references_digest == references_digest(paper.references)
    assert manifest.bootstrap_ready
    assert (run_root / paper.paper_id / "paper-input" / "others" / "paper.json").is_file()
    assert (run_root / paper.paper_id / "subject_references" / "bootstrap.json").is_file()
    found = ReferenceSearchTool(SubjectReferenceStore(run_root)).search(
        paper.paper_id,
        ReferenceSearchArguments(query="bootstrap citation"),
    )
    assert found.results


def test_ready_cache_is_reused_without_bootstrap_and_snapshot_is_independent(tmp_path):
    stable_root = tmp_path / "stable"
    paper = _paper()
    first_service = ReferenceBootstrapService(
        ReferenceProviderRegistry([FakeProvider()]),
        SubjectReferenceStore(stable_root),
    )
    prepare_paper_input_references(
        paper,
        stable_output_root=stable_root,
        run_output_root=tmp_path / "runs" / "0001",
        service=first_service,
    )

    class MustNotRun:
        async def bootstrap(self, *_args, **_kwargs):
            raise AssertionError("ready cache should be reused")

    run_root = tmp_path / "runs" / "0002"
    prepare_paper_input_references(
        paper,
        stable_output_root=stable_root,
        run_output_root=run_root,
        service=MustNotRun(),
    )
    stable_bootstrap = (
        stable_root / paper.paper_id / "subject_references" / "bootstrap.json"
    )
    stable_bootstrap.write_text("{}", encoding="utf-8")

    assert SubjectReferenceStore(run_root).load_bootstrap(paper.paper_id).bootstrap_ready


def test_reference_digest_mismatch_forces_bootstrap_refresh(tmp_path):
    stable_root = tmp_path / "stable"
    initial = _paper()
    service = ReferenceBootstrapService(
        ReferenceProviderRegistry([FakeProvider()]),
        SubjectReferenceStore(stable_root),
    )
    prepare_paper_input_references(
        initial,
        stable_output_root=stable_root,
        run_output_root=tmp_path / "runs" / "0001",
        service=service,
    )
    changed = _paper(["A different citation without identifiers. 2020."])

    refreshed = prepare_paper_input_references(
        changed,
        stable_output_root=stable_root,
        run_output_root=tmp_path / "runs" / "0002",
        service=service,
    )

    assert refreshed.references_digest == references_digest(changed.references)
    assert refreshed.entries[0].raw_reference == changed.references[0]


def test_force_option_refreshes_an_already_ready_cache(tmp_path):
    stable_root = tmp_path / "stable"
    paper = _paper()
    delegate = ReferenceBootstrapService(
        ReferenceProviderRegistry([FakeProvider()]),
        SubjectReferenceStore(stable_root),
    )
    prepare_paper_input_references(
        paper,
        stable_output_root=stable_root,
        run_output_root=tmp_path / "runs" / "0001",
        service=delegate,
    )

    class RecordingService:
        calls = 0

        async def bootstrap(self, *args, **kwargs):
            self.calls += 1
            assert kwargs["force"] is True
            return await delegate.bootstrap(*args, **kwargs)

    recorder = RecordingService()
    prepare_paper_input_references(
        paper,
        stable_output_root=stable_root,
        run_output_root=tmp_path / "runs" / "0002",
        force=True,
        service=recorder,
    )

    assert recorder.calls == 1


def test_non_ready_bootstrap_fails_paper_input_pipeline(tmp_path):
    paper = _paper()

    class IncompleteService:
        async def bootstrap(self, paper_id, references, **_kwargs):
            return ReferenceBootstrapManifest(
                subject_paper_id=paper_id,
                references_digest=references_digest(references),
            )

    with pytest.raises(PaperInputReferenceBootstrapError, match="not ready"):
        prepare_paper_input_references(
            paper,
            stable_output_root=tmp_path / "stable",
            run_output_root=tmp_path / "runs" / "0001",
            service=IncompleteService(),
        )
