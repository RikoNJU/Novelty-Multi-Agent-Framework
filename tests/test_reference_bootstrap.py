from __future__ import annotations

import asyncio
import threading

import pytest

from novelty_agent_framework.persistence import ReferenceStore, SubjectReferenceStore
from novelty_agent_framework.ports import SearchHit
from novelty_agent_framework.processing.paper_input_bootstrap import (
    PaperInputReferenceBootstrapError,
    prepare_paper_input_references,
)
from novelty_agent_framework.processing.reference_bootstrap import (
    CitationMatcher,
    CitationParser,
    ReferenceBootstrapService,
    ReferenceProviderRegistry,
    ReferenceTarget,
    references_digest,
    select_reference_ordinals,
)
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


GB_T_REFERENCES = [
    "[1] ABDI H, WILLIAMS L J. Principal component analysis[J]. Wiley interdisciplinary reviews: computational statistics, 2010, 2(4) : 433 - 459",
    "[2] HAMILTON W, YING Z. Inductive representation learning on large graphs[C] // NIPS. 2017",
    "[3] ZENG H, ZHOU H. Graphsaint: Graph sampling based inductive learning method[J]. arXiv preprint arXiv:1907.04931, 2019.",
    "[4] 张三, 李四. 大规模时序图表示学习[J]. 计算机学报, 2021, 44(3): 1-15",
]


def test_parser_extracts_identifiers():
    parsed = CitationParser().parse(
        'Alice Zhang. "Deterministic Reference Resolution". 2024. '
        "doi:10.1000/demo https://example.test/paper"
    )
    assert parsed.doi == "10.1000/demo"
    assert parsed.year == 2024
    assert parsed.url == "https://example.test/paper"


def test_parser_reads_gbt7714_reference_fields() -> None:
    parser = CitationParser()
    journal, conference, preprint, _chinese = [
        parser.parse(raw) for raw in GB_T_REFERENCES
    ]

    assert journal.title == "Principal component analysis"
    assert journal.authors == ["ABDI H", "WILLIAMS L J"]
    assert journal.year == 2010
    assert conference.title == "Inductive representation learning on large graphs"
    assert conference.authors == ["HAMILTON W", "YING Z"]
    assert preprint.arxiv_id == "1907.04931"


def test_parser_prefers_publication_year_over_arxiv_id_digits() -> None:
    """arXiv ID ``1907.04931`` 里的 1907 不得被当成出版年。"""

    citation = CitationParser().parse(GB_T_REFERENCES[2])

    assert citation.year == 2019


def test_selector_picks_lexically_related_references() -> None:
    target = ReferenceTarget(
        target_id="NP-1",
        text="inductive representation learning on large graphs",
    )

    assert select_reference_ordinals(
        GB_T_REFERENCES, [target], per_target_limit=1
    ) == [2]


def test_selector_falls_back_to_all_without_targets_or_limit() -> None:
    target = ReferenceTarget(target_id="NP-1", text="graph")

    assert select_reference_ordinals(
        GB_T_REFERENCES, [], per_target_limit=2
    ) == [1, 2, 3, 4]
    assert select_reference_ordinals(
        GB_T_REFERENCES, [target], per_target_limit=0
    ) == [1, 2, 3, 4]


def test_bootstrap_with_targets_only_resolves_selected_references(tmp_path) -> None:
    """预筛命中的才联网解析，其余标为 SKIPPED 且不重复请求。"""

    class CountingProvider:
        source_id = "arxiv"

        def __init__(self) -> None:
            self.calls = 0

        def resolve_identifier(self, identifier):
            self.calls += 1
            return None

        def search_known_item(self, citation, *, limit=5):
            self.calls += 1
            return []

    provider = CountingProvider()
    service = ReferenceBootstrapService(
        ReferenceProviderRegistry([provider]), SubjectReferenceStore(tmp_path)
    )
    target = ReferenceTarget(
        target_id="NP-1",
        text="inductive representation learning on large graphs",
    )

    result = asyncio.run(
        service.bootstrap(
            "paper-filter",
            GB_T_REFERENCES,
            targets=[target],
            per_target_limit=1,
        )
    )

    statuses = {entry.ordinal: entry.resolution_status for entry in result.entries}
    assert provider.calls == 1
    assert statuses[2] != ResolutionStatus.SKIPPED
    assert statuses[1] == ResolutionStatus.SKIPPED
    assert statuses[3] == ResolutionStatus.SKIPPED
    assert statuses[4] == ResolutionStatus.SKIPPED
    assert result.bootstrap_ready

    provider.calls = 0
    again = asyncio.run(
        service.bootstrap(
            "paper-filter",
            GB_T_REFERENCES,
            targets=[target],
            per_target_limit=1,
        )
    )
    assert provider.calls == 0
    assert [entry.ordinal for entry in again.entries] == [1, 2, 3, 4]


