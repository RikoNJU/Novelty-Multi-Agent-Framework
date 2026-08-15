import json

import pytest
from pydantic import ValidationError

from novelty_agent_framework.processing import DefaultPaperProcessor
from novelty_agent_framework.processing.cli import main as cli_main
from novelty_agent_framework.schemas import PaperDocument, PaperInput

PDF = "examples/MF2033k6lC.pdf"
EXPECTED_TITLE = "面向大规模动态图的图神经网络优化机制研究"


def test_text_layer_full_flow():
    doc = DefaultPaperProcessor(parser="text_layer").process(PDF)

    assert doc.source == "text_layer"
    assert doc.paper_id == "MF2033k6lC"
    assert doc.title == EXPECTED_TITLE
    assert "GSAERU" in doc.abstract
    assert "图表示学习" in doc.sections.get("keywords", "")
    assert doc.references
    assert len(doc.references) >= 80
    assert len(doc.pages) == 90
    assert "面向大规模动态图" in doc.full_text
    PaperDocument.model_validate(doc.model_dump(mode="json"))


def test_english_abstract_and_keywords_structured():
    doc = DefaultPaperProcessor(parser="text_layer").process(PDF)

    assert "graph representation learning" in doc.english_abstract
    assert doc.keywords_zh == ["图表示学习", "深度学习", "图神经网络", "分布式技术"]
    assert doc.keywords_en == [
        "graph representation learning",
        "deep learning",
        "graph neural network",
        "distributed",
    ]


def test_to_paper_input_roundtrip():
    processor = DefaultPaperProcessor(parser="text_layer")
    doc = processor.process(PDF)
    compatible = processor.to_paper_input(doc)
    data = compatible.model_dump(mode="json")

    PaperInput.model_validate(data)
    assert data["paper_id"] == "MF2033k6lC"
    assert data["title"] == EXPECTED_TITLE
    assert data["english_abstract"]
    assert data["keywords_zh"]
    assert data["keywords_en"]
    assert data["metadata"]["source"] == "text_layer"
    assert data["references"]


def test_paper_input_backward_and_forward_compatible():
    old_shape = {
        "paper_id": "p",
        "title": "t",
        "abstract": "a",
        "full_text": "f",
    }
    loaded_old = PaperInput.model_validate(old_shape)

    assert loaded_old.english_abstract == ""
    assert loaded_old.keywords_zh == []
    assert loaded_old.keywords_en == []

    new_shape = {
        "paper_id": "p",
        "title": "t",
        "abstract": "a",
        "english_abstract": "ea",
        "full_text": "f",
        "keywords_zh": ["k1"],
        "keywords_en": ["k1-en"],
    }
    loaded_new = PaperInput.model_validate(new_shape)

    assert loaded_new.english_abstract == "ea"
    assert loaded_new.keywords_zh == ["k1"]
    assert loaded_new.keywords_en == ["k1-en"]

    with pytest.raises(ValidationError):
        PaperInput.model_validate({**new_shape, "unknown": 1})


def test_cli_writes_paper_workspace(tmp_path):
    assert cli_main(["--input", PDF, "--output", str(tmp_path), "--parser", "text_layer"]) == 0

    workspace = tmp_path / "MF2033k6lC"
    compatible = workspace / "paper-input" / "others" / "paper.json"
    assert compatible.exists()
    assert (workspace / "paper-input" / "full.md").exists()
    assert (workspace / "paper-input" / "content-list.json").exists()
    assert (workspace / "paper-input" / "images").is_dir()
    assert (workspace / "report").is_dir()
    PaperInput.model_validate(json.loads(compatible.read_text(encoding="utf-8")))
