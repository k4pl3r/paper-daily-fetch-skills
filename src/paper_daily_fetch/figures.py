from __future__ import annotations

from html import unescape
from pathlib import Path
import re
from urllib.parse import urljoin

from .models import FigureSelection

CAPTION_HINTS = ("overview", "pipeline", "framework", "architecture", "method", "teaser")


def select_figure_from_html(html: str, base_url: str) -> FigureSelection | None:
    candidates = _extract_html_candidates(html, base_url)
    if not candidates:
        return None
    ranked = sorted(candidates, key=_candidate_score, reverse=True)
    best = ranked[0]
    if best["matched_hint"]:
        return FigureSelection(url=best["url"], reason=f"matched:{best['matched_hint']}")
    return FigureSelection(url=best["url"], reason="fallback:first-image")


def select_figure(
    arxiv_html: str | None,
    base_url: str,
    pdf_candidates: list[FigureSelection] | None = None,
) -> FigureSelection | None:
    html_figure = select_figure_from_html(arxiv_html or "", base_url)
    if html_figure:
        return html_figure
    if pdf_candidates:
        return pdf_candidates[0]
    return None


def extract_pdf_candidates(pdf_path: str | Path) -> list[FigureSelection]:
    try:
        import fitz  # type: ignore
    except Exception:
        return []
    path = Path(pdf_path)
    if not path.exists():
        return []
    candidates: list[FigureSelection] = []
    with fitz.open(path) as document:
        for page_index in range(len(document)):
            for image_index, image in enumerate(document.get_page_images(page_index), start=1):
                xref = image[0]
                pixmap = fitz.Pixmap(document, xref)
                output_path = path.with_name(f"{path.stem}-page{page_index + 1}-img{image_index}.png")
                pixmap.save(output_path)
                candidates.append(
                    FigureSelection(
                        url=str(output_path),
                        reason=f"pdf-extract:page-{page_index + 1}",
                    )
                )
                pixmap = None
            # Only scan the first page that yields images — return early to avoid
            # extracting the entire PDF when we only need one representative figure.
            if candidates:
                return candidates
    return candidates


def _extract_html_candidates(html: str, base_url: str) -> list[dict[str, str]]:
    figures: list[dict[str, str]] = []
    saw_figure = False
    skipped_svg_with_hint = False
    for match in re.finditer(r"<figure\b.*?</figure>", html, flags=re.IGNORECASE | re.DOTALL):
        saw_figure = True
        block = match.group(0)
        caption_match = re.search(
            r"<figcaption\b[^>]*>(.*?)</figcaption>",
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )
        caption = ""
        if caption_match:
            caption = re.sub(r"<[^>]+>", " ", caption_match.group(1))
        caption = " ".join(unescape(caption).split()).lower()
        matched_hint = next((hint for hint in CAPTION_HINTS if hint in caption), "")
        # arXiv sometimes renders architecture diagrams as composite SVG figures with nested
        # thumbnails inside <foreignObject>. Using the first nested <img> produces a misleading crop.
        # Let PDF fallback handle these composite figures instead.
        if "<svg" in block.lower():
            skipped_svg_with_hint = skipped_svg_with_hint or bool(matched_hint)
            continue
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', block, flags=re.IGNORECASE)
        if not img_match:
            continue
        figures.append(
            {
                "url": urljoin(base_url, img_match.group(1)),
                "caption": caption,
                "matched_hint": matched_hint,
            }
        )
    if figures:
        if skipped_svg_with_hint and not any(candidate["matched_hint"] for candidate in figures):
            return []
        return figures
    if saw_figure:
        return []

    img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)
    return [
        {"url": urljoin(base_url, src), "caption": "", "matched_hint": ""}
        for src in img_matches
    ]


def _candidate_score(candidate: dict[str, str]) -> int:
    if candidate["matched_hint"]:
        return 100 - CAPTION_HINTS.index(candidate["matched_hint"])
    return 1
