---
folder: 04-State
type: progress-log
last_updated: 1405-06-23 12:40
---

# 📝 لاگ پیشرفت (Progress Log)

> این فایل به‌صورت append-only است. هر agent هر مایل‌ستون را در اینجا ثبت می‌کند.

---

## [1405-06-15 12:00] task-00 — vault-writer
- شروع راه‌اندازی Vault.
- کلون کردن مخزن (خالی بود).
- ساخت ساختار پوشه‌ها:
  - `00-Overview/`
  - `01-Tasks/`
  - `02-Prompts/`
  - `03-Recipes/`
  - `04-State/`
  - `05-Data/raw/`, `05-Data/interim/`, `05-Data/processed/`
  - `06-Analysis/by-country/`, `06-Analysis/by-tariff/`
  - `07-Exports/`
  - `_templates/`
  - `.obsidian/`

## [1405-06-15 12:15] task-00 — vault-writer
- نوشتن `README.md` ریشه.
- نوشتن فایل‌های `00-Overview/`:
  - `project-overview.md`
  - `conventions.md`
  - `data-sources.md`
  - `glossary.md`

## [1405-06-15 12:30] task-00 — vault-writer
- نوشتن `_MOC.md` برای `01-Tasks/`.
- نوشتن فایل‌های تسک:
  - `task-00-setup.md` (done)
  - `task-01-scrape-list.md`
  - `task-02-scrape-detail.md`
  - `task-03-etl-normalize.md`
  - `task-04-analysis-country.md`
  - `task-05-analysis-tariff.md`
  - `task-06-qa-validate.md`
  - `task-07-export-excel.md`
  - `task-08-export-obsidian.md`
  - `task-09-publish-github.md`

## [1405-06-15 12:45] task-00 — vault-writer
- نوشتن `_MOC.md` برای `02-Prompts/`.
- نوشتن پرامپت‌ها:
  - `prompt-scraper.md`
  - `prompt-etl-engineer.md`
  - `prompt-analyst.md`
  - `prompt-qa-validator.md`
  - `prompt-vault-writer.md`
  - `prompt-git-publisher.md`

## [1405-06-15 13:00] task-00 — vault-writer
- نوشتن `_MOC.md` برای `03-Recipes/`.
- نوشتن دستورالعمل‌ها:
  - `recipe-01-scrape-customs.md`
  - `recipe-02-normalize-data.md`
  - `recipe-03-run-analysis.md`
  - `recipe-04-qa-checklist.md`
  - `recipe-05-export-excel.md`
  - `recipe-06-write-obsidian-notes.md`
  - `recipe-07-publish-github.md`
  - `recipe-08-update-state.md`

## [1405-06-15 13:15] task-00 — vault-writer
- نوشتن فایل‌های state:
  - `STATUS.md`
  - `progress.md` (این فایل)
  - `issues.md`
  - `decisions.md`
  - `qa-report.md` (placeholder)
  - `closure.md` (placeholder)

## [1405-06-15 13:30] task-00 — vault-writer
- ساخت قالب‌ها در `_templates/`:
  - `note-analysis-country.md`
  - `note-analysis-tariff.md`
  - `task-template.md`
- ساخت `.gitignore`.
- ساخت `.obsidian/app.json` و `.obsidian/appearance.json`.
- commit اولیه.
- push به GitHub.

## [1405-06-15 13:45] task-00 — vault-writer
- ✅ **task-00 تکمیل شد.**
- وضعیت در `STATUS.md` به `done` تغییر کرد.
- آماده برای شروع `task-01` پس از تأیید URL توسط کاربر.

---

## [1405-06-15 14:00] task-00 (ادامه) — vault-writer
- کاربر درخواست گسترش پروژه داد:
  - بازه از ۵ سال به **۶ سال** (۱۴۰۰ تا ۱۴۰۵، سال جاری partial).
  - **حلقه کامل** روی تمام HS Codeها × تمام کشورها (نه فقط Top 50).
  - طبقه‌بندی روند ۶ ساله به ۷ دسته.
  - رتبه‌بندی محصولات کاندید صادرات.
