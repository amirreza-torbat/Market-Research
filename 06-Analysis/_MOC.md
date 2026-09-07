---
folder: 06-Analysis
type: moc
last_updated: 1405-06-15
---

# 📈 MOC تحلیل‌ها (Analysis Map of Content)

## ساختار

```
06-Analysis/
├── executive-summary.md       # گزارش اجرایی نهایی
├── methodology.md             # روش‌شناسی
├── key-findings.md            # یافته‌های کلیدی
├── _MOC.md                    # این فایل
├── _index.md                  # ایندکس درختی
├── by-country/
│   ├── _MOC.md
│   ├── _summary.md
│   ├── country-XX-trend.md    # ۴۰+ یادداشت
│   └── charts/
│       └── country-XX-trend.png
└── by-tariff/
    ├── _MOC.md
    ├── _summary.md
    ├── hs-XX-XXXX-XX-XX.md    # ۵۰+ یادداشت
    └── charts/
        └── hs-XX-XXXX-XX-XX-*.png
```

## یادداشت‌های اصلی

| یادداشت | توضیح | وضعیت |
|---------|-------|-------|
| `executive-summary.md` | خلاصه اجرایی برای مدیران | ⬜ pending |
| `methodology.md` | روش‌شناسی کامل | ⬜ pending |
| `key-findings.md` | یافته‌های کلیدی | ⬜ pending |
| `by-country/_summary.md` | خلاصه تحلیل کشورها | ⬜ pending |
| `by-tariff/_summary.md` | خلاصه تحلیل تعرفه‌ها | ⬜ pending |

## مراحل تولید

| مرحله | نقش | تسک |
|-------|-----|-----|
| تحلیل کشور | Analyst | [[task-04-analysis-country]] |
| تحلیل تعرفه | Analyst | [[task-05-analysis-tariff]] |
| گزارش نهایی | Vault Writer | [[task-08-export-obsidian]] |

## مراجع
- [[task-04-analysis-country]]
- [[task-05-analysis-tariff]]
- [[task-08-export-obsidian]]
- [/03-Recipes/recipe-06-write-obsidian-notes](../03-Recipes/recipe-06-write-obsidian-notes.md)
