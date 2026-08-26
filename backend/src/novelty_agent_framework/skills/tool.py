"""Infrastructure tool for loading one discovered skill on demand."""

from __future__ import annotations

from pydantic import Field

from ..schemas import ResearcherToolObservation, StrictModel, TaskResearchRequest
from .registry import SkillRegistry


class LoadSkillArguments(StrictModel):
    name: str = Field(min_length=1)


class LoadSkillTool:
    name = "load_skill"
    description = "Load the full instructions for one available skill by name."
    args_schema = LoadSkillArguments

    def __init__(
        self, registry: SkillRegistry, *, max_loaded: int | None = None
    ) -> None:
        self.registry = registry
        self.max_loaded = max_loaded
        self._loaded: dict[tuple[str, str], set[str]] = {}

    async def ainvoke(
        self, arguments: LoadSkillArguments, *, scope: TaskResearchRequest
    ) -> ResearcherToolObservation:
        run_key = (scope.run_id, scope.research_task.task_id)
        loaded = self._loaded.setdefault(run_key, set())
        if arguments.name in loaded:
            return ResearcherToolObservation(
                tool_name=self.name,
                arguments=arguments.model_dump(mode="json"),
                succeeded=True,
                summary=f"skill {arguments.name!r} already loaded",
                payload={"name": arguments.name, "status": "already_loaded"},
            )
        if self.max_loaded is not None and len(loaded) >= self.max_loaded:
            raise ValueError("maximum loaded skills reached for this run")
        body = self.registry.load(arguments.name)
        loaded.add(arguments.name)
        return ResearcherToolObservation(
            tool_name=self.name,
            arguments=arguments.model_dump(mode="json"),
            succeeded=True,
            summary=f"loaded skill {arguments.name!r}",
            payload={"name": arguments.name, "status": "loaded", "content": body},
        )

    def project_model_context(
        self, observation: ResearcherToolObservation
    ) -> dict[str, object]:
        return {
            "succeeded": observation.succeeded,
            **observation.payload,
        }
