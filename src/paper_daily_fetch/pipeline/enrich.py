from __future__ import annotations

import inspect
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path
from time import monotonic
from typing import Callable

from ..enrichment import arxiv_html_url, enrich_paper_links
from ..figures import extract_pdf_candidates, select_figure
from ..models import PaperRecord


def enrich_candidates(
    papers: list[PaperRecord],
    http_get: Callable[[str], str],
    http_get_bytes: Callable[[str], bytes] | None = None,
    cache_dir: str | Path | None = None,
    max_workers: int = 5,
    timeout: int = 30,
) -> list[PaperRecord]:
    """Enrich papers with code URLs and figures using parallel processing.

    Args:
        papers: List of papers to enrich.
        http_get: Function to fetch text content from URLs.
        http_get_bytes: Function to fetch binary content (for PDFs).
        cache_dir: Directory to cache downloaded PDFs.
        max_workers: Maximum number of parallel workers (default: 5, minimum: 1).
        timeout: Deadline budget in seconds for each paper's enrichment (default: 30).

    Returns:
        List of enriched papers in the same order as input.
    """
    if not papers:
        return []

    # Ensure max_workers is at least 1
    max_workers = max(1, max_workers)

    total = len(papers)
    print(
        f"[paper-daily-fetch] enrich: processing {total} papers with {max_workers} workers (timeout={timeout}s)",
        file=sys.stderr,
    )

    # Use a dict to preserve order while allowing parallel processing
    results: dict[int, PaperRecord] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(
                _enrich_single_paper,
                paper,
                http_get,
                http_get_bytes,
                cache_dir,
                timeout,
            ): idx
            for idx, paper in enumerate(papers)
        }

        # Collect results as they complete
        completed = 0
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            completed += 1
            try:
                result = future.result()
                results[idx] = result
                arxiv_id = result.arxiv_id
                print(
                    f"[paper-daily-fetch] enrich: [{completed}/{total}] completed {arxiv_id!r}",
                    file=sys.stderr,
                )
            except TimeoutError:
                results[idx] = papers[idx]
                arxiv_id = papers[idx].arxiv_id
                print(
                    f"[paper-daily-fetch] enrich: [{completed}/{total}] timeout {arxiv_id!r}",
                    file=sys.stderr,
                )
            except Exception as exc:
                # On unexpected error, keep original paper
                results[idx] = papers[idx]
                arxiv_id = papers[idx].arxiv_id
                print(
                    f"[paper-daily-fetch] enrich: [{completed}/{total}] failed {arxiv_id!r}: {exc!r}",
                    file=sys.stderr,
                )

    # Return in original order
    return [results[i] for i in range(total)]


def _enrich_single_paper(
    paper: PaperRecord,
    http_get: Callable[[str], str],
    http_get_bytes: Callable[[str], bytes] | None,
    cache_dir: str | Path | None,
    timeout: float,
) -> PaperRecord:
    """Enrich a single paper with code URL and figure."""
    deadline = monotonic() + max(timeout, 0)
    timed_get = _with_deadline(http_get, deadline)
    timed_get_bytes = (
        _with_deadline(http_get_bytes, deadline) if http_get_bytes is not None else None
    )

    # Fetch arXiv abstract page
    try:
        abs_html = timed_get(paper.paper_url)
    except Exception as exc:
        print(
            f"[paper-daily-fetch] enrich: abs fetch failed for {paper.arxiv_id!r}: {exc!r}",
            file=sys.stderr,
        )
        abs_html = None

    # Fetch arXiv HTML version
    try:
        html = timed_get(arxiv_html_url(paper.paper_url))
    except Exception as exc:
        print(
            f"[paper-daily-fetch] enrich: html fetch failed for {paper.arxiv_id!r}: {exc!r}",
            file=sys.stderr,
        )
        html = None

    # Enrich code links
    try:
        enriched_paper = enrich_paper_links(
            paper,
            http_get=timed_get,
            arxiv_abs_html=abs_html,
            arxiv_html=html,
        )
    except Exception as exc:
        print(
            f"[paper-daily-fetch] enrich: link enrichment failed for {paper.arxiv_id!r}: {exc!r}",
            file=sys.stderr,
        )
        return paper

    # Extract figure candidates from PDF if needed
    pdf_candidates = _fetch_pdf_candidates(
        paper=enriched_paper,
        http_get_bytes=timed_get_bytes,
        cache_dir=cache_dir,
        deadline=deadline,
    )

    # Select best figure
    figure = select_figure(
        html,
        base_url=arxiv_html_url(enriched_paper.paper_url),
        pdf_candidates=pdf_candidates,
    )

    if figure is None:
        return enriched_paper

    return replace(
        enriched_paper,
        figure_url_or_path=figure.url,
        figure_reason=figure.reason,
    )


def _fetch_pdf_candidates(
    paper: PaperRecord,
    http_get_bytes: Callable[[str], bytes] | None,
    cache_dir: str | Path | None,
    deadline: float | None = None,
):
    if http_get_bytes is None or cache_dir is None:
        return []
    try:
        _remaining_timeout(deadline)
    except TimeoutError:
        return []
    pdf_url = _arxiv_pdf_url(paper.paper_url)
    if pdf_url is None:
        return []
    target_dir = (
        Path(cache_dir).expanduser() / "figures" / paper.arxiv_id.replace("/", "_")
    )
    target_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = target_dir / "paper.pdf"
    try:
        pdf_path.write_bytes(http_get_bytes(pdf_url))
    except Exception:
        return []
    try:
        _remaining_timeout(deadline)
    except TimeoutError:
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


def _with_deadline(fetcher, deadline: float):
    if fetcher is None:
        return None

    accepts_timeout = _accepts_timeout_kw(fetcher)

    def wrapped(url: str):
        remaining = _remaining_timeout(deadline)
        if accepts_timeout:
            return fetcher(url, timeout=remaining)
        return fetcher(url)

    return wrapped


def _remaining_timeout(deadline: float | None) -> float:
    if deadline is None:
        return 0.0
    remaining = deadline - monotonic()
    if remaining <= 0:
        raise TimeoutError("enrich deadline exceeded")
    return remaining


def _accepts_timeout_kw(fetcher) -> bool:
    try:
        parameters = inspect.signature(fetcher).parameters.values()
    except (TypeError, ValueError):
        return False
    return any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD or parameter.name == "timeout"
        for parameter in parameters
    )
