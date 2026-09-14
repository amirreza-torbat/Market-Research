---
folder: 05-Data
type: moc
last_updated: 1405-06-22
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
    ├── exports_1400-1405.parquet      # ۶۲۶,۳۹۵ رکورد نرمال (task-03)
    ├── trend-analysis-5y.parquet      # ۵۰,۱۹۶ جفت × ۲۱ ستون شاخص روند (task-10)
    ├── trend-analysis-summary.md      # گزارش تحلیل روند ۱۰ بخشی (task-10)
    ├── countries-mapping.csv          # نگاشت نام فارسی → ISO alpha-2
    ├── countries.csv
    ├── hs-codes.csv
    ├── _dataset-metadata.json         # schema + issues (task-03)
    └── _validation-report.md          # گزارش validation (task-03)
```

## مراحل تولید داده

| مرحله | پوشه | نقش | تسک |
|-------|------|-----|-----|
| استخراج خام | `raw/` | Scraper | [[task-01-scrape-list]] |
| CSV موقت | `interim/` | Scraper | [[task-01-scrape-list]] |
| نرمال‌سازی | `processed/exports_1400-1405.parquet` | ETL Engineer | [[task-03-etl-normalize]] |
| **تحلیل روند جامع** | `processed/trend-analysis-5y.parquet` | Analyst | [[task-10-trend-analysis]] |
| تحلیل کشور | `processed/analysis-by-country.csv` | Analyst | [[task-04-analysis-country]] |
| تحلیل تعرفه | `processed/analysis-by-tariff*.csv` | Analyst | [[task-05-analysis-tariff]] |
| طبقه‌بندی روند | `processed/trend-classification*.parquet` | Analyst | [[task-11-trend-classification]] |
| **رتبه‌بندی کاندیدها** | `processed/export-candidates-ranked.parquet` (۵۷۴ × ۳۱) | Analyst | [[task-12-export-candidates]] |

## نکات

- ⚠️ **داده خام قابل تغییر نیست**: فایل‌های `raw/` پس از استخراج نباید تغییر کنند.
- ⚠️ **فایل‌های بزرگ**: اگر `processed/exports_1400-1405.parquet` یا `trend-analysis-5y.parquet` > 50MB شد، با Git LFS یا ذخیره خارجی (فعلاً ۱۵MB و ۳.۱MB).
- ⚠️ **encoding**: همه فایل‌ها UTF-8.

## مراجع
- [[task-01-scrape-list]]
- [[task-03-etl-normalize]]
- [[task-10-trend-analysis]]
- [[task-04-analysis-country]]
- [[task-05-analysis-tariff]]
- [/00-Overview/data-sources](../00-Overview/data-sources.md)
