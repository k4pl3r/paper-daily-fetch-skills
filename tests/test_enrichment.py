from pathlib import Path

from paper_daily_fetch.enrichment import enrich_links
from paper_daily_fetch.models import PaperRecord


def make_paper() -> PaperRecord:
    return PaperRecord(
        arxiv_id="2603.00001v1",
        title="DreamWM: World Models for Controllable Video Generation",
        authors=["Carol Example"],
        published_at="2026-03-28T05:00:00+00:00",
        abstract="A world model improves controllable video generation quality.",
        paper_url="https://arxiv.org/abs/2603.00001v1",
        code_url=None,
        figure_url_or_path=None,
        figure_reason=None,
        topic_matches=["video generation", "world model"],
    )


def test_enrich_links_prefers_arxiv_page_code_link():
    html = Path("tests/fixtures/arxiv_page_with_code_and_figures.html").read_text()

    enriched = enrich_links(
        make_paper(),
        arxiv_html=html,
        pwc_search_html=None,
        pwc_paper_html=None,
    )

    assert enriched.code_url == "https://github.com/example/dreamwm"


def test_enrich_links_falls_back_to_paperswithcode():
    search_html = Path("tests/fixtures/paperswithcode_search.html").read_text()
    paper_html = Path("tests/fixtures/paperswithcode_paper.html").read_text()

    enriched = enrich_links(
        make_paper(),
        arxiv_html=Path("tests/fixtures/arxiv_page_without_code.html").read_text(),
        pwc_search_html=search_html,
        pwc_paper_html=paper_html,
    )

    assert enriched.code_url == "https://github.com/pwc/dreamwm-official"

