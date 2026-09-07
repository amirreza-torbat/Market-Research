---
type: template
template_for: task-note
last_updated: 1405-06-15
---

# قالب یادداشت تسک (Task)

> این قالب را برای ساخت تسک جدید در `01-Tasks/` استفاده کنید.
> نام فایل: `task-NN-short-slug.md`.

---

```markdown
---
type: task
task_id: task-NN
title: عنوان کوتاه تسک
status: pending
assignee: role
created: YYYY-MM-DD
updated: YYYY-MM-DD
depends_on: [task-XX]
blocks: [task-YY]
estimated_effort: N day(s)
---

# task-NN — عنوان تسک

## 🎯 هدف
[۱-۲ جمله — چرا این تسک]

## 📋 شرح کار

### مرحله ۱: ...
- ...

### مرحله ۲: ...
- ...

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [ ] ...
- [ ] ...
- [ ] commit با پیام `type(scope): task-NN ...`

## 📦 خروجی‌ها
- `path/to/output1`
- `path/to/output2`

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-role.md`](../02-Prompts/prompt-role.md)
- [`03-Recipes/recipe-NN-slug.md`](../03-Recipes/recipe-NN-slug.md)

## 🔗 وابستگی‌ها
- [[task-XX-dependency]]
- بلاک‌کننده [[task-YY-blocked]]
```
