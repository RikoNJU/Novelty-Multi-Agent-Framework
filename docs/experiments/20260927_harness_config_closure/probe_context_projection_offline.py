"""Offline control: fixed mechanical trajectories, no semantic/model efficacy claim."""
from pathlib import Path
import hashlib
import json
import sys
from dataclasses import asdict
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'backend/src'), str(ROOT / 'tests')]
from test_context_projection import Client, Registry, TEXT, call, run, state
from backend.env import ModelResponse
from novelty_agent_framework.core.tool_call_harness import ToolCallHarnessConfig, RUNTIME_STATE_PREFIX
OUT = Path(__file__).parent / 'context_projection_offline'


def one(enabled, long=False):
    responses = ([call('reader', artifact_id='artifact', max_chars=len(TEXT)) for _ in range(30)]
                 if long else [call('database_search', source_id='arxiv', fail=True),
                    call('database_search', source_id='arxiv'),
                    call('reader', artifact_id='artifact', max_chars=len(TEXT)),
                    call('submit_evidence'), call('reader', artifact_id='artifact', char_start=len(TEXT), max_chars=1)])
    client = Client([*responses, ModelResponse(content='done')])
    result, registry = run(client, config=ToolCallHarnessConfig(runtime_state_projection=enabled,
        reuse_reader_results=True, max_turns=32 if long else 10, max_tool_calls=8,
        max_total_read_chars=200, per_tool_limits={'reader': 3, 'database_search': 3, 'submit_evidence': 2}))
    contexts = [[asdict(message) for message in messages] for messages, _ in client.calls]
    projection_rows = [state(messages) for messages, _ in client.calls] if enabled else []
    return {'flag': enabled, 'long_trajectory': long, 'contexts': contexts,
        'physical_tool_calls': len(registry.calls), 'model_fixture_calls': len(client.calls),
        'turns_used': result.turns_used,
        'state_message_counts': [sum((row['content'] or '').startswith(RUNTIME_STATE_PREFIX) for row in rows) for rows in contexts],
        'serialized_context_chars': [len(json.dumps(rows, ensure_ascii=False)) for rows in contexts],
        'projected_state_chars': [len(json.dumps(row, ensure_ascii=False)) for row in projection_rows],
        'state': projection_rows,
        'original_non_system_history': [[row for row in rows if row['role'] != 'system'] for rows in contexts]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {'live_model_requests': 0, 'fixture_kind': 'synthetic mechanical state; no semantic evidence claim',
        'count_units': 'serialized characters, never token estimates', 'experiments': []}
    for label, long in [('mixed', False), ('long', True)]:
        old, new = one(False, long), one(True, long)
        same = old.pop('original_non_system_history') == new.pop('original_non_system_history')
        assert same
        for condition, value in [('off', old), ('on', new)]:
            (OUT / f'{label}_{condition}.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        summary['experiments'].append({'label': label, 'original_non_system_messages_byte_equal': same,
            'model_fixture_calls': [old['model_fixture_calls'], new['model_fixture_calls']],
            'physical_tool_calls': [old['physical_tool_calls'], new['physical_tool_calls']],
            'state_message_count_max': [max(old['state_message_counts']), max(new['state_message_counts'])],
            'last_context_chars': [old['serialized_context_chars'][-1], new['serialized_context_chars'][-1]],
            'on_first_state_chars': new['projected_state_chars'][0],
            'on_last_state_chars': new['projected_state_chars'][-1],
            'on_read_state_stable_after_first_read': all(row['reader_artifacts'] == new['state'][1]['reader_artifacts'] for row in new['state'][1:]) if long else None})
    summary['code_sha256'] = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in [
        'backend/src/novelty_agent_framework/core/tool_call_harness.py', 'tests/test_context_projection.py']}
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
