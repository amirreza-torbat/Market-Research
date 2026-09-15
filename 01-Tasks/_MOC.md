---
folder: 01-Tasks
type: moc
last_updated: 1405-06-25
---

# 🗺️ MOC تسک‌ها (Tasks Map of Content)

این فایل فهرست اصلی همه تسک‌های پروژه است. هر agent قبل از انتخاب کار، این فایل را چک کند.

---

## نمودار وابستگی

```
[task-00: setup] ✅
       ↓
[task-01/02: scrape 6y] ✅ DONE (626,395 records)
       ↓
[task-03: etl-normalize 6y] 🟠 review (Parquet ready)
       ↓
   ┌────────────┴────────────────────────┐
   ↓                                       ↓
[task-04: by-country 6y]            [task-05: by-tariff Top50]
   ↓                                       ↓
   └────────────┬──────────────────────────┘
                ↓
       [task-10: trend-analysis ALL HS×Country]  🟠 review
                ↓
       [task-11: trend-classification]  🟠 review
                ↓
       [task-12: export-candidates ranking]
                ↓
       [task-06: qa-validate]  🟠 review — ۴۹/۴۹ PASS (1405-06-23)
                ↓
   ┌────────────┴────────────┐
   ↓                          ↓
[task-07: export-excel]  🟠 review (18-sheet Excel, 12.58 MB) | [task-08: export-obsidian]  🟠 review (3 گزارش نهایی + _index + 5 MOC)
   ↓                          ↓
   └────────────┬─────────────┘
                ↓
       [task-09: publish-github]
```

---

## فهرست تسک‌ها

| Task ID | عنوان | وضعیت | فایل | وابسته به | نقش agent |
|---------|-------|-------|------|-----------|-----------|
| `task-00` | راه‌اندازی Vault و قراردادها | ✅ done | [task-00-setup.md](task-00-setup.md) | — | Vault Writer |
| `task-01` | استخراج فهرست صادرات (۶ سال) | ✅ done | [task-01-scrape-list.md](task-01-scrape-list.md) | `task-00` | Scraper |
| `task-02` | استخراج جزئیات هر رکورد | ✅ done | [task-02-scrape-detail.md](task-02-scrape-detail.md) | `task-01` | Scraper |
| `task-03` | نرمال‌سازی و ETL (۶ سال) | 🟠 review | [task-03-etl-normalize.md](task-03-etl-normalize.md) | `task-02` | ETL Engineer |
| `task-04` | تحلیل به تفکیک کشور (۶ سال) | ⬜ pending | [task-04-analysis-country.md](task-04-analysis-country.md) | `task-03` | Analyst |
| `task-05` | تحلیل به تفکیک تعرفه (Top 50) | ⬜ pending | [task-05-analysis-tariff.md](task-05-analysis-tariff.md) | `task-03` | Analyst |
| **`task-10`** | **تحلیل جامع روند (تمام HS × تمام کشورها)** | 🟠 review | [task-10-trend-analysis.md](task-10-trend-analysis.md) | `task-03`, `task-04`, `task-05` | Analyst |
| **`task-11`** | **طبقه‌بندی روند + اعتبارسنجی آماری** | 🟠 review | [task-11-trend-classification.md](task-11-trend-classification.md) | `task-10` | Analyst |
| **`task-12`** | **رتبه‌بندی کاندیدهای صادرات** | 🟠 review | [task-12-export-candidates.md](task-12-export-candidates.md) | `task-11` | Analyst |
| `task-06` | اعتبارسنجی دقت < 0.0001٪ | 🟠 review | [task-06-qa-validate.md](task-06-qa-validate.md) | `task-10,11,12` | QA Validator |
| `task-07` | خروجی Excel (۱۸ شیت) | 🟠 review | [task-07-export-excel.md](task-07-export-excel.md) | `task-06` | ETL Engineer |
| `task-08` | خروجی Obsidian notes | 🟠 review | [task-08-export-obsidian.md](task-08-export-obsidian.md) | `task-06` | Vault Writer |
| `task-09` | انتشار در GitHub | ⬜ pending | [task-09-publish-github.md](task-09-publish-github.md) | `task-07,08` | Git Publisher |

**راهنمای وضعیت**: `pending` → `in-progress` → `review` → `done` | `blocked`

---

## تسک‌های موازی

تسک‌های ۴ و ۵ می‌توانند به‌صورت **موازی** اجرا شوند (هر دو وابسته فقط به `task-03` هستند).
تسک‌های ۷ و ۸ نیز موازی هستند.

---

## توالی تسک‌های ۱۰، ۱۱، ۱۲ (تحلیل روند)

این سه تسک **قلب اصلی** پروژه‌اند:
- `task-10`: محاسبه شاخص‌های روند برای **تمام** جفت‌های (HS × Country) در ۶ سال.
- `task-11`: طبقه‌بندی هر جفت به یکی از ۷ دسته (strong_growth, moderate_growth, stable, volatile, declining, emerging, disappearing).
- `task-12`: رتبه‌بندی محصولات کاندید صادرات با نمره ترکیبی (CAGR + slope + حجم + تنوع + ثبات - نوسان).

این تسک‌ها به‌صورت سری اجرا می‌شوند (هر کدام به قبلی وابسته‌است).

---

## چگونه یک تسک را شروع کنیم؟

1. فایل تسک را در این پوشه باز کن.
2. بخش «پذیرش» (Acceptance) را بخوان.
3. پرامپت مرتبط در `02-Prompts/` را مطالعه کن.
4. در `04-State/STATUS.md` تسک را به `in-progress` تغییر بده و نام خودت را ثبت کن.
5. شاخه `feature/task-NN-slug` بساز.
6. کار را انجام بده و هر مایل‌ستون را در `04-State/progress.md` ثبت کن.
7. PR بساز و برای review آماده کن.

---

## چگونه یک تسک را تمام کنیم؟

1. معیارهای پذیرش در فایل تسک بررسی شوند.
2. در `04-State/progress.md` یک سطر final ثبت شود.
3. در همین `_MOC.md` وضعیت تسک به `done` تغییر کند.
4. PR در `main` merge شود.
5. اگر تسک‌های وابسته وجود دارد، در `STATUS.md` به `unblocked` تغییر کنند.

---

## مراجع

- [/02-Prompts/_MOC](../02-Prompts/_MOC.md)
- [/03-Recipes/_MOC](../03-Recipes/_MOC.md)
- [/04-State/STATUS](../04-State/STATUS.md)
- [/00-Overview/project-overview](../00-Overview/project-overview.md)
- [/00-Overview/conventions](../00-Overview/conventions.md) — بخش ۵ (تاکسونومی روند) و ۵.۳ (نمره‌دهی)
