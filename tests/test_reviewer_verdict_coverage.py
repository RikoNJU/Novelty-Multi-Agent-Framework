"""Only the not_novel / complete-single-Work relation is mechanical here."""
import json
from pathlib import Path

import pytest
from novelty_agent_framework.agents.evidence_reviewer import _validate_verdict_coverage
from novelty_agent_framework.schemas import NoveltyPointReview
from test_novelty_point_reviewer import _request


def case():
    request=_request()
    request.novelty_point.technical_features=['mechanism A','mechanism B']
    review=NoveltyPointReview.model_validate({'novelty_point_id':'NP-1','status':'reviewed',
        'verdict':'not_novel','verdict_reason':'one source covers the combination','confidence':0.8,
        'feature_comparisons':[{'feature_id':fid,'work_id':'work-1','relation':'supported',
            'basis_type':'direct_statement','evidence_refs':['E-1'],'reason':'source statement'} for fid in ('F1','F2')]})
    return request,review


@pytest.mark.parametrize('mutation',['unknown','partial','contradicted','missing','empty_refs','duplicate','two_works','no_features'])
def test_not_novel_requires_one_work_complete_declared_coverage(mutation):
    request,review=case()
    if mutation=='unknown': review.feature_comparisons[1].relation='unknown'
    if mutation=='partial': review.feature_comparisons[1].relation='partially_supported'
    if mutation=='contradicted': review.feature_comparisons[1].relation='contradicted'
    if mutation=='missing': review.feature_comparisons.pop()
    if mutation=='empty_refs': review.feature_comparisons[1].evidence_refs=[]
    if mutation=='duplicate': review.feature_comparisons.append(review.feature_comparisons[1].model_copy())
    if mutation=='two_works': review.feature_comparisons[1].work_id='work-2'
    if mutation=='no_features': request.novelty_point.technical_features=[]
    before=review.model_dump(mode='json')
    result=_validate_verdict_coverage(review,request)
    assert result.status.value=='insufficient_evidence' and result.verdict is None
    assert result.incomplete_reason=='semantic_evidence'
    assert result.feature_comparisons==review.feature_comparisons
    assert review.model_dump(mode='json')==before
    assert result.execution_issues[-1].code=='review.missing_features'


def test_complete_single_work_keeps_not_novel():
    request,review=case()
    assert _validate_verdict_coverage(review,request)==review


@pytest.mark.parametrize('verdict',['novel','partially_novel'])
def test_rule_does_not_expand_to_other_verdicts_or_guess_semantics(verdict):
    request,review=case()
    review.verdict=type(review.verdict)(verdict)
    review.feature_comparisons[1].relation='unknown'
    assert _validate_verdict_coverage(review,request)==review


@pytest.mark.parametrize('sample',[1,2,3])
def test_three_frozen_real_qwen_outputs_preserve_relations_but_reject_label(sample):
    folder=Path(__file__).resolve().parents[1]/'docs/experiments/20260927_harness_config_closure/reviewer_local_fixed'
    from novelty_agent_framework.schemas import NoveltyPointReviewRequest
    request=NoveltyPointReviewRequest.model_validate_json((folder/'request.json').read_text())
    observed=json.loads((folder/f'sample-{sample}.json').read_text())
    for original in (observed['card_review'],observed['summary_attempt']['review']):
        review=NoveltyPointReview.model_validate(original)
        assert review.verdict.value=='not_novel'
        guarded=_validate_verdict_coverage(review,request)
        assert guarded.verdict is None and guarded.status.value=='insufficient_evidence'
        assert guarded.feature_comparisons==review.feature_comparisons
        assert guarded.highly_relevant_works==review.highly_relevant_works
        assert guarded.review_evidence==review.review_evidence
