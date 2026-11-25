"""Clean, deduplicate and shape scraped rows into a table."""

from __future__ import annotations

import datetime

import pandas as pd

from src.config import PRODUCT_URL_TEMPLATE

COLUMNS = [
    "name", "brand", "price", "base_price", "discount_pct", "in_stock",
    "best_seller", "new_arrival", "price_drop", "seller", "category",
    "sku", "variant_id", "offer_id", "url", "scraped_at",
]


def to_frame(rows: list[dict], category: str, scraped_at: str | None = None) -> pd.DataFrame:
    if not rows:
        raise ValueError("input rows are empty: nothing to normalize")

    frame = pd.DataFrame(rows).drop_duplicates(subset="variant_id", keep="first").copy()
    frame["discount_pct"] = (
        (frame["base_price"] - frame["price"]) / frame["base_price"] * 100
    ).round(1)
    frame["category"] = category
    frame["url"] = frame.apply(
        lambda row: PRODUCT_URL_TEMPLATE.format(
            variant_id=row["variant_id"], offer_id=row["offer_id"]
        ),
        axis=1,
    )
    frame["scraped_at"] = scraped_at or datetime.datetime.now().isoformat(timespec="seconds")
    return frame[COLUMNS].sort_values("price").reset_index(drop=True)
