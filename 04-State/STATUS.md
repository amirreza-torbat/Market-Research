---
folder: 04-State
type: status
last_updated: 1405-06-15 12:00
---

# 📊 وضعیت پروژه (STATUS)

> **این فایل نقطه شروع هر agent است.** قبل از هر کاری این فایل را بخوانید.

## 🎯 وضعیت کلی

| فیلد | مقدار |
|------|-------|
| **وضعیت کلی** | 🟡 `in-progress` |
| **تسک فعلی** | `task-00` (راه‌اندازی) — در حال تکمیل |
| **agent مسئول فعلی** | `vault-writer` |
| **آخرین به‌روزرسانی** | ۱۴۰۵-۰۶-۱۵ ۱۲:۰۰ |
| **بلوک‌ها** | — |
| **قدم بعدی** | تأیید URL گمرک توسط کاربر، سپس شروع `task-01` |

## 📋 وضعیت تسک‌ها

| Task ID | عنوان | وضعیت | Assignee | به‌روزرسانی |
|---------|-------|-------|----------|--------------|
| `task-00` | راه‌اندازی Vault | 🟢 `done` | vault-writer | 1405-06-15 |
| `task-01` | استخراج فهرست صادرات | ⬜ `pending` | — | — |
| `task-02` | استخراج جزئیات | ⬜ `pending` | — | — |
| `task-03` | نرمال‌سازی ETL | ⬜ `pending` | — | — |
| `task-04` | تحلیل به تفکیک کشور | ⬜ `pending` | — | — |
| `task-05` | تحلیل به تفکیک تعرفه | ⬜ `pending` | — | — |
| `task-06` | اعتبارسنجی QA | ⬜ `pending` | — | — |
| `task-07` | خروجی Excel | ⬜ `pending` | — | — |
| `task-08` | خروجی Obsidian | ⬜ `pending` | — | — |
| `task-09` | انتشار GitHub | ⬜ `pending` | — | — |

**راهنما**: ⬜ pending → 🟡 in-progress → 🟠 review → 🟢 done | 🔴 blocked

## 🚦 مسیر فعلی

```
[task-00: setup] ✅ DONE
       ↓
[task-01: scrape-list] ⬜ READY TO START (پس از تأیید URL)
       ↓
[task-02: scrape-detail] ⬜
       ↓
[task-03: etl-normalize] ⬜
       ↓
   ┌────────────┴────────────┐
   ↓                          ↓
[task-04: by-country]    [task-05: by-tariff]
   ↓                          ↓
   └────────────┬─────────────┘
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

### برای همه agentها:
- قبل از شروع، این فایل را بخوان.
- بعد از پایان کار، این فایل را به‌روز کن (طبق [`recipe-08`](../03-Recipes/recipe-08-update-state.md)).
- اگر مسأله‌ای یافتی، در [`issues.md`](issues.md) ثبت کن.

## 🔗 مراجع

- [/01-Tasks/_MOC](../01-Tasks/_MOC.md)
- [/04-State/progress](progress.md)
- [/04-State/issues](issues.md)
- [/04-State/decisions](decisions.md)
- [/00-Overview/project-overview](../00-Overview/project-overview.md)
