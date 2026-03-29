# Installing paper-daily-fetch-skills for Codex

Install this repository through Codex native skill discovery.

## Agent-Facing Goal

Clone this repository locally, make the `skills/` directory discoverable to Codex, then verify that the Codex paper digest skill is available.

Repository:

```text
https://github.com/k4pl3r/paper-daily-fetch-skills.git
```

## Recommended Steps

1. Clone the repository to a stable local path such as:

```bash
git clone https://github.com/k4pl3r/paper-daily-fetch-skills.git ~/.codex/paper-daily-fetch-skills
```

2. Register the repository skills through Codex native discovery:

```bash
mkdir -p ~/.agents/skills
ln -s ~/.codex/paper-daily-fetch-skills/skills ~/.agents/skills/paper-daily-fetch-skills
```

3. Restart Codex or refresh skill discovery.

4. Verify the install by checking that `codex-paper-digest` is discoverable, then summarize:
   - where the repo was cloned
   - where the skills symlink points
   - how to use the Codex skill to generate a markdown digest

## Skill To Use

Primary skill for Codex:

```text
skills/codex-paper-digest/SKILL.md
```

## If Something Fails

Inspect the current Codex skills directory, adjust the clone or symlink path to match the local environment, and report the exact change you made.

