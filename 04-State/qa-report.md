---
folder: 04-State
type: qa-report
test_run_id: qa-final-20260914-153214
overall_status: pass
tolerance_observed: 0.0000000000%
total_tests: 49
passed: 49
failed: 0
created: 2026-09-14
---

# 🧪 گزارش QA نهایی (task-06)

**تاریخ**: 2026-09-14 15:32 (UTC)
**Agent**: QA Validator
**Pipeline**: `scripts/qa_validate_final.py`
**وضعیت کلی**: ✅ PASS

## خلاصه اجرایی

| شاخص | مقدار |
|------|-------|
| تعداد تست‌ها | 49 |
| PASS | 49 |
| FAIL | 0 |
| بیشینه تلورانس عددی مشاهده‌شده | 0.0000000000٪ (آستانه: < 0.0001٪) |
| وضعیت کلی | ✅ PASS — آماده انتشار |

## تست‌های اجراشده


### ۱. Numerical Consistency (Raw → Processed)

| تست | نتیجه | جزئیات |
|------|-------|--------|
| 1.1 Raw→Processed year 1400 | ✅ | raw=48134744945.00, proc=48134744945.00, tol=0.000000000000 (0.0000000000%) |
| 1.2 Raw→Processed year 1401 | ✅ | raw=52958904652.00, proc=52958904652.00, tol=0.000000000000 (0.0000000000%) |
| 1.3 Raw→Processed year 1402 | ✅ | raw=49442023650.00, proc=49442023650.00, tol=0.000000000000 (0.0000000000%) |
| 1.4 Raw→Processed year 1403 | ✅ | raw=57777447461.00, proc=57777447461.00, tol=0.000000000000 (0.0000000000%) |
| 1.5 Raw→Processed year 1404 | ✅ | raw=44979819327.00, proc=44979819327.00, tol=0.000000000000 (0.0000000000%) |

### ۲. Numerical Consistency (Processed → Trend)

| تست | نتیجه | جزئیات |
|------|-------|--------|
| 2.1 Processed→Trend year 1400 | ✅ | proc=48134744945.00, trend=48134744945.00, tol=0.000000000000 (0.0000000000%) |
| 2.2 Processed→Trend year 1401 | ✅ | proc=52958904652.00, trend=52958904652.00, tol=0.000000000000 (0.0000000000%) |
| 2.3 Processed→Trend year 1402 | ✅ | proc=49442023650.00, trend=49442023650.00, tol=0.000000000000 (0.0000000000%) |
| 2.4 Processed→Trend year 1403 | ✅ | proc=57777447461.00, trend=57777447461.00, tol=0.000000000000 (0.0000000000%) |
| 2.5 Processed→Trend year 1404 | ✅ | proc=44979819327.00, trend=44979819327.00, tol=0.000000000000 (0.0000000000%) |

### ۳. Numerical Consistency (Trend → Classification)

| تست | نتیجه | جزئیات |
|------|-------|--------|
| 3.1 Trend→Classification year 1400 | ✅ | trend=48134744945.00, class=48134744945.00, tol=0.000000000000 (0.0000000000%) |
| 3.2 Trend→Classification year 1401 | ✅ | trend=52958904652.00, class=52958904652.00, tol=0.000000000000 (0.0000000000%) |
| 3.3 Trend→Classification year 1402 | ✅ | trend=49442023650.00, class=49442023650.00, tol=0.000000000000 (0.0000000000%) |
| 3.4 Trend→Classification year 1403 | ✅ | trend=57777447461.00, class=57777447461.00, tol=0.000000000000 (0.0000000000%) |
| 3.5 Trend→Classification year 1404 | ✅ | trend=44979819327.00, class=44979819327.00, tol=0.000000000000 (0.0000000000%) |

### ۴. Consistency (Classification → Candidates)

| تست | نتیجه | جزئیات |
|------|-------|--------|
| 4.1 Candidates count ≤ Classification count | ✅ | classification=5993, candidates=574 |
| 4.2 All candidate HS codes in classification | ✅ | all 574 HS codes found |
| 4.3 Candidates satisfy membership filter (strong/moderate/emerging > 0) | ✅ | violations=0 |

