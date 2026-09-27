"""Finish only saved review aggregation after diagnostic row omitted index; no card rerun."""
import asyncio,json,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
from novelty_agent_framework.config import load_application_config
from novelty_agent_framework.config.factory import build_workflow
from novelty_agent_framework.core.runtime_artifacts import RuntimeArtifactManager,RuntimeDebugConfig
from novelty_agent_framework.schemas import NoveltyPointReviewRequest
D=OUT/'review_followup'
if (D/'summary_attempt.json').exists():raise SystemExit('Refusing overwrite')
request=NoveltyPointReviewRequest.model_validate_json((D/'startup/inputs/review-request.json').read_text())
card=json.loads((D/'card_review.json').read_text())
config=load_application_config(profile_path=D/'profile.json',environ={})
reviewer=build_workflow(config,output_root=D).services.reviewer
manager=RuntimeArtifactManager('MF2033k6lC',run_id='finish-saved-summary',config=RuntimeDebugConfig(enabled=True,output_root=D,archive_root=D/'archive',max_model_calls=1,max_physical_provider_requests=1),runtime_config=config.model_dump(mode='json'),enabled_tools=[],stage_names=['summarize_review'])
async def main():
 manager.activate();status='FAILED';error=None
 rows=[{'index':1,'card_id':request.cards[0].card_id,'novelty_point_id':request.novelty_point.point_id,'status':'completed','review':card}]
 stage=manager.start_stage('summarize_review',{'request':request.model_dump(mode='json'),'card_reviews':rows})
 try:
  result=await reviewer.summarize_with_checkpoint(request,rows,output_root=D,run_id='finish-saved-summary')
  manager.finish_stage(stage,result);(D/'summary_attempt.json').write_text(result.model_dump_json(indent=2)+'\n');status='SUCCESS'
 except BaseException as exc:
  error=exc;manager.fail_stage(stage,exc);raise
 finally:
  manager.finish_run(status,error=error);manager.deactivate()
asyncio.run(main())
