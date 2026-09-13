---
folder: 04-State
type: status
last_updated: 2026-09-13 15:02 (1405-06-22)
---

# 📊 وضعیت پروژه (STATUS)

> **این فایل نقطه شروع هر agent است.** قبل از هر کاری این فایل را بخوانید.

## 🎯 وضعیت کلی

| فیلد | مقدار |
|------|-------|
| **وضعیت کلی** | 🟠 `review` (برای task-10) |
| **تسک فعلی** | `task-10` — تحلیل جامع روند ۵ ساله (تمام HS × تمام کشورها) تکمیل شد — منتظر review کاربر |
| **agent مسئول فعلی** | `analyst` (کار تمام) → قدم بعد با `analyst` (task-11) |
| **آخرین به‌روزرسانی** | 1405-06-22 (2026-09-13) 15:02 |
| **بلوک‌ها** | داده ۱۴۰۵ هنوز در منبع منتشر نشده (Issue-007/008) — تحلیل روی ۵ سال کامل انجام شد |
| **قدم بعدی** | review خروجی task-10 → شروع `task-11` (طبقه‌بندی روند ۷ دسته) |

## 📋 وضعیت تسک‌ها

| Task ID | عنوان | وضعیت | Assignee | به‌روزرسانی |
|---------|-------|-------|----------|--------------|
| `task-00` | راه‌اندازی Vault | 🟢 `done` | vault-writer | 1405-06-15 |
| `task-01` | استخراج فهرست صادرات (۶ سال) | 🟢 `done` | scraper | 1405-06-16 |
| `task-02` | استخراج جزئیات | 🟢 `done` (با task-01) | scraper | 1405-06-16 |
| `task-03` | نرمال‌سازی ETL (۶ سال) | 🟠 `review` | etl-engineer | 1405-06-17 |
| `task-04` | تحلیل به تفکیک کشور (۶ سال) | ⬜ `pending` | — | — |
| `task-05` | تحلیل به تفکیک تعرفه (Top 50) | ⬜ `pending` | — | — |
| **`task-10`** | **تحلیل جامع روند (تمام HS×تمام کشورها)** | 🟠 `review` | analyst | 1405-06-22 |
| **`task-11`** | **طبقه‌بندی روند + اعتبارسنجی آماری** | ⬜ `pending` | — | — |
| **`task-12`** | **رتبه‌بندی کاندیدهای صادرات** | ⬜ `pending` | — | — |
| `task-06` | اعتبارسنجی QA | ⬜ `pending` | — | — |
| `task-07` | خروجی Excel (۱۸ شیت) | ⬜ `pending` | — | — |
| `task-08` | خروجی Obsidian | ⬜ `pending` | — | — |
| `task-09` | انتشار GitHub | ⬜ `pending` | — | — |

**راهنما**: ⬜ pending → 🟡 in-progress → 🟠 review → 🟢 done | 🔴 blocked

## 🚦 مسیر فعلی (با تسک‌های جدید)

