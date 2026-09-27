"""Offline comparison of the former unregistered-tool normalization failure."""
import asyncio,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'backend/src'),str(ROOT/'tests')]
from backend.env import ModelResponse,ModelToolCall
from novelty_agent_framework.tools import ResearcherToolRegistry
from novelty_agent_framework.workflows import TaskResearcherWorkflow
from test_task_researcher_workflow import FakeModel,FakeBuilder,scope,finish
class FormerFailureProjection(ResearcherToolRegistry):
    def project_model_context(self,tool_name,observation):
        if not observation.succeeded:
            self.get(tool_name) # Exact former lookup boundary, before failure projection.
        return super().project_model_context(tool_name,observation)
def run(registry):
    model=FakeModel([ModelResponse(content=None,tool_calls=(ModelToolCall('bad','unregistered',{}),)),finish()])
    result=asyncio.run(TaskResearcherWorkflow(model,registry,FakeBuilder()).ainvoke(scope()))
    return {'status':result.status.value,'fixture_model_calls':len(model.messages),
        'failure_codes':[f.code.value for f in result.execution_failures], 'cards':len(result.evidence_cards)}
result={'type':'offline same-input boundary replay, not an old complete source checkout',
        'former_failure_projection':run(FormerFailureProjection()),'current_projection':run(ResearcherToolRegistry()),
        'real_model_or_network_calls':0}
Path(__file__).with_name('tool_choice_before_after.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
