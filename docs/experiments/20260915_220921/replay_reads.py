"""Read archived artifacts locally through the fixed ReviewerReaderTool."""
import asyncio,json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.schemas import NoveltyPointReviewRequest, ReaderArguments, ResearchTask
from novelty_agent_framework.tools.reader import ReviewerReaderTool
from novelty_agent_framework.tools.reference_reader import ReferenceArtifactReaderTool
b=Path(__file__).resolve().parent
root=Path('docs/experiments/20260915_212448/run')
w=root/'MF2033k6lC'
result=json.loads((root/'result.json').read_text())
evidence={e['evidence_id']:e for p in w.glob('research-runs/*/*/attempt-*.json')
          for e in json.loads(p.read_text()).get('evidence',[])}
async def main():
    tool=ReviewerReaderTool(ReferenceArtifactReaderTool(ReferenceStore(root)))
    rows=[]
    for point in result['brief']['novelty_points']:
        cards=[c for c in result['evidence_cards'] if c['novelty_point_id']==point['point_id']]
        evid=[evidence[eid] for card in cards for eid in card['evidence_ids']]
        tasks=[ResearchTask(task_id=tid,novelty_point_id=point['point_id'],task_type='validation',language='en') for tid in {c['task_id'] for c in cards}]
        request=NoveltyPointReviewRequest(subject_paper_id='MF2033k6lC',novelty_point=point,cards=cards,evidence=evid,tasks=tasks)
        for artifact_id in sorted({e['artifact_id'] for e in evid}):
            response=await tool.ainvoke(ReaderArguments(artifact_id=artifact_id,max_chars=200),scope=request)
            read=response.payload['read_result']
            rows.append({'point':point['point_id'],'artifact_id':artifact_id,'namespace':read['namespace'],
                         'success':response.succeeded,'chars':len(read['text'])})
    (b/'archived_read_replay.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    print(json.dumps(rows,ensure_ascii=False))
asyncio.run(main())
