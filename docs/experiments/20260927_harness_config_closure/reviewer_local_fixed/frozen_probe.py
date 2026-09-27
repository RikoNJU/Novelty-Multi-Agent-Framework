"""Three fixed real-paper Reviewer samples, <= 4 local requests each / 12 total.

No retrieval, cloud models, forced tools, or adaptive prompt changes. Freeze source
and input before importing production modules; refuse to overwrite observations.
"""
from __future__ import annotations
import asyncio
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent / 'reviewer_local_fixed'
HIST = ROOT/'docs/experiments/20260917_214820_retrieval_repair/runs/full/0001'
PAPER = 'MF2033k6lC'
CARD = 'card_055dcd710a45194158c1d5ba'
STAGE = HIST/PAPER/'runtime/run-d606cd37534a47349b905d42c6141768/stages/0012_review_evidence/input.json'


def sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def freeze():
    if OUT.exists():
        raise SystemExit('Refusing to overwrite prior observations')
    OUT.mkdir()
    snapshot=OUT/'source_snapshot'
    hashes={}
    for relative in ('backend/env','backend/src/novelty_agent_framework'):
        for source in (ROOT/relative).rglob('*'):
            if not source.is_file() or '__pycache__' in source.parts:
                continue
            if source.suffix not in {'.py','.md','.json'}:
                continue
            target=snapshot/source.relative_to(ROOT)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(source.read_bytes())
            hashes[str(source.relative_to(ROOT))]=hashlib.sha256(target.read_bytes()).hexdigest()
    shutil.copy2(__file__,OUT/'frozen_probe.py')
    shutil.copytree(HIST/PAPER/'references',OUT/'artifacts'/PAPER/'references')
    state=json.loads(STAGE.read_text())
    card=next(item for item in state['validator_accepted_cards'] if item['card_id']==CARD)
    request={'subject_paper_id':PAPER,'novelty_point':next(item for item in state['novelty_points'] if item['point_id']=='NP-3'),
             'tasks':[item for item in state['all_research_tasks'] if item['novelty_point_id']=='NP-3'],
             'cards':[card],'evidence':[item for item in state['raw_evidence'] if item['evidence_id'] in card['evidence_ids']]}
    save(OUT/'request.json',request)
    save(OUT/'source_manifest.json',{'source_sha256':hashes,'input_sha256':sha(request),
        'source_stage':str(STAGE.relative_to(ROOT)),'source_stage_sha256':hashlib.sha256(STAGE.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256((OUT/'frozen_probe.py').read_bytes()).hexdigest(),
        'plan':{'repetitions':3,'max_physical_model_requests':12,'max_requests_per_repetition':4,
                'endpoint':'http://127.0.0.1:8000/v1','external_retrieval':False,'forced_tool_choice':False,
                'semantic_rubric':'Check positive clustering/stream partition facts against actual quotes; abstract silence does not establish absence of Count-Min Sketch/min-heap or novel verdict; keep unresolved features.'}})
    sys.path[:0]=[str(snapshot/'backend/src'),str(snapshot)]
    return request


async def main():
    raw_request=freeze()
    from backend.env import ModelCallOptions, ModelProfile, OpenAICompatibleChatClient, ModelCallBudgetExceeded
    from novelty_agent_framework.agents.evidence_reviewer import NoveltyEvidenceReviewer,EvidenceReviewerConfig
    from novelty_agent_framework.schemas import NoveltyPointReviewRequest
    from novelty_agent_framework.persistence import ReferenceStore
    from novelty_agent_framework.tools import ReviewerReaderTool,ReferenceArtifactReaderTool,ResearcherToolRegistry
    request=NoveltyPointReviewRequest.model_validate(raw_request)
    options=ModelCallOptions(max_tokens=1024,temperature=0.0,timeout_seconds=60)
    config=EvidenceReviewerConfig(max_steps=2,max_tool_calls=1,max_total_read_chars=2000,
        card_timeout_seconds=90,summary_timeout_seconds=90,summary_input_date='2026-09-27')
    save(OUT/'config.json',{'config':asdict(config),'options':asdict(options),'model':'qwen2.5-7b-instruct',
                           'context_window':32768,'max_per_sample':4,'max_total':12})
    os.environ['NO_PROXY']='127.0.0.1,localhost'
    os.environ['no_proxy']='127.0.0.1,localhost'
    rows=[]
    class Client:
        def __init__(self):
            self.raw=OpenAICompatibleChatClient(ModelProfile(alias='local-reviewer-fixed',model='qwen2.5-7b-instruct',
                base_url='http://127.0.0.1:8000/v1',api_key='local-placeholder',context_window=32768))
            self.profile=self.raw.profile
            self.sample=0
            self.sample_calls=0
        async def acomplete(self,messages,*,options=None):
            if len(rows)>=12 or self.sample_calls>=4:
                raise ModelCallBudgetExceeded('fixed Reviewer physical model request cap reached')
            payload=self.raw._build_payload(messages,options)
            row={'sequence':len(rows)+1,'sample':self.sample,'request':payload,'request_sha256':sha(payload)}
            rows.append(row); self.sample_calls+=1
            started=time.monotonic()
            try:
                response=await self.raw.acomplete(messages,options=options)
                row.update(response=response.raw,response_sha256=sha(response.raw),usage=response.usage)
                return response
            except Exception as exc:
                row.update(error_type=type(exc).__name__,error=str(exc))
                raise
            finally:
                row['duration_seconds']=time.monotonic()-started
                save(OUT/f'call-{row["sequence"]:02}.json',row)
    client=Client()
    outcomes=[]
    for index in range(1,4):
        client.sample=index;client.sample_calls=0
        tool=ReviewerReaderTool(ReferenceArtifactReaderTool(ReferenceStore(OUT/'artifacts'),max_chars_per_read=2000))
        reviewer=NoveltyEvidenceReviewer(client,config=config,model_options=options,
                                         tool_registry=ResearcherToolRegistry([tool]))
        card_review=await reviewer.review_card(request)
        card_rows=[{'index':1,'card_id':CARD,'novelty_point_id':'NP-3','status':'completed',
                    'review':card_review.model_dump(mode='json')}]
        attempt=await reviewer.summarize_with_checkpoint(request,card_rows,output_root=OUT/'artifacts',run_id=f'fixed-sample-{index}')
        sample={'sample':index,'input_sha256':sha(raw_request),'card_review':card_review.model_dump(mode='json'),
                'summary_attempt':attempt.model_dump(mode='json'),'physical_calls':client.sample_calls}
        save(OUT/f'sample-{index}.json',sample); outcomes.append(sample)
        print(json.dumps({'sample':index,'physical_calls':client.sample_calls,'card_status':card_review.status.value,
            'card_reason':card_review.incomplete_reason,'summary_status':attempt.status,
            'summary_reason':attempt.review.incomplete_reason,'verdict':attempt.review.verdict.value if attempt.review.verdict else None}),flush=True)
        if rows and rows[-1].get('error_type') and not rows[-1].get('response'):
            print('Transport/model error observed; no further network samples.',flush=True)
            break
    usage={'prompt_tokens':0,'completion_tokens':0,'total_tokens':0}
    for row in rows:
        for key in usage:
            usage[key]+=(row.get('usage') or {}).get(key,0) or 0
    save(OUT/'summary.json',{'samples':len(outcomes),'physical_model_requests':len(rows),'usage':usage,
        'cloud_model_calls':0,'retrieval_calls':0,'api_billing':'UNPRICED','local_compute_cost':None,
        'duration_seconds':sum(row['duration_seconds'] for row in rows),
        'input_hashes':[outcome['input_sha256'] for outcome in outcomes],
        'semantic_accuracy':'requires independent quote comparison; execution/ID validation is insufficient'})


if __name__=='__main__':
    asyncio.run(main())
