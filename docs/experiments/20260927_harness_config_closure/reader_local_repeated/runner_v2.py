"""Six bounded local Reader-only repetitions from executable frozen source.

Same real archived task/material as continued/replay_reader_local.py. Reduced
exploration budget is a new condition: never compare absolute calls to its 10-step pair.
"""
from pathlib import Path
import asyncio
from dataclasses import asdict
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from urllib.parse import urlsplit

ORDER = [('off_1', False), ('on_1', True), ('on_2', True), ('off_2', False), ('off_3', False), ('on_3', True)]

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + '\n')


def freeze():
    root = Path(__file__).resolve().parents[3]
    sys.path[:0] = [str(root), str(root / 'backend/src')]
    from novelty_agent_framework.config.loader import load_application_config
    from novelty_agent_framework.config.experiment import prepare_startup
    os.environ['LOCAL_VLLM_API_KEY'] = 'local'
    out = Path(__file__).parent / 'reader_local_repeated'
    out.mkdir(exist_ok=False)
    base = root / 'docs/experiments/runtime/MF2033k6lC_2026-09-24/run-f41ac741cf6f49deaa52124ae5b23903'
    inputs = {'runner.py': Path(__file__).read_bytes(),
              'historical_input.json': (base / 'stages/0007_run_research_task/input.json').read_bytes(),
              'historical_database_result.json': (base / 'tools/0002_database_search.json').read_bytes()}
    inputs.update({'workspace/' + p.relative_to(base / 'workspace').as_posix(): p.read_bytes()
                   for p in (base / 'workspace').rglob('*') if p.is_file()})
    overrides = {'researcher': {'model': {'temperature': 0, 'max_tokens': 2048, 'timeout_seconds': 120,
            'enable_thinking': None}, 'harness': {'max_turns': 4, 'max_total_tool_calls': 4,
            'per_tool_limits': {'reader': 4}, 'reuse_reader_results': False,
            'runtime_state_projection': False, 'enable_evidence_checkpoint': False},
            'tools': {'reader': {'max_chars_per_read': 16000, 'default_chars_per_read': 8000, 'max_total_read_chars': 64000}}},
        'project': {'runtime_debug': {'max_model_calls': 6, 'max_physical_provider_requests': 1}}}
    config = load_application_config(environ={}, profile_path=root / 'config/profiles/local-baseline.json', overrides=overrides)
    controls = {'local_only': True, 'enabled_tools': ['reader'], 'order': ORDER,
        'physical_chat_requests_total_limit': 36, 'physical_chat_requests_per_run_limit': 6,
        'runtime_model_calls_per_run_limit': 6, 'only_group_difference': 'reuse_reader_results',
        'actual_constructor_settings_saved_separately': True,
        'source_fixture': str(base.relative_to(root)),
        'comparison_to_previous_10_step_pair': 'not_directly_comparable; shared max_steps now 4'}
    frozen = prepare_startup(config, output_root=out, entrypoint='reader_repeated_local',
        snapshot_dir=out / 'startup', input_contents=inputs, active_roles=('researcher',),
        require_reviewer=False, runtime_controls=controls)
    write(out / 'experiment_plan.json', controls)
    snapshot = Path(frozen['code']['source_snapshot']['path'])
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', NO_PROXY='127.0.0.1,localhost,::1', no_proxy='127.0.0.1,localhost,::1')
    print('FROZEN_SOURCE ' + str(snapshot), flush=True)
    return subprocess.call([sys.executable, str(snapshot / 'inputs/runner.py'), '--worker', str(snapshot), str(out)], env=env, cwd=out)


