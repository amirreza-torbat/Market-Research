---
folder: 03-Recipes
type: recipe
recipe_id: recipe-09
title: متدولوژی طبقه‌بندی روند و رتبه‌بندی کاندیدها
related_tasks: [task-10, task-11, task-12]
last_updated: 1405-06-15
priority: critical
---

# 📖 Recipe-09 — متدولوژی طبقه‌بندی روند و رتبه‌بندی کاندیدها

> **نقش**: Analyst Agent
> **تسک‌های مرتبط**: [[task-10-trend-analysis]]، [[task-11-trend-classification]]، [[task-12-export-candidates]]
> **هدف**: تشریح کامل متدولوژی برای محاسبه شاخص‌ها، طبقه‌بندی روند و رتبه‌بندی کاندیدهای صادرات.

## ۱. چرا این متدولوژی؟

کاربر می‌خواهد **تمام** HS Codeها × تمام کشورها را در ۶ سال بررسی کند تا **محصولاتی با روند رو به رشد** برای توسعه صادرات شناسایی کند. این نیازمند:

1. **حلقه کامل** (نه نمونه): هیچ HS Code یا کشوری حذف نشود.
2. **شاخص‌های آماری معنادار**: فقط CAGR کافی نیست — باید معناداری آماری (Mann-Kendall) و کیفیت برازش (R²) هم بررسی شود.
3. **طبقه‌بندی چندبُعدی**: نه فقط "افزایشی/کاهشی" بلکه ۷ دسته (شامل نوظهور، محوشده، نوسانی).
4. **نمره ترکیبی**: برای رتبه‌بندی محصولات، چندین شاخص با وزن‌های متفاوت ترکیب شود.
5. **دقت عددی**: < 0.0001٪.

## ۲. معماری pipeline

```
exports_1400-1405.parquet
         ↓
   [task-10: trend analysis]
         ↓
trend-analysis-6y.parquet (تمام جفت‌ها + شاخص‌ها)
         ↓
   [task-11: classification]
         ↓
trend-classification.parquet (تمام جفت‌ها + دسته)
trend-classification-by-hs.parquet (تجمیع به HS)
         ↓
   [task-12: ranking]
         ↓
export-candidates-ranked.parquet (Top 100 با نمره)
```

## ۳. شاخص‌های محاسبه‌شده (در task-10)

| شاخص | نوع | فرمول | دقت |
|------|-----|-------|-----|
| `value_1400`..`value_1404` | Decimal | `sum(export_value_usd)` per year | Decimal |
| `value_1405_ytd` | Decimal | `sum` تا آخرین ماه | Decimal |
| `value_1405_annualized` | Decimal | `value_1405_ytd * 12 / months_available_1405` | Decimal |
| `cagr_5y` | Decimal | `(v_1404 / v_1400)^(1/4) - 1` | Decimal |
| `cagr_6y` | Decimal | `(v_1405_ann / v_1400)^(1/5) - 1` | Decimal |
| `pct_change_5y` | Decimal | `(v_1404 - v_1400) / v_1400 * 100` | Decimal |
| `growth_multiplier` | Decimal | `v_1404 / v_1400` | Decimal |
| `slope` | Decimal | OLS slope روی ۶ سال | float→Decimal |
| `r_squared` | Decimal | ضریب تعیین OLS | float→Decimal |
| `mk_p_value` | Decimal | Mann-Kendall p-value | float→Decimal |
| `cv` | Decimal | `std / mean` | float→Decimal |
| `trend_consistency` | int | تعداد سال‌های متوالی با رشد مثبت | int |
| `mean_value` | Decimal | `mean(v_1400..v_1405_ann)` | Decimal |
| `mean_recent_3y` | Decimal | `mean(v_1402, v_1403, v_1404)` | Decimal |
| `n_years_with_data` | int | برای تشخیص نوظهور/محوشده | int |

## ۴. تست Mann-Kendall (ناپارامتریک)

برای n = ۶ سال (کوچک)، Mann-Kendall بهترین انتخاب است چون:
- ناپارامتریک (نیازی به نرمال‌بودن توزیع ندارد).
- مناسب اندازه نمونه کوچک.
- قوی به outlier‌ها.

### الگوریتم
```python
def mann_kendall_test(values: list[float]) -> tuple[float, float]:
    n = len(values)
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            s += np.sign(values[j] - values[i])
    
    # tie correction
    unique_vals, counts = np.unique(values, return_counts=True)
    tie_correction = sum(t * (t - 1) * (2 * t + 5) for t in counts if t > 1)
    var_s = (n * (n - 1) * (2 * n + 5) - tie_correction) / 18
    
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0.0
    
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    return z, p_value
```

### تفسیر
- `p < 0.05`: روند معنادار (95٪ اطمینان).
- `p < 0.10`: روند متوسط (90٪ اطمینان).
- `p ≥ 0.10`: بدون روند معنادار.

## ۵. طبقه‌بندی روند (در task-11)

### ترتیب اولویت دسته‌بندی
1. **emerging** (نوظهور): اگر `value_1400 == 0` و `value_1404 > threshold`.
2. **disappearing** (محوشده): اگر `value_1400 > threshold` و `value_1404 < threshold/10`.
3. اگر `cagr_5y` قابل محاسبه نباشد → `insufficient_data`.
4. **strong_growth**: `cagr_5y > 10٪` و `mk_p < 0.05` و `slope > 0`.
5. **moderate_growth**: `0 < cagr_5y ≤ 10٪` و `mk_p < 0.10`.
6. **declining**: `cagr_5y < 0` و `mk_p < 0.10`.
7. **volatile**: `cv > 0.5` و `r_squared < 0.3`.
8. **stable**: `|cagr_5y| ≤ 2٪` و `r_squared < 0.3`.
9. در غیر این صورت:
   - `weak_growth` (اگر `cagr_5y > 0`).
   - `weak_decline` (اگر `cagr_5y < 0`).
   - `stable` (اگر `cagr_5y == 0`).