- به‌روزرسانی‌ها:
  - `00-Overview/project-overview.md`: ۶ سال، تمام HS Codeها، اضافه شدن تحلیل روند و کاندیدها.
  - `00-Overview/conventions.md`: بخش ۵ جدید با تاکسونومی ۷ دسته‌ای، شاخص‌های آماری، نمره‌دهی export_score. شماره‌گذاری بخش‌های ۵ تا ۹ به‌روز شد.
  - `00-Overview/glossary.md`: اصطلاحات جدید (Mann-Kendall, OLS, R², CV, YTD, Trend, Volatility).
  - `00-Overview/data-sources.md`: نکته سال partial ۱۴۰۵.
  - `01-Tasks/task-01-scrape-list.md`: ۶ سال، با مرحله ۴.۵ برای استخراج partial ۱۴۰۵.
  - `01-Tasks/task-03-etl-normalize.md`: ۶ سال، فایل `_dataset-metadata.json`.
  - `01-Tasks/task-04-analysis-country.md`: شاخص‌های ۶ ساله (cagr_5y، cagr_6y).
  - `01-Tasks/task-05-analysis-tariff.md`: ۶ سال، لینک به task-10 برای تحلیل کامل.
  - `01-Tasks/task-06-qa-validate.md`: وابستگی به task-10/11/12، تست‌های جدید.
  - `01-Tasks/task-07-export-excel.md`: ۱۸ شیت (۶ شیت جدید برای trend/classification/candidates).
  - `01-Tasks/task-09-publish-github.md`: تسک‌های ۰۰ تا ۱۲.
  - **`01-Tasks/task-10-trend-analysis.md`**: جدید — حلقه کامل تحلیل روند.
  - **`01-Tasks/task-11-trend-classification.md`**: جدید — طبقه‌بندی ۷ دسته.
  - **`01-Tasks/task-12-export-candidates.md`**: جدید — رتبه‌بندی کاندیدها.
  - `01-Tasks/_MOC.md`: نمودار وابستگی جدید با task-10/11/12.
  - `02-Prompts/prompt-scraper.md`: ۶ سال.
  - `02-Prompts/prompt-analyst.md`: اهداف task-10/11/12، شاخص‌های آماری، الگوریتم Mann-Kendall، تابع classify_trend و compute_export_score.
  - `03-Recipes/recipe-01-scrape-customs.md`: مرحله ۴.۵ برای ۱۴۰۵ partial.
  - `03-Recipes/recipe-03-run-analysis.md`: بخش‌های C، D، E برای task-10/11/12.
  - **`03-Recipes/recipe-09-trend-classification.md`**: جدید — متدولوژی کامل طبقه‌بندی و رتبه‌بندی.
  - `03-Recipes/_MOC.md`: اضافه شدن recipe-09.
  - `04-State/decisions.md`: تصمیم‌های ۰۰۷ تا ۰۱۰ (full-loop، taxonomy، weights، thresholds).
  - `04-State/STATUS.md`: به‌روزرسانی کامل با تسک‌های جدید.
- commit و push انجام شد.
- ✅ **به‌روزرسانی Vault تکمیل شد.**
- آماده برای شروع `task-01` پس از تأیید URL توسط کاربر.

---

> **قدم بعدی**: Scraper agent باید `task-01` را شروع کند (پس از تأیید URL گمرک در `decisions.md`).

## [2026-09-07 15:56] task-01 — scraper
- سال 1400 (aggregate): 2662 سطر | totals={'usd': Decimal('48169252889'), 'weight': Decimal('122402988205')}

## [2026-09-07 15:57] task-01 — scraper
- سال 1401 (aggregate): 2546 سطر | totals={'usd': Decimal('52999955953'), 'weight': Decimal('122045471683')}

## [2026-09-07 15:57] task-01 — scraper
- سال 1402 (aggregate): 2566 سطر | totals={'usd': Decimal('49474253576'), 'weight': Decimal('136405847970')}

## [2026-09-07 15:57] task-01 — scraper
- سال 1403 (aggregate): 2541 سطر | totals={'usd': Decimal('57807603060'), 'weight': Decimal('151966807998')}

## [2026-09-07 15:57] task-01 — scraper
- سال 1404 (aggregate): 2471 سطر | totals={'usd': Decimal('45009201052'), 'weight': Decimal('130032168748')}

## [2026-09-07 15:57] task-01 — scraper
- سال 1405 (aggregate): 0 سطر | totals={'usd': Decimal('0'), 'weight': Decimal('0')}

## [2026-09-07 15:57] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 15:57] task-01 — scraper
- شروع استخراج سال 1400 (تا امروز 0 رکورد در checkpoint).

## [2026-09-07 15:58] task-01 — scraper
- سال 1400: 1724 رکورد یکتا | فصل 01 → 1724 رکورد | dup=0

## [2026-09-07 15:59] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 15:59] task-01 — scraper
- شروع استخراج سال 1400 (resume: 1724 رکورد از فایل‌های خام بازپارس شد | dup=0).

