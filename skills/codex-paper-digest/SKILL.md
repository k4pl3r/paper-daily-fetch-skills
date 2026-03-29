---
name: codex-paper-digest
description: Use when Codex needs to fetch recent papers by configurable keywords and write a Markdown digest to a chosen output_path.
---

# Codex Paper Digest

## Overview
Use the shared `paper-daily-fetch` CLI to collect papers, then render a Markdown digest to `output_path`.

## Inputs
- `topic`: topic name in `config/paper_fetch.toml`
- `days`: optional lookback window override
- `limit`: optional top N override
- `output_path`: Markdown destination

## Commands
```bash
paper-daily-fetch collect --config config/paper_fetch.toml --topic <topic> --days <days> --limit <limit> --include-seen > /tmp/papers.json
paper-daily-fetch render --target markdown --input /tmp/papers.json --output <output_path>
```

## Required Behavior
- Default to `config/paper_fetch.toml` when the user does not provide a topic.
- For on-demand usage, include seen papers so repeated manual runs still produce a full digest.
- Write the final Markdown to `output_path`.

