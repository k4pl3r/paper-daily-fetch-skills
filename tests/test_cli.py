import json
from pathlib import Path

from paper_daily_fetch.cli import main


def test_discover_command_outputs_json(monkeypatch, capsys):
    sample = {
        "topic": "video-generation",
        "generated_at": "2026-03-29T12:00:00+00:00",
        "papers": [
            {
                "arxiv_id": "2603.00001v1",
                "title": "DreamWM",
                "authors": ["Carol Example"],
                "published_at": "2026-03-28T05:00:00+00:00",
                "abstract": "A world model improves controllable video generation quality.",
                "paper_url": "https://arxiv.org/abs/2603.00001v1",
                "code_url": None,
                "figure_url_or_path": None,
                "figure_reason": None,
                "topic_matches": ["video generation"],
                "source": "hf-daily",
                "sources": ["hf-daily"],
            },
        ],
    }

    monkeypatch.setattr(
        "paper_daily_fetch.cli.discover_command",
        lambda args: sample,
    )

    exit_code = main(["discover", "--topic", "video-generation"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert json.loads(captured.out) == sample


def test_pipeline_daily_command_writes_ranked_json(monkeypatch, tmp_path: Path):
    output_path = tmp_path / "rank.json"

    monkeypatch.setattr(
        "paper_daily_fetch.cli.pipeline_daily_command",
        lambda args: {"topic": "video-generation", "generated_at": "2026-03-29T12:00:00+00:00", "papers": []},
    )

    exit_code = main(
        [
            "pipeline",
            "daily",
            "--topic",
            "video-generation",
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert json.loads(output_path.read_text())["topic"] == "video-generation"


def test_render_command_writes_markdown(tmp_path: Path):
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "daily.md"
    input_path.write_text(
        json.dumps(
            {
                "topic": "video-generation",
                "generated_at": "2026-03-29T12:00:00+00:00",
                "papers": [
                    {
                        "arxiv_id": "2603.00001v1",
                        "title": "DreamWM",
                        "authors": ["Carol Example"],
                        "published_at": "2026-03-28T05:00:00+00:00",
                        "abstract": "A world model improves controllable video generation quality.",
                        "paper_url": "https://arxiv.org/abs/2603.00001v1",
                        "code_url": None,
                        "figure_url_or_path": None,
                        "figure_reason": None,
                        "topic_matches": ["video generation"],
                        "source": "hf-daily",
                        "sources": ["hf-daily"],
                    }
                ],
            }
        )
    )

    exit_code = main(
        [
            "render",
            "--target",
            "markdown",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert "# 每日论文速递：video-generation" in output_path.read_text()
