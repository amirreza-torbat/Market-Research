---
folder: 04-State
type: qa-report
status: pending
last_updated: 1405-06-15 12:00
---

# 🧪 گزارش QA (Placeholder)

> این فایل در `task-06` توسط QA Validator Agent پر می‌شود. تا آن زمان، این یک placeholder است.

## وضعیت فعلی

🟡 **در انتظار اجرای task-06**

گزارش QA پس از تکمیل `task-04` و `task-05` و اجرای `task-06` تولید خواهد شد.

## تست‌های مورد انتظار

### تست‌های عددی
- [ ] Test 1.1: مجموع value (raw vs processed) — تلورانس < 0.0001٪
- [ ] Test 1.2: مجموع value (analysis vs parquet) — تلورانس < 0.0001٪
- [ ] Test 1.3: مجموع value (analysis-by-tariff vs parquet) — تلورانس < 0.0001٪
- [ ] Test 1.4: مجموع value (analysis-by-tariff-country vs parquet) — تلورانس < 0.0001٪

### تست‌های کامل‌بودن
- [ ] Test 2.1: ۵ سال موجود (۱۴۰۰ تا ۱۴۰۴)
- [ ] Test 2.2: تعداد کشورها > 100
- [ ] Test 2.3: تعداد HS Codeها > 1000
- [ ] Test 2.4: هیچ null در فیلدهای کلیدی

### تست‌های فرمت
- [ ] Test 3.1: HS Code فرمت `HH.HH.HH.HH`
- [ ] Test 3.2: Country ISO فرمت `[A-Z]{2}`
- [ ] Test 3.3: export_value_usd > 0
- [ ] Test 3.4: export_weight_kg > 0

### تست‌های تحلیل
- [ ] Test 4.1: همه کشورهای Parquet در analysis-by-country
- [ ] Test 4.2: همه HS Codeهای Parquet در analysis-by-tariff
- [ ] Test 4.3: همه جفت‌های (HS, Country) در analysis-by-tariff-country

### تست‌های متقابل (Mirror Data)
- [ ] Test 5.1: مقایسه با UN Comtrade (در صورت دسترسی)

---

> وقتی `task-06` اجرا شد، این فایل با گزارش واقعی جایگزین می‌شود.