def summarize_saved(out, label, enabled, run_dir, dispatches, *, exception=None):
    stage = run_dir / 'stages/0001_run_research_task'
    result = json.loads((stage / 'output.json').read_text()) if (stage / 'output.json').exists() else None
    meta = json.loads((stage / 'meta.json').read_text()) if (stage / 'meta.json').exists() else {}
    calls = [json.loads(p.read_text()) for p in sorted((run_dir / 'llm_calls').glob('*.json'))]
    tools = [json.loads(p.read_text()) for p in sorted((run_dir / 'tools').glob('*.json'))]
    physical_reads = []
    for tool in tools:
        raw = tool.get('raw_result') or {}
        if raw.get('tool_name') == 'reader':
            payload = raw.get('payload', {})
            physical_reads.extend(payload.get('read_results', [payload['read_result']] if 'read_result' in payload else []))
    ranges = {}
    for read in physical_reads:
        address = '|'.join(str(read.get(k)) for k in ('namespace', 'artifact_id', 'sha256'))
        ranges.setdefault(address, []).append((read['char_start'], read['char_end']))
    unique_chars = 0
    for rows in ranges.values():
        covered = 0
        for start, end in sorted(rows):
            unique_chars += max(0, end - max(start, covered))
            covered = max(covered, end)
    summary = {'label': label, 'reuse_reader_results': enabled, 'status': result['status'] if result else 'exception',
        'wall_seconds': meta.get('duration'), 'model_records': len(calls),
        'physical_chat_requests': sum(row['label'] == label for row in dispatches),
        'successful_model_responses': sum(c.get('status') == 'SUCCESS' for c in calls),
        'usage_available_calls': sum(bool(c.get('provider_usage')) for c in calls),
        'input_tokens_known_sum': sum(c.get('tokens', {}).get('input_tokens', 0) for c in calls),
        'output_tokens_known_sum': sum(c.get('tokens', {}).get('output_tokens', 0) for c in calls),
        'charged_tool_executions': sum(bool(t.get('raw_result')) for t in tools),
        'reader_replays': sum((t.get('normalized_result') or {}).get('reader_state_reused') is True or
                              (t.get('normalized_result') or {}).get('reused_result') is True for t in tools),
        'physical_read_segments': len(physical_reads),
        'empty_physical_read_segments': sum(r['char_end'] <= r['char_start'] for r in physical_reads),
        'physical_returned_chars': sum(len(r['text']) for r in physical_reads),
        'unique_read_chars': unique_chars, 'unique_read_artifacts': len(ranges),
        'read_ranges': ranges, 'cards': len(result['evidence_cards']) if result else None,
        'warnings': result['warnings'] if result else [], 'exception': exception,
        'tool_record_statuses': [t.get('execution_status') for t in tools], 'result': result,
        'harness_trace_sidecar_available': (out / label / 'trace.json').is_file(),
        'metrics_source': 'original runtime tool and model records plus saved stage output'}
    write(out / f'{label}.json', summary)
    return summary


