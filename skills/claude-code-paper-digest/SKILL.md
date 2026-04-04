---
name: claude-code-paper-digest
description: Use when Claude Code needs to fetch recent papers by configurable keywords and write a Markdown digest to a chosen output_path.
---

# Claude Code Paper Digest

## Overview
Use `sh scripts/run_cli.sh` to resolve a compatible Python automatically, then run the shared `paper-daily-fetch` pipeline CLI to discover, enrich, rank, and render a Markdown digest to `output_path`.

## Inputs
- `topic`: topic name in `config/paper_fetch.toml`
- `days`: optional lookback window override
- `limit`: optional top N override
- `output_path`: Markdown destination

## Commands
```bash
sh scripts/run_cli.sh pipeline daily --config config/paper_fetch.toml --topic <topic> --days <days> --limit <limit> --include-seen --output /tmp/rank.json
sh scripts/run_cli.sh annotate --input /tmp/rank.json --annotations /tmp/annotations.json --output /tmp/annotated.json
sh scripts/run_cli.sh render --target markdown --input /tmp/annotated.json --output <output_path>
```

For step-by-step debugging:

```bash
sh scripts/run_cli.sh discover --config config/paper_fetch.toml --topic <topic> --days <days> --output /tmp/discover.json
sh scripts/run_cli.sh enrich --config config/paper_fetch.toml --input /tmp/discover.json --output /tmp/enrich.json
sh scripts/run_cli.sh rank --config config/paper_fetch.toml --topic <topic> --input /tmp/enrich.json --limit <limit> --output /tmp/rank.json
sh scripts/run_cli.sh annotate --input /tmp/rank.json --annotations /tmp/annotations.json --output /tmp/annotated.json
sh scripts/run_cli.sh render --target markdown --input /tmp/annotated.json --output <output_path>
```

## Required Behavior
- Keep the output in Chinese unless the user explicitly overrides it.
- Before the first CLI call, resolve Python with `sh scripts/resolve_python.sh`.
- If a compatible interpreter exists, proceed without asking the user to upgrade Python.
- Only if no compatible interpreter exists, or runtime still fails after using the resolved interpreter, ask whether the user wants help locating Python 3.11+, creating a virtual environment, or adjusting the install flow.
- Before running `annotate`, create `/tmp/annotations.json` with the following schema — one entry per paper using the `arxiv_id` values returned by the previous step:

```json
{
  "papers": [
    {
      "arxiv_id": "<id from rank output>",
      "summary_zh": "<full faithful Chinese translation of the English abstract — not a compressed summary>",
      "positive_take": "<one sentence: the paper's key contribution in positive framing>",
      "critical_take": "<one sentence: a sharp, honest critique compared with prior work>"
    }
  ]
}
```

- Use `output_path` as the final artifact path.
- For manual runs, prefer `--include-seen` so the digest is reproducible.
