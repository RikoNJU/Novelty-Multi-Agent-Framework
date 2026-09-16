"""Summarize original Runtime Debug records and retained evidence provenance."""
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent


def summarize(mode):
    root = BASE / 'runtime' / mode
    manifest_path = root / 'run.json'
    if not manifest_path.exists():
        return {'status': 'NOT_RUN'}
    manifest = json.loads(manifest_path.read_text())
    raw_events = [json.loads(p.read_text()) for p in root.glob('MF*/runtime/*/provider_requests/*.json')]
    physical = [e for e in raw_events if e['event_type'] == 'physical_request']
    tools = [json.loads(p.read_text()) for p in root.glob('MF*/runtime/*/tools/*.json')]
    stages = [json.loads(p.read_text()) for p in root.glob('MF*/runtime/*/stages/*/meta.json')]
    stages.sort(key=lambda s: s.get('started_at', ''))
    results_path = root / 'results.json'
    results = json.loads(results_path.read_text()) if results_path.exists() else []
    if mode == 'full':
        for path in root.glob('MF*/runtime/*/stages/*run_research_task/output.json'):
            results.extend(json.loads(path.read_text()).get('task_research_results', []))
    tasks = []
    for result in results:
        evidence = {e['evidence_id']: e for e in result.get('evidence', [])}
        cards = result.get('evidence_cards', [])
        external_cards = [c['card_id'] for c in cards if any(
            evidence.get(eid, {}).get('provenance', {}).get('artifact_namespace') == 'research_reference'
            for eid in c['evidence_ids'])]
        tasks.append({'task_id': result.get('task_id'), 'novelty_point_id': result.get('novelty_point_id'), 'status': result['status'], 'read_count': len(result.get('read_results', [])),
            'card_count': len(cards), 'web_candidate_card_ids': external_cards,
            'read_namespaces': dict(Counter(r['namespace'] for r in result.get('read_results', [])))})
    intervals = [e['previous_request_interval_ms'] for e in physical if e.get('previous_request_interval_ms') is not None]
    final = None
    if (root / 'result.json').exists():
        final_result = json.loads((root / 'result.json').read_text())
        external_ids = {card_id for task in tasks for card_id in task['web_candidate_card_ids']}
        final = {'card_count': len(final_result.get('evidence_cards', [])),
            'web_candidate_card_ids': [c['card_id'] for c in final_result.get('evidence_cards', []) if c['card_id'] in external_ids],
            'rounds': final_result.get('rounds'),
            'review_count': len(final_result.get('novelty_reviews', [])),
            'insufficient_final_evidence_points': final_result.get('insufficient_final_evidence_points', [])}
    return {'manifest': manifest, 'tasks': tasks, 'final': final,
        'request_metrics': {'logical_web_requests': sum(e['event_type'] == 'logical_request' for e in raw_events),
            'physical_web_requests': len(physical),
            'status_counts': dict(Counter(str(e['status_code']) for e in physical)),
            'retry_count': sum(e['attempt'] > 1 for e in physical),
            'interval_violation_count': sum(bool(e.get('interval_violation')) for e in physical),
            'minimum_observed_interval_ms': min(intervals, default=None),
            'task_ids': sorted({e['task_id'] for e in physical if e.get('task_id')})},
        'tool_counts': dict(Counter(t['tool_name'] for t in tools)),
        'retrieval_states': dict(Counter(t.get('business_status') for t in tools if t['tool_name'] == 'database_search')),
        'stages': [{k: s.get(k) for k in ['stage_name', 'started_at', 'finished_at', 'status', 'duration_ms']} for s in stages]}


if __name__ == '__main__':
    result = {mode: summarize(mode) for mode in ['single', 'parallel', 'full']}
    (BASE / 'metrics/workflows.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({mode: {'status': v.get('manifest', {}).get('status', v.get('status')),
        'tasks': v.get('tasks', []), 'request_metrics': v.get('request_metrics')} for mode, v in result.items()}, ensure_ascii=False, indent=2))
