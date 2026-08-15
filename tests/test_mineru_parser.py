"""MinerU 适配器与兜底链路测试（不依赖真实 mineru 环境）。"""

from __future__ import annotations

import json

import pymupdf

from novelty_agent_framework.processing.mineru_parser import (
    MineruError,
    MineruParser,
    MineruSettings,
    _pages_from_v1,
    _pages_from_v2,
    _structured_from_v1,
    _structured_from_v2,
)
from novelty_agent_framework.processing.paper_processor import DefaultPaperProcessor
from novelty_agent_framework.processing.textify import TextifyResult
from novelty_agent_framework.schemas import (
    PaperEquation,
    PaperImage,
    PaperPage,
    PaperTable,
)


class ThrowingMineruParser:
    def parse(self, source, *, paper_id=None):
        raise MineruError("mineru not available")


def test_pages_from_v2_groups_by_page():
    data = [
        [
            {
                "type": "title",
                "content": {
                    "level": 1,
                    "title_content": [{"type": "text", "content": "Introduction"}],
                },
            }
        ],
        [
            {
                "type": "paragraph",
                "content": {
                    "paragraph_content": [{"type": "text", "content": "Body text"}]
                },
            }
        ],
    ]
    pages = _pages_from_v2(data)
    assert len(pages) == 2
    assert pages[0].page == 1
    assert pages[0].text == "# Introduction"
    assert pages[1].page == 2
    assert pages[1].text == "Body text"


def test_pages_from_v2_renders_list_item_content():
    data = [
        [
            {
                "type": "list",
                "content": {
                    "list_items": [
                        {
                            "item_type": "text",
                            "item_content": [{"type": "text", "content": "Abstract"}],
                        },
                        {
                            "item_type": "text",
                            "item_content": [
                                {"type": "text", "content": "Body content"}
                            ],
                        },
                    ]
                },
            }
        ]
    ]
    pages = _pages_from_v2(data)
    assert pages[0].text == "- Abstract\n- Body content"


def test_pages_from_v1_groups_by_page_idx():
    data = [
        {"type": "text", "text": "First", "page_idx": 0},
        {"type": "text", "text": "Second", "page_idx": 1},
        {"type": "page_footer", "text": "skip me", "page_idx": 0},
    ]
    pages = _pages_from_v1(data)
    assert len(pages) == 2
    assert pages[0].text == "First"
    assert pages[1].text == "Second"


def test_structured_from_v2_extracts_image_table_equation():
    data = [
        [
            {
                "type": "image",
                "content": {
                    "image_source": {"path": "images/abc.jpg"},
                    "image_caption": [{"type": "text", "content": "Figure 1"}],
                },
                "bbox": [1, 2, 3, 4],
            },
            {
                "type": "table",
                "content": {
                    "table_caption": [{"type": "text", "content": "Table 1"}],
                    "table_body": "<table><tr><td>a</td></tr></table>",
                },
                "bbox": [5, 6, 7, 8],
            },
            {
                "type": "equation_interline",
                "content": {
                    "math_content": [{"type": "text", "content": "x = y"}]
                },
                "bbox": [9, 10, 11, 12],
            },
        ]
    ]
    images, tables, equations = _structured_from_v2(data)
    assert len(images) == 1
    assert isinstance(images[0], PaperImage)
    assert images[0].kind == "image"
    assert images[0].path == "images/abc.jpg"
    assert images[0].caption == "Figure 1"
    assert images[0].bbox == [1.0, 2.0, 3.0, 4.0]

    assert len(tables) == 1
    assert isinstance(tables[0], PaperTable)
    assert tables[0].body.startswith("<table>")
    assert tables[0].body_format == "html"

    assert len(equations) == 1
    assert isinstance(equations[0], PaperEquation)
    assert equations[0].latex == "x = y"


def test_structured_from_v1_extracts_image_table_equation():
    data = [
        {
            "type": "image",
            "img_path": "images/a.png",
            "image_caption": ["Figure 1"],
            "page_idx": 0,
        },
        {
            "type": "table",
            "table_body": "<table><tr><td>b</td></tr></table>",
            "table_caption": ["Table 1"],
            "page_idx": 1,
        },
        {
            "type": "equation",
            "text": "a^2 + b^2 = c^2",
            "page_idx": 1,
        },
    ]
    images, tables, equations = _structured_from_v1(data)
    assert images[0].page == 1
    assert images[0].path == "images/a.png"
    assert tables[0].page == 2
    assert tables[0].body.startswith("<table>")
    assert equations[0].page == 2
    assert equations[0].latex == "a^2 + b^2 = c^2"


def test_to_textify_result_reads_v2(tmp_path):
    parse_dir = tmp_path / "parse"
    parse_dir.mkdir()
    content_list_v2 = parse_dir / "paper_content_list_v2.json"
    content_list_v2.write_text(
        json.dumps(
            [
                [
                    {
                        "type": "paragraph",
                        "content": {
                            "paragraph_content": [{"type": "text", "content": "Hello"}]
                        },
                    }
                ]
            ]
        ),
        encoding="utf-8",
    )
    manifest = {
        "ok": True,
        "content_list_v2": str(content_list_v2),
        "content_list": str(parse_dir / "missing.json"),
    }
    parser = MineruParser()
    result = parser._to_textify_result(manifest, tmp_path / "paper.pdf")
    assert result.source == "mineru"
    assert result.pages[0].text == "Hello"


