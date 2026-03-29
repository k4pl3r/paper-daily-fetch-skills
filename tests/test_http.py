from urllib.error import HTTPError

from paper_daily_fetch.infra.http import HttpClient


def test_http_client_retries_429_then_succeeds():
    calls = {"count": 0}

    def transport(url: str, timeout: int) -> str:
        calls["count"] += 1
        if calls["count"] == 1:
            raise HTTPError(url, 429, "Too Many Requests", hdrs=None, fp=None)
        return "ok"

    client = HttpClient(transport=transport, retries=1, backoff_seconds=0.0, timeout=5)

    assert client.get_text("https://example.com") == "ok"
    assert calls["count"] == 2


def test_http_client_raises_after_retry_budget_exhausted():
    def transport(url: str, timeout: int) -> str:
        raise HTTPError(url, 429, "Too Many Requests", hdrs=None, fp=None)

    client = HttpClient(transport=transport, retries=1, backoff_seconds=0.0, timeout=5)

    try:
        client.get_text("https://example.com")
    except HTTPError as exc:
        assert exc.code == 429
    else:
        raise AssertionError("Expected HTTPError")
