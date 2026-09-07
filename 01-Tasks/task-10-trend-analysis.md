---
type: task
task_id: task-10
title: تحلیل جامع روند ۶ ساله (تمامی HS × تمامی کشورها)
status: pending
assignee: analyst
created: 1405-06-15
updated: 1405-06-15
depends_on: [task-03]
blocks: [task-11, task-06]
estimated_effort: 3-4 days
priority: critical
---

# task-10 — تحلیل جامع روند ۶ ساله برای تمامی جفت‌های (HS × Country)

## 🎯 هدف
**حلقه کامل (full loop)** روی تمامی کدهای تعرفه × تمامی کشورهای مقصد، و محاسبه شاخص‌های روند ۶ ساله برای هر جفت. این تسک **متمم و گسترش** [[task-05-analysis-tariff]] است، با این تفاوت که:
- همه HS Codeها بررسی می‌شوند (نه فقط Top 50).
- همه کشورها بررسی می‌شوند.
- سال ۱۴۰۵ (partial) هم در محاسبات لحاظ می‌شود.
- شاخص‌های آماری (slope, R², Mann-Kendall) محاسبه می‌شود.

## 📋 شرح کار

### ۱. آماده‌سازی داده
- load از `05-Data/processed/exports_1400-1405.parquet`.
- **هیچ فیلتری اعمال نشود** — تمام رکوردها نگه داشته شوند.
- aggregate به سطح `(year, hs_code, destination_country_iso2)` با `sum(export_value_usd)`.

### ۲. حلقه کامل (Full Loop)
برای هر جفت `(hs_code, destination_country_iso2)` در دیتاست:

```python
from decimal import Decimal, getcontext
import numpy as np
from scipy import stats
import pandas as pd

getcontext().prec = 28

def compute_trend_metrics(yearly_values: list[Decimal], years: list[int]) -> dict:
    """
    yearly_values: [v_1400, v_1401, v_1402, v_1403, v_1404, v_1405_partial_or_annualized]
    years: [1400, 1401, 1402, 1403, 1404, 1405]
    """
    # تبدیل به float برای محاسبات آماری (تنها برای slope/R²/MK)
    vals_float = [float(v) for v in yearly_values]
    
    # --- CAGR (5 سال کامل) ---
    if yearly_values[0] > 0 and yearly_values[4] > 0:
        cagr_5y = (Decimal(yearly_values[4]) / Decimal(yearly_values[0])) ** (Decimal(1) / Decimal(4)) - Decimal(1)
    else:
        cagr_5y = None
    
    # --- CAGR (6 سال، با 1405 annualized) ---
    if yearly_values[0] > 0 and yearly_values[5] > 0:
        cagr_6y = (Decimal(yearly_values[5]) / Decimal(yearly_values[0])) ** (Decimal(1) / Decimal(5)) - Decimal(1)
    else:
        cagr_6y = None
    
    # --- درصد تغییر ---
    if yearly_values[0] > 0:
        pct_change_5y = (Decimal(yearly_values[4]) - Decimal(yearly_values[0])) / Decimal(yearly_values[0]) * 100
        growth_multiplier = Decimal(yearly_values[4]) / Decimal(yearly_values[0])
    else:
        pct_change_5y = None
        growth_multiplier = None
    
    # --- OLS slope و R² ---
    slope, intercept, r_value, p_value, std_err = stats.linregress(years, vals_float)
    slope_dec = Decimal(str(slope))
    r_squared = Decimal(str(r_value ** 2))
    
    # --- Mann-Kendall test ---
    mk_p_value = Decimal(str(mann_kendall_test(vals_float)))
    
    # --- ضریب تغییرات (CV) ---
    mean_val = Decimal(str(np.mean(vals_float)))
    std_val = Decimal(str(np.std(vals_float, ddof=1))) if len(vals_float) > 1 else Decimal(0)
    cv = std_val / mean_val if mean_val > 0 else None
    
    # --- ثبات روند ---
    trend_consistency = sum(1 for i in range(1, len(vals_float)) 
                           if vals_float[i] > vals_float[i-1])
    
    return {
        "cagr_5y": cagr_5y,
        "cagr_6y": cagr_6y,
        "pct_change_5y": pct_change_5y,
        "growth_multiplier": growth_multiplier,
        "slope": slope_dec,
        "r_squared": r_squared,
        "mk_p_value": mk_p_value,
        "cv": cv,
        "trend_consistency": trend_consistency,
        "mean_value": mean_val,
        "mean_recent_3y": Decimal(str(np.mean(vals_float[-4:-1]))),  # 1402, 1403, 1404
        "value_1405_ytd": yearly_values[5],  # یا annualized
    }


def mann_kendall_test(values: list[float]) -> float:
    """Mann-Kendall trend test. Returns p-value."""
    n = len(values)
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            s += np.sign(values[j] - values[i])
    
    # ties correction
    unique_vals, counts = np.unique(values, return_counts=True)
    tie_correction = sum(t * (t - 1) * (2 * t + 5) for t in counts if t > 1)
    
    var_s = (n * (n - 1) * (2 * n + 5) - tie_correction) / 18
    
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0
    
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    return p_value
```

