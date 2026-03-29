# Claude Code Installation

## One-Line Installer

Tell Claude Code:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/k4pl3r/paper-daily-fetch-skills/main/.claude/INSTALL.md
```

## Manual Install

```bash
git clone https://github.com/k4pl3r/paper-daily-fetch-skills.git ~/.claude/paper-daily-fetch-skills
mkdir -p ~/.claude/skills
ln -s ~/.claude/paper-daily-fetch-skills/skills ~/.claude/skills/paper-daily-fetch-skills
```

Start a new Claude Code session after registration.

## What To Use After Install

- Skill: `skills/claude-code-paper-digest/SKILL.md`
- Default config: `config/paper_fetch.toml`
- Output mode: Markdown file

## Example Request

```text
Use the claude-code-paper-digest skill to run paper-daily-fetch pipeline daily for 3dgs-reconstruction and write the rendered markdown digest to ./reports/3dgs.md
```
