---
name: claude-code-paper-digest
description: Use when Claude Code needs to fetch recent papers by configurable keywords and write a Markdown digest to a chosen output_path.
---

# Claude Code Paper Digest

## Overview
Use the shared `paper-daily-fetch` pipeline CLI to discover, enrich, rank, and then render a Markdown digest to `output_path`.

## Inputs
- `topic`: topic name in `config/paper_fetch.toml`
- `days`: optional lookback window override
- `limit`: optional top N override
- `output_path`: Markdown destination

## Commands
```bash
paper-daily-fetch pipeline daily --config config/paper_fetch.toml --topic <topic> --days <days> --limit <limit> --include-seen --output /tmp/rank.json
paper-daily-fetch render --target markdown --input /tmp/rank.json --output <output_path>
```

For step-by-step debugging:

```bash
paper-daily-fetch discover --config config/paper_fetch.toml --topic <topic> --days <days> --output /tmp/discover.json
paper-daily-fetch enrich --config config/paper_fetch.toml --input /tmp/discover.json --output /tmp/enrich.json
paper-daily-fetch rank --config config/paper_fetch.toml --topic <topic> --input /tmp/enrich.json --limit <limit> --output /tmp/rank.json
paper-daily-fetch render --target markdown --input /tmp/rank.json --output <output_path>
```

## Required Behavior
- Keep the output in Chinese unless the user explicitly overrides it.
- Use `output_path` as the final artifact path.
- For manual runs, prefer `--include-seen` so the digest is reproducible.