async def worker(snapshot, out):
    source = snapshot / 'source'
    sys.path[:0] = [str(source), str(source / 'backend/src')]
    from backend.env import ModelProfile, ModelCallOptions, OpenAICompatibleChatClient, PromptLibrary
    from novelty_agent_framework.core import RuntimeArtifactManager, RuntimeDebugConfig
    from novelty_agent_framework.persistence import ReferenceStore
    from novelty_agent_framework.schemas import TaskResearchRequest
    from novelty_agent_framework.tools import ReaderTool, ReferenceArtifactReaderTool, ResearcherToolRegistry, EvidenceCardBuilder
    from novelty_agent_framework.workflows.research_task import TaskResearcherWorkflow, TaskResearcherConfig
    from novelty_agent_framework.config.experiment import verify_startup_snapshot
    from novelty_agent_framework.workflows import research_task
    assert Path(research_task.__file__).resolve().is_relative_to(source)
    assert verify_startup_snapshot(snapshot)
    os.environ['NO_PROXY'] = os.environ['no_proxy'] = '127.0.0.1,localhost,::1'
    transport = urllib.request.urlopen
    dispatches = json.loads((out / 'physical_dispatches.json').read_text()) if (out / 'physical_dispatches.json').exists() else []
    current = {'label': None, 'count': 0}
    def local_bounded_transport(request, *args, **kwargs):
        url = request.full_url if hasattr(request, 'full_url') else str(request)
        parsed = urlsplit(url)
        if (parsed.scheme, parsed.hostname, parsed.port, parsed.path) != ('http', '127.0.0.1', 8000, '/v1/chat/completions'):
            raise RuntimeError('experiment disallows nonlocal or nonchat transport')
        if len(dispatches) >= 36 or current['count'] >= 6:
            raise RuntimeError('experiment physical chat hard limit')
        current['count'] += 1
        dispatches.append({'label': current['label'], 'ordinal': len(dispatches) + 1,
            'request_sha256': hashlib.sha256(request.data).hexdigest(), 'started_at_unix': time.time()})
        write(out / 'physical_dispatches.json', dispatches)
        return transport(request, *args, **kwargs)
    urllib.request.urlopen = local_bounded_transport
    fixture = json.loads((snapshot / 'inputs/historical_database_result.json').read_text())['normalized_result']
    class FixtureWorkflow(TaskResearcherWorkflow):
        def _render_prompt(self, request, **kwargs):
            system, user = super()._render_prompt(request, **kwargs)
            return system, user + '\n\nThis is a frozen-candidate Reader experiment. Database search has already finished; no additional providers are enabled. Evaluate these existing candidates with Reader and produce the normal final draft.\n' + json.dumps(fixture, ensure_ascii=False)
    old = json.loads((snapshot / 'inputs/historical_input.json').read_text())
    request = TaskResearchRequest(subject_paper_id=old['subject_paper_id'], run_id='reader-local-repeat',
        novelty_point=old['current_point'], research_task=old['current_task'],
        search_plan=old['current_search_plan'], target_identity=old['target_identity'])
    write(out / 'request.json', request.model_dump(mode='json'))
    profile = ModelProfile(alias='local-qwen2.5-7b', model='qwen2.5-7b-instruct',
        base_url='http://127.0.0.1:8000/v1', api_key='local', context_window=32768,
        defaults={'timeout_seconds': 120, 'max_tokens': 2048})
    snapshots = []
    for label, enabled in ORDER:
        assert verify_startup_snapshot(snapshot)
        existing_run = out / label / request.subject_paper_id / 'runtime' / label
        if (existing_run / 'stages/0001_run_research_task/output.json').is_file():
            recovered = summarize_saved(out, label, enabled, existing_run, dispatches,
                exception={'type': 'ExperimentRunnerFinalizationError', 'message': 'Initial runner used unsupported PARTIAL terminal status; model and stage result preserved; no model rerun.'})
            snapshots.append(recovered)
            print('RECOVERED_WITHOUT_MODEL_RERUN ' + label, flush=True)
            continue
        current.update(label=label, count=sum(row['label'] == label for row in dispatches))
        fixture_path = out / label / 'fixture'
        shutil.copytree(snapshot / 'inputs/workspace', fixture_path)
        store = ReferenceStore(output_root=fixture_path)
        config = TaskResearcherConfig(max_steps=4, max_tool_calls=4,
            max_chars_per_read=16000, max_total_read_chars=64000, per_tool_limits={'reader': 4},
            reuse_reader_results=enabled, runtime_state_projection=False, enable_evidence_checkpoint=False,
            model_options=ModelCallOptions(temperature=0, max_tokens=2048, timeout_seconds=120, tool_choice='auto'))
        workflow = FixtureWorkflow(OpenAICompatibleChatClient(profile),
            ResearcherToolRegistry([ReaderTool(ReferenceArtifactReaderTool(store))]),
            EvidenceCardBuilder(store), prompts=PromptLibrary(source / 'backend/src/novelty_agent_framework/prompts'), config=config)
        settings = {'profile': {'alias': profile.alias, 'model': profile.model, 'base_url': profile.base_url,
            'context_window': profile.context_window, 'defaults': dict(profile.defaults), 'context_admission': asdict(profile.context_admission)},
            'task_config': asdict(config), 'actual_tools': workflow.tools.descriptions(),
            'source_snapshot': str(snapshot), 'source_module': research_task.__file__,
            'fixture_source': 'historical archived real publications; no synthetic document text',
            'max_model_calls': 6, 'only_group_difference': 'reuse_reader_results'}
        write(out / label / 'actual_settings.json', settings)
        runtime = RuntimeArtifactManager(request.subject_paper_id, run_id=label,
            config=RuntimeDebugConfig(output_root=out / label, archive_root=out / 'archive',
                max_model_calls=6, max_physical_provider_requests=1))
        result, trace, exception = None, (), None
        runtime.activate()
        started = time.monotonic()
        print('START ' + label, flush=True)
        try:
            stage = runtime.start_stage('run_research_task', request.model_dump(mode='json'))
            result, trace = await workflow._research(request)
            runtime.finish_stage(stage, result.model_dump(mode='json'))
            runtime.finish_run('SUCCESS' if result.status.value == 'completed' else 'FAILED')
        except Exception as exc:
            exception = {'type': type(exc).__name__, 'message': str(exc)}
            runtime.finish_run('FAILED', error=exc)
        finally:
            runtime.deactivate()
        elapsed = round(time.monotonic() - started, 3)
        trace_json = [{**asdict(event), 'observation': event.observation.model_dump(mode='json') if event.observation else None} for event in trace]
        write(out / label / 'trace.json', trace_json)
        summary = summarize_saved(out, label, enabled, runtime.run_dir, dispatches, exception=exception)
        snapshots.append(summary)
        write(out / 'comparison.json', snapshots)
        print(json.dumps({k: v for k, v in summary.items() if k not in {'result', 'read_ranges', 'warnings'}}, ensure_ascii=False), flush=True)
    validity = {'completed_conditions': len(snapshots), 'physical_chat_requests': len(dispatches),
        'physical_chat_hard_limit': 36, 'nonlocal_or_retrieval_requests': 0,
        'model_inference_samples': sum(s['successful_model_responses'] > 0 for s in snapshots),
        'source_snapshot_verified_after': verify_startup_snapshot(snapshot),
        'only_group_difference': 'reuse_reader_results', 'runtime_state_projection': False,
        'evidence_checkpoint': False, 'full_workflow': False,
        'statistical_claim': 'descriptive only; 3 repetitions per arm on one fixed task',
        'new_budget_condition': 'max_steps=4; not directly comparable with earlier max_steps=10 pair'}
    write(out / 'validity.json', validity)
    print(json.dumps(validity, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--worker':
        asyncio.run(worker(Path(sys.argv[2]), Path(sys.argv[3])))
    else:
        raise SystemExit(freeze())
