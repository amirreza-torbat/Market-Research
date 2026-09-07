---
type: task
task_id: task-01
title: استخراج فهرست صادرات (۵ سال)
status: pending
assignee: scraper
created: 1405-06-15
updated: 1405-06-15
depends_on: [task-00]
blocks: [task-02]
estimated_effort: 2-3 days
---

# task-01 — استخراج فهرست صادرات (۵ سال)

## 🎯 هدف
استخراج **فهرست کامل صادرات ایران** در سال‌های ۱۴۰۰، ۱۴۰۱، ۱۴۰۲، ۱۴۰۳، ۱۴۰۴ از سایت گمرک. در این مرحله فقط متادیتای هر رکورد (سال، ماه، کد تعرفه، کشور مقصد، ارزش، وزن) استخراج می‌شود. جزئیات بیشتر در `task-02`.

## 📋 شرح کار

### ۱. تأیید URL منبع
- مطالعه [`00-Overview/data-sources.md`](../00-Overview/data-sources.md).
- در `04-State/decisions.md` URL نهایی توسط کاربر تأیید شود.

### ۲. کشف ساختار صفحه
- بازدید دستی یا با `curl` از صفحه.
- شناسایی: pagination، فرم فیلتر، type درخواست (GET/POST)، captcha.
- شناسایی encoding و کوکی‌های session.

### ۳. ساخت Scraper
- پایتون با `httpx` (async) یا `requests` (sync).
- تأخیر ۲-۳ ثانیه بین درخواست‌ها.
- retry با backoff نمایی (حداکثر ۳ بار).
- ذخیره پاسخ خام در `05-Data/raw/YYYY/`.

### ۴. حلقه استخراج (Loop)
برای هر سال (۱۴۰۰ تا ۱۴۰۴):
  برای هر ماه (۱ تا ۱۲):
    برای هر صفحه (۱ تا N):
      GET/POST به سایت
      ذخیره HTML خام
      استخراج فیلدهای مورد نیاز با BeautifulSoup
      append به CSV موقت

### ۵. لاگ و گزارش
- در `04-State/progress.md` هر ۱۰۰ رکورد لاگ شود.
- در پایان، آمار خلاصه در `05-Data/raw/_summary.md` نوشته شود.

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [ ] برای هر سال، فایل HTML خام در `05-Data/raw/YYYY/` ذخیره شده باشد.
- [ ] برای هر سال، یک CSV موقت در `05-Data/interim/exports_YYYY_raw.csv` ساخته شده باشد.
- [ ] تعداد کل رکوردها منطقی باشد (هر سال > 100,000 رکورد متوقع است).
- [ ] نرخ موفقیت استخراج > 99٪ (یعنی < 1٪ صفحه به خطا خورده باشد).
- [ ] گزارش خلاصه در `05-Data/raw/_summary.md` شامل: تعداد رکوردها، تعداد کشورها، تعداد کدهای تعرفه.
- [ ] commit با پیام `feat(scraper): task-01 extract export list YYYY` برای هر سال.

## 📦 خروجی‌ها
- `05-Data/raw/1400/` تا `05-Data/raw/1404/` شامل HTML خام
- `05-Data/interim/exports_YYYY_raw.csv` برای هر سال
- `05-Data/raw/_summary.md`

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-scraper.md`](../02-Prompts/prompt-scraper.md)
- [`03-Recipes/recipe-01-scrape-customs.md`](../03-Recipes/recipe-01-scrape-customs.md)

## 🔗 وابستگی‌ها
- [[task-00-setup]] ✅
- بلاک‌کننده [[task-02-scrape-detail]]
