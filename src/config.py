"""Shared constants for the B.TECH price monitor."""

from pathlib import Path
import os

BASE = "https://btech.com"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

CATEGORIES = [
    "mobile-phones",
    "audio-recording",
    "wearables",
    "laptop-pc",
    "tvs-projectors",
    "gaming-area",
    "personal-care",
    "small-home-appliances",
]

DELAY_SECONDS = 3.0
MAX_RETRIES = 3
TIMEOUT_SECONDS = 40

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("PRICE_RADAR_RAW_DIR", PROJECT_DIR / "data" / "raw"))
OUTPUT_DIR = PROJECT_DIR / "output"
FIXTURES_DIR = PROJECT_DIR / "tests" / "fixtures"

PRODUCT_URL_TEMPLATE = BASE + "/ar/p/{variant_id}?offering_id={offer_id}"
CATEGORY_URL_TEMPLATE = BASE + "/ar/c/{slug}"
