from __future__ import annotations

import json
from pathlib import Path


class PublishHistoryStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def filter_new(self, arxiv_ids: list[str]) -> list[str]:
        seen = self._load()
        return [paper_id for paper_id in arxiv_ids if paper_id not in seen]

    def mark_published(self, arxiv_ids: list[str]) -> None:
        seen = self._load()
        seen.update(arxiv_ids)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"published_ids": sorted(seen)}, ensure_ascii=False, indent=2)
        )

    def _load(self) -> set[str]:
        if not self.path.exists():
            return set()
        data = json.loads(self.path.read_text())
        return set(data.get("published_ids", []))
