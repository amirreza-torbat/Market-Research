---
folder: 06-Analysis/export-candidates
type: moc
last_updated: 1405-06-15
status: pending
---

# 🎯 MOC کاندیدهای صادرات (Export Candidates)

> این پوشه پس از تکمیل [[task-12-export-candidates]] پر می‌شود. این **هدف نهایی** پروژه است.

## ساختار مورد انتظار

- `_executive-ranking.md` — گزارش اجرایی با Top 20 کاندید
- `rank-NN-hs-XX-XXXX-XX-XX.md` — یادداشت تفصیلی برای هر کاندید (۵۰ یادداشت)
- `by-target-country.md` — گزارش کشور-محور
- `chapter-country-matrix.md` — ماتریس فصل × کشور با heatmap
- `charts/` — نمودارهای Top 20 و heatmap

## فهرست یادداشت‌ها (پس از تکمیل)

> ⬜ هنوز هیچ یادداشتی ساخته نشده.

## نمره‌دهی export_score

برای جزئیات، به [[conventions]] بخش ۵.۳ مراجعه کنید:

```
export_score = 0.30 * norm(cagr_6y)
             + 0.20 * norm(slope)
             + 0.20 * norm(mean_recent_3y)
             + 0.10 * norm(n_destinations)
             + 0.10 * norm(trend_consistency)
             - 0.10 * norm(cv)
```

## فیلتر کاندیدها

فقط HS Codeهایی که:
1. در دسته `strong_growth`، `moderate_growth`، یا `emerging` باشند.
2. `mean_recent_3y > 1,000,000 USD`.
3. `n_destinations >= 3`.

## توصیه‌ها

برای هر کاندید، `recommendation`:
- `select`: `export_score > 0.7`.
- `monitor`: `export_score` بین ۰.۴ و ۰.۷.
- `investigate`: `export_score < 0.4` یا نوسان بالا.

## مراجع
- [[task-12-export-candidates]]
- [[recipe-09-trend-classification]]
- [[../_MOC]]
- [[../trend/_MOC]]
