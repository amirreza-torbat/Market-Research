---
type: task
task_id: task-07
title: خروجی Excel نهایی
status: pending
assignee: etl-engineer
created: 1405-06-15
updated: 1405-06-15
depends_on: [task-06]
blocks: [task-09]
estimated_effort: 1 day
---

# task-07 — خروجی Excel نهایی

## 🎯 هدف
ساخت یک فایل Excel نهایی با چند شیت برای مصرف کاربر نهایی و آماده ارسال به کاربر.

## 📋 شرح کار

### ۱. ساخت Workbook
فایل `07-Exports/iran-exports-1400-1404-YYYYMMDD.xlsx` با شیت‌های زیر:

| شیت | محتوا |
|-----|-------|
| `Overview` | توضیح پروژه، تاریخ تولید، منبع، دقت |
| `Data-All` | کل داده نرمال‌شده (در صورت بزرگ بودن، نمونه + لینک به Parquet) |
| `By-Country-Summary` | خلاصه تحلیل کشورها (همه کشورها) |
| `By-Country-Top20-Growth` | Top 20 کشور با بیشترین رشد مطلق |
| `By-Country-Top20-CAGR` | Top 20 کشور با بیشترین CAGR |
| `By-Tariff-Summary` | خلاصه تحلیل HS Codeها |
| `By-Tariff-Top50` | Top 50 HS Code |
| `By-Tariff-Country` | جدول HS Code × Country (فقط رکوردهای افزایشی و معنادار) |
| `Charts-Country` | نمودارهای توپ کشورها |
| `Charts-Tariff` | نمودارهای توپ تعرفه‌ها |
| `QA` | خلاصه گزارش QA |

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
- [ ] فایل `07-Exports/iran-exports-1400-1404-YYYYMMDD.xlsx` ساخته شود.
- [ ] همه ۱۱ شیت موجود باشند.
- [ ] قالب‌بندی شامل: هدر bold، autofilter، فریز هدر، فرمت عدد.
- [ ] نمودارهای داخلی Excel کار کنند.
- [ ] فایل با Excel/LibreOffice بدون خطا باز شود.
- [ ] اندازه فایل < 50MB (در صورت بیشتر، نمونه‌گیری یا Git LFS).
- [ ] commit با پیام `feat(exports): task-07 excel workbook`.

## 📦 خروجی‌ها
- `07-Exports/iran-exports-1400-1404-YYYYMMDD.xlsx`

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-etl-engineer.md`](../02-Prompts/prompt-etl-engineer.md)
- [`03-Recipes/recipe-05-export-excel.md`](../03-Recipes/recipe-05-export-excel.md)

## 🔗 وابستگی‌ها
- [[task-06-qa-validate]]
- بلاک‌کننده [[task-09-publish-github]]
- موازی با [[task-08-export-obsidian]]
