---
folder: 03-Recipes
type: moc
last_updated: 1405-06-15
---

# 📚 MOC دستورالعمل‌ها (Recipes Map of Content)

این پوشه شامل **دستورالعمل‌های گام‌به‌گام (SOP)** برای کارهای تکرارپذیر است. هر recipe را قبل از شروع کار مرتبط بخوانید.

---

## فهرست دستورالعمل‌ها

| ID | عنوان | نقش مرتبط | فایل |
|----|-------|-----------|------|
| `recipe-01` | استخراج داده از گمرک (۶ سال) | Scraper | [recipe-01-scrape-customs.md](recipe-01-scrape-customs.md) |
| `recipe-02` | نرمال‌سازی و ETL | ETL Engineer | [recipe-02-normalize-data.md](recipe-02-normalize-data.md) |
| `recipe-03` | اجرای تحلیل (کشور + تعرفه + روند + کاندیدها) | Analyst | [recipe-03-run-analysis.md](recipe-03-run-analysis.md) |
| `recipe-04` | چک‌لیست QA | QA Validator | [recipe-04-qa-checklist.md](recipe-04-qa-checklist.md) |
| `recipe-05` | ساخت فایل Excel | ETL Engineer | [recipe-05-export-excel.md](recipe-05-export-excel.md) |
| `recipe-06` | نوشتن یادداشت Obsidian | Vault Writer | [recipe-06-write-obsidian-notes.md](recipe-06-write-obsidian-notes.md) |
| `recipe-07` | انتشار در GitHub | Git Publisher | [recipe-07-publish-github.md](recipe-07-publish-github.md) |
| `recipe-08` | به‌روزرسانی وضعیت (state) | همه | [recipe-08-update-state.md](recipe-08-update-state.md) |
| **`recipe-09`** | **متدولوژی طبقه‌بندی روند و رتبه‌بندی کاندیدها** | Analyst | [recipe-09-trend-classification.md](recipe-09-trend-classification.md) |

---

## اصول مشترک همه Recipes

1. **ترتیب‌محور**: مراحل به ترتیب اجرا می‌شوند.
2. **قابل تکرار**: هر بار با همان نتیجه.
3. **دارای verification**: هر مرحله یک چک تأیید دارد.
4. **دارای rollback**: اگر خطا خورد، چطور برگردیم.
5. **دارای log**: در `04-State/progress.md` ثبت می‌شود.

---

## مراجع

- [/01-Tasks/_MOC](../01-Tasks/_MOC.md)
- [/02-Prompts/_MOC](../02-Prompts/_MOC.md)
- [/04-State/STATUS](../04-State/STATUS.md)
