from __future__ import annotations

from dataclasses import replace

from ..models import PaperRecord


def apply_annotations(
    papers: list[PaperRecord],
    annotations: list[dict[str, str | None]],
) -> list[PaperRecord]:
    by_id = {
        item["arxiv_id"]: item
        for item in annotations
        if item.get("arxiv_id")
    }
    annotated: list[PaperRecord] = []
    for paper in papers:
        patch = by_id.get(paper.arxiv_id)
        if not patch:
            annotated.append(paper)
            continue
        annotated.append(
            replace(
                paper,
                summary_zh=patch.get("summary_zh") or paper.summary_zh,
                positive_take=patch.get("positive_take") or paper.positive_take,
                critical_take=patch.get("critical_take") or paper.critical_take,
            )
        )
    return annotated
