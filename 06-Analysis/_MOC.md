---
folder: 06-Analysis
type: moc
last_updated: 1405-06-25
status: done
---

# 📈 MOC تحلیل‌ها (Analysis Map of Content)

> این MOC دروازه ورود به همه تحلیل‌های پروژه است. برای شروع مطالعه: [[executive-summary]] → [[key-findings]] → [[methodology]] → یادداشت‌های تفصیلی. ایندکس کامل درختی در [[_index]] است.

## ساختار

```
06-Analysis/
├── executive-summary.md       # 🌟 گزارش اجرایی نهایی (task-08)
├── methodology.md             # 🌟 روش‌شناسی کامل (task-08)
├── key-findings.md            # 🌟 یافته‌های کلیدی (task-08)
├── _MOC.md                    # این فایل
├── _index.md                  # 🌟 ایندکس درختی همه یادداشت‌ها (task-08)
├── by-country/
│   ├── _MOC.md                # فهرست تحلیل کشور-محور
│   └── (یادداشت‌های کشور از task-04 در دست ساخت نیست — تحلیل کشور-محور در export-candidates/by-target-country.md انجام شد)
├── by-tariff/
│   ├── _MOC.md                # فهرست تحلیل تعرفه-محور
│   └── (یادداشت‌های تعرفه از task-05 در دست ساخت نیست — تحلیل تعرفه-محور در trend/ و export-candidates/ انجام شد)
├── trend/                     # ⭐ تحلیل جامع روند (تمام HS × Country)
│   ├── _MOC.md                # فهرست ۱۰۸ یادداشت
│   ├── _classification-summary.md
│   ├── strong-growth/         # ۳۰ یادداشت
│   ├── moderate-growth/       # ۱۸ یادداشت
│   ├── emerging/              # ۳۰ یادداشت
│   ├── declining/             # ۳۰ یادداشت
│   └── charts/                # ۱۰۲ نمودار PNG
└── export-candidates/         # ⭐ هدف نهایی — رتبه‌بندی کاندیدها
    ├── _MOC.md
    ├── _executive-ranking.md  # گزارش اجرایی Top 50 (بازکالیبره‌شده)
    ├── rank-NN-hs-*.md        # ۵۰ یادداشت تفصیلی
    ├── by-target-country.md
    ├── chapter-country-matrix.md
    └── charts/                # ۵۲ نمودار PNG
```

## یادداشت‌های اصلی

| یادداشت | توضیح | وضعیت |
|---------|-------|-------|
| `executive-summary.md` | 🌟 خلاصه اجرایی نهایی (۷ بخش: زمینه، روش، آمار، یافته‌ها، محدودیت‌ها، توصیه‌ها، خروجی‌ها) | 🟢 done |
| `methodology.md` | 🌟 روش‌شناسی کامل (۹ بخش: منبع، مدل داده، شاخص‌ها، تاکسونومی، نمره‌دهی، membership، صدک، دقت، محدودیت‌ها) | 🟢 done |
| `key-findings.md` | 🌟 پنج یافته کلیدی با تحلیل عمیق و backlink | 🟢 done |
| `_index.md` | 🌟 ایندکس درختی همه یادداشت‌ها و گزارش‌ها | 🟢 done |
| `trend/_classification-summary.md` | خلاصه طبقه‌بندی روند ۵۰,۱۹۶ جفت (task-11) | 🟠 review |
| `export-candidates/_executive-ranking.md` | گزارش اجرایی کاندیدها — مهم‌ترین خروجی تحلیلی (بازکالیبره‌شده) | 🟠 review |
| `export-candidates/by-target-country.md` | گزارش کشور-محور (۱۰۵ کشور با جفت رشد) | 🟠 review |
| `export-candidates/chapter-country-matrix.md` | ماتریس فصل × کشور + heatmap | 🟠 review |

## مسیر مطالعه پیشنهادی

1. **تصمیم‌گیر یا مدیر**: [[executive-summary]] → [[export-candidates/_executive-ranking]] → [[key-findings]]
2. **تحلیل‌گر یا reviewer فنی**: [[methodology]] → [[trend/_classification-summary]] → [[../04-State/qa-report]]
3. **برنامه‌ریز بازار**: [[export-candidates/by-target-country]] → [[export-candidates/chapter-country-matrix]] → یادداشت‌های rank-*

## مراحل تولید

| مرحله | نقش | تسک | وضعیت |
|-------|-----|-----|-------|
| تحلیل کشور (۶ سال) | Analyst | [[task-04-analysis-country]] | ⬜ pending (جایگزین شد با task-10/12) |
| تحلیل تعرفه (Top 50) | Analyst | [[task-05-analysis-tariff]] | ⬜ pending (جایگزین شد با task-10/12) |
| **تحلیل جامع روند (تمام HS×Country)** | Analyst | [[task-10-trend-analysis]] | 🟠 review |
| **طبقه‌بندی روند** | Analyst | [[task-11-trend-classification]] | 🟠 review |
| **رتبه‌بندی کاندیدها** | Analyst | [[task-12-export-candidates]] | 🟠 review |
| گزارش نهایی Obsidian | Vault Writer | [[task-08-export-obsidian]] | 🟡 in-progress → review |

## مراجع

- [[_index]] — ایندکس کامل درختی
- [[executive-summary]] | [[methodology]] | [[key-findings]]
- [[task-04-analysis-country]] | [[task-05-analysis-tariff]] | [[task-10-trend-analysis]] | [[task-11-trend-classification]] | [[task-12-export-candidates]] | [[task-08-export-obsidian]]
- [/03-Recipes/recipe-06-write-obsidian-notes](../03-Recipes/recipe-06-write-obsidian-notes.md)
- [/03-Recipes/recipe-09-trend-classification](../03-Recipes/recipe-09-trend-classification.md)
- [/05-Data/processed/trend-analysis-summary](../05-Data/processed/trend-analysis-summary.md)
