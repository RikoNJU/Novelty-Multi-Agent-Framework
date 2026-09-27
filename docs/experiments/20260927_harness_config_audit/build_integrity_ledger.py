"""Read-only historical audit; emit compact scope/provenance facts beside this file."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
LOCAL = ROOT / 'docs/experiments/runtime/MF2033k6lC_2026-09-24/run-f41ac741cf6f49deaa52124ae5b23903'
BUNDLE = ROOT / 'docs/experiments/20260924_local_llm_full_workflow'
HISTORICAL = ROOT / 'docs/experiments/20260917_005448/runs/full/0001/MF2033k6lC'


def read(path):
    return json.loads(path.read_text())


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def run_facts(runtime, workspace=None):
    paper = read(next((runtime/'stages').glob('*extract_points/input.json')))['paper']
    plan = read(next((runtime/'stages').glob('*plan/output.json')))['brief']
    calls = [read(path) for path in sorted((runtime/'llm_calls').glob('*.json'))]
    trace_path = runtime/'diagnostics/point_extraction_trace.json'
    trace = read(trace_path) if trace_path.exists() else {}
    return {'runtime': str(runtime.relative_to(ROOT)), 'paper_input_sha256': sha(paper),
            'full_text_sha256': hashlib.sha256(paper['full_text'].encode()).hexdigest(),
            'digest_sha256': trace.get('digest_sha256'),
            'point_ids': [p['point_id'] for p in plan['novelty_points']],
            'tasks': [{k:t[k] for k in ('novelty_point_id','task_id','language')} for t in plan['research_tasks']],
            'models': sorted({(c.get('alias',''),c.get('model','')) for c in calls}),
            'first_prompt_request_sha256': sha(calls[0].get('request_payload'))}


trace = read(LOCAL/'diagnostics/point_extraction_trace.json')
result = read(BUNDLE/'result.json')
plans = read(BUNDLE/'data/retrieval-plans.json')['novelty_point_plans']
reviews = {r['novelty_point_id']:r for r in result['novelty_reviews']}
conclusions = {r['novelty_point_id']:r for r in result['report']['conclusions']}
rows = []
for point in result['brief']['novelty_points']:
    pid = point['point_id']
    plan = next(p for p in plans if p['novelty_point_id']==pid)
    queries = plan.get('executed_queries',[])
    rows.append({'point_id':pid,'claim':point['claim'],'task_ids':[t['task_id'] for t in plan['research_tasks']],
                 'search_plan_task_ids':[p['task_id'] for p in plan['search_plans']],
                 'query_status_counts':{s:sum(q.get('status')==s for q in queries) for s in sorted({q.get('status') for q in queries})},
                 'evidence_cards':sum(c['novelty_point_id']==pid for c in result['evidence_cards']),
                 'review_status':reviews[pid]['status'],'review_cause':reviews[pid]['incomplete_reason'],
                 'report_status':conclusions[pid]['review_status'],'verdict':conclusions[pid]['verdict'],
                 'final_state':'no_bound_material_no_novelty_verdict'})
ledger = {
    'run_id':'run-f41ac741cf6f49deaa52124ae5b23903',
    'source_trace':str((LOCAL/'diagnostics/point_extraction_trace.json').relative_to(ROOT)),
    'source_trace_sha256':sha(trace),
    'candidate_ledger':[
        {'candidate_index':1,'original_id':'GSAERU','dedup_action':'retained','final_point_id':'NP-1'},
        {'candidate_index':2,'original_id':'GSAERU_Summary','dedup_action':'deleted_without_mapping','final_point_id':None,
         'audit_state':'possible_duplicate_of_GSAERU_requires_semantic_review'},
        {'candidate_index':3,'original_id':'DSGNN','dedup_action':'deleted_without_mapping','coverage_followup':'restored_with_rewording','final_point_id':'NP-2'},
        {'candidate_index':4,'original_id':'Sketch-DBH','dedup_action':'deleted_without_mapping','coverage_followup':'not_restored','final_point_id':None,
         'audit_state':'lost_before_task_creation_author_independent_contribution_visible'},
    ],
    'confirmed_point_ledger':rows,
    'all_confirmed_points_present_in_report':set(reviews)==set(conclusions)=={r['point_id'] for r in rows},
    'local':run_facts(LOCAL),
    'historical':run_facts(HISTORICAL/'runtime/run-bdb2796a9ad145e2b741706bd4dd4368'),
    'causality_limit':'Same PaperInput; prompt, model and runtime options differ, so historical comparison is observational.',
}
(OUT/'integrity_ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'points':len(rows),'all_confirmed_points_present_in_report':ledger['all_confirmed_points_present_in_report'],
                  'same_paper_input':ledger['local']['paper_input_sha256']==ledger['historical']['paper_input_sha256']},ensure_ascii=False))
