"""arXiv 检索、全文与元数据工具实现。"""

from __future__ import annotations

from .adapter import (
    AdapterFactory,
    ArxivQueryAdapter,
    CompiledQuery,
    QueryAdapter,
    QueryAdapterError,
    compile_search_plan,
)
from .arxiv import ArxivFullTextTool, ArxivMetadataTool, ArxivSearchTool
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
    "QueryAdapter",
    "QueryAdapterError",
    "RendererFactory",
    "ReportRenderer",
    "ReportRenderError",
    "compile_search_plan",
    "render_report",
]
