---
folder: 00-Overview
type: convention
last_updated: 1405-06-15
---

# 📐 قراردادها و استانداردها (Conventions)

این سند **منبع حقیقت** برای همه قراردادهای نام‌گذاری، فرمت و زبان در Vault است. هر agent **باید** قبل از ایجاد هر فایلی این سند را رعایت کند.

---

## ۱. زبان و فونت

- **زبان اصلی**: فارسی برای توضیحات و تحلیل‌ها.
- **اصطلاحات فنی**: به انگلیسی نگه داشته شوند (مثل `HS Code`, `ETL`, `schema`).
- **نام فیلدهای داده**: همیشه انگلیسی و `snake_case` (مثل `export_value_usd`, `destination_country`).
- **اعداد**: در فایل‌های متنی فارسی، ارقام فارسی (`۱۲۳۴`) استفاده شود. در داده‌ساختاریافته (CSV/Parquet) ارقام لاتین.
- **تاریخ**: همیشه به فرمت ISO با پسوند شمسی، مثلاً `1404-12-29 (jalali)`. در نام فایل از `YYYY-MM-DD` میلادی استفاده شود.

---

## ۲. نام‌گذاری فایل‌ها

### ۲.۱ یادداشت‌های عمومی
- فرمت: `kebab-case`
- بدون پیشوند عددی (مگر اینکه ترتیب مهم باشد)
- مثال: `country-iraq-trend.md`

### ۲.۲ تسک‌ها
- فرمت: `task-NN-short-slug.md`
- `NN` = شماره دو رقمی تسک
- مثال: `task-04-analysis-country.md`

### ۲.۳ پرامپت‌ها
- فرمت: `prompt-role-name.md`
- مثال: `prompt-scraper.md`

### ۲.۴ دستورالعمل‌ها
- فرمت: `recipe-NN-short-slug.md`
- مثال: `recipe-01-scrape-customs.md`

### ۲.۵ فایل‌های داده
- داده خام: `raw/YYYY/export_YYYY_table-NN.html`
- داده پردازش‌شده: `processed/exports_1400-1404.parquet`
- گزارش Excel: `07-Exports/iran-exports-1400-1404-YYYYMMDD.xlsx`

---

## ۳. ساختار یادداشت‌های Obsidian

هر یادداشت تحلیلی باید این frontmatter داشته باشد:

```yaml
---
type: analysis|task|recipe|prompt|state|overview|data
title: عنوان فارسی
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: draft|in-progress|review|done|blocked
tags:
  - analysis
  - country/iraq
related:
  - "[[task-04-analysis-country]]"
---
```

---

## ۴. قراردادهای داده

### ۴.۱ واحدها
- ارزش: همیشه به **دلار آمریکا (USD)**. اگر منبع به یورو یا ریال بود، نرخ تبدیل روز پایگاه داده گمرک استفاده شود و در فایل `exchange-rates.csv` ذخیره شود.
- وزن: کیلوگرم (kg).
- تعداد: عدد صحیح (integer).

### ۴.۲ دقت عددی
- **الزامی**: از `decimal.Decimal` در پایتون استفاده شود، نه `float`.
- خطای نهایی کل **کمتر از 0.0001٪**.
- در گزارش‌ها، ارقام اعشار حداکثر ۴ رقم نشان داده شود.

### ۴.۲.۱ بازه زمانی و سال partial
- بازه تحلیل: **۱۴۰۰ تا ۱۴۰۵** (۶ سال).
- سال ۱۴۰۵ (سال جاری) **partial** است — فقط داده تا آخرین ماه موجود.
- برای محاسبه CAGR و روند، روش‌های زیر اعمال شود:
  - **روش اصلی**: استفاده از ۵ سال کامل (۱۴۰۰ تا ۱۴۰۴) برای CAGR.
  - **روش YTD**: مقایسه همان تعداد ماه از ۱۴۰۵ با همان تعداد ماه از سال‌های قبلی.
  - **روش annualized**: تبدیل مقدار partial ۱۴۰۵ به سالانه با ضریب `12/months_available`.
- روش انتخابی باید در `04-State/decisions.md` ثبت شود.

### ۴.۲.۲ فرمول‌های کلیدی

