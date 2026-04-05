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
            "<html><body>"
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
            "<html><body>"
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
            "<html><body>"
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


def test_enrich_candidates_falls_back_to_pdf_for_composite_svg_figures(
    monkeypatch, tmp_path: Path
):
    paper = make_paper()
    abs_html = Path("tests/fixtures/arxiv_abs_page_with_code.html").read_text()
    svg_html = (
        "<figure>"
        '<svg><foreignObject><img src="images/preview.png" /></foreignObject></svg>'
        "<figcaption>Overview of PiJEPA.</figcaption>"
        "</figure>"
    )

    def fake_get(url: str) -> str:
        if url == paper.paper_url:
            return abs_html
        if url == arxiv_html_url(paper.paper_url):
            return svg_html
        raise AssertionError(f"unexpected fetch: {url}")

    monkeypatch.setattr(
        "paper_daily_fetch.pipeline.enrich._fetch_pdf_candidates",
        lambda **kwargs: [
            FigureSelection(url="/tmp/from-pdf.png", reason="pdf-extract:page-1")
        ],
    )

    enriched = enrich_candidates(
        [paper],
        http_get=fake_get,
        http_get_bytes=lambda url: b"%PDF-1.4",
        cache_dir=tmp_path,
    )

    assert enriched[0].figure_url_or_path == "/tmp/from-pdf.png"
    assert enriched[0].figure_reason == "pdf-extract:page-1"


def test_enrich_candidates_falls_back_to_pdf_when_html_fetch_fails(
    monkeypatch, tmp_path: Path
):
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
        lambda **kwargs: [
            FigureSelection(url="/tmp/fallback.png", reason="pdf-extract:page-2")
        ],
    )

    enriched = enrich_candidates(
        [paper],
        http_get=fake_get,
        http_get_bytes=lambda url: b"%PDF-1.4",
        cache_dir=tmp_path,
    )

    assert enriched[0].figure_url_or_path == "/tmp/fallback.png"
    assert enriched[0].figure_reason == "pdf-extract:page-2"


# === Concurrency behavior tests ===


def make_paper_with_id(arxiv_id: str) -> PaperRecord:
    return PaperRecord(
        arxiv_id=arxiv_id,
        title=f"Paper {arxiv_id}",
        authors=[],
        published_at="2026-03-28T05:00:00+00:00",
        abstract=f"Abstract for {arxiv_id}",
        paper_url=f"https://arxiv.org/abs/{arxiv_id}",
        code_url=None,
        figure_url_or_path=None,
        figure_reason=None,
        topic_matches=[],
    )


def test_enrich_candidates_preserves_order_when_completion_is_out_of_order(monkeypatch):
    """Test that output order is stable even when tasks complete in different order."""
    import threading
    import time

    papers = [make_paper_with_id(f"2603.0000{i}v1") for i in range(5)]
    completion_order = []
    lock = threading.Lock()

    # Simulate varying completion times (reverse order)
    def fake_get(url: str) -> str:
        arxiv_id = url.split("/")[-1]
        # Paper 4 completes first, paper 0 completes last
        delay = 0.01 * int(arxiv_id[-3])  # Extract digit before 'v1'
        time.sleep(delay)
        with lock:
            completion_order.append(arxiv_id)
        return "<html></html>"

    monkeypatch.setattr(
        "paper_daily_fetch.pipeline.enrich._fetch_pdf_candidates",
        lambda **kwargs: [],
    )

    enriched = enrich_candidates(papers, http_get=fake_get, max_workers=5)

    # Output order should match input order, not completion order
    assert [p.arxiv_id for p in enriched] == [p.arxiv_id for p in papers]
    # Verify that completion was indeed out of order
    assert completion_order != [p.arxiv_id.split("/")[-1] for p in papers]


def test_enrich_candidates_single_failure_does_not_affect_others(monkeypatch):
    """Test that one paper failing doesn't prevent other papers from being enriched."""
    papers = [make_paper_with_id(f"2603.0000{i}v1") for i in range(3)]
    successful_ids = []

    def fake_get(url: str) -> str:
        arxiv_id = url.split("/")[-1]
        if "00001" in arxiv_id:  # Paper 1 fails
            raise RuntimeError("Simulated network error")
        successful_ids.append(arxiv_id)
        return "<html><a href='https://github.com/test/repo'>code</a></html>"

    monkeypatch.setattr(
        "paper_daily_fetch.pipeline.enrich._fetch_pdf_candidates",
        lambda **kwargs: [],
    )

    enriched = enrich_candidates(papers, http_get=fake_get, max_workers=3)

    # All 3 papers should be in output
    assert len(enriched) == 3
    # Paper 0 and 2 should have code_url (successful), paper 1 should be unchanged
    assert enriched[0].code_url == "https://github.com/test/repo"
    assert enriched[1].code_url is None  # Failed paper keeps original
    assert enriched[2].code_url == "https://github.com/test/repo"


def test_enrich_candidates_max_workers_zero_or_negative_is_clamped_to_one():
    """Test that invalid max_workers values are handled gracefully."""
    papers = [make_paper_with_id("2603.00001v1")]

    def fake_get(url: str) -> str:
        return "<html></html>"

    # Should not raise, max_workers should be clamped to 1
    enriched = enrich_candidates(papers, http_get=fake_get, max_workers=0)
    assert len(enriched) == 1

    enriched = enrich_candidates(papers, http_get=fake_get, max_workers=-5)
    assert len(enriched) == 1


def test_enrich_candidates_timeout_limits_timeout_aware_fetches(monkeypatch):
    """Timeout should be propagated to timeout-aware fetchers and return promptly."""
    import time

    papers = [make_paper_with_id("2603.00001v1")]
    requested_timeouts = []

    def slow_get(url: str, timeout: float | None = None) -> str:
        requested_timeouts.append(timeout)
        assert timeout is not None
        time.sleep(min(timeout, 0.01))
        raise TimeoutError("simulated timeout")

    monkeypatch.setattr(
        "paper_daily_fetch.pipeline.enrich._fetch_pdf_candidates",
        lambda **kwargs: [],
    )

    started = time.perf_counter()
    enriched = enrich_candidates(
        papers,
        http_get=slow_get,
        max_workers=1,
        timeout=0.1,
    )
    elapsed = time.perf_counter() - started

    assert len(enriched) == 1
    assert enriched[0].arxiv_id == "2603.00001v1"
    assert enriched[0].code_url is None
    assert requested_timeouts
    assert all(timeout is not None and timeout <= 0.1 for timeout in requested_timeouts)
    assert elapsed < 0.5


def test_enrich_candidates_empty_list_returns_empty():
    """Test edge case of empty input."""
    enriched = enrich_candidates([], http_get=lambda url: "<html></html>")
    assert enriched == []
