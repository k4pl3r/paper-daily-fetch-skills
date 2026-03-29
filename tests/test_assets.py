from pathlib import Path


def test_skill_documents_exist_with_expected_entrypoints():
    expectations = {
        "openclaw-paper-digest": "target_chat",
        "codex-paper-digest": "output_path",
        "claude-code-paper-digest": "output_path",
        "opencode-paper-digest": "output_path",
    }
    for skill_name, required_token in expectations.items():
        content = Path(f"skills/{skill_name}/SKILL.md").read_text()
        assert "paper-daily-fetch collect" in content
        assert "paper-daily-fetch render" in content
        assert required_token in content


def test_example_artifacts_exist():
    assert Path("examples/sample_collect.json").exists()
    assert Path("examples/sample_openclaw_payload.json").exists()
    assert Path("examples/sample_digest.md").exists()


def test_install_entrypoints_and_docs_exist():
    required_paths = [
        ".codex/INSTALL.md",
        ".opencode/INSTALL.md",
        ".claude/INSTALL.md",
        ".openclaw/INSTALL.md",
        "docs/README.codex.md",
        "docs/README.opencode.md",
        "docs/README.claude-code.md",
        "docs/README.openclaw.md",
    ]
    for path in required_paths:
        assert Path(path).exists(), path


def test_readme_publishes_real_install_entrypoints():
    readme = Path("README.md").read_text()
    expected_urls = [
        "https://raw.githubusercontent.com/k4pl3r/paper-daily-fetch-skills/main/.codex/INSTALL.md",
        "https://raw.githubusercontent.com/k4pl3r/paper-daily-fetch-skills/main/.opencode/INSTALL.md",
        "https://raw.githubusercontent.com/k4pl3r/paper-daily-fetch-skills/main/.claude/INSTALL.md",
        "https://raw.githubusercontent.com/k4pl3r/paper-daily-fetch-skills/main/.openclaw/INSTALL.md",
    ]
    for url in expected_urls:
        assert url in readme
    assert "skills/openclaw-paper-digest/SKILL.md" in readme
    assert "skills/codex-paper-digest/SKILL.md" in readme
    assert "skills/claude-code-paper-digest/SKILL.md" in readme
    assert "skills/opencode-paper-digest/SKILL.md" in readme
