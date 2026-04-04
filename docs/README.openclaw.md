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
- Runtime wrapper: `sh scripts/resolve_python.sh` then `sh scripts/run_cli.sh ...`

## Python Runtime Rule

- This repository currently requires Python 3.11+.
- Do not ask the user to upgrade Python just because `python3` is older.
- First run `sh scripts/resolve_python.sh` and use the compatible interpreter it finds.
- Only if no compatible interpreter exists, or runtime still fails after using it, ask whether the user wants help locating Python 3.11+ or creating a virtual environment.

## Example Request

```text
Use the openclaw-paper-digest skill to fetch papers for video-generation, automatically produce a full Chinese translation for each abstract plus positive and critical one-liners, and prepare a rendered OpenClaw digest for target_chat=paper-daily-chat
```
