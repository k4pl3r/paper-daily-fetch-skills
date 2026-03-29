from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(slots=True)
class TopicConfig:
    name: str
    keywords: list[str]


@dataclass(slots=True)
class OpenClawConfig:
    default_target: str | None


@dataclass(slots=True)
class AppConfig:
    default_topic: str
    lookback_days: int
    limit: int
    language: str
    image_strategy: str
    state_path: Path
    markdown_output_dir: Path
    openclaw: OpenClawConfig
    topics: dict[str, TopicConfig]
    config_path: Path

    def topic_keywords(self, topic_name: str | None) -> list[str]:
        selected = topic_name or self.default_topic
        return self.topics[selected].keywords


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path).expanduser().resolve()
    data = tomllib.loads(config_path.read_text())
    topics = {
        name: TopicConfig(name=name, keywords=list(value["keywords"]))
        for name, value in data["topics"].items()
    }
    return AppConfig(
        default_topic=data["default_topic"],
        lookback_days=int(data["lookback_days"]),
        limit=int(data["limit"]),
        language=data["language"],
        image_strategy=data["image_strategy"],
        state_path=(config_path.parent / data["state_path"]).resolve(),
        markdown_output_dir=(config_path.parent / data["markdown_output_dir"]).resolve(),
        openclaw=OpenClawConfig(
            default_target=data.get("openclaw", {}).get("default_target")
        ),
        topics=topics,
        config_path=config_path,
    )

