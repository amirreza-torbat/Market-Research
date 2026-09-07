---
folder: 06-Analysis/trend
type: moc
last_updated: 1405-06-15
status: pending
---

# 📈 MOC تحلیل روند (Trend Analysis)

> این پوشه پس از تکمیل [[task-10-trend-analysis]] و [[task-11-trend-classification]] پر می‌شود.

## ساختار مورد انتظار

- `_classification-summary.md` — خلاصه طبقه‌بندی روند
- `strong-growth/` — یادداشت‌های HS Code با روند رشد قوی (Top 30)
- `moderate-growth/` — یادداشت‌های HS Code با رشد متوسط (Top 30)
- `emerging/` — یادداشت‌های HS Code نوظهور (Top 30)
- `declining/` — یادداشت‌های HS Code کاهشی (Top 30)
- `charts/` — نمودارهای روند aggregated و heatmap

## فهرست یادداشت‌ها (پس از تکمیل)

> ⬜ هنوز هیچ یادداشتی ساخته نشده. پس از تکمیل `task-10` و `task-11` این فهرست پر خواهد شد.

## تاکسونومی روند

برای جزئیات دسته‌بندی، به [[conventions]] بخش ۵.۱ مراجعه کنید:

| دسته | کد | معیار |
|------|----|-------|
| رشد قوی | `strong_growth` | CAGR > 10٪، MK p < 0.05، slope > 0 |
| رشد متوسط | `moderate_growth` | 0 < CAGR ≤ 10٪، MK p < 0.1 |
| پایدار | `stable` | |CAGR| ≤ 2٪، R² < 0.3 |
| نوسانی | `volatile` | CV > 0.5، R² < 0.3 |
| کاهشی | `declining` | CAGR < 0، MK p < 0.1 |
| نوظهور | `emerging` | value_start = 0، value_end > threshold |
| محوشده | `disappearing` | value_start > threshold، value_end ≈ 0 |

## مراجع
- [[task-10-trend-analysis]]
- [[task-11-trend-classification]]
- [[recipe-09-trend-classification]]
- [[../_MOC]]
