import pandas as pd

from src.normalize import to_frame


def sample_rows():
    return [
        {"variant_id": "a" * 36, "offer_id": "b" * 36, "sku": "S1", "name": "هاتف",
         "brand": "سامسونج", "image": "x.jpg", "price": 1000, "base_price": 1200,
         "in_stock": True, "best_seller": False, "new_arrival": False,
         "price_drop": 200, "seller": "B.TECH", "l1": "mobiles", "l2": "phones"},
        {"variant_id": "a" * 36, "offer_id": "b" * 36, "sku": "S1", "name": "هاتف مكرر",
         "brand": "سامسونج", "image": "x.jpg", "price": 1000, "base_price": 1200,
         "in_stock": True, "best_seller": False, "new_arrival": False,
         "price_drop": 200, "seller": "B.TECH", "l1": "mobiles", "l2": "phones"},
        {"variant_id": "c" * 36, "offer_id": "d" * 36, "sku": "S2", "name": "سماعة",
         "brand": "انكر", "image": "y.jpg", "price": 500, "base_price": 500,
         "in_stock": False, "best_seller": True, "new_arrival": True,
         "price_drop": 0, "seller": "First mobile", "l1": "audio", "l2": "audio"},
    ]


def test_duplicates_are_removed_by_variant_id():
    frame = to_frame(sample_rows(), "audio")
    assert len(frame) == 2


def test_sorted_by_price_ascending():
    frame = to_frame(sample_rows(), "audio")
    assert list(frame["price"]) == [500, 1000]


def test_discount_percentage_is_computed():
    frame = to_frame(sample_rows(), "audio")
    row = frame[frame["sku"] == "S1"].iloc[0]
    assert row["discount_pct"] == 16.7


def test_url_is_built_from_ids():
    frame = to_frame(sample_rows(), "audio")
    row = frame[frame["sku"] == "S2"].iloc[0]
    assert row["url"] == f"https://btech.com/ar/p/{'c' * 36}?offering_id={'d' * 36}"


def test_columns_are_in_the_documented_order():
    frame = to_frame(sample_rows(), "audio")
    assert list(frame.columns) == [
        "name", "brand", "price", "base_price", "discount_pct", "in_stock",
        "best_seller", "new_arrival", "price_drop", "seller", "category",
        "sku", "variant_id", "offer_id", "url", "scraped_at",
    ]


def test_empty_input_raises():
    try:
        to_frame([], "audio")
    except ValueError as error:
        assert "empty" in str(error).lower()
    else:
        raise AssertionError("expected ValueError")
