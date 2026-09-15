"""Verify the completed run's report and task recovery outcomes, offline."""
import json
from pathlib import Path
from collections import Counter
b=Path(__file__).resolve().parent;w=b/'run/MF2033k6lC'
def read(p,d=None):return json.loads(p.read_text()) if p.exists() else d
result=read(b/'run/result.json',{})
plans=read(w/'retrieval-plans.json',{}).get('novelty_point_plans',[])
report_path=w/'report/MF2033k6lC-report.md'
report=report_path.read_text() if report_path.exists() else ''
tasks=[read(p,{}) for p in w.glob('research-runs/*/*/attempt-*.json')]
tools=[read(p,{}) for p in w.glob('runtime/*/tools/*.json')]
queries=[]
for point in plans:
 rows=point.get('executed_queries',[])
 queries.append({'point':point['novelty_point_id'],'executions':len(rows),
                 'markers':dict(Counter(x.get('result_marker') for x in rows)),
                 'all_queries_in_report':all(x['query'] in report for x in rows) if rows else None})
checks={'report_exists':bool(report),'queries':queries,
        'cards_by_point':dict(Counter(c['novelty_point_id'] for c in result.get('evidence_cards',[]))),
        'review_statuses':[{'point':x['novelty_point_id'],'status':x['status'],'verdict':x.get('verdict'),'supplement_request':x.get('supplement_request')} for x in result.get('novelty_reviews',[])],
        'reader_failures':[{'stage':x.get('stage_name'),'error':(x.get('error')or{}).get('message')} for x in tools if x.get('tool_name')=='reader' and x.get('execution_status')=='FAILED'],
        'web_failures':[{'error':(x.get('raw_result')or{}).get('error'),'payload':(x.get('raw_result')or{}).get('payload')} for x in tools if x.get('tool_name')=='web_search' and x.get('execution_status')=='FAILED'],
        'recovery_warnings':[{'point':t.get('novelty_point_id'),'task':t.get('task_id'),'warnings':[s for s in t.get('warnings',[]) if any(word in s for word in ['recovery','repair','conflict','finalization','correction'])]} for t in tasks if any(any(word in s for word in ['recovery','repair','conflict','finalization','correction']) for s in t.get('warnings',[]))],
        'web_advice_shown':'无论文可用时的补充信息建议' in report,
        'bibliography_rows':sum(s.startswith('- ') for s in report.split('### 检索到的文献')[-1].splitlines()) if '### 检索到的文献' in report else 0}
(b/'verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
print(json.dumps(checks,ensure_ascii=False))
