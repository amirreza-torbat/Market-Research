#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task-07 — ساخت فایل Excel نهایی و جامع با ۱۸ شیت.

خروجی: 07-Exports/iran-exports-1400-1405-YYYYMMDD.xlsx

شیت‌ها:
  1.  Overview                       — معرفی پروژه + آمار + QA
  2.  Data-All                       — نمونه ۱۰۰۰ رکورد
  3.  By-Country-Summary             — تحلیل همه کشورها
  4.  By-Country-Top20-Growth        — Top 20 کشور با بیشترین رشد مطلق
  5.  By-Country-Top20-CAGR          — Top 20 کشور با بیشترین CAGR
  6.  By-Tariff-Summary              — تحلیل همه HS Codeها
  7.  By-Tariff-Top50                — Top 50 HS Code
  8.  By-Tariff-Country              — جدول HS × Country (فقط رشد قوی)
  9.  Trend-All-HS-Country           — جدول master trend
  10. Trend-Classification           — طبقه‌بندی همه جفت‌ها
  11. Trend-By-HS-Summary            — تجمیع به ازای هر HS Code
  12. Export-Candidates-Ranked       — همه ۵۷۴ کاندید
  13. Export-Candidates-Top20-Detail  — Top 20 با جزئیات کامل
  14. Chapter-Country-Matrix         — ماتریس فصل × کشور
  15. Charts-Country                 — نمودار Top 20 کشور
  16. Charts-Tariff                  — نمودار Top 20 HS Code
  17. Charts-Trend-Classification    — نمودار توزیع دسته‌ها
  18. Charts-Export-Candidates       — نمودار Top 20 کاندید