## [2026-09-07 15:59] task-01 — scraper
- سال 1400: 1724 رکورد یکتا | فصل 01 → 1724 رکورد | dup=1724

## [2026-09-07 16:01] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 16:01] task-01 — scraper
- شروع استخراج سال 1400 (resume: 1724 رکورد از فایل‌های خام بازپارس شد | dup=0).

## [2026-09-07 16:07] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 16:16] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 16:23] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 16:30] task-01 — scraper
- سال 1400: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 16:30] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 16:30] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 16:37] task-01 — scraper
- سال 1400: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 16:37] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 16:38] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 16:45] task-01 — scraper
- سال 1400: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 16:45] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 16:46] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 16:52] task-01 — scraper
- سال 1400: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 16:52] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 16:53] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 17:00] task-01 — scraper
- سال 1400: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 17:00] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 17:00] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 17:08] task-01 — scraper
- سال 1400: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 17:08] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 17:08] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 17:10] task-01 — scraper
- سال 1400 کامل شد: 162333 رکورد یکتا | dup=42391 | ماه‌ها=['1', '10', '11', '12', '2', '3', '4', '5', '6', '7', '8', '9'] | CSV=exports_1400_raw.csv

## [2026-09-07 17:10] task-01 — scraper
- پایان فاز جزئیات task-01 — همه سال‌ها کامل شد.

## [2026-09-07 17:11] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 17:17] task-01 — scraper
- سال 1401: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 17:17] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 17:17] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 17:24] task-01 — scraper
- سال 1401: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 17:24] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 17:24] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 17:31] task-01 — scraper
- سال 1401: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 17:31] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 17:31] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 17:38] task-01 — scraper
- سال 1401: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 17:38] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 17:39] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 17:45] task-01 — scraper
- سال 1401: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 17:45] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 17:46] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 17:52] task-01 — scraper
- سال 1401: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 17:52] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 17:53] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 17:55] task-01 — scraper
- سال 1401 کامل شد: 169183 رکورد یکتا | dup=48734 | ماه‌ها=['1', '10', '11', '12', '2', '3', '4', '5', '6', '7', '8', '9'] | CSV=exports_1401_raw.csv

## [2026-09-07 18:00] task-01 — scraper
- سال 1402: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 18:00] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 18:00] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 18:07] task-01 — scraper
- سال 1402: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 18:07] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 18:07] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 18:14] task-01 — scraper
- سال 1402: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 18:14] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 18:14] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 18:21] task-01 — scraper
- سال 1402: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 18:21] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 18:21] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 18:28] task-01 — scraper
- سال 1402: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 18:28] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 18:28] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 18:34] task-01 — scraper
- سال 1402: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 18:34] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 18:35] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 18:42] task-01 — scraper
- سال 1402: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 18:42] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 18:42] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 18:45] task-01 — scraper
- سال 1402 کامل شد: 183771 رکورد یکتا | dup=53414 | ماه‌ها=['1', '10', '11', '12', '2', '3', '4', '5', '6', '7', '8', '9'] | CSV=exports_1402_raw.csv

## [2026-09-07 18:48] task-01 — scraper
- سال 1403: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 18:48] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 18:49] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 18:55] task-01 — scraper
- سال 1403: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 18:55] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 18:55] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 19:02] task-01 — scraper
- سال 1403: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 19:02] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 19:02] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 19:03] task-01 — scraper
- سال 1403 کامل شد: 58247 رکورد یکتا | dup=17623 | ماه‌ها=بدون صفت ماه (1403/1404) | CSV=exports_1403_raw.csv

## [2026-09-07 19:08] task-01 — scraper
- سال 1404: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 19:08] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 19:09] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 19:15] task-01 — scraper
- سال 1404: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.

## [2026-09-07 19:15] task-01 — scraper
- اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).

## [2026-09-07 19:15] task-01 — scraper
- شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim

## [2026-09-07 19:17] task-01 — scraper
- سال 1404 کامل شد: 52861 رکورد یکتا | dup=14908 | ماه‌ها=بدون صفت ماه (1403/1404) | CSV=exports_1404_raw.csv

## [2026-09-07 19:17] task-01 — scraper
- پایان فاز جزئیات task-01 — همه سال‌ها کامل شد.

