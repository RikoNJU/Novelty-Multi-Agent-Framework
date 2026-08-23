import pytest

from novelty_agent_framework.processing.sections import (
    SECTION_ORDER,
    extract_keywords_en,
    listify_references,
    parse_keywords_zh,
    split_sections,
)


STANDARD_TEXT = """
# Page 1
## 摘要
这是摘要内容。

关键词：A；B

## 英文摘要
Abstract
English abstract content.
Keywords: alpha, beta

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
    assert "English abstract content." in sections["english_abstract"]
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


BILINGUAL_TEXT = """
# Page 1
## 摘要
这是中文摘要内容。

关键词：图表示学习；深度学习；图神经网络；分布式技术

# Page 2
南京大学研究生毕业论文英文摘要首页用纸
Abstract
This is the English abstract about graph representation learning.
keywords: graph representation learning,deep learning,graph neural network, distributed

# Page 3
目
录
中文摘要· · · · · · · · · · · · · · · · · · · · 1
第一章 绪论 · · · · · · · · · · · · · · · · · · · 5

# Page 4
第一章 绪论
绪论内容。
"""


def test_bilingual_sections_split():
    sections, warnings = split_sections(BILINGUAL_TEXT)

    assert "这是中文摘要内容" in sections["abstract"]
    assert "图表示学习；深度学习" in sections["keywords"]
    assert "This is the English abstract" in sections["english_abstract"]
    assert "中文摘要· · · ·" not in sections["english_abstract"]  # 目录被截断在外
    assert "绪论内容" in sections["introduction"]
    assert not any("english_abstract" in warning for warning in warnings)


def test_english_only_paper_keeps_abstract_section():
    text = "# Page 1\nAbstract\nEnglish abstract body.\n\nKeywords: A, B\n\nIntroduction\nBody."

    sections, _ = split_sections(text)

    assert "English abstract body." in sections["abstract"]
    assert "english_abstract" not in sections


@pytest.mark.parametrize(
    "keywords_line",
    [
        "Keywords: A, B, C",
        "keywords: A, B, C",
        "KEY WORDS: A, B, C",
        "Key words: A, B, C",
        "Keywords：A，B，C",
    ],
)
def test_extract_keywords_en_variants(keywords_line):
    text = f"Abstract\nSome English text.\n{keywords_line}\n"

    assert extract_keywords_en(text) == ["A", "B", "C"]


def test_extract_keywords_en_missing_returns_empty():
    assert extract_keywords_en("Abstract\nNo keywords line.\n") == []
    assert extract_keywords_en("") == []


def test_parse_keywords_zh_splits_separators():
    assert parse_keywords_zh("图表示学习；深度学习；图神经网络；分布式技术") == [
        "图表示学习",
        "深度学习",
        "图神经网络",
        "分布式技术",
    ]
    assert parse_keywords_zh("A, B, C") == ["A", "B", "C"]
    assert parse_keywords_zh("") == []
