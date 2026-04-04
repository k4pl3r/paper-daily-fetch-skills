# paper-daily-fetch-skills

`paper-daily-fetch-skills` is a public skill repository for OpenClaw, Codex, Claude Code, and OpenCode. It helps agents discover fresh papers from multiple sources, merge and enrich them, keep only the most relevant ones for your topic keywords, attach a representative figure, and output either a push-ready OpenClaw message or a Markdown digest.

## Why This Repo Exists

- Track new papers for topics like video generation, world models, and 3D Gaussian Splatting
- Keep the install flow lightweight for multiple agent tools
- Separate public installation docs from the real skill logic in `skills/`
- Reuse the same Python pipeline CLI and config across all supported tools

## Supported Agents

- OpenClaw
- Codex
- Claude Code
- OpenCode

## One-Line Installers

Copy the matching block below into your agent.

### OpenClaw

```text
Fetch and follow instructions from https://raw.githubusercontent.com/k4pl3r/paper-daily-fetch-skills/main/.openclaw/INSTALL.md, install the skill using your native skill or extension mechanism, and then tell me how to request a digest into a target chat.
```

### Codex

```text
Fetch and follow instructions from https://raw.githubusercontent.com/k4pl3r/paper-daily-fetch-skills/main/.codex/INSTALL.md
```

### Claude Code

```text
Fetch and follow instructions from https://raw.githubusercontent.com/k4pl3r/paper-daily-fetch-skills/main/.claude/INSTALL.md
```

### OpenCode

```text
Fetch and follow instructions from https://raw.githubusercontent.com/k4pl3r/paper-daily-fetch-skills/main/.opencode/INSTALL.md
```

## Manual Install And Detailed Docs

| Tool | Quick Doc | Notes |
| --- | --- | --- |
| OpenClaw | `docs/README.openclaw.md` | Prompt-driven install flow |
| Codex | `docs/README.codex.md` | Native skill discovery via repo clone + skills registration |
| Claude Code | `docs/README.claude-code.md` | One-line prompt plus manual fallback |
| OpenCode | `docs/README.opencode.md` | One-line prompt plus configurable skill path fallback |

## What You Get After Install

- `skills/openclaw-paper-digest/SKILL.md`
- `skills/codex-paper-digest/SKILL.md`
- `skills/claude-code-paper-digest/SKILL.md`
- `skills/opencode-paper-digest/SKILL.md`

Default behavior:

- multi-source retrieval: HuggingFace Daily / Trending + arXiv API + arXiv search fallback
- keyword + negative keyword + domain boost ranking
- top 3 papers by default after ranking
- Chinese output
- prefer overview/pipeline figure, then fallback to the first image
- runtime wrapper scripts in `scripts/` choose a compatible Python automatically before running the CLI

## What The Agent Can Do

- Fetch recent papers for a configured topic
- Merge duplicate candidates from multiple sources
- Rank papers by keyword, negative keyword, and domain boost match
- Attach a code link when one is discoverable
- Pick an overview, pipeline, framework, or fallback figure
- Render a Markdown digest or OpenClaw-ready payload

Pipeline stages:

- `discover` for multi-source candidate collection
- `enrich` for metadata, code link, and figure fallback
- `rank` for final scoring and filtering
- `annotate` for a host-agent-generated full Chinese translation of each abstract plus positive and critical takes
- `render` for Markdown or OpenClaw output

Runtime behavior:

- the repository currently requires Python 3.11+
- agents should first run `sh scripts/resolve_python.sh`
- if a compatible interpreter already exists, use `sh scripts/run_cli.sh ...` and do not ask the user to upgrade Python
- only if no compatible interpreter is found, or a real runtime error still occurs, ask whether the user wants help creating a virtual environment or updating Python

Example outputs:

- [examples/sample_collect.json](examples/sample_collect.json)
- [examples/sample_openclaw_payload.json](examples/sample_openclaw_payload.json)
- [examples/sample_digest.md](examples/sample_digest.md)

## Project Structure

```text
.
├── skills/            # Real skill documents used by agents
├── .codex/            # Codex install entrypoint
├── .claude/           # Claude Code install entrypoint
├── .openclaw/         # OpenClaw install entrypoint
├── .opencode/         # OpenCode install entrypoint
├── docs/              # Human-readable installation details
├── scripts/           # Python detection and CLI wrapper scripts
├── src/               # Shared Python CLI
├── config/            # Default topic and output config
└── examples/          # Sample outputs
```

## FAQ

### Will changing the README break the skills?

Not by itself. Skill behavior depends on the real files in `skills/` and on each tool's install entrypoint continuing to point to those files. This is why the repo keeps README, install docs, and skill paths as separate layers.

### Where do I change topics and defaults?

Edit `config/paper_fetch.toml`.

### Where is the developer-facing CLI usage?

The shared CLI lives in `src/paper_daily_fetch`. The homepage keeps install and usage simple; implementation details can stay in the code, examples, and tool-specific docs. The preferred path is `sh scripts/run_cli.sh ...`, which resolves a compatible Python first, then runs `discover -> enrich -> rank -> annotate -> render` or `pipeline daily` plus an explicit annotation step.

## Updating

- Re-run the same installer prompt in your agent, or
- Pull the latest version of this repository and keep the registered skill path pointing at it

## Contributing

Issues and pull requests are welcome. Keep public install paths stable once they are published in the README.
