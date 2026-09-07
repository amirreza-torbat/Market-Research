---
folder: 05-Data
type: moc
last_updated: 1405-06-15
---

# 📦 MOC داده‌ها (Data Map of Content)

## ساختار

```
05-Data/
├── raw/              # داده خام (HTML, JSON از گمرک)
│   ├── 1400/
│   ├── 1401/
│   ├── 1402/
│   ├── 1403/
│   ├── 1404/
│   └── _summary.md   # گزارش خلاصه scraping
├── interim/          # داده میانی (CSV موقت قبل از نرمال‌سازی)
│   ├── exports_1400_raw.csv
│   ├── exports_1401_raw.csv
│   ├── exports_1402_raw.csv
│   ├── exports_1403_raw.csv
│   └── exports_1404_raw.csv
└── processed/        # داده نرمال‌شده (آماده تحلیل)
    ├── exports_1400-1404.parquet
    ├── analysis-by-country.csv
    ├── analysis-by-tariff.csv
    ├── analysis-by-tariff-country.csv
    ├── countries.csv
    ├── hs-codes.csv
    ├── exchange-rates.csv
    └── _validation-report.md
```

## مراحل تولید داده

| مرحله | پوشه | نقش | تسک |
|-------|------|-----|-----|
| استخراج خام | `raw/` | Scraper | [[task-01-scrape-list]] |
| CSV موقت | `interim/` | Scraper | [[task-01-scrape-list]] |
| نرمال‌سازی | `processed/` | ETL Engineer | [[task-03-etl-normalize]] |
| تحلیل کشور | `processed/analysis-by-country.csv` | Analyst | [[task-04-analysis-country]] |
| تحلیل تعرفه | `processed/analysis-by-tariff*.csv` | Analyst | [[task-05-analysis-tariff]] |

## نکات

- ⚠️ **داده خام قابل تغییر نیست**: فایل‌های `raw/` پس از استخراج نباید تغییر کنند.
- ⚠️ **فایل‌های بزرگ**: اگر `processed/exports_1400-1404.parquet` > 50MB شد، با Git LFS یا ذخیره خارجی.
- ⚠️ **encoding**: همه فایل‌ها UTF-8.

## مراجع
- [[task-01-scrape-list]]
- [[task-03-etl-normalize]]
- [[task-04-analysis-country]]
- [[task-05-analysis-tariff]]
- [/00-Overview/data-sources](../00-Overview/data-sources.md)
