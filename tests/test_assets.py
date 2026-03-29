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
