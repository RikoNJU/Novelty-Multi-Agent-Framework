from novelty_agent_framework.processing.sections import (
    SECTION_ORDER,
    listify_references,
    split_sections,
)


STANDARD_TEXT = """
# Page 1
## 摘要
这是摘要内容。

关键词：A；B

## 引言
引言内容。

## 方法
方法内容。

## 结果
结果内容。

## 讨论
讨论内容。

## 结论
结论内容。

## 参考文献
[1] 作者1. 标题1[J]. 期刊, 2020.
[2] 作者2. 标题2[M]. 出版社, 2019.
"""


def test_chain_split_all_sections():
    sections, warnings = split_sections(STANDARD_TEXT)

    assert set(SECTION_ORDER) <= set(sections)
    assert "这是摘要内容" in sections["abstract"]
    assert "关键词" not in sections["abstract"]
    assert "A；B" in sections["keywords"]
    assert "引言内容" in sections["introduction"]
    assert "参考文献" not in sections["reference"]
    assert not [w for w in warnings if "未检测到" in w]


def test_missing_section_records_warning():
    text = """
# Page 1
## 摘要
摘要内容。

## 引言
引言内容。

## 结论
结论内容。
"""
    sections, warnings = split_sections(text)

    assert "discussion" not in sections
    assert any("discussion" in warning for warning in warnings)


def test_keywords_and_introduction_same_page():
    text = """
# Page 1
## 摘要
摘要内容。
关键词：K1；K2
## 引言
引言内容。
"""
    sections, _ = split_sections(text)

    assert "K1；K2" in sections["keywords"]
    assert "引言内容" in sections["introduction"]
    assert "引言内容" not in sections["keywords"]


def test_missing_end_anchor_bounds_to_page_marker():
    text = "# Page 1\n## 摘要\n摘要内容很长。\n\n# Page 2\n其他内容。\n\n# Page 3\n更多。"
    sections, _ = split_sections(text)

    assert "摘要内容" in sections["abstract"]
    assert "其他内容" not in sections["abstract"]


def test_vertical_chinese_title_anchor():
    text = (
        "# Page 5\n南京大学研究生毕业论文中文摘要首页用纸\n"
        "毕业论文题目：示例\n摘\n要\n摘要正文内容。\n\n# Page 6\n后续。"
    )
    sections, _ = split_sections(text)

    assert "摘要正文内容" in sections["abstract"]


def test_thesis_style_chapter_conclusion():
    text = "# Page 10\n第六章 总结与展望\n总结内容。\n\n参考文献\n[1] 作者. 标题."
    sections, _ = split_sections(text)

    assert "总结内容" in sections["conclusion"]
    assert "[1] 作者. 标题." in sections["reference"]


def test_listify_references_multiline():
    refs = listify_references(
        "[1] 作者1. 标题1[J]. 期刊, 2020.\n续行内容。\n[2] 作者2. 标题2."
    )

    assert refs == [
        "[1] 作者1. 标题1[J]. 期刊, 2020. 续行内容。",
        "[2] 作者2. 标题2.",
    ]
