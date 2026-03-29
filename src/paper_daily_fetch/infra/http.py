from __future__ import annotations

from dataclasses import dataclass
from time import sleep
from typing import Callable
from urllib.error import HTTPError
from urllib.request import Request, urlopen


Transport = Callable[[str, int], str]


def default_transport(url: str, timeout: int) -> str:
    request = Request(url, headers={"User-Agent": "paper-daily-fetch/0.2"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


@dataclass(slots=True)
class HttpClient:
    transport: Transport = default_transport
    retries: int = 2
    backoff_seconds: float = 1.0
    timeout: int = 20

    def get_text(self, url: str) -> str:
        last_error: Exception | None = None
        attempts = self.retries + 1
        for attempt in range(attempts):
            try:
                return self.transport(url, self.timeout)
            except HTTPError as exc:
                last_error = exc
                if attempt >= self.retries or exc.code not in {429, 500, 502, 503, 504}:
                    raise
            except Exception as exc:  # pragma: no cover - fallback path
                last_error = exc
                if attempt >= self.retries:
                    raise
            if self.backoff_seconds > 0:
                sleep(self.backoff_seconds * (attempt + 1))
        if last_error is not None:
            raise last_error
        raise RuntimeError("unreachable")
