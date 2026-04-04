from datetime import datetime, timezone
from urllib.error import HTTPError

from paper_daily_fetch.models import PaperRecord
from paper_daily_fetch.pipeline.discover import discover_candidates
from paper_daily_fetch.pipeline.merge import merge_candidates
from paper_daily_fetch.pipeline.rank import rank_candidates


def make_candidate(
    *,
    arxiv_id: str,
    title: str,
    abstract: str,
    source: str,
    published_at: str = "2026-03-26T00:00:00+00:00",
) -> PaperRecord:
    return PaperRecord(
        arxiv_id=arxiv_id,
        title=title,
        authors=[],
        published_at=published_at,
        abstract=abstract,
        paper_url=f"https://arxiv.org/abs/{arxiv_id}",
        code_url=None,
        figure_url_or_path=None,
        figure_reason=None,
        topic_matches=[],
        source=source,
        sources=[source],
    )


def test_discover_candidates_continues_when_one_source_hits_429():
    def api_source(**_: object) -> list[PaperRecord]:
        raise HTTPError("https://export.arxiv.org/api/query", 429, "Too Many Requests", hdrs=None, fp=None)

    def search_source(**_: object) -> list[PaperRecord]:
        return [
            make_candidate(
                arxiv_id="2603.25745",
                title="Less Gaussians, Texture More",
                abstract="4K novel view synthesis with compact gaussian primitives.",
                source="arxiv-search",
            )
        ]

    discovered = discover_candidates(
        topic_name="3dgs-reconstruction",
        keywords=["gaussian splatting"],
        days=7,
        enabled_sources=["arxiv-api", "arxiv-search"],
        source_fetchers={"arxiv-api": api_source, "arxiv-search": search_source},
    )

    assert [paper.arxiv_id for paper in discovered] == ["2603.25745"]
    assert discovered[0].sources == ["arxiv-search"]


def test_merge_candidates_deduplicates_by_arxiv_id_and_accumulates_sources():
    merged = merge_candidates(
        [
            make_candidate(
                arxiv_id="2603.25745",
                title="Less Gaussians, Texture More",
                abstract="Candidate from hf daily.",
                source="hf-daily",
            ),
            make_candidate(
                arxiv_id="2603.25745",
                title="Less Gaussians, Texture More",
                abstract="Candidate from arxiv search.",
                source="arxiv-search",
            ),
        ]
    )

    assert len(merged) == 1
    assert merged[0].sources == ["arxiv-search", "hf-daily"]


def test_rank_candidates_applies_negative_keywords_and_domain_boost():
    ranked = rank_candidates(
        papers=[
            make_candidate(
                arxiv_id="2603.25745",
                title="Less Gaussians, Texture More",
                abstract="4K novel view synthesis with gaussian splatting.",
                source="hf-daily",
            ),
            make_candidate(
                arxiv_id="2603.25265",
                title="Diffusion Benchmark",
                abstract="A benchmark for diffusion noise schedules only.",
                source="hf-trending",
            ),
        ],
        keywords=["gaussian splatting"],
        negative_keywords=["benchmark"],
        domain_boost_keywords=["4k"],
        limit=3,
        now=datetime(2026, 3, 29, 12, 0, tzinfo=timezone.utc),
    )

    assert [paper.arxiv_id for paper in ranked] == ["2603.25745"]
    assert ranked[0].score > 0
    assert "domain-boost:4k" in ranked[0].match_reason


def test_discover_candidates_respects_candidate_limit_after_merge():
    def hf_source(**_: object) -> list[PaperRecord]:
        return [
            make_candidate(
                arxiv_id="2603.30001",
                title="Newest",
                abstract="First",
                source="hf-daily",
                published_at="2026-03-29T00:00:00+00:00",
            ),
            make_candidate(
                arxiv_id="2603.30002",
                title="Second",
                abstract="Second",
                source="hf-daily",
                published_at="2026-03-28T00:00:00+00:00",
            ),
        ]

    def api_source(**_: object) -> list[PaperRecord]:
        return [
            make_candidate(
                arxiv_id="2603.30003",
                title="Third",
                abstract="Third",
                source="arxiv-api",
                published_at="2026-03-27T00:00:00+00:00",
            ),
            make_candidate(
                arxiv_id="2603.30004",
                title="Fourth",
                abstract="Fourth",
                source="arxiv-api",
                published_at="2026-03-26T00:00:00+00:00",
            ),
        ]

    discovered = discover_candidates(
        topic_name="video-generation",
        keywords=["world model"],
        days=7,
        enabled_sources=["hf-daily", "arxiv-api"],
        source_fetchers={"hf-daily": hf_source, "arxiv-api": api_source},
        candidate_limit=2,
    )

    assert [paper.arxiv_id for paper in discovered] == ["2603.30001", "2603.30002"]
