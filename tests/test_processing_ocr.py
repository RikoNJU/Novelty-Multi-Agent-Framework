import pymupdf

from backend.env import ModelResponse
from novelty_agent_framework.processing import DefaultPaperProcessor
from novelty_agent_framework.processing.normalize import normalize_ocr_text


class FakeOcrClient:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []

    def complete(self, messages, *, options=None):
        self.calls.append(messages)
        content = self.outputs[min(len(self.calls) - 1, len(self.outputs) - 1)]
        return ModelResponse(content=content)


def make_two_page_pdf(tmp_path):
    doc = pymupdf.open()
    doc.new_page().insert_text((72, 72), "Page one body")
    doc.new_page().insert_text((72, 72), "Page two body")
    path = tmp_path / "sample.pdf"
    doc.save(path)
    doc.close()
    return path


PAGE1 = (
    "## 摘要\n摘要内容。<|ref|x<|/ref|>带标记<|det|>[[1,2,3,4]]<|/det|>\n"
    "关键词：A；B\n## 引言\n引言内容。"
)
PAGE2 = "## 结论\n结论内容。\n参考文献\n[1] 作者1. 标题1.\n[2] 作者2. 标题2."


def test_ocr_path_full_flow(tmp_path):
    pdf = make_two_page_pdf(tmp_path)
    client = FakeOcrClient([PAGE1, PAGE2])
    doc = DefaultPaperProcessor(ocr_client=client).process(pdf, force_ocr=True)

    assert doc.source == "ocr"
    assert len(doc.pages) == 2
    assert "摘要内容" in doc.abstract
    assert "<|ref|>" not in doc.abstract
    assert "A；B" in doc.sections["keywords"]
    assert "引言内容" in doc.sections["introduction"]
    assert "结论内容" in doc.sections["conclusion"]
    assert doc.references == ["[1] 作者1. 标题1.", "[2] 作者2. 标题2."]
    assert client.calls


def test_normalize_ocr_strips_markers():
    cleaned = normalize_ocr_text(
        "文本<|ref|>sub_title<|/ref|><|det|>[[445, 309, 552, 333]]<|/det|>正常。"
    )

    assert "<|ref|>" not in cleaned
    assert "<|det|>" not in cleaned
    assert "正常" in cleaned
