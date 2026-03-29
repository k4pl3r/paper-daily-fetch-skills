# Skill Usage Examples

## OpenClaw

```bash
paper-daily-fetch collect --config config/paper_fetch.toml --topic video-generation > /tmp/papers.json
paper-daily-fetch render --target openclaw --input /tmp/papers.json --output /tmp/openclaw_payload.json --target-chat group-42
```

## Codex

```bash
paper-daily-fetch collect --config config/paper_fetch.toml --topic world-model --include-seen > /tmp/papers.json
paper-daily-fetch render --target markdown --input /tmp/papers.json --output ./reports/world-model.md
```

## Claude Code

```bash
paper-daily-fetch collect --config config/paper_fetch.toml --topic 3dgs-reconstruction --include-seen > /tmp/papers.json
paper-daily-fetch render --target markdown --input /tmp/papers.json --output ./reports/3dgs.md
```

## OpenCode

```bash
paper-daily-fetch collect --config config/paper_fetch.toml --topic video-generation --include-seen > /tmp/papers.json
paper-daily-fetch render --target markdown --input /tmp/papers.json --output ./reports/video-generation.md
```

