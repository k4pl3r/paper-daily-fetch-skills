from paper_daily_fetch.models import PaperRecord
from paper_daily_fetch.pipeline.annotate import apply_annotations


def make_paper() -> PaperRecord:
    return PaperRecord(
        arxiv_id="2603.00001v1",
        title="DreamWM",
        authors=["Carol Example"],
        published_at="2026-03-28T05:00:00+00:00",
        abstract="A world model improves controllable video generation quality.",
        paper_url="https://arxiv.org/abs/2603.00001v1",
        code_url=None,
        figure_url_or_path=None,
        figure_reason=None,
        topic_matches=["video generation"],
    )


def test_apply_annotations_merges_translation_and_takes():
    annotated = apply_annotations(
        [make_paper()],
        [
            {
                "arxiv_id": "2603.00001v1",
                "summary_zh": "一段完整中文翻译。",
                "positive_take": "一句话正面贡献。",
                "critical_take": "一句话负面锐评。",
            }
        ],
    )

    assert annotated[0].summary_zh == "一段完整中文翻译。"
    assert annotated[0].positive_take == "一句话正面贡献。"
    assert annotated[0].critical_take == "一句话负面锐评。"


def test_apply_annotations_ignores_unknown_arxiv_ids():
    annotated = apply_annotations(
        [make_paper()],
        [{"arxiv_id": "9999.00001", "summary_zh": "不会生效"}],
    )

    assert annotated[0].summary_zh is None
