"""Modal app: weekly refresh + public web page for the B.TECH price radar."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import modal

APP_NAME = "btech-price-radar"
VOLUME_NAME = "btech-price-radar-data"
DATA_ROOT = "/data"
LATEST_DIR = Path(DATA_ROOT) / "latest"

app = modal.App(APP_NAME)

image = (
    modal.Image.debian_slim()
    .pip_install("requests", "pandas", "openpyxl", "fastapi")
    .add_local_python_source("src")
)

volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)


def _publish(result: dict) -> dict:
    """Copy the newest outputs to a stable path the web app can serve."""
    LATEST_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(result["csv"], LATEST_DIR / "products.csv")
    shutil.copy(result["xlsx"], LATEST_DIR / "products.xlsx")
    shutil.copy(result["report"], LATEST_DIR / "report.html")
    meta = {
        "products": result["products"],
        "failed": result["failed"],
        "generated_at": Path(result["csv"]).parent.name,
    }
    (LATEST_DIR / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return meta


@app.function(
    image=image,
    volumes={DATA_ROOT: volume},
    timeout=1800,
    schedule=modal.Cron("0 7 * * 1"),
)
def refresh() -> dict:
    """Scrape the eight categories and publish the newest snapshot."""
    import os

    os.environ["PRICE_RADAR_RAW_DIR"] = str(Path(DATA_ROOT) / "raw")

    from src.config import CATEGORIES
    from src.run import run

    result = run(CATEGORIES, Path(DATA_ROOT) / "output")
    meta = _publish(result)
    volume.commit()
    return meta


@app.function(image=image, volumes={DATA_ROOT: volume})
@modal.asgi_app()
def web():
    from fastapi import FastAPI
    from fastapi.responses import FileResponse, HTMLResponse

    api = FastAPI(title="B.TECH Price Radar")

    toolbar = (
        '<a class="btn-light" href="/data.csv">تحميل CSV</a>'
        '<a class="btn-ghost" href="/data.xlsx">تحميل Excel</a>'
        '<form method="post" action="/refresh" style="margin:0">'
        '<button class="btn-soft" type="submit">تحديث البيانات الآن</button>'
        "</form>"
    )

    def _snapshot_html() -> str:
        report = LATEST_DIR / "report.html"
        if not report.exists():
            return (
                "<html dir='rtl'><body style=\"font-family:Tahoma;padding:40px\">"
                "<h2>لا توجد بيانات بعد</h2>"
                "<p>شغّل التحديث مرة واحدة لتوليد أول نسخة.</p></body></html>"
            )
        html = report.read_text(encoding="utf-8")
        return html.replace(
            '<div class="toolbar" id="toolbar"></div>',
            f'<div class="toolbar">{toolbar}</div>',
            1,
        )

    @api.get("/", response_class=HTMLResponse)
    def index() -> str:
        volume.reload()
        return _snapshot_html()

    @api.get("/data.csv")
    def data_csv():
        volume.reload()
        return FileResponse(
            LATEST_DIR / "products.csv", media_type="text/csv; charset=utf-8",
            filename="btech-products.csv",
        )

    @api.get("/data.xlsx")
    def data_xlsx():
        volume.reload()
        return FileResponse(
            LATEST_DIR / "products.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="btech-products.xlsx",
        )

    @api.get("/api/meta")
    def meta() -> dict:
        volume.reload()
        path = LATEST_DIR / "meta.json"
        if not path.exists():
            return {"status": "empty"}
        return json.loads(path.read_text(encoding="utf-8"))

    @api.post("/refresh")
    def do_refresh() -> HTMLResponse:
        refresh.remote()
        volume.reload()
        return HTMLResponse(
            "<html dir='rtl'><body style=\"font-family:Tahoma;padding:40px\">"
            "<h2>تم تحديث البيانات</h2><p><a href='/'>عرض التقرير</a></p></body></html>"
        )

    return api


@app.local_entrypoint()
def main() -> None:
    print(refresh.remote())