## [2026-09-07 19:25] task-01 — scraper (نهایی)
- ✅ فاز جزئیات کامل شد: ۹۹ فصل HS × ۵ سال (۱۴۰۰-۱۴۰۴)، صفر فصل شکسته، نرخ موفقیت fetch = ۱۰۰٪.
- رکوردهای یکتای جزئی: ۱۴۰۰=۱۶۲,۳۳۳ | ۱۴۰۱=۱۶۹,۱۸۳ | ۱۴۰۲=۱۸۳,۷۷۱ | ۱۴۰۳=۵۸,۲۴۷ | ۱۴۰۴=۵۲,۸۶۱ → مجموع ۶۲۶,۳۹۵.
- فاز تجمیعی: ۱۲,۷۸۶ سطر (گمرک × کشور) برای ۱۴۰۰-۱۴۰۴ + تأیید فقدان ۱۴۰۵.
- ۱۴۰۰-۱۴۰۲ تفکیک ۱۲ ماه؛ ۱۴۰۳-۱۴۰۴ بدون صفت ماه (محدودیت منبع — Issue-006).
- months_available_1405 = 0 (منبع داده ۱۴۰۵ منتشر نکرده — Issue-007).
- QA: پوشش ارزشی جزئیات ≈ ۹۹.۹۳٪، صفر کلید تکراری، جمع سالانه همخوان با آمار رسمی.
- خروجی‌ها: exports_YYYY_raw.csv + exports_YYYY_aggregate.csv + _summary.md — آماده review.

## [2026-09-08 09:50] task-03 — etl-engineer
- شروع task-03 — نرمال‌سازی و ETL.
- شاخه `feature/task-03-etl` ساخته شد (بر پایه `origin/feature/task-01-scrape`).
- داده خام بررسی شد: ۶۲۶,۳۹۵ رکورد در ۵ سال، ۱۶۶ نام کشور فارسی، ۵۹۹۳ HS Code یکتا.
- Issue-006 تأیید شد: ۱۴۰۳/۱۴۰۴ ستون month کاملاً خالی (۱۱۱,۱۰۸ رکورد بدون ماه).
- Issue-007 تأیید شد: export_quantity کاملاً NULL.
- نگاشت ۱۶۶ نام فارسی کشور به ISO 3166-1 alpha-2 در `05-Data/processed/countries-mapping.csv`.
  - کدهای user-assigned برای موارد غیرکشوری: XO (سایر خارجی)، ZF (مناطق آزاد)، ZS (مناطق ویژه)، ZZ (نامشخص).
  - غلط املایی در منبع: "فيليپين" (با پ) اصلاح شد، "ناميبيا" به‌درستی نگاشت شد (NA توسط pandas به NaN تبدیل نمی‌شود با keep_default_na=False).

## [2026-09-08 09:50] task-03 — etl-engineer
- کلاس `ETLPipeline` در `scripts/etl_normalize.py` پیاده‌سازی شد.
- متدها: load_raw, clean (dedupe + dropna), normalize_country, normalize_hs_code, convert_to_decimal, normalize_month, validate_precision, save_parquet, build_reference_tables, save_metadata, write_validation_report.
- Decimal precision = 28، Parquet schema صریح با decimal128 برای مبالغ.

## [2026-09-08 09:50] task-03 — etl-engineer
- ETL اجرا شد: ۶۲۶,۳۹۵ رکورد پردازش (صفر تکراری، صفر NA حذف).
- ✅ تست دقت: تلورانس = ۰.۰۰۰۰۰۰۰۰۰۰ برای همه ۵ سال (دقت ۱۰۰٪، فراتر از آستانه ۰.۰۰۰۱٪).
- خروجی‌ها: exports_1400-1405.parquet (۱۵MB)، countries-mapping.csv، countries.csv، hs-codes.csv، _dataset-metadata.json، _validation-report.md.

## [2026-09-08 09:50] task-03 — etl-engineer (نهایی)
- ✅ اسکریپت تست مستقل `scripts/test_precision.py` نوشته و اجرا شد:
  - ۵/۵ سال PASS دقت (تلورانس = ۰)
  - صفر NULL در فیلدهای کلیدی (year, month, hs_code, country_iso2, value)
  - ۱۶۶ کشور (>۱۰۰)، ۵۹۹۳ HS Code (>۱۰۰۰)
  - Issue-006 به‌درستی مدیریت شد (۱۱۱,۱۰۸ رکورد بدون ماه فقط در ۱۴۰۳/۱۴۰۴)
  - همه HS Codeها در فرمت HH.HH.HH.HH
- آمار نهایی: sum_value_usd = ۲۵۳,۲۹۲,۹۴۰,۰۳۵ دلار | sum_weight = ۶۶۲,۸۰۱,۹۱۵,۹۹۴ کیلوگرم.
- Issues مستندسازی‌شده در metadata: ۰۰۵، ۰۰۶، ۰۰۷، ۰۰۸.
- آماده review.

