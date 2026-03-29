from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
import re
from typing import Callable
from urllib.parse import quote_plus

from ..models import PaperRecord

ARXIV_SEARCH_URL = "https://arxiv.org/search/"


def build_search_url(keywords: list[str], max_results: int = 50) -> str:
    query_terms = " OR ".join(f'"{keyword}"' for keyword in keywords if keyword.strip())
    query = quote_plus(query_terms or "all")
    return (
        f"{ARXIV_SEARCH_URL}?query={query}&searchtype=all&abstracts=show"
        f"&order=-announced_date_first&size={max_results}"
    )


def parse_arxiv_search_html(html: str) -> list[PaperRecord]:
    candidates: list[PaperRecord] = []
    for block in re.findall(r'<li class="arxiv-result".*?</li>', html, flags=re.DOTALL):
        paper_match = re.search(r'href="(https://arxiv\.org/abs/([^"]+))"', block)
        title_match = re.search(r'<p class="title is-5 mathjax">\s*(.*?)\s*</p>', block, flags=re.DOTALL)
        abstract_match = re.search(
            r'<span class="abstract-full[^"]*"[^>]*>\s*(.*?)\s*</span>',
            block,
            flags=re.DOTALL,
        )
        if not paper_match or not title_match:
            continue
        authors = re.findall(r'<p class="authors">.*?</p>', block, flags=re.DOTALL)
        author_names: list[str] = []
        if authors:
            author_names = [name.strip() for name in re.findall(r"<a[^>]*>(.*?)</a>", authors[0], flags=re.DOTALL)]
        date_match = re.search(r"Submitted</span>\s*([^;]+);", block)
        published_at = _parse_submitted(date_match.group(1)) if date_match else datetime.now(timezone.utc).isoformat()
        title = _clean_html(title_match.group(1))
        abstract = _clean_html(abstract_match.group(1) if abstract_match else "")
        arxiv_id = paper_match.group(2)
        paper_url = paper_match.group(1)
        candidates.append(
            PaperRecord(
                arxiv_id=arxiv_id,
                title=title,
                authors=author_names,
                published_at=published_at,
                abstract=abstract,
                paper_url=paper_url,
                code_url=None,
                figure_url_or_path=None,
                figure_reason=None,
                topic_matches=[],
                source="arxiv-search",
                sources=["arxiv-search"],
                canonical_url=paper_url,
            )
        )
    return candidates


def fetch_candidates(
    *,
    keywords: list[str],
    days: int,
    http_get: Callable[[str], str],
    max_results: int = 50,
) -> list[PaperRecord]:
    papers = parse_arxiv_search_html(http_get(build_search_url(keywords, max_results=max_results)))
    cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
    return [
        paper
        for paper in papers
        if datetime.fromisoformat(paper.published_at).timestamp() >= cutoff
    ]


def _parse_submitted(value: str) -> str:
    parsed = datetime.strptime(value.strip(), "%d %B, %Y").replace(tzinfo=timezone.utc)
    return parsed.isoformat()


def _clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return " ".join(unescape(text).split())
