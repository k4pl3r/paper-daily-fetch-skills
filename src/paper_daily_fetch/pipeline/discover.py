from __future__ import annotations

from datetime import datetime, timezone
import sys
from typing import Callable

from ..infra.http import HttpClient
from ..models import PaperRecord
from ..sources import arxiv_api, arxiv_search, hf_daily, hf_trending
from .merge import merge_candidates


SourceFetcher = Callable[..., list[PaperRecord]]

DEFAULT_SOURCE_FETCHERS: dict[str, SourceFetcher] = {
    "hf-daily": hf_daily.fetch_candidates,
    "hf-trending": hf_trending.fetch_candidates,
    "arxiv-api": arxiv_api.fetch_candidates,
    "arxiv-search": arxiv_search.fetch_candidates,
}


def discover_candidates(
    *,
    topic_name: str,
    keywords: list[str],
    days: int,
    enabled_sources: list[str],
    source_fetchers: dict[str, SourceFetcher] | None = None,
    http_client: HttpClient | None = None,
    candidate_limit: int = 50,
) -> list[PaperRecord]:
    del topic_name
    fetchers = source_fetchers or DEFAULT_SOURCE_FETCHERS
    client = http_client or HttpClient()
    collected: list[PaperRecord] = []
    for source_name in enabled_sources:
        fetcher = fetchers.get(source_name)
        if not fetcher:
            continue
        try:
            items = fetcher(
                keywords=keywords,
                days=days,
                http_get=client.get_text,
                max_results=candidate_limit,
            )
        except Exception as exc:
            print(
                f"[paper-daily-fetch] source {source_name!r} failed: {exc!r}",
                file=sys.stderr,
            )
            continue
        collected.extend(items)
    merged = merge_candidates(collected)
    merged.sort(
        key=lambda paper: (_parse_published(paper.published_at), paper.arxiv_id),
        reverse=True,
    )
    return merged[:candidate_limit]


def _parse_published(value: str) -> datetime:
    published = datetime.fromisoformat(value)
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    return published
