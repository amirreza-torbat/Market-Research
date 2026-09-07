---
folder: 03-Recipes
type: recipe
recipe_id: recipe-01
title: استخراج داده از گمرک (۶ سال)
related_tasks: [task-01, task-02]
last_updated: 1405-06-15
---

# 📖 Recipe-01 — استخراج داده از گمرک (۶ سال)

> **نقش**: Scraper Agent
> **تسک‌های مرتبط**: [[task-01-scrape-list]], [[task-02-scrape-detail]]
> **زمان تخمینی**: ۳-۴ روز برای ۶ سال (۱۴۰۰ تا ۱۴۰۵)

## هدف
استخراج کامل داده‌های صادرات ایران از سایت گمرک برای ۶ سال گذشته. سال ۱۴۰۵ (سال جاری) به‌صورت partial استخراج می‌شود.

## پیش‌نیازها
- [ ] Python 3.11+ نصب باشد.
- [ ] پکیج‌ها: `httpx`, `beautifulsoup4`, `lxml`, `pandas`.
- [ ] دسترسی به اینترنت (با پروکسی در صورت نیاز).
- [ ] مطالعه [`00-Overview/data-sources.md`](../00-Overview/data-sources.md).
- [ ] URL نهایی توسط کاربر در `04-State/decisions.md` تأیید شده باشد.

## مراحل

### مرحله ۱: کشف ساختار سایت (۲ ساعت)
1. بازدید دستی از سایت با مرورگر.
2. روشن کردن DevTools → Network.
3. فیلتر year=1404 و country=all را اعمال کن.
4. درخواست‌های XHR/Fetch را بررسی کن.
5. ساختار pagination را شناسایی کن (page param یا cursor؟).
6. در `04-State/decisions.md` یادداشت کن:
   - URL پایه.
   - روش (GET/POST).
   - پارامترهای کلیدی.
   - چالش‌ها (captcha, session, ...).

**✅ Verification**: می‌توانی یک درخواست نمونه با `curl` اجرا کنی و پاسخ معتبر بگیری.

### مرحله ۲: ساخت Scraper Skeleton (۲ ساعت)
1. شاخه `feature/task-01-scrape` بساز.
2. در `scripts/scrape_customs.py`:
   - کلاس `CustomsScraper` (طبق پرامپت Scraper).
   - متد `fetch_page(page_num)`.
   - متد `parse_page(html)`.
   - متد `scrape_year(year)`.
3. تست با ۱ صفحه: scraping، ذخیره خام، parse.

**✅ Verification**: `python scripts/scrape_customs.py --year 1404 --page 1` کار کند.

### مرحله ۳: اجرای استخراج برای سال ۱۴۰۴ (نمونه) (۳ ساعت)
1. اجرای scraper برای سال ۱۴۰۴.
2. ذخیره HTML در `05-Data/raw/1404/page-NNNN.html`.
3. ذخیره CSV موقت در `05-Data/interim/exports_1404_raw.csv`.
4. لاگ هر ۱۰۰ رکورد در `04-State/progress.md`.
5. در صورت خطا، در `04-State/issues.md` ثبت کن و retry.

**✅ Verification**:
- تعداد رکوردها > 100,000.
- نرخ موفقیت > 99٪.
- هیچ صفحه‌ای fail نشده باشد (یا retry موفق شده باشد).

### مرحله ۴: اجرای استخراج برای بقیه سال‌های کامل (۸ ساعت)
1. برای سال‌های ۱۴۰۰ تا ۱۴۰۳ تکرار کن.
2. هر سال به‌صورت جداگانه اجرا و validate کن.

**✅ Verification**: همه ۵ سال کامل (۱۴۰۰ تا ۱۴۰۴) استخراج شده باشند.

### مرحله ۴.۵: استخراج سال جاری ۱۴۰۵ (partial) (۲ ساعت)
1. اجرای scraper برای سال ۱۴۰۵.
2. **مهم**: فقط ماه‌های موجود در سایت استخراج شود (معمولاً تا ۱ یا ۲ ماه قبل از ماه جاری).
3. در `05-Data/raw/_summary.md` فیلد `months_available_1405` ثبت شود (مثلاً `6` اگر ۶ ماه موجود است).
4. ذخیره CSV موقت در `05-Data/interim/exports_1405_raw.csv`.
5. لاگ: تعداد ماه‌های استخراج‌شده در `04-State/progress.md`.

**✅ Verification**:
- سال ۱۴۰۵ استخراج شده باشد.
- `months_available_1405` در summary ثبت شده باشد.
- تعداد رکوردها متناسب با تعداد ماه‌ها باشد.

### مرحله ۵: تولید گزارش خلاصه (۱ ساعت)
1. در `05-Data/raw/_summary.md`:
   - تعداد رکوردها برای هر سال (۱۴۰۰ تا ۱۴۰۵).
   - تعداد کشورها برای هر سال.
   - تعداد HS Codeها برای هر سال.
   - مجموع ارزش صادرات برای هر سال.
   - **`months_available_1405`**: تعداد ماه‌های موجود سال ۱۴۰۵.
   - مسائل باز.

**✅ Verification**: گزارش خوانا و قابل فهم باشد.

### مرحله ۶: commit و PR (۳۰ دقیقه)
1. در `04-State/STATUS.md`، `task-01` را به `review` تغییر بده.
2. در `04-State/progress.md` سطر نهایی ثبت کن.
3. commit با پیام `feat(scraper): task-01 extract export list 1400-1405`.
4. push شاخه.
5. PR بساز.

**✅ Verification**: PR ایجاد شده و قابل review است.

## مدیریت خطا (Rollback)

### اگر scraper در وسط کار شکست:
- داده‌های ذخیره‌شده در `05-Data/raw/` حفظ می‌شوند (idempotent).
- با `--resume-from-page N` از صفحه‌ای که شکست خورده ادامه بده.

### اگر captcha ظاهر شد:
- در `04-State/issues.md` ثبت کن.
- scraper را متوقف کن.
- یا captcha به‌صورت manual حل شود، یا از سرویس OCR استفاده شود.

### اگر سایت تغییر کرد:
- structure change را در `04-State/issues.md` ثبت کن.
- scraper را به‌روز کن.
- صفحه‌های قبلی را re-scrape کن.

## نکات مهم

- ⚠️ **هیچ پردازشی روی داده خام انجام نده**. HTML دقیقاً همان چیزی که دریافت شده ذخیره شود.
- ⚠️ **تأخیر اخلاقی**: حداقل ۲ ثانیه بین درخواست‌ها.
- ⚠️ **User-Agent**: از یک UA واقعی استفاده کن (نه default httpx).
- ⚠️ **Encoding**: حتماً UTF-8 بررسی شود.

## مراجع
- [[task-01-scrape-list]]
- [[prompt-scraper]]
- [[data-sources]]
- [[conventions]]
