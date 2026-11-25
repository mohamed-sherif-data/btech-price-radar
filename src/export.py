"""Write the scraped table to CSV and a formatted Excel workbook."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

COLUMN_WIDTHS = {
    "name": 62, "brand": 16, "seller": 20, "category": 18,
    "url": 58, "scraped_at": 20, "sku": 22,
}


def write_csv(frame: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def write_excel(frame: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name="products")
        sheet = writer.sheets["products"]
        sheet.freeze_panes = "A2"

        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1F3864")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for index, column in enumerate(frame.columns, start=1):
            sheet.column_dimensions[get_column_letter(index)].width = (
                COLUMN_WIDTHS.get(column, 14)
            )

        price_columns = [
            frame.columns.get_loc("price") + 1,
            frame.columns.get_loc("base_price") + 1,
        ]
        for row in sheet.iter_rows(
            min_row=2, min_col=min(price_columns), max_col=max(price_columns)
        ):
            for cell in row:
                cell.number_format = "#,##0"

    return path
