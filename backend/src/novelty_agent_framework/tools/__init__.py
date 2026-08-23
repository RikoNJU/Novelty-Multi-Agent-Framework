"""arXiv 检索、全文与元数据工具实现。"""

from __future__ import annotations

from .adapter import (
    AdapterFactory,
    CompiledQuery,
    QueryAdapter,
    QueryAdapterError,
    compile_search_plan,
)
from .null_catalog import NullQueryAdapter, NullSearchTool, build_null_catalog_source
from .legacy_researcher_tools import StructuredRetrievalResearcherTool
from .retrieval_sources import RetrievalSource, RetrievalSourceRegistry
from .reference_reader import ReferenceArtifactReaderTool
from .reader import ReaderTool, ReferenceReaderResearcherTool
from .researcher_registry import (
    ResearcherTool,
    ResearcherToolRegistry,
)
from .structured_retrieval import (
    StructuredRetrievalAdapter,
    StructuredSourceRetrievalTool,
)
from .renderer import (
    MarkdownRenderer,
    RendererFactory,
    ReportRenderer,
    ReportRenderError,
    render_report,
)

__all__ = [
    "AdapterFactory",
    "ArxivFullTextTool",
    "ArxivMetadataTool",
    "ArxivQueryAdapter",
    "ArxivSearchTool",
    "CompiledQuery",
    "MarkdownRenderer",
    "NullQueryAdapter",
    "NullSearchTool",
    "QueryAdapter",
    "QueryAdapterError",
    "RetrievalSource",
    "RetrievalSourceRegistry",
    "ReferenceArtifactReaderTool",
    "ReaderTool",
    "ReferenceReaderResearcherTool",
    "ResearcherTool",
    "ResearcherToolRegistry",
    "StructuredRetrievalResearcherTool",
    "StructuredSourceRetrievalTool",
    "StructuredRetrievalAdapter",
    "RendererFactory",
    "ReportRenderer",
    "ReportRenderError",
    "compile_search_plan",
    "build_arxiv_source",
    "build_null_catalog_source",
    "render_report",
]

# Null Object 随核心安装；arXiv 具体实现则按需延迟导入。
AdapterFactory.register("null_catalog", NullQueryAdapter)


def __getattr__(name: str):
    """延迟暴露 arXiv 兼容 API，避免通用包导入时绑定具体来源。"""

    arxiv_names = {
        "ArxivFullTextTool",
        "ArxivMetadataTool",
        "ArxivQueryAdapter",
        "ArxivSearchTool",
        "build_arxiv_source",
    }
    if name not in arxiv_names:
        raise AttributeError(name)
    from . import arxiv

    value = getattr(arxiv, name)
    if name == "ArxivQueryAdapter":
        AdapterFactory.register("arxiv", value)
    globals()[name] = value
    return value
