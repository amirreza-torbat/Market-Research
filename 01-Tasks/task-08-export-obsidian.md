---
type: task
task_id: task-08
title: خروجی یادداشت‌های Obsidian
status: in-progress
assignee: vault-writer
created: 1405-06-15
updated: 1405-06-25
depends_on: [task-06]
blocks: [task-09]
estimated_effort: 1 day
---

# task-08 — خروجی نهایی یادداشت‌های Obsidian

## 🎯 هدف
ساخت یادداشت‌های نهایی خلاصه، فهرست و گزارش اجرایی برای مطالعه کاربر در Obsidian. یادداشت‌های جزئی‌تر در `task-04` و `task-05` ساخته شده‌اند، این تسک آن‌ها را به یک گزارش منسجم تبدیل می‌کند.

## 📋 شرح کار

### ۱. یادداشت گزارش اجرایی
ساخت `06-Analysis/executive-summary.md`:
- خلاصه یافته‌های کلیدی (حداقل ۵۰۰ کلمه).
- Top 10 کشور با رشد.
- Top 10 HS Code با رشد.
- توصیه‌های کلی.
- backlink به همه تحلیل‌های مرتبط.

### ۲. یادداشت روش‌شناسی
ساخت `06-Analysis/methodology.md`:
- توضیح منابع داده.
- توضیح مدل داده.
- توضیح شاخص‌ها (CAGR, percent_change, ...).
- توضیح دقت و تلورانس.
- محدودیت‌ها.

### ۳. به‌روزرسانی MOCها
- `06-Analysis/_MOC.md` ساخته شود (فهرست همه یادداشت‌های تحلیلی).
- `_MOC.md` هر پوشه به‌روزرسانی شود.

### ۴. یادداشت یافته‌های کلیدی
ساخت `06-Analysis/key-findings.md`:
- یافته ۱: بزرگ‌ترین رشد (کشور و HS Code).
- یافته ۲: روند منطقه‌ای (مثلاً کشورهای همسایه).
- یافته ۳: روند محصولی (مثلاً پتروشیمی، کشاورزی).
- هر یافته با backlink به یادداشت تحلیلی.

### ۵. ایندکس نهایی
ساخت `06-Analysis/_index.md`:
- درختی از همه یادداشت‌ها.
- مرتب‌شده بر اساس موضوع (کشور، HS Code، خلاصه).

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [ ] `06-Analysis/executive-summary.md` (حداقل ۵۰۰ کلمه).
- [ ] `06-Analysis/methodology.md` کامل.
- [ ] `06-Analysis/key-findings.md` با حداقل ۳ یافته.
- [ ] `06-Analysis/_MOC.md` و `06-Analysis/_index.md` ساخته شوند.
- [ ] همه یادداشت‌های `task-04` و `task-05` در `_MOC.md` فهرست شوند.
- [ ] commit با پیام `docs(vault): task-08 final obsidian notes`.

## 📦 خروجی‌ها
- `06-Analysis/executive-summary.md`
- `06-Analysis/methodology.md`
- `06-Analysis/key-findings.md`
- `06-Analysis/_MOC.md`
- `06-Analysis/_index.md`

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-vault-writer.md`](../02-Prompts/prompt-vault-writer.md)
- [`03-Recipes/recipe-06-write-obsidian-notes.md`](../03-Recipes/recipe-06-write-obsidian-notes.md)

## 🔗 وابستگی‌ها
- [[task-06-qa-validate]]
- بلاک‌کننده [[task-09-publish-github]]
- موازی با [[task-07-export-excel]]