def test_defer_resolution_writes_parsed_only_manifest(tmp_path) -> None:
    """defer 模式只做本地解析，不触网，台账依然 ready。"""

    paper = PaperInput(
        paper_id="paper-defer",
        title="Paper",
        full_text="body",
        references=GB_T_REFERENCES,
    )
    run_root = tmp_path / "runs" / "0001"

    manifest = prepare_paper_input_references(
        paper,
        stable_output_root=tmp_path / "stable",
        run_output_root=run_root,
        defer_resolution=True,
    )

    assert manifest.bootstrap_ready
    assert [entry.resolution_status for entry in manifest.entries] == [
        ResolutionStatus.SKIPPED
    ] * len(GB_T_REFERENCES)
    assert manifest.entries[0].parsed.title == "Principal component analysis"
    persisted = SubjectReferenceStore(run_root).load_bootstrap("paper-defer")
    assert len(persisted.entries) == len(GB_T_REFERENCES)
    # 稳定缓存不被写入：defer 模式不产生跨运行的副作用
    assert SubjectReferenceStore(tmp_path / "stable").load_bootstrap(
        "paper-defer"
    ).entries == []


def test_workflow_reference_node_is_noop_without_manifest(tmp_path) -> None:
    from novelty_agent_framework.schemas import NoveltyPoint
    from novelty_agent_framework.workflows import NoveltyWorkflow

    workflow = NoveltyWorkflow.default()
    workflow.output_root = tmp_path / "outputs"
    state = {
        "paper": PaperInput(
            paper_id="paper-none",
            title="Paper",
            full_text="body",
            references=GB_T_REFERENCES,
        ),
        "novelty_points": [NoveltyPoint(point_id="NP-1", claim="claim")],
    }

    assert asyncio.run(workflow._resolve_subject_references(state)) == {}
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


def test_sync_identifier_provider_does_not_block_bootstrap_event_loop(tmp_path):
    provider_threads: list[int] = []
    release = threading.Event()
    released_by_event_loop = False

    class BlockingProvider:
        source_id = "blocking"

        def resolve_identifier(self, identifier):
            provider_threads.append(threading.get_ident())
            nonlocal released_by_event_loop
            released_by_event_loop = release.wait(timeout=0.5)
            return _arxiv_hit(identifier.value)

    service = ReferenceBootstrapService(
        ReferenceProviderRegistry([BlockingProvider()]),
        SubjectReferenceStore(tmp_path),
    )

    async def run() -> int:
        event_loop_thread = threading.get_ident()
        task = asyncio.create_task(
            service.bootstrap(
                "paper-async-id",
                ["Vaswani et al. Attention Is All You Need. 2017. arXiv:1706.03762"],
            )
        )
        await asyncio.sleep(0.01)
        release.set()
        result = await task
        assert result.entries[0].resolution_status == ResolutionStatus.RESOLVED
        return event_loop_thread

    event_loop_thread = asyncio.run(run())

    assert released_by_event_loop is True
    assert provider_threads and provider_threads[0] != event_loop_thread


def test_sync_known_item_provider_does_not_block_bootstrap_event_loop(tmp_path):
    provider_threads: list[int] = []
    release = threading.Event()
    released_by_event_loop = False

    class BlockingProvider:
        source_id = "blocking"

        def search_known_item(self, citation, *, limit=5):
            provider_threads.append(threading.get_ident())
            nonlocal released_by_event_loop
            released_by_event_loop = release.wait(timeout=0.5)
            return [
                SearchHit(
                    document_id="1706.03762",
                    title=citation.title or "Attention Is All You Need",
                    year=citation.year,
                    source_id="blocking",
                )
            ]

    service = ReferenceBootstrapService(
        ReferenceProviderRegistry([BlockingProvider()]),
        SubjectReferenceStore(tmp_path),
    )

    async def run() -> int:
        event_loop_thread = threading.get_ident()
        task = asyncio.create_task(
            service.bootstrap(
                "paper-async-title",
                ["Vaswani et al. Attention Is All You Need. 2017."],
            )
        )
        await asyncio.sleep(0.01)
        release.set()
        result = await task
        assert result.entries[0].resolution_status == ResolutionStatus.RESOLVED
        return event_loop_thread

    event_loop_thread = asyncio.run(run())

    assert released_by_event_loop is True
    assert provider_threads and provider_threads[0] != event_loop_thread


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