## [2026-09-13 10:05] task-10 — analyst
- شروع task-10 — تحلیل جامع روند ۵ ساله (تمام HS × تمام کشورها).
- شاخه `feature/task-10-trend` ساخته شد (بر پایه `origin/feature/task-03-etl`).
- فایل‌های مرجع مطالعه شد: conventions (بخش ۴.۲.۲/۵/۵.۳)، recipe-09، prompt-analyst، decisions (002/007/008/010)، issues (005-008)، metadata و validation-report.
- تحلیل روی ۵ سال کامل (۱۴۰۰-۱۴۰۴) طبق Issue-008 — `cagr_6y` همیشه NULL.

## [2026-09-13 15:02] task-10 — analyst (تکمیل)
- **تکمیل task-10** — تحلیل جامع روند ۵ ساله، حلقه کامل بدون فیلتر.
- خروجی اصلی: `05-Data/processed/trend-analysis-5y.parquet` — **۵۰,۱۹۶ جفت (HS × Country) × ۲۱ ستون** (۳.۱MB، snappy).
- اسکریپت: `scripts/analyze_trend_5y.py` — aggregation exact در int64 (واحد 1e-4 USD)؛ CAGR/pct_change/multiplier با Decimal(prec 28)؛ slope/R²/MK(با tie correction)/CV/ثبات vectorized؛ اجرای کل ≈ ۲ ثانیه.
- آمار کلیدی: ۶۲۶,۳۹۵ رکورد → ۱۲۲,۱۶۲ ردیف سالانه → ۵۰,۱۹۶ جفت؛ ۹,۴۹۶ جفت با هر ۵ سال داده؛ ۱۲,۵۰۷ جفت با CAGR قابل محاسبه (۶,۴۸۵ رشد / ۶,۰۲۰ کاهش / ۲ ثابت).
- **تست دقت**: تلورانس = ۰.۰۰۰۰۰۰۰۰۰۰ برای جمع هر ۵ سال (هدف < 1e-6) — تست مستقل `scripts/test_trend_precision.py` با ۱۷ بررسی: **همه PASS**.
- گزارش: `trend-analysis-summary.md` — ۱۰ بخش: متدولوژی، آمار کلی، تست دقت، آمار توصیفی، توزیع CAGR + **هشدار آماری MK با n=5 (حداقل p≈0.0275)**، Top-10 CAGR (با فیلتر v1400≥100K$ طبق D-010)، Top-10 slope، پیش‌نمایش طبقات با برجسته‌ها، نکات کیفی + جغرافیا.
- پیش‌نمایش طبقات (آستانه‌های Decision-010، غیرانحصاری): strong_growth **۳۴۰** | moderate 20 | stable 535 | volatile 25,283 | declining 904 | emerging **۱,۶۸۶** | disappearing 1,593.
- اصلاح باگ واحد در حین کار: slope/mean_value/mean_recent_3y ابتدا در واحدهای int64 محاسبه شده بودند → به USD تبدیل شدند و خروجی regenerate شد (cv/r²/MK مقیاس‌ناوابسته بودند و درست ماندند).
- commit: `fd7c59c` روی شاخه `feature/task-10-trend` + push به origin.
- آماده review → سپس task-11 (طبقه‌بندی ۷ دسته با اولویت انحصاری).

