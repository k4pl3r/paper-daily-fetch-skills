from __future__ import annotations

from typing import Callable

from .hf_daily import _parse_cards, _parse_hydrated_props

HF_TRENDING_URL = "https://huggingface.co/papers/trending"


def parse_hf_trending_html(html: str):
    hydrated = _parse_hydrated_props(html, source_name="hf-trending")
    if hydrated:
        return hydrated
    return _parse_cards(html, source_name="hf-trending")


def fetch_candidates(
    *,
    keywords: list[str],
    days: int,
    http_get: Callable[[str], str],
    max_results: int = 50,
):
    del keywords, days, max_results
    return parse_hf_trending_html(http_get(HF_TRENDING_URL))