### ۳. خروجی‌ها

#### ۳.۱ جدول master trend
فایل `05-Data/processed/trend-analysis-6y.parquet`:

| ستون | نوع | توضیح |
|------|-----|-------|
| `hs_code` | string | HH.HH.HH.HH |
| `destination_country_iso2` | string | XX |
| `hs_description` | string | شرح کالا |
| `destination_country_fa` | string | نام فارسی کشور |
| `value_1400` | decimal | مجموع سالانه |
| `value_1401` | decimal | |
| `value_1402` | decimal | |
| `value_1403` | decimal | |
| `value_1404` | decimal | |
| `value_1405_ytd` | decimal | جمع YTD ۱۴۰۵ |
| `value_1405_annualized` | decimal | تخمین سالانه |
| `months_available_1405` | int | تعداد ماه‌های موجود ۱۴۰۵ |
| `cagr_5y` | decimal | (NULL اگر قابل محاسبه نباشد) |
| `cagr_6y` | decimal | |
| `pct_change_5y` | decimal | |
| `growth_multiplier` | decimal | |
| `slope` | decimal | از OLS |
| `r_squared` | decimal | |
| `mk_p_value` | decimal | Mann-Kendall |
| `cv` | decimal | ضریب تغییرات |
| `trend_consistency` | int | ۰ تا ۵ |
| `mean_value` | decimal | |
| `mean_recent_3y` | decimal | |
| `n_years_with_data` | int | برای تشخیص نوظهور/محوشده |

#### ۳.۲ گزارش خلاصه
فایل `05-Data/processed/trend-analysis-summary.md`:
- تعداد کل جفت‌های (HS × Country).
- تعداد جفت‌های با داده در همه ۶ سال.
- آمار توصیفی شاخص‌ها.

### ۴. مدیریت داده‌های sparse
برخی جفت‌ها ممکن است در برخی سال‌ها داده نداشته باشند (یعنی صادرات صفر یا NaN). استراتژی:
- اگر `value == 0` یا `NaN` → `Decimal(0)` جایگزین شود.
- اگر ALL سال‌ها صفر → آن جفت در خروجی نباشد.
- اگر فقط سال ۱۴۰۵ صفر (partial) → `value_1405_annualized = 0` و در یادداشت ذکر شود.

### ۵. کارایی (Performance)
- تعداد جفت‌ها می‌تواند تا ۱ میلیون برسد (5000 HS × 200 کشور).
- **الزامی**: استفاده از `polars` یا `pandas` vectorized operations، نه loop روی هر جفت به‌صورت جدا.
- برای Mann-Kendall: vectorize با `numba` یا اجرای موازی با `multiprocessing`.
- محاسبه OLS slope می‌تواند با `numpy.polyfit` به‌صورت vectorized روی همه جفت‌ها انجام شود.

### ۶. دقت عددی
- **الزامی**: `cagr`, `pct_change`, `growth_multiplier` با `Decimal`.
- `slope`, `r_squared`, `mk_p_value`, `cv` می‌توانند با float (این شاخص‌های آماری به دقت < 0.0001٪ نیاز ندارند).
- تست: مجموع `value_1400` در trend-analysis باید با مجموع `export_value_usd` سال ۱۴۰۰ در Parquet برابر باشد (تلورانس < 0.0001٪).

## ✅ معیارهای پذیرش (Acceptance Criteria)
- [ ] فایل `05-Data/processed/trend-analysis-6y.parquet` ساخته شود.
- [ ] **تمام** جفت‌های (HS × Country) با داده در فایل موجود باشند.
- [ ] همه شاخص‌های جدول بالا محاسبه شده باشند.
- [ ] فایل `05-Data/processed/trend-analysis-summary.md` کامل شود.
- [ ] تست دقت: مجموع value_1400..1404 با Parquet برابر باشد (تلورانس < 0.0001٪).
- [ ] commit با پیام `analysis(trend): task-10 full 6-year trend analysis for all HS×Country`.

## 📦 خروجی‌ها
- `05-Data/processed/trend-analysis-6y.parquet` — جدول master با همه شاخص‌ها.
- `05-Data/processed/trend-analysis-summary.md` — گزارش خلاصه.

## 🔗 پرامپت مرتبط
- [`02-Prompts/prompt-analyst.md`](../02-Prompts/prompt-analyst.md)
- [`03-Recipes/recipe-09-trend-classification.md`](../03-Recipes/recipe-09-trend-classification.md)

## 🔗 وابستگی‌ها
- [[task-03-etl-normalize]]
- بلاک‌کننده [[task-11-trend-classification]], [[task-06-qa-validate]]
- **تمام** تسک‌های تحلیلی بعدی به خروجی این تسک وابسته‌اند.

## 🔗 یادداشت
- این تسک مبنای [[task-11-trend-classification]] و [[task-12-export-candidates]] است.
- اگر این تسک ناقص باشد، کل تحلیل روند فاقد ارزش است.
