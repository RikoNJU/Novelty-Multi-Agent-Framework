"""论文处理模块：PDF → 文本 → 规整 → 章节切分 → 结构化产物。"""

from .paper_processor import DefaultPaperProcessor
from .textify import TextifyResult, assemble_marked_text, textify

__all__ = [
    "DefaultPaperProcessor",
    "TextifyResult",
    "assemble_marked_text",
    "textify",
]
