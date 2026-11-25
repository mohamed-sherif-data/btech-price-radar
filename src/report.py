"""Build a one-page, self-contained HTML report from the scraped table."""

from __future__ import annotations

import datetime

import pandas as pd

_STYLE = """
*{box-sizing:border-box}
body{margin:0;background:#eef1f7;color:#0b1220;
     font-family:'Segoe UI',Tahoma,'Noto Kufi Arabic',sans-serif;padding:28px 18px 48px}
.page{max-width:1080px;margin:0 auto}
.hero{position:relative;overflow:hidden;border-radius:22px;padding:30px 32px 26px;
      background:linear-gradient(135deg,#4338ca 0%,#2563eb 45%,#0ea5e9 100%);
      color:#fff;box-shadow:0 18px 40px -18px rgba(37,99,235,.65)}
.hero:before{content:"";position:absolute;inset:0;
      background:radial-gradient(circle at 88% 12%,rgba(255,255,255,.22),transparent 42%),
                 radial-gradient(circle at 12% 88%,rgba(255,255,255,.14),transparent 45%)}
.hero-inner{position:relative;z-index:1}
.badge{display:inline-block;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.32);
      padding:5px 12px;border-radius:999px;font-size:12px;letter-spacing:.2px;margin-bottom:14px}
h1{margin:0;font-size:30px;font-weight:700;letter-spacing:-.3px}
.hero .sub{margin:8px 0 0;font-size:13.5px;color:rgba(255,255,255,.88)}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px}
.toolbar a,.toolbar button{display:inline-flex;align-items:center;gap:7px;border:0;cursor:pointer;
      padding:10px 16px;border-radius:11px;font-size:13.5px;font-weight:600;text-decoration:none;
      font-family:inherit;transition:transform .12s ease,box-shadow .12s ease}
.toolbar a:hover,.toolbar button:hover{transform:translateY(-1px);box-shadow:0 8px 18px -8px rgba(0,0,0,.45)}
.btn-light{background:#fff;color:#1d4ed8}
.btn-soft{background:rgba(255,255,255,.16);color:#fff;border:1px solid rgba(255,255,255,.4)!important}
.btn-ghost{background:rgba(255,255,255,.9);color:#0f172a}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0}
.kpi{position:relative;background:#fff;border:1px solid #e4e9f2;border-radius:16px;padding:16px 18px;
     box-shadow:0 1px 2px rgba(15,23,42,.04);overflow:hidden}
.kpi:after{content:"";position:absolute;top:0;right:0;left:0;height:3px;
     background:linear-gradient(90deg,#6366f1,#22d3ee)}
.kpi span{display:block;font-size:12px;color:#64748b;font-weight:600}
.kpi b{display:block;font-size:25px;font-weight:700;margin-top:7px;letter-spacing:-.5px}
.kpi.accent b{color:#0f766e}
.panel{background:#fff;border:1px solid #e4e9f2;border-radius:18px;padding:20px 22px;margin-bottom:20px;
       box-shadow:0 1px 2px rgba(15,23,42,.04)}
h2{margin:0 0 16px;font-size:16px;font-weight:700;display:flex;align-items:center;gap:9px}
h2:before{content:"";width:4px;height:17px;border-radius:3px;
       background:linear-gradient(180deg,#6366f1,#22d3ee)}
.bars{display:grid;gap:13px}
.bar-row{display:grid;grid-template-columns:150px 1fr 78px;align-items:center;gap:14px;font-size:13px}
.bar-track{display:block;height:12px;background:#eef2f9;border-radius:999px;overflow:hidden}
.bar-fill{display:block;height:100%;border-radius:999px;
      background:linear-gradient(90deg,#6366f1,#22d3ee)}
.bar-count{color:#475569;font-variant-numeric:tabular-nums;font-size:12.5px}
.bar-count b{color:#0b1220}
table{width:100%;border-collapse:separate;border-spacing:0;font-size:13px}
thead th{background:#f4f7fd;color:#334155;font-weight:700;font-size:12.5px;text-align:right;
       padding:11px 12px;border-bottom:1px solid #e4e9f2;white-space:nowrap}
thead th:first-child{border-radius:0 10px 0 0}
thead th:last-child{border-radius:10px 0 0 0}
tbody td{padding:11px 12px;border-bottom:1px solid #f0f3f9;vertical-align:middle}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:#f8fbff}
tbody tr:nth-child(even){background:#fcfdff}
tbody tr:nth-child(even):hover{background:#f8fbff}
.rank{display:inline-flex;align-items:center;justify-content:center;width:23px;height:23px;
      border-radius:8px;background:#eef2ff;color:#4338ca;font-size:11.5px;font-weight:700}
.price{font-weight:700;color:#0f766e;font-variant-numeric:tabular-nums;white-space:nowrap}
.name{line-height:1.55;color:#1e293b}
a.open{display:inline-block;padding:5px 11px;border-radius:8px;background:#eff6ff;color:#1d4ed8;
      text-decoration:none;font-size:12px;font-weight:600;white-space:nowrap}
a.open:hover{background:#dbeafe}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
footer{text-align:center;color:#7c889c;font-size:12px;margin-top:8px;line-height:1.9}
@media (max-width:900px){
  .kpis{grid-template-columns:repeat(2,1fr)}
  .grid2{grid-template-columns:1fr}
  h1{font-size:24px}
  .bar-row{grid-template-columns:110px 1fr 64px;gap:10px}
}
"""