"""
from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "07-Exports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ═════════════════════════════════════════
# استایل‌ها
# ═════════════════════════════════════════
HEADER_FONT = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
HEADER_FILL = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
BORDER = Border(
    left=Side(style="thin", color="CCCCCC"),
    right=Side(style="thin", color="CCCCCC"),
    top=Side(style="thin", color="CCCCCC"),
    bottom=Side(style="thin", color="CCCCCC"),
)
THIN_BORDER = Border(
    left=Side(style="thin", color="EEEEEE"),
    right=Side(style="thin", color="EEEEEE"),
    top=Side(style="thin", color="EEEEEE"),
    bottom=Side(style="thin", color="EEEEEE"),
)
SECTION_FONT = Font(bold=True, size=12, color="1F4E78")
TITLE_FONT = Font(bold=True, size=14)
NOTE_FONT = Font(italic=True, color="666666", size=10)
NUM_FORMAT_USD = '#,##0'
NUM_FORMAT_FLOAT = '#,##0.00'
NUM_FORMAT_PERCENT = '0.00%'


# ═════════════════════════════════════════
# Utility functions
# ═════════════════════════════════════════

def style_header(ws, n_cols, row=1):
    for col in range(1, n_cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = HEADER_ALIGN
        cell.border = BORDER
    ws.row_dimensions[row].height = 30


def autofit_columns(ws, max_width=50):
    """تنظیم عرض ستون‌ها بر اساس محتوا."""
    for col_letter in {cell.column_letter for row in ws.iter_rows() for cell in row}:
        max_length = 0
        for cell in ws[col_letter]:
            try:
                val = str(cell.value) if cell.value is not None else ""
                # For RTL Persian, length may be misleading; use 1.3x multiplier
                length = len(val)
                if length > max_length:
                    max_length = length
            except Exception:
                pass
        adjusted = min(max(max_length + 2, 10), max_width)
        ws.column_dimensions[col_letter].width = adjusted


def add_autofilter_and_freeze(ws):
    ws.auto_filter.ref = ws.dimensions
    ws.freeze_panes = "A2"


def clean_value(val):
    """تبدیل مقادیر Decimal/NaN/Timestamp به نوع قابل نوشتن در Excel.
    
    همچنین حذف کاراکترهای غیرمجاز برای openpyxl (control chars 0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F).
    """
    if val is None:
        return ""
    if pd.isna(val):
        return ""
    if isinstance(val, Decimal):
        # برای Excel به float تبدیل می‌کنیم (مقادیر ما به اندازه کافی کوچک‌اند که float کافی است)
        return float(val)
    if isinstance(val, (pd.Timestamp, datetime)):
        return val.strftime("%Y-%m-%d")
    if hasattr(val, "item"):  # numpy types
        try:
            return val.item()
        except Exception:
            pass
    # numpy types
    try:
        if isinstance(val, (int, float, str, bool)):
            pass  # already a base type
    except Exception:
        pass
    
    # برای رشته‌ها: حذف کاراکترهای غیرمجاز openpyxl
    if isinstance(val, str):
        # openpyxl Illegal chars: \x00-\x08, \x0B, \x0C, \x0E-\x1F (نه \t \n \r)
        val = "".join(
            c for c in val
            if not (0x00 <= ord(c) <= 0x08 or ord(c) == 0x0B or ord(c) == 0x0C
                   or 0x0E <= ord(c) <= 0x1F)
        )
    
    return val


def write_dataframe(ws, df: pd.DataFrame, cols=None, number_format_map=None):
    """نوشتن DataFrame در worksheet با استایل.
    
    number_format_map: dict of {col_name: format_string} to apply number formats.
    """
    if cols is None:
        cols = list(df.columns)
    # فقط ستون‌های موجود
    cols = [c for c in cols if c in df.columns]
    
    # هدر
    for col_idx, col_name in enumerate(cols, 1):
        ws.cell(row=1, column=col_idx, value=str(col_name))
    style_header(ws, len(cols))
    
    # داده
    for row_idx, (_, row) in enumerate(df.iterrows(), 2):
        for col_idx, col_name in enumerate(cols, 1):
            val = clean_value(row.get(col_name))
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.border = THIN_BORDER
            # Apply number format if specified
            if number_format_map and col_name in number_format_map:
                cell.number_format = number_format_map[col_name]
    
    autofit_columns(ws)
    add_autofilter_and_freeze(ws)


def add_cagr_conditional(ws, cagr_col_letter, n_rows):
    """conditional formatting سبز/قرمز برای CAGR (from -1 to +1)."""
    if n_rows == 0:
        return
    range_str = f"{cagr_col_letter}2:{cagr_col_letter}{n_rows + 1}"
    rule = ColorScaleRule(
        start_type="num", start_value=-1, start_color="F8696B",
        mid_type="num", mid_value=0, mid_color="FFEB84",
        end_type="num", end_value=1, end_color="63BE7B",
    )
    ws.conditional_formatting.add(range_str, rule)


# ═════════════════════════════════════════
# بارگذاری داده‌ها
# ═════════════════════════════════════════

def load_data():
    """بارگذاری همه داده‌های مورد نیاز از Parquet/JSON."""
    print("Loading data...")
    data = {}
    
    # Parquet اصلی
    data["exports"] = pd.read_parquet(REPO_ROOT / "05-Data/processed/exports_1400-1405.parquet")
    print(f"  exports: {len(data['exports']):,} records")
    
    # trend analysis
    data["trend"] = pd.read_parquet(REPO_ROOT / "05-Data/processed/trend-analysis-5y.parquet")
    print(f"  trend: {len(data['trend']):,} pairs")
    
    # classification
    data["classification"] = pd.read_parquet(REPO_ROOT / "05-Data/processed/trend-classification.parquet")
    print(f"  classification: {len(data['classification']):,} pairs")
    
    data["classification_by_hs"] = pd.read_parquet(REPO_ROOT / "05-Data/processed/trend-classification-by-hs.parquet")
    print(f"  classification_by_hs: {len(data['classification_by_hs']):,} HS codes")
    
    # candidates
    data["candidates"] = pd.read_parquet(REPO_ROOT / "05-Data/processed/export-candidates-ranked-recalibrated.parquet")
    print(f"  candidates: {len(data['candidates']):,} candidates")
    
    # metadata
    with open(REPO_ROOT / "05-Data/processed/_dataset-metadata.json", "r", encoding="utf-8") as f:
        data["metadata"] = json.load(f)
    
    # QA report
    with open(REPO_ROOT / "05-Data/processed/qa-validation.json", "r", encoding="utf-8") as f:
        data["qa"] = json.load(f)
    print(f"  qa: {data['qa'].get('passed')}/{data['qa'].get('total_tests')} tests passed")
    
    return data


# ═════════════════════════════════════════
# محاسبات تحلیل کشور و تعرفه
# ═════════════════════════════════════════

def compute_by_country(exports: pd.DataFrame) -> pd.DataFrame:
    """تحلیل به تفکیک کشور."""
    print("Computing by-country analysis...")
    
    # اگر export_value_usd به Decimal است، به float تبدیل می‌کنیم
    if exports["export_value_usd"].dtype == object:
        exports_local = exports.copy()
        exports_local["export_value_usd"] = exports_local["export_value_usd"].apply(
            lambda x: float(x) if x is not None and not pd.isna(x) else 0.0
        )
    else:
        exports_local = exports.copy()
    
    yearly = exports_local.groupby(
        ["destination_country_iso2", "destination_country_fa", "year"]
    )["export_value_usd"].sum().unstack(fill_value=0)
    # ستون‌های سال
    yearly.columns = [f"value_{y}" for y in yearly.columns]
    yearly = yearly.reset_index()
    
    # محاسبه شاخص‌ها
    if "value_1400" in yearly.columns and "value_1404" in yearly.columns:
        yearly["absolute_change"] = yearly["value_1404"] - yearly["value_1400"]
        yearly["pct_change"] = yearly.apply(
            lambda r: (r["value_1404"] - r["value_1400"]) / r["value_1400"] * 100 if r["value_1400"] > 0 else None,
            axis=1
        )
        yearly["cagr_5y"] = yearly.apply(
            lambda r: ((r["value_1404"] / r["value_1400"]) ** 0.25 - 1) if r["value_1400"] > 0 and r["value_1404"] > 0 else None,
            axis=1
        )
        yearly["is_increasing"] = (yearly["cagr_5y"] > 0) & (yearly["value_1404"] > yearly["value_1400"])
    
    value_cols = [c for c in yearly.columns if c.startswith("value_")]
    yearly["total_value_5y"] = yearly[value_cols].sum(axis=1)
    return yearly.sort_values("total_value_5y", ascending=False).reset_index(drop=True)


def compute_by_tariff(exports: pd.DataFrame) -> pd.DataFrame:
    """تحلیل به تفکیک HS Code."""
    print("Computing by-tariff analysis...")
    
    if exports["export_value_usd"].dtype == object:
        exports_local = exports.copy()
        exports_local["export_value_usd"] = exports_local["export_value_usd"].apply(
            lambda x: float(x) if x is not None and not pd.isna(x) else 0.0
        )
    else:
        exports_local = exports.copy()
    
    yearly = exports_local.groupby(
        ["hs_code", "hs_description", "year"]
    )["export_value_usd"].sum().unstack(fill_value=0)
    yearly.columns = [f"value_{y}" for y in yearly.columns]
    yearly = yearly.reset_index()
    
    if "value_1400" in yearly.columns and "value_1404" in yearly.columns:
        yearly["absolute_change"] = yearly["value_1404"] - yearly["value_1400"]
        yearly["cagr_5y"] = yearly.apply(
            lambda r: ((r["value_1404"] / r["value_1400"]) ** 0.25 - 1) if r["value_1400"] > 0 and r["value_1404"] > 0 else None,
            axis=1
        )
    
    value_cols = [c for c in yearly.columns if c.startswith("value_")]
    yearly["total_value_5y"] = yearly[value_cols].sum(axis=1)
    return yearly.sort_values("total_value_5y", ascending=False).reset_index(drop=True)


# ═════════════════════════════════════════
# Sheet Builders
# ═════════════════════════════════════════

def build_sheet_overview(wb, data):
    """شیت ۱: Overview."""
    print("  Sheet 1: Overview")
    ws = wb.create_sheet("01-Overview")
    
    meta = data["metadata"]
    qa = data["qa"]
    exports = data["exports"]
    
    # Total value (محاسبه از Decimal)
    total_value = float(sum(float(v) for v in exports["export_value_usd"] if not pd.isna(v)))
    
    # Recommendation counts
    cand_recs = data["candidates"]["recommendation"].value_counts().to_dict() if "recommendation" in data["candidates"].columns else {}
    
    content = [
        ("تحلیل صادرات ایران ۱۴۰۰-۱۴۰۵", "", "title"),
        ("", "", ""),
        ("تاریخ تولید", datetime.now().strftime("%Y-%m-%d %H:%M"), ""),
        ("نسخه", "1.0", ""),
        ("Agent", "ETL Engineer — task-07", ""),
        ("", "", ""),
        ("─── منبع داده ───", "", "section"),
        ("منبع اصلی", meta.get("source", {}).get("primary", "tsd.irica.ir"), ""),
        ("منبع جایگزین", meta.get("source", {}).get("fallback_used", "service.tccim.ir"), ""),
        ("دلیل جایگزینی", meta.get("source", {}).get("reason", "Issue-005"), ""),
        ("", "", ""),
        ("─── بازه زمانی ───", "", "section"),
        ("سال‌های موجود", "، ".join(str(y) for y in meta.get("years_included", [])), ""),
        ("سال ۱۴۰۵", "موجود نیست (Issue-008)", ""),
        ("تفکیک ماهانه ۱۴۰۳/۱۴۰۴", "موجود نیست (Issue-006)", ""),
        ("", "", ""),
        ("─── آمار کلی ───", "", "section"),
        ("تعداد رکوردها", f"{len(exports):,}", ""),
        ("تعداد کشورها", f"{exports['destination_country_iso2'].nunique()}", ""),
        ("تعداد HS Codeها", f"{exports['hs_code'].nunique()}", ""),
        ("تعداد گمرک‌ها", f"{exports['customs_office_fa'].nunique() if 'customs_office_fa' in exports.columns else 'N/A'}", ""),
        ("مجموع ارزش (USD)", f"{total_value:,.0f}", ""),
        ("", "", ""),
        ("─── تحلیل روند ───", "", "section"),
        ("تعداد جفت‌های (HS × Country)", f"{len(data['trend']):,}", ""),
        ("تعداد HS Codeهای یکتا", f"{len(data['classification_by_hs']):,}", ""),
        ("توزیع دسته‌ها", "", ""),
    ]
    
    # trend category counts
    cat_counts = data["classification"]["trend_category"].value_counts().to_dict()
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        content.append((f"  • {cat}", f"{cnt:,}", ""))
    
    content += [
        ("", "", ""),
        ("─── کاندیدهای صادرات ───", "", "section"),
        ("تعداد کل کاندیدها", f"{len(data['candidates']):,}", ""),
        ("select", f"{cand_recs.get('select', 0)}", ""),
        ("monitor", f"{cand_recs.get('monitor', 0)}", ""),
        ("investigate", f"{cand_recs.get('investigate', 0)}", ""),
        ("", "", ""),
        ("─── اعتبارسنجی QA ───", "", "section"),
        ("وضعیت کلی", "✅ PASS" if qa.get("overall_pass") else "❌ FAIL", ""),
        ("تعداد تست‌ها", qa.get("total_tests"), ""),
        ("PASS", qa.get("passed"), ""),
        ("FAIL", qa.get("failed"), ""),
        ("تلورانس عددی", f"{qa.get('tolerance_observed_max_percent', 0)}٪ (آستانه: < 0.0001٪)", ""),
        ("", "", ""),
        ("─── فایل‌های مرجع ───", "", "section"),
        ("داده اصلی", "05-Data/processed/exports_1400-1405.parquet", ""),
        ("تحلیل روند", "05-Data/processed/trend-analysis-5y.parquet", ""),
        ("طبقه‌بندی", "05-Data/processed/trend-classification.parquet", ""),
        ("کاندیدها", "05-Data/processed/export-candidates-ranked-recalibrated.parquet", ""),
        ("گزارش QA", "04-State/qa-report.md", ""),
        ("", "", ""),
        ("─── شیت‌های این فایل ───", "", "section"),
        ("01-Overview", "این شیت", ""),
        ("02-Data-All", "نمونه ۱۰۰۰ رکورد از Parquet اصلی", ""),
        ("03-By-Country-Summary", "تحلیل همه کشورها (۱۶۶ ردیف)", ""),
        ("04-By-Country-Top20-Growth", "Top 20 کشور با بیشترین رشد مطلق", ""),
        ("05-By-Country-Top20-CAGR", "Top 20 کشور با بیشترین CAGR", ""),
        ("06-By-Tariff-Summary", "تحلیل همه HS Codeها (۵٬۹۹۳ ردیف)", ""),
        ("07-By-Tariff-Top50", "Top 50 HS Code بر اساس مجموع ۵ سال", ""),
        ("08-By-Tariff-Country", "جدول HS × Country (فقط رشد قوی)", ""),
        ("09-Trend-All-HS-Country", f"جدول master trend ({len(data['trend']):,} جفت)", ""),
        ("10-Trend-Classification", "طبقه‌بندی همه جفت‌ها", ""),
        ("11-Trend-By-HS-Summary", "تجمیع به ازای هر HS Code", ""),
        ("12-Export-Candidates-Ranked", f"همه {len(data['candidates']):,} کاندید با نمره", ""),
        ("13-Export-Candidates-Top20-Detail", "Top 20 با جزئیات کامل", ""),
        ("14-Chapter-Country-Matrix", "ماتریس فصل × کشور", ""),
        ("15-Charts-Country", "نمودار Top 20 کشور", ""),
        ("16-Charts-Tariff", "نمودار Top 20 HS Code", ""),
        ("17-Charts-Trend-Classification", "نمودار توزیع دسته‌ها", ""),
        ("18-Charts-Export-Candidates", "نمودار Top 20 کاندید", ""),
    ]
    
    for row_idx, (key, val, kind) in enumerate(content, 1):
        c1 = ws.cell(row=row_idx, column=1, value=key)
        c2 = ws.cell(row=row_idx, column=2, value=val)
        if kind == "title":
            c1.font = TITLE_FONT
        elif kind == "section":
            c1.font = SECTION_FONT
        elif key and not val:
            c1.font = TITLE_FONT if "───" not in key else SECTION_FONT
    
    ws.column_dimensions["A"].width = 45
    ws.column_dimensions["B"].width = 80


def build_sheet_data_all(wb, data):
    """شیت ۲: Data-All (نمونه ۱۰۰۰ رکورد)."""
    print("  Sheet 2: Data-All (sample 1000)")
    ws = wb.create_sheet("02-Data-All")
    
    # نمونه ۱۰۰۰ رکورد با seed ثابت برای reproducibility
    sample = data["exports"].sample(n=min(1000, len(data["exports"])), random_state=42).copy()
    
    # تبدیل Decimal به float برای Excel
    for col in ["export_value_usd", "export_value_rial", "export_weight_kg"]:
        if col in sample.columns:
            sample[col] = sample[col].apply(lambda x: float(x) if x is not None and not pd.isna(x) else 0.0)
    
    cols = ["year", "month", "is_monthly", "hs_code", "hs_description",
            "destination_country_iso2", "destination_country_fa",
            "customs_office_fa", "export_value_usd", "export_weight_kg", "export_value_rial"]
    available_cols = [c for c in cols if c in sample.columns]
    
    number_formats = {
        "export_value_usd": NUM_FORMAT_USD,
        "export_value_rial": NUM_FORMAT_USD,
        "export_weight_kg": NUM_FORMAT_USD,
    }
    write_dataframe(ws, sample[available_cols], available_cols, number_formats)
    
    # یادداشت در بالای شیت
    ws.insert_rows(1)
    ws.cell(row=1, column=1, value=f"نمونه ۱۰۰۰ رکورد از {len(data['exports']):,} رکورد کل. داده کامل در 05-Data/processed/exports_1400-1405.parquet").font = NOTE_FONT
    ws.row_dimensions[1].height = 20


def build_sheet_by_country_summary(wb, data):
    """شیت ۳: By-Country-Summary."""
    print("  Sheet 3: By-Country-Summary")
    ws = wb.create_sheet("03-By-Country-Summary")
    
    by_country = compute_by_country(data["exports"])
    cols = ["destination_country_iso2", "destination_country_fa",
            "value_1400", "value_1401", "value_1402", "value_1403", "value_1404",
            "total_value_5y", "absolute_change", "pct_change", "cagr_5y", "is_increasing"]
    available_cols = [c for c in cols if c in by_country.columns]
    
    number_formats = {col: NUM_FORMAT_USD for col in available_cols
                     if col.startswith("value_") or col == "absolute_change" or col == "total_value_5y"}
    if "pct_change" in available_cols:
        number_formats["pct_change"] = NUM_FORMAT_FLOAT
    if "cagr_5y" in available_cols:
        number_formats["cagr_5y"] = NUM_FORMAT_PERCENT
    
    write_dataframe(ws, by_country[available_cols], available_cols, number_formats)
    
    if "cagr_5y" in available_cols:
        cagr_col = get_column_letter(available_cols.index("cagr_5y") + 1)
        add_cagr_conditional(ws, cagr_col, len(by_country))


def build_sheet_by_country_top20_growth(wb, data):
    """شیت ۴: By-Country-Top20-Growth."""
    print("  Sheet 4: By-Country-Top20-Growth")
    ws = wb.create_sheet("04-By-Country-Top20-Growth")
    
    by_country = compute_by_country(data["exports"])
    significant = by_country[by_country["value_1404"] > 1_000_000].copy()
    top20 = significant.nlargest(20, "absolute_change")
    
    cols = ["destination_country_iso2", "destination_country_fa",
            "value_1400", "value_1404", "absolute_change", "pct_change", "cagr_5y"]
    available_cols = [c for c in cols if c in top20.columns]
    
    number_formats = {col: NUM_FORMAT_USD for col in available_cols
                     if col.startswith("value_") or col == "absolute_change"}
    if "pct_change" in available_cols:
        number_formats["pct_change"] = NUM_FORMAT_FLOAT
    if "cagr_5y" in available_cols:
        number_formats["cagr_5y"] = NUM_FORMAT_PERCENT
    
    write_dataframe(ws, top20[available_cols], available_cols, number_formats)


def build_sheet_by_country_top20_cagr(wb, data):
    """شیت ۵: By-Country-Top20-CAGR."""
    print("  Sheet 5: By-Country-Top20-CAGR")
    ws = wb.create_sheet("05-By-Country-Top20-CAGR")
    
    by_country = compute_by_country(data["exports"])
    significant = by_country[
        (by_country["value_1404"] > 1_000_000) &
        (by_country["cagr_5y"].notna())
    ].copy()
    top20 = significant.nlargest(20, "cagr_5y")
    
    cols = ["destination_country_iso2", "destination_country_fa",
            "value_1400", "value_1404", "cagr_5y", "pct_change"]
    available_cols = [c for c in cols if c in top20.columns]
    
    number_formats = {col: NUM_FORMAT_USD for col in available_cols if col.startswith("value_")}
    if "pct_change" in available_cols:
        number_formats["pct_change"] = NUM_FORMAT_FLOAT
    if "cagr_5y" in available_cols:
        number_formats["cagr_5y"] = NUM_FORMAT_PERCENT
    
    write_dataframe(ws, top20[available_cols], available_cols, number_formats)


def build_sheet_by_tariff_summary(wb, data):
    """شیت ۶: By-Tariff-Summary."""
    print("  Sheet 6: By-Tariff-Summary")
    ws = wb.create_sheet("06-By-Tariff-Summary")
    
    by_tariff = compute_by_tariff(data["exports"])
    cols = ["hs_code", "hs_description",
            "value_1400", "value_1401", "value_1402", "value_1403", "value_1404",
            "total_value_5y", "absolute_change", "cagr_5y"]
    available_cols = [c for c in cols if c in by_tariff.columns]
    
    number_formats = {col: NUM_FORMAT_USD for col in available_cols
                     if col.startswith("value_") or col == "absolute_change" or col == "total_value_5y"}
    if "cagr_5y" in available_cols:
        number_formats["cagr_5y"] = NUM_FORMAT_PERCENT
    
    write_dataframe(ws, by_tariff[available_cols], available_cols, number_formats)


def build_sheet_by_tariff_top50(wb, data):
    """شیت ۷: By-Tariff-Top50."""
    print("  Sheet 7: By-Tariff-Top50")
    ws = wb.create_sheet("07-By-Tariff-Top50")
    
    by_tariff = compute_by_tariff(data["exports"])
    top50 = by_tariff.nlargest(50, "total_value_5y")
    
    cols = ["hs_code", "hs_description",
            "value_1400", "value_1404", "total_value_5y", "absolute_change", "cagr_5y"]
    available_cols = [c for c in cols if c in top50.columns]
    
    number_formats = {col: NUM_FORMAT_USD for col in available_cols
                     if col.startswith("value_") or col == "absolute_change" or col == "total_value_5y"}
    if "cagr_5y" in available_cols:
        number_formats["cagr_5y"] = NUM_FORMAT_PERCENT
    
    write_dataframe(ws, top50[available_cols], available_cols, number_formats)


def build_sheet_by_tariff_country(wb, data):
    """شیت ۸: By-Tariff-Country (فقط رشد قوی)."""
    print("  Sheet 8: By-Tariff-Country (strong/moderate/emerging only)")
    ws = wb.create_sheet("08-By-Tariff-Country")
    
    strong_cats = ["strong_growth", "moderate_growth", "emerging"]
    available_cats = [c for c in strong_cats if c in data["classification"]["trend_category"].unique()]
    strong = data["classification"][
        data["classification"]["trend_category"].isin(available_cats)
    ].copy()
    
    cols = ["hs_code", "hs_description", "destination_country_iso2", "destination_country_fa",
            "value_1400", "value_1404", "cagr_5y", "trend_category", "confidence",
            "is_significant", "mk_p_value", "r_squared"]
    available_cols = [c for c in cols if c in strong.columns]
    
    number_formats = {col: NUM_FORMAT_USD for col in available_cols if col.startswith("value_")}
    if "cagr_5y" in available_cols:
        number_formats["cagr_5y"] = NUM_FORMAT_PERCENT
    if "mk_p_value" in available_cols:
        number_formats["mk_p_value"] = NUM_FORMAT_FLOAT
    if "r_squared" in available_cols:
        number_formats["r_squared"] = NUM_FORMAT_FLOAT
    if "confidence" in available_cols:
        number_formats["confidence"] = NUM_FORMAT_FLOAT
    
    write_dataframe(ws, strong[available_cols], available_cols, number_formats)


def build_sheet_trend_all(wb, data):
    """شیت ۹: Trend-All-HS-Country."""
    print("  Sheet 9: Trend-All-HS-Country")
    ws = wb.create_sheet("09-Trend-All-HS-Country")
    
    trend = data["trend"].copy()
    # Convert numeric cols to float
    numeric_cols = ["value_1400", "value_1401", "value_1402", "value_1403", "value_1404",
                    "cagr_5y", "cagr_6y", "pct_change_5y", "growth_multiplier", "slope",
                    "r_squared", "mk_p_value", "cv", "mean_value", "mean_recent_3y"]
    for col in numeric_cols:
        if col in trend.columns:
            trend[col] = pd.to_numeric(trend[col], errors="coerce")
    
    cols = ["hs_code", "destination_country_iso2", "hs_description", "destination_country_fa",
            "value_1400", "value_1401", "value_1402", "value_1403", "value_1404",
            "cagr_5y", "pct_change_5y", "slope", "r_squared", "mk_p_value", "cv",
            "trend_consistency", "mean_value", "mean_recent_3y", "n_years_with_data"]
    available_cols = [c for c in cols if c in trend.columns]
    
    number_formats = {col: NUM_FORMAT_USD for col in available_cols
                     if col.startswith("value_") or col == "mean_value" or col == "mean_recent_3y"}
    for col in ["cagr_5y", "cagr_6y", "growth_multiplier", "cv"]:
        if col in available_cols:
            number_formats[col] = NUM_FORMAT_PERCENT
    for col in ["pct_change_5y", "slope", "r_squared", "mk_p_value"]:
        if col in available_cols:
            number_formats[col] = NUM_FORMAT_FLOAT
    
    write_dataframe(ws, trend[available_cols], available_cols, number_formats)


def build_sheet_trend_classification(wb, data):
    """شیت ۱۰: Trend-Classification."""
    print("  Sheet 10: Trend-Classification")
    ws = wb.create_sheet("10-Trend-Classification")
    
    classification = data["classification"].copy()
    # Convert numeric
    numeric_cols = ["value_1400", "value_1401", "value_1402", "value_1403", "value_1404",
                    "cagr_5y", "pct_change_5y", "growth_multiplier", "slope",
                    "r_squared", "mk_p_value", "cv", "mean_value", "mean_recent_3y"]
    for col in numeric_cols:
        if col in classification.columns:
            classification[col] = pd.to_numeric(classification[col], errors="coerce")
    
    cols = ["hs_code", "destination_country_iso2", "hs_description", "destination_country_fa",
            "value_1400", "value_1404", "cagr_5y", "trend_category", "confidence",
            "is_significant", "mk_p_value", "r_squared", "recommendation_action"]
    available_cols = [c for c in cols if c in classification.columns]
    
    number_formats = {col: NUM_FORMAT_USD for col in available_cols if col.startswith("value_")}
    if "cagr_5y" in available_cols:
        number_formats["cagr_5y"] = NUM_FORMAT_PERCENT
    for col in ["confidence", "mk_p_value", "r_squared"]:
        if col in available_cols:
            number_formats[col] = NUM_FORMAT_FLOAT
    
    write_dataframe(ws, classification[available_cols], available_cols, number_formats)


def build_sheet_trend_by_hs_summary(wb, data):
    """شیت ۱۱: Trend-By-HS-Summary."""
    print("  Sheet 11: Trend-By-HS-Summary")
    ws = wb.create_sheet("11-Trend-By-HS-Summary")
    
    by_hs = data["classification_by_hs"].copy()
    # Convert numeric
    numeric_cols = ["total_value_5y", "total_value_1404", "agg_value_1400", "agg_value_1404",
                    "mean_recent_3y_aggregated", "trend_consistency_aggregated",
                    "cv_aggregated", "slope_aggregated", "cagr_5y_aggregated",
                    "growth_diversity_score"]
    for col in numeric_cols:
        if col in by_hs.columns:
            by_hs[col] = pd.to_numeric(by_hs[col], errors="coerce")
    
    cols = ["hs_code", "hs_description", "n_countries_total", "total_value_5y", "total_value_1404",
            "n_strong_growth", "n_moderate_growth", "n_emerging", "n_declining", "n_disappearing",
            "n_growth_pairs", "n_destinations_active", "dominant_trend",
            "growth_diversity_score", "cagr_5y_aggregated", "slope_aggregated"]
    available_cols = [c for c in cols if c in by_hs.columns]
    
    number_formats = {col: NUM_FORMAT_USD for col in available_cols
                     if col.startswith("total_") or col == "mean_recent_3y_aggregated"}
    if "cagr_5y_aggregated" in available_cols:
        number_formats["cagr_5y_aggregated"] = NUM_FORMAT_PERCENT
    for col in ["slope_aggregated", "growth_diversity_score"]:
        if col in available_cols:
            number_formats[col] = NUM_FORMAT_FLOAT
    
    write_dataframe(ws, by_hs[available_cols], available_cols, number_formats)


def build_sheet_export_candidates_ranked(wb, data):
    """شیت ۱۲: Export-Candidates-Ranked."""
    print("  Sheet 12: Export-Candidates-Ranked")
    ws = wb.create_sheet("12-Export-Candidates-Ranked")
    
    candidates = data["candidates"].copy()
    # Convert numeric
    numeric_cols = ["export_score", "cagr_5y_aggregated", "slope_aggregated",
                    "mean_recent_3y_aggregated", "total_value_5y", "total_value_1404",
                    "max_country_share", "score_growth", "score_slope", "score_volume",
                    "score_diversity", "score_consistency", "score_volatility_penalty"]
    for col in numeric_cols:
        if col in candidates.columns:
            candidates[col] = pd.to_numeric(candidates[col], errors="coerce")
    
    cols = ["rank", "hs_code", "hs_description", "hs_chapter",
            "export_score", "recommendation", "risk_flags",
            "cagr_5y_aggregated", "slope_aggregated", "mean_recent_3y_aggregated",
            "n_destinations_active", "trend_consistency_aggregated", "cv_aggregated",
            "total_value_5y", "total_value_1404",
            "n_strong_growth", "n_moderate_growth", "n_emerging",
            "top_5_countries", "max_country_share"]
    available_cols = [c for c in cols if c in candidates.columns]
    
    number_formats = {col: NUM_FORMAT_USD for col in available_cols
                     if col.startswith("total_") or col == "mean_recent_3y_aggregated"}
    if "export_score" in available_cols:
        number_formats["export_score"] = NUM_FORMAT_FLOAT
    if "cagr_5y_aggregated" in available_cols:
        number_formats["cagr_5y_aggregated"] = NUM_FORMAT_PERCENT
    if "max_country_share" in available_cols:
        number_formats["max_country_share"] = NUM_FORMAT_PERCENT
    for col in ["slope_aggregated", "cv_aggregated"]:
        if col in available_cols:
            number_formats[col] = NUM_FORMAT_FLOAT
    
    write_dataframe(ws, candidates[available_cols], available_cols, number_formats)
    
    # conditional formatting روی export_score
    if "export_score" in available_cols:
        score_col = get_column_letter(available_cols.index("export_score") + 1)
        score_range = f"{score_col}2:{score_col}{len(candidates) + 1}"
        rule = ColorScaleRule(
            start_type="min", start_color="F8696B",
            mid_type="percentile", mid_value=50, mid_color="FFEB84",
            end_type="max", end_color="63BE7B",
        )
        ws.conditional_formatting.add(score_range, rule)


def build_sheet_export_candidates_top20_detail(wb, data):
    """شیت ۱۳: Export-Candidates-Top20-Detail."""
    print("  Sheet 13: Export-Candidates-Top20-Detail")
    ws = wb.create_sheet("13-Candidates-Top20-Detail")
    
    top20 = data["candidates"].head(20).copy()
    # Convert numeric
    for col in top20.columns:
        if col not in ["hs_code", "hs_description", "hs_chapter", "recommendation",
                       "risk_flags", "trend_category", "top_5_countries",
                       "recommendation_old"]:
            top20[col] = pd.to_numeric(top20[col], errors="coerce")
    
    cols = list(top20.columns)
    write_dataframe(ws, top20, cols)


def build_sheet_chapter_country_matrix(wb, data):
    """شیت ۱۴: Chapter-Country-Matrix."""
    print("  Sheet 14: Chapter-Country-Matrix")
    ws = wb.create_sheet("14-Chapter-Country-Matrix")
    
    # Filter for strong_growth only (per task spec)
    strong = data["classification"][data["classification"]["trend_category"] == "strong_growth"].copy()
    strong["hs_chapter"] = strong["hs_code"].str[:2]
    
    # Top 30 countries with most strong_growth pairs
    top_countries = strong["destination_country_iso2"].value_counts().head(30).index.tolist()
    
    # Build matrix
    matrix_data = strong[strong["destination_country_iso2"].isin(top_countries)].groupby(
        ["hs_chapter", "destination_country_iso2"]
    ).size().unstack(fill_value=0)
    
    # Ensure all top_countries are in columns
    for country in top_countries:
        if country not in matrix_data.columns:
            matrix_data[country] = 0
    matrix_data = matrix_data[top_countries]
    matrix_data = matrix_data.sort_index()
    
    # Write header
    ws.cell(row=1, column=1, value="فصل HS")
    for col_idx, country in enumerate(top_countries, 2):
        ws.cell(row=1, column=col_idx, value=country)
    style_header(ws, len(top_countries) + 1)
    
    # Write data
    for row_idx, chapter in enumerate(matrix_data.index, 2):
        ws.cell(row=row_idx, column=1, value=chapter)
        for col_idx, country in enumerate(top_countries, 2):
            val = int(matrix_data.loc[chapter, country]) if chapter in matrix_data.index else 0
            cell = ws.cell(row=row_idx, column=col_idx, value=val if val > 0 else "")
            cell.alignment = Alignment(horizontal="center")
    
    autofit_columns(ws, max_width=10)
    add_autofilter_and_freeze(ws)
    
    # Add note
    ws.insert_rows(1)
    ws.cell(row=1, column=1, value=f"ماتریس تعداد جفت‌های (HS Chapter × Country) با روند strong_growth. Total strong_growth pairs: {len(strong):,}").font = NOTE_FONT
    ws.row_dimensions[1].height = 20


def build_sheet_charts_country(wb, data):
    """شیت ۱۵: Charts-Country."""
    print("  Sheet 15: Charts-Country")
    ws = wb.create_sheet("15-Charts-Country")
    
    by_country = compute_by_country(data["exports"])
    significant = by_country[by_country["value_1404"] > 1_000_000]
    top20 = significant.nlargest(20, "value_1404")
    
    # Header
    ws.cell(row=1, column=1, value="کشور")
    ws.cell(row=1, column=2, value="ارزش ۱۴۰۴ (USD)")
    style_header(ws, 2)
    
    for row_idx, (_, row) in enumerate(top20.iterrows(), 2):
        ws.cell(row=row_idx, column=1, value=row["destination_country_iso2"])
        c = ws.cell(row=row_idx, column=2, value=float(row["value_1404"]))
        c.number_format = NUM_FORMAT_USD
    
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 20
    
    # BarChart
    chart = BarChart()
    chart.type = "bar"
    chart.title = "Top 20 کشور مقصد (ارزش ۱۴۰۴)"
    chart.x_axis.title = "ارزش (USD)"
    chart.y_axis.title = "کشور"
    chart.width = 25
    chart.height = 18
    
    chart_data = Reference(ws, min_col=2, min_row=1, max_row=21)
    chart_cats = Reference(ws, min_col=1, min_row=2, max_row=21)
    chart.add_data(chart_data, titles_from_data=True)
    chart.set_categories(chart_cats)
    
    ws.add_chart(chart, "D2")


def build_sheet_charts_tariff(wb, data):
    """شیت ۱۶: Charts-Tariff."""
    print("  Sheet 16: Charts-Tariff")
    ws = wb.create_sheet("16-Charts-Tariff")
    
    by_tariff = compute_by_tariff(data["exports"])
    top20 = by_tariff.nlargest(20, "total_value_5y")
    
    ws.cell(row=1, column=1, value="HS Code")
    ws.cell(row=1, column=2, value="مجموع ۵ سال (USD)")
    style_header(ws, 2)
    
    for row_idx, (_, row) in enumerate(top20.iterrows(), 2):
        ws.cell(row=row_idx, column=1, value=row["hs_code"])
        c = ws.cell(row=row_idx, column=2, value=float(row["total_value_5y"]))
        c.number_format = NUM_FORMAT_USD
    
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 20
    
    chart = BarChart()
    chart.type = "bar"
    chart.title = "Top 20 HS Code (مجموع ۵ سال)"
    chart.x_axis.title = "ارزش (USD)"
    chart.y_axis.title = "HS Code"
    chart.width = 25
    chart.height = 18
    
    chart_data = Reference(ws, min_col=2, min_row=1, max_row=21)
    chart_cats = Reference(ws, min_col=1, min_row=2, max_row=21)
    chart.add_data(chart_data, titles_from_data=True)
    chart.set_categories(chart_cats)
    
    ws.add_chart(chart, "D2")


def build_sheet_charts_trend_classification(wb, data):
    """شیت ۱۷: Charts-Trend-Classification."""
    print("  Sheet 17: Charts-Trend-Classification")
    ws = wb.create_sheet("17-Charts-Trend-Classification")
    
    classification = data["classification"]
    cat_counts = classification["trend_category"].value_counts().sort_values(ascending=False)
    
    ws.cell(row=1, column=1, value="دسته روند")
    ws.cell(row=1, column=2, value="تعداد جفت‌ها")
    style_header(ws, 2)
    
    for row_idx, (cat, count) in enumerate(cat_counts.items(), 2):
        ws.cell(row=row_idx, column=1, value=str(cat))
        ws.cell(row=row_idx, column=2, value=int(count))
    
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 18
    
    # PieChart
    chart = PieChart()
    chart.title = "توزیع دسته‌های روند (۵۰٬۱۹۶ جفت)"
    chart.width = 20
    chart.height = 15
    
    chart_data = Reference(ws, min_col=2, min_row=1, max_row=len(cat_counts) + 1)
    chart_cats = Reference(ws, min_col=1, min_row=2, max_row=len(cat_counts) + 1)
    chart.add_data(chart_data, titles_from_data=True)
    chart.set_categories(chart_cats)
    
    ws.add_chart(chart, "D2")


def build_sheet_charts_export_candidates(wb, data):
    """شیت ۱۸: Charts-Export-Candidates."""
    print("  Sheet 18: Charts-Export-Candidates")
    ws = wb.create_sheet("18-Charts-Export-Candidates")
    
    top20 = data["candidates"].head(20).copy()
    top20["export_score"] = pd.to_numeric(top20["export_score"], errors="coerce")
    
    ws.cell(row=1, column=1, value="رتبه")
    ws.cell(row=1, column=2, value="HS Code")
    ws.cell(row=1, column=3, value="نمره صادرات")
    style_header(ws, 3)
    
    for row_idx, (_, row) in enumerate(top20.iterrows(), 2):
        ws.cell(row=row_idx, column=1, value=int(row["rank"]))
        ws.cell(row=row_idx, column=2, value=str(row["hs_code"]))
        c = ws.cell(row=row_idx, column=3, value=float(row["export_score"]))
        c.number_format = NUM_FORMAT_FLOAT
    
    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 18
    
    chart = BarChart()
    chart.type = "bar"
    chart.title = "Top 20 کاندید صادرات (نمره)"
    chart.x_axis.title = "نمره"
    chart.y_axis.title = "رتبه"
    chart.width = 25
    chart.height = 18
    
    chart_data = Reference(ws, min_col=3, min_row=1, max_row=21)
    chart_cats = Reference(ws, min_col=1, min_row=2, max_row=21)
    chart.add_data(chart_data, titles_from_data=True)
    chart.set_categories(chart_cats)
    
    ws.add_chart(chart, "E2")


# ═════════════════════════════════════════
# Main
# ═════════════════════════════════════════

def main():
    print("=" * 70)
    print("task-07: ساخت فایل Excel نهایی با ۱۸ شیت")
    print("=" * 70)
    
    data = load_data()
    
    wb = Workbook()
    wb.remove(wb.active)  # remove default "Sheet"
    
    print("\nBuilding sheets:")
    build_sheet_overview(wb, data)
    build_sheet_data_all(wb, data)
    build_sheet_by_country_summary(wb, data)
    build_sheet_by_country_top20_growth(wb, data)
    build_sheet_by_country_top20_cagr(wb, data)
    build_sheet_by_tariff_summary(wb, data)
    build_sheet_by_tariff_top50(wb, data)
    build_sheet_by_tariff_country(wb, data)
    build_sheet_trend_all(wb, data)
    build_sheet_trend_classification(wb, data)
    build_sheet_trend_by_hs_summary(wb, data)
    build_sheet_export_candidates_ranked(wb, data)
    build_sheet_export_candidates_top20_detail(wb, data)
    build_sheet_chapter_country_matrix(wb, data)
    build_sheet_charts_country(wb, data)
    build_sheet_charts_tariff(wb, data)
    build_sheet_charts_trend_classification(wb, data)
    build_sheet_charts_export_candidates(wb, data)
    
    # ذخیره
    today = datetime.now().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f"iran-exports-1400-1405-{today}.xlsx"
    wb.save(output_path)
    
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\n✅ Saved: {output_path}")
    print(f"   File size: {size_mb:.2f} MB")
    print(f"   Sheets: {len(wb.sheetnames)}")
    print(f"   Sheet names: {wb.sheetnames}")
    
    return output_path


if __name__ == "__main__":
    main()
