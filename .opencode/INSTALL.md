# Installing paper-daily-fetch-skills for OpenCode

Install this repository so OpenCode can discover the bundled paper digest skills.

## Agent-Facing Goal

Clone this repository locally, add its `skills/` directory to OpenCode skill discovery, restart or refresh OpenCode, and verify that the OpenCode paper digest skill is available.

Repository:

```text
https://github.com/k4pl3r/paper-daily-fetch-skills.git
```

## Recommended Steps

1. Clone the repository to a stable local path such as:

```bash
git clone https://github.com/k4pl3r/paper-daily-fetch-skills.git ~/.config/opencode/paper-daily-fetch-skills
```

2. Register the repository `skills/` directory with OpenCode. Prefer the native skill discovery setting if available. If OpenCode uses `skills.paths`, add:

```json
{
  "skills": {
    "paths": ["~/.config/opencode/paper-daily-fetch-skills/skills"]
  }
}
```

3. Restart OpenCode or refresh the skill index.

4. Verify that `opencode-paper-digest` is discoverable, then summarize:
   - clone path
   - configured skill path
   - how to use `sh scripts/resolve_python.sh` and `sh scripts/run_cli.sh pipeline daily`, then generate `/tmp/annotations.json` with a full Chinese translation for each abstract plus `positive_take` and `critical_take`, then run `sh scripts/run_cli.sh annotate` and `sh scripts/run_cli.sh render` to render a markdown digest

Important runtime rule:

- Do not ask the user to upgrade Python just because `python3` is older.
- First run `sh scripts/resolve_python.sh` and use the compatible interpreter it finds.
- Only if no compatible interpreter exists, or runtime still fails after using it, ask whether the user wants help locating Python 3.11+, creating a virtual environment, or adjusting the install flow.

## Skill To Use

Primary skill for OpenCode:

```text
skills/opencode-paper-digest/SKILL.md
```

## If Something Fails

Inspect the local OpenCode config format and adapt the registration step to its native discovery mechanism rather than assuming `skills.paths`.
