from paper_daily_fetch.history import PublishHistoryStore


def test_publish_history_filters_recently_published_ids(tmp_path):
    store = PublishHistoryStore(tmp_path / "history.json")

    recent = store.filter_new(["2603.25745", "2603.25265"])
    assert recent == ["2603.25745", "2603.25265"]

    store.mark_published(["2603.25745"])

    assert store.filter_new(["2603.25745", "2603.25129"]) == ["2603.25129"]
