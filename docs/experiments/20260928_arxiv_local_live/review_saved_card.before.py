"""Explicit, bounded fresh review of the card whose original review hit the run budget."""
import asyncio,json,shutil,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
from novelty_agent_framework.config import load_application_config
from novelty_agent_framework.config.factory import build_workflow
from novelty_agent_framework.config.experiment import prepare_startup
from novelty_agent_framework.core.runtime_artifacts import RuntimeArtifactManager,RuntimeDebugConfig
from novelty_agent_framework.schemas import NoveltyPointReviewRequest,NoveltyPoint,EvidenceCard,Evidence,ResearchTask
PAPER='MF2033k6lC';dest=OUT/'review_followup';source=OUT/'runs/0002'
if dest.exists():raise SystemExit('Refusing to overwrite reviewer followup')
dest.mkdir()
raw_rt=next((source/PAPER/'runtime').iterdir())
raw=json.loads((raw_rt/'stages/0014_review_evidence/input.json').read_text())
cards=[EvidenceCard.model_validate(c) for c in raw['validator_accepted_cards']]
assert len(cards)==1
point_id=cards[0].novelty_point_id
ids=set(cards[0].evidence_ids)
request=NoveltyPointReviewRequest(subject_paper_id=PAPER,novelty_point=next(NoveltyPoint.model_validate(p) for p in raw['novelty_points'] if p['point_id']==point_id),cards=cards,evidence=[Evidence.model_validate(e) for e in raw['raw_evidence'] if e['evidence_id'] in ids],tasks=[ResearchTask.model_validate(t) for t in raw['all_research_tasks'] if t['novelty_point_id']==point_id])
shutil.copytree(source/PAPER/'references',dest/PAPER/'references')
profile=json.loads((OUT/'web_profile.json').read_text());profile['project']['runtime_debug'].update(max_model_calls=8,max_physical_provider_requests=1,output_root=str(dest),archive_root=str(dest/'archive'))
(dest/'profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n')
config=load_application_config(profile_path=dest/'profile.json',environ={})
frozen=prepare_startup(config,entrypoint='review_saved_card',input_path=source/'paper-input.json',output_root=dest,snapshot_dir=dest/'startup',input_contents={'review-request.json':request.model_dump_json().encode()},active_roles=('reviewer',),require_reviewer=True)
reviewer=build_workflow(config,output_root=dest).services.reviewer
manager=RuntimeArtifactManager(PAPER,run_id='review-saved-card',config=RuntimeDebugConfig(enabled=True,output_root=dest,archive_root=dest/'archive',max_model_calls=8,max_physical_provider_requests=1),runtime_config=frozen['effective_config'],enabled_tools=list(reviewer.tools.names),stage_names=['review_card','summarize_review'])
async def main():
 manager.activate();status='FAILED';error=None
 try:
  stage=manager.start_stage('review_card',request)
  card=await reviewer.review_card(request)
  manager.finish_stage(stage,card)
  rows=[{'card_id':cards[0].card_id,'novelty_point_id':point_id,'status':'completed','review':card.model_dump(mode='json')}]
  (dest/'card_review.json').write_text(card.model_dump_json(indent=2)+'\n')
  stage=manager.start_stage('summarize_review',{'request':request.model_dump(mode='json'),'card_reviews':rows})
  summary=await reviewer.summarize_with_checkpoint(request,rows,output_root=dest,run_id='review-saved-card')
  manager.finish_stage(stage,summary)
  (dest/'summary_attempt.json').write_text(summary.model_dump_json(indent=2)+'\n');status='SUCCESS'
 except BaseException as exc:
  error=exc
  manager.fail_stage(stage,exc)
  raise
 finally:
  manager.finish_run(status,error=error);manager.deactivate()
asyncio.run(main())
