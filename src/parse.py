"""Turn a raw B.TECH category page into a list of product dictionaries."""

from __future__ import annotations

import html as html_lib
import re

_PATTERNS = {
    "offer_id": re.compile(r'"offer_id":"([0-9a-f-]{36})"'),
    "sku": re.compile(r'"sku":"([^"]*)"'),
    "name": re.compile(r'"name":"([^"]*)"'),
    "brand": re.compile(r'"brand":"([^"]*)"'),
    "image": re.compile(r'"thumbnail_url":"([^"]*)"'),
    "price": re.compile(r'"price":\{"final_price":(\d+)'),
    "base_price": re.compile(r'"base_price":(\d+)'),
    "in_stock": re.compile(r'"is_in_stock":(true|false)'),
    "best_seller": re.compile(r'"is_best_seller":(true|false)'),
    "new_arrival": re.compile(r'"is_new_arrival":(true|false)'),
    "price_drop": re.compile(r'"price_drop_amount":(\d+)'),
    "seller": re.compile(r'"seller_name":"([^"]*)"'),
    "l1": re.compile(r'"l1":\{[^}]*?"slug":"([^"]*)"'),
    "l2": re.compile(r'"l2":\{[^}]*?"slug":"([^"]*)"'),
}


def unescape_page(raw_html: str) -> str:
    """The page stores its JSON inside a JS string, so quotes are escaped."""
    return raw_html.replace('\\"', '"')


def _to_int(value: str | None, fallback: int = 0) -> int:
    return int(value) if value and value.isdigit() else fallback


def parse_products(raw_html: str) -> list[dict]:
    text = unescape_page(raw_html)
    rows: list[dict] = []

    for chunk in text.split('"variant_id":"')[1:]:
        variant_id = chunk[:36]
        if not re.fullmatch(r"[0-9a-f-]{36}", variant_id):
            continue

        row: dict = {"variant_id": variant_id}
        for key, pattern in _PATTERNS.items():
            match = pattern.search(chunk)
            row[key] = match.group(1) if match else None

        price = _to_int(row["price"])
        if price <= 0 or not row["offer_id"]:
            continue

        row["name"] = html_lib.unescape(row["name"] or "")
        row["brand"] = html_lib.unescape(row["brand"] or "")
        row["seller"] = html_lib.unescape(row["seller"]) if row["seller"] else None
        row["price"] = price
        row["base_price"] = max(_to_int(row["base_price"], price), price)
        row["price_drop"] = _to_int(row["price_drop"])
        row["in_stock"] = row["in_stock"] == "true"
        row["best_seller"] = row["best_seller"] == "true"
        row["new_arrival"] = row["new_arrival"] == "true"
        rows.append(row)

    return rows
