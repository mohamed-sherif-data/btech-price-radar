import src.fetch as fetch_module


def test_returns_cached_file_without_network(tmp_path, monkeypatch):
    cache = tmp_path / "audio.html"
    cache.write_text("<html>cached</html>" * 10000, encoding="utf-8")

    def boom(*args, **kwargs):
        raise AssertionError("network must not be used when cache exists")

    monkeypatch.setattr(fetch_module.requests, "get", boom)
    result = fetch_module.fetch_category("audio", tmp_path)
    assert "cached" in result


def test_raises_after_three_failed_attempts(tmp_path, monkeypatch):
    class FailingResponse:
        def raise_for_status(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(fetch_module.requests, "get", lambda *a, **k: FailingResponse())
    monkeypatch.setattr(fetch_module.time, "sleep", lambda *_: None)

    try:
        fetch_module.fetch_category("audio", tmp_path)
    except RuntimeError as error:
        assert "audio" in str(error)
    else:
        raise AssertionError("expected RuntimeError")
