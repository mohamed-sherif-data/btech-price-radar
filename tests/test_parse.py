from pathlib import Path

from src.parse import parse_products, unescape_page

FIXTURE = Path(__file__).parent / "fixtures" / "category_audio.html"


def load_fixture() -> str:
    return FIXTURE.read_text(encoding="utf-8", errors="replace")


def test_unescape_page_turns_escaped_quotes_into_real_ones():
    assert unescape_page('{\\"a\\":\\"b\\"}') == '{"a":"b"}'


def test_parse_products_returns_twenty_rows():
    rows = parse_products(load_fixture())
    assert len(rows) == 20


def test_every_row_has_required_fields():
    for row in parse_products(load_fixture()):
        assert row["variant_id"] and len(row["variant_id"]) == 36
        assert row["offer_id"] and len(row["offer_id"]) == 36
        assert isinstance(row["price"], int) and row["price"] > 0
        assert isinstance(row["in_stock"], bool)
        assert row["name"] and len(row["name"]) > 5


def test_prices_are_integers_not_strings():
    rows = parse_products(load_fixture())
    assert all(isinstance(row["price"], int) for row in rows)


def test_base_price_never_lower_than_final_price():
    for row in parse_products(load_fixture()):
        assert row["base_price"] >= row["price"]
