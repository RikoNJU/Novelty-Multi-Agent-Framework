"""论文处理模块：PDF → 文本 → 规整 → 章节切分 → 结构化产物。"""

from .mineru_parser import MineruError, MineruParser, MineruSettings
from .paper_processor import DefaultPaperProcessor
from .reference_bootstrap import (
    CitationMatcher,
    CitationParser,
    ReferenceBootstrapService,
    ReferenceProviderRegistry,
)
from .textify import TextifyResult, assemble_marked_text, textify

__all__ = [
    "CitationMatcher",
    "CitationParser",
    "DefaultPaperProcessor",
    "MineruError",
    "MineruParser",
    "MineruSettings",
    "ReferenceBootstrapService",
    "ReferenceProviderRegistry",
    "TextifyResult",
    "assemble_marked_text",
    "textify",
]
