---
folder: 03-Recipes
type: recipe
recipe_id: recipe-02
title: نرمال‌سازی و ETL
related_tasks: [task-03]
last_updated: 1405-06-15
---

# 📖 Recipe-02 — نرمال‌سازی و ETL

> **نقش**: ETL Engineer Agent
> **تسک‌های مرتبط**: [[task-03-etl-normalize]]
> **زمان تخمینی**: ۲-۳ روز

## هدف
تبدیل داده خام به مدل داده‌ای تحلیلی تمیز و یکپارچه با دقت عددی < 0.0001٪.

## پیش‌نیازها
- [ ] `task-01` و `task-02` کامل شده باشند.
- [ ] پکیج‌ها: `pandas`, `pyarrow`, `openpyxl`, `python-decimal`.
- [ ] مطالعه [`00-Overview/conventions.md`](../00-Overview/conventions.md).

## مراحل

### مرحله ۱: ساخت کلاس ETLPipeline (۳ ساعت)
1. شاخه `feature/task-03-etl` بساز.
2. در `scripts/etl_normalize.py` کلاس `ETLPipeline` (طبق پرامپت ETL).
3. متدها:
   - `load_raw(year)`.
   - `clean(df)`.
   - `normalize_country(df)`.
   - `normalize_hs_code(df)`.
   - `convert_to_decimal(df)`.
   - `validate(df, year)`.
   - `save_parquet(df)`.

**✅ Verification**: کلاس با ۱ سال تست شود.

### مرحله ۲: ساخت نگاشت کشورها (۲ ساعت)
1. استخراج همه نام‌های فارسی کشورها از `05-Data/interim/exports_*_raw.csv`.
2. ساخت فایل `05-Data/processed/countries-mapping.csv` با ستون‌های:
   - `country_fa` (نام فارسی در منبع).
   - `country_iso2` (کد ISO 3166-1 alpha-2).
   - `country_en` (نام انگلیسی).
   - `notes` (در صورت ابهام).
3. مرجع: لیست رسمی ISO 3166-1.
4. در صورت ابهام (مثلاً "کره" → KP یا KR)، در `04-State/issues.md` ثبت کن.

**✅ Verification**: همه نام‌های فارسی نگاشت شده باشند.

### مرحله ۳: اجرای پاکسازی برای هر سال (۴ ساعت)
1. برای هر سال ۱۴۰۰ تا ۱۴۰۴:
   - `load_raw(year)`.
   - `clean(df)` (حذف تکراری، NA).
   - `normalize_country(df)`.
   - `normalize_hs_code(df)`.
   - `convert_to_decimal(df)`.
2. concat همه سال‌ها.
3. ذخیره به Parquet.

**✅ Verification**: فایل `05-Data/processed/exports_1400-1404.parquet` ساخته شود.

### مرحله ۴: ساخت جداول مرجع (۱ ساعت)
1. `countries.csv` (استخراج شده از نگاشت).
2. `hs-codes.csv` (کد + شرح، استخراج شده از داده).
3. `exchange-rates.csv` (در صورت نیاز به تبدیل واحد).

**✅ Verification**: همه فایل‌ها ساخته شده باشند.

### مرحله ۵: تست دقت عددی (۱ ساعت) — **حیاتی**
1. اسکریپت `scripts/test_precision.py`:
   ```python
   from decimal import Decimal
   import pandas as pd
   import pyarrow.parquet as pq
   
   def test_precision():
       # مجموع در داده خام
       raw_sums = {}
       for year in range(1400, 1405):
           df = pd.read_csv(f"05-Data/interim/exports_{year}_raw.csv", dtype=str)
           raw_sums[year] = sum(Decimal(str(v)) for v in df["export_value_usd"])
       
       # مجموع در داده پردازش‌شده
       proc = pq.read_table("05-Data/processed/exports_1400-1404.parquet").to_pandas()
       proc["export_value_usd"] = proc["export_value_usd"].apply(Decimal)
       proc_sums = proc.groupby("year")["export_value_usd"].sum().to_dict()
       
       # مقایسه
       for year in range(1400, 1405):
           tolerance = abs(proc_sums[year] - raw_sums[year]) / raw_sums[year]
           print(f"Year {year}: tolerance = {tolerance}")
           assert tolerance < Decimal("0.000001"), f"Year {year} tolerance too high"
   ```
2. اجرا و تأیید pass.

**✅ Verification**: همه سال‌ها با تلورانس < 0.0001٪.

### مرحله ۶: گزارش validation (۱ ساعت)
1. در `05-Data/processed/_validation-report.md`:
   - تعداد رکوردها قبل و بعد از پاکسازی (هر سال).
   - تعداد رکوردهای حذف‌شده با دلیل.
   - تلورانس عددی مشاهده‌شده.
   - آمار توصیفی (min, max, mean, sum) برای value و weight.
   - تعداد کشورها و HS Codeها.

**✅ Verification**: گزارش کامل و خوانا.

### مرحله ۷: commit و PR (۳۰ دقیقه)
1. در `04-State/STATUS.md`، `task-03` را به `review` تغییر بده.
2. در `04-State/progress.md` سطر نهایی.
3. commit با پیام `feat(etl): task-03 normalize and validate exports`.
4. push و PR.

**✅ Verification**: PR ایجاد شده.

## مدیریت خطا (Rollback)

### اگر تست دقت fail شد:
1. در `04-State/issues.md` ثبت کن با جزئیات:
   - کدام سال؟
   - تلورانس مشاهده‌شده چقدر؟
   - احتمالاً کجای پاکسازی مقدار از دست رفته (مثلاً rounding در تبدیل Decimal).
2. ریشه‌یابی کن (مثلاً NaNها به 0 تبدیل شده‌اند؟).
3. اصلاح کن و تست را re-run.

### اگر نگاشت کشورها ناقص بود:
1. نام‌های نگاشت‌نشده را در `04-State/issues.md` فهرست کن.
2. با کاربر یا منابع خارجی تأیید کن.
3. نگاشت را کامل کن.

## نکات مهم

- ⚠️ **الزامی**: از `decimal.Decimal` استفاده کن، نه `float`.
- ⚠️ **HS Code به‌عنوان string**: چون ممکن است با 0 شروع شود.
- ⚠️ **Parquet schema صریح**: نه inferred.

## مراجع
- [[task-03-etl-normalize]]
- [[prompt-etl-engineer]]
- [[conventions]]
