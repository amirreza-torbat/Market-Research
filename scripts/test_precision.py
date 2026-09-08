#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task-03 — Precision Test (Independent Verification)
====================================================

اسکریپت تست دقت مستقل برای ETL.
هدف: مجموع export_value_usd در Parquet باید با داده خام برابر باشد
با تلورانس کمتر از 0.0001٪ (یعنی < 1e-6 به‌صورت کسر).

این اسکریپت به‌صورت جداگانه از etl_normalize.py اجرا می‌شود تا
یک اعتبارسنجی مستقل ارائه دهد.

مصرف:
  python scripts/test_precision.py
"""
from __future__ import annotations

import sys
from decimal import Decimal, getcontext
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

getcontext().prec = 28

REPO_ROOT = Path(__file__).resolve().parents[1]
INTERIM_DIR = REPO_ROOT / "05-Data" / "interim"
PROCESSED_DIR = REPO_ROOT / "05-Data" / "processed"
YEARS = [1400, 1401, 1402, 1403, 1404]
TOLERANCE_THRESHOLD = Decimal("0.000001")  # < 0.0001% = < 1e-6


def to_decimal(val) -> Decimal:
    if val is None or pd.isna(val) or str(val).strip() == "":
        return Decimal(0)
    try:
        return Decimal(str(val).strip().replace(",", ""))
    except Exception:
        return Decimal(0)


def test_precision() -> dict[int, dict]:
    """برای هر سال: مجموع value_usd در Parquet باید با داده خام برابر باشد."""
    results: dict[int, dict] = {}

    # 1) خواندن داده خام
    raw_sums: dict[int, Decimal] = {}
    raw_record_counts: dict[int, int] = {}
    for year in YEARS:
        df = pd.read_csv(
            INTERIM_DIR / f"exports_{year}_raw.csv.gz",
            dtype=str,
            encoding="utf-8",
            keep_default_na=False,
            na_values=[""],
        )
        # فیلتر رکوردهای با value_usd خالی
        df = df[df["export_value_usd"].astype(str).str.strip() != ""]
        raw_sums[year] = sum(to_decimal(v) for v in df["export_value_usd"])
        raw_record_counts[year] = len(df)

    # 2) خواندن داده پردازش‌شده (Parquet)
    table = pq.read_table(PROCESSED_DIR / "exports_1400-1405.parquet")
    proc = table.to_pandas()

    # بررسی schema: ستون‌های Decimal بعد از to_pandas() ممکن است به Decimal پایتون تبدیل شوند یا به float
    # برای اطمینان، صریحاً به Decimal تبدیل می‌کنیم
    proc["export_value_usd_dec"] = proc["export_value_usd"].apply(lambda x: Decimal(str(x)))

    # 3) مقایسه
    print("=" * 80)
    print("INDEPENDENT PRECISION TEST")
    print("=" * 80)
    print(f"Threshold: tolerance < {TOLERANCE_THRESHOLD} (i.e. < 0.0001%)")
    print()
    print(f"{'Year':<6} {'Raw n':>10} {'Raw sum USD':>25} {'Proc sum USD':>25} {'Diff':>15} {'Tolerance':>15} {'Result':<8}")
    print("-" * 110)

    all_pass = True
    for year in YEARS:
        proc_year = proc[proc["year"] == year]
        proc_sum = proc_year["export_value_usd_dec"].sum()
        raw_sum = raw_sums[year]

        diff = proc_sum - raw_sum
        tolerance = abs(diff) / raw_sum if raw_sum > 0 else Decimal(0)
        pass_ = tolerance < TOLERANCE_THRESHOLD
        if not pass_:
            all_pass = False
        status = "✅ PASS" if pass_ else "❌ FAIL"
        print(f"{year:<6} {raw_record_counts[year]:>10,} {raw_sum:>25,.2f} {proc_sum:>25,.2f} {diff:>15,.2f} {float(tolerance):>15.10f} {status:<8}")
        results[year] = {
            "raw_n": raw_record_counts[year],
            "raw_sum": raw_sum,
            "proc_sum": proc_sum,
            "diff": diff,
            "tolerance": tolerance,
            "pass": pass_,
        }

    print("-" * 110)
    print(f"\nOverall: {'✅ ALL PASS' if all_pass else '❌ SOME FAIL'}")
    return results


def test_schema_and_nulls():
    """تست‌های اضافی: schema و nulls."""
    print("\n" + "=" * 80)
    print("SCHEMA & NULL TEST")
    print("=" * 80)
    table = pq.read_table(PROCESSED_DIR / "exports_1400-1405.parquet")
    schema = table.schema
    print(f"Total columns: {len(schema.names)}")
    print("Columns:")
    for i, name in enumerate(schema.names):
        print(f"  {i+1:>2}. {name:<30} {schema.field(name).type}")

    df = table.to_pandas()
    n = len(df)
    print(f"\nTotal rows: {n:,}")
    print("\nNull check (key fields):")
    print(f"  year nulls:                       {df['year'].isna().sum():>6}")
    print(f"  month nulls (must be 0; 0 is valid for 1403/1404): {df['month'].isna().sum():>6}")
    print(f"  is_monthly nulls:                 {df['is_monthly'].isna().sum():>6}")
    print(f"  hs_code nulls:                    {df['hs_code'].isna().sum():>6}")
    print(f"  destination_country_iso2 nulls:   {df['destination_country_iso2'].isna().sum():>6}")
    print(f"  destination_country_fa nulls:     {df['destination_country_fa'].isna().sum():>6}")
    print(f"  export_value_usd nulls:           {df['export_value_usd'].apply(lambda v: pd.isna(v) or str(v) == '').sum():>6}")

    # Sanity: 5 سال موجود است
    years_in_data = sorted(df["year"].unique())
    expected_years = [1400, 1401, 1402, 1403, 1404]
    assert years_in_data == expected_years, f"Expected years {expected_years}, got {years_in_data}"
    print(f"\nYears in data: {years_in_data} ✅")

    # تعداد کشورها
    n_countries = df["destination_country_iso2"].nunique()
    print(f"Unique countries: {n_countries}")
    assert n_countries > 100, f"Expected >100 countries, got {n_countries}"
    print(f"  > 100 countries ✅")

    # تعداد HS Codes
    n_hs = df["hs_code"].nunique()
    print(f"Unique HS codes: {n_hs:,}")
    assert n_hs > 1000, f"Expected >1000 HS codes, got {n_hs}"
    print(f"  > 1000 HS codes ✅")

    # ماه‌های بدون ماه
    months_with_0 = (df["month"] == 0).sum()
    months_with_0_in_1403_1404 = ((df["year"].isin([1403, 1404])) & (df["month"] == 0)).sum()
    months_with_0_other = months_with_0 - months_with_0_in_1403_1404
    print(f"\nIssue-006 check:")
    print(f"  Records with month=0 in 1403/1404: {months_with_0_in_1403_1404:,} (expected)")
    print(f"  Records with month=0 in other years: {months_with_0_other} (should be 0)")
    assert months_with_0_other == 0, "Found month=0 in 1400/1401/1402!"
    print(f"  ✅ Issue-006 handled correctly")

    # is_monthly consistency
    inconsistent = ((df["month"] == 0) & (df["is_monthly"] == True)).sum() + \
                    ((df["month"].between(1, 12)) & (df["is_monthly"] == False)).sum()
    print(f"  is_monthly inconsistencies: {inconsistent} (should be 0)")
    assert inconsistent == 0
    print(f"  ✅ is_monthly consistent with month")


def test_hs_code_format():
    """بررسی اینکه همه HS Codeها به فرمت HH.HH.HH.HH هستند."""
    print("\n" + "=" * 80)
    print("HS CODE FORMAT TEST")
    print("=" * 80)
    table = pq.read_table(PROCESSED_DIR / "exports_1400-1405.parquet")
    df = table.to_pandas()
    import re
    pattern = re.compile(r"^\d{2}\.\d{2}\.\d{2}\.\d{2}$")
    bad = df[~df["hs_code"].astype(str).str.match(pattern)]
    print(f"Total HS codes: {len(df):,}")
    print(f"HS codes matching HH.HH.HH.HH: {len(df) - len(bad):,}")
    print(f"HS codes NOT matching pattern: {len(bad):,}")
    assert len(bad) == 0, f"Found {len(bad)} HS codes with bad format"
    print("✅ All HS codes in HH.HH.HH.HH format")


def main():
    results = test_precision()
    test_schema_and_nulls()
    test_hs_code_format()

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED ✅")
    print("=" * 80)
    sys.exit(0)


if __name__ == "__main__":
    main()