```
[task-00: setup] ✅ DONE
       ↓
[task-01/02: scrape 6y] ✅ DONE (626,395 records, 5 years)
       ↓
[task-03: etl-normalize 6y] 🟠 REVIEW (Parquet + refs ready)
       ↓
   ┌────────────┴────────────────────────┐
   ↓                                       ↓
[task-04: by-country 6y]            [task-05: by-tariff Top50]
   ↓                                       ↓
   └────────────┬──────────────────────────┘
                ↓
       [task-10: trend-analysis ALL HS×Country]  ⭐ قلب پروژه
                ↓
       [task-11: trend-classification]
                ↓
       [task-12: export-candidates ranking]  ⭐ هدف نهایی
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

## 🆕 تغییرات اخیر (۱۴۰۵-۰۶-۲۲ — task-10 توسط analyst)

1. **تحلیل روند ۵ ساله کامل شد**: تمام **۵۰,۱۹۶ جفت** (HS × Country) از ۶۲۶,۳۹۵ رکورد بدون هیچ فیلتری → `05-Data/processed/trend-analysis-5y.parquet` (۳.۱MB، ۲۱ ستون، snappy).
2. **دقت عددی ۱۰۰٪**: تلورانس = ۰.۰۰۰۰۰۰۰۰۰۰ برای جمع هر ۵ سال (آستانه: ۰.۰۰۰۱٪) — تست مستقل `scripts/test_trend_precision.py` (۱۷ بررسی، همه PASS).
3. **۱۳ شاخص برای هر جفت**: cagr_5y/pct_change_5y/growth_multiplier با Decimal(prec 28)؛ slope/r_squared (OLS)، mk_p_value (Mann-Kendall با tie correction)، cv، trend_consistency، mean_value، mean_recent_3y، n_years_with_data — vectorized (۲ ثانیه).
4. **`cagr_6y` همیشه NULL** (Issue-008: ۱۴۰۵ در منبع نیست؛ N=4 برای CAGR) — اسکیما برای task-11/12 حفظ شد.
5. **گزارش خلاصه ۱۰ بخشی**: `trend-analysis-summary.md` شامل متدولوژی، توزیع CAGR (۶,۴۸۵ رشد / ۶,۰۲۰ کاهش)، **هشدار آماری MK با n=5 (حداقل p≈0.0275)**، Top-10 ها و پیش‌نمایش طبقات (آستانه‌های Decision-010): strong_growth ۳۴۰، declining ۹۰۴، emerging ۱,۶۸۶، disappearing ۱,۵۹۳.
6. آماده task-11 (طبقه‌بندی ۷ دسته با اولویت انحصاری) و task-12 (رتبه‌بندی با وزن‌های Decision-009).

## 🆕 تغییرات اخیر (۱۴۰۵-۰۶-۱۷ — task-03 توسط etl-engineer)

1. **ETL کامل شد**: ۶۲۶,۳۹۵ رکورد از ۵ سال (۱۴۰۰-۱۴۰۴) به یک Parquet واحد نرمال شد (`05-Data/processed/exports_1400-1405.parquet`, ۱۵MB).
2. **دقت عددی ۱۰۰٪**: تلورانس = ۰.۰۰۰۰۰۰۰۰۰۰ برای همه ۵ سال (آستانه: ۰.۰۰۰۱٪) — تست مستقل در `scripts/test_precision.py`.
3. **نگاشت ۱۶۶ کشور**: همه نام‌های فارسی به ISO 3166-1 alpha-2 نگاشت شد در `05-Data/processed/countries-mapping.csv`. کدهای user-assigned برای موارد غیراستاندارد: XO (سایر خارجی)، ZF (مناطق آزاد)، ZS (مناطق ویژه)، ZZ (نامشخص).
4. **۵۹۹۳ HS Code** در فرمت HH.HH.HH.HH، با مشتقات hs_code_2/4/6/8.
5. **Issues مستندسازی شد**: 005 (منبع جایگزین)، 006 (۱۴۰۳/۱۴۰۴ بدون ماه → month=0 + is_monthly=False)، 007 (export_quantity حذف شد)، 008 (۱۴۰۵ در Parquet نیست).
6. **خروجی‌ها**: exports_1400-1405.parquet, _dataset-metadata.json, countries-mapping.csv, countries.csv, hs-codes.csv, _validation-report.md.

## 🆕 تغییرات اخیر (۱۴۰۵-۰۶-۱۵ ۱۴:۰۰)

بر اساس درخواست کاربر در پیام دوم:
1. **بازه زمانی از ۵ سال به ۶ سال** افزایش یافت (۱۴۰۰ تا ۱۴۰۵، سال جاری partial).
2. **۳ تسک جدید** اضافه شد:
   - `task-10`: حلقه کامل روی **تمام** HS × **تمام** کشورها در ۶ سال.
   - `task-11`: طبقه‌بندی روند به ۷ دسته با اعتبارسنجی آماری (Mann-Kendall).
   - `task-12`: رتبه‌بندی کاندیدهای صادرات با نمره ترکیبی.
3. **تاکسونومی روند ۷ دسته‌ای** در `conventions.md` بخش ۵ اضافه شد.
4. **نمره‌دهی export_score** با ۶ وزن قابل تنظیم در `conventions.md` بخش ۵.۳.
5. **شیت‌های Excel از ۱۱ به ۱۸** رسید (شامل Trend-All، Classification، Candidates).
6. **recipe-09** جدید برای متدولوژی طبقه‌بندی و رتبه‌بندی.

## 🆕 تغییرات اخیر (۱۴۰۵-۰۶-۱۶ — task-01 توسط scraper)

1. **منبع داده**: تست DNS سه resolver جهانی → `tsd.irica.ir` از خارج ایران قابل دسترسی نیست → آینه `service.tccim.ir` به‌عنوان منبع فعال ثبت شد (**Decision-011**).
2. **استخراج کامل ۱۴۰۰ تا ۱۴۰۴** انجام شد: **۶۲۶,۳۹۵ رکورد یکتای جزئی** (کد تعرفه × ماه × گمرک × کشور) + **۱۲,۷۸۶ سطر تجمیعی** (گمرک × کشور) — ۹۹ فصل HS × ۵ سال، صفر فصل شکسته.
3. **۱۴۰۰-۱۴۰۲**: تفکیک ماهانه کامل (۱۲ ماه). **۱۴۰۳-۱۴۰۴**: رکورد جزئی بدون صفت ماه (Issue-006).
4. **۱۴۰۵**: منبع هیچ داده‌ای ندارد → `months_available_1405 = 0` (Issue-007) — پس از انتشار، با `scripts/scrape_customs.py` قابل افزودن است.
5. **QA**: پوشش جزئیات ≈ ۹۹.۹۳٪ جریان ارزش؛ صفر کلید تکراری؛ جمع سالانه با آمار رسمی همخوان (جدول در `05-Data/raw/_summary.md`).
6. خروجی‌ها: `05-Data/interim/exports_YYYY_raw.csv` + `exports_YYYY_aggregate.csv` + `05-Data/raw/_summary.md`.

## ⚠️ مسائل بحرانی (Critical Issues)

### ۱. URL گمرک — ✅ حل شد (Decision-011)
- **وضعیت**: 🟢 resolved — منبع فعال `service.tccim.ir` ثبت شد
- **توضیح**: تست DNS نشان داد `tsd.irica.ir` از خارج ایران قابل دسترسی نیست. طبق دستور کاربر در پرامپت task-01، آینه معتبر tccim (اعتبارسنجی‌شده) جایگزین شد.
- **اقدام آینده**: در صورت دسترسی از داخل ایران به TSD، اعتبارسنجی متقابل انجام شود.

### ۲. توکن GitHub در معرض عموم قرار گرفته
- **وضعیت**: 🔴 security
- **توضیح**: کاربر توکن GitHub را در پیام IM فرستادند.
- **اقدام**: کاربر باید توکن را revoke کرده و یکی جدید بسازد. توکن جدید در فایل `.env` یا `gh auth login` قرار گیرد. **هرگز در فایل‌ها commit نشود**.

## 📝 یادداشت‌های مهم برای agentهای بعدی

### برای Scraper (task-01) — ✅ انجام شد:
- ~~قبل از شروع، decisions.md را برای URL تأییدشده بررسی کن~~ → Decision-011 ثبت شد.
- ~~اگر URL تأیید نشده، متوقف شو~~ → طبق دستور پرامپت، منبع جایگزین تست و ثبت شد.
- ~~۶ سال استخراج کن~~ → ۱۴۰۰-۱۴۰۴ کامل شد؛ ۱۴۰۵ در منبع خالی است (Issue-007).
- ادامه کار: پس از انتشار داده ۱۴۰۵ در منبع: `python scripts/scrape_customs.py detail --years 1405`

### برای ETL Engineer (task-03) — ✅ انجام شد:
- ✅ ۶ سال (به‌جز ۱۴۰۵ که در منبع نیست) در Parquet ذخیره شد.
- ✅ فایل `_dataset-metadata.json` با `months_available_per_year` و `issues_addressed` ساخته شد.
- ✅ دقت عددی ۱۰۰٪ تأیید شد (تلورانس = ۰).
- ✅ جداول مرجع countries.csv و hs-codes.csv ساخته شد.
- ادامه کار: پس از افزودن داده ۱۴۰۵ (وقتی در منبع منتشر شد)، کافی است `python scripts/scrape_customs.py detail --years 1405 && python scripts/etl_normalize.py` اجرا شود.

### برای Analyst (task-04 / task-05 / task-11 / task-12):
- داده آماده در `05-Data/processed/exports_1400-1405.parquet`.
- **خروجی task-10 آماده است**: `05-Data/processed/trend-analysis-5y.parquet` (۵۰,۱۹۶ جفت × ۲۱ ستون) + `trend-analysis-summary.md`.
- Schema در `_dataset-metadata.json`.
- **محدودیت مهم (Issue-006)**: تحلیل‌های ماهانه فقط روی ۱۴۰۰-۱۴۰۲ قابل اجراست. برای ۱۴۰۳/۱۴۰۴ فقط تحلیل سالانه.
- **محدودیت (Issue-008)**: ۱۴۰۵ در داده نیست. CAGR ۵ ساله (۱۴۰۰-۱۴۰۴) حساب شد؛ `cagr_6y` NULL.
- **هشدار آماری (task-11)**: با n=5 حداقل p-value ممکن در MK ≈ 0.0275 است؛ معیار p<0.05 عملاً یعنی سری کاملاً یکنواخت. MK را در کنار CAGR/R²/ثبات تفسیر کن.
- `task-04`: تحلیل به تفکیک کشور روی ۱۶۶ کشور (شامل کدهای user-assigned XO/ZF/ZS/ZZ).
- `task-05`: تحلیل به تفکیک تعرفه روی ۵۹۹۳ HS Code.
- `task-11`: ۷ دسته روند را با **اولویت انحصاری** (دسته‌ها هم‌اکنون overlap دارند) طبقه‌بندی کن؛ آستانه‌های Decision-010.
- `task-12`: نمره‌دهی با وزن‌های Decision-009.
- برای خواندن Parquet:
  ```python
  import pyarrow.parquet as pq
  df = pq.read_table('05-Data/processed/exports_1400-1405.parquet').to_pandas()
  # export_value_usd / export_value_rial / export_weight_kg به‌صورت Decimal
  ```

### برای همه agentها:
- قبل از شروع، این فایل را بخوان.
- بعد از پایان کار، این فایل را به‌روز کن (طبق [`recipe-08`](../03-Recipes/recipe-08-update-state.md)).
- اگر مسأله‌ای یافتی، در [`issues.md`](issues.md) ثبت کن.

## 🔗 مراجع

- [/01-Tasks/_MOC](../01-Tasks/_MOC.md) — فهرست تسک‌ها با نمودار وابستگی جدید
- [/04-State/progress](progress.md)
- [/04-State/issues](issues.md)
- [/04-State/decisions](decisions.md) — تصمیم‌های ۰۰۷ تا ۰۱۰ اضافه شد
- [/00-Overview/project-overview](../00-Overview/project-overview.md)
- [/00-Overview/conventions](../00-Overview/conventions.md) — بخش ۵ (تاکسونومی روند)
- [/03-Recipes/recipe-09-trend-classification](../03-Recipes/recipe-09-trend-classification.md) — متدولوژی جدید
- [/05-Data/processed/_validation-report](../05-Data/processed/_validation-report.md) — گزارش task-03
- [/05-Data/processed/_dataset-metadata](../05-Data/processed/_dataset-metadata.json) — schema و issues
