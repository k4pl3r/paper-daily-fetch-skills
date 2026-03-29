from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import re

from .models import PaperRecord


def rank_papers(
    papers: list[PaperRecord],
    keywords: list[str],
    limit: int,
    now: datetime | None = None,
) -> list[PaperRecord]:
    now = now or datetime.now(timezone.utc)
    scored: list[tuple[float, PaperRecord]] = []
    for paper in papers:
        title_text = _normalize_text(paper.title)
        abstract_text = _normalize_text(paper.abstract)
        matches: list[str] = []
        score = 0.0
        for keyword in keywords:
            normalized_keyword = _normalize_text(keyword)
            in_title = normalized_keyword in title_text
            in_abstract = normalized_keyword in abstract_text
            if in_title or in_abstract:
                matches.append(keyword)
                if in_title:
                    score += 5.0
                if in_abstract:
                    score += 3.0
        if not matches:
            continue
        age_days = max(
            0.0,
            (now - datetime.fromisoformat(paper.published_at)).total_seconds() / 86400,
        )
        score += max(0.0, 2.0 - min(age_days, 2.0))
        scored.append((score, replace(paper, topic_matches=matches)))
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

