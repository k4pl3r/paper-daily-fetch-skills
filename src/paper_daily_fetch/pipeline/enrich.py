from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

from ..enrichment import arxiv_html_url, enrich_paper_links
from ..figures import extract_pdf_candidates, select_figure
from ..models import PaperRecord


def enrich_candidates(
    papers: list[PaperRecord],
    http_get,
    http_get_bytes=None,
    cache_dir: str | Path | None = None,
) -> list[PaperRecord]:
    enriched: list[PaperRecord] = []
    for paper in papers:
        try:
            abs_html = http_get(paper.paper_url)
        except Exception as exc:
            print(f"[paper-daily-fetch] enrich: abs fetch failed for {paper.arxiv_id!r}: {exc!r}", file=sys.stderr)
            abs_html = None
        try:
            html = http_get(arxiv_html_url(paper.paper_url))
        except Exception as exc:
            print(f"[paper-daily-fetch] enrich: html fetch failed for {paper.arxiv_id!r}: {exc!r}", file=sys.stderr)
            html = None
        try:
            enriched_paper = enrich_paper_links(
                paper,
                http_get=http_get,
                arxiv_abs_html=abs_html,
                arxiv_html=html,
            )
        except Exception as exc:
            print(f"[paper-daily-fetch] enrich: link enrichment failed for {paper.arxiv_id!r}: {exc!r}", file=sys.stderr)
            enriched.append(paper)
            continue
        pdf_candidates = _fetch_pdf_candidates(
            paper=enriched_paper,
            http_get_bytes=http_get_bytes,
            cache_dir=cache_dir,
        )
        figure = select_figure(
            html,
            base_url=arxiv_html_url(enriched_paper.paper_url),
            pdf_candidates=pdf_candidates,
        )
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


def _fetch_pdf_candidates(
    paper: PaperRecord,
    http_get_bytes,
    cache_dir: str | Path | None,
):
    if http_get_bytes is None or cache_dir is None:
        return []
    pdf_url = _arxiv_pdf_url(paper.paper_url)
    if pdf_url is None:
        return []
    target_dir = Path(cache_dir).expanduser() / "figures" / paper.arxiv_id.replace("/", "_")
    target_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = target_dir / "paper.pdf"
    try:
        pdf_path.write_bytes(http_get_bytes(pdf_url))
    except Exception:
        return []
    try:
        return extract_pdf_candidates(pdf_path)
    except Exception:
        return []


def _arxiv_pdf_url(paper_url: str) -> str | None:
    arxiv_id = paper_url.rstrip("/").split("/")[-1]
    if not arxiv_id:
        return None
    return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
