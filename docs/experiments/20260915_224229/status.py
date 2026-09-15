import json
from pathlib import Path
from collections import Counter
b=Path(__file__).resolve().parent/'run'
def read(p,d=None):
 try:return json.loads(p.read_text())
 except (FileNotFoundError,json.JSONDecodeError):return d
calls=read(b/'model_calls.json',[])
stages=[(p.parent.name,read(p,{}).get('status')) for p in (b/'MF2033k6lC').glob('runtime/*/stages/*/meta.json')]
events=[read(p,{}) for p in (b/'MF2033k6lC').glob('runtime/*/tools/*.json')]
print(json.dumps({'run':read(b/'run.json',{}).get('status'),'models':len(calls),'tokens':sum(x.get('total_tokens') or 0 for x in calls),'last_stages':sorted(stages)[-5:],'tools':dict(Counter((x.get('tool_name','?')+':'+x.get('execution_status','?')) for x in events))},ensure_ascii=False))
