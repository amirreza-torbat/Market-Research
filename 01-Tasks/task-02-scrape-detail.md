---
type: task
task_id: task-02
title: استخراج جزئیات هر رکورد
status: pending
assignee: scraper
created: 1405-06-15
updated: 1405-06-15
depends_on: [task-01]
blocks: [task-03]
estimated_effort: 1-2 days
---

# task-02 — استخراج جزئیات هر رکورد

## 🎯 هدف
در صورتی که در `task-01` فقط خلاصه استخراج شده، در این تسک جزئیات تکمیلی (مثل شرح کامل کالا، واحد ثانویه، استان مبدأ و...) استخراج می‌شود.

## 📋 شرح کار

### ۱. شناسایی فیلدهای گمشده
- مقایسه فیلدهای استخراج‌شده با فهرست مورد انتظار در `00-Overview/data-sources.md`.
- فهرست فیلدهای ناقص در `04-State/issues.md` (در صورت وجود).

### ۲. استخراج جزئیات
- برای هر رکورد در `05-Data/interim/exports_YYYY_raw.csv`:
  - اگر صفحه جزئیات موجود است، GET به آن.
  - استخراج فیلدهای گمشده.
  - merge با CSV اصلی.

### ۳. آیا نیاز است؟
اگر منبع داده همه فیلدها را در صفحه فهرست ارائه می‌دهد، این تسک می‌تواند به‌عنوان تأیید کامل‌بودن داده `task-01` استفاده شود. در این صورت فقط verify انجام می‌شود.

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [ ] همه فیلدهای مورد انتظار در `00-Overview/data-sources.md` موجود باشد.
- [ ] اگر فیلدی قابل استخراج نبود، در `04-State/issues.md` مستند شود.
- [ ] CSVهای `05-Data/interim/exports_YYYY_raw.csv` کامل باشند.

## 📦 خروجی‌ها
- CSVهای نهایی در `05-Data/interim/exports_YYYY_raw.csv`
- لاگ اعتبارسنجی فیلدها

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-scraper.md`](../02-Prompts/prompt-scraper.md)

## 🔗 وابستگی‌ها
- [[task-01-scrape-list]]
- بلاک‌کننده [[task-03-etl-normalize]]
