"""Replay frozen plans through the production compiler/executor without model/network calls."""
import asyncio, collections, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
import httpx

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
from novelty_agent_framework.schemas import NoveltyPoint,ResearchTask,SearchPlan,SearchConcept,SearchStrategy,StructuredSourceRetrievalRequest
from novelty_agent_framework.schemas.failures import FailureCode, RecoveryAction
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.tools.database_search import RetrievalSource,StructuredSourceRetrievalTool
from novelty_agent_framework.tools.database_search.providers.arxiv import ArxivQueryAdapter

SOURCE=ROOT/'docs/experiments/runtime/MF2033k6lC_2026-09-27/run-d55196716d254641a84cf1b0c19f14e9/workspace/MF2033k6lC'

class NoPlanner:
    def plan(self,*args,**kwargs):raise AssertionError('Frozen plan must not invoke a planner or model')

class ControlledSource:
    source_id='arxiv'
    def __init__(self,mode):self.mode=mode;self.calls=[]
    def search(self,query,*,limit=10):
        self.calls.append(query)
        request=httpx.Request('GET','https://example.test/controlled-provider')
        if self.mode=='http406':httpx.Response(406,request=request).raise_for_status()
        if self.mode=='network_timeout':raise httpx.ReadTimeout('Injected read timeout',request=request)
        return []

async def main():
    target=OUT/'offline_results.json'
    if target.exists():raise SystemExit('Refusing to overwrite an existing experiment')
    point_rows=json.loads((SOURCE/'novelty-points.json').read_text())['novelty_points'];points={p['point_id']:NoveltyPoint.model_validate(p) for p in point_rows}
    plan_rows=json.loads((SOURCE/'retrieval-plans.json').read_text())['novelty_point_plans']
    results=[];compilations=[]
    with tempfile.TemporaryDirectory(prefix='novelty-causal-offline-') as temp:
        for row in plan_rows:
            task=ResearchTask.model_validate(row['research_tasks'][0]);model=SearchPlan.model_validate(row['search_plans'][0])
            human=model.model_copy(update={'concepts':[SearchConcept(concept_id='C1',name='graph neural network',terms=['graph neural network'],role='escape')],'strategies':[SearchStrategy(strategy_id='S1',level='strict',expression='C1'),SearchStrategy(strategy_id='S2',level='medium',expression='C1'),SearchStrategy(strategy_id='S3',level='broad',expression='C1')],'protected_concept_ids':['C1']})
            for label,plan in [('archived_qwen',model),('human_fixed_control',human)]:
                queries=[q.query for q in ArxivQueryAdapter().compile(plan)]
                if label=='archived_qwen':assert queries[0]==row['executed_queries'][0]['query'],row['novelty_point_id']
                compilations.append({'point_id':plan.novelty_point_id,'plan_kind':label,'plan':plan.model_dump(mode='json'),'compiled_base_queries':queries,'legacy_render_queries':[q.query for q in ArxivQueryAdapter(render_v2=False).compile(plan)]})
                for mode in ['http406','network_timeout','http200_empty']:
                    fake=ControlledSource(mode)
                    source=RetrievalSource(source_id='arxiv',query_adapter=ArxivQueryAdapter(),search_tool=fake,metadata_tool=None,full_text_tool=None)
                    tool=StructuredSourceRetrievalTool(search_planner=NoPlanner(),source=source,reference_store=ReferenceStore(Path(temp)/f'{plan.novelty_point_id}-{label}-{mode}'),candidate_limit=8,max_provider_requests=50)
                    request=StructuredSourceRetrievalRequest(subject_paper_id='MF2033k6lC',source_id='arxiv',novelty_point=points[plan.novelty_point_id],research_task=task,search_plan=plan,run_id='offline-causality')
                    bundle=await tool.ainvoke(request)
                    statuses=dict(collections.Counter(e.status.value for e in bundle.search_executions))
                    result={'point_id':plan.novelty_point_id,'plan_kind':label,'injected_response':mode,'stub_search_calls':len(fake.calls),'execution_status_counts':statuses,'executions':[{'query':e.query,'status':e.status.value,'not_run_reason':e.parameters.get('not_run_reason'),'failure_code':e.failure.code.value if e.failure else None} for e in bundle.search_executions]}
                    if mode=='http200_empty':assert len(fake.calls)>1 and 'not_run' not in statuses and 'failed' not in statuses
                    else:assert len(fake.calls)==1 and statuses.get('failed')==1 and statuses.get('not_run',0)>0
                    results.append(result)
    payload={'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'model_calls':0,'network_calls':0,'historical_plan_source':(SOURCE/'retrieval-plans.json').relative_to(ROOT).as_posix(),'historical_plan_sha256':hashlib.sha256((SOURCE/'retrieval-plans.json').read_bytes()).hexdigest(),'failure_codes':[c.value for c in FailureCode],'recovery_actions':[a.value for a in RecoveryAction],'case_count':len(results),'compiler_matches_historical_first_queries':True,'compilations':compilations,'results':results}
    target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'cases':len(results),'model_calls':0,'network_calls':0,'all_causal_assertions_passed':True,'failure_codes':len(FailureCode),'recovery_actions':len(RecoveryAction)}))

if __name__=='__main__':asyncio.run(main())