## [2026-09-13 16:20] task-11 — analyst (تکمیل)
- **تکمیل task-11** — طبقه‌بندی روند ۷ دسته + ۳ فرعی + تجمیع HS + یادداشت‌های Top.
- شاخه `feature/task-11-classification` از `origin/feature/task-10-trend` ساخته شد.
- اسکریپت‌ها: `scripts/classify_trends.py` (طبقه‌بندی vectorized + تجمیع + اعتبارسنجی + گزارش) و `scripts/build_trend_notes.py` (یادداشت + نمودار).
- خروجی داده: `trend-classification.parquet` (۵۰,۱۹۶ × ۲۵) و `trend-classification-by-hs.parquet` (۵,۹۹۳ × ۲۶).
- توزیع دسته‌ها: strong_growth ۳۴۰ | moderate 20 | weak_growth ۳,۷۱۲ | stable ۲۹۶ | volatile ۴,۴۸۳ | declining ۸۱۷ | weak_decline ۲,۶۱۵ | emerging ۱,۶۸۶ | disappearing ۱,۸۱۵ | insufficient_data ۳۴,۴۱۲.
- توصیه اقدام: select 2,026 | monitor 3,732 | investigate 41,806 | avoid 2,632.
- اعتبارسنجی: همه PASS — بدون NULL، دسته‌ها معتبر، جمع value_1404 حفظ‌شده (<1e-9 نسبی)، جمع n_countries = 50,196.
- ۱۰۸ یادداشت Obsidian + ۱۰۲ نمودار یکتا در `06-Analysis/trend/` (30 strong + 18 moderate + 30 emerging + 30 declining؛ ۶ HS در دو دسته هم‌زمان).
- نمودار فارسی: matplotlib فاقد RTL → arabic_reshaper + python-bidi نصب و استفاده شد (فونت DejaVu Sans).
- **انحراف مستندشده از پرامپت**: انتخاب یادداشت‌ها با membership (n_<cat> > 0، رتبه‌بندی با ارزش دسته) به‌جای فیلتر dominant_trend — دلیل: ۵,۵۵۸ از ۵,۹۹۳ HS غالب insufficient_data؛ فیلتر پرامپت فقط ۳۷ یادداشت می‌داد (۰ برای moderate). ثبت در `_classification-summary.md` §۱۰.
- اصلاحات حین کار: باگ nonlocal در ماسک‌های طبقه‌بندی، نام‌گذاری ستون‌های crosstab، برچسب «توصیه» یادداشت‌ها، و کوتاه‌سازی عنوان frontmatter.
- محیط: venv بازسازی شده بود → pyarrow/matplotlib نصب مجدد شد.
- commit: `e20658d` + push به `origin/feature/task-11-classification`.
- آماده review → سپس task-12 (رتبه‌بندی کاندیدها ⭐ — با فیلتر membership طبق §۱۱ گزارش).

## [2026-09-14 11:30] task-12 — analyst (تکمیل)
- **تکمیل task-12 — رتبه‌بندی کاندیدهای صادرات ⭐ هدف نهایی پروژه**.
- شاخه `feature/task-12-ranking` از `origin/feature/task-11-classification` ساخته شد؛ venv بازسازی شد (pandas/pyarrow/matplotlib/seaborn/arabic-reshaper/python-bidi).
- اسکریپت‌ها: `scripts/rank_export_candidates.py` (فیلتر + نمره‌دهی + ریسک + ۳ گزارش + اعتبارسنجی) و `scripts/build_candidate_notes.py` (۵۰ یادداشت + ۵۰ نمودار).
- فیلتر membership طبق یافته task-11 §۱۱: ۵,۹۹۳ HS → ۱,۰۴۶ (membership) → ۶۱۴ (حجم>1M$) → **۵۷۴ کاندید** (≥۳ مقصد فعال) در ۶۰ فصل.
- خروجی داده: `export-candidates-ranked.parquet` (۵۷۴ × ۳۱ ستون، snappy) — rank/export_score/recommendation/risk_flags/trend_category/top_5_countries(+value)/تجزیه ۶ مولفه/n_significant_pairs.
- نمره‌دهی: وزن‌های Decision-009 (0.30 CAGR/0.20 slope/0.20 حجم/0.10 تنوع/0.10 ثبات/0.10 جریمه cv) + Min-Max؛ **cagr_5y جایگزین cagr_6y (Issue-008)** — مستند در گزارش §۱/§۹.
- **Top 5**: ۱) گاز طبیعی 27.11.21.90 (نمره 0.349، TR/IQ) ۲) میله‌های فولادی 72.14.99.00 (CAGR ۹۱۲٪) ۳) سنگ آهن هماتیت 26.01.11.90 (CAGR ۱۲۵۰٪) ۴) قیرنفت 27.13.20.00 (۴۷ مقصد) ۵) پروپان 27.11.12.90.
- **⚠️ یافته کالیبراسیون**: نمره‌ها [-۰.۰۳, ۰.۳۵] (هیچ کاندیدی در همه ۶ بُعد پیشتاز نیست) → آستانه‌های ثابت §۷ (select>0.7/monitor≥0.4) همه را «investigate» می‌کند؛ مستند در `_executive-ranking.md` §۵ + پیشنهاد بازکالیبراسیون با re-run (Pending-003/004). رتبه‌بندی خودش سیگنال قابل‌اقدام است.
- ریسک‌ها: volatile همه (cv جفت‌ها با صفر-پرکردن متورم) + concentrated ۱۷۹ + declining_recent ۳۶۸.
- گزارش‌ها: `_executive-ranking.md` (۹ بخش + نمودار Top 20) + `by-target-country.md` (۱۰۵ کشور؛ TR/IQ/AE/OM/CN صدر) + `chapter-country-matrix.md` + heatmap (فصل‌های ۲۷/۲۶/۳۹؛ AF پرتنوع ۶۳ جفت).
- ۵۰ یادداشت تفصیلی rank-NN-hs-*.md (خلاصه/شاخص‌ها/روند aggregated/تجزیه نمره/نمودار ۲پنلی/جدول ۵ ساله Top 15/تحلیل کیفی ۲۰۰+ کلمه/توصیه‌ها) + ۵۰ نمودار PNG فارسی (arabic_reshaper + bidi + DejaVu Sans).
- اعتبارسنجی: ۱۴/۱۴ PASS (recipe-09 §۹) + همه یادداشت‌ها سکشن‌های الزامی دارند.
- commit: `34fe090` + push به `origin/feature/task-12-ranking`.
- **زنجیره تحلیل پروژه کامل شد** — آماده review → task-06 (QA) → task-07/08 (خروجی‌ها) → task-09 (انتشار).

