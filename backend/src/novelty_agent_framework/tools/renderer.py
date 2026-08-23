"""把单篇论文的结构化查新产物确定性渲染为最终报告。"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from ..persistence import DEFAULT_OUTPUTS_DIR, paper_workspace

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
DEFAULT_MARKDOWN_TEMPLATE = TEMPLATES_DIR / "markdown" / "default.md"


class ReportRenderError(RuntimeError):
    """报告模板、输入产物或输出格式不合法。"""


class ReportRenderer(ABC):
    """报告 Renderer 的统一协议。"""

    output_suffix: str

    @abstractmethod
    def render(
        self,
        *,
        template_path: str | Path,
        paper_name: str,
        save_path: str | Path,
    ) -> Path:
        """读取 paper 工作目录并将报告写入 save_path。"""


class MarkdownRenderer(ReportRenderer):
    """使用 Mustache 风格简单占位符生成 Markdown 报告。"""

    output_suffix = ".md"

    def render(
        self,
        *,
        template_path: str | Path,
        paper_name: str,
        save_path: str | Path,
    ) -> Path:
        template = Path(template_path)
        if not template.is_file():
            raise ReportRenderError(f"Markdown 模板不存在：{template}")

        workspace = paper_workspace(paper_name)
        data = _load_workspace_data(workspace)
        context = _build_markdown_context(paper_name, data)
        rendered = _render_template(template.read_text(encoding="utf-8"), context)

        destination = Path(save_path)
        if destination.suffix.lower() != self.output_suffix:
            destination = destination.with_suffix(self.output_suffix)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered.rstrip() + "\n", encoding="utf-8")
        return destination


class RendererFactory:
    """按格式选择 Renderer，便于后续注册 LaTeX、HTML 实现。"""

    _renderers: dict[str, type[ReportRenderer]] = {
        "md": MarkdownRenderer,
        "markdown": MarkdownRenderer,
    }

    @classmethod
    def create(cls, output_format: str) -> ReportRenderer:
        normalized = output_format.strip().lower()
        renderer_type = cls._renderers.get(normalized)
        if renderer_type is None:
            supported = ", ".join(sorted(cls._renderers))
            raise ReportRenderError(
                f"不支持的报告格式：{output_format!r}；当前支持：{supported}"
            )
        return renderer_type()

    @classmethod
    def register(cls, output_format: str, renderer: type[ReportRenderer]) -> None:
        """注册后续输出格式实现。"""

        cls._renderers[output_format.strip().lower()] = renderer


def render_report(
    output_format: str = "markdown",
    template_path: str | Path | None = None,
    paper_name: str = "",
    save_path: str | Path | None = None,
) -> Path:
    """统一报告渲染入口。

    默认读取 ``outputs/<paper_name>/``，使用内置 Markdown 模板，并写入
    ``outputs/<paper_name>/report/<paper_name>-report.md``。
    """

    if not paper_name.strip():
        raise ReportRenderError("paper_name 不能为空")
    renderer = RendererFactory.create(output_format)
    workspace = paper_workspace(paper_name)
    template = Path(template_path) if template_path else _default_template(renderer)
    destination = (
        Path(save_path)
        if save_path is not None
        else workspace / "report" / f"{workspace.name}-report{renderer.output_suffix}"
    )
    return renderer.render(
        template_path=template,
        paper_name=paper_name,
        save_path=destination,
    )


def _default_template(renderer: ReportRenderer) -> Path:
    if isinstance(renderer, MarkdownRenderer):
        return DEFAULT_MARKDOWN_TEMPLATE
    raise ReportRenderError(f"{type(renderer).__name__} 未配置默认模板")


def _load_workspace_data(workspace: Path) -> dict[str, Any]:
    required = {
        "paper": workspace / "paper-input" / "others" / "paper.json",
        "points": workspace / "novelty-points.json",
        "plans": workspace / "retrieval-plans.json",
        "evidence": workspace / "evidence-cards.json",
        "report": workspace / "report.json",
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    if missing:
        raise ReportRenderError("缺少报告输入产物：" + "；".join(missing))
    try:
        return {
            name: json.loads(path.read_text(encoding="utf-8"))
            for name, path in required.items()
        }
    except (OSError, json.JSONDecodeError) as exc:
        raise ReportRenderError(f"读取报告输入产物失败：{exc}") from exc


def _build_markdown_context(
    paper_name: str,
    data: Mapping[str, Any],
) -> dict[str, str]:
    paper = data["paper"]
    points = data["points"].get("novelty_points", [])
    plans = data["plans"].get("novelty_point_plans", [])
    evidence = data["evidence"]
    report = data["report"]
    accepted = evidence.get("accepted_evidence_cards", [])
    rejected = evidence.get("rejected_evidence", [])

    point_by_id = {point.get("point_id", ""): point for point in points}
    accepted_by_point: dict[str, list[Mapping[str, Any]]] = {}
    for card in accepted:
        accepted_by_point.setdefault(card.get("novelty_point_id", ""), []).append(card)

    all_queries = _unique(
        query
        for plan in plans
        for query in plan.get("query_plan", {}).get("queries", [])
    )
    sources = _evidence_sources(accepted)
    insufficient = [
        conclusion.get("novelty_point_id", "")
        for conclusion in report.get("conclusions", [])
        if conclusion.get("level") == "insufficient"
    ]

    purpose = paper.get("abstract") or "基于论文技术内容开展公开文献检索与新颖性对比。"
    technical_summary = _technical_summary(paper, points)
    scope_terms = _unique(
        [*paper.get("keywords_zh", []), *paper.get("keywords_en", [])]
    )
    return {
        "paper_name": _cell(paper.get("title") or paper_name),
        "paper_name_en": _cell(paper.get("metadata", {}).get("title_en") or "—"),
        "generated_at": datetime.now(UTC).astimezone().isoformat(timespec="seconds"),
        "novelty_scope": "、".join(scope_terms) or "论文相关技术领域",
        "purpose": purpose,
        "technical_summary": technical_summary,
        "novelty_points": _format_points(points),
        "search_scope": "检索范围围绕各查新点的中英文表述及技术特征展开。",
        "search_sources": "\n".join(f"- {source}" for source in sources)
        or "- 未记录有效证据来源",
        "search_terms": "\n".join(f"- {term}" for term in scope_terms)
        or "- 未提供关键词",
        "search_queries": _format_query_plans(plans),
        "search_summary": (
            f"共执行 {data['plans'].get('rounds', 0)} 轮检索计划，"
            f"生成 {len(evidence.get('raw_evidence_cards', []))} 张原始证据卡；"
            f"通过 {len(accepted)} 张，拒绝 {len(rejected)} 张。"
        ),
        "evidence_list": _format_evidence(accepted),
        "evidence_coverage": _format_coverage(points, accepted_by_point),
        "coverage_gaps": "\n".join(f"- {point_id}：证据不足" for point_id in insufficient)
        or "无。",
        "novelty_conclusions": _format_conclusions(
            report.get("conclusions", []), point_by_id
        ),
        "limitations": _format_list(report.get("limitations", [])),
        "attachments": _format_attachments(report, rejected),
    }


def _render_template(template: str, context: Mapping[str, str]) -> str:
    pattern = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")
    unknown = sorted({name for name in pattern.findall(template) if name not in context})
    if unknown:
        raise ReportRenderError("模板包含未知变量：" + ", ".join(unknown))
    return pattern.sub(lambda match: context[match.group(1)], template)


def _technical_summary(paper: Mapping[str, Any], points: list[Mapping[str, Any]]) -> str:
    contributions = paper.get("claimed_contributions", [])
    if contributions:
        return "\n".join(f"- {item}" for item in contributions)
    if points:
        return "\n".join(f"- {point.get('claim', '—')}" for point in points)
    return paper.get("abstract") or "未提供。"


def _format_points(points: list[Mapping[str, Any]]) -> str:
    if not points:
        return "未生成查新点。"
    rows = ["| 序号 | 中文查新点 | 英文查新点 |", "| --- | --- | --- |"]
    for point in points:
        rows.append(
            "| {id} | {claim} | {claim_en} |".format(
                id=_cell(point.get("point_id", "—")),
                claim=_cell(point.get("claim", "—")),
                claim_en=_cell(point.get("claim_en") or "—"),
            )
        )
    return "\n".join(rows)


def _format_query_plans(plans: list[Mapping[str, Any]]) -> str:
    if not plans:
        return "未生成检索计划。"
    sections = []
    for plan in plans:
        queries = plan.get("query_plan", {}).get("queries", [])
        body = "\n".join(f"  - `{query}`" for query in queries) or "  - 无"
        sections.append(f"- **{plan.get('novelty_point_id', '未知查新点')}**\n{body}")
    return "\n".join(sections)


def _format_evidence(cards: list[Mapping[str, Any]]) -> str:
    if not cards:
        return "没有证据卡通过质量校验。"
    sections = []
    for card in cards:
        source_lines = []
        for source in card.get("sources", []):
            target = source.get("doi") or source.get("url") or source.get("location") or "—"
            source_lines.append(f"  - {source.get('title', '来源')}：{target}")
        sources = "\n".join(source_lines) or "  - 未记录"
        sections.append(
            f"### {card.get('card_id', 'Evidence')} · {card.get('document_title', '未命名文献')}\n\n"
            f"- 查新点：{card.get('novelty_point_id', '—')}\n"
            f"- 主要贡献：{card.get('main_contribution', '—')}\n"
            f"- 相关性：{card.get('relevance', 0):.2f}\n"
            f"- 置信度：{card.get('confidence', 0):.2f}\n"
            f"- 来源：\n{sources}"
        )
    return "\n\n".join(sections)


def _format_coverage(
    points: list[Mapping[str, Any]],
    accepted_by_point: Mapping[str, list[Mapping[str, Any]]],
) -> str:
    rows = ["| 查新点 | 有效证据数 | 状态 |", "| --- | ---: | --- |"]
    for point in points:
        point_id = point.get("point_id", "—")
        count = len(accepted_by_point.get(point_id, []))
        rows.append(f"| {_cell(point_id)} | {count} | {'已覆盖' if count else '未覆盖'} |")
    return "\n".join(rows) if points else "无查新点覆盖数据。"


def _format_conclusions(
    conclusions: list[Mapping[str, Any]],
    point_by_id: Mapping[str, Mapping[str, Any]],
) -> str:
    if not conclusions:
        return "未生成结构化查新结论。"
    labels = {
        "strong": "强创新",
        "partial": "部分创新",
        "weak": "弱创新",
        "insufficient": "证据不足",
    }
    sections = []
    for conclusion in conclusions:
        point_id = conclusion.get("novelty_point_id", "—")
        claim = point_by_id.get(point_id, {}).get("claim", "")
        sections.append(
            f"### {point_id} · {labels.get(conclusion.get('level'), conclusion.get('level', '—'))}\n\n"
            f"{claim}\n\n"
            f"**结论：** {conclusion.get('summary', '—')}  \n"
            f"**置信度：** {conclusion.get('confidence', 0):.2f}"
        )
    return "\n\n".join(sections)


def _format_attachments(report: Mapping[str, Any], rejected: list[Mapping[str, Any]]) -> str:
    parts = [
        ("缺失参考文献", report.get("missing_references", [])),
        ("缺失 Baseline", report.get("missing_baselines", [])),
        ("引用问题", report.get("citation_issues", [])),
        (
            "被拒绝证据",
            [f"{item.get('card_id', '—')}：{item.get('reason', '—')}" for item in rejected],
        ),
    ]
    sections = []
    for title, items in parts:
        sections.append(f"### {title}\n\n{_format_list(items)}")
    return "\n\n".join(sections)


def _format_list(items: list[Any]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "无。"


def _evidence_sources(cards: list[Mapping[str, Any]]) -> list[str]:
    sources = []
    for card in cards:
        for source in card.get("sources", []):
            url = source.get("url") or ""
            host = urlparse(url).netloc
            sources.append(host or source.get("title") or "未知来源")
    return _unique(sources)


def _unique(values: Iterable[Any]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")
