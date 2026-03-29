# OpenClaw Installation

## One-Line Installer

Tell OpenClaw:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/k4pl3r/paper-daily-fetch-skills/main/.openclaw/INSTALL.md, install the skill using your native skill or extension mechanism, and then tell me how to request a digest into a target chat.
```

## Manual Fallback

OpenClaw support in this repository is intentionally prompt-driven. If the one-line installer does not work, ask OpenClaw to:

1. Clone `https://github.com/k4pl3r/paper-daily-fetch-skills.git`
2. Inspect its current local skill or extension layout
3. Register `skills/openclaw-paper-digest/SKILL.md` using the same native pattern
4. Confirm how `target_chat` should be supplied

## What To Use After Install

- Skill: `skills/openclaw-paper-digest/SKILL.md`
- Default config: `config/paper_fetch.toml`
- Output mode: push-ready OpenClaw payload

## Example Request

```text
Use the openclaw-paper-digest skill to fetch the newest video-generation papers and prepare a digest for target_chat=paper-daily-chat
```

