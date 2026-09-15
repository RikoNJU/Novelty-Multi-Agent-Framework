"""Regression tests for the recorded full-run failures."""
import asyncio
import json

import pytest
from backend.env import ModelResponse
from novelty_agent_framework.schemas import ArtifactNamespace, ReaderArguments, ResearchFinishDraft
from novelty_agent_framework.tools import ReviewerReaderTool, WebSearchTool
from test_novelty_point_reviewer import _request, _reviewer, _review_json, RecordingReader, ScriptedClient
from test_card_recovery import workflow, Reader, call, finish
from test_tool_call_harness import ScriptedModelClient
from test_evidence_card_builder import read, card, quote, scope


class AddressReader(RecordingReader):
    async def ainvoke(self, request):
        result = await super().ainvoke(request)
        return result.model_copy(update={'namespace': request.namespace})


def test_reviewer_resolves_subject_reference_from_evidence():
    request = _request()
    request.evidence[0].provenance['artifact_namespace'] = 'subject_reference'
    reader = AddressReader()
    result = asyncio.run(ReviewerReaderTool(reader).ainvoke(ReaderArguments(artifact_id='artifact-1'), scope=request))
    assert reader.requests[0].namespace == ArtifactNamespace.SUBJECT_REFERENCE
    assert result.succeeded


def test_reviewer_rejects_namespace_collision_before_reading():
    request = _request()
    request.evidence.append(request.evidence[0].model_copy(update={'evidence_id': 'E-2', 'provenance': {'artifact_namespace': 'subject_reference'}}))
    request.cards[0].evidence_ids.append('E-2')
    reader = AddressReader()
    with pytest.raises(PermissionError, match='ambiguous'):
        asyncio.run(ReviewerReaderTool(reader).ainvoke(ReaderArguments(artifact_id='artifact-1'), scope=request))
    assert not reader.requests


def test_reviewer_rejects_reader_returning_wrong_namespace():
    request = _request()
    request.evidence[0].provenance['artifact_namespace'] = 'subject_reference'
    class WrongReader(RecordingReader):
        async def ainvoke(self, request):
            result = await super().ainvoke(request)
            return result.model_copy(update={'namespace': ArtifactNamespace.RESEARCH_REFERENCE})
    with pytest.raises(PermissionError):
        asyncio.run(ReviewerReaderTool(WrongReader()).ainvoke(ReaderArguments(artifact_id='artifact-1'), scope=request))


def test_conflicting_finish_reason_preserves_valid_card_without_model_retry(tmp_path):
    payload = json.loads(finish(card(quote('Alpha unique quote.'))).content)
    payload['no_evidence_reason'] = 'Coverage is incomplete'
    model = ScriptedModelClient(call('a'), ModelResponse(content=json.dumps(payload)))
    result = asyncio.run(workflow(tmp_path, model, Reader([read()])).ainvoke(scope()))
    assert len(result.evidence_cards) == 1 and len(model.calls) == 2
    assert any('Coverage is incomplete' in warning for warning in result.warnings)


@pytest.mark.parametrize('valid', [True, False])
def test_research_format_repair_is_bounded_and_keeps_reads(tmp_path, valid):
    repaired = finish(card(quote('Alpha unique quote.'))) if valid else ModelResponse(content='still not JSON')
    model = ScriptedModelClient(call('a'), ModelResponse(content='not JSON'), repaired)
    result = asyncio.run(workflow(tmp_path, model, Reader([read()])).ainvoke(scope()))
    assert len(model.calls) == 3 and len(result.read_results) == 1
    assert len(result.evidence_cards) == int(valid)
    assert not model.calls[-1][1].tools and model.calls[-1][1].tool_choice == 'none'


@pytest.mark.parametrize('valid', [True, False])
def test_reviewer_format_repair_still_validates_identifiers(valid):
    repaired = json.loads(_review_json())
    if not valid:
        repaired['highly_relevant_works'][0]['work_id'] = 'invented-work'
    model = ScriptedClient(ModelResponse(content='Plain-text partial-overlap conclusion'), ModelResponse(content=json.dumps(repaired)))
    result = asyncio.run(_reviewer(model, AddressReader()).review(_request()))
    assert len(model.calls) == 2
    assert result.status.value == ('reviewed' if valid else 'insufficient_evidence')
    assert not model.calls[-1][1].tools and model.calls[-1][1].tool_choice == 'none'