def _rank_table(frame: pd.DataFrame) -> str:
    head = "<tr><th>#</th><th>المنتج</th><th>الماركة</th><th>السعر (ج.م)</th><th>الرابط</th></tr>"
    body = ""
    for position, (_, row) in enumerate(frame.iterrows(), start=1):
        body += (
            "<tr>"
            f'<td><span class="rank">{position}</span></td>'
            f'<td class="name">{row["name"]}</td>'
            f'<td>{row["brand"]}</td>'
            f'<td class="price">{int(row["price"]):,}</td>'
            f'<td><a class="open" href="{row["url"]}" target="_blank">فتح</a></td>'
            "</tr>"
        )
    return f"<table><thead>{head}</thead><tbody>{body}</tbody></table>"


def build_report(frame: pd.DataFrame, category_label: str) -> str:
    total = len(frame)
    brand_count = int(frame["brand"].nunique())
    category_count = int(frame["category"].nunique())
    median = int(frame["price"].median())
    average = int(frame["price"].mean())
    min_price = int(frame["price"].min())
    max_price = int(frame["price"].max())
    discounted = int((frame["base_price"] > frame["price"]).sum())
    cheapest = frame.nsmallest(10, "price")[["name", "brand", "price", "url"]]
    priciest = frame.nlargest(10, "price")[["name", "brand", "price", "url"]]

    edges = [0, 2000, 10000, 30000, float("inf")]
    labels = ["أقل من 2,000", "2,000 – 10,000", "10,000 – 30,000", "أكثر من 30,000"]
    bars = ""
    max_share = 1
    bucket_rows = []
    for start, end, label in zip(edges, edges[1:], labels):
        count = int(((frame["price"] >= start) & (frame["price"] < end)).sum())
        share = round(count / total * 100, 1)
        bucket_rows.append((label, count, share))
        max_share = max(max_share, share)
    for label, count, share in bucket_rows:
        width = round(share / max_share * 100, 1)
        bars += (
            '<div class="bar-row">'
            f"<span>{label}</span>"
            f'<span class="bar-track"><span class="bar-fill" style="width:{width}%"></span></span>'
            f'<span class="bar-count"><b>{count}</b> · {share}%</span>'
            "</div>"
        )

    generated = datetime.datetime.now().strftime("%Y-%m-%d · %H:%M")

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>مرصد الأسعار — B.TECH</title>
<style>{_STYLE}</style></head>
<body><div class="page">

<header class="hero"><div class="hero-inner">
  <span class="badge">تحديث أسبوعي تلقائي · B.TECH</span>
  <h1>مرصد أسعار المنافسين</h1>
  <p class="sub">{category_label} · تاريخ السحب {generated}</p>
  <div class="toolbar" id="toolbar"></div>
</div></header>

<section class="kpis">
  <div class="kpi accent"><span>عدد المنتجات</span><b>{total}</b></div>
  <div class="kpi"><span>عدد الماركات</span><b>{brand_count}</b></div>
  <div class="kpi"><span>عدد التصنيفات</span><b>{category_count}</b></div>
  <div class="kpi"><span>عليها خصم</span><b>{discounted}</b></div>
  <div class="kpi accent"><span>أقل سعر</span><b>{min_price:,}</b></div>
  <div class="kpi"><span>متوسط السعر</span><b>{average:,}</b></div>
  <div class="kpi"><span>وسيط السعر</span><b>{median:,}</b></div>
  <div class="kpi"><span>أعلى سعر</span><b>{max_price:,}</b></div>
</section>

<section class="panel">
  <h2>توزيع الأسعار</h2>
  <div class="bars">{bars}</div>
</section>

<div class="grid2">
  <section class="panel"><h2>أرخص 10 منتجات</h2>{_rank_table(cheapest)}</section>
  <section class="panel"><h2>أغلى 10 منتجات</h2>{_rank_table(priciest)}</section>
</div>

<footer>
  البيانات مسحوبة من صفحات تصنيفات btech.com العامة · 20 منتجًا لكل تصنيف<br>
  مشروع شخصي للعرض التقني — لا يمثّل عميلًا ولا نتيجة مُدَّعاة
</footer>

</div></body></html>"""
