"""Download category pages politely, with caching and retries."""

from __future__ import annotations

import time
from pathlib import Path

import requests

from src.config import (
    CATEGORY_URL_TEMPLATE,
    DELAY_SECONDS,
    MAX_RETRIES,
    TIMEOUT_SECONDS,
    USER_AGENT,
)

MIN_CACHE_BYTES = 100_000


def fetch_category(slug: str, raw_dir: Path) -> str:
    """Return the raw HTML for one category page, using the on-disk cache."""
    cache_file = raw_dir / f"{slug}.html"
    if cache_file.exists() and cache_file.stat().st_size > MIN_CACHE_BYTES:
        return cache_file.read_text(encoding="utf-8", errors="replace")

    url = CATEGORY_URL_TEMPLATE.format(slug=slug)
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "ar,en;q=0.8"}
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            raw_dir.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(response.text, encoding="utf-8")
            time.sleep(DELAY_SECONDS)
            return response.text
        except Exception as error:  # noqa: BLE001 - retried below
            last_error = error
            time.sleep(DELAY_SECONDS * attempt)

    raise RuntimeError(f"could not fetch category '{slug}' from {url}: {last_error}")
