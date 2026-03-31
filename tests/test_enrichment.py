from pathlib import Path

from paper_daily_fetch.enrichment import arxiv_html_url
from paper_daily_fetch.enrichment import enrich_links
from paper_daily_fetch.enrichment import enrich_paper_links
from paper_daily_fetch.models import FigureSelection
from paper_daily_fetch.models import PaperRecord
from paper_daily_fetch.pipeline.enrich import enrich_candidates


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


def test_enrich_links_ignores_generic_huggingface_links_without_code_context():
    enriched = enrich_links(
        make_paper(),
        arxiv_html=(
            '<html><body>'
            '<a href="https://huggingface.co/huggingface">What is Hugging Face?</a>'
            "</body></html>"
        ),
        pwc_search_html=None,
        pwc_paper_html=None,
    )

    assert enriched.code_url is None


def test_enrich_links_ignores_issue_tracker_links():
    enriched = enrich_links(
        make_paper(),
        arxiv_html=(
            '<html><body>'
            '<a href="https://github.com/arXiv/html_feedback/issues">Report HTML feedback</a>'
            "</body></html>"
        ),
        pwc_search_html=None,
        pwc_paper_html=None,
    )

    assert enriched.code_url is None


def test_enrich_links_ignores_wiki_links():
    enriched = enrich_links(
        make_paper(),
        arxiv_html=(
            '<html><body>'
            '<a href="https://github.com/brucemiller/LaTeXML/wiki/Porting-LaTeX-packages-for-LaTeXML">Porting guide</a>'
            "</body></html>"
        ),
        pwc_search_html=None,
        pwc_paper_html=None,
    )

    assert enriched.code_url is None


def test_enrich_paper_links_prefers_abs_page_before_paperswithcode():
    paper = make_paper()
    abs_html = Path("tests/fixtures/arxiv_abs_page_with_code.html").read_text()
    html_page = Path("tests/fixtures/arxiv_page_without_code.html").read_text()
    calls: list[str] = []

    def fake_get(url: str) -> str:
        calls.append(url)
        if url == paper.paper_url:
            return abs_html
        if url == arxiv_html_url(paper.paper_url):
            return html_page
        raise AssertionError(f"unexpected fetch: {url}")

    enriched = enrich_paper_links(paper, http_get=fake_get)

    assert enriched.code_url == "https://github.com/example/dreamwm"
    assert not any("paperswithcode.com" in url for url in calls)


def test_enrich_candidates_reuses_html_fetch_for_code_and_figure():
    paper = make_paper()
    abs_html = Path("tests/fixtures/arxiv_abs_page_with_code.html").read_text()
    html_page = Path("tests/fixtures/arxiv_page_with_code_and_figures.html").read_text()
    calls: list[str] = []

    def fake_get(url: str) -> str:
        calls.append(url)
        if url == paper.paper_url:
            return abs_html
        if url == arxiv_html_url(paper.paper_url):
            return html_page
        raise AssertionError(f"unexpected fetch: {url}")

    enriched = enrich_candidates([paper], http_get=fake_get)

    assert enriched[0].code_url == "https://github.com/example/dreamwm"
    assert enriched[0].figure_url_or_path == "https://arxiv.org/figures/fig2.png"
    assert enriched[0].figure_reason == "matched:overview"
    assert calls.count(arxiv_html_url(paper.paper_url)) == 1


def test_enrich_candidates_falls_back_to_pdf_for_composite_svg_figures(monkeypatch, tmp_path: Path):
    paper = make_paper()
    abs_html = Path("tests/fixtures/arxiv_abs_page_with_code.html").read_text()
    svg_html = (
        '<figure>'
        '<svg><foreignObject><img src="images/preview.png" /></foreignObject></svg>'
        '<figcaption>Overview of PiJEPA.</figcaption>'
        '</figure>'
    )

    def fake_get(url: str) -> str:
        if url == paper.paper_url:
            return abs_html
        if url == arxiv_html_url(paper.paper_url):
            return svg_html
        raise AssertionError(f"unexpected fetch: {url}")

    monkeypatch.setattr(
        "paper_daily_fetch.pipeline.enrich._fetch_pdf_candidates",
        lambda **kwargs: [FigureSelection(url="/tmp/from-pdf.png", reason="pdf-extract:page-1")],
    )

    enriched = enrich_candidates(
        [paper],
        http_get=fake_get,
        http_get_bytes=lambda url: b"%PDF-1.4",
        cache_dir=tmp_path,
    )

    assert enriched[0].figure_url_or_path == "/tmp/from-pdf.png"
    assert enriched[0].figure_reason == "pdf-extract:page-1"


def test_enrich_candidates_falls_back_to_pdf_when_html_fetch_fails(monkeypatch, tmp_path: Path):
    paper = make_paper()
    abs_html = Path("tests/fixtures/arxiv_abs_page_with_code.html").read_text()

    def fake_get(url: str) -> str:
        if url == paper.paper_url:
            return abs_html
        if url == arxiv_html_url(paper.paper_url):
            raise TimeoutError("html timed out")
        raise AssertionError(f"unexpected fetch: {url}")

    monkeypatch.setattr(
        "paper_daily_fetch.pipeline.enrich._fetch_pdf_candidates",
        lambda **kwargs: [FigureSelection(url="/tmp/fallback.png", reason="pdf-extract:page-2")],
    )

    enriched = enrich_candidates(
        [paper],
        http_get=fake_get,
        http_get_bytes=lambda url: b"%PDF-1.4",
        cache_dir=tmp_path,
    )

    assert enriched[0].figure_url_or_path == "/tmp/fallback.png"
    assert enriched[0].figure_reason == "pdf-extract:page-2"
