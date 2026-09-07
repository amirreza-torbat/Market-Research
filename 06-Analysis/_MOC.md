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
├── by-tariff/
│   ├── _MOC.md
│   ├── _summary.md
│   ├── hs-XX-XXXX-XX-XX.md    # ۵۰+ یادداشت
│   └── charts/
│       └── hs-XX-XXXX-XX-XX-*.png
├── trend/                     # ⭐ تحلیل روند ۶ ساله (تمام HS × Country)
│   ├── _MOC.md
│   ├── _classification-summary.md
│   ├── strong-growth/         # یادداشت‌های HS Code با رشد قوی
│   ├── moderate-growth/
│   ├── emerging/
│   ├── declining/
│   └── charts/
└── export-candidates/         # ⭐ هدف نهایی — رتبه‌بندی کاندیدها
    ├── _MOC.md
    ├── _executive-ranking.md
    ├── rank-NN-hs-XX-XXXX-XX-XX.md  # ۵۰+ یادداشت تفصیلی
    ├── by-target-country.md
    ├── chapter-country-matrix.md
    └── charts/
```

## یادداشت‌های اصلی

| یادداشت | توضیح | وضعیت |
|---------|-------|-------|
| `executive-summary.md` | خلاصه اجرایی برای مدیران | ⬜ pending |
| `methodology.md` | روش‌شناسی کامل | ⬜ pending |
| `key-findings.md` | یافته‌های کلیدی | ⬜ pending |
| `by-country/_summary.md` | خلاصه تحلیل کشورها | ⬜ pending |
| `by-tariff/_summary.md` | خلاصه تحلیل تعرفه‌ها | ⬜ pending |
| **`trend/_classification-summary.md`** | **خلاصه طبقه‌بندی روند** | ⬜ pending |
| **`export-candidates/_executive-ranking.md`** | **گزارش اجرایی کاندیدها — مهم‌ترین خروجی** | ⬜ pending |
| **`export-candidates/by-target-country.md`** | **گزارش کشور-محور** | ⬜ pending |
| **`export-candidates/chapter-country-matrix.md`** | **ماتریس فصل × کشور** | ⬜ pending |

## مراحل تولید

| مرحله | نقش | تسک |
|-------|-----|-----|
| تحلیل کشور (۶ سال) | Analyst | [[task-04-analysis-country]] |
| تحلیل تعرفه (Top 50) | Analyst | [[task-05-analysis-tariff]] |
| **تحلیل جامع روند (تمام HS×Country)** | Analyst | [[task-10-trend-analysis]] |
| **طبقه‌بندی روند** | Analyst | [[task-11-trend-classification]] |
| **رتبه‌بندی کاندیدها** | Analyst | [[task-12-export-candidates]] |
| گزارش نهایی | Vault Writer | [[task-08-export-obsidian]] |

## مراجع
- [[task-04-analysis-country]]
- [[task-05-analysis-tariff]]
- [[task-10-trend-analysis]]
- [[task-11-trend-classification]]
- [[task-12-export-candidates]]
- [[task-08-export-obsidian]]
- [/03-Recipes/recipe-06-write-obsidian-notes](../03-Recipes/recipe-06-write-obsidian-notes.md)
- [/03-Recipes/recipe-09-trend-classification](../03-Recipes/recipe-09-trend-classification.md)
