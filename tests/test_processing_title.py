from novelty_agent_framework.processing.title import extract_title_from_lines


def test_title_joins_consecutive_lines():
    candidates = [
        "南京大学研究生毕业论文中文摘要首页用纸",
        "毕业论文题目：",
        "面向大规模动态图的",
        "图神经网络优化机制研究",
        "专业2020级硕士生姓名：",
    ]

    assert (
        extract_title_from_lines(candidates)
        == "面向大规模动态图的图神经网络优化机制研究"
    )


def test_title_skips_template_and_short_lines():
    assert extract_title_from_lines(["研究生毕业论文", "面向大规模动态图"]) == "面向大规模动态图"
    assert extract_title_from_lines(["摘要", "面向大规模动态图"]) == "面向大规模动态图"
    assert extract_title_from_lines(["****", "面向大规模动态图"]) == "面向大规模动态图"


def test_title_none_when_no_acceptable_line():
    assert extract_title_from_lines(["研究生毕业论文", "****", ""]) is None