#### CAGR (Compound Annual Growth Rate)
برای N سال کامل:
```
CAGR = (value_end / value_start)^(1 / N) - 1
```
برای پروژه فعلی با ۵ بازه (۱۴۰۰ تا ۱۴۰۴): `N = 4`.
برای ۶ سال (۱۴۰۰ تا ۱۴۰۵): اگر ۱۴۰۵ annualize شود `N = 5`.

#### درصد تغییر کل
```
percent_change = (value_end - value_start) / value_start * 100
```

#### ضریب رشد (Growth Multiplier)
```
growth_multiplier = value_end / value_start
```

#### تلورانس
```
tolerance = abs(calculated - reference) / reference
```
باید < 0.0001٪ (یعنی < 0.000001 به‌صورت کسر).

### ۴.۳ کد تعرفه (HS Code)
- همیشه به‌صورت رشته (string) ذخیره شود (چون ممکن است با 0 شروع شود).
- فرمت استاندارد: `HH.HH.HH.HH` (HS 8-digit).
- در صورت وجود کد ۶ رقمی یا ۴ رقمی در منبع، در فیلد جداگانه نگه داشته شود.

### ۴.۴ نام کشورها
- استاندارد: **ISO 3166-1 alpha-2** (کد ۲ حرفی) + نام فارسی.
- مثال: `IQ` + `عراق`.
- فایل مرجع: `05-Data/processed/countries.csv` (پس از استخراج ساخته می‌شود).

---

## ۵. تاکسونومی روند (Trend Taxonomy)

برای طبقه‌بندی روند هر جفت (HS Code × Country) در ۶ سال، از سیستم طبقه‌بندی زیر استفاده شود. این طبقه‌بندی در [[task-10-trend-analysis]] و [[task-11-trend-classification]] اعمال می‌شود.

### ۵.۱ دسته‌های اصلی روند

| دسته | کد | شرح | معیار |
|------|----|------|-------|
| رشد قوی | `strong_growth` | رشد پایدار و معنادار | CAGR > 10٪، Mann-Kendall p < 0.05، slope > 0 |
| رشد متوسط | `moderate_growth` | رشد معنادار اما کند | 0 < CAGR ≤ 10٪، Mann-Kendall p < 0.۱ |
| پایدار | `stable` | تغییر قابل توجه نیست | |CAGR| ≤ 2٪، R² < 0.3 |
| نوسانی | `volatile` | تغییرات شدید بدون روند روشن | CV > 0.5، R² < 0.3 |
| کاهشی | `declining` | روند نزولی معنادار | CAGR < 0، Mann-Kendall p < 0.1 |
| نوظهور | `emerging` | صفر در سال‌های اول، مثبت در سال‌های اخیر | value_start = 0، value_end > threshold |
| محوشده | `disappearing` | مثبت در سال‌های اول، صفر یا نزدیک به صفر در آخر | value_start > threshold، value_end ≈ 0 |

### ۵.۲ شاخص‌های محاسبه‌شده برای هر جفت

برای هر جفت `(hs_code, destination_country_iso2)`:

| شاخص | نماد | فرمول | کاربرد |
|------|------|-------|--------|
| CAGR | `cagr_5y` | `(value_1404 / value_1400)^(1/4) - 1` | رشد سالانه مرکب (۵ سال کامل) |
| CAGR شامل ۱۴۰۵ | `cagr_6y` | `(value_1405_annualized / value_1400)^(1/5) - 1` | رشد شامل سال جاری |
| درصد تغییر | `pct_change_5y` | `(value_1404 - value_1400) / value_1400 * 100` | تغییر کل |
| ضریب تغییر | `growth_multiplier` | `value_1404 / value_1400` | ضریب رشد |
| slope رگرسیون | `slope` | slope از OLS روی ۶ نقطه | شدت روند |
| R² | `r_squared` | ضریب تعیین رگرسیون | کیفیت برازش |
| Mann-Kendall p | `mk_p_value` | p-value از تست Mann-Kendall | معناداری آماری |
| ضریب تغییرات | `cv` | std / mean | نوسان |
| ثبات روند | `trend_consistency` | تعداد سال‌های متوالی با رشد مثبت | پایداری |
| میانگین سالانه | `mean_value` | mean(value_1400..1405) | حجم متوسط |
| میانگین ۳ سال اخیر | `mean_recent_3y` | mean(value_1402..1404) | حجم اخیر |
| آخرین مقدار | `value_1405_ytd` | جمع ۱۴۰۵ (تا آخرین ماه) | وضعیت فعلی |
| annualized ۱۴۰۵ | `value_1405_annualized` | `value_1405_ytd * 12 / months_available` | تخمین سالانه ۱۴۰۵ |

