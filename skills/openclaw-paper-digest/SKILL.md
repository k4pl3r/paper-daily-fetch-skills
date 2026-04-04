---
name: openclaw-paper-digest
description: Use when OpenClaw needs to fetch recent papers by keywords and send a push-ready digest into a group chat or target conversation.
---

# OpenClaw Paper Digest

## Overview
Use `sh scripts/run_cli.sh` to resolve a compatible Python automatically, then run the shared `paper-daily-fetch` pipeline CLI and render an OpenClaw payload. This skill does not send messages itself; it produces a ready-to-send payload with `target_chat`.

## Inputs
- `topic`: topic name in `config/paper_fetch.toml`
- `days`: optional lookback window override
- `limit`: optional top N override
- `target_chat`: optional conversation or group id override

## Commands
```bash
sh scripts/run_cli.sh pipeline daily --config config/paper_fetch.toml --topic <topic> --days <days> --limit <limit> --output /tmp/rank.json
sh scripts/run_cli.sh annotate --input /tmp/rank.json --annotations /tmp/annotations.json --output /tmp/annotated.json
sh scripts/run_cli.sh render --target openclaw --input /tmp/annotated.json --output /tmp/openclaw_payload.json --target-chat <target_chat>
```

For step-by-step debugging:

```bash
sh scripts/run_cli.sh discover --config config/paper_fetch.toml --topic <topic> --days <days> --output /tmp/discover.json
sh scripts/run_cli.sh enrich --config config/paper_fetch.toml --input /tmp/discover.json --output /tmp/enrich.json
sh scripts/run_cli.sh rank --config config/paper_fetch.toml --topic <topic> --input /tmp/enrich.json --limit <limit> --output /tmp/rank.json
sh scripts/run_cli.sh annotate --input /tmp/rank.json --annotations /tmp/annotations.json --output /tmp/annotated.json
sh scripts/run_cli.sh render --target openclaw --input /tmp/annotated.json --output /tmp/openclaw_payload.json --target-chat <target_chat>
```

## Required Behavior
- Default to `config/paper_fetch.toml` when the user does not provide a topic.
- Before the first CLI call, resolve Python with `sh scripts/resolve_python.sh`.
- If a compatible interpreter exists, proceed without asking the user to upgrade Python.
- Only if no compatible interpreter exists, or runtime still fails after using the resolved interpreter, ask whether the user wants help locating Python 3.11+, creating a virtual environment, or adjusting the install flow.
- Before `render`, automatically create `/tmp/annotations.json` with a full Chinese translation in `summary_zh`, plus `positive_take` and `critical_take` for each paper.
- Use the rendered JSON payload directly.
- Preserve `target_chat` in the final output.
- If the user asks for “new papers”, prefer the default pipeline path over the legacy `collect` wrapper.
