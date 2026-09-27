"""Read-only consistency check of the saved six-run local experiment."""
from pathlib import Path
import hashlib
import json
from statistics import mean

OUT = Path(__file__).parent / 'reader_local_repeated'

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()

def main():
    rows = json.loads((OUT / 'comparison.json').read_text())
    settings, first_payloads = [], []
    by_arm = {}
    for row in rows:
        label = row['label']
        setting = json.loads((OUT / label / 'actual_settings.json').read_text())
        assert setting['task_config'].pop('reuse_reader_results') == row['reuse_reader_results']
        settings.append(setting)
        run = OUT / label / 'MF2033k6lC/runtime' / label
        calls = [json.loads(p.read_text()) for p in sorted((run / 'llm_calls').glob('*.json'))]
        first_payloads.append(calls[0]['request_payload'])
        tools = [json.loads(p.read_text()) for p in sorted((run / 'tools').glob('*.json'))]
        assert all(t['execution_status'] == 'SUCCESS' for t in tools)
        by_arm[label] = {
            'initial_request_sha256': hashlib.sha256(canonical(first_payloads[-1])).hexdigest(),
            'actual_settings_except_flag_sha256': hashlib.sha256(canonical(setting)).hexdigest(),
            'duplicate_or_overlapping_returned_chars': row['physical_returned_chars'] - row['unique_read_chars'],
            'empty_reads': row['empty_physical_read_segments'],
            'invalid_or_failed_tool_records': sum(t['execution_status'] != 'SUCCESS' for t in tools),
            'usage_available_for_every_dispatched_call': row['usage_available_calls'] == row['physical_chat_requests'],
            'candidate_artifacts_read': row['unique_read_artifacts'],
            'all_observed_material_roles': sorted({read['role'] for read in row['result']['read_results']}),
            'all_provider_usage': [call['provider_usage'] for call in calls],
        }
    assert all(value == settings[0] for value in settings)
    assert all(value == first_payloads[0] for value in first_payloads)
    groups = {}
    for enabled in (False, True):
        group = [row for row in rows if row['reuse_reader_results'] == enabled]
        groups['on' if enabled else 'off'] = {key: [row[key] for row in group] for key in (
            'physical_chat_requests','reader_replays','physical_read_segments','empty_physical_read_segments',
            'physical_returned_chars','unique_read_chars','unique_read_artifacts','cards',
            'input_tokens_known_sum','output_tokens_known_sum','wall_seconds')}
        groups['on' if enabled else 'off']['mean_wall_seconds'] = mean(row['wall_seconds'] for row in group)
    report = {'actual_settings_identical_except_reuse_reader_results': True,
        'all_six_initial_requests_identical': True, 'total_physical_chat_requests': sum(row['physical_chat_requests'] for row in rows),
        'no_usage_missing': all(value['usage_available_for_every_dispatched_call'] for value in by_arm.values()),
        'declared_candidate_artifacts': 8, 'by_arm': by_arm, 'groups': groups,
        'semantic_coverage_verified': False, 'full_text_read': False,
        'scientific_or_end_to_end_success': False,
        'runner_deviation': 'off_1 completed research then initial runner failed at Runtime terminal status; records recovered without repeat requests; resume_note.json keeps hash/version boundary',
        'sampling_limit': 'three repetitions per arm, same one real historical task, temperature 0; descriptive only'}
    (OUT / 'consistency.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'by_arm'}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
