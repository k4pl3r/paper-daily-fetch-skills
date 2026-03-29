---
name: openclaw-paper-digest
description: Use when OpenClaw needs to fetch recent papers by keywords and send a push-ready digest into a group chat or target conversation.
---

# OpenClaw Paper Digest

## Overview
Use the shared `paper-daily-fetch` pipeline CLI, then render an OpenClaw payload. This skill does not send messages itself; it produces a ready-to-send payload with `target_chat`.

## Inputs
- `topic`: topic name in `config/paper_fetch.toml`
- `days`: optional lookback window override
- `limit`: optional top N override
- `target_chat`: optional conversation or group id override

## Commands
```bash
paper-daily-fetch pipeline daily --config config/paper_fetch.toml --topic <topic> --days <days> --limit <limit> --output /tmp/rank.json
paper-daily-fetch render --target openclaw --input /tmp/rank.json --output /tmp/openclaw_payload.json --target-chat <target_chat>
```

For step-by-step debugging:

```bash
paper-daily-fetch discover --config config/paper_fetch.toml --topic <topic> --days <days> --output /tmp/discover.json
paper-daily-fetch enrich --config config/paper_fetch.toml --input /tmp/discover.json --output /tmp/enrich.json
paper-daily-fetch rank --config config/paper_fetch.toml --topic <topic> --input /tmp/enrich.json --limit <limit> --output /tmp/rank.json
paper-daily-fetch render --target openclaw --input /tmp/rank.json --output /tmp/openclaw_payload.json --target-chat <target_chat>
```

## Required Behavior
- Default to `config/paper_fetch.toml` when the user does not provide a topic.
- Use the rendered JSON payload directly.
- Preserve `target_chat` in the final output.
- If the user asks for “new papers”, prefer the default pipeline path over the legacy `collect` wrapper.