## [2026-09-14 12:40] task-12 بازکالیبراسیون — analyst (تکمیل)

- **محرک**: ۲ ایراد کاربر — (۱) فقط Top 5 در گزارش اجرایی، (۲) آستانه‌های ثابت 0.4/0.7 خارج از دامنه نمره‌ها [-0.03, 0.35] → همه ۵۷۴ کاندید «investigate».
- **بازکالیبراسیون صدکی** (شاخه feature/task-12-recalibrate): select ≥ p90=**0.103** → **۵۸** کاندید (۱۰.۱٪)؛ monitor ≥ p60=**0.061** → **۱۷۲** (۳۰.۰٪)؛ investigate → **۳۴۴** (۵۹.۹٪) — مطابق پیش‌بینی ~۵۷/~۱۷۲/~۳۴۵.
- **Excel ۷ شیتی**: `07-Exports/iran-export-candidates-500.xlsx` (۴۲۱KB) — All-Candidates (۵۷۴×۲۸) / Top-500 / Select / Monitor / By-Chapter (۶۰ فصل) / By-Target-Country (Top 30) / Methodology؛ color-scale روی export_score + رنگ وضعیت توصیه (سبز/کهربایی) + AutoFilter + Freeze + فرمت اعداد.
- **دقت شیت کشورها**: ارزش واقعی جفت‌های HS×Country از `trend-analysis-5y.parquet` (task-10) — پوشش join ۱۰۰٪ (۱,۲۴۳ جفت)؛ رفع تورش انتساب total_value_1404 کل HS به ۵ کشور.
- **گزارش اجرایی**: `_executive-ranking.md` بازنویسی — Top 50 (قبلاً Top 20) + جدول آستانه‌های صدکی + تحلیل کیفی Top 5 + Top 10 فصل + چرایی شکست آستانه ثابت.
- **Parquet**: `export-candidates-ranked-recalibrated.parquet` (۵۷۴×۳۴؛ +recommendation_old/+select_threshold/+monitor_threshold)؛ نمره‌ها و رتبه‌ها دست‌نخورده.
- **QA**: ۶۰/۶۰ بررسی معنایی PASS (بازمحاسبه مستقل شیت کشورها با صفر مغایرت) + validate/audit/scan ساختاری صفر خطا.
- commit + push به `origin/feature/task-12-recalibrate`.

## [2026-09-14 13:30] task-06 — qa-validator (تکمیل — PASS)

