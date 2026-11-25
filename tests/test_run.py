import src.run as run_module


def test_run_skips_categories_that_fail(tmp_path, monkeypatch):
    rows = [
        {"variant_id": "a" * 36, "offer_id": "b" * 36, "sku": "S1", "name": "هاتف",
         "brand": "سامسونج", "image": "x.jpg", "price": 1000, "base_price": 1200,
         "in_stock": True, "best_seller": False, "new_arrival": False,
         "price_drop": 200, "seller": "B.TECH", "l1": "m", "l2": "p"}
    ]

    def fake_fetch(slug, raw_dir):
        if slug == "broken":
            raise RuntimeError("network down")
        return "<html></html>"

    monkeypatch.setattr(run_module, "fetch_category", fake_fetch)
    monkeypatch.setattr(run_module, "parse_products", lambda raw: rows)

    result = run_module.run(["audio", "broken"], tmp_path, scraped_at="2026-11-26T10:00:00")

    assert result["products"] == 1
    assert result["failed"] == ["broken"]
    assert result["csv"].exists()
    assert result["xlsx"].exists()
    assert result["report"].exists()
