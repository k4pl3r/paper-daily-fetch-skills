from __future__ import annotations

from dataclasses import replace
import re
from typing import Callable
from urllib.parse import quote_plus, urljoin
from urllib.request import Request, urlopen

from .models import PaperRecord

CODE_HOST_HINTS = ("github.com", "gitlab.com", "huggingface.co", "bitbucket.org")
PWC_BASE_URL = "https://paperswithcode.com"


def _http_get(url: str, timeout: int = 20) -> str:
    request = Request(url, headers={"User-Agent": "paper-daily-fetch/0.1"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def enrich_links(
    paper: PaperRecord,
    arxiv_html: str | None,
    pwc_search_html: str | None,
    pwc_paper_html: str | None,
) -> PaperRecord:
    code_url = _find_code_url(arxiv_html or "")
    if not code_url and pwc_search_html and pwc_paper_html:
        code_url = _find_code_url(pwc_paper_html)
    return replace(paper, code_url=code_url)


def enrich_paper_links(
    paper: PaperRecord,
    http_get: Callable[[str], str] | None = None,
) -> PaperRecord:
    fetch = http_get or _http_get
    arxiv_html = fetch(arxiv_html_url(paper.paper_url))
    code_url = _find_code_url(arxiv_html)
    if code_url:
        return replace(paper, code_url=code_url)
    pwc_search_url = f"{PWC_BASE_URL}/search?q={quote_plus(paper.title)}"
    search_html = fetch(pwc_search_url)
    pwc_paper_path = _extract_first_pwc_paper_path(search_html)
    if not pwc_paper_path:
        return paper
    pwc_paper_html = fetch(urljoin(PWC_BASE_URL, pwc_paper_path))
    return replace(paper, code_url=_find_code_url(pwc_paper_html))


def arxiv_html_url(paper_url: str) -> str:
    arxiv_id = paper_url.rstrip("/").split("/")[-1]
    return f"https://arxiv.org/html/{arxiv_id}"


def _find_code_url(html: str) -> str | None:
    links = re.findall(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    prioritized: list[str] = []
    fallbacks: list[str] = []
    for href, label in links:
        href = href.strip()
        label_text = re.sub(r"<[^>]+>", " ", label).lower()
        if any(host in href for host in CODE_HOST_HINTS):
            if any(token in label_text for token in ("code", "github", "official", "project")):
                prioritized.append(href)
            else:
                fallbacks.append(href)
    if prioritized:
        return prioritized[0]
    if fallbacks:
        return fallbacks[0]
    return None


def _extract_first_pwc_paper_path(html: str) -> str | None:
    match = re.search(r'href=["\'](/paper/[^"\']+)["\']', html, flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(1)