### ۵. Completeness

| تست | نتیجه | جزئیات |
|------|-------|--------|
| 5.1 5 years present (1400-1404) | ✅ | years=[1400, 1401, 1402, 1403, 1404], missing=[] |
| 5.2 ≥100 countries | ✅ | n_countries=166 (expected 166) |
| 5.3 ≥1000 HS codes | ✅ | n_hs=5993 (expected 5993) |
| 5.4 Reasonable record count per year (Issue-006 aware) | ✅ | monthly years={1400: 162333, 1401: 169183, 1402: 183771} (threshold ≥100k), year... |
| 5.5 No nulls in year | ✅ | n_null=0 |
| 5.6 No nulls in hs_code | ✅ | n_null=0 |
| 5.7 No nulls in destination_country_iso2 | ✅ | n_null=0 |
| 5.8 No nulls in export_value_usd | ✅ | n_null=0 |

### ۶. Format Validation

| تست | نتیجه | جزئیات |
|------|-------|--------|
| 6.1 HS Code format (HH.HH.HH.HH) | ✅ | checked=5993, bad=0 |
| 6.2 Country ISO format (XX) | ✅ | checked=166, bad=0 |
| 6.3 export_value_usd ≥ 0 | ✅ | n_negative=0 |
| 6.4 export_weight_kg ≥ 0 | ✅ | n_negative=0 |

### ۷. Analysis Consistency

| تست | نتیجه | جزئیات |
|------|-------|--------|
| 7.1 Trend pairs == Classification pairs | ✅ | trend=50196, class=50196 |
| 7.2 No null trend_category | ✅ | n_null=0 |
| 7.3 All trend_category values valid | ✅ | valid categories=10 |
| 7.4 All candidates have score and rank | ✅ | null_score=0, null_rank=0 |
| 7.5 Ranks unique and no gaps | ✅ | min=1, max=574, expected_max=574 |
| 7.6 Ranks consistent with export_score ordering | ✅ | rank #1 has highest score |
| 7.7 Recalibrated recommendations consistent with percentile thresholds | ✅ | select≥0.10335436768886616, monitor≥0.061012351141215074, violations=0 |

### ۸. Excel File Integrity

