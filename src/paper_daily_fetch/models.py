from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class FigureSelection:
    url: str
    reason: str


@dataclass(slots=True)
class PaperRecord:
    arxiv_id: str
    title: str
    authors: list[str]
    published_at: str
    abstract: str
    paper_url: str
    code_url: str | None
    figure_url_or_path: str | None
    figure_reason: str | None
    topic_matches: list[str]
    source: str | None = None
    sources: list[str] = field(default_factory=list)
    canonical_url: str | None = None
    institutions: list[str] = field(default_factory=list)
    score: float | None = None
    match_reason: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PaperRecord":
        return cls(
            arxiv_id=data["arxiv_id"],
            title=data["title"],
            authors=list(data.get("authors", [])),
            published_at=data["published_at"],
            abstract=data["abstract"],
            paper_url=data["paper_url"],
            code_url=data.get("code_url"),
            figure_url_or_path=data.get("figure_url_or_path"),
            figure_reason=data.get("figure_reason"),
            topic_matches=list(data.get("topic_matches", [])),
            source=data.get("source"),
            sources=list(data.get("sources", [])),
            canonical_url=data.get("canonical_url"),
            institutions=list(data.get("institutions", [])),
            score=data.get("score"),
            match_reason=list(data.get("match_reason", [])),
        )
