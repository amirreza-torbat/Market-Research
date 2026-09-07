---
type: template
template_for: analysis-tariff-note
last_updated: 1405-06-15
---

# قالب یادداشت تحلیل تعرفه (HS Code)

> این قالب را برای ساخت یادداشت‌های تحلیل HS Code در `06-Analysis/by-tariff/` استفاده کنید.
> نام فایل: `hs-XX-XXXX-XX-XX.md` (HS Code با نقطه).

---

```markdown
---
type: analysis
title: روند صادرات [شرح کالا] به تفکیک کشور (۱۴۰۰-۱۴۰۴)
hs_code: HH.HH.HH.HH
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft
tags:
  - analysis
  - tariff/HH.HH.HH.HH
related:
  - "[[task-05-analysis-tariff]]"
  - "[[data-sources]]"
folder: 06-Analysis/by-tariff
---

# روند صادرات [شرح کالا] (HS: HH.HH.HH.HH) به تفکیک کشور

## خلاصه
[۳-۵ جمله کلیات — نوع کالا، اهمیت، روند کلی]

## شاخص‌های کلی (aggregated)
| سال | ارزش (USD) | وزن (kg) |
|-----|------------|----------|
| 1400 | ... | ... |
| 1401 | ... | ... |
| 1402 | ... | ... |
| 1403 | ... | ... |
| 1404 | ... | ... |

- **CAGR**: X.XX%
- **تغییر مطلق**: X,XXX,XXX,XXX USD
- **تغییر درصدی**: XX.XX%
- **تعداد کشورهای مقصد**: N
- **تعداد کشورهای با رشد**: N

## نمودار روند کلی
![[charts/hs-XX-XXXX-XX-XX-trend.png]]

## کشورهای با افزایش صادرات

| کشور | 1400 | 1404 | CAGR | تغییر مطلق |
|------|------|------|------|------------|
| ... | ... | ... | ... | ... |

## نمودار Top 10 کشور
![[charts/hs-XX-XXXX-XX-XX-top10.png]]

## تحلیل کیفی
[۱۵۰-۲۰۰ کلمه — نوع کالا، عوامل رشد، کشورهای کلیدی، روند جهانی]

## یافته‌های کلیدی
- **یافته ۱**: [۳-۵ جمله]
- **یافته ۲**: [۳-۵ جمله]
- **یافته ۳**: [۳-۵ جمله]

## توصیه‌ها
- [۳-۵ جمله]

## مراجع
- [[task-05-analysis-tariff]]
- [[data-sources]]
- [[by-tariff/_summary]]
- [[by-tariff/_MOC]]
```
