---
folder: 03-Recipes
type: recipe
recipe_id: recipe-04
title: چک‌لیست QA
related_tasks: [task-06]
last_updated: 1405-06-15
---

# 📖 Recipe-04 — چک‌لیست QA

> **نقش**: QA Validator Agent
> **تسک مرتبط**: [[task-06-qa-validate]]
> **زمان تخمینی**: ۱-۲ روز

## هدف
اعتبارسنجی کامل دقت و کامل‌بودن داده و تحلیل با تلورانس < 0.0001٪.

## پیش‌نیازها
- [ ] `task-04` و `task-05` کامل شده باشند (status: review یا done).
- [ ] همه فایل‌های پردازش‌شده موجود.

## مراحل

### مرحله ۱: ساخت اسکریپت تست (۲ ساعت)
1. شاخه `feature/task-06-qa` بساز.
2. در `scripts/qa_validate.py`:
   - `test_value_consistency()`
   - `test_completeness()`
   - `test_analysis_country()`
   - `test_analysis_tariff()`
   - `test_no_nulls()`
   - `test_hs_code_format()`
   - `test_country_iso_format()`

### مرحله ۲: تست‌های عددی (۱ ساعت)

#### Test 1.1: raw vs processed
```python
def test_value_consistency():
    raw_sums = {}
    for year in range(1400, 1405):
        df = pd.read_csv(f"05-Data/interim/exports_{year}_raw.csv", dtype=str)
        raw_sums[year] = sum(Decimal(str(v)) for v in df["export_value_usd"])
    
    proc = pq.read_table("05-Data/processed/exports_1400-1404.parquet").to_pandas()
    proc["export_value_usd"] = proc["export_value_usd"].apply(Decimal)
    proc_sums = proc.groupby("year")["export_value_usd"].sum().to_dict()
    
    for year in range(1400, 1405):
        tolerance = abs(proc_sums[year] - raw_sums[year]) / raw_sums[year]
        assert tolerance < Decimal("0.000001"), \
            f"Year {year} tolerance {tolerance} exceeds 0.0001%"
```

#### Test 1.2: analysis vs parquet
```python
def test_analysis_country():
    proc = pq.read_table("05-Data/processed/exports_1400-1404.parquet").to_pandas()
    proc["export_value_usd"] = proc["export_value_usd"].apply(Decimal)
    proc_total = proc["export_value_usd"].sum()
    
    analysis = pd.read_csv("05-Data/processed/analysis-by-country.csv")
    # مجموع value_1400 + ... + value_1404 باید برابر proc_total باشد
    analysis_total = sum(Decimal(str(v)) for v in 
                         (analysis[f"value_{y}"] for y in range(1400, 1405)))
    
    tolerance = abs(analysis_total - proc_total) / proc_total
    assert tolerance < Decimal("0.000001")
```

### مرحله ۳: تست‌های کامل‌بودن (۳۰ دقیقه)

#### Test 2.1: ۵ سال موجود
```python
def test_5_years_present():
    proc = pq.read_table("05-Data/processed/exports_1400-1404.parquet").to_pandas()
    years = set(proc["year"].unique())
    expected = {1400, 1401, 1402, 1403, 1404}
    assert years == expected, f"Missing years: {expected - years}"
```

#### Test 2.2: حداقل کشورها و HS Codeها
```python
def test_minimum_countries():
    proc = pq.read_table("05-Data/processed/exports_1400-1404.parquet").to_pandas()
    n_countries = proc["destination_country_iso2"].nunique()
    assert n_countries > 100, f"Only {n_countries} countries"

def test_minimum_hs_codes():
    proc = pq.read_table("05-Data/processed/exports_1400-1404.parquet").to_pandas()
    n_hs = proc["hs_code"].nunique()
    assert n_hs > 1000, f"Only {n_hs} HS codes"
```

#### Test 2.3: هیچ null در فیلدهای کلیدی
```python
def test_no_nulls():
    proc = pq.read_table("05-Data/processed/exports_1400-1404.parquet").to_pandas()
    for col in ["year", "hs_code", "destination_country_iso2", "export_value_usd"]:
        assert proc[col].isna().sum() == 0, f"Nulls in {col}"
```

### مرحله ۴: تست‌های فرمت (۳۰ دقیقه)

#### Test 3.1: HS Code فرمت
```python
import re
def test_hs_code_format():
    proc = pq.read_table("05-Data/processed/exports_1400-1404.parquet").to_pandas()
    pattern = re.compile(r"^\d{2}\.\d{2}\.\d{2}\.\d{2}$")
    bad = [code for code in proc["hs_code"].unique() if not pattern.match(code)]
    assert len(bad) == 0, f"Bad HS codes: {bad[:5]}"
```

#### Test 3.2: Country ISO فرمت
```python
def test_country_iso_format():
    proc = pq.read_table("05-Data/processed/exports_1400-1404.parquet").to_pandas()
    pattern = re.compile(r"^[A-Z]{2}$")
    bad = [c for c in proc["destination_country_iso2"].unique() if not pattern.match(c)]
    assert len(bad) == 0, f"Bad ISO codes: {bad[:5]}"
```

### مرحله ۵: تست‌های تحلیل (۱ ساعت)

#### Test 4.1: تحلیل country
```python
def test_analysis_country_completeness():
    analysis = pd.read_csv("05-Data/processed/analysis-by-country.csv")
    # همه کشورها در Parquet باید در analysis باشند
    proc = pq.read_table("05-Data/processed/exports_1400-1404.parquet").to_pandas()
    proc_countries = set(proc["destination_country_iso2"].unique())
    analysis_countries = set(analysis["destination_country_iso2"])
    missing = proc_countries - analysis_countries
    assert len(missing) == 0, f"Missing countries in analysis: {missing}"
```

#### Test 4.2: تحلیل tariff
```python
def test_analysis_tariff_completeness():
    analysis = pd.read_csv("05-Data/processed/analysis-by-tariff.csv")
    proc = pq.read_table("05-Data/processed/exports_1400-1404.parquet").to_pandas()
    proc_hs = set(proc["hs_code"].unique())
    analysis_hs = set(analysis["hs_code"])
    missing = proc_hs - analysis_hs
    assert len(missing) == 0, f"Missing HS codes in analysis: {missing}"
```

### مرحله ۶: Mirror Data (اختیاری) (۲ ساعت)
1. از UN Comtrade داده واردات کشورهای مقصد از ایران را بگیر.
2. مقایسه با داده ما.
3. اختلاف > 10٪ = هشدار، > 30٪ = issue.

### مرحله ۷: گزارش QA (۱ ساعت)
1. در `04-State/qa-report.md` (با قالب در پرامپت QA).
2. شامل:
   - وضعیت کلی.
   - نتیجه هر تست.
   - تلورانس مشاهده‌شده.
   - مسائل باز.

### مرحله ۸: commit و PR
1. `task-06` به `review` در STATUS.md.
2. commit: `qa: task-06 validation report`.
3. push و PR.

## اگر تست fail شد

### اگر Test 1.1 (numerical) fail شد:
- تلورانس را گزارش کن.
- در `04-State/issues.md` ثبت کن.
- به ETL Engineer اطلاع بده.
- STATUS.md تسک مرتبط را به `blocked` تغییر بده.

### اگر Test 2.1 (۵ سال) fail شد:
- احتمالاً scraper برای آن سال کار نکرده.
- به Scraper اطلاع بده.
- آن سال re-scrape شود.

## مراجع
- [[task-06-qa-validate]]
- [[prompt-qa-validator]]
- [[conventions]]
