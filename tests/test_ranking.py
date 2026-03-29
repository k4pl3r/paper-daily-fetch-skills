from datetime import datetime, timezone
from pathlib import Path

from paper_daily_fetch.pipeline.rank import rank_candidates
from paper_daily_fetch.sources.arxiv_api import parse_arxiv_feed


def test_rank_candidates_prefers_phrase_hits_then_recency():
    xml_text = Path("tests/fixtures/collect_feed.xml").read_text()
    papers = parse_arxiv_feed(xml_text)

    ranked = rank_candidates(
        papers,
        keywords=["video generation", "world model", "3dgs reconstruction"],
        negative_keywords=[],
        domain_boost_keywords=[],
        limit=3,
        now=datetime(2026, 3, 29, 12, 0, tzinfo=timezone.utc),
    )

    assert [paper.arxiv_id for paper in ranked] == [
        "2603.00004v1",
        "2603.00001v1",
        "2603.00002v1",
    ]
    assert ranked[0].topic_matches == ["video generation", "world model"]
