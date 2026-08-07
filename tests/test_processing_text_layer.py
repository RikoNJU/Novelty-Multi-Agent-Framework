import json

from novelty_agent_framework.processing import DefaultPaperProcessor
from novelty_agent_framework.processing.cli import main as cli_main
from novelty_agent_framework.schemas import PaperDocument, PaperInput

PDF = "examples/MF2033k6lC.pdf"
EXPECTED_TITLE = "面向大规模动态图的图神经网络优化机制研究"


def test_text_layer_full_flow():
    doc = DefaultPaperProcessor().process(PDF)

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


def test_to_paper_input_roundtrip():
    processor = DefaultPaperProcessor()
    doc = processor.process(PDF)
    compatible = processor.to_paper_input(doc)
    data = compatible.model_dump(mode="json")

    PaperInput.model_validate(data)
    assert data["paper_id"] == "MF2033k6lC"
    assert data["title"] == EXPECTED_TITLE
    assert data["metadata"]["source"] == "text_layer"
    assert data["references"]


def test_cli_writes_compatible_json_only(tmp_path):
    assert cli_main(["--input", PDF, "--output", str(tmp_path)]) == 0

    compatible = tmp_path / "MF2033k6lC.json"
    assert compatible.exists()
    assert not (tmp_path / "MF2033k6lC.document.json").exists()
    PaperInput.model_validate(json.loads(compatible.read_text(encoding="utf-8")))
