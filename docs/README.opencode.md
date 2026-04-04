# OpenCode Installation

## One-Line Installer

Tell OpenCode:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/k4pl3r/paper-daily-fetch-skills/main/.opencode/INSTALL.md
```

## Manual Install

1. Clone the repository:

```bash
git clone https://github.com/k4pl3r/paper-daily-fetch-skills.git ~/.config/opencode/paper-daily-fetch-skills
```

2. Register the skill path in your OpenCode config if your setup supports `skills.paths`:

```json
{
  "skills": {
    "paths": ["~/.config/opencode/paper-daily-fetch-skills/skills"]
  }
}
```

3. Restart OpenCode or refresh skill discovery.

## What To Use After Install

- Skill: `skills/opencode-paper-digest/SKILL.md`
- Default config: `config/paper_fetch.toml`
- Output mode: Markdown file
- Runtime wrapper: `sh scripts/resolve_python.sh` then `sh scripts/run_cli.sh ...`

## Python Runtime Rule

- This repository currently requires Python 3.11+.
- Do not ask the user to upgrade Python just because `python3` is older.
- First run `sh scripts/resolve_python.sh` and use the compatible interpreter it finds.
- Only if no compatible interpreter exists, or runtime still fails after using it, ask whether the user wants help locating Python 3.11+ or creating a virtual environment.

## Example Request

```text
Use the opencode-paper-digest skill to fetch papers for world-model, automatically produce a full Chinese translation for each abstract plus positive and critical one-liners, and write the rendered markdown digest to ./reports/world-model.md
```
