---
type: task
task_id: task-03
title: نرمال‌سازی و ETL
status: pending
assignee: etl-engineer
created: 1405-06-15
updated: 1405-06-15
depends_on: [task-02]
blocks: [task-04, task-05]
estimated_effort: 2-3 days
---

# task-03 — نرمال‌سازی و ETL

## 🎯 هدف
تبدیل داده خام به مدل داده‌ای تحلیلی تمیز، یکپارچه و قابل پرس‌وجو. خروجی این تسک مبنای همه تحلیل‌های بعدی است. شامل ۶ سال (۱۴۰۰ تا ۱۴۰۵) با سال ۱۴۰۵ به‌صورت partial.

## 📋 شرح کار

### ۱. پاکسازی (Clean)
برای هر سال:
- حذف رکوردهای تکراری (deduplication با کلید: `year, month, hs_code, destination_country_iso2`).
- حذف رکوردهای ناقص (NA در فیلدهای کلیدی).
- استانداردسازی نام کشورها به ISO 3166-1 alpha-2 (نگاشت از نام فارسی).
- استانداردسازی HS Code به فرمت ۸ رقمی با نقطه: `HH.HH.HH.HH`.
- تبدیل اعداد فارسی به لاتین.
- تبدیل واحد پول به USD (در صورت نیاز، با نرخ روز از `exchange-rates.csv`).

### ۲. ادغام (Merge)
- concat همه سال‌ها (۱۴۰۰ تا ۱۴۰۵) به یک DataFrame واحد.
- اضافه کردن فیلد `year` و `month` (اگر نبود).
- ذخیره به فرمت **Parquet** (با `pyarrow`) در `05-Data/processed/exports_1400-1405.parquet`.
- ذخیره فایل metadata در `05-Data/processed/_dataset-metadata.json` شامل:
  - `years_included`: `[1400, 1401, 1402, 1403, 1404, 1405]`
  - `months_available_per_year`: `{1400: 12, ..., 1405: N}` (تعداد ماه‌های موجود هر سال)
  - `is_partial_year`: `{1405: true}`

### ۳. اعتبارسنجی (Validate)
- بررسی null در فیلدهای کلیدی.
- بررسی محدوده ارزش (مثلاً value > 0).
- بررسی وجود همه سال‌ها (۵ سال).
- بررسی تعداد کشورها (باید > 100).
- گزارش در `05-Data/processed/_validation-report.md`.

### ۴. ساخت جداول مرجع
- `05-Data/processed/countries.csv`: لیست همه کشورهای دیده‌شده با کد ISO و نام فارسی.
- `05-Data/processed/hs-codes.csv`: لیست همه HS Codeها با شرح.
- `05-Data/processed/exchange-rates.csv`: نرخ ارز روزانه.

### ۵. دقت عددی
- **الزامی**: از `decimal.Decimal` در پایتون استفاده شود.
- خطای محاسباتی کل باید ۰ باشد (مقادیر دقیقاً همان منبع).
- تست: sum(value) برای هر سال باید با total reported توسط گمرک برابر باشد (با تلورانس < 0.0001٪).

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [ ] `05-Data/processed/exports_1400-1405.parquet` ساخته شود.
- [ ] `05-Data/processed/_dataset-metadata.json` ساخته شود با مشخصات سال‌ها.
- [ ] هیچ null در فیلدهای کلیدی (`year`, `hs_code`, `destination_country_iso2`, `export_value_usd`) نباشد.
- [ ] گزارش validation در `05-Data/processed/_validation-report.md`.
- [ ] تست دقت عددی با تلورانس < 0.0001٪ پاس شود (برای هر سال).
- [ ] جداول مرجع (`countries.csv`, `hs-codes.csv`, `exchange-rates.csv`) ساخته شوند.
- [ ] commit با پیام `feat(etl): task-03 normalize and validate exports`.

## 📦 خروجی‌ها
- `05-Data/processed/exports_1400-1405.parquet`
- `05-Data/processed/_dataset-metadata.json`
- `05-Data/processed/countries.csv`
- `05-Data/processed/hs-codes.csv`
- `05-Data/processed/exchange-rates.csv`
- `05-Data/processed/_validation-report.md`

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-etl-engineer.md`](../02-Prompts/prompt-etl-engineer.md)
- [`03-Recipes/recipe-02-normalize-data.md`](../03-Recipes/recipe-02-normalize-data.md)

## 🔗 وابستگی‌ها
- [[task-02-scrape-detail]]
- بلاک‌کننده [[task-04-analysis-country]], [[task-05-analysis-tariff]]
