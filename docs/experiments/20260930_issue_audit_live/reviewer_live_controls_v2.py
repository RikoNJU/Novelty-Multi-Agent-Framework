"""Six predeclared real-local-model controls on freshly retrieved public full text."""
import asyncio,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
OUT=Path(__file__).resolve().parent;DEST=OUT/'semantic-controls-v2'
from novelty_agent_framework.config import load_application_config,build_workflow
from novelty_agent_framework.config.experiment import freeze_config
from novelty_agent_framework.core.runtime_artifacts import RuntimeArtifactManager,RuntimeDebugConfig
from novelty_agent_framework.persistence import ReferenceStore
from novelty_agent_framework.schemas import Work,SourceRecord,Artifact,ReferenceManifest,NoveltyPointReviewRequest
TEXT=(OUT/'arxiv-web-fulltext-text.txt').read_text()
START=TEXT.index('The dominant sequence transduction models are based')
END=TEXT.index('1 Introduction',START)
QUOTE=TEXT[START:END].strip()
CASES=[('supported','The Transformer uses attention mechanisms without recurrence or convolution.',['supported']),('contradicted','The Transformer uses recurrent and convolutional layers as its core sequence transduction architecture.',['contradicted']),('unrelated','The Transformer has been evaluated for predicting protein subcellular localization.',['unknown'])]
DEST.mkdir(exist_ok=False)
(DEST/'plan.json').write_text(json.dumps({'source':'https://arxiv.org/html/1706.03762','source_sha256':hashlib.sha256(TEXT.encode()).hexdigest(),'source_quote':QUOTE,'repetitions':2,'cases':CASES,'max_model_calls_each':8,'allowed_providers':[],'expected_semantics_note':'A bounded feature-support control, not a scientific novelty gold standard.'},ensure_ascii=False,indent=2)+'\n')
config=load_application_config(profile_path=OUT/'live-profile.json',environ={},overrides={'reviewer':{'max_steps':4,'max_tool_calls':2,'max_total_read_chars':24000,'card_timeout_seconds':120,'summary_timeout_seconds':90,'model':{'temperature':0,'max_tokens':2048,'timeout_seconds':90}}})
(DEST/'config.json').write_text(json.dumps(freeze_config(config),ensure_ascii=False,indent=2)+'\n')
store=ReferenceStore(DEST);paper='public-attention-control';work='attention-1706';art='attention-fulltext';now=datetime.now(timezone.utc)
store.write_document(paper,work_id=work,artifact_id=art,extension='txt',content=TEXT)
store.persist_manifest(paper,ReferenceManifest(subject_paper_id=paper,updated_at=now,works=[Work(work_id=work,work_type='article',title='Attention Is All You Need')],source_records=[SourceRecord(source_record_id='arxiv-1706',work_id=work,source_id='arxiv',source_kind='structured_database',title='Attention Is All You Need',access_status='full_text_acquired',observed_at=now)],artifacts=[Artifact(artifact_id=art,work_id=work,source_record_id='arxiv-1706',role='full_text',media_type='text/plain',relative_path=f'documents/{work}/{art}.txt',sha256=hashlib.sha256(TEXT.encode()).hexdigest(),content_extent='unknown',acquired_at=now)]))
verified_read=store.read_document_slice(paper,artifact_id=art,char_start=START,max_chars=len(QUOTE))
assert verified_read.text == QUOTE
PROVENANCE={'artifact_namespace':'research_reference','read_id':verified_read.read_id,'read_char_start':START,'read_char_end':START+len(QUOTE)}
from novelty_agent_framework.agents.reviewer_checkpoint import _source_snapshot
reviewer=build_workflow(config,output_root=DEST).services.reviewer
results=[]
async def main():
 for rep in range(1,3):
  for name,claim,expected in CASES:
   trial=f'{name}-{rep}';number=str([x[0] for x in CASES].index(name)+1);point='NP-'+number;eid='ev-'+number;card='card-'+number;task='task-'+number
   request=NoveltyPointReviewRequest.model_validate({'subject_paper_id':paper,'novelty_point':{'point_id':point,'claim':claim,'technical_features':[claim]},'tasks':[{'task_id':task,'novelty_point_id':point,'task_type':'semantic_control','language':'en'}],'cards':[{'card_id':card,'task_id':task,'novelty_point_id':point,'document_title':'Attention Is All You Need','main_contribution':QUOTE,'sources':[{'title':'Attention Is All You Need','url':'https://arxiv.org/abs/1706.03762','quote':QUOTE,'location':'Abstract'}],'relevance':1,'confidence':1,'evidence_ids':[eid]}],'evidence':[{'evidence_id':eid,'work_id':work,'artifact_id':art,'novelty_point_id':point,'task_id':task,'quote':QUOTE,'interpretation':'Exact source abstract; feature relation is deliberately unassessed.','confidence':1,'locator':{'char_start':START,'char_end':START+len(QUOTE)},'provenance':PROVENANCE}]})
   _source_snapshot(request,[],DEST)
   manager=RuntimeArtifactManager(paper,run_id=trial,config=RuntimeDebugConfig(output_root=DEST,archive_root=DEST/'archive',max_model_calls=8,max_physical_provider_requests=1),runtime_config={'case':name,'repeat':rep},diagnostics=[])
   manager.activate();row={'case':name,'repeat':rep,'expected_relations':expected};results.append(row)
   try:
    stage=manager.start_stage('review_card',request);review=await reviewer.review_card(request);manager.finish_stage(stage,review)
    (DEST/(trial+'-card.json')).write_text(review.model_dump_json(indent=2)+'\n')
    cardrows=[{'index':1,'card_id':card,'novelty_point_id':point,'status':'completed','review':review.model_dump(mode='json')}]
    stage=manager.start_stage('summarize_review',{'request':request.model_dump(mode='json'),'card_reviews':cardrows})
    summary=await reviewer.summarize_with_checkpoint(request,cardrows,output_root=DEST,run_id=trial);manager.finish_stage(stage,summary)
    (DEST/(trial+'-summary.json')).write_text(summary.model_dump_json(indent=2)+'\n')
    relations=[f.relation for f in review.feature_comparisons];final=[f.relation for f in summary.review.feature_comparisons]
    row.update(card_status=review.status.value,card_incomplete_reason=review.incomplete_reason,card_relations=relations,card_matches_expected=bool(relations) and all(r in expected for r in relations),summary_status=summary.status,summary_incomplete_reason=summary.review.incomplete_reason,summary_relations=final,summary_matches_expected=bool(final) and all(r in expected for r in final),issues=[i.code for i in review.execution_issues])
    manager.finish_run('SUCCESS')
   except Exception as e:row.update(experiment_error=type(e).__name__,detail=str(e));manager.finish_run('FAILED',error=e)
   finally:
    manager.deactivate();row['model_calls']=manager._llm_call_counter
    (DEST/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print(json.dumps(row,ensure_ascii=False),flush=True)
asyncio.run(main())
