from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .config import load_config
from .models import PaperRecord
from .render import render_markdown, render_openclaw_payload
from .service import collect_papers

DEFAULT_CONFIG_PATH = Path("config/paper_fetch.toml")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="paper-daily-fetch")
    subparsers = parser.add_subparsers(dest="command", required=True)

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


def collect_command(args: argparse.Namespace) -> dict[str, object]:
    config = load_config(args.config)
    return collect_papers(
        config=config,
        topic_name=args.topic,
        days=args.days,
        limit=args.limit,
        include_seen=args.include_seen,
    )


def render_command(args: argparse.Namespace) -> str | dict[str, object]:
    payload = json.loads(Path(args.input).read_text())
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
    if args.command == "collect":
        result = collect_command(args)
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
        sys.stdout.write("\n")
        return 0

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


if __name__ == "__main__":
    raise SystemExit(main())

