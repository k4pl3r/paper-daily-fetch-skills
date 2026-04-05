from __future__ import annotations

from dataclasses import dataclass
from time import sleep
from typing import Callable
from urllib.error import HTTPError
from urllib.request import Request, urlopen


Transport = Callable[[str, float], str]
BinaryTransport = Callable[[str, float], bytes]


def default_transport(url: str, timeout: float) -> str:
    request = Request(url, headers={"User-Agent": "paper-daily-fetch/0.2"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def default_binary_transport(url: str, timeout: float) -> bytes:
    request = Request(url, headers={"User-Agent": "paper-daily-fetch/0.2"})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


@dataclass(slots=True)
class HttpClient:
    transport: Transport = default_transport
    binary_transport: BinaryTransport = default_binary_transport
    retries: int = 2
    backoff_seconds: float = 1.0
    timeout: float = 20

    def get_text(self, url: str, timeout: float | None = None) -> str:
        effective_timeout = self.timeout if timeout is None else timeout
        return self._request(lambda: self.transport(url, effective_timeout))

    def get_bytes(self, url: str, timeout: float | None = None) -> bytes:
        effective_timeout = self.timeout if timeout is None else timeout
        return self._request(lambda: self.binary_transport(url, effective_timeout))

    def _request(self, operation):
        last_error: Exception | None = None
        attempts = self.retries + 1
        for attempt in range(attempts):
            try:
                return operation()
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
