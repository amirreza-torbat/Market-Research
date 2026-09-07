---
type: task
task_id: task-09
title: انتشار در GitHub
status: pending
assignee: git-publisher
created: 1405-06-15
updated: 1405-06-15
depends_on: [task-07, task-08]
blocks: []
estimated_effort: 0.5 day
---

# task-09 — انتشار در GitHub و تحویل نهایی

## 🎯 هدف
merge کردن همه PRهای باز، ساخت release، و تحویل نهایی به کاربر.

## 📋 شرح کار

### ۱. تأیید وضعیت همه تسک‌ها
- همه تسک‌های `task-00` تا `task-08` باید `done` باشند.
- `04-State/STATUS.md` باید نهایی شده باشد.
- `04-State/qa-report.md` باید pass باشد.

### ۲. Merge PRها
- همه شاخه‌های `feature/task-NN-*` به `main` merge شوند.
- حل conflict در صورت وجود.

### ۳. ساخت Release
- tag با فرمت `v1.0.0-YYYYMMDD`.
- release notes شامل:
  - خلاصه پروژه.
  - آمار (تعداد رکوردها، کشورها، HS Codeها).
  - لینک به فایل Excel در `07-Exports/`.
  - لینک به `06-Analysis/executive-summary.md`.

### ۴. به‌روزرسانی README
- اضافه کردن badge وضعیت.
- لینک به release.
- لینک به گزارش اجرایی.

### ۵. تحویل به کاربر
- ارسال لینک release به کاربر در IM.
- ارسال فایل Excel به کاربر (در صورت درخواست).

### ۶. بستن پروژه
- `04-State/STATUS.md` به `done` تغییر کند.
- یادداشت `04-State/closure.md` با درس‌آموخته‌ها.

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [ ] همه تسک‌ها `done`.
- [ ] همه PRها merge شده.
- [ ] tag `v1.0.0-YYYYMMDD` ساخته شده.
- [ ] release notes کامل.
- [ ] README به‌روزرسانی شده.
- [ ] `04-State/STATUS.md` نهایی.
- [ ] فایل Excel به کاربر تحویل داده شده (در IM یا در مخزن).

## 📦 خروجی‌ها
- Release در GitHub
- `04-State/closure.md`

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-git-publisher.md`](../02-Prompts/prompt-git-publisher.md)

## 🔗 وابستگی‌ها
- [[task-07-export-excel]]
- [[task-08-export-obsidian]]
