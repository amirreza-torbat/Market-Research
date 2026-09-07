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

### ۴.۳ کد تعرفه (HS Code)
- همیشه به‌صورت رشته (string) ذخیره شود (چون ممکن است با 0 شروع شود).
- فرمت استاندارد: `HH.HH.HH.HH` (HS 8-digit).
- در صورت وجود کد ۶ رقمی یا ۴ رقمی در منبع، در فیلد جداگانه نگه داشته شود.

### ۴.۴ نام کشورها
- استاندارد: **ISO 3166-1 alpha-2** (کد ۲ حرفی) + نام فارسی.
- مثال: `IQ` + `عراق`.
- فایل مرجع: `05-Data/processed/countries.csv` (پس از استخراج ساخته می‌شود).

---

## ۵. قراردادهای Git

### ۵.۱ پیام commit
- فرمت: `type(scope): subject` (به انگلیسی)
- types: `feat`, `fix`, `docs`, `refactor`, `data`, `analysis`, `chore`
- مثال: `feat(scraper): add pagination handler for 1402 exports`

### ۵.۲ شاخه‌ها (Branches)
- `main` — همیشه قابل انتشار و پایدار
- `feature/task-NN-slug` — برای کار روی تسک NN
- `hotfix/...` — برای رفع اشکال فوری
- هر agent قبل از شروع کار، شاخه جدید می‌سازد.

### ۵.۳ PR
- هیچ push مستقیمی به `main` (مگر برای فایل‌های State).
- PR حداقل به یک reviewer نیاز دارد (یا خود کاربر در صورت کار solo).

---

## ۶. قراردادهای Vault

### ۶.۱ MOC (Map of Content)
- هر پوشه یک `_MOC.md` دارد که فهرست یادداشت‌های آن پوشه است.
- `_MOC.md` همیشه به‌روز نگه داشته شود.

### ۶.۲ Backlinks
- هر یادداشت تحلیلی باید حداقل به یک تسک و یک منبع داده backlink داشته باشد.
- مثال: `[[task-04-analysis-country]]` و `[[exports-1400-1404]]`

### ۶.۳ وضعیت یادداشت
- یادداشت‌های `draft` نباید در گزارش نهایی استفاده شوند.
- یادداشت‌های `done` قابل استناد هستند.

---

## ۷. مدیریت خطاها

### ۷.۱ اگر scraper به خطا خورد
- در `04-State/issues.md` ثبت شود.
- اگر retry شد، نتیجه در همان issue یادداشت شود.
- اگر data-driven blocker است، تسک مرتبط به `blocked` تغییر وضعیت دهد.

### ۷.۲ اگر دقت عددی زیر 0.0001٪ نشد
- کار متوقف شود.
- در `04-State/issues.md` ریشه‌یابی شود.
- تا رفع، status پروژه در `STATUS.md` به `blocked` تغییر کند.

---

## ۸. حریم خصوصی و امنیت

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
