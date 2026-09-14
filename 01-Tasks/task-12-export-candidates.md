---
type: task
task_id: task-12
title: رتبه‌بندی محصولات کاندید صادرات
status: review
assignee: analyst
created: 1405-06-15
updated: 1405-06-23
depends_on: [task-11]
blocks: [task-06, task-08]
estimated_effort: 2 days
priority: critical
---

# task-12 — رتبه‌بندی محصولات کاندید صادرات (Export Candidate Ranking)

## 🎯 هدف
**هدف نهایی پروژه**: شناسایی و رتبه‌بندی محصولات با روند رو به رشد برای انتخاب صادرات. این تسک به کاربر می‌گوید **کدام محصولات** برای توسعه صادرات مناسب‌ترند و **به کدام کشورها**.

## 📋 شرح کار

### ۱. تعریف معیارهای انتخاب
از [`conventions.md`](../00-Overview/conventions.md) بخش ۵.۳:

```
export_score = w1 * norm(cagr_6y)
             + w2 * norm(slope)
             + w3 * norm(mean_recent_3y)
             + w4 * norm(n_destinations)
             + w5 * norm(trend_consistency)
             - w6 * norm(cv)
```

وزن‌های پیشنهادی (قابل تنظیم در [`decisions.md`](../04-State/decisions.md)):
- `w1 = 0.30` (رشد)
- `w2 = 0.20` (شیب روند)
- `w3 = 0.20` (حجم)
- `w4 = 0.10` (تنوع بازار)
- `w5 = 0.10` (ثبات)
- `w6 = 0.10` (جریمه نوسان)

### ۲. محاسبه نمره برای هر HS Code
برای هر HS Code (aggregated across countries):
- `cagr_6y_aggregated` — از `trend-classification-by-hs`.
- `slope_aggregated` — slope از OLS روی مقادیر aggregated.
- `mean_recent_3y_aggregated` — میانگین ۱۴۰۲ تا ۱۴۰۴.
- `n_destinations_active` — تعداد کشورهایی که در ۱۴۰۴ صادرات داشته‌اند.
- `trend_consistency_aggregated` — از ۰ تا ۵.
- `cv_aggregated` — ضریب تغییرات مقادیر سالانه aggregated.

### ۳. نرمال‌سازی
- Min-Max normalization روی کل دیتاست (سراسری HS Codeها).
- مقادیر NaN به ۰.
- مقادیر منفی برای CV (که جریمه است) به‌صورت `(1 - norm(cv))` استفاده شود.

### ۴. فیلتر اولیه
فقط HS Codeهایی که:
- در دسته `strong_growth`، `moderate_growth`، یا `emerging` باشند.
- `mean_recent_3y_aggregated > 1,000,000 USD` (حداقل ۱ میلیون دلار سالانه).
- `n_destinations_active >= 3` (حداقل ۳ کشور مقصد).

### ۵. رتبه‌بندی
- مرتب‌سازی نزولی بر اساس `export_score`.
- اختصاص `rank` (۱، ۲، ۳، ...).
- برای Top 100، یادداشت تفصیلی بساز.

### ۶. توصیه‌های استراتژیک
برای هر کاندید Top، توصیه‌های زیر:
- **انتخاب برای صادرات**: آیا بله/خیر.
- **کشورهای هدف**: Top 5 کشور مقصد با بهترین روند.
- **ریسک‌ها**: نوسان، تمرکز روی یک کشور، ...
- **مزیت‌های رقابتی احتمالی**: بر اساس نوع کالا و منطقه.
- **توصیه اقدام**: توسعه بازار، حفظ بازار فعلی، تنوع‌بخشی، ...

### ۷. خروجی‌ها

#### ۷.۱ جدول رتبه‌بندی نهایی
فایل `05-Data/processed/export-candidates-ranked.parquet`:

| ستون | توضیح |
|------|-------|
| `rank` | رتبه (۱ = بهترین) |
| `hs_code` | |
| `hs_description` | |
| `hs_chapter` | ۲ رقم اول (chapter) |
| `export_score` | نمره نهایی (۰ تا ۱) |
| `trend_category` | از task-11 |
| `cagr_6y_aggregated` | |
| `mean_recent_3y_aggregated` | |
| `n_destinations_active` | |
| `trend_consistency_aggregated` | |
| `cv_aggregated` | |
| `top_5_countries` | لیست ISO2 با رشد مثبت |
| `top_5_countries_value_1404` | ارزش ۱۴۰۴ به آن کشورها |
| `recommendation` | `select` / `monitor` / `investigate` |
| `risk_flags` | لیست ریسک‌ها |
| `score_growth` | مولفه رشد (w1 * norm_cagr) |
| `score_slope` | |
| `score_volume` | |
| `score_diversity` | |
| `score_consistency` | |
| `score_volatility_penalty` | (منفی) |

