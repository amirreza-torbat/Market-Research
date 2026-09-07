---
folder: 03-Recipes
type: recipe
recipe_id: recipe-03
title: اجرای تحلیل (کشور و تعرفه)
related_tasks: [task-04, task-05]
last_updated: 1405-06-15
---

# 📖 Recipe-03 — اجرای تحلیل

> **نقش**: Analyst Agent
> **تسک‌های مرتبط**: [[task-04-analysis-country]], [[task-05-analysis-tariff]]
> **زمان تخمینی**: ۱-۲ روز برای task-04، ۳-۴ روز برای task-05

## هدف
محاسبه شاخص‌های رشد، رتبه‌بندی، ساخت نمودارها و یادداشت‌های Obsidian.

## پیش‌نیازها
- [ ] `task-03` کامل شده باشد.
- [ ] `05-Data/processed/exports_1400-1404.parquet` موجود.
- [ ] پکیج‌ها: `pandas`, `pyarrow`, `matplotlib`, `decimal`.
- [ ] فونت `Noto Sans SC` نصب شده باشد (برای فارسی در نمودار).

## بخش A: تحلیل کشور (task-04)

### مرحله A1: محاسبه شاخص‌ها (۲ ساعت)
1. شاخه `feature/task-04-by-country` بساز.
2. در `scripts/analyze_by_country.py`:
   - load Parquet.
   - pivot table: index=`destination_country_iso2`, columns=`year`, values=`export_value_usd`.
   - محاسبه `cagr`, `absolute_change`, `percent_change`, `is_increasing`, `is_significant`, `trend_consistency`.
3. ذخیره به `05-Data/processed/analysis-by-country.csv`.

**✅ Verification**: فایل CSV ساخته شود و تعداد رکوردها > 100.

### مرحله A2: تست دقت (۳۰ دقیقه)
1. `sum(total_value)` در CSV باید با `sum(export_value_usd)` در Parquet برابر باشد.
2. تلورانس < 0.0001٪.

**✅ Verification**: تست pass.

### مرحله A3: ساخت نمودارها (۳ ساعت)
1. برای هر کشور در Top 20 (دو دسته: absolute_change و cagr):
   - نمودار خطی ۵ ساله.
   - ذخیره در `06-Analysis/by-country/charts/country-XX-trend.png`.
2. تنظیمات فونت فارسی (طبق پرامپت Analyst).
3. `constrained_layout=True`.

**✅ Verification**: ۴۰ نمودار PNG ساخته شود.

### مرحله A4: ساخت یادداشت‌های Obsidian (۴ ساعت)
1. با قالب `_templates/note-analysis-country.md`.
2. برای هر کشور Top 20:
   - عنوان: `country-XX-trend.md`.
   - بخش‌ها: خلاصه، داده‌ها، نمودار، شاخص‌ها، تحلیل کیفی (۱۵۰+ کلمه)، یافته‌ها، مراجع.
3. ذخیره در `06-Analysis/by-country/`.

**✅ Verification**: ۴۰ یادداشت ساخته شود.

### مرحله A5: یادداشت خلاصه (۱ ساعت)
1. `06-Analysis/by-country/_summary.md`:
   - آمار کلی.
   - Top 20 فهرست‌ها.
   - نمودار کلی.
   - حداقل ۳ یافته کلیدی (هر کدام ۵۰+ کلمه).

**✅ Verification**: خلاصه کامل.

### مرحله A6: commit و PR
1. `task-04` به `review` در STATUS.md.
2. commit: `analysis(country): task-04 by-country analysis`.
3. push و PR.

---

## بخش B: تحلیل تعرفه (task-05)

### مرحله B1: محاسبه به ازای (HS Code × Country) (۴ ساعت)
1. شاخه `feature/task-05-by-tariff` بساز.
2. در `scripts/analyze_by_tariff.py`:
   - load Parquet.
   - pivot table: index=(`hs_code`, `destination_country_iso2`), columns=`year`, values=`export_value_usd`.
   - محاسبه شاخص‌ها.
3. ذخیره به `05-Data/processed/analysis-by-tariff-country.csv`.

**✅ Verification**: فایل CSV ساخته شود.

### مرحله B2: محاسبه به ازای HS Code (aggregated) (۲ ساعت)
1. group by `hs_code` و محاسبه شاخص‌ها.
2. ذخیره به `05-Data/processed/analysis-by-tariff.csv`.

**✅ Verification**: فایل CSV ساخته شود.

### مرحله B3: تست دقت (۳۰ دقیقه)
- `sum(total_value)` در هر دو CSV باید با کل برابر باشد.
- تلورانس < 0.0001٪.

### مرحله B4: فیلتر و رتبه‌بندی (۱ ساعت)
1. فقط HS Codeهای `is_significant` (مجموع ۵ ساله > 10M USD).
2. رتبه‌بندی بر اساس:
   - تعداد کشور با رشد.
   - absolute_change.
   - CAGR.

### مرحله B5: ساخت نمودارها (۴ ساعت)
1. برای هر HS Code در Top 50:
   - نمودار خطی ۵ ساله (aggregated).
   - نمودار میله‌ای Top 10 کشور برای این HS Code.
2. ذخیره در `06-Analysis/by-tariff/charts/`.

**✅ Verification**: ۱۰۰ نمودار (۵۰ HS × ۲ نمودار).

### مرحله B6: ساخت یادداشت‌های Obsidian (۶ ساعت)
1. با قالب `_templates/note-analysis-tariff.md`.
2. برای هر HS Code در Top 50:
   - عنوان: `hs-XX-XXXX-XX-XX.md`.
   - بخش‌ها: خلاصه، داده‌ها، نمودار، شاخص‌ها، کشورهای افزایشی (جدول)، تحلیل کیفی (۱۵۰+ کلمه)، مراجع.
3. ذخیره در `06-Analysis/by-tariff/`.

**✅ Verification**: ۵۰ یادداشت ساخته شود.

### مرحله B7: یادداشت خلاصه (۲ ساعت)
1. `06-Analysis/by-tariff/_summary.md`:
   - آمار کلی.
   - Top 50 فهرست.
   - heatmap HS Code × Country (با matplotlib).
   - حداقل ۳ یافته کلیدی.

### مرحله B8: commit و PR
1. `task-05` به `review` در STATUS.md.
2. commit: `analysis(tariff): task-05 by-tariff analysis`.
3. push و PR.

## مدیریت خطا (Rollback)

### اگر حافظه کم آمد (task-05):
- داده را به chunks تقسیم کن (مثلاً به ازای هر سال).
- از `pyarrow` به‌جای `pandas` برای کار با داده بزرگ استفاده کن.
- یا از `polars` به‌جای `pandas`.

### اگر نمودار فارسی خراب شد:
- مطمئن شو `Noto Sans SC` نصب است (`fc-list | grep -i noto`).
- `font.sans-serif` را به `['Noto Sans SC', 'DejaVu Sans']` تنظیم کن.

## مراجع
- [[task-04-analysis-country]]
- [[task-05-analysis-tariff]]
- [[prompt-analyst]]
- [[conventions]]
