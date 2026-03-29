from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable
from urllib.error import URLError
from urllib.request import Request, urlopen

from .config import AppConfig
from .discovery import fetch_recent_arxiv_papers
from .enrichment import arxiv_html_url, enrich_paper_links
from .figures import select_figure
from .models import FigureSelection, PaperRecord
from .ranking import rank_papers
from .state import SeenStateStore


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
    papers = fetch_recent_arxiv_papers(
        keywords=keywords,
        days=days or config.lookback_days,
        http_get=http_get,
    )
    ranked = rank_papers(papers, keywords=keywords, limit=limit or config.limit)
    enriched = [_enrich_paper(paper, http_get=http_get) for paper in ranked]
    state = SeenStateStore(config.state_path)
    if include_seen:
        visible = enriched
    else:
        visible_ids = set(state.filter_new([paper.arxiv_id for paper in enriched]))
        visible = [paper for paper in enriched if paper.arxiv_id in visible_ids]
        state.mark_seen(list(visible_ids))
    return {
        "topic": selected_topic,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "papers": [paper.to_dict() for paper in visible],
    }


def _enrich_paper(
    paper: PaperRecord,
    http_get: Callable[[str], str] | None = None,
) -> PaperRecord:
    fetch = http_get or _http_get
    try:
        paper = enrich_paper_links(paper, http_get=fetch)
        html = fetch(arxiv_html_url(paper.paper_url))
    except Exception:
        return paper
    figure = select_figure(html, base_url=arxiv_html_url(paper.paper_url))
    if not figure:
        return paper
    return PaperRecord(
        arxiv_id=paper.arxiv_id,
        title=paper.title,
        authors=paper.authors,
        published_at=paper.published_at,
        abstract=paper.abstract,
        paper_url=paper.paper_url,
        code_url=paper.code_url,
        figure_url_or_path=figure.url,
        figure_reason=figure.reason,
        topic_matches=paper.topic_matches,
    )


def _http_get(url: str, timeout: int = 20) -> str:
    request = Request(url, headers={"User-Agent": "paper-daily-fetch/0.1"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")

