from __future__ import annotations

from dataclasses import replace

from ..enrichment import enrich_paper_links
from ..figures import select_figure
from ..models import PaperRecord


def enrich_candidates(
    papers: list[PaperRecord],
    http_get,
) -> list[PaperRecord]:
    enriched: list[PaperRecord] = []
    for paper in papers:
        try:
            enriched_paper = enrich_paper_links(paper, http_get=http_get)
        except Exception:
            enriched.append(paper)
            continue
        try:
            html = http_get(f"https://arxiv.org/html/{enriched_paper.arxiv_id}")
            figure = select_figure(html, base_url=f"https://arxiv.org/html/{enriched_paper.arxiv_id}")
        except Exception:
            figure = None
        if figure is None:
            enriched.append(enriched_paper)
            continue
        enriched.append(
            replace(
                enriched_paper,
                figure_url_or_path=figure.url,
                figure_reason=figure.reason,
            )
        )
    return enriched