#### ۷.۲ گزارش اجرایی کاندیدها
فایل `06-Analysis/export-candidates/_executive-ranking.md`:
- Top 20 کاندید با شرح کامل.
- برای هر کدام: شرح کالا، روند، کشورهای هدف، توصیه.
- حداقل ۱۵۰ کلمه به ازای هر کاندید.
- نمودار Top 20 با نمودار میله‌ای.

#### ۷.۳ یادداشت‌های تفصیلی
برای هر کاندید در Top 50:
- فایل `06-Analysis/export-candidates/rank-NN-hs-XX-XXXX-XX-XX.md`.
- شامل:
  - شرح کالا و فصل HS.
  - جدول روند ۶ ساله aggregated.
  - جدول Top 10 کشورهای با رشد.
  - نمودار روند aggregated.
  - نمودار سهم کشورها در ۱۴۰۴.
  - شاخص‌ها و نمره.
  - تحلیل کیفی (۲۰۰+ کلمه).
  - توصیه‌های استراتژیک.
  - ریسک‌ها.

#### ۷.۴ گزارش کشور-محور
فایل `06-Analysis/export-candidates/by-target-country.md`:
- برای هر کشور مقصد بزرگ (Top 30)، فهرست HS Codeهای با رشد قوی به آن کشور.
- ماتریس heat: کشور × فصل HS.

#### ۷.۵ ماتریس فصل × کشور
فایل `06-Analysis/export-candidates/chapter-country-matrix.md`:
- جدول: ۲۱ فصل HS (۲-digit) × Top 30 کشور.
- مقدار سلول: تعداد HS Codeهای با `strong_growth` به آن کشور در آن فصل.
- نمودار heatmap (PNG).

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [x] فایل `05-Data/processed/export-candidates-ranked.parquet` ساخته شود. (۵۷۴ × ۳۱ ستون)
- [x] حداقل ۱۰۰ رکورد در آن (پس از فیلتر). (۵۷۴ کاندید)
- [x] همه رکوردها نمره و رتبه داشته باشند. (۱۴/۱۴ اعتبارسنجی PASS)
- [x] فایل `06-Analysis/export-candidates/_executive-ranking.md` (با Top 20). (+ نمودار میله‌ای Top 20)
- [x] ۵۰ یادداشت تفصیلی در `06-Analysis/export-candidates/`. (۵۰ یادداشت + ۵۰ نمودار)
- [x] گزارش `by-target-country.md` کامل. (۱۰۵ کشور، Top 30 + Top 10 HS هر کشور)
- [x] ماتریس `chapter-country-matrix.md` با نمودار heatmap. (heatmap ۵۲×۳۰)
- [x] commit با پیام `analysis(ranking): task-12 export candidate ranking`. (`34fe090`)
- [x] تطابق Issue-008 (cagr_5y به‌جای cagr_6y) و روش membership مستند شد (گزارش §۱ و §۹).
- [x] push به شاخه `feature/task-12-ranking`.

> **یادداشت تکمیل (۱۴۰۵-۰۶-۲۳)**: نمره‌ها در بازه [-۰.۰۳, ۰.۳۵] فشرده‌اند (هیچ کاندیدی در همه ۶ بُعد هم‌زمان پیشتاز نیست)؛ در نتیجه آستانه‌های ثابت §۷ توصیه (select>0.7/monitor≥0.4) به همه «investigate» می‌رسد. این یافته + پیشنهاد بازکالیبراسیون در `_executive-ranking.md` §۵ مستند شد؛ سیگنال قابل‌اقدام رتبه‌بندی (۱..۵۷۴) و یادداشت‌های Top 50 است. ستون `cagr_6y_aggregated` طبق Issue-008 با نام `cagr_5y_aggregated` ذخیره شد.

## 📦 خروجی‌ها
- `05-Data/processed/export-candidates-ranked.parquet`
- `06-Analysis/export-candidates/_executive-ranking.md`
- `06-Analysis/export-candidates/rank-NN-*.md` (۵۰ یادداشت)
- `06-Analysis/export-candidates/by-target-country.md`
- `06-Analysis/export-candidates/chapter-country-matrix.md`
- `06-Analysis/export-candidates/charts/*.png`

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-analyst.md`](../02-Prompts/prompt-analyst.md)
- [`03-Recipes/recipe-10-export-ranking.md`](../03-Recipes/recipe-10-export-ranking.md) (در صورت ساخت)

## 🔗 وابستگی‌ها
- [[task-11-trend-classification]] (الزامی)
- بلاک‌کننده [[task-06-qa-validate]], [[task-08-export-obsidian]]

## 🔗 یادداشت
- این تسک خروجی نهایی اصلی پروژه است — کاربر می‌خواهد برای **انتخاب محصول صادراتی** از آن استفاده کند.
- وزن‌ها در [`decisions.md`](../04-State/decisions.md) قابل تنظیم.
- اگر کاربر وزن‌های متفاوتی خواست، این تسک با وزن‌های جدید re-run شود.
