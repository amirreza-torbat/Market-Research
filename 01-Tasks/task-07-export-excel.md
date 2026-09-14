---
type: task
task_id: task-07
title: خروجی Excel نهایی (۶ سال + روند + کاندیدها)
status: review
assignee: etl-engineer
created: 1405-06-15
updated: 1405-06-24
depends_on: [task-06]
blocks: [task-09]
estimated_effort: 1-2 days
---

# task-07 — خروجی Excel نهایی (۶ سال + روند + کاندیدها)

## 🎯 هدف
ساخت یک فایل Excel نهایی با چند شیت برای مصرف کاربر نهایی و آماده ارسال به کاربر.

## 📋 شرح کار

### ۱. ساخت Workbook
فایل `07-Exports/iran-exports-1400-1405-YYYYMMDD.xlsx` با شیت‌های زیر:

| شیت | محتوا |
|-----|-------|
| `Overview` | توضیح پروژه، تاریخ تولید، منبع، دقت |
| `Data-All` | کل داده نرمال‌شده (در صورت بزرگ بودن، نمونه + لینک به Parquet) |
| `By-Country-Summary` | خلاصه تحلیل کشورها (همه کشورها) — ۶ سال |
| `By-Country-Top20-Growth` | Top 20 کشور با بیشترین رشد مطلق |
| `By-Country-Top20-CAGR` | Top 20 کشور با بیشترین CAGR |
| `By-Tariff-Summary` | خلاصه تحلیل HS Codeها — ۶ سال |
| `By-Tariff-Top50` | Top 50 HS Code |
| `By-Tariff-Country` | جدول HS Code × Country (فقط رکوردهای افزایشی و معنادار) |
| **`Trend-All-HS-Country`** | **جدول master trend-analysis-6y (تمام جفت‌ها با شاخص‌ها)** |
| **`Trend-Classification`** | **تمام جفت‌ها با trend_category و confidence** |
| **`Trend-By-HS-Summary`** | **تجمیع به ازای هر HS Code با dominant_trend** |
| **`Export-Candidates-Ranked`** | **Top 100 کاندید صادرات با export_score و rank** |
| **`Export-Candidates-Top20-Detail`** | **Top 20 با جزئیات کامل کشورها** |
| **`Chapter-Country-Matrix`** | **ماتریس فصل HS × کشور (تعداد رشد قوی)** |
| `Charts-Country` | نمودارهای توپ کشورها |
| `Charts-Tariff` | نمودارهای توپ تعرفه‌ها |
| `Charts-Trend-Classification` | نمودار توزیع دسته‌های روند |
| `Charts-Export-Candidates` | نمودار Top 20 کاندید |
| `QA` | خلاصه گزارش QA |

> شیت‌های **bold** جدید اضافه شده‌اند برای پوشش کامل task-10، task-11، task-12.

### ۲. قالب‌بندی
- هدرها bold با رنگ پس‌زمینه.
- فیلتر خودکار (autofilter) روی همه شیت‌ها.
- ستون‌ها به اندازه محتوا تنظیم شوند.
- فرمت عدد: `#,##0.0000` برای ارزش‌ها.
- فریز کردن هدر و ستون اول.
-conditional formatting روی ستون CAGR (سبز برای مثبت، قرمز برای منفی).

### ۳. نمودارهای داخلی Excel
- در شیت `Charts-Country`: نمودار میله‌ای Top 20 کشور (بر اساس CAGR).
- در شیت `Charts-Tariff`: نمودار میله‌ای Top 20 HS Code (بر اساس CAGR).
- در شیت `Overview`: نمودار خطی مجموع صادرات ۵ ساله.

### ۴. اعتبارسنجی نهایی
- باز کردن فایل با openpyxl و بررسی.
- تست فرمول‌ها (در صورت وجود).
- تأیید اینکه همه شیت‌ها موجود و درست هستند.

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [ ] فایل `07-Exports/iran-exports-1400-1405-YYYYMMDD.xlsx` ساخته شود.
- [ ] همه شیت‌ها (۱۸ شیت) موجود باشند.
- [ ] قالب‌بندی شامل: هدر bold، autofilter، فریز هدر، فرمت عدد.
- [ ] نمودارهای داخلی Excel کار کنند.
- [ ] فایل با Excel/LibreOffice بدون خطا باز شود.
- [ ] اندازه فایل < 100MB (در صورت بیشتر، نمونه‌گیری یا Git LFS).
- [ ] commit با پیام `feat(exports): task-07 excel workbook 6y`.

## 📦 خروجی‌ها
- `07-Exports/iran-exports-1400-1405-YYYYMMDD.xlsx`

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-etl-engineer.md`](../02-Prompts/prompt-etl-engineer.md)
- [`03-Recipes/recipe-05-export-excel.md`](../03-Recipes/recipe-05-export-excel.md)

## 🔗 وابستگی‌ها
- [[task-06-qa-validate]]
- بلاک‌کننده [[task-09-publish-github]]
- موازی با [[task-08-export-obsidian]]
