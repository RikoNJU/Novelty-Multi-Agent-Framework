"""Inspect this run using the existing arXiv acceptance audit, without network."""
import importlib.util
import json
from pathlib import Path

ROOT = Path.cwd()
BASE = Path(__file__).resolve().parent
RAW = ROOT / 'outputs' / BASE.name
spec = importlib.util.spec_from_file_location('arxiv_workflow_audit', ROOT / 'docs/experiments/ARXIV_LIMIT_FINAL_2026-09-16/audit_workflows.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.BASE = RAW
result = module.summarize('full')
root = RAW / 'runtime/full'
summary_paths = list(root.glob('MF*/runtime/*/summary.json'))
if summary_paths:
    runtime = json.loads(summary_paths[0].read_text())
    result['runtime_run'] = runtime.get('run')
    result['integrity_gates'] = runtime.get('integrity_gates')
    result['llm_usage'] = runtime.get('llm_usage')
    result['provider_summary'] = runtime.get('provider_requests')
    result['runtime_summary_path'] = str(summary_paths[0].relative_to(ROOT))
if (root / 'result.json').exists():
    final = json.loads((root / 'result.json').read_text())
    result['review_verdicts'] = final.get('novelty_reviews', [])
    result['issues'] = final.get('issues', [])
    result['final_cards'] = [{'card_id': c['card_id'], 'title': c['document_title'], 'point_id': c['novelty_point_id'], 'sources': c['sources']} for c in final.get('evidence_cards', [])]
(BASE / 'metrics.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': result.get('manifest', {}).get('status'), 'final': result.get('final'), 'requests': result.get('request_metrics'), 'task_statuses': [(t['novelty_point_id'], t['task_id'], t['status'], t['card_count']) for t in result.get('tasks', [])]}, ensure_ascii=False, indent=2))
