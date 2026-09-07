---
folder: 03-Recipes
type: recipe
recipe_id: recipe-03
title: اجرای تحلیل (کشور و تعرفه — ۶ سال)
related_tasks: [task-04, task-05, task-10, task-11, task-12]
last_updated: 1405-06-15
---

# 📖 Recipe-03 — اجرای تحلیل (کشور و تعرفه — ۶ سال)

> **نقش**: Analyst Agent
> **تسک‌های مرتبط**: [[task-04-analysis-country]]، [[task-05-analysis-tariff]]، [[task-10-trend-analysis]]، [[task-11-trend-classification]]، [[task-12-export-candidates]]
> **زمان تخمینی**: ۱-۲ روز برای task-04، ۳-۴ روز برای task-05، ۳-۴ روز برای task-10، ۱-۲ روز برای task-11، ۲ روز برای task-12

## هدف
محاسبه شاخص‌های رشد، رتبه‌بندی، ساخت نمودارها و یادداشت‌های Obsidian.

## پیش‌نیازها
- [ ] `task-03` کامل شده باشد.
- [ ] `05-Data/processed/exports_1400-1405.parquet` موجود (۶ سال).
- [ ] پکیج‌ها: `pandas`, `polars` (اختیاری برای کارایی), `pyarrow`, `matplotlib`, `scipy`, `decimal`, `numba` (اختیاری).
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
2. commit: `analysis(tariff): task-05 by-tariff analysis 6y`.
3. push و PR.

---

## بخش C: تحلیل جامع روند ۶ ساله (task-10) — **مهم‌ترین بخش**

> این بخش **حلقه کامل** روی تمامی HS Codeها × تمامی کشورها اجرا می‌کند. خروجی این بخش ستون فقرات همه تحلیل‌های بعدی است.

### مرحله C1: آماده‌سازی داده (۱ ساعت)
1. شاخه `feature/task-10-trend` بساز.
2. در `scripts/analyze_trend_6y.py`:
   - load `05-Data/processed/exports_1400-1405.parquet`.
   - خواندن `months_available_1405` از `_dataset-metadata.json`.
   - aggregate به سطح `(year, hs_code, destination_country_iso2)` با `sum(export_value_usd)`.
   - ساخت pivot table: index=`(hs_code, destination_country_iso2)`, columns=`year`.

**✅ Verification**: pivot table ساخته شود با تعداد ردیف‌های منطقی (تا ۱ میلیون).

### مرحله C2: annualize کردن ۱۴۰۵ (۳۰ دقیقه)
1. برای هر جفت: `value_1405_annualized = value_1405_ytd * 12 / months_available_1405`.
2. ذخیره در ستون جدید.

**✅ Verification**: همه جفت‌ها مقدار `value_1405_annualized` داشته باشند.

### مرحله C3: محاسبه شاخص‌های آماری (۳-۴ ساعت)
1. برای هر جفت، محاسبه:
   - `cagr_5y` (با Decimal).
   - `cagr_6y` (با Decimal).
   - `pct_change_5y`, `growth_multiplier`.
   - `slope`, `r_squared` (با `scipy.stats.linregress`).
   - `mk_p_value` (با تابع Mann-Kendall).
   - `cv` (ضریب تغییرات).
   - `trend_consistency`.
   - `mean_value`, `mean_recent_3y`.
2. **کارایی**: استفاده از `polars` یا vectorization. برای Mann-Kendall، می‌توان از `numba.jit` یا `multiprocessing.Pool` استفاده کرد.

**✅ Verification**: همه شاخص‌ها محاسبه شده باشند (NULL فقط برای موارد غیرقابل‌محاسبه).

### مرحله C4: ذخیره خروجی (۳۰ دقیقه)
1. ذخیره به `05-Data/processed/trend-analysis-6y.parquet` با schema صریح.
2. ساخت `05-Data/processed/trend-analysis-summary.md`.

**✅ Verification**: فایل Parquet باز شود و تعداد رکوردها منطقی باشد.

### مرحله C5: تست دقت (۳۰ دقیقه) — حیاتی
1. مجموع `value_1400` در trend-analysis باید با مجموع `export_value_usd` سال ۱۴۰۰ در Parquet برابر باشد.
2. تلورانس < 0.0001٪.
3. تست برای همه ۵ سال کامل.

**✅ Verification**: تست pass.

### مرحله C6: commit و PR
1. `task-10` به `review` در STATUS.md.
2. commit: `analysis(trend): task-10 full 6-year trend analysis`.
3. push و PR.

