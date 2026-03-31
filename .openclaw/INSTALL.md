# Installing paper-daily-fetch-skills for OpenClaw

Install this repository so OpenClaw can use the paper digest skill and remember how to run it later.

## Agent-Facing Goal

Clone this repository, inspect the current OpenClaw skill or prompt-extension conventions, install the OpenClaw paper digest skill using the native mechanism available in the local environment, then verify that the skill is usable.

Repository:

```text
https://github.com/k4pl3r/paper-daily-fetch-skills.git
```

## Required Outcomes

1. Place the repository in a stable local path.
2. Register or import the OpenClaw skill from:

```text
skills/openclaw-paper-digest/SKILL.md
```

3. Make sure OpenClaw also knows this repository includes the shared Python CLI and config file:
   - `src/paper_daily_fetch`
   - `config/paper_fetch.toml`

4. Verify the install by summarizing:
   - where the repository was placed
   - which OpenClaw mechanism was used to register the skill
   - how to target a chat and request a paper digest using `paper-daily-fetch pipeline daily`, then generate `/tmp/annotations.json` with a full Chinese translation for each abstract plus `positive_take` and `critical_take`, then run `paper-daily-fetch annotate` and `paper-daily-fetch render --target openclaw`

## Installation Strategy

Prefer OpenClaw's native skill or extension registration flow. If there is no single documented mechanism, inspect the local environment for existing installed skills, prompts, or plugin directories and follow the established pattern instead of inventing a new one.

## If Something Fails

Report the exact blocker, inspect the local OpenClaw install layout, and choose the nearest native pattern that successfully registers `openclaw-paper-digest`.
