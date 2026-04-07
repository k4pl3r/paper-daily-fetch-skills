from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from .config import AppConfig
from .history import PublishHistoryStore
from .infra.http import HttpClient, default_transport
from .models import PaperRecord
from .pipeline.discover import discover_candidates
from .pipeline.enrich import enrich_candidates
from .pipeline.rank import rank_candidates


def collect_papers(
    config: AppConfig,
    topic_name: str | None = None,
    days: int | None = None,
    limit: int | None = None,
    include_seen: bool = False,
    http_get: Callable[[str], str] | None = None,
) -> dict[str, object]:
    selected_topic = topic_name or config.default_topic
    keywords = config.topic_keywords(selected_topic)
    negative_keywords = config.topic_negative_keywords(selected_topic)
    domain_boost_keywords = config.topic_domain_boost_keywords(selected_topic)
    client = HttpClient(
        transport=(lambda url, timeout: http_get(url))
        if http_get
        else default_transport,
        retries=config.sources.retries,
        backoff_seconds=config.sources.backoff_seconds,
        timeout=config.sources.timeout,
    )
    discovered = discover_candidates(
        topic_name=selected_topic,
        keywords=keywords,
        days=days or config.lookback_days,
        enabled_sources=config.sources.enabled,
        http_client=client,
        candidate_limit=config.discover.candidate_limit,
    )
    desired_limit = limit or config.rank.final_limit
    ranked_candidates = rank_candidates(
        discovered,
        keywords=keywords,
        negative_keywords=negative_keywords,
        domain_boost_keywords=domain_boost_keywords,
        limit=len(discovered),
    )
    if include_seen:
        visible_candidates = ranked_candidates
    else:
        state = PublishHistoryStore(config.history.path)
        visible_ids = set(
            state.filter_new([paper.arxiv_id for paper in ranked_candidates])
        )
        visible_candidates = [
            paper for paper in ranked_candidates if paper.arxiv_id in visible_ids
        ]
    pre_rank_limit = max(config.enrich.pre_rank_limit, desired_limit)
    pre_ranked = visible_candidates[:pre_rank_limit]
    enriched = enrich_candidates(
        pre_ranked,
        http_get=client.get_text,
        http_get_bytes=client.get_bytes,
        cache_dir=config.cache_dir,
        max_workers=config.enrich.max_workers,
        timeout=config.enrich.timeout,
    )
    ranked = rank_candidates(
        enriched,
        keywords=keywords,
        negative_keywords=negative_keywords,
        domain_boost_keywords=domain_boost_keywords,
        limit=desired_limit,
    )
    return {
        "topic": selected_topic,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "papers": [paper.to_dict() for paper in ranked],
    }
