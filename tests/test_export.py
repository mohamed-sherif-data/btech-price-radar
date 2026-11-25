import pandas as pd

from src.export import write_csv, write_excel


def frame():
    return pd.DataFrame(
        {
            "name": ["سماعة", "هاتف"],
            "brand": ["انكر", "سامسونج"],
            "price": [500, 1000],
            "base_price": [600, 1200],
            "discount_pct": [16.7, 16.7],
            "in_stock": [True, False],
            "best_seller": [True, False],
            "new_arrival": [True, False],
            "price_drop": [100, 200],
            "seller": ["B.TECH", "B.TECH"],
            "category": ["audio", "audio"],
            "sku": ["S2", "S1"],
            "variant_id": ["c" * 36, "a" * 36],
            "offer_id": ["d" * 36, "b" * 36],
            "url": ["https://example.com/1", "https://example.com/2"],
            "scraped_at": ["2026-11-26T10:00:00", "2026-11-26T10:00:00"],
        }
    )


def test_csv_is_written_with_bom_for_excel(tmp_path):
    path = write_csv(frame(), tmp_path / "products.csv")
    raw = path.read_bytes()
    assert path.exists()
    assert raw.startswith(b"\xef\xbb\xbf")
    assert "سماعة" in raw.decode("utf-8-sig")


def test_excel_is_written_and_readable(tmp_path):
    path = write_excel(frame(), tmp_path / "products.xlsx")
    back = pd.read_excel(path)
    assert len(back) == 2
    assert list(back["price"]) == [500, 1000]
