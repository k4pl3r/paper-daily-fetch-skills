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
        base_score = 0.0
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
                    base_score += 5.0
                if in_abstract:
                    base_score += 3.0
        for boost in domain_boost_keywords:
            normalized_boost = _normalize_text(boost)
            if normalized_boost and normalized_boost in corpus:
                base_score += 2.0
                reasons.append(f"domain-boost:{boost}")
        if not matches:
            continue
        # Bug fix: guard against naive datetimes from arxiv_search fallback paths.
        published = datetime.fromisoformat(paper.published_at)
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        age_days = max(0.0, (now - published).total_seconds() / 86400)
        freshness = max(0.0, 1.0 - min(age_days / 14.0, 1.0))
        # Freshness as a multiplicative decay factor so recency is always meaningful:
        #   freshness=1.0 (today)    → full score
        #   freshness=0.5 (7 days)   → 75 % of base score
        #   freshness=0.0 (≥14 days) → 50 % of base score
        score = base_score * (0.5 + 0.5 * freshness)
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
            _parse_published(item[1].published_at),
            item[1].arxiv_id,
        ),
        reverse=True,
    )
    return [paper for _, paper in scored[:limit]]


def _parse_published(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _normalize_text(text: str) -> str:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    normalized = []
    for token in tokens:
        # Skip stemming for alphanumeric tokens (e.g. "3dgs", "gpt4") — stripping a
        # trailing "s" from "3dgs" yields "3dg" which will never match anything.
        if len(token) > 3 and token.endswith("s") and not re.search(r"\d", token):
            token = token[:-1]
        normalized.append(token)
    return " ".join(normalized)
