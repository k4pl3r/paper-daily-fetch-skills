from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import re

from ..models import PaperRecord


def rank_candidates(
    papers: list[PaperRecord],
    keywords: list[str],
    negative_keywords: list[str],
    domain_boost_keywords: list[str],
    limit: int,
    now: datetime | None = None,
) -> list[PaperRecord]:
    now = now or datetime.now(timezone.utc)
    scored: list[tuple[float, PaperRecord]] = []
    for paper in papers:
        title_text = _normalize_text(paper.title)
        abstract_text = _normalize_text(paper.abstract)
        corpus = f"{title_text} {abstract_text}".strip()
        matches: list[str] = []
        reasons: list[str] = []
        score = 0.0
        if any(_normalize_text(keyword) in corpus for keyword in negative_keywords):
            continue
        for keyword in keywords:
            normalized_keyword = _normalize_text(keyword)
            in_title = normalized_keyword in title_text
            in_abstract = normalized_keyword in abstract_text
            if in_title or in_abstract:
                matches.append(keyword)
                reasons.append(f"keyword:{keyword}")
                if in_title:
                    score += 5.0
                if in_abstract:
                    score += 3.0
        for boost in domain_boost_keywords:
            normalized_boost = _normalize_text(boost)
            if normalized_boost and normalized_boost in corpus:
                score += 2.0
                reasons.append(f"domain-boost:{boost}")
        if not matches:
            continue
        published = datetime.fromisoformat(paper.published_at)
        age_days = max(0.0, (now - published).total_seconds() / 86400)
        freshness = max(0.0, 1.0 - min(age_days / 14.0, 1.0))
        score += freshness
        reasons.append(f"freshness:{freshness:.2f}")
        scored.append(
            (
                score,
                replace(
                    paper,
                    topic_matches=matches,
                    score=score,
                    match_reason=reasons,
                ),
            )
        )
    scored.sort(
        key=lambda item: (
            item[0],
            datetime.fromisoformat(item[1].published_at),
            item[1].arxiv_id,
        ),
        reverse=True,
    )
    return [paper for _, paper in scored[:limit]]


def _normalize_text(text: str) -> str:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    normalized = []
    for token in tokens:
        if len(token) > 3 and token.endswith("s"):
            token = token[:-1]
        normalized.append(token)
    return " ".join(normalized)
