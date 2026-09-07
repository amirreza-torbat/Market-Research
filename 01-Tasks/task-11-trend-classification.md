---
type: task
task_id: task-11
title: طبقه‌بندی روند و اعتبارسنجی آماری
status: pending
assignee: analyst
created: 1405-06-15
updated: 1405-06-15
depends_on: [task-10]
blocks: [task-12, task-06]
estimated_effort: 1-2 days
priority: critical
---

# task-11 — طبقه‌بندی روند (Trend Classification)

## 🎯 هدف
طبقه‌بندی هر جفت (HS × Country) به یکی از ۷ دسته روند تعریف‌شده در [`conventions.md`](../00-Overview/conventions.md) بخش ۵.۱، با تأیید آماری.

## 📋 شرح کار

### ۱. مرجع طبقه‌بندی
از [`00-Overview/conventions.md`](../00-Overview/conventions.md) بخش ۵.۱:

| دسته | کد | معیار |
|------|----|-------|
| رشد قوی | `strong_growth` | CAGR > 10٪، MK p < 0.05، slope > 0 |
| رشد متوسط | `moderate_growth` | 0 < CAGR ≤ 10٪، MK p < 0.1 |
| پایدار | `stable` | |CAGR| ≤ 2٪، R² < 0.3 |
| نوسانی | `volatile` | CV > 0.5، R² < 0.3 |
| کاهشی | `declining` | CAGR < 0، MK p < 0.1 |
| نوظهور | `emerging` | value_start = 0، value_end > threshold |
| محوشده | `disappearing` | value_start > threshold، value_end ≈ 0 |

### ۲. آستانه‌ها (Thresholds)
- `threshold_emerging_disappearing` = 100,000 USD (۱۰۰ هزار دلار) — در [`04-State/decisions.md`](../04-State/decisions.md) قابل تنظیم.
- `cagr_strong` = 10٪
- `cagr_stable` = 2٪
- `cv_volatile` = 0.5
- `r_squared_clear` = 0.3
- `mk_significant` = 0.05
- `mk_moderate` = 0.1

### ۳. الگوریتم طبقه‌بندی
```python
def classify_trend(row) -> str:
    """طبقه‌بندی یک جفت (HS, Country) بر اساس شاخص‌ها."""
    value_start = row["value_1400"]
    value_end = row["value_1404"]
    value_end_6y = row.get("value_1405_annualized", 0)
    
    # 1. نوظهور
    if value_start == 0 and value_end > THRESHOLD:
        return "emerging"
    
    # 2. محوشده
    if value_start > THRESHOLD and value_end < THRESHOLD / 10:
        return "disappearing"
    
    # 3. CAGR قابل محاسبه نباشد
    if row["cagr_5y"] is None:
        return "insufficient_data"
    
    cagr = row["cagr_5y"]
    mk_p = row["mk_p_value"]
    slope = row["slope"]
    r_sq = row["r_squared"]
    cv = row["cv"]
    
    # 4. رشد قوی
    if cagr > 0.10 and mk_p < 0.05 and slope > 0:
        return "strong_growth"
    
    # 5. رشد متوسط
    if 0 < cagr <= 0.10 and mk_p < 0.1:
        return "moderate_growth"
    
    # 6. کاهشی
    if cagr < 0 and mk_p < 0.1:
        return "declining"
    
    # 7. نوسانی (اول از پایدار چک شود چون ممکنه هر دو شرط رو داشته باشه)
    if cv is not None and cv > 0.5 and r_sq < 0.3:
        return "volatile"
    
    # 8. پایدار
    if abs(cagr) <= 0.02 and r_sq < 0.3:
        return "stable"
    
    # 9. پیش‌فرض: weak_growth (کمی رشد اما بدون معناداری آماری)
    if cagr > 0:
        return "weak_growth"
    elif cagr < 0:
        return "weak_decline"
    else:
        return "stable"
```

> **نکته**: ترتیب شرط‌ها مهم است. نوظهور و محوشده اول چک شوند چون CAGR برای آنها تعریف نشده.

### ۴. خروجی‌ها

#### ۴.۱ جدول طبقه‌بندی‌شده
فایل `05-Data/processed/trend-classification.parquet`:

| ستون | نوع |
|------|-----|
| `hs_code` | string |
| `destination_country_iso2` | string |
| `trend_category` | string (یکی از ۷ دسته + `weak_growth` + `weak_decline` + `insufficient_data`) |
| `confidence` | decimal (۰ تا ۱) — بر اساس MK p-value |
| `is_significant` | bool (MK p < 0.05) |
| `n_signs` | string — علامت‌های شاخص‌ها به‌صورت کد |
| `recommendation_action` | string (`select`, `monitor`, `avoid`, `investigate`) |

#### ۴.۲ جدول تجمیع شده (Aggregated by HS Code)
فایل `05-Data/processed/trend-classification-by-hs.parquet`:

| ستون | توضیح |
|------|-------|
| `hs_code` | |
| `hs_description` | |
| `n_countries_total` | تعداد کل کشورهای مقصد |
| `n_strong_growth` | تعداد کشورهای با رشد قوی |
| `n_moderate_growth` | |
| `n_weak_growth` | |
| `n_stable` | |
| `n_volatile` | |
| `n_declining` | |
| `n_weak_decline` | |
| `n_emerging` | |
| `n_disappearing` | |
| `n_insufficient_data` | |
| `total_value_5y` | مجموع ۵ سال |
| `total_value_6y` | مجموع ۶ سال (با 1405 annualized) |
| `cagr_5y_aggregated` | CAGR در سطح HS (aggregated) |
| `dominant_trend` | دسته غالب |
| `growth_diversity_score` | (n_strong + n_moderate + n_emerging) / n_countries_total |

### ۵. گزارش‌ها

#### ۵.۱ گزارش خلاصه طبقه‌بندی
فایل `06-Analysis/trend/_classification-summary.md`:
- تعداد کل جفت‌ها.
- تعداد در هر دسته.
- نمودار توزیع دسته‌ها.
- تعداد HS Code با حداقل یک کشور در دسته `strong_growth`.
- تعداد HS Code با `dominant_trend = strong_growth`.

#### ۵.۲ یادداشت‌های Top در هر دسته
برای هر دسته، Top 30 HS Code (بر اساس `total_value_6y`) یادداشت Obsidian بساز در:
- `06-Analysis/trend/strong-growth/`
- `06-Analysis/trend/moderate-growth/`
- `06-Analysis/trend/emerging/`
- `06-Analysis/trend/declining/`
- (به‌اختصار برای بقیه دسته‌ها)

هر یادداشت شامل:
- عنوان: `hs-XX-XXXX-XX-XX-<category>.md`
- شرح کالا.
- جدول کشورهای در این دسته.
- نمودار روند aggregated.
- نمودار Top 10 کشور.
- تحلیل کیفی (۱۵۰+ کلمه).

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [ ] فایل `05-Data/processed/trend-classification.parquet` ساخته شود.
- [ ] فایل `05-Data/processed/trend-classification-by-hs.parquet` ساخته شود.
- [ ] همه جفت‌ها در `trend-classification` دسته‌بندی شده باشند (هیچ NULL نباشد).
- [ ] فهرست دسته‌ها دقیقاً شامل مقادیر معتبر باشد.
- [ ] گزارش `06-Analysis/trend/_classification-summary.md` کامل شود.
- [ ] حداقل ۵۰ یادداشت در `06-Analysis/trend/` (Top در هر دسته).
- [ ] commit با پیام `analysis(trend): task-11 trend classification`.

## 📦 خروجی‌ها
- `05-Data/processed/trend-classification.parquet`
- `05-Data/processed/trend-classification-by-hs.parquet`
- `06-Analysis/trend/_classification-summary.md`
- `06-Analysis/trend/<category>/hs-*.md` (۵۰+ یادداشت)

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-analyst.md`](../02-Prompts/prompt-analyst.md)
- [`03-Recipes/recipe-09-trend-classification.md`](../03-Recipes/recipe-09-trend-classification.md)

## 🔗 وابستگی‌ها
- [[task-10-trend-analysis]] (الزامی)
- بلاک‌کننده [[task-12-export-candidates]], [[task-06-qa-validate]]
