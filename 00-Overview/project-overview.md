---
folder: 00-Overview
type: overview
last_updated: 1405-06-15
---

# 📌 معرفی پروژه (Project Overview)

## چیستی پروژه

این پروژه با هدف **استخراج، نرمال‌سازی و تحلیل آمار صادرات ایران** در بازه ۵ ساله (۱۴۰۰ تا ۱۴۰۴ شمسی) از پایگاه داده گمرک جمهوری اسلامی ایران انجام می‌شود. خروجی نهایی شامل:

- گزارش‌های تحلیلی به فرمت Obsidian (این مخزن)
- فایل‌های Excel با داده‌های ساختاریافته
- شناسایی کشورهای با روند افزایشی صادرات
- شناسایی الگوی افزایش هر **کد تعرفه (HS Code)** به تفکیک کشور مقصد

## چرا Obsidian؟

Obsidian به ما اجازه می‌دهد:
- یادداشت‌های تحلیلی را به‌صورت **گرافی از یادداشت‌های کوچک** بسازیم.
- با **backlinks** (`[[...]]`) ارتباط بین داده‌ها، تحلیل‌ها و گزارش‌ها را حفظ کنیم.
- هر agent بتواند با خواندن یک یادداشت، مسیر دسترسی به یادداشت‌های مرتبط را پیدا کند.
- تغییرات در طول زمان با git قابل پیگیری باشد.

## چرا GitHub؟

- نسخه‌بندی کامل از همه تغییرات
- همکاری هم‌زمان چند agent
- دسترسی به تاریخچه تصمیمات (decisions log)
- احتمالاً CI/CD برای اعتبارسنجی داده‌ها

## محدوده پروژه (Scope)

### در محدوده (In-scope)
- آمار صادرات ایران (نه واردات)
- بازه زمانی ۱۴۰۰ تا ۱۴۰۴ (۵ سال)
- تمامی کدهای تعرفه (HS 2-digit تا 8-digit در صورت دسترسی)
- تمام کشورهای مقصد
- ارزش دلاری + وزن کیلوگرمی

### خارج از محدوده (Out-of-scope)
- واردات
- آمار سال ۱۴۰۵ (سال جاری، هنوز کامل نشده)
- ترانزیت
- صادرات خدمات

## معیار پذیرش (Acceptance Criteria)

پروژه وقتی تمام‌شده محسوب می‌شود که:

1. ✅ داده‌های خام هر ۵ سال در `05-Data/raw/` ذخیره شده باشد.
2. ✅ داده‌های نرمال‌شده در `05-Data/processed/` به فرمت Parquet/CSV باشد.
3. ✅ تحلیل "افزایش به کشور" در `06-Analysis/by-country/` باشد.
4. ✅ تحلیل "افزایش به تفکیک تعرفه" در `06-Analysis/by-tariff/` باشد.
5. ✅ فایل Excel نهایی در `07-Exports/` قرار گرفته باشد.
6. ✅ خطای محاسباتی کل < 0.0001٪ باشد (با گزارش QA).
7. ✅ همه چیز commit و push شده باشد.

## نقش‌های agent

| نقش | توضیح | فایل پرامپت |
|-----|--------|--------------|
| Scraper | استخراج داده از سایت گمرک | [`02-Prompts/prompt-scraper.md`](../02-Prompts/prompt-scraper.md) |
| ETL Engineer | نرمال‌سازی، پاکسازی، ساخت مدل داده | [`02-Prompts/prompt-etl-engineer.md`](../02-Prompts/prompt-etl-engineer.md) |
| Analyst | تحلیل روند کشور/تعرفه | [`02-Prompts/prompt-analyst.md`](../02-Prompts/prompt-analyst.md) |
| QA Validator | اعتبارسنجی دقت و کامل‌بودن | [`02-Prompts/prompt-qa-validator.md`](../02-Prompts/prompt-qa-validator.md) |
| Vault Writer | تبدیل تحلیل به یادداشت‌های Obsidian | [`02-Prompts/prompt-vault-writer.md`](../02-Prompts/prompt-vault-writer.md) |
| Git Publisher | commit, push, release | [`02-Prompts/prompt-git-publisher.md`](../02-Prompts/prompt-git-publisher.md) |

## پیش‌نیازها

- Python 3.11+ با پکیج‌های: `pandas`, `pyarrow`, `httpx`, `beautifulsoup4`, `openpyxl`, `decimal`
- git و دسترسی push به مخزن
- obsidian.md (اختیاری برای مشاهده محلی)
- دسترسی به سایت گمرک (در صورت فیلتر بودن، از پروکسی استفاده شود)

## مراجع

- [[conventions]]
- [[data-sources]]
- [[glossary]]
- [/01-Tasks/_MOC](../01-Tasks/_MOC.md)
- [/04-State/STATUS](../04-State/STATUS.md)
