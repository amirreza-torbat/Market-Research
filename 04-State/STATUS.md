---
folder: 04-State
type: status
last_updated: 1405-06-15 14:00
---

# 📊 وضعیت پروژه (STATUS)

> **این فایل نقطه شروع هر agent است.** قبل از هر کاری این فایل را بخوانید.

## 🎯 وضعیت کلی

| فیلد | مقدار |
|------|-------|
| **وضعیت کلی** | 🟡 `in-progress` |
| **تسک فعلی** | `task-00` تکمیل شد — آماده `task-01` پس از تأیید URL |
| **agent مسئول فعلی** | `vault-writer` (در حال به‌روزرسانی Vault با تسک‌های جدید) |
| **آخرین به‌روزرسانی** | ۱۴۰۵-۰۶-۱۵ ۱۴:۰۰ |
| **بلوک‌ها** | URL گمرک تأیید نشده |
| **قدم بعدی** | تأیید URL گمرک توسط کاربر، سپس شروع `task-01` (با ۶ سال) |

## 📋 وضعیت تسک‌ها

| Task ID | عنوان | وضعیت | Assignee | به‌روزرسانی |
|---------|-------|-------|----------|--------------|
| `task-00` | راه‌اندازی Vault | 🟢 `done` | vault-writer | 1405-06-15 |
| `task-01` | استخراج فهرست صادرات (۶ سال) | ⬜ `pending` | — | — |
| `task-02` | استخراج جزئیات | ⬜ `pending` | — | — |
| `task-03` | نرمال‌سازی ETL (۶ سال) | ⬜ `pending` | — | — |
| `task-04` | تحلیل به تفکیک کشور (۶ سال) | ⬜ `pending` | — | — |
| `task-05` | تحلیل به تفکیک تعرفه (Top 50) | ⬜ `pending` | — | — |
| **`task-10`** | **تحلیل جامع روند (تمام HS×تمام کشورها)** | ⬜ `pending` | — | — |
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
[task-01: scrape-list 6y] ⬜ READY TO START (پس از تأیید URL)
       ↓
[task-02: scrape-detail] ⬜
       ↓
[task-03: etl-normalize 6y] ⬜
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

## ⚠️ مسائل بحرانی (Critical Issues)

### ۱. URL گمرک نیاز به تأیید کاربر دارد
- **وضعیت**: 🔴 blocker برای `task-01`
- **توضیح**: کاربر در پیام اول اشاره به "سایت گمرک" کرده‌اند اما URL دقیق مشخص نشده. کاندیدها در [`00-Overview/data-sources.md`](../00-Overview/data-sources.md) فهرست شده‌اند.
- **اقدام مورد نیاز**: کاربر باید URL نهایی را در [`04-State/decisions.md`](decisions.md) ثبت کند.

### ۲. توکن GitHub در معرض عموم قرار گرفته
- **وضعیت**: 🔴 security
- **توضیح**: کاربر توکن GitHub را در پیام IM فرستادند.
- **اقدام**: کاربر باید توکن را revoke کرده و یکی جدید بسازد. توکن جدید در فایل `.env` یا `gh auth login` قرار گیرد. **هرگز در فایل‌ها commit نشود**.

## 📝 یادداشت‌های مهم برای agentهای بعدی

### برای Scraper (task-01):
- قبل از شروع، [`04-State/decisions.md`](decisions.md) را برای URL تأییدشده بررسی کن.
- اگر URL تأیید نشده، متوقف شو و در [`issues.md`](issues.md) ثبت کن.
- **۶ سال** استخراج کن (۱۴۰۰ تا ۱۴۰۵). سال ۱۴۰۵ partial است.

### برای ETL Engineer (task-03):
- ۶ سال رو در Parquet ذخیره کن.
- فایل `_dataset-metadata.json` با `months_available_1405` بساز.

### برای Analyst (task-10/11/12):
- `task-10`: **حلقه کامل** روی تمام HS × تمام کشورها. هیچ فیلتری اعمال نکن.
- `task-11`: ۷ دسته روند را با Mann-Kendall تأیید کن.
- `task-12`: نمره‌دهی با وزن‌های Decision-009.

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
