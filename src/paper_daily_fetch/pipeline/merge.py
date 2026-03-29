from __future__ import annotations

from dataclasses import replace

from ..models import PaperRecord


def merge_candidates(candidates: list[PaperRecord]) -> list[PaperRecord]:
    merged: dict[str, PaperRecord] = {}
    for candidate in candidates:
        key = candidate.arxiv_id or candidate.canonical_url or candidate.paper_url
        if key not in merged:
            merged[key] = candidate
            continue
        existing = merged[key]
        sources = sorted(set(existing.sources + candidate.sources))
        merged[key] = replace(
            existing,
            authors=existing.authors or candidate.authors,
            published_at=existing.published_at if existing.published_at != "1970-01-01T00:00:00+00:00" else candidate.published_at,
            abstract=existing.abstract if len(existing.abstract) >= len(candidate.abstract) else candidate.abstract,
            code_url=existing.code_url or candidate.code_url,
            canonical_url=existing.canonical_url or candidate.canonical_url,
            source=existing.source or candidate.source,
            sources=sources,
        )
    return list(merged.values())