def test_to_textify_result_includes_structured_blocks(tmp_path):
    parse_dir = tmp_path / "parse"
    parse_dir.mkdir()
    content_list_v2 = parse_dir / "paper_content_list_v2.json"
    content_list_v2.write_text(
        json.dumps(
            [
                [
                    {
                        "type": "image",
                        "content": {
                            "image_path": "images/abc.jpg",
                            "image_caption": [{"type": "text", "content": "Figure"}],
                        },
                    },
                    {
                        "type": "table",
                        "content": {
                            "table_body": "<table><tr><td>x</td></tr></table>"
                        },
                    },
                    {
                        "type": "equation_interline",
                        "content": {
                            "math_content": [{"type": "text", "content": "E=mc^2"}]
                        },
                    },
                ]
            ]
        ),
        encoding="utf-8",
    )
    manifest = {
        "ok": True,
        "content_list_v2": str(content_list_v2),
        "content_list": str(parse_dir / "missing.json"),
    }
    result = MineruParser()._to_textify_result(manifest, tmp_path / "paper.pdf")
    assert len(result.images) == 1
    assert result.images[0].path == "images/abc.jpg"
    assert len(result.tables) == 1
    assert result.tables[0].body.startswith("<table>")
    assert len(result.equations) == 1
    assert result.equations[0].latex == "E=mc^2"


def test_to_textify_result_missing_content_list_raises(tmp_path):
    manifest = {"ok": True}
    parser = MineruParser()
    try:
        parser._to_textify_result(manifest, tmp_path / "paper.pdf")
    except MineruError as exc:
        assert "content_list" in str(exc)
    else:
        raise AssertionError("expected MineruError")


def test_build_command_uses_explicit_python(tmp_path):
    python = tmp_path / "python.exe"
    python.write_text("", encoding="utf-8")
    settings = MineruSettings(python_path=str(python), worker_path="scripts/mineru_worker.py")
    parser = MineruParser(settings)
    command = parser._build_command(
        tmp_path / "input.pdf",
        tmp_path / "work",
        tmp_path / "manifest.json",
    )
    assert command[0] == str(python)
    assert any("mineru_worker.py" in str(part) for part in command)


def _make_pdf_with_text(tmp_path, pages_texts):
    doc = pymupdf.open()
    for text in pages_texts:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    path = tmp_path / "sample.pdf"
    doc.save(path)
    doc.close()
    return path


def test_mineru_failure_falls_back_to_text_layer(tmp_path):
    pdf = _make_pdf_with_text(
        tmp_path,
        [
            "Abstract\nAbstract content is long enough to pass the text layer gate.\nKeywords: A; B",
            "Introduction\nIntro content.",
        ],
    )
    processor = DefaultPaperProcessor(
        parser="mineru",
        mineru_parser=ThrowingMineruParser(),
        min_chars_per_page=10,
    )
    doc = processor.process(pdf)
    assert doc.source == "text_layer"
    assert any("mineru" in warning for warning in doc.parse_warnings)
    assert "Abstract content" in doc.abstract


def test_mineru_structured_blocks_flow_into_document_and_input(tmp_path):
    class StructuredMineruParser:
        def parse(self, source, *, paper_id=None):
            return TextifyResult(
                pages=(
                    PaperPage(
                        page=1,
                        text="## Abstract\nAbstract content.",
                    ),
                ),
                source="mineru",
                warnings=(),
                images=(PaperImage(image_id="image-1-1", kind="image", page=1, path="images/a.jpg"),),
                tables=(PaperTable(table_id="table-1-1", page=1, body="<table></table>"),),
                equations=(PaperEquation(equation_id="equation-1-1", page=1, latex="x=1"),),
            )

    pdf = _make_pdf_with_text(
        tmp_path,
        [
            "Abstract\nAbstract content is long enough to pass the text layer gate.\nKeywords: A; B",
        ],
    )
    processor = DefaultPaperProcessor(
        parser="mineru",
        mineru_parser=StructuredMineruParser(),
        min_chars_per_page=1,
    )
    doc = processor.process(pdf)
    assert doc.source == "mineru"
    assert len(doc.images) == 1
    assert doc.images[0].path == "images/a.jpg"
    assert len(doc.tables) == 1
    assert doc.tables[0].body == "<table></table>"
    assert len(doc.equations) == 1
    assert doc.equations[0].latex == "x=1"

    paper_input = processor.to_paper_input(doc)
    assert len(paper_input.images) == 1
    assert len(paper_input.tables) == 1
    assert len(paper_input.equations) == 1


def test_mineru_quality_fail_falls_back_to_text_layer(tmp_path):
    class EmptyMineruParser:
        def parse(self, source, *, paper_id=None):
            return TextifyResult(pages=(), source="mineru", warnings=())

    pdf = _make_pdf_with_text(
        tmp_path,
        [
            "Abstract\nAbstract content is long enough to pass the text layer gate.\nKeywords: A; B",
            "Introduction\nIntro content.",
        ],
    )
    processor = DefaultPaperProcessor(
        parser="mineru",
        mineru_parser=EmptyMineruParser(),
        min_chars_per_page=10,
    )
    doc = processor.process(pdf)
    assert doc.source == "text_layer"
    assert any("质量不足" in warning for warning in doc.parse_warnings)
