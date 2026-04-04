from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re
from typing import Callable
from urllib.parse import quote_plus
from xml.etree import ElementTree

from ..models import PaperRecord

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_API_URL = "https://export.arxiv.org/api/query"


def build_arxiv_query(keywords: list[str], max_results: int = 50) -> str:
    """Build an arXiv API query URL for one or more keywords (OR-joined).

    Prefer calling with a single keyword so that each term gets its own result
    budget; OR-joining multiple terms causes high-volume keywords to crowd out
    the others within the shared max_results window.
    """
    joined = " OR ".join(f'all:"{keyword}"' for keyword in keywords)
    return (
        f"{ARXIV_API_URL}?search_query={quote_plus(joined)}"
        f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )


def parse_arxiv_feed(xml_text: str) -> list[PaperRecord]:
    root = ElementTree.fromstring(xml_text)
    records: list[PaperRecord] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        paper_url = entry.findtext("atom:id", default="", namespaces=ATOM_NS).strip()
        arxiv_id = paper_url.rstrip("/").split("/")[-1]
        title = " ".join(entry.findtext("atom:title", default="", namespaces=ATOM_NS).split())
        abstract = " ".join(
            entry.findtext("atom:summary", default="", namespaces=ATOM_NS).split()
        )
        published_at = _isoformat_z(
            entry.findtext("atom:published", default="", namespaces=ATOM_NS).strip()
        )
        authors = [
            author.findtext("atom:name", default="", namespaces=ATOM_NS).strip()
            for author in entry.findall("atom:author", ATOM_NS)
        ]
        records.append(
            PaperRecord(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                published_at=published_at,
                abstract=abstract,
                paper_url=paper_url,
                code_url=None,
                figure_url_or_path=None,
                figure_reason=None,
                topic_matches=[],
                source="arxiv-api",
                sources=["arxiv-api"],
                canonical_url=paper_url,
            )
        )
    return records


def fetch_candidates(
    *,
    keywords: list[str],
    days: int,
    http_get: Callable[[str], str],
    max_results: int = 50,
) -> list[PaperRecord]:
    # Query each keyword independently so that no single high-volume keyword
    # crowds out the others within a shared max_results budget.
    # Scale per-keyword limit by days to avoid truncation on wider look-back
    # windows; cap at 100 to stay within arXiv API fair-use guidelines.
    per_keyword_limit = min(100, max(max_results, days * 5))
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    seen_ids: set[str] = set()
    all_papers: list[PaperRecord] = []
    for keyword in keywords:
        try:
            raw = http_get(build_arxiv_query([keyword], max_results=per_keyword_limit))
        except Exception:
            continue
        for paper in parse_arxiv_feed(raw):
            if paper.arxiv_id in seen_ids:
                continue
            seen_ids.add(paper.arxiv_id)
            if _parse_datetime(paper.published_at) >= cutoff:
                all_papers.append(paper)
    return all_papers


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(_isoformat_z(value))


def _isoformat_z(value: str) -> str:
    if value.endswith("Z"):
        return value[:-1] + "+00:00"
    return value
