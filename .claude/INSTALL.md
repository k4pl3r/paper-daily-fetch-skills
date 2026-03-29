# Installing paper-daily-fetch-skills for Claude Code

Install this repository so Claude Code can discover and use the paper digest skill.

## Agent-Facing Goal

Clone this repository locally, register its `skills/` directory with Claude Code, verify that the Claude Code paper digest skill is available, then explain how to use it.

Repository:

```text
https://github.com/k4pl3r/paper-daily-fetch-skills.git
```

## Recommended Steps

1. Clone the repository to a stable local path such as:

```bash
git clone https://github.com/k4pl3r/paper-daily-fetch-skills.git ~/.claude/paper-daily-fetch-skills
```

2. Register the repository `skills/` directory with Claude Code. If Claude Code uses a filesystem skills directory, place or symlink the repo skills there, for example:

```bash
mkdir -p ~/.claude/skills
ln -s ~/.claude/paper-daily-fetch-skills/skills ~/.claude/skills/paper-daily-fetch-skills
```

3. Refresh Claude Code skill discovery or start a new session.

4. Verify that `claude-code-paper-digest` is discoverable, then summarize:
   - clone path
   - registered skills path
   - how to use `paper-daily-fetch pipeline daily` and `paper-daily-fetch render` to generate a markdown digest

## Skill To Use

Primary skill for Claude Code:

```text
skills/claude-code-paper-digest/SKILL.md
```

## If Something Fails

Inspect the local Claude Code skill registration conventions and adapt the registration step to the native mechanism in that environment.
