from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from .models import PaperRecord

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_API_URL = "https://export.arxiv.org/api/query"


def _http_get(url: str, timeout: int = 20) -> str:
    request = Request(url, headers={"User-Agent": "paper-daily-fetch/0.1"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


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
        published_at = entry.findtext(
            "atom:published", default="", namespaces=ATOM_NS
        ).strip()
        authors = [
            author.findtext("atom:name", default="", namespaces=ATOM_NS).strip()
            for author in entry.findall("atom:author", ATOM_NS)
        ]
        records.append(
            PaperRecord(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                published_at=_isoformat_z(published_at),
                abstract=abstract,
                paper_url=paper_url,
                code_url=None,
                figure_url_or_path=None,
                figure_reason=None,
                topic_matches=[],
            )
        )
    return records


def fetch_recent_arxiv_papers(
    keywords: list[str],
    days: int,
    http_get: Callable[[str], str] | None = None,
    now: datetime | None = None,
    max_results: int = 50,
) -> list[PaperRecord]:
    fetch = http_get or _http_get
    raw = fetch(build_arxiv_query(keywords, max_results=max_results))
    papers = parse_arxiv_feed(raw)
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    return [
        paper
        for paper in papers
        if datetime.fromisoformat(paper.published_at) >= cutoff
    ]


def _isoformat_z(value: str) -> str:
    if value.endswith("Z"):
        return value[:-1] + "+00:00"
    return value

