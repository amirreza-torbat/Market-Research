---
folder: 07-Exports
type: moc
last_updated: 1405-06-24
---

# 📤 MOC خروجی‌ها (Exports)

> این پوشه شامل خروجی‌های نهایی برای مصرف کاربر است.

## فایل‌ها

| فایل | توضیح | تسک |
|------|-------|-----|
| `iran-export-candidates-500.xlsx` | ✅ **ساخته شد** (۱۴۰۵-۰۶-۲۳) — Excel کاندیدهای صادرات با آستانه‌های صدکی؛ ۷ شیت: All-Candidates (۵۷۴) / Top-500 / Select (۵۸) / Monitor (۱۷۲) / By-Chapter / By-Target-Country / Methodology | [[task-12-export-candidates]] |
| `iran-exports-1400-1405-20260914.xlsx` | ✅ **ساخته شد** (۱۴۰۵-۰۶-۲۴) — فایل Excel جامع نهایی با **۱۸ شیت** شامل داده کامل، تحلیل کشور/تعرفه/روند/طبقه‌بندی/کاندیدها و نمودارها. حجم: ۱۲.۵۸ MB. | [[task-07-export-excel]] |
| `release-notes.md` | یادداشت‌های release GitHub | [[task-09-publish-github]] |

## شیت‌های Excel نهایی (task-07 — ۱۸ شیت)

| # | شیت | محتوا | تعداد رکورد |
|---|-----|-------|--------------|
| 1 | `01-Overview` | معرفی پروژه + آمار کلی + وضعیت QA | (متن) |
| 2 | `02-Data-All` | نمونه ۱۰۰۰ رکورد از Parquet اصلی | ۱٬۰۰۰ |
| 3 | `03-By-Country-Summary` | تحلیل همه کشورها | ۱۶۶ |
| 4 | `04-By-Country-Top20-Growth` | Top 20 کشور با بیشترین رشد مطلق | ۲۰ |
| 5 | `05-By-Country-Top20-CAGR` | Top 20 کشور با بیشترین CAGR | ۲۰ |
| 6 | `06-By-Tariff-Summary` | تحلیل همه HS Codeها | ۹٬۸۵۴ |
| 7 | `07-By-Tariff-Top50` | Top 50 HS Code بر اساس مجموع ۵ سال | ۵۰ |
| 8 | `08-By-Tariff-Country` | جدول HS × Country (فقط رشد قوی/متوسط/نوظهور) | ۲٬۰۴۶ |
| 9 | `09-Trend-All-HS-Country` | جدول master trend | ۵۰٬۱۹۶ |
| 10 | `10-Trend-Classification` | طبقه‌بندی همه جفت‌ها | ۵۰٬۱۹۶ |
| 11 | `11-Trend-By-HS-Summary` | تجمیع به ازای هر HS Code | ۵٬۹۹۳ |
| 12 | `12-Export-Candidates-Ranked` | همه کاندیدها با نمره | ۵۷۴ |
| 13 | `13-Candidates-Top20-Detail` | Top 20 با ۳۴ ستون جزئیات | ۲۰ |
| 14 | `14-Chapter-Country-Matrix` | ماتریس فصل HS × ۳۰ کشور برتر | ~۵۰ |
| 15 | `15-Charts-Country` | BarChart Top 20 کشور | ۲۰ |
| 16 | `16-Charts-Tariff` | BarChart Top 20 HS Code | ۲۰ |
| 17 | `17-Charts-Trend-Classification` | PieChart توزیع دسته‌ها | ۱۰ |
| 18 | `18-Charts-Export-Candidates` | BarChart Top 20 کاندید | ۲۰ |

**ویژگی‌های فایل:**
- Header: bold، رنگ #1F4E78، رنگ متن سفید.
- AutoFilter و Freeze Panes روی همه شیت‌های داده.
- Conditional formatting روی ستون‌های CAGR (شیت ۳) و export_score (شیت ۱۲).
- Number format: `#,##0` برای ارزش‌ها، `0.00%` برای CAGR/نسبت‌ها.
- ۴ نمودار داخلی Excel (BarChart × ۳، PieChart × ۱).
- حجم: ۱۲.۵۸ MB (زیر limit 50 MB).

## مراجع
- [[task-07-export-excel]]
- [[task-09-publish-github]]
- [[recipe-05-export-excel]]
- [[recipe-07-publish-github]]
