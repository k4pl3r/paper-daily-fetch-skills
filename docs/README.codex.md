# Codex Installation

## One-Line Installer

Tell Codex:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/k4pl3r/paper-daily-fetch-skills/main/.codex/INSTALL.md
```

## Manual Install

```bash
git clone https://github.com/k4pl3r/paper-daily-fetch-skills.git ~/.codex/paper-daily-fetch-skills
mkdir -p ~/.agents/skills
ln -s ~/.codex/paper-daily-fetch-skills/skills ~/.agents/skills/paper-daily-fetch-skills
```

Restart Codex after creating the symlink.

## What To Use After Install

- Skill: `skills/codex-paper-digest/SKILL.md`
- Default config: `config/paper_fetch.toml`
- Output mode: Markdown file

## Example Request

```text
Use the codex-paper-digest skill to fetch the latest video-generation papers and write the digest to ./reports/video-generation.md
```

