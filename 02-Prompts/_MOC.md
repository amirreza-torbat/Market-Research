---
folder: 02-Prompts
type: moc
last_updated: 1405-06-15
---

# 🗣️ MOC پرامپت‌ها (Prompts Map of Content)

این پوشه شامل پرامپت‌های آماده برای فراخوانی هر نقش agent است. هر پرامپت **خودکفا** است و شامل همه چیزهایی است که agent باید بداند.

---

## فهرست پرامپت‌ها

| نقش | فایل | تسک‌های مرتبط |
|-----|------|---------------|
| Scraper | [prompt-scraper.md](prompt-scraper.md) | `task-01`, `task-02` |
| ETL Engineer | [prompt-etl-engineer.md](prompt-etl-engineer.md) | `task-03`, `task-07` |
| Analyst | [prompt-analyst.md](prompt-analyst.md) | `task-04`, `task-05` |
| QA Validator | [prompt-qa-validator.md](prompt-qa-validator.md) | `task-06` |
| Vault Writer | [prompt-vault-writer.md](prompt-vault-writer.md) | `task-00`, `task-08` |
| Git Publisher | [prompt-git-publisher.md](prompt-git-publisher.md) | `task-09` |

---

## نحوه استفاده

### برای انسان (human agent)
1. فایل پرامپت نقش خودت را باز کن.
2. مطالعه کن.
3. تسک مرتبط در `01-Tasks/` را باز کن.
4. شروع به کار کن.

### برای AI agent (مثلاً در محیط Cursor یا Claude Code)
1. پرامپت نقش را به‌عنوان system prompt یا اولین user message قرار بده.
2. تسک مرتبط را به‌عنوان پیام کاربر بده.
3. agent به‌صورت خودکار شروع به کار می‌کند.

### مثال

```bash
# اجرای Scraper agent
claude-code --system-prompt-file 02-Prompts/prompt-scraper.md \
            --task-file 01-Tasks/task-01-scrape-list.md
```

---

## اصول مشترک همه پرامپت‌ها

1. **خودکفایی**: پرامپت بدون نیاز به توضیحات اضافی قابل اجراست.
2. **ارجاع به Vault**: هر پرامپت به فایل‌های مرجع در Vault لینک دارد.
3. **فرمت YAML frontmatter**: برای metadata.
4. **واضح بودن نقش**: نقش و وظایف مشخص است.
5. **خط قرمز دقت**: همه پرامپت‌ها به خطای < 0.0001٪ اشاره دارند.

---

## مراجع

- [/01-Tasks/_MOC](../01-Tasks/_MOC.md)
- [/03-Recipes/_MOC](../03-Recipes/_MOC.md)
- [/00-Overview/conventions](../00-Overview/conventions.md)
