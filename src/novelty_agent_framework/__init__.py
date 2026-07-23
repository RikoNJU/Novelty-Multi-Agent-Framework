"""论文查新总分总工作流。"""

from .schemas import PaperInput
from .workflow import NoveltyWorkflow, NoveltyWorkflowConfig, NoveltyWorkflowServices

__all__ = [
    "NoveltyWorkflow",
    "NoveltyWorkflowConfig",
    "NoveltyWorkflowServices",
    "PaperInput",
]