### آستانه‌ها (Thresholds)
ثبت در [`04-State/decisions.md`](../04-State/decisions.md):
- `threshold_emerging_disappearing` = 100,000 USD
- `cagr_strong` = 10٪ (0.10)
- `cagr_stable` = 2٪ (0.02)
- `cv_volatile` = 0.5
- `r_squared_clear` = 0.3
- `mk_significant` = 0.05
- `mk_moderate` = 0.1

## ۶. نمره‌دهی برای رتبه‌بندی (در task-12)

### فرمول
```
export_score = w1 * norm(cagr_6y)
             + w2 * norm(slope)
             + w3 * norm(mean_recent_3y)
             + w4 * norm(n_destinations)
             + w5 * norm(trend_consistency)
             - w6 * norm(cv)
```

### وزن‌های پیشنهادی
| نماد | مقدار | توضیح |
|------|-------|-------|
| `w1` | 0.30 | رشد (مهم‌ترین) |
| `w2` | 0.20 | شیب روند (شدت) |
| `w3` | 0.20 | حجم (اهمیت اقتصادی) |
| `w4` | 0.10 | تنوع بازار |
| `w5` | 0.10 | ثبات روند |
| `w6` | 0.10 | جریمه نوسان |

> این وزن‌ها در [`04-State/decisions.md`](../04-State/decisions.md) قابل تنظیم هستند. اگر کاربر وزن‌های متفاوتی خواست، task-12 re-run شود.

### نرمال‌سازی
- **Min-Max** روی کل دیتاست.
- `norm(x) = (x - min) / (max - min)`.
- برای `cv` که جریمه است: `norm_penalty(cv) = (cv - min) / (max - min)` (هرچه بیشتر، جریمه بیشتر).

### فیلتر اولیه
فقط HS Codeهایی که:
1. در دسته `strong_growth`، `moderate_growth`، یا `emerging` باشند.
2. `mean_recent_3y_aggregated > 1,000,000 USD`.
3. `n_destinations_active >= 3` (حداقل ۳ کشور مقصد در ۱۴۰۴).

## ۷. توصیه‌های استراتژیک (در task-12)

برای هر کاندید Top 100، توصیه زیر:
- **`select`**: `export_score > 0.7` و `trend_category in [strong_growth, moderate_growth]`.
- **`monitor`**: `export_score` بین ۰.۴ و ۰.۷.
- **`investigate`**: `export_score < 0.4` یا نوسان بالا.

### ریسک‌ها (Risk Flags)
- `volatile`: اگر `cv > 0.7`.
- `concentrated`: اگر سهم بزرگ‌ترین کشور > 70٪.
- `declining_recent`: اگر `value_1404 < value_1403`.
- `partial_data`: اگر داده‌ای در ۱۴۰۵ کمتر از ۳ ماه است.

## ۸. خروجی‌ها

### ۸.۱ فایل‌های داده
- `05-Data/processed/trend-analysis-6y.parquet`
- `05-Data/processed/trend-classification.parquet`
- `05-Data/processed/trend-classification-by-hs.parquet`
- `05-Data/processed/export-candidates-ranked.parquet`

### ۸.۲ یادداشت‌های Obsidian
- `06-Analysis/trend/_classification-summary.md`
- `06-Analysis/trend/<category>/hs-*.md` (۵۰+ یادداشت)
- `06-Analysis/export-candidates/_executive-ranking.md`
- `06-Analysis/export-candidates/rank-NN-*.md` (۵۰+ یادداشت)
- `06-Analysis/export-candidates/by-target-country.md`
- `06-Analysis/export-candidates/chapter-country-matrix.md`

## ۹. دقت و اعتبارسنجی

### تست‌های الزامی (در task-06)
1. **Sum consistency**: مجموع `value_1400..1404` در `trend-analysis-6y` باید با Parquet برابر باشد (تلورانس < 0.0001٪).
2. **Completeness**: همه جفت‌های (HS × Country) در `trend-classification` دسته‌بندی شده باشند.
3. **Classification validity**: هیچ مقدار NULL یا invalid در `trend_category`.
4. **Score range**: `export_score` بین ۰ و ۱.
5. **Rank uniqueness**: `rank` یکتا و بدون شکاف.

### اگر تست fail شد
- در `04-State/issues.md` ثبت کن.
- اگر numerical fail → به task-10 برگرد.
- اگر classification fail → به task-11 برگرد.
- اگر ranking fail → به task-12 برگرد.

## ۱۰. مدیریت داده‌های sparse

برخی جفت‌ها ممکن است در برخی سال‌ها داده نداشته باشند. استراتژی:
- اگر `value == NaN` یا `NULL` → `Decimal(0)` جایگزین شود.
- اگر **همه** ۶ سال صفر → آن جفت در خروجی نباشد.
- اگر فقط سال ۱۴۰۵ صفر (partial) → `value_1405_annualized = 0` و در یادداشت ذکر شود.
- برای جفت‌های با داده‌های ناقص در سال‌های وسط → `cagr` قابل محاسبه نخواهد بود و دسته `insufficient_data` می‌گیرد.

## مراجع

- [[task-10-trend-analysis]]
- [[task-11-trend-classification]]
- [[task-12-export-candidates]]
- [[conventions]] — بخش ۵ (تاکسونومی روند) و ۵.۳ (نمره‌دهی)
- [[glossary]] — اصطلاحات آماری
- [[prompt-analyst]]
