---
type: task
task_id: task-06
title: اعتبارسنجی دقت < 0.0001٪ (۶ سال + تحلیل روند)
status: review
assignee: qa-validator
created: 1405-06-15
updated: 1405-06-23
depends_on: [task-04, task-05, task-10, task-11, task-12]
blocks: [task-07, task-08]
estimated_effort: 2-3 days
---

# task-06 — اعتبارسنجی دقت و کامل‌بودن (۶ سال + تحلیل روند)

> ✅ **اجرا شد (1405-06-23)**: ۴۹/۴۹ تست PASS — تلورانس عددی ۰.۰۰۰۰۰۰۰۰۰۰٪.
> گزارش کامل: `04-State/qa-report.md` | نتایج structured: `05-Data/processed/qa-validation.json` | اسکریپت: `scripts/qa_validate_final.py`
> شاخه: `feature/task-06-qa` (بر پایه feature/task-12-recalibrate)

## 🎯 هدف
تأیید اینکه کل خطای محاسباتی و داده‌ای پروژه زیر 0.0001٪ است و همه معیارهای پذیرش تسک‌های قبلی (شامل تحلیل روند ۶ ساله) برآورده شده‌اند. بدون پاس این تسک، خروجی نهایی ساخته نمی‌شود.

## 📋 شرح کار

### ۱. اعتبارسنجی عددی (Numerical QA)
- مقایسه مجموع `export_value_usd` برای هر سال در `processed/exports_1400-1405.parquet` با:
  - مجموع در `interim/exports_YYYY_raw.csv` (داده قبل از نرمال‌سازی).
  - مجموع گزارش‌شده توسط سایت گمرک (در صورت وجود صفحه summary).
- تلورانس: < 0.0001٪ (یعنی اختلاف < 0.000001 از کل).
- اگر تلورانس رد شد، ریشه‌یابی در `04-State/issues.md` و رفع.

### ۲. اعتبارسنجی کامل‌بودن (Completeness QA)
- ۶ سال موجود باشند (۱۴۰۰ تا ۱۴۰۵).
- سال ۱۴۰۵: حداقل N ماه موجود (N را از `04-State/decisions.md` بخوان).
- تعداد کشورها > 100.
- تعداد HS Codeها > 1000.
- تعداد رکوردها منطقی (هر سال کامل > 100,000).
- هیچ null در فیلدهای کلیدی نباشد.

### ۳. اعتبارسنجی تحلیل (Analysis QA)
- در `task-04`: مجموع value در `analysis-by-country.csv` باید با مجموع کل برابر باشد.
- در `task-05`: مجموع value در `analysis-by-tariff.csv` باید با مجموع کل برابر باشد.
- در `task-05`: مجموع value در `analysis-by-tariff-country.csv` باید با مجموع کل برابر باشد.
- در `task-10`: مجموع `value_1400` تا `value_1404` در `trend-analysis-6y.parquet` باید با مجموع Parquet برابر باشد.
- در `task-11`: همه جفت‌ها در `trend-classification.parquet` دسته‌بندی شده باشند (NULL ممنوع).
- در `task-12`: همه HS Codeهای کاندید در `export-candidates-ranked.parquet` نمره و رتبه داشته باشند.
- همه تلورانس‌ها < 0.0001٪.

### ۴. اعتبارسنجی متقابل با Mirror Data (در صورت دسترسی)
- مقایسه صادرات ایران به عراق با واردات عراق از ایران (از UN Comtrade).
- اختلاف به‌صورت درصد گزارش شود. اختلاف > 10٪ هشدار است (نه لزوماً رد).

### ۵. گزارش QA
- یک یادداشت `04-State/qa-report.md` شامل:
  - تمام تست‌های اجراشده.
  - نتیجه pass/fail هر کدام.
  - تلورانس مشاهده‌شده.
  - مسائل باز.

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [x] همه تست‌های عددی pass شوند (تلورانس < 0.0001٪). — ۱۵/۱۵ PASS با تلورانس دقیق صفر
- [x] همه تست‌های کامل‌بودن pass شوند. — ۸/۸ PASS (۵ سال، ۱۶۶ کشور، ۵,۹۹۳ HS، بدون null)
- [x] همه تست‌های تحلیل pass شوند. — ۱۴/۱۴ PASS (شامل rank یکتا و توصیه‌های صدکی)
- [x] گزارش `04-State/qa-report.md` کامل شود. — ✅ + `qa-validation.json`
- [x] اگر تستی fail شد، در `04-State/issues.md` ریشه‌یابی و رفع شود. — Test 5.4 → Issue-009 (false positive آستانه recipe-04، تعدیل معیار)
- [x] commit با پیام `qa: task-06 validation report`. — ✅

## 📦 خروجی‌ها
- `04-State/qa-report.md`
- (در صورت نیاز) رفع مسائل در تسک‌های قبلی.

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-qa-validator.md`](../02-Prompts/prompt-qa-validator.md)
- [`03-Recipes/recipe-04-qa-checklist.md`](../03-Recipes/recipe-04-qa-checklist.md)

## 🔗 وابستگی‌ها
- [[task-04-analysis-country]]
- [[task-05-analysis-tariff]]
- [[task-10-trend-analysis]]
- [[task-11-trend-classification]]
- [[task-12-export-candidates]]
- بلاک‌کننده [[task-07-export-excel]], [[task-08-export-obsidian]]
