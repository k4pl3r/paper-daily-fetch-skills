from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(slots=True)
class TopicConfig:
    name: str
    keywords: list[str]
    negative_keywords: list[str]
    domain_boost_keywords: list[str]


@dataclass(slots=True)
class OpenClawConfig:
    default_target: str | None


@dataclass(slots=True)
class SourcesConfig:
    enabled: list[str]
    timeout: int
    retries: int
    backoff_seconds: float


@dataclass(slots=True)
class DiscoverConfig:
    candidate_limit: int


@dataclass(slots=True)
class RankConfig:
    final_limit: int


@dataclass(slots=True)
class HistoryConfig:
    path: Path
    lookback_days: int


@dataclass(slots=True)
class AppConfig:
    default_topic: str
    lookback_days: int
    limit: int
    language: str
    image_strategy: str
    cache_dir: Path
    state_path: Path
    markdown_output_dir: Path
    openclaw: OpenClawConfig
    sources: SourcesConfig
    discover: DiscoverConfig
    rank: RankConfig
    history: HistoryConfig
    topics: dict[str, TopicConfig]
    config_path: Path

    def topic_keywords(self, topic_name: str | None) -> list[str]:
        selected = topic_name or self.default_topic
        return self.topics[selected].keywords

    def topic_negative_keywords(self, topic_name: str | None) -> list[str]:
        selected = topic_name or self.default_topic
        return self.topics[selected].negative_keywords

    def topic_domain_boost_keywords(self, topic_name: str | None) -> list[str]:
        selected = topic_name or self.default_topic
        return self.topics[selected].domain_boost_keywords


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path).expanduser().resolve()
    data = tomllib.loads(config_path.read_text())
    cache_dir = Path(
        data.get("cache_dir", "~/.cache/paper-daily-fetch")
    ).expanduser()
    state_path_value = data.get("state_path", str(cache_dir / "state" / "seen.json"))
    history_path_value = data.get(
        "history", {}
    ).get("path", str(cache_dir / "history" / "published.json"))
    topics = {
        name: TopicConfig(
            name=name,
            keywords=list(value["keywords"]),
            negative_keywords=list(value.get("negative_keywords", [])),
            domain_boost_keywords=list(value.get("domain_boost_keywords", [])),
        )
        for name, value in data["topics"].items()
    }
    return AppConfig(
        default_topic=data["default_topic"],
        lookback_days=int(data.get("lookback_days", data.get("history", {}).get("lookback_days", 1))),
        limit=int(data.get("limit", data.get("rank", {}).get("final_limit", 3))),
        language=data["language"],
        image_strategy=data["image_strategy"],
        cache_dir=cache_dir,
        state_path=_resolve_path(config_path, state_path_value),
        markdown_output_dir=_resolve_path(config_path, data["markdown_output_dir"]),
        openclaw=OpenClawConfig(
            default_target=data.get("openclaw", {}).get("default_target")
        ),
        sources=SourcesConfig(
            enabled=list(data.get("sources", {}).get("enabled", ["hf-daily", "hf-trending", "arxiv-api", "arxiv-search"])),
            timeout=int(data.get("sources", {}).get("timeout", 20)),
            retries=int(data.get("sources", {}).get("retries", 2)),
            backoff_seconds=float(data.get("sources", {}).get("backoff_seconds", 1.0)),
        ),
        discover=DiscoverConfig(
            candidate_limit=int(data.get("discover", {}).get("candidate_limit", 50))
        ),
        rank=RankConfig(
            final_limit=int(data.get("rank", {}).get("final_limit", data.get("limit", 3)))
        ),
        history=HistoryConfig(
            path=_resolve_path(config_path, history_path_value),
            lookback_days=int(data.get("history", {}).get("lookback_days", data.get("lookback_days", 14))),
        ),
        topics=topics,
        config_path=config_path,
    )


def _resolve_path(config_path: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (config_path.parent / path).resolve()
