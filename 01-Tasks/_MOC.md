---
folder: 01-Tasks
type: moc
last_updated: 1405-06-15
---

# 🗺️ MOC تسک‌ها (Tasks Map of Content)

این فایل فهرست اصلی همه تسک‌های پروژه است. هر agent قبل از انتخاب کار، این فایل را چک کند.

---

## نمودار وابستگی

```
[task-00: setup] ✅
       ↓
[task-01: scrape-list] ⬜
       ↓
[task-02: scrape-detail] ⬜
       ↓
[task-03: etl-normalize] ⬜
       ↓
   ┌────────────┴────────────┐
   ↓                          ↓
[task-04: by-country]    [task-05: by-tariff]
   ↓                          ↓
   └────────────┬─────────────┘
                ↓
       [task-06: qa-validate]
                ↓
   ┌────────────┴────────────┐
   ↓                          ↓
[task-07: export-excel]  [task-08: export-obsidian]
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
| `task-01` | استخراج فهرست صادرات (۵ سال) | ⬜ pending | [task-01-scrape-list.md](task-01-scrape-list.md) | `task-00` | Scraper |
| `task-02` | استخراج جزئیات هر رکورد | ⬜ pending | [task-02-scrape-detail.md](task-02-scrape-detail.md) | `task-01` | Scraper |
| `task-03` | نرمال‌سازی و ETL | ⬜ pending | [task-03-etl-normalize.md](task-03-etl-normalize.md) | `task-02` | ETL Engineer |
| `task-04` | تحلیل به تفکیک کشور | ⬜ pending | [task-04-analysis-country.md](task-04-analysis-country.md) | `task-03` | Analyst |
| `task-05` | تحلیل به تفکیک تعرفه | ⬜ pending | [task-05-analysis-tariff.md](task-05-analysis-tariff.md) | `task-03` | Analyst |
| `task-06` | اعتبارسنجی دقت < 0.0001٪ | ⬜ pending | [task-06-qa-validate.md](task-06-qa-validate.md) | `task-04,05` | QA Validator |
| `task-07` | خروجی Excel | ⬜ pending | [task-07-export-excel.md](task-07-export-excel.md) | `task-06` | ETL Engineer |
| `task-08` | خروجی Obsidian notes | ⬜ pending | [task-08-export-obsidian.md](task-08-export-obsidian.md) | `task-06` | Vault Writer |
| `task-09` | انتشار در GitHub | ⬜ pending | [task-09-publish-github.md](task-09-publish-github.md) | `task-07,08` | Git Publisher |

**راهنمای وضعیت**: `pending` → `in-progress` → `review` → `done` | `blocked`

---

## تسک‌های موازی

تسک‌های ۴ و ۵ می‌توانند به‌صورت **موازی** اجرا شوند (هر دو وابسته فقط به `task-03` هستند).
تسک‌های ۷ و ۸ نیز موازی هستند.

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
