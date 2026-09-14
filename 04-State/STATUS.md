---
folder: 04-State
type: status
last_updated: 2026-09-14 16:30 (1405-06-24)
---

# 📊 وضعیت پروژه (STATUS)

> **این فایل نقطه شروع هر agent است.** قبل از هر کاری این فایل را بخوانید.

## 🎯 وضعیت کلی

| فیلد | مقدار |
|------|-------|
| **وضعیت کلی** | 🟠 `review` (برای task-07 — فایل Excel ۱۸ شیت ساخته شد) |
| **تسک فعلی** | `task-07` — فایل Excel نهایی ساخته شد (۱۲.۵۸ MB، ۱۸ شیت، ۴ نمودار) — منتظر review کاربر |
| **agent مسئول فعلی** | `etl-engineer` (کار تمام) → قدم بعد: task-08 (Obsidian) و task-09 (انتشار) |
| **آخرین به‌روزرسانی** | 1405-06-24 (2026-09-14) |
| **بلوک‌ها** | داده ۱۴۰۵ هنوز در منبع منتشر نشده (Issue-007/008) — تحلیل روی ۵ سال کامل انجام شد |
| **قدم بعدی** | review فایل Excel (`07-Exports/iran-exports-1400-1405-20260914.xlsx`) → سپس `task-08` (Obsidian) و `task-09` (انتشار) |

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
| **`task-11`** | **طبقه‌بندی روند + اعتبارسنجی آماری** | 🟠 `review` | analyst | 1405-06-22 |
| **`task-12`** | **رتبه‌بندی کاندیدهای صادرات + بازکالیبراسیون** | 🟠 `review` | analyst | 1405-06-23 |
| `task-06` | اعتبارسنجی QA | 🟠 `review` | qa-validator | 1405-06-23 |
| `task-07` | خروجی Excel (۱۸ شیت) | 🟠 `review` | etl-engineer | 1405-06-24 |
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

## 🆕 تغییرات اخیر (۱۴۰۵-۰۶-۲۳ — task-06 توسط qa-validator)

1. **اعتبارسنجی نهایی کل pipeline انجام شد — ۴۹/۴۹ تست PASS** (`scripts/qa_validate_final.py`، شاخه `feature/task-06-qa`). بیشینه تلورانس عددی مشاهده‌شده: **۰.۰۰۰۰۰۰۰۰۰۰٪** (آستانه < 0.0001٪) — زنجیره raw → processed → trend → classification → candidates بدون هیچ خطای عددی.
2. **۹ گروه تست**: (۱) سازگاری عددی Raw→Processed هر ۵ سال، (۲) Processed→Trend، (۳) Trend→Classification، (۴) Classification→Candidates (شامل فیلتر membership)، (۵) کامل‌بودن (۵ سال / ۱۶۶ کشور / ۵,۹۹۳ HS / بدون null)، (۶) فرمت (HS HH.HH.HH.HH / ISO XX / value ≥ 0)، (۷) سازگاری تحلیل (rank یکتا، توصیه‌های صدکی سازگار با آستانه‌ها)، (۸) Excel ۷ شیت (All-Candidates ۵۷۴ / Select ۵۸ / Monitor ۱۷۲ / Top-500)، (۹) مستندسازی Issues 005/006/007/008 در metadata.
3. **یافته ریشه‌یابی‌شده**: آستانه «۱۰۰k رکورد/سال» recipe-04 (مورخ قبل از کشف Issue-006) برای ۱۴۰۳/۱۴۰۴ false positive داد — این سال‌ها در منبع سطح-سال تجمیع‌اند (مشکل صفت ماه، نه فقدان داده)؛ کامل‌بودن ارزش‌شان مستقلاً با تلورانس صفر تأیید شد. معیار به نسخه Issue-006-aware اصلاح و در Issue-009 ثبت شد — **هیچ داده یا کد تسک‌های قبلی تغییر نکرد**.
4. **خروجی‌ها**: `04-State/qa-report.md` (گزارش کامل با بخش شفافیت اجرا) + `05-Data/processed/qa-validation.json` (structured) + `scripts/qa_validate_final.py` (قابل اجرای مجدد).
5. **نتیجه**: گات task-06 عبور شد — `task-07` (Excel ۱۸ شیت)، `task-08` (Obsidian) و `task-09` (انتشار) **unblocked** هستند.

## 🆕 تغییرات اخیر (۱۴۰۵-۰۶-۲۳ — task-12 بازکالیبراسیون توسط analyst)

