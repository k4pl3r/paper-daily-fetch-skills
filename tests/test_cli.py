import json
from pathlib import Path
from types import SimpleNamespace

from paper_daily_fetch.cli import main, pipeline_daily_command
from paper_daily_fetch.models import PaperRecord


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
        lambda args: {
            "topic": "video-generation",
            "generated_at": "2026-03-29T12:00:00+00:00",
            "papers": [],
        },
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


def test_annotate_command_merges_annotations(tmp_path: Path):
    input_path = tmp_path / "rank.json"
    annotations_path = tmp_path / "annotations.json"
    output_path = tmp_path / "annotated.json"
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
                    }
                ],
            }
        )
    )
    annotations_path.write_text(
        json.dumps(
            {
                "papers": [
                    {
                        "arxiv_id": "2603.00001v1",
                        "summary_zh": "完整中文翻译。",
                        "positive_take": "正面总结。",
                        "critical_take": "负面锐评。",
                    }
                ]
            }
        )
    )

    exit_code = main(
        [
            "annotate",
            "--input",
            str(input_path),
            "--annotations",
            str(annotations_path),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    payload = json.loads(output_path.read_text())
    assert payload["papers"][0]["summary_zh"] == "完整中文翻译。"
    assert payload["papers"][0]["positive_take"] == "正面总结。"
    assert payload["papers"][0]["critical_take"] == "负面锐评。"


def test_publish_command_marks_history_after_success(tmp_path: Path):
    input_path = tmp_path / "annotated.json"
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "\n".join(
            [
                'default_topic = "video-generation"',
                'language = "zh-CN"',
                'image_strategy = "prefer-overview-otherwise-first"',
                'markdown_output_dir = "./output"',
                'cache_dir = "./cache"',
                "",
                "[sources]",
                'enabled = ["arxiv-search"]',
                "timeout = 5",
                "retries = 0",
                "backoff_seconds = 0.1",
                "",
                "[discover]",
                "candidate_limit = 10",
                "",
                "[rank]",
                "final_limit = 3",
                "",
                "[history]",
                'path = "./history/published.json"',
                "lookback_days = 14",
                "",
                "[openclaw]",
                'default_target = "paper-daily-chat"',
                "",
                "[topics.video-generation]",
                'keywords = ["video generation"]',
                "negative_keywords = []",
                "domain_boost_keywords = []",
            ]
        )
        + "\n"
    )
    input_path.write_text(
        json.dumps(
            {
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
                    }
                ]
            }
        )
    )

    exit_code = main(
        [
            "publish",
            "--config",
            str(config_path),
            "--input",
            str(input_path),
        ]
    )

    assert exit_code == 0
    history = json.loads((tmp_path / "history" / "published.json").read_text())
    assert history["published_ids"] == ["2603.00001v1"]


def test_pipeline_daily_filters_history_without_marking_published(
    monkeypatch, tmp_path: Path
):
    history_path = tmp_path / "history.json"
    history_path.write_text(json.dumps({"published_ids": ["2603.00002v1"]}))

    config = SimpleNamespace(
        default_topic="video-generation",
        lookback_days=7,
        cache_dir=tmp_path,
        sources=SimpleNamespace(
            enabled=["arxiv-search"], retries=0, backoff_seconds=0.0, timeout=5
        ),
        discover=SimpleNamespace(candidate_limit=10),
        enrich=SimpleNamespace(max_workers=5, timeout=30),
        rank=SimpleNamespace(final_limit=3),
        history=SimpleNamespace(path=history_path),
    )
    config.topic_keywords = lambda topic: ["video generation"]
    config.topic_negative_keywords = lambda topic: []
    config.topic_domain_boost_keywords = lambda topic: []

    papers = [
        PaperRecord(
            arxiv_id="2603.00001v1",
            title="DreamWM",
            authors=[],
            published_at="2026-03-28T05:00:00+00:00",
            abstract="A world model improves controllable video generation quality.",
            paper_url="https://arxiv.org/abs/2603.00001v1",
            code_url=None,
            figure_url_or_path=None,
            figure_reason=None,
            topic_matches=[],
        ),
        PaperRecord(
            arxiv_id="2603.00002v1",
            title="SeenWM",
            authors=[],
            published_at="2026-03-27T05:00:00+00:00",
            abstract="Already published paper.",
            paper_url="https://arxiv.org/abs/2603.00002v1",
            code_url=None,
            figure_url_or_path=None,
            figure_reason=None,
            topic_matches=[],
        ),
    ]

    monkeypatch.setattr("paper_daily_fetch.cli.load_config", lambda path: config)
    monkeypatch.setattr(
        "paper_daily_fetch.cli.discover_candidates", lambda **kwargs: papers
    )
    monkeypatch.setattr(
        "paper_daily_fetch.cli.enrich_candidates", lambda papers, **kwargs: papers
    )
    monkeypatch.setattr(
        "paper_daily_fetch.cli.rank_candidates", lambda papers, **kwargs: papers
    )

    payload = pipeline_daily_command(
        SimpleNamespace(
            config="unused",
            topic="video-generation",
            days=None,
            limit=None,
            sources=None,
            include_seen=False,
        )
    )

    assert [paper["arxiv_id"] for paper in payload["papers"]] == ["2603.00001v1"]
    history = json.loads(history_path.read_text())
    assert history["published_ids"] == ["2603.00002v1"]
