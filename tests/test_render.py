import json

from paper_daily_fetch.models import PaperRecord
from paper_daily_fetch.render import render_markdown, render_openclaw_payload


def make_paper() -> PaperRecord:
    return PaperRecord(
        arxiv_id="2603.00001v1",
        title="DreamWM: World Models for Controllable Video Generation",
        authors=["Carol Example"],
        published_at="2026-03-28T05:00:00+00:00",
        abstract="A world model improves controllable video generation quality.",
        summary_zh="这篇论文提出 DreamWM，用世界模型提升可控视频生成的时序一致性和可编辑性。",
        positive_take="把世界模型显式引入视频生成链路，重点解决长程时序控制不稳的问题。",
        critical_take="本质上仍然依赖较重的视频生成骨架，收益可能更像强工程整合而不是范式级突破。",
        paper_url="https://arxiv.org/abs/2603.00001v1",
        code_url="https://github.com/example/dreamwm",
        figure_url_or_path="https://arxiv.org/figures/fig2.png",
        figure_reason="matched:overview",
        topic_matches=["video generation", "world model"],
    )


def test_render_openclaw_payload_has_target_and_message():
    payload = render_openclaw_payload(
        papers=[make_paper()],
        target_chat="group-42",
        topic_name="video-generation",
    )

    assert payload["target_chat"] == "group-42"
    assert "DreamWM" in payload["message"]
    assert "代码" in payload["message"]
    assert "贡献" in payload["message"]
    assert "锐评" in payload["message"]


def test_render_markdown_snapshot():
    markdown = render_markdown(
        papers=[make_paper()],
        topic_name="video-generation",
        generated_at="2026-03-29T12:00:00+00:00",
    )

    assert markdown == (
        "# 每日论文速递：video-generation\n\n"
        "- 生成时间：2026-03-29T12:00:00+00:00\n"
        "- 论文数量：1\n\n"
        "## DreamWM: World Models for Controllable Video Generation\n\n"
        "- arXiv ID：2603.00001v1\n"
        "- 作者：Carol Example\n"
        "- 发布时间：2026-03-28T05:00:00+00:00\n"
        "- 匹配主题：video generation, world model\n"
        "- 论文链接：[https://arxiv.org/abs/2603.00001v1](https://arxiv.org/abs/2603.00001v1)\n"
        "- 代码链接：[https://github.com/example/dreamwm](https://github.com/example/dreamwm)\n"
        "- 配图：![DreamWM: World Models for Controllable Video Generation](https://arxiv.org/figures/fig2.png)\n"
        "- 配图说明：matched:overview\n\n"
        "### 中文摘要\n\n"
        "这篇论文提出 DreamWM，用世界模型提升可控视频生成的时序一致性和可编辑性。\n\n"
        "### 一句话总结贡献（正面）\n\n"
        "把世界模型显式引入视频生成链路，重点解决长程时序控制不稳的问题。\n\n"
        "### 毒舌锐评和其他方法的差异与不足（负面）\n\n"
        "本质上仍然依赖较重的视频生成骨架，收益可能更像强工程整合而不是范式级突破。\n"
    )