1. **بازکالیبراسیون آستانه‌های توصیه با روش صدک** (پاسخ به ۲ ایراد کاربر): آستانه‌های ثابت 0.4/0.7 با دامنه واقعی نمره‌ها [-0.03, 0.35] ناسازگار بودند و همه ۵۷۴ کاندید «investigate» می‌شدند → آستانه‌های نسبی: **select ≥ صدک ۹۰ (= 0.103)**، **monitor ≥ صدک ۶۰ (= 0.061)**.
2. **توزیع جدید**: select **۵۸** (۱۰.۱٪) | monitor **۱۷۲** (۳۰.۰٪) | investigate **۳۴۴** (۵۹.۹٪) — قابل‌اقدام و منطقی (پیش‌بینی تسک: ~۵۷/~۱۷۲/~۳۴۵).
3. **Excel کامل همه کاندیدها**: `07-Exports/iran-export-candidates-500.xlsx` (۴۲۱KB، ۷ شیت: All-Candidates ۵۷۴ / Top-500 / Select / Monitor / By-Chapter ۶۰ فصل / By-Target-Country ۳۰ کشور / Methodology) — color-scale روی export_score + رنگ وضعیت توصیه + AutoFilter/Freeze + فرمت اعداد.
4. **دقت شیت کشورها**: به‌جای انتساب total_value_1404 کل HS به هر کشورِ top-5 (تورش تا ۵×)، ارزش واقعی جفت‌های HS×Country از `trend-analysis-5y.parquet` (task-10) خوانده شد — پوشش join: ۱۰۰٪ (۱,۲۴۳ جفت).
5. **گزارش اجرایی به Top 50 گسترش یافت** (`_executive-ranking.md` بازنویسی: ۷ بخش + جدول آستانه‌های صدکی + تحلیل کیفی Top 5 + Top 10 فصل + چرایی شکست آستانه ثابت).
6. **خروجی‌ها**: `export-candidates-ranked-recalibrated.parquet` (۵۷۴×۳۴؛ ستون‌های +recommendation_old/+select_threshold/+monitor_threshold) + اسکریپت `scripts/recalibrate_and_export_excel.py`.
7. **QA**: ۶۰/۶۰ بررسی معنایی PASS (شامل بازمحاسبه مستقل شیت کشورها) + validate/audit/scan ساختاری صفر خطا.
8. شاخه: `feature/task-12-recalibrate` (بر پایه feature/task-12-ranking).

## 🆕 تغییرات اخیر (۱۴۰۵-۰۶-۲۳ — task-12 توسط analyst)

1. **رتبه‌بندی کاندیدهای صادرات (هدف نهایی پروژه) تکمیل شد**: از ۵,۹۹۳ HS Code → فیلتر membership (حداقل یک جفت strong/moderate/emerging طبق یافته task-11) → ۱,۰۴۶ → با فیلترهای recipe-09 §۶ (mean_recent_3y > 1M$ و n_destinations_active ≥ 3) → **۵۷۴ کاندید نهایی** در ۶۰ فصل HS — `export-candidates-ranked.parquet` (۵۷۴ × ۳۱ ستون).
2. **نمره‌دهی**: `export_score` با وزن‌های Decision-009 (0.30/0.20/0.20/0.10/0.10/0.10) و Min-Max؛ **cagr_5y جایگزین cagr_6y** (Issue-008 — مستند در گزارش §۱/§۹)؛ ستون اطلاعاتی `n_significant_pairs` برای هشدار MK (n=5, min p≈0.0275) بدون تغییر وزن‌ها.
3. **رتبه‌بندی معنادار**: رتبه ۱ گاز طبیعی (27.11.21.90 — TR/IQ)، ۲ میله‌های فولادی (CAGR ۹۱۲٪)، ۳ سنگ آهن هماتیت (CAGR ۱۲۵۰٪)، ۴ قیرنفت (۴۷ مقصد)، ۵ پروپان، ۸ اوره، ۱۱ پسته...
4. **⚠️ یافته کالیبراسیون**: نمره‌ها در بازه [-۰.۰۳, ۰.۳۵] فشرده‌اند (هیچ کاندیدی در همه ۶ بُعد هم‌زمان پیشتاز نیست) → آستانه‌های ثابت recipe-09 §۷ (select>0.7/monitor≥0.4) به همه «investigate» می‌رسد؛ مستند در `_executive-ranking.md` §۵ + پیشنهاد بازکالیبراسیون (مثلاً select ≥ 0.25) با re-run در صورت تأیید کاربر (Pending-003/004).
5. **ریسک‌ها**: volatile (همه — cv جفت‌ها با صفر-پرکردن متورم است)، concentrated ۱۷۹، declining_recent ۳۶۸.
6. **خروجی‌های گزارشی**: `_executive-ranking.md` (Top 20 + نمودار میله‌ای + توزیع) + `by-target-country.md` (۱۰۵ کشور؛ TR ۳.۴B$ / IQ ۲.۸B$ / AE / OM / CN در صدر) + `chapter-country-matrix.md` + heatmap (فصل‌های ۲۷/۲۶/۳۹ پرپتانسیل؛ AF با ۶۳ جفت رشد قوی پرتنوع‌ترین مقصد) + **۵۰ یادداشت تفصیلی + ۵۰ نمودار** (rank-NN-hs-*.md).
7. **اعتبارسنجی**: ۱۴/۱۴ بررسی PASS (recipe-09 §۹) — تعداد/نمره/رتبه یکتا/ترتیب/بازه تئوری/جمع مولفه‌ها/فیلترها/سازگاری جمع با task-11.
8. **زنجیره تحلیل کامل شد**: scrape (626,395) → ETL → task-10 (50,196 جفت × ۱۳ شاخص) → task-11 (طبقه‌بندی) → task-12 (رتبه‌بندی ⭐). آماده task-06 (QA) و task-07/08 (خروجی‌ها).

