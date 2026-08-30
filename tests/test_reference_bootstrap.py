from __future__ import annotations

import asyncio

from novelty_agent_framework.persistence import ReferenceStore, SubjectReferenceStore
from novelty_agent_framework.ports import SearchHit
from novelty_agent_framework.processing.reference_bootstrap import CitationMatcher, CitationParser, ReferenceBootstrapService, ReferenceProviderRegistry
from novelty_agent_framework.schemas import ArtifactNamespace, ParsedCitation, ReferenceNamespace, ReferenceSearchArguments, ResolutionStatus
from novelty_agent_framework.tools import ReferenceSearchTool


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
