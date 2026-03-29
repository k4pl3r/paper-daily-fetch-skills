from pathlib import Path

from paper_daily_fetch.sources.arxiv_api import parse_arxiv_feed
from paper_daily_fetch.sources.arxiv_search import build_search_url, parse_arxiv_search_html
from paper_daily_fetch.sources.hf_daily import parse_hf_daily_html
from paper_daily_fetch.sources.hf_trending import parse_hf_trending_html


def test_parse_hf_daily_html_extracts_candidates():
    html = Path("tests/fixtures/hf_daily.html").read_text()

    candidates = parse_hf_daily_html(html)

    assert [candidate.arxiv_id for candidate in candidates] == ["2603.25745", "2603.25265"]
    assert candidates[0].source == "hf-daily"


def test_parse_hf_trending_html_extracts_candidates():
    html = Path("tests/fixtures/hf_trending.html").read_text()

    candidates = parse_hf_trending_html(html)

    assert [candidate.arxiv_id for candidate in candidates] == ["2603.25129", "2603.25745"]
    assert candidates[0].source == "hf-trending"


def test_parse_hf_daily_html_extracts_candidates_from_hydrated_props():
    html = Path("tests/fixtures/hf_daily_hydrater.html").read_text()

    candidates = parse_hf_daily_html(html)

    assert [candidate.arxiv_id for candidate in candidates] == ["2603.30001", "2603.30002"]
    assert candidates[0].authors == ["Alice Example", "Bob Example"]
    assert candidates[0].code_url == "https://github.com/example/dreamwm"


def test_parse_hf_trending_html_extracts_candidates_from_hydrated_props():
    html = Path("tests/fixtures/hf_trending_hydrater.html").read_text()

    candidates = parse_hf_trending_html(html)

    assert [candidate.arxiv_id for candidate in candidates] == ["2603.31001", "2603.31002"]
    assert candidates[0].code_url == "https://example.com/ewm"


def test_parse_arxiv_api_feed_extracts_candidates():
    xml_text = Path("tests/fixtures/collect_feed.xml").read_text()

    candidates = parse_arxiv_feed(xml_text)

    assert candidates[0].arxiv_id == "2603.00004v1"
    assert candidates[0].source == "arxiv-api"


def test_parse_arxiv_search_html_extracts_candidates():
    html = Path("tests/fixtures/arxiv_search_results.html").read_text()

    candidates = parse_arxiv_search_html(html)

    assert [candidate.arxiv_id for candidate in candidates] == ["2603.25745", "2603.25265"]
    assert candidates[1].source == "arxiv-search"


def test_build_arxiv_search_url_uses_or_phrases():
    url = build_search_url(["world model", "video prediction"], max_results=25)

    assert "%22world+model%22+OR+%22video+prediction%22" in url
    assert "size=25" in url
