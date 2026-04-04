from __future__ import annotations

from dataclasses import replace
import re
from typing import Callable
from urllib.parse import quote_plus, urljoin
from urllib.parse import urlparse
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
    arxiv_abs_html: str | None = None,
    arxiv_html: str | None = None,
) -> PaperRecord:
    fetch = http_get or _http_get
    abs_html = arxiv_abs_html
    if abs_html is None:
        abs_html = fetch(paper.paper_url)
    code_url = _find_code_url(abs_html)
    html_page = arxiv_html
    if not code_url:
        if html_page is None:
            html_page = fetch(arxiv_html_url(paper.paper_url))
        code_url = _find_code_url(html_page)
    if code_url:
        return replace(paper, code_url=code_url)
    pwc_search_url = f"{PWC_BASE_URL}/search?q={quote_plus(paper.title)}"
    search_html = fetch(pwc_search_url)
    pwc_paper_path = _extract_first_pwc_paper_path(search_html, paper.title)
    if not pwc_paper_path:
        return paper
    pwc_paper_html = fetch(urljoin(PWC_BASE_URL, pwc_paper_path))
    return replace(paper, code_url=_find_code_url(pwc_paper_html))


def arxiv_html_url(paper_url: str) -> str:
    arxiv_id = paper_url.rstrip("/").split("/")[-1]
    return f"https://arxiv.org/html/{arxiv_id}"


def _find_code_url(html: str) -> str | None:
    links = re.finditer(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    prioritized: list[str] = []
    fallbacks: list[str] = []
    for match in links:
        href, label = match.groups()
        href = href.strip()
        label_text = re.sub(r"<[^>]+>", " ", label).lower()
        if not any(host in href for host in CODE_HOST_HINTS):
            continue
        if _is_excluded_link(href):
            continue
        context = _normalize_text(
            html[max(0, match.start() - 120): min(len(html), match.end() + 120)]
        )
        if any(token in context or token in label_text for token in ("code", "github", "official", "project", "repo", "implementation", "weights", "checkpoint", "model")):
            prioritized.append(href)
            continue
        if _is_code_host_fallback(href):
            fallbacks.append(href)
    if prioritized:
        return prioritized[0]
    if fallbacks:
        return fallbacks[0]
    return None


def _extract_first_pwc_paper_path(html: str, query_title: str | None = None) -> str | None:
    """Return the first PaperWithCode paper path from a search result page.

    When *query_title* is given the candidate is only accepted when its anchor
    text is similar enough to the query title (Jaccard ≥ 0.4).  This guards
    against returning a completely unrelated paper that happens to rank first.
    """
    for match in re.finditer(
        r'href=["\'](/paper/[^"\']+)["\'][^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        path = match.group(1)
        anchor_text = re.sub(r"<[^>]+>", " ", match.group(2)).strip()
        if query_title and not _titles_similar(query_title, anchor_text):
            continue
        return path
    # Fallback: accept any /paper/ href without title verification.
    simple = re.search(r'href=["\'](/paper/[^"\']+)["\']', html, flags=re.IGNORECASE)
    return simple.group(1) if simple else None


def _titles_similar(a: str, b: str, threshold: float = 0.4) -> bool:
    """Jaccard similarity on lowercased word tokens; True when >= threshold."""
    if not b:
        return False
    tokens_a = set(re.findall(r"[a-z0-9]+", a.lower()))
    tokens_b = set(re.findall(r"[a-z0-9]+", b.lower()))
    if not tokens_a or not tokens_b:
        return False
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union) >= threshold


def _normalize_text(text: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", text).lower().split())


def _is_code_host_fallback(href: str) -> bool:
    parsed = urlparse(href)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    if any(domain in host for domain in ("github.com", "gitlab.com", "bitbucket.org")):
        return bool(path and "/" in path)
    if "huggingface.co" in host:
        if not path or path in {"huggingface", "docs", "docs/hub", "docs/hub/spaces"}:
            return False
        return path.count("/") >= 1
    return False


def _is_excluded_link(href: str) -> bool:
    parsed = urlparse(href)
    path = parsed.path.lower()
    return any(token in path for token in ("/issues", "/pull/", "/pulls", "/discussions", "/wiki/"))
