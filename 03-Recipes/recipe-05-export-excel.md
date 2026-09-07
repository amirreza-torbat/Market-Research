---
folder: 03-Recipes
type: recipe
recipe_id: recipe-05
title: ساخت فایل Excel
related_tasks: [task-07]
last_updated: 1405-06-15
---

# 📖 Recipe-05 — ساخت فایل Excel

> **نقش**: ETL Engineer Agent
> **تسک مرتبط**: [[task-07-export-excel]]
> **زمان تخمینی**: ۱ روز

## هدف
ساخت فایل Excel نهایی با ۱۱ شیت، قالب‌بندی حرفه‌ای و نمودارهای داخلی.

## پیش‌نیازها
- [ ] `task-06` pass شده باشد (qa-report.md: pass).
- [ ] پکیج: `openpyxl`.
- [ ] همه فایل‌های `05-Data/processed/` موجود.

## مراحل

### مرحله ۱: ساخت اسکریپت (۲ ساعت)
1. شاخه `feature/task-07-excel` بساز.
2. در `scripts/build_excel.py`:

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule
import pandas as pd
import pyarrow.parquet as pq
from datetime import datetime

def build_excel():
    wb = Workbook()
    
    # حذف شیت پیش‌فرض
    wb.remove(wb.active)
    
    # ۱. Overview
    build_overview_sheet(wb)
    
    # ۲. Data-All (نمونه)
    build_data_sheet(wb)
    
    # ۳. By-Country-Summary
    build_country_summary(wb)
    
    # ۴. By-Country-Top20-Growth
    build_country_top20_growth(wb)
    
    # ۵. By-Country-Top20-CAGR
    build_country_top20_cagr(wb)
    
    # ۶. By-Tariff-Summary
    build_tariff_summary(wb)
    
    # ۷. By-Tariff-Top50
    build_tariff_top50(wb)
    
    # ۸. By-Tariff-Country
    build_tariff_country(wb)
    
    # ۹. Charts-Country
    build_charts_country(wb)
    
    # ۱۰. Charts-Tariff
    build_charts_tariff(wb)
    
    # ۱۱. QA
    build_qa_sheet(wb)
    
    # ذخیره
    today = datetime.now().strftime("%Y%m%d")
    wb.save(f"07-Exports/iran-exports-1400-1404-{today}.xlsx")
```

### مرحله ۲: قالب‌بندی مشترک (۱ ساعت)
```python
HEADER_FONT = Font(name="B Nazanin", bold=True, color="FFFFFF", size=11)
HEADER_FILL = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
BORDER = Border(
    left=Side(style="thin", color="CCCCCC"),
    right=Side(style="thin", color="CCCCCC"),
    top=Side(style="thin", color="CCCCCC"),
    bottom=Side(style="thin", color="CCCCCC"),
)

def style_header(ws, row=1, n_cols=None):
    if n_cols is None:
        n_cols = ws.max_column
    for col in range(1, n_cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = HEADER_ALIGN
        cell.border = BORDER
    ws.row_dimensions[row].height = 30

def autofit_columns(ws):
    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                length = len(str(cell.value))
                if length > max_length:
                    max_length = length
            except:
                pass
        ws.column_dimensions[col_letter].width = min(max_length + 2, 50)

def freeze_header(ws):
    ws.freeze_panes = "A2"

def add_autofilter(ws):
    ws.auto_filter.ref = ws.dimensions
```

### مرحله ۳: شیت‌های داده (۳ ساعت)
برای هر شیت داده:
1. load از CSV/Parquet.
2. write به worksheet.
3. style header.
4. autofit columns.
5. freeze header.
6. autofilter.
7. conditional formatting برای CAGR.

```python
def add_cagr_conditional(ws, cagr_col_letter, n_rows):
    """سبز برای مثبت، قرمز برای منفی."""
    range_str = f"{cagr_col_letter}2:{cagr_col_letter}{n_rows+1}"
    rule = ColorScaleRule(
        start_type="num", start_value=-1, start_color="F8696B",
        mid_type="num", mid_value=0, mid_color="FFEB84",
        end_type="num", end_value=1, end_color="63BE7B",
    )
    ws.conditional_formatting.add(range_str, rule)
```

### مرحله ۴: شیت‌های نمودار (۲ ساعت)
```python
def build_charts_country(wb):
    ws = wb.create_sheet("Charts-Country")
    
    # خواندن داده
    df = pd.read_csv("05-Data/processed/analysis-by-country.csv")
    top20 = df.nlargest(20, "cagr")
    
    # نوشتن داده در worksheet (برای نمودار)
    ws["A1"] = "Country"
    ws["B1"] = "CAGR"
    for i, (_, row) in enumerate(top20.iterrows(), start=2):
        ws[f"A{i}"] = row["destination_country_iso2"]
        ws[f"B{i}"] = float(row["cagr"])
    
    # ساخت نمودار
    chart = BarChart()
    chart.type = "bar"
    chart.title = "Top 20 Countries by CAGR (1400-1404)"
    chart.x_axis.title = "CAGR"
    chart.y_axis.title = "Country"
    
    data = Reference(ws, min_col=2, min_row=1, max_row=21)
    cats = Reference(ws, min_col=1, min_row=2, max_row=21)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    
    ws.add_chart(chart, "D2")
```

### مرحله ۵: شیت QA (۳۰ دقیقه)
```python
def build_qa_sheet(wb):
    ws = wb.create_sheet("QA")
    ws["A1"] = "گزارش QA"
    ws["A1"].font = Font(bold=True, size=14)
    
    # خواندن qa-report.md و نمایش خلاصه
    with open("04-State/qa-report.md", encoding="utf-8") as f:
        content = f.read()
    
    ws["A3"] = "وضعیت کلی"
    ws["B3"] = "PASS"  # از گزارش استخراج شود
    
    ws["A4"] = "تلورانس مشاهده‌شده"
    ws["B4"] = "0.0000X%"  # از گزارش
    
    ws["A6"] = "تاریخ تولید"
    ws["B6"] = datetime.now().isoformat()
```

### مرحله ۶: اعتبارسنجی نهایی (۳۰ دقیقه)
1. باز کردن فایل با openpyxl و بررسی:
   - همه ۱۱ شیت موجود.
   - هدرها درست.
   - نمودارها موجود.
2. تست باز کردن با LibreOffice (در صورت دسترسی).

### مرحله ۷: commit و PR
1. `task-07` به `review` در STATUS.md.
2. commit: `feat(exports): task-07 excel workbook`.
3. push و PR.

## نکات مهم

- ⚠️ **اندازه فایل**: اگر > 50MB، نمونه‌گیری در شیت Data-All یا استفاده از Git LFS.
- ⚠️ **فرمت عدد**: `#,##0.0000` برای ارزش‌ها.
- ⚠️ **فونت فارسی**: `B Nazanin` یا `Vazir` (در صورت نصب).

## مراجع
- [[task-07-export-excel]]
- [[prompt-etl-engineer]]