## 🆕 تغییرات اخیر (۱۴۰۵-۰۶-۲۲ — task-11 توسط analyst)

1. **طبقه‌بندی روند کامل شد**: هر **۵۰,۱۹۶ جفت** (HS × Country) به ۷ دسته اصلی + ۳ فرعی طبق recipe-09 §۵ و آستانه‌های Decision-010 دسته‌بندی شد — بدون هیچ NULL. خروجی: `trend-classification.parquet` (۵۰,۱۹۶ × ۲۵ ستون).
2. **توزیع**: strong_growth **۳۴۰** | moderate 20 | weak_growth 3,712 | stable 296 | volatile 4,483 | declining **۸۱۷** | weak_decline 2,615 | emerging **۱,۶۸۶** | disappearing 1,815 | insufficient_data 34,412 (۶۸.۶٪ — جفت‌های sparse با CAGR NULL).
3. **تجمیع به ۵,۹۹۳ HS Code**: `trend-classification-by-hs.parquet` با dominant_trend، شمارش دسته‌ها، growth_diversity_score، cagr_5y_aggregated و n_destinations_active.
4. **۱۰۸ یادداشت Obsidian + ۱۰۲ نمودار PNG** در `06-Analysis/trend/` (Top 30 strong-growth / 18 moderate / 30 emerging / 30 declining) — نمودارهای فارسی با arabic_reshaper + bidi + DejaVu Sans (matplotlib از RTL shaping پشتیبانی نمی‌کند).
5. **انحراف مستندشده**: انتخاب یادداشت‌ها با روش membership (`n_<cat> > 0`) به‌جای فیلتر dominant_trend پرامپت — چون ۵,۵۵۸ از ۵,۹۹۳ HS غالب insufficient_data دارند و فیلتر اولیه فقط ۳۷ یادداشت می‌داد. جزئیات در `_classification-summary.md` §۱۰.
6. **هشدار آماری MK** (n=5 → حداقل p≈0.0275) در گزارش §۴ مستند شد؛ توصیه task-12: فیلتر membership (نه dominant) + is_significant به‌عنوان وزن.
7. اعتبارسنجی: همه PASS (تعداد ردیف، اعتبار دسته‌ها، حفظ جمع value_1404 < 1e-9 نسبی، جمع n_countries = 50,196).

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

### برای Analyst (task-04 / task-05) — task-12 ✅ انجام شد:
- ~~فیلتر membership + وزن‌های Decision-009~~ → `export-candidates-ranked.parquet` (۵۷۴ کاندید × ۳۱ ستون) + `_executive-ranking.md` + `by-target-country.md` + `chapter-country-matrix.md` + ۵۰ یادداشت در `06-Analysis/export-candidates/`.
- ~~در صورت تأیید کاربر، بازکالیبراسیون آستانه‌های توصیه (§۵ گزارش اجرایی) با re-run~~ → ✅ انجام شد (۱۴۰۵-۰۶-۲۳): آستانه‌های صدکی (select ≥ p90=0.103 → ۵۸ کاندید؛ monitor ≥ p60=0.061 → ۱۷۲) + Excel کامل ۵۷۴ کاندید در `07-Exports/iran-export-candidates-500.xlsx`.
- ادامه کار: پس از انتشار داده ۱۴۰۵، به‌روزرسانی کامل زنجیره (task-01 → 03 → 10 → 11 → 12).
- `task-04`: تحلیل به تفکیک کشور روی ۱۶۶ کشور (شامل کدهای user-assigned XO/ZF/ZS/ZZ).
- `task-05`: تحلیل به تفکیک تعرفه روی ۵۹۹۳ HS Code.
- داده خام در `05-Data/processed/exports_1400-1405.parquet` (Schema در `_dataset-metadata.json`؛ خواندن با pyarrow — مقادیر به‌صورت Decimal).
- **محدودیت (Issue-006)**: تحلیل ماهانه فقط روی ۱۴۰۰-۱۴۰۲؛ **(Issue-008)**: ۱۴۰۵ نیست، `cagr_6y` → NULL؛ **هشدار MK (n=5, min p≈0.0275)**: `is_significant` را در کنار CAGR/R²/ثبات تفسیر کنید.

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
