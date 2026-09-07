---
folder: 03-Recipes
type: recipe
recipe_id: recipe-07
title: انتشار در GitHub
related_tasks: [task-09]
last_updated: 1405-06-15
---

# 📖 Recipe-07 — انتشار در GitHub

> **نقش**: Git Publisher Agent
> **تسک مرتبط**: [[task-09-publish-github]]

## هدف
merge نهایی، ساخت release، تحویل به کاربر.

## پیش‌نیازها
- [ ] همه تسک‌های `task-00` تا `task-08` در `done` باشند.
- [ ] `04-State/qa-report.md`: pass.
- [ ] `gh` CLI نصب و auth شده.
- [ ] دسترسی push به مخزن.

## مراحل

### مرحله ۱: تأیید نهایی (۳۰ دقیقه)
1. مطالعه `04-State/STATUS.md` — همه تسک‌ها باید `done` باشند.
2. مطالعه `04-State/qa-report.md` — باید pass.
3. اگر issue باز است، رفع کن یا به تأیید کاربر برسان.

### مرحله ۲: merge PRها (۱ ساعت)
1. فهرست همه PRهای باز:
   ```bash
   gh pr list --state open
   ```
2. برای هر PR:
   - بررسی CI (در صورت وجود).
   - review (در صورت نیاز).
   - merge با squash:
     ```bash
     gh pr merge <PR-NUM> --squash --delete-branch
     ```

### مرحله ۳: به‌روزرسانی README (۳۰ دقیقه)
1. اضافه کردن badge وضعیت:
   ```markdown
   ![Status](https://img.shields.io/badge/status-done-brightgreen)
   ![QA](https://img.shields.io/badge/QA-pass-brightgreen)
   ```
2. اضافه کردن لینک به release (به‌زودی).
3. اضافه کردن آمار کلیدی.

### مرحله ۴: ساخت tag (۱۵ دقیقه)
```bash
TODAY=$(date +%Y%m%d)
git tag -a "v1.0.0-${TODAY}" -m "Release v1.0.0 — تحلیل صادرات ایران ۱۴۰۰-۱۴۰۴"
git push origin "v1.0.0-${TODAY}"
```

### مرحله ۵: ساخت Release (۳۰ دقیقه)
```bash
TODAY=$(date +%Y%m%d)
gh release create "v1.0.0-${TODAY}" \
  --title "Release v1.0.0 — تحلیل صادرات ایران ۱۴۰۰-۱۴۰۴" \
  --notes-file 07-Exports/release-notes.md \
  07-Exports/iran-exports-1400-1404-*.xlsx
```

**نکته**: فایل `07-Exports/release-notes.md` را با قالب در پرامپت Git Publisher بساز.

### مرحله ۶: بستن پروژه (۳۰ دقیقه)
1. در `04-State/STATUS.md`:
   - `overall_status`: `done`.
   - `current_task`: `none`.
   - تاریخ پایان.
2. در `04-State/closure.md`:
   ```markdown
   # بستن پروژه
   
   ## خلاصه
   - تاریخ شروع: شهریور ۱۴۰۵
   - تاریخ پایان: [تاریخ]
   - تسک‌های انجام‌شده: ۱۰ از ۱۰
   - تلورانس نهایی: 0.0000X%
   
   ## درس‌آموخته‌ها
   - ...
   
   ## مسائل باز (در صورت وجود)
   - ...
   
   ## پیشنهادها برای پروژه‌های بعدی
   - ...
   ```

### مرحله ۷: commit و push نهایی
```bash
git add .
git commit -m "chore: project closure — v1.0.0"
git push origin main
```

### مرحله ۸: تحویل به کاربر
1. لینک release: `https://github.com/amirreza-torbat/Market-Research/releases/tag/v1.0.0-YYYYMMDD`
2. در IM، لینک و فایل Excel را بفرست.
3. خلاصه یافته‌های کلیدی را به کاربر بگو.

## مدیریت خطا

### اگر CI fail شد:
- در `04-State/issues.md` ثبت کن.
- ریشه‌یابی کن.
- اصلاح کن و دوباره push.

### اگر merge conflict داشت:
- شاخه را rebase کن روی `main`.
- conflict را حل کن.
- push کن.

## مراجع
- [[task-09-publish-github]]
- [[prompt-git-publisher]]
- [[conventions]]
