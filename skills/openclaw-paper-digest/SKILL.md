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
# Deliver /tmp/openclaw_payload.json to the target chat via the OpenClaw API or tool.
# Only after confirmed delivery:
sh scripts/run_cli.sh publish --input /tmp/annotated.json
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

- Use the rendered JSON payload directly.
- Preserve `target_chat` in the final output.
- **Do not** pass `--include-seen` to `pipeline daily` for automated / scheduled runs. Omitting it activates history-based deduplication so papers that have already been pushed to the target chat are not sent again. Only add `--include-seen` when the user explicitly wants a full repeat of the digest regardless of history.
- Only run `sh scripts/run_cli.sh publish --input /tmp/annotated.json` after the payload has actually been delivered successfully. Do not mark papers as published before the final send step succeeds.
- If the user asks for "new papers", prefer the default pipeline path over the legacy `collect` wrapper.
