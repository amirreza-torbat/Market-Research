---
folder: 03-Recipes
type: recipe
recipe_id: recipe-08
title: به‌روزرسانی وضعیت (state)
related_tasks: [all]
last_updated: 1405-06-15
---

# 📖 Recipe-08 — به‌روزرسانی وضعیت (State)

> **نقش**: همه agentها
> **هدف**: هر agent هر بار که کاری انجام می‌دهد، باید state را به‌روز کند.

## چرا مهم است؟
این مکانیسم به همه agentها (و انسان‌ها) اجازه می‌دهد بدانند:
- کجای مسیر هستیم.
- چه کسی روی چه چیزی کار می‌کند.
- چه مسائلی باز است.
- چه تصمیماتی گرفته شده.

## فایل‌های state

| فایل | محتوا | فرکانس به‌روزرسانی |
|------|-------|---------------------|
| `04-State/STATUS.md` | وضعیت کلی و تسک فعلی | هر بار تغییر وضعیت |
| `04-State/progress.md` | لاگ پیشرفت | هر مایل‌ستون |
| `04-State/issues.md` | مسائل باز | هر بار issue جدید |
| `04-State/decisions.md` | تصمیمات | هر بار تصمیم جدید |
| `04-State/qa-report.md` | گزارش QA | در task-06 |

## قواعد

### ۱. STATUS.md
هر بار که تسکی شروع، تمام یا تغییر وضعیت داد، این فایل به‌روز شود.

```markdown
# وضعیت پروژه

**آخرین به‌روزرسانی**: 1405-06-15 14:30
**وضعیت کلی**: in-progress
**تسک فعلی**: task-04 (by-country analysis)
**agent مسئول**: analyst

## وضعیت تسک‌ها
| Task ID | Status | Assignee | Updated |
|---------|--------|----------|---------|
| task-00 | done | vault-writer | 1405-06-15 |
| task-01 | done | scraper | 1405-06-15 |
| task-02 | done | scraper | 1405-06-15 |
| task-03 | done | etl-engineer | 1405-06-15 |
| task-04 | in-progress | analyst | 1405-06-15 |
| task-05 | pending | - | - |
| task-06 | pending | - | - |
| task-07 | pending | - | - |
| task-08 | pending | - | - |
| task-09 | pending | - | - |
```

### ۲. progress.md
هر مایل‌ستون یک سطر اضافه شود. فرمت:

```markdown
# لاگ پیشرفت

## [1405-06-15 14:30] task-04 — analyst
- شروع تحلیل by-country.
- load Parquet با موفقیت.
- 195 کشور شناسایی شد.

## [1405-06-15 15:00] task-04 — analyst
- محاسبه CAGR برای همه کشورها.
- Top 20 بر اساس absolute_change استخراج شد.

## [1405-06-15 15:30] task-04 — analyst
- ساخت نمودار برای ۲۰ کشور top.
- ۲۰ نمودار PNG در 06-Analysis/by-country/charts/ ذخیره شد.
```

### ۳. issues.md
هر بار issue جدید:

```markdown
# مسائل باز

## Issue-001 — [1405-06-15] task-01
**عنوان**: Captcha در صفحه ۴۵ سال ۱۴۰۲ ظاهر شد.
**وضعیت**: blocked
**توضیح**: هنگام scrape سال ۱۴۰۲ صفحه ۴۵ captcha نشان داد.
**اقدام**: نیاز به حل دستی یا OCR.
**assignee**: scraper

## Issue-002 — [1405-06-15] task-03
**عنوان**: نام "کره" در داده - ابهام KP vs KR.
**وضعیت**: open
**توضیح**: در داده خام، "کره" بدون مشخص شدن شمالی یا جنوبی آمده.
**اقدام**: بررسی متن و کشورهای همسایه. ۹۵٪ موارد KR (جنوبی) است.
**assignee**: etl-engineer
```

### ۴. decisions.md
هر بار تصمیم مهم:

```markdown
# تصمیمات پروژه

## Decision-001 — [1405-06-15] data-source
**عنوان**: انتخاب URL پایه گمرک.
**تصمیم**: https://tsd.irica.ir/ به‌عنوان منبع اصلی.
**دلیل**: پایگاه رسمی آمار تجارت خارجی ایران است.
**تصمیم‌گیرنده**: user
**تأثیر**: همه scraping بر این اساس.

## Decision-002 — [1405-06-15] precision
**عنوان**: استاندارد دقت عددی.
**تصمیم**: تلورانس < 0.0001٪ با Decimal.
**دلیل**: اطمینان از صحت محاسبات مالی.
**تصمیم‌گیرنده**: user
```

## مراحل به‌روزرسانی

### قبل از شروع کار:
1. `STATUS.md` را بخوان.
2. تسک خودت را به `in-progress` تغییر بده.
3. در `progress.md` یک سطر "شروع" اضافه کن.

### حین کار:
1. هر مایل‌ستون، در `progress.md` یک سطر اضافه کن.
2. اگر issue یافتی، در `issues.md` ثبت کن.
3. اگر تصمیمی گرفتی، در `decisions.md` ثبت کن.

### بعد از پایان:
1. در `progress.md` یک سطر "پایان" با خلاصه.
2. در `STATUS.md` تسک را به `review` یا `done` تغییر بده.
3. commit و push.

## قالب سطر progress

```
## [YYYY-MM-DD HH:MM] task-NN — role
- اقدام ۱.
- اقدام ۲.
- نتیجه.
```

## قالب issue

```
## Issue-NNN — [YYYY-MM-DD] task-NN
**عنوان**: ...
**وضعیت**: open|in-progress|resolved|blocked
**توضیح**: ...
**اقدام**: ...
**assignee**: role
```

## قالب decision

```
## Decision-NNN — [YYYY-MM-DD] topic
**عنوان**: ...
**تصمیم**: ...
**دلیل**: ...
**تصمیم‌گیرنده**: user|role
**تأثیر**: ...
```

## مراجع
- [/04-State/STATUS](../04-State/STATUS.md)
- [/04-State/progress](../04-State/progress.md)
- [/04-State/issues](../04-State/issues.md)
- [/04-State/decisions](../04-State/decisions.md)
