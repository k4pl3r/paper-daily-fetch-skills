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
    raw = http_get(build_arxiv_query(keywords, max_results=max_results))
    papers = parse_arxiv_feed(raw)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return [
        paper
        for paper in papers
        if _parse_datetime(paper.published_at) >= cutoff
    ]


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(_isoformat_z(value))


def _isoformat_z(value: str) -> str:
    if value.endswith("Z"):
        return value[:-1] + "+00:00"
    return value