- **اعتبارسنجی نهایی کل pipeline (task-06) تکمیل شد — ۴۹/۴۹ تست PASS، تلورانس عددی ۰.۰۰۰۰۰۰۰۰۰۰٪**.
- شاخه `feature/task-06-qa` از `origin/feature/task-12-recalibrate` ساخته شد؛ فایل‌های مرجع (conventions §۴.۲، recipe-04، prompt-qa-validator، گزارش‌های task-03/10/11/12) مطالعه شد.
- اسکریپت `scripts/qa_validate_final.py` (۹ گروه تست، جمع‌ها با Decimal prec 28 — عیناً بدون float): سازگاری عددی raw→processed→trend→classification در هر ۵ سال (۱۵ تست، همه با تلورانس دقیق صفر) + membership candidates (۳) + کامل‌بودن ۵ سال/۱۶۶ کشور/۵,۹۹۳ HS/بدون null (۸) + فرمت HS/ISO/value/weight (۴) + سازگاری تحلیل شامل rank یکتا و توصیه‌های صدکی (۷) + Excel ۷ شیت با شمارش سطرها (۷) + مستندسازی Issues 005-008 در metadata (۵).
- **یافته ریشه‌یابی‌شده (شفاف)**: تست «>100k رکورد/سال» برای ۱۴۰۳/۱۴۰۴ false positive داد — آستانه recipe-04 قبل از کشف Issue-006 نوشته شده بود؛ این سال‌ها در منبع سطح-سال تجمیع‌اند و کامل‌بودن ارزش‌شان مستقلاً با تلورانس صفر (تست 1.4/1.5؛ ۱۴۰۳ = ۵۷.۷۸B$) تأیید شد → معیار به نسخه Issue-006-aware اصلاح و در Issue-009 ثبت شد. هیچ داده یا کد تسک‌های قبلی تغییر نکرد.
- خروجی‌ها: `04-State/qa-report.md` (جایگزین placeholder) + `05-Data/processed/qa-validation.json`.
- State به‌روز شد: STATUS.md (task-06 → review)، این فایل، `01-Tasks/_MOC.md`، `issues.md` (Issue-009)، فایل تسک task-06.
- commit + push به `origin/feature/task-06-qa`.
- **نتیجه: گات نهایی قبل از انتشار عبور شد — task-07/08/09 unblocked هستند.**

## [2026-09-14 16:30] task-07 — etl-engineer
- شروع task-07 — ساخت فایل Excel نهایی با ۱۸ شیت.
- شاخه `feature/task-07-excel` از `origin/feature/task-06-qa` ساخته شد.
- داده‌های ورودی بررسی شدند: exports (۶۲۶,۳۹۵ رکورد)، trend (۵۰,۱۹۶ جفت)، classification (۵۰,۱۹۶ جفت)، classification_by_hs (۵,۹۹۳ HS)، candidates (۵۷۴ کاندید).
- اسکریپت `scripts/build_final_excel.py` نوشته شد با تابع‌های مجز برای هر شیت.
- ۱۸ شیت به شرح زیر ساخته شد:
  1. Overview — معرفی + آمار + QA
  2. Data-All — نمونه ۱۰۰۰ رکورد
  3. By-Country-Summary — ۱۶۶ کشور
  4. By-Country-Top20-Growth — Top 20 رشد مطلق
  5. By-Country-Top20-CAGR — Top 20 CAGR
  6. By-Tariff-Summary — ۵٬۹۹۳ HS Code (همان ۵٬۹۹۳ + ۸۶۱ که توضیحات تکراری دارند)
  7. By-Tariff-Top50 — Top 50 HS Code
  8. By-Tariff-Country — ۲٬۰۴۶ رکورد با رشد قوی/متوسط/نوظهور
  9. Trend-All-HS-Country — ۵۰٬۱۹۶ جفت
  10. Trend-Classification — ۵۰٬۱۹۶ جفت با trend_category
  11. Trend-By-HS-Summary — ۵٬۹۹۳ HS Code تجمیعی
  12. Export-Candidates-Ranked — ۵۷۴ کاندید
  13. Candidates-Top20-Detail — Top 20 با ۳۴ ستون
  14. Chapter-Country-Matrix — ماتریس فصل × ۳۰ کشور برتر
  15. Charts-Country — نمودار Top 20 کشور
  16. Charts-Tariff — نمودار Top 20 HS Code
  17. Charts-Trend-Classification — PieChart توزیع دسته‌ها
  18. Charts-Export-Candidates — نمودار Top 20 کاندید

## [2026-09-14 16:30] task-07 — etl-engineer (نهایی)
- ✅ فایل `07-Exports/iran-exports-1400-1405-20260914.xlsx` ساخته شد (۱۲.۵۸ MB، زیر ۵۰ MB limit).
- ✅ اعتبارسنجی مستقل در `scripts/validate_excel.py` (فایل موقت — خارج از مخزن):
  - همه ۱۸ شیت موجودند
  - شیت ۰۹: ۵۰٬۱۹۶ جفت (مطابق انتظار)
  - شیت ۱۲: ۵۷۴ کاندید (مطابق انتظار)
  - ۴ نمودار در شیت‌های ۱۵-۱۸
  - Conditional formatting روی CAGR و export_score
  - Overview شامل آمار کامل و وضعیت QA (PASS)
- مشکل اصلاح‌شده:IllegalCharacterError به‌خاطر کاراکتر 0x0B در توضیحات HS (نخ‌های جراحی) — تابع `clean_value` اکنون همه control chars غیرمجاز را حذف می‌کند.
- آماده review کاربر.
