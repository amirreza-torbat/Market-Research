---
type: task
task_id: task-05
title: تحلیل به تفکیک تعرفه
status: pending
assignee: analyst
created: 1405-06-15
updated: 1405-06-15
depends_on: [task-03]
blocks: [task-06]
estimated_effort: 3-4 days
---

# task-05 — تحلیل به تفکیک تعرفه (HS Code)

## 🎯 هدف
بررسی تک‌به‌تک کدهای تعرفه (HS Code) برای تعیین اینکه هر کد طی ۵ سال به کدام کشورها افزایش یافته است.

## 📋 شرح کار

### ۱. محاسبه به ازای هر (HS Code × Country)
برای هر جفت `(hs_code, destination_country_iso2)`:
- `total_value_1400` تا `total_value_1404`.
- `cagr`, `absolute_change`, `percent_change`.
- `is_increasing`, `is_significant`.
- `trend_consistency`.

> ⚠️ **نکته**: تعداد جفت‌ها می‌تواند بسیار زیاد باشد (مثلاً 5000 HS Code × 150 کشور = 750,000 رکورد). حافظه و کارایی را با Parquet و `pandas` groupby مدیریت کن.

### ۲. تحلیل دو سطح
**سطح ۱: کل HS Code (به‌صورت کلی، نه به تفکیک کشور)**
برای هر HS Code:
- `total_value_1400-1404` (مجموع همه کشورها).
- شاخص‌های رشد.

**سطح ۲: تفکیک HS Code × Country**
برای هر HS Code:
- لیست کشورهایی که صادرات آن HS Code به آن‌ها افزایشی بوده.
- Top 5 کشور برای هر HS Code.

### ۳. فیلتر و رتبه‌بندی
- فقط HS Codeهایی که `is_significant` (مجموع ۵ ساله > 10,000,000 USD) نگه داشته شوند.
- رتبه‌بندی HS Codeها بر اساس:
  - بیشترین تعداد کشور با رشد.
  - بیشترین رشد مطلق.
  - بیشترین CAGR.

### ۴. گزارش‌ها
برای هر HS Code در Top 50 (به ازای هر دسته رتبه‌بندی):
- یک یادداشت در `06-Analysis/by-tariff/hs-XX-XXXX-XX-XX.md`.
- جدول کشورهای افزایشی.
- نمودار روند (۵ سال، aggregated).
- نمودار Top 10 کشور برای این HS Code.
- توضیح کیفی (حداقل ۱۵۰ کلمه).
- backlink به [[task-05-analysis-tariff]] و [[hs-XX]].

### ۵. یادداشت خلاصه
`06-Analysis/by-tariff/_summary.md` شامل:
- آمار کلی (تعداد HS Codeهای افزایشی/کاهشی).
- Top 50 در هر دسته.
- ماتریس热度 HS Code × Country (به‌صورت heatmap).

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [ ] فایل `05-Data/processed/analysis-by-tariff-country.csv` شامل همه جفت‌ها.
- [ ] فایل `05-Data/processed/analysis-by-tariff.csv` شامل تحلیل سطح ۱.
- [ ] حداقل ۵۰ یادداشت در `06-Analysis/by-tariff/`.
- [ ] نمودار PNG برای هر یادداشت.
- [ ] یادداشت `_summary.md` کامل.
- [ ] دقت محاسباتی با تست دستی، خطا < 0.0001٪.
- [ ] commit با پیام `analysis(tariff): task-05 by-tariff analysis`.

## 📦 خروجی‌ها
- `05-Data/processed/analysis-by-tariff-country.csv`
- `05-Data/processed/analysis-by-tariff.csv`
- `06-Analysis/by-tariff/*.md`
- `06-Analysis/by-tariff/charts/*.png`
- `06-Analysis/by-tariff/_summary.md`

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-analyst.md`](../02-Prompts/prompt-analyst.md)
- [`03-Recipes/recipe-03-run-analysis.md`](../03-Recipes/recipe-03-run-analysis.md)

## 🔗 وابستگی‌ها
- [[task-03-etl-normalize]]
- بلاک‌کننده [[task-06-qa-validate]]
- موازی با [[task-04-analysis-country]]
