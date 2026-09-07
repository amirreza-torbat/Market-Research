---
type: task
task_id: task-04
title: تحلیل به تفکیک کشور (۶ سال)
status: pending
assignee: analyst
created: 1405-06-15
updated: 1405-06-15
depends_on: [task-03]
blocks: [task-06]
estimated_effort: 1-2 days
---

# task-04 — تحلیل به تفکیک کشور (۶ سال)

## 🎯 هدف
شناسایی کشورهایی که صادرات ایران به آن‌ها در بازه ۱۴۰۰ تا ۱۴۰۵ **افزایشی** بوده است.

## 📋 شرح کار

### ۱. محاسبه شاخص‌های کلیدی به ازای هر کشور
برای هر کشور (group by `destination_country_iso2`):
- `total_value_1400` تا `total_value_1404` (مجموع ارزش صادرات سالانه کامل).
- `total_value_1405_ytd` (جمع YTD سال جاری).
- `total_value_1405_annualized` (تخمین سالانه ۱۴۰۵).
- `cagr_5y` (نرخ رشد سالانه مرکب): `(value_1404 / value_1400)^(1/4) - 1`.
- `cagr_6y`: `(value_1405_annualized / value_1400)^(1/5) - 1`.
- `absolute_change`: `value_1404 - value_1400`.
- `percent_change`: `(value_1404 - value_1400) / value_1400 * 100`.
- `is_increasing`: اگر `cagr_5y > 0` و `value_1404 > value_1400` → True.
- `is_significant`: اگر `total_value_1404 > 1,000,000 USD` (آستانه ۱ میلیون دلار).
- `trend_consistency`: در چند سال از ۵ سال متوالی رشد داشته است؟
- `slope`, `r_squared`, `mk_p_value`, `cv` (شاخص‌های آماری طبق [[conventions]]).

### ۲. رتبه‌بندی
- Top 20 کشور با بیشترین رشد مطلق (`absolute_change`).
- Top 20 کشور با بیشترین CAGR (با شرط `is_significant`).
- Top 20 کشور با بیشترین `trend_consistency`.

### ۳. گزارش‌ها
برای هر کشور در Top 20 (دو دسته اول)، یک یادداشت Obsidian در `06-Analysis/by-country/` بساز. هر یادداشت شامل:
- نام کشور، کد ISO، پرچم (در صورت امکان).
- جدول ارزش ۵ ساله.
- نمودار روند (تولید به‌صورت PNG با matplotlib).
- CAGR, absolute_change, percent_change.
- توضیح کیفی (حداقل ۱۵۰ کلمه).
- backlink به [[task-04-analysis-country]] و [[country-XXX-trend]].

### ۴. یادداشت خلاصه
یک یادداشت `06-Analysis/by-country/_summary.md` شامل:
- تعداد کشورهای افزایشی و کاهشی.
- Top 20 در هر دسته.
- نمودار کلی.

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [ ] فایل `05-Data/processed/analysis-by-country.csv` شامل همه شاخص‌ها برای همه کشورها.
- [ ] حداقل ۴۰ یادداشت در `06-Analysis/by-country/` (۲۰ top-growth + ۲۰ top-cagr).
- [ ] نمودار PNG برای هر یادداشت.
- [ ] یادداشت `_summary.md` کامل.
- [ ] دقت محاسباتی: تست با مجموع دستی، خطا < 0.0001٪.
- [ ] commit با پیام `analysis(country): task-04 by-country analysis`.

## 📦 خروجی‌ها
- `05-Data/processed/analysis-by-country.csv`
- `06-Analysis/by-country/*.md` (۴۰+ یادداشت)
- `06-Analysis/by-country/charts/*.png`
- `06-Analysis/by-country/_summary.md`

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-analyst.md`](../02-Prompts/prompt-analyst.md)
- [`03-Recipes/recipe-03-run-analysis.md`](../03-Recipes/recipe-03-run-analysis.md)

## 🔗 وابستگی‌ها
- [[task-03-etl-normalize]]
- بلاک‌کننده [[task-06-qa-validate]]
