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

## Example Request

```text
Use the opencode-paper-digest skill to fetch papers for world-model, automatically produce a full Chinese translation for each abstract plus positive and critical one-liners, and write the rendered markdown digest to ./reports/world-model.md
```