---

## بخش D: طبقه‌بندی روند (task-11)

### مرحله D1: اجرای طبقه‌بندی‌کننده (۱ ساعت)
1. شاخه `feature/task-11-classification` بساز.
2. در `scripts/classify_trends.py`:
   - load `trend-analysis-6y.parquet`.
   - اعمال تابع `classify_trend` (طبق پرامپت Analyst) روی هر جفت.
   - ذخیره به `trend-classification.parquet`.

**✅ Verification**: همه جفت‌ها دسته‌بندی شده باشند.

### مرحله D2: تجمیع به سطح HS (۳۰ دقیقه)
1. group by `hs_code` و محاسبه:
   - `n_countries_total`, `n_strong_growth`, `n_moderate_growth`, ...
   - `dominant_trend`.
   - `growth_diversity_score`.
2. ذخیره به `trend-classification-by-hs.parquet`.

### مرحله D3: ساخت یادداشت‌های Top (۴ ساعت)
1. برای هر دسته، Top 30 HS Code بر اساس `total_value_6y`.
2. یادداشت در `06-Analysis/trend/<category>/hs-XX-XXXX-XX-XX.md`.
3. نمودار روند + نمودار Top 10 کشور.

### مرحله D4: گزارش خلاصه (۱ ساعت)
1. `06-Analysis/trend/_classification-summary.md`:
   - توزیع دسته‌ها.
   - نمودار pie/bar.
   - HS Codeهای با بیشترین تعداد `strong_growth`.
   - یافته‌های کلیدی.

### مرحله D5: commit و PR
1. `task-11` به `review` در STATUS.md.
2. commit: `analysis(trend): task-11 trend classification`.
3. push و PR.

---

## بخش E: رتبه‌بندی کاندیدهای صادرات (task-12) — **هدف نهایی**

### مرحله E1: محاسبه نمره (۲ ساعت)
1. شاخه `feature/task-12-ranking` بساز.
2. در `scripts/rank_export_candidates.py`:
   - load `trend-classification-by-hs.parquet`.
   - محاسبه `export_score` (طبق فرمول در [[conventions]] بخش ۵.۳).
   - اعمال وزن‌ها از `04-State/decisions.md`.
   - اعمال فیلتر: فقط `strong_growth`, `moderate_growth`, `emerging` با `mean_recent_3y > 1M USD` و `n_destinations >= 3`.

**✅ Verification**: نمره‌ها بین ۰ و ۱.

### مرحله E2: رتبه‌بندی (۳۰ دقیقه)
1. مرتب‌سازی نزولی بر اساس `export_score`.
2. اختصاص `rank`.

### مرحله E3: توصیه‌های استراتژیک (۳ ساعت)
1. برای هر کاندید Top 100:
   - استخراج Top 5 کشورهای هدف (از `trend-classification.parquet` با دسته `strong_growth`).
   - محاسبه ریسک‌ها (نوسان، تمرکز).
   - تعیین `recommendation`: `select` / `monitor` / `investigate`.

### مرحله E4: ذخیره خروجی (۳۰ دقیقه)
1. ذخیره به `05-Data/processed/export-candidates-ranked.parquet`.

### مرحله E5: ساخت یادداشت‌های تفصیلی (۶ ساعت)
1. برای هر کاندید Top 50:
   - فایل `06-Analysis/export-candidates/rank-NN-hs-XX-XXXX-XX-XX.md`.
   - شامل: شرح کالا، جدول ۶ ساله، Top 10 کشور، نمودار، تحلیل کیفی (۲۰۰+ کلمه)، توصیه‌ها، ریسک‌ها.

### مرحله E6: گزارش اجرایی (۲ ساعت)
1. `06-Analysis/export-candidates/_executive-ranking.md`:
   - Top 20 کاندید با شرح کامل.
   - نمودار Top 20.
   - توصیه‌های کلی.

### مرحله E7: گزارش کشور-محور (۱ ساعت)
1. `06-Analysis/export-candidates/by-target-country.md`:
   - برای هر کشور مقصد بزرگ، فهرست HS Codeهای با `strong_growth`.

### مرحله E8: ماتریس فصل × کشور (۲ ساعت)
1. `06-Analysis/export-candidates/chapter-country-matrix.md`:
   - جدول ۲۱ فصل HS × Top 30 کشور.
   - نمودار heatmap (PNG).

### مرحله E9: commit و PR
1. `task-12` به `review` در STATUS.md.
2. commit: `analysis(ranking): task-12 export candidate ranking`.
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