def test_baidu_query_constraint_reaches_schema_and_error_context(tmp_path):
    from novelty_agent_framework.persistence import ReferenceStore
    from novelty_agent_framework.tools.web_search_backend import SearchBackendResult
    class Backend:
        name = 'baidu'
        calls = []
        async def search(self, query, *, max_results):
            self.calls.append(query)
            return SearchBackendResult(query=query)
    backend = Backend()
    tool = WebSearchTool(backend, ReferenceStore(tmp_path))
    assert '72' in tool.args_schema.model_json_schema()['properties']['query']['description']
    bad = tool.args_schema(query='图' * 37)
    observation = asyncio.run(tool.ainvoke(bad, scope=scope()))
    context = tool.project_model_context(observation)
    assert not backend.calls and context['query_units'] == 74
    assert context['error_code'] == 'INVALID_QUERY' and context['max_query_units'] == 72
    good = asyncio.run(tool.ainvoke(tool.args_schema(query='图摘要 分布式GNN'), scope=scope()))
    assert good.succeeded and len(backend.calls) == 1


def test_zero_hit_and_failed_queries_are_preserved_separately(tmp_path):
    from datetime import datetime, timezone
    from novelty_agent_framework.schemas import TaskResearchResult, TaskResearchStatus
    from novelty_agent_framework.schemas.references import SearchExecution
    from novelty_agent_framework.workflows.research_task import _search_audit, _trusted_bundles
    from novelty_agent_framework.persistence import persist_task_retrieval_audit
    from novelty_agent_framework.tools.renderer import _format_query_plans
    from test_card_recovery import event
    from test_persistence import make_paper, make_task, make_plan
    task = make_task('T1', 'NP-1', 'query one', 1)
    executions = [SearchExecution(execution_id=f'ex-{i}', tool_name='database_search',
        source_id='springer', query=query, status=status, started_at=datetime.now(timezone.utc),
        error='HTTP 404' if status == 'failed' else None)
        for i, (query, status) in enumerate([('empty query', 'succeeded'), ('failed query', 'failed')])]
    trace = [event('database_search', {'search_executions': [ex.model_dump(mode='json')]}, ex.status.value == 'succeeded') for ex in executions]
    audit = _search_audit(trace)
    assert len(audit) == 2 and _trusted_bundles(trace)[0] == []
    result = TaskResearchResult(task_id='T1', novelty_point_id='NP-1', status=TaskResearchStatus.PARTIAL,
                                steps_used=2, search_executions=audit)
    path = persist_task_retrieval_audit(make_paper(), [task], [result], search_plans=[make_plan(task, 'query one')], rounds=1, output_root=tmp_path)
    plans = json.loads(path.read_text())['novelty_point_plans']
    rows = plans[0]['executed_queries']
    assert [row['result_marker'] for row in rows] == ['zero_hits', 'failed']
    assert rows[1]['error'] == 'HTTP 404'
    rendered = _format_query_plans(plans)
    assert 'empty query' in rendered and '零命中' in rendered
    assert 'failed query' in rendered and '执行失败' in rendered


def test_query_audit_retains_repeated_executions_with_same_stable_id():
    from datetime import datetime, timezone, timedelta
    from novelty_agent_framework.schemas.references import SearchExecution
    from novelty_agent_framework.workflows.research_task import _search_audit
    from test_card_recovery import event
    first = SearchExecution(execution_id='stable-id', tool_name='database_search', source_id='springer',
                            query='same query', status='succeeded', started_at=datetime.now(timezone.utc))
    second = first.model_copy(update={'started_at': first.started_at + timedelta(seconds=1)})
    row = first.model_dump(mode='json')
    trace = [event('database_search', {'search_executions': [row], 'research_bundle': {'search_executions': [row]}}),
             event('database_search', {'search_executions': [second.model_dump(mode='json')]})]
    assert len(_search_audit(trace)) == 2
