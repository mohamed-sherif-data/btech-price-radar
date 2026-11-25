import pandas as pd

from src.report import build_report


def frame():
    return pd.DataFrame(
        {
            "name": [f"منتج {i}" for i in range(5)],
            "brand": ["A"] * 5,
            "price": [100, 200, 300, 400, 500],
            "base_price": [120, 200, 300, 450, 500],
            "discount_pct": [16.7, 0.0, 0.0, 11.1, 0.0],
            "in_stock": [True, True, False, True, False],
            "best_seller": [False, True, False, False, False],
            "new_arrival": [False, False, False, False, True],
            "price_drop": [20, 0, 0, 50, 0],
            "seller": ["B.TECH"] * 5,
            "category": ["audio"] * 5,
            "sku": [f"S{i}" for i in range(5)],
            "variant_id": [str(i) * 36 for i in range(5)],
            "offer_id": [str(i) * 36 for i in range(5)],
            "url": ["https://example.com"] * 5,
            "scraped_at": ["2026-11-26T10:00:00"] * 5,
        }
    )


def test_report_is_rtl_html():
    html = build_report(frame(), "audio")
    assert 'dir="rtl"' in html
    assert html.startswith("<!DOCTYPE html>")


def test_report_shows_count_and_stats():
    html = build_report(frame(), "audio")
    assert "5" in html
    assert "300" in html
    assert "2" in html


def test_report_lists_cheapest_and_priciest():
    html = build_report(frame(), "audio")
    assert "منتج 0" in html
    assert "منتج 4" in html


def test_report_is_self_contained():
    html = build_report(frame(), "audio")
    assert "http://" not in html.replace("https://example.com", "")
