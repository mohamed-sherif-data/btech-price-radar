"""Command line entry point: fetch, parse, normalize, export, report."""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

import pandas as pd

from src.config import CATEGORIES, DATA_DIR, OUTPUT_DIR
from src.export import write_csv, write_excel
from src.fetch import fetch_category
from src.normalize import to_frame
from src.parse import parse_products
from src.report import build_report


def run(
    categories: list[str],
    output_root: Path = OUTPUT_DIR,
    scraped_at: str | None = None,
) -> dict:
    stamp = scraped_at or datetime.datetime.now().isoformat(timespec="seconds")
    day = stamp[:10]
    raw_dir = DATA_DIR / day
    out_dir = output_root / day

    frames: list[pd.DataFrame] = []
    failed: list[str] = []

    for slug in categories:
        try:
            html = fetch_category(slug, raw_dir)
            rows = parse_products(html)
            if not rows:
                failed.append(slug)
                print(f"[skip] {slug}: no products parsed", file=sys.stderr)
                continue
            frames.append(to_frame(rows, slug, scraped_at=stamp))
            print(f"[ok]   {slug}: {len(rows)} products")
        except Exception as error:  # noqa: BLE001 - reported per category
            failed.append(slug)
            print(f"[fail] {slug}: {error}", file=sys.stderr)

    if not frames:
        raise SystemExit("no data collected: every category failed")

    frame = (
        pd.concat(frames, ignore_index=True)
        .drop_duplicates(subset="variant_id", keep="first")
        .sort_values("price")
        .reset_index(drop=True)
    )

    csv_path = write_csv(frame, out_dir / "products.csv")
    xlsx_path = write_excel(frame, out_dir / "products.xlsx")
    report_path = out_dir / "report.html"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    label = f"{len(categories)} تصنيفات"
    report_path.write_text(build_report(frame, label), encoding="utf-8")

    return {
        "products": len(frame),
        "csv": csv_path,
        "xlsx": xlsx_path,
        "report": report_path,
        "failed": failed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="B.TECH price monitor")
    parser.add_argument(
        "--categories",
        default=",".join(CATEGORIES),
        help="comma separated category slugs",
    )
    parser.add_argument("--out", default=str(OUTPUT_DIR), help="output root folder")
    args = parser.parse_args()

    slugs = [slug.strip() for slug in args.categories.split(",") if slug.strip()]
    result = run(slugs, Path(args.out))

    print(f"\nproducts: {result['products']}")
    print(f"csv:      {result['csv']}")
    print(f"excel:    {result['xlsx']}")
    print(f"report:   {result['report']}")
    if result["failed"]:
        print(f"failed:   {', '.join(result['failed'])}")


if __name__ == "__main__":
    main()