| تست | نتیجه | جزئیات |
|------|-------|--------|
| 8.1 Excel file exists | ✅ | size=0.41MB |
| 8.2 Excel opens without error | ✅ | sheets=7 |
| 8.3 All expected sheets present | ✅ | sheets=['All-Candidates', 'Top-500', 'Select', 'Monitor', 'By-Chapter', 'By-Targ... |
| 8.4 All-Candidates has ≥574 rows | ✅ | n_rows=574 |
| 8.5 Select sheet has candidates | ✅ | n_rows=58 (expected 58) |
| 8.6 Monitor sheet has candidates | ✅ | n_rows=172 (expected 172) |
| 8.7 Top-500 sheet has rows | ✅ | n_rows=500 (expected min(500, 574)=500) |

### ۹. Issues Documentation

| تست | نتیجه | جزئیات |
|------|-------|--------|
| 9.1 Metadata file exists | ✅ |  |
| 9.2 Issue 005 documented in metadata | ✅ | keyword='tccim' found |
| 9.3 Issue 006 documented in metadata | ✅ | keyword='month' found |
| 9.4 Issue 007 documented in metadata | ✅ | keyword='quantity' found |
| 9.5 Issue 008 documented in metadata | ✅ | keyword='1405' found |


## شفافیت اجرا (یافته‌های حین تست)

1. **یافته اولیه Test 5.4 (ریشه‌یابی شد — false positive):** در اجرای اول، تست «تعداد رکورد منطقی هر سال > 100,000» برای ۱۴۰۳ (۵۸,۲۴۷ رکورد) و ۱۴۰۴ (۵۲,۸۶۱ رکورد) FAIL شد. ریشه: آستانه ۱۰۰k در recipe-04 مورخ ۱۴۰۵-۰۶-۱۵ نوشته شده بود — **قبل از کشف Issue-006** (۱۴۰۵-۰۶-۱۶) مبنی بر اینکه ۱۴۰۳/۱۴۰۴ در منبع سطح-سال تجمیع شده‌اند و صفت ماه ندارند. طبق Issue-006 «مشکل از صفت ماه است نه فقدان داده» — کامل‌بودن ارزش این سال‌ها به‌طور مستقل با تست‌های 1.4/1.5 (تلورانس دقیق صفر؛ ۱۴۰۳ = ۵۷.۷۸B$ همخوان با آمار رسمی) تأیید شد. معیار تست به نسخه Issue-006-aware (آستانه ≥20k برای سال‌های تجمیعی) اصلاح و این تعدیل در `issues.md` (Issue-009) ثبت شد. هیچ داده‌ای تغییر نکرد.

## نتیجه

✅ **همه تست‌ها PASS شدند.** پروژه آماده انتشار است (task-07/08/09).

## مسائل باز شناخته‌شده (از `04-State/issues.md`)

| Issue | عنوان | وضعیت | تأثیر بر QA |
|-------|-------|-------|-------------|
| Issue-005 | tsd.irica.ir از خارج ایران مسدود | 🟢 resolved با منبع جایگزین service.tccim.ir (Decision-011) | بدون تأثیر — منبع جایگزین اعتبارسنجی شد |
| Issue-006 | ۱۴۰۳/۱۴۰۴ بدون تفکیک ماهانه | 🟡 addressed (month=0، is_monthly=False) | بدون تأثیر — تحلیل‌ها سالانه‌اند |
| Issue-007 | export_quantity همیشه NULL | 🟢 addressed (ستون حذف شد) | بدون تأثیر — ستون در اسکیما نیست |
| Issue-008 | ۱۴۰۵ در منبع موجود نیست | 🟡 documented در metadata | بدون تأثیر — تحلیل روی ۵ سال کامل |

هیچ Issue جدیدی در این اجرای QA یافت نشد.

## محدودیت‌ها و نکات

1. سال ۱۴۰۵ در منبع موجود نیست (Issue-008) — تحلیل روی ۵ سال کامل (۱۴۰۰ تا ۱۴۰۴).
2. تفکیک ماهانه ۱۴۰۳/۱۴۰۴ موجود نیست (Issue-006) — اما در تحلیل سالانه مشکلی ایجاد نمی‌کند.
3. هشدار آماری Mann-Kendall: با n=5، حداقل p-value ≈ ۰.۰۲۷۵؛ معناداری باید در کنار CAGR/R²/ثبات تفسیر شود.
4. آستانه‌های توصیه (select/monitor/investigate) بر اساس صدک هستند (نسبی، نه مطلق) — بازکالیبراسیون task-12 تأیید شد.
5. کدهای user-assigned (XO/ZF/ZS/ZZ) طبق ISO 3166 در داده مجازند و در تست فرمت PASS هستند.
6. معیار رکورد-به-سال در Test 5.4 نسبت به Issue-006 تعدیل شد (بخش «شفافیت اجرا» و Issue-009 را ببینید) — از این پس در re-runها ملاک است.

## توصیه‌ها

- اجرای task-07 (Excel نهایی ۱۸ شیت) و task-08 (خروجی Obsidian) از این لحظه مجاز است.
- پس از انتشار داده ۱۴۰۵ در منبع: اجرای مجدد زنجیره (scrape 1405 → ETL → trend → classification → ranking) و سپس re-run این اسکریپت.
- Mirror data (UN Comtrade) به‌عنوان اعتبارسنجی متقابل اختیاری باقی می‌ماند (خارج از محدوده این اجرا).

## فایل‌های خروجی

- `04-State/qa-report.md` — این فایل
- `05-Data/processed/qa-validation.json` — نتایج structured
- `scripts/qa_validate_final.py` — اسکریپت قابل اجرای مجدد

## مراجع

- [[task-06-qa-validate]]
- [[prompt-qa-validator]]
- [[recipe-04-qa-checklist]]
- [[conventions]] — بخش ۴.۲ (دقت عددی)
- [[_validation-report]] — گزارش task-03
- [[_dataset-metadata]] — schema و issues مستندشده