### ۵.۳ نمره‌دهی برای انتخاب صادرات (Export Attractiveness Score)

برای رتبه‌بندی محصولات کاندید صادرات، از نمره ترکیبی زیر استفاده شود:

```
export_score = w1 * normalized(cagr_6y)
             + w2 * normalized(slope)
             + w3 * normalized(mean_recent_3y)
             + w4 * normalized(n_destinations)
             + w5 * normalized(trend_consistency)
             - w6 * normalized(cv)        # نوسان بالا = نمره کمتر
```

وزن‌های پیشنهادی (قابل تنظیم در `decisions.md`):
- `w1 = 0.30` (رشد مهم‌ترین)
- `w2 = 0.20` (شیب روند)
- `w3 = 0.20` (حجم)
- `w4 = 0.10` (تنوع بازار)
- `w5 = 0.10` (ثبات)
- `w6 = 0.10` (جریمه نوسان)

نرمال‌سازی: min-max روی کل دیتاست.

---

## ۶. قراردادهای Git

### ۶.۱ پیام commit
- فرمت: `type(scope): subject` (به انگلیسی)
- types: `feat`, `fix`, `docs`, `refactor`, `data`, `analysis`, `chore`
- مثال: `feat(scraper): add pagination handler for 1402 exports`

### ۶.۲ شاخه‌ها (Branches)
- `main` — همیشه قابل انتشار و پایدار
- `feature/task-NN-slug` — برای کار روی تسک NN
- `hotfix/...` — برای رفع اشکال فوری
- هر agent قبل از شروع کار، شاخه جدید می‌سازد.

### ۶.۳ PR
- هیچ push مستقیمی به `main` (مگر برای فایل‌های State).
- PR حداقل به یک reviewer نیاز دارد (یا خود کاربر در صورت کار solo).

---

## ۷. قراردادهای Vault

### ۷.۱ MOC (Map of Content)
- هر پوشه یک `_MOC.md` دارد که فهرست یادداشت‌های آن پوشه است.
- `_MOC.md` همیشه به‌روز نگه داشته شود.

### ۷.۲ Backlinks
- هر یادداشت تحلیلی باید حداقل به یک تسک و یک منبع داده backlink داشته باشد.
- مثال: `[[task-04-analysis-country]]` و `[[exports-1400-1404]]`

### ۷.۳ وضعیت یادداشت
- یادداشت‌های `draft` نباید در گزارش نهایی استفاده شوند.
- یادداشت‌های `done` قابل استناد هستند.

---

## ۸. مدیریت خطاها

### ۸.۱ اگر scraper به خطا خورد
- در `04-State/issues.md` ثبت شود.
- اگر retry شد، نتیجه در همان issue یادداشت شود.
- اگر data-driven blocker است، تسک مرتبط به `blocked` تغییر وضعیت دهد.

### ۸.۲ اگر دقت عددی زیر 0.0001٪ نشد
- کار متوقف شود.
- در `04-State/issues.md` ریشه‌یابی شود.
- تا رفع، status پروژه در `STATUS.md` به `blocked` تغییر کند.

---

## ۹. حریم خصوصی و امنیت

- هیچ توکن، کلمه عبور یا اطلاعات حساس در فایل‌ها قرار نگیرد.
- فایل `.gitignore` شامل: `.env`, `*.local.md`, `secrets.*`, فایل‌های بزرگ داده (که به LFS منتقل می‌شوند یا کلاً commit نمی‌شوند).
- برای داده‌های بزرگ (>10MB) از Git LFS یا ذخیره خارجی استفاده شود.

---

## مراجع

- [[project-overview]]
- [[data-sources]]
- [[glossary]]
- [/02-Prompts/_MOC](../02-Prompts/_MOC.md)
- [/03-Recipes/_MOC](../03-Recipes/_MOC.md)
