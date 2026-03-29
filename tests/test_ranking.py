from datetime import datetime, timezone
from pathlib import Path

from paper_daily_fetch.discovery import parse_arxiv_feed
from paper_daily_fetch.ranking import rank_papers


def test_rank_papers_prefers_phrase_hits_then_recency():
    xml_text = Path("tests/fixtures/collect_feed.xml").read_text()
    papers = parse_arxiv_feed(xml_text)

    ranked = rank_papers(
        papers,
        keywords=["video generation", "world model", "3dgs reconstruction"],
        limit=3,
        now=datetime(2026, 3, 29, 12, 0, tzinfo=timezone.utc),
    )

    assert [paper.arxiv_id for paper in ranked] == [
        "2603.00004v1",
        "2603.00001v1",
        "2603.00002v1",
    ]
    assert ranked[0].topic_matches == ["video generation", "world model"]

