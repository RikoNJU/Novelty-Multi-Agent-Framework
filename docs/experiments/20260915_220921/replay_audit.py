"""Rebuild query audit from archived observations using the repaired code."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from novelty_agent_framework.schemas import PaperInput, TaskResearchResult, ResearchTask, SearchPlan, ResearcherToolObservation
from novelty_agent_framework.core.tool_call_harness import ToolCallHarnessEvent
from novelty_agent_framework.workflows.research_task import _search_audit
from novelty_agent_framework.persistence import persist_task_retrieval_audit
from novelty_agent_framework.tools.renderer import _format_query_plans
b=Path(__file__).resolve().parent
w=Path('docs/experiments/20260915_212448/run/MF2033k6lC')
old=json.loads((w/'retrieval-plans.json').read_text())
paper=PaperInput.model_validate_json((w/'paper-input/others/paper.json').read_text())
trace=[]
for p in w.glob('runtime/*/tools/*database_search.json'):
    observation=ResearcherToolObservation.model_validate(json.loads(p.read_text())['raw_result'])
    trace.append(ToolCallHarnessEvent(kind='tool_result',observation=observation))
executions=_search_audit(trace)
results=[]
for p in w.glob('research-runs/*/*/attempt-*.json'):
    r=TaskResearchResult.model_validate_json(p.read_text())
    matches=[e for e in executions if e.parameters.get('novelty_point_id')==r.novelty_point_id and e.parameters.get('task_id')==r.task_id]
    results.append(r.model_copy(update={'search_executions':matches}))
tasks=[ResearchTask.model_validate(t) for point in old['novelty_point_plans'] for t in point['research_tasks']]
plans=[SearchPlan.model_validate(t) for point in old['novelty_point_plans'] for t in point['search_plans']]
path=persist_task_retrieval_audit(paper,tasks,results,search_plans=plans,rounds=old['rounds'],output_root=b/'audit-replay')
new=json.loads(path.read_text())
(b/'query-audit-preview.md').write_text(_format_query_plans(new['novelty_point_plans']))
summary=[{'point':p['novelty_point_id'],'queries':len(p['executed_queries']),
          'markers':[q['result_marker'] for q in p['executed_queries']]} for p in new['novelty_point_plans']]
(b/'audit_replay_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(summary)
