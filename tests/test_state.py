from pathlib import Path

from paper_daily_fetch.state import SeenStateStore


def test_seen_state_store_deduplicates_ids(tmp_path: Path):
    state = SeenStateStore(tmp_path / "seen.json")

    assert state.filter_new(["2603.00001v1", "2603.00002v1"]) == [
        "2603.00001v1",
        "2603.00002v1",
    ]
    state.mark_seen(["2603.00001v1", "2603.00002v1"])

    assert state.filter_new(["2603.00002v1", "2603.00003v1"]) == ["2603.00003v1"]

