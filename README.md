# paper-daily-fetch-skills

Cross-agent paper fetching and rendering skills for OpenClaw, Codex, Claude Code, and OpenCode.

## What This Repo Provides

- A Python CLI for discovering new arXiv papers with keyword filters
- Ranking, code link enrichment, figure selection, and state-based deduplication
- Four host-specific skill packages
- Markdown and OpenClaw renderers

## Default Behavior

- arXiv-first retrieval
- keyword-list topic matching
- top 3 papers by default
- Chinese output
- prefer overview/pipeline figure, then fallback to the first image

## Install And Run

```bash
python3 -m pip install -e .
paper-daily-fetch collect --config config/paper_fetch.toml --topic video-generation
paper-daily-fetch render --target markdown --input examples/sample_collect.json --output examples/output/daily.md
```

For local development without installation:

```bash
PYTHONPATH=src python3 -m paper_daily_fetch collect --config config/paper_fetch.toml --topic video-generation
PYTHONPATH=src python3 -m paper_daily_fetch render --target markdown --input examples/sample_collect.json --output examples/output/daily.md
```

## Skill Layout

- `skills/openclaw-paper-digest`
- `skills/codex-paper-digest`
- `skills/claude-code-paper-digest`
- `skills/opencode-paper-digest`

## Config

Edit [config/paper_fetch.toml](/Users/kapler/paper-daily-fetch-skills/config/paper_fetch.toml) to change topics, keywords, lookback window, output defaults, and OpenClaw target chat.

## Example Artifacts

- [examples/sample_collect.json](/Users/kapler/paper-daily-fetch-skills/examples/sample_collect.json)
- [examples/sample_openclaw_payload.json](/Users/kapler/paper-daily-fetch-skills/examples/sample_openclaw_payload.json)
- [examples/sample_digest.md](/Users/kapler/paper-daily-fetch-skills/examples/sample_digest.md)
