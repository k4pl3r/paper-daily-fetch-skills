from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
import json
import re
import sys
from typing import Callable

from ..models import PaperRecord

HF_DAILY_URL = "https://huggingface.co/papers?sort=recent"


def parse_hf_daily_html(html: str) -> list[PaperRecord]:
    hydrated = _parse_hydrated_props(html, source_name="hf-daily")
    if hydrated:
        return hydrated
    return _parse_cards(html, source_name="hf-daily")


def fetch_candidates(
    *,
    keywords: list[str],
    days: int,
    http_get: Callable[[str], str],
    max_results: int = 50,
) -> list[PaperRecord]:
    del keywords, days, max_results
    return parse_hf_daily_html(http_get(HF_DAILY_URL))


def _parse_cards(html: str, source_name: str) -> list[PaperRecord]:
    cards = re.findall(r"<article[^>]*data-card=\"paper\".*?</article>", html, flags=re.DOTALL)
    candidates: list[PaperRecord] = []
    for card in cards:
        link_match = re.search(r'href="(/papers/([^"]+))"', card)
        title_match = re.search(r"<a[^>]*>\s*(.*?)\s*</a>", card, flags=re.DOTALL)
        summary_match = re.search(r'<p class="summary">\s*(.*?)\s*</p>', card, flags=re.DOTALL)
        if not link_match or not title_match:
            continue
        arxiv_id = link_match.group(2)
        paper_url = f"https://arxiv.org/abs/{arxiv_id}"
        # Try to parse a real date from <time datetime="..."> inside the card.
        # Fall back to today (UTC) so freshness scoring is not penalised for
        # papers discovered via the HTML fallback path.
        published_at = _parse_card_date(card)
        candidates.append(
            PaperRecord(
                arxiv_id=arxiv_id,
                title=" ".join(re.sub(r"<[^>]+>", " ", title_match.group(1)).split()),
                authors=[],
                published_at=published_at,
                abstract=" ".join(re.sub(r"<[^>]+>", " ", (summary_match.group(1) if summary_match else "")).split()),
                paper_url=paper_url,
                code_url=None,
                figure_url_or_path=None,
                figure_reason=None,
                topic_matches=[],
                source=source_name,
                sources=[source_name],
                canonical_url=paper_url,
            )
        )
    return candidates


def _parse_card_date(card_html: str) -> str:
    """Extract publication date from a HF paper card's <time> element.

    Returns an ISO-8601 string with UTC offset. Falls back to today (UTC midnight)
    rather than the Unix epoch so that freshness scoring is not incorrectly penalised.
    """
    time_match = re.search(r'<time[^>]+datetime=["\']([^"\']+)["\']', card_html, flags=re.IGNORECASE)
    if time_match:
        raw = time_match.group(1).strip()
        try:
            return _normalize_timestamp(raw)
        except Exception:
            print(
                f"[paper-daily-fetch] hf_daily: could not parse date {raw!r}, using today",
                file=sys.stderr,
            )
    # Use today at UTC midnight as a safe fallback — better than 1970-01-01.
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return today.isoformat()


def _parse_hydrated_props(html: str, source_name: str) -> list[PaperRecord]:
    match = re.search(r'data-target="DailyPapers"\s+data-props="([^"]+)"', html, flags=re.DOTALL)
    if not match:
        return []
    props = json.loads(unescape(match.group(1)))
    candidates: list[PaperRecord] = []
    for item in props.get("dailyPapers", []):
        paper = item.get("paper", {})
        arxiv_id = paper.get("id")
        title = paper.get("title") or item.get("title")
        if not arxiv_id or not title:
            continue
        paper_url = f"https://arxiv.org/abs/{arxiv_id}"
        candidates.append(
            PaperRecord(
                arxiv_id=arxiv_id,
                title=title.strip(),
                authors=[author.get("name", "").strip() for author in paper.get("authors", []) if author.get("name")],
                published_at=_normalize_timestamp(paper.get("publishedAt") or item.get("publishedAt")),
                abstract=(paper.get("summary") or item.get("summary") or "").strip(),
                paper_url=paper_url,
                code_url=paper.get("githubRepo") or paper.get("projectPage"),
                figure_url_or_path=item.get("thumbnail"),
                figure_reason="huggingface-thumbnail" if item.get("thumbnail") else None,
                topic_matches=[],
                source=source_name,
                sources=[source_name],
                canonical_url=paper_url,
            )
        )
    return candidates


def _normalize_timestamp(value: str | None) -> str:
    if not value:
        return "1970-01-01T00:00:00+00:00"
    if value.endswith("Z"):
        return value[:-1] + "+00:00"
    return value
