from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .config import load_config
from .history import PublishHistoryStore
from .models import PaperRecord
from .pipeline.annotate import apply_annotations
from .pipeline.discover import discover_candidates
from .pipeline.enrich import enrich_candidates
from .pipeline.rank import rank_candidates
from .render import render_markdown, render_openclaw_payload
from .service import collect_papers
from .infra.http import HttpClient

DEFAULT_CONFIG_PATH = Path("config/paper_fetch.toml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="paper-daily-fetch")
    subparsers = parser.add_subparsers(dest="command", required=True)

    discover = subparsers.add_parser("discover")
    discover.add_argument("--topic")
    discover.add_argument("--days", type=int)
    discover.add_argument("--sources")
    discover.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    discover.add_argument("--output")

    enrich = subparsers.add_parser("enrich")
    enrich.add_argument("--input", required=True)
    enrich.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    enrich.add_argument("--output")

    rank = subparsers.add_parser("rank")
    rank.add_argument("--input", required=True)
    rank.add_argument("--topic")
    rank.add_argument("--limit", type=int)
    rank.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    rank.add_argument("--output")

    annotate = subparsers.add_parser("annotate")
    annotate.add_argument("--input", required=True)
    annotate.add_argument("--annotations", required=True)
    annotate.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    annotate.add_argument("--output")

    publish = subparsers.add_parser("publish")
    publish.add_argument("--input", required=True)
    publish.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    publish.add_argument("--output")

    pipeline = subparsers.add_parser("pipeline")
    pipeline_subparsers = pipeline.add_subparsers(
        dest="pipeline_command", required=True
    )
    pipeline_daily = pipeline_subparsers.add_parser("daily")
    pipeline_daily.add_argument("--topic")
    pipeline_daily.add_argument("--days", type=int)
    pipeline_daily.add_argument("--limit", type=int)
    pipeline_daily.add_argument("--sources")
    pipeline_daily.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    pipeline_daily.add_argument("--output")
    pipeline_daily.add_argument("--include-seen", action="store_true")

    collect = subparsers.add_parser("collect")
    collect.add_argument("--topic")
    collect.add_argument("--days", type=int)
    collect.add_argument("--limit", type=int)
    collect.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    collect.add_argument("--format", default="json", choices=["json"])
    collect.add_argument("--include-seen", action="store_true")

    render = subparsers.add_parser("render")
    render.add_argument("--target", required=True, choices=["openclaw", "markdown"])
    render.add_argument("--input", required=True)
    render.add_argument("--output")
    render.add_argument("--target-chat")

    return parser


def discover_command(args: argparse.Namespace) -> dict[str, object]:
    config = load_config(args.config)
    topic = args.topic or config.default_topic
    sources = (
        [item.strip() for item in args.sources.split(",") if item.strip()]
        if args.sources
        else config.sources.enabled
    )
    client = HttpClient(
        retries=config.sources.retries,
        backoff_seconds=config.sources.backoff_seconds,
        timeout=config.sources.timeout,
    )
    papers = discover_candidates(
        topic_name=topic,
        keywords=config.topic_keywords(topic),
        days=args.days or config.lookback_days,
        enabled_sources=sources,
        http_client=client,
        candidate_limit=config.discover.candidate_limit,
    )
    return {
        "topic": topic,
        "generated_at": _now(),
        "papers": [paper.to_dict() for paper in papers],
    }


def enrich_command(args: argparse.Namespace) -> dict[str, object]:
    config = load_config(args.config)
    payload = _read_payload(args.input)
    client = HttpClient(
        retries=config.sources.retries,
        backoff_seconds=config.sources.backoff_seconds,
        timeout=config.sources.timeout,
    )
    papers = [PaperRecord.from_dict(item) for item in payload.get("papers", [])]
    enriched = enrich_candidates(
        papers,
        http_get=client.get_text,
        http_get_bytes=client.get_bytes,
        cache_dir=config.cache_dir,
        max_workers=config.enrich.max_workers,
        timeout=config.enrich.timeout,
    )
    return {
        "topic": payload.get("topic", config.default_topic),
        "generated_at": payload.get("generated_at", _now()),
        "papers": [paper.to_dict() for paper in enriched],
    }


def rank_command(args: argparse.Namespace) -> dict[str, object]:
    config = load_config(args.config)
    payload = _read_payload(args.input)
    topic = args.topic or payload.get("topic") or config.default_topic
    papers = [PaperRecord.from_dict(item) for item in payload.get("papers", [])]
    ranked = rank_candidates(
        papers,
        keywords=config.topic_keywords(topic),
        negative_keywords=config.topic_negative_keywords(topic),
        domain_boost_keywords=config.topic_domain_boost_keywords(topic),
        limit=args.limit or config.rank.final_limit,
    )
    return {
        "topic": topic,
        "generated_at": payload.get("generated_at", _now()),
        "papers": [paper.to_dict() for paper in ranked],
    }


def annotate_command(args: argparse.Namespace) -> dict[str, object]:
    config = load_config(args.config)
    payload = _read_payload(args.input)
    annotations_payload = _read_payload(args.annotations)
    papers = [PaperRecord.from_dict(item) for item in payload.get("papers", [])]
    annotated = apply_annotations(papers, annotations_payload.get("papers", []))
    return {
        "topic": payload.get("topic", config.default_topic),
        "generated_at": payload.get("generated_at", _now()),
        "papers": [paper.to_dict() for paper in annotated],
    }


def publish_command(args: argparse.Namespace) -> dict[str, object]:
    config = load_config(args.config)
    payload = _read_payload(args.input)
    papers = [PaperRecord.from_dict(item) for item in payload.get("papers", [])]
    published_ids = [paper.arxiv_id for paper in papers if paper.arxiv_id]
    history = PublishHistoryStore(config.history.path)
    if published_ids:
        history.mark_published(published_ids)
    return {
        "published_ids": published_ids,
        "count": len(published_ids),
        "history_path": str(config.history.path),
    }


def pipeline_daily_command(args: argparse.Namespace) -> dict[str, object]:
    config = load_config(args.config)
    topic = args.topic or config.default_topic
    sources = (
        [item.strip() for item in args.sources.split(",") if item.strip()]
        if args.sources
        else config.sources.enabled
    )
    client = HttpClient(
        retries=config.sources.retries,
        backoff_seconds=config.sources.backoff_seconds,
        timeout=config.sources.timeout,
    )
    discovered = discover_candidates(
        topic_name=topic,
        keywords=config.topic_keywords(topic),
        days=args.days or config.lookback_days,
        enabled_sources=sources,
        http_client=client,
        candidate_limit=config.discover.candidate_limit,
    )
    desired_limit = args.limit or config.rank.final_limit
    ranked_candidates = rank_candidates(
        discovered,
        keywords=config.topic_keywords(topic),
        negative_keywords=config.topic_negative_keywords(topic),
        domain_boost_keywords=config.topic_domain_boost_keywords(topic),
        limit=len(discovered),
    )
    if args.include_seen:
        visible_candidates = ranked_candidates
    else:
        history = PublishHistoryStore(config.history.path)
        new_ids = set(history.filter_new([p.arxiv_id for p in ranked_candidates]))
        visible_candidates = [
            paper for paper in ranked_candidates if paper.arxiv_id in new_ids
        ]
    pre_rank_limit = max(config.enrich.pre_rank_limit, desired_limit)
    pre_ranked = visible_candidates[:pre_rank_limit]
    enriched = enrich_candidates(
        pre_ranked,
        http_get=client.get_text,
        http_get_bytes=client.get_bytes,
        cache_dir=config.cache_dir,
        max_workers=config.enrich.max_workers,
        timeout=config.enrich.timeout,
    )
    ranked = rank_candidates(
        enriched,
        keywords=config.topic_keywords(topic),
        negative_keywords=config.topic_negative_keywords(topic),
        domain_boost_keywords=config.topic_domain_boost_keywords(topic),
        limit=desired_limit,
    )
    return {
        "topic": topic,
        "generated_at": _now(),
        "papers": [paper.to_dict() for paper in ranked],
    }


def collect_command(args: argparse.Namespace) -> dict[str, object]:
    return pipeline_daily_command(args)


def render_command(args: argparse.Namespace) -> str | dict[str, object]:
    payload = _read_payload(args.input)
    papers = [PaperRecord.from_dict(item) for item in payload.get("papers", [])]
    topic_name = payload.get("topic", "papers")
    generated_at = payload.get("generated_at", "")
    if args.target == "markdown":
        return render_markdown(
            papers=papers,
            topic_name=topic_name,
            generated_at=generated_at,
        )
    return render_openclaw_payload(
        papers=papers,
        target_chat=args.target_chat,
        topic_name=topic_name,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "discover":
        return _emit_json_or_write(discover_command(args), args.output)
    if args.command == "enrich":
        return _emit_json_or_write(enrich_command(args), args.output)
    if args.command == "rank":
        return _emit_json_or_write(rank_command(args), args.output)
    if args.command == "annotate":
        return _emit_json_or_write(annotate_command(args), args.output)
    if args.command == "publish":
        return _emit_json_or_write(publish_command(args), args.output)
    if args.command == "pipeline":
        if args.pipeline_command == "daily":
            return _emit_json_or_write(pipeline_daily_command(args), args.output)
        raise SystemExit(f"unknown pipeline command: {args.pipeline_command}")
    if args.command == "collect":
        return _emit_json_or_write(collect_command(args), None)

    rendered = render_command(args)
    if isinstance(rendered, dict):
        output = json.dumps(rendered, ensure_ascii=False, indent=2)
    else:
        output = rendered
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output)
    else:
        sys.stdout.write(output)
        if not output.endswith("\n"):
            sys.stdout.write("\n")
    return 0


def _emit_json_or_write(payload: dict[str, object], output: str | None) -> int:
    content = json.dumps(payload, ensure_ascii=False, indent=2)
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content + "\n")
    else:
        sys.stdout.write(content)
        sys.stdout.write("\n")
    return 0


def _read_payload(path: str) -> dict[str, object]:
    return json.loads(Path(path).read_text())


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
