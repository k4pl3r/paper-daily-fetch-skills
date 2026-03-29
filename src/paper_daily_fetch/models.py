from __future__ import annotations

from dataclasses import asdict, dataclass
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
        )

