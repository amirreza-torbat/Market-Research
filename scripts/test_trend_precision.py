#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task-10 — Precision Test for Trend Analysis (Independent Verification)
======================================================================

اسکریپت تست دقت مستقل برای تحلیل روند ۵ ساله.
هدف: مجموع value_1400..value_1404 در trend-analysis-5y.parquet باید با
مجموع export_value_usd سالانه در exports_1400-1405.parquet برابر باشد
با تلورانس کمتر از 0.0001٪ (یعنی < 1e-6 به‌صورت کسر).

این اسکریپت به‌صورت جداگانه از analyze_trend_5y.py اجرا می‌شود تا
یک اعتبارسنجی مستقل (فایل on-disk → فایل on-disk) ارائه دهد:
  1. جمع سالانه source (exact در Decimal از decimal128)
  2. جمع سالانه خروجی (float64 از فایل ذخیره‌شده)
  3. مقایسه با تلورانس Decimal
  4. بررسی‌های ساختاری: تعداد جفت، تعداد رکورد، NULLها

مصرف:
  python scripts/test_trend_precision.py
"""
from __future__ import annotations

import sys
from decimal import Decimal, getcontext
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

getcontext().prec = 28

REPO_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO_ROOT / "05-Data" / "processed"
SOURCE_PARQUET = PROCESSED_DIR / "exports_1400-1405.parquet"
TREND_PARQUET = PROCESSED_DIR / "trend-analysis-5y.parquet"

YEARS = [1400, 1401, 1402, 1403, 1404]
TOL = Decimal("1e-6")  # 0.0001٪
DEC_10K = Decimal(10000)

EXPECTED_ROWS_SOURCE = 626_395
EXPECTED_YEARS_TOTALS = {
    1400: Decimal("48134744945.0000"),
    1401: Decimal("52958904652.0000"),
    1402: Decimal("49442023650.0000"),
    1403: Decimal("57777447461.0000"),
    1404: Decimal("44979819327.0000"),
}  # از گزارش validation گزارش task-03


def source_yearly_sums_exact() -> dict[int, Decimal]:
    """جمع سالانه source به‌صورت exact (Decimal از decimal128)."""
    tbl = pq.read_table(
        SOURCE_PARQUET, columns=["year", "export_value_usd"]
    )
    df = tbl.to_pandas()
    out: dict[int, Decimal] = {}
    for y, grp in df.groupby("year"):
        # exact: هر Decimal → واحدهای int64 (×1e-4) → جمع integer → Decimal
        units = sum(int(d.scaleb(4)) for d in grp["export_value_usd"])
        out[int(y)] = Decimal(units) / DEC_10K
    return out


def trend_yearly_sums() -> dict[int, Decimal]:
    """جمع سالانه خروجی از فایل ذخیره‌شده (float64 → Decimal برای مقایسه)."""
    tbl = pq.read_table(
        TREND_PARQUET, columns=[f"value_{y}" for y in YEARS]
    )
    df = tbl.to_pandas()
    out: dict[int, Decimal] = {}
    for y in YEARS:
        # جمع float64 با Kahan-like دقت: از numpy sum (pairwise) استفاده
        # می‌شود؛ برای مقایسه Decimal با ۶ رقم اعشار کافی است.
        s = float(np.sum(df[f"value_{y}"].to_numpy(dtype=np.float64)))
        out[y] = Decimal(str(round(s, 4)))
    return out


def main() -> int:
    print("=" * 72)
    print("task-10 — تست دقت مستقل تحلیل روند (tol < 0.0001٪)")
    print("=" * 72)

    failures: list[str] = []

    # --- ۱. جمع سالانه ---
    src = source_yearly_sums_exact()
    out = trend_yearly_sums()

    print("\n[۱] جمع سالانه (source exact ↔ خروجی on-disk):")
    print(f"{'سال':<6}{'جمع source (USD)':<24}{'جمع خروجی (USD)':<24}{'تلورانس':<16}{'نتیجه'}")
    grand_src = Decimal(0)
    grand_out = Decimal(0)
    for y in YEARS:
        s, o = src[y], out[y]
        grand_src += s
        grand_out += o
        tol = abs(o - s) / s if s != 0 else Decimal(0)
        passed = tol < TOL
        if not passed:
            failures.append(f"year {y}: tol={tol} >= {TOL}")
        print(
            f"{y:<6}{s:>24,.2f}{o:>24,.2f}"
            f"{float(tol):>16.12f}   {'✅ PASS' if passed else '❌ FAIL'}"
        )
    # جمع کل
    tol_g = abs(grand_out - grand_src) / grand_src
    passed_g = tol_g < TOL
    if not passed_g:
        failures.append(f"grand total: tol={tol_g} >= {TOL}")
    print(
        f"{'مجموع':<6}{grand_src:>24,.2f}{grand_out:>24,.2f}"
        f"{float(tol_g):>16.12f}   {'✅ PASS' if passed_g else '❌ FAIL'}"
    )

    # --- ۲. مقایسه با گزارش validation تسک ۰۳ ---
    print("\n[۲] مقایسه با ارقام ثبت‌شده در گزارش validation (task-03):")
    for y in YEARS:
        exp = EXPECTED_YEARS_TOTALS[y]
        got = src[y]
        ok = got == exp
        if not ok:
            failures.append(f"year {y}: source {got} != validation {exp}")
        print(
            f"  year {y}: source={got:,} | validation={exp:,} "
            f"→ {'✅' if ok else '❌'}"
        )

    # --- ۳. بررسی‌های ساختاری ---
    print("\n[۳] بررسی‌های ساختاری:")
    src_tbl = pq.read_table(
        SOURCE_PARQUET,
        columns=["year", "hs_code", "destination_country_iso2",
                 "export_value_usd"],
    )
    src_df = src_tbl.to_pandas()
    n_src = len(src_df)
    ok = n_src == EXPECTED_ROWS_SOURCE
    if not ok:
        failures.append(f"source rows {n_src} != {EXPECTED_ROWS_SOURCE}")
    print(
        f"  رکوردهای source: {n_src:,} "
        f"(انتظار {EXPECTED_ROWS_SOURCE:,}) → {'✅' if ok else '❌'}"
    )

    src_pairs = src_df.groupby(
        ["hs_code", "destination_country_iso2"]
    ).ngroups
    tr_tbl = pq.read_table(TREND_PARQUET)
    n_tr = tr_tbl.num_rows
    ok = n_tr == src_pairs
    if not ok:
        failures.append(f"trend rows {n_tr} != unique pairs {src_pairs}")
    print(
        f"  جفت‌های یکتا source: {src_pairs:,} | ردیف‌های trend: {n_tr:,} "
        f"→ {'✅' if ok else '❌'}"
    )

    tr_df = tr_tbl.to_pandas()

    # جفت‌های aایج‌شده در خروجی باید دقیقاً همان جفت‌های source باشند
    tr_pairs = tr_df.groupby(
        ["hs_code", "destination_country_iso2"]
    ).ngroups
    ok = tr_pairs == src_pairs
    if not ok:
        failures.append(f"distinct pairs in trend {tr_pairs} != {src_pairs}")
    print(f"  جفت‌های یکتا در trend: {tr_pairs:,} → {'✅' if ok else '❌'}")

    # ستون‌های الزامی
    required = [
        "hs_code", "destination_country_iso2", "hs_description",
        "destination_country_fa", "value_1400", "value_1401", "value_1402",
        "value_1403", "value_1404", "cagr_5y", "cagr_6y", "pct_change_5y",
        "growth_multiplier", "slope", "r_squared", "mk_p_value", "cv",
        "trend_consistency", "mean_value", "mean_recent_3y",
        "n_years_with_data",
    ]
    missing = [c for c in required if c not in tr_df.columns]
    ok = not missing
    if not ok:
        failures.append(f"missing columns: {missing}")
    print(
        f"  ستون‌های الزامی ({len(required)}): "
        f"{'همه موجود ✅' if ok else f'ناقص ❌ {missing}'}"
    )

    # مقدارهای منفی (نباید هیچ‌کدام)
    neg = int(
        sum((tr_df[f"value_{y}"] < 0).sum() for y in YEARS)
    )
    ok = neg == 0
    if not ok:
        failures.append(f"negative values: {neg}")
    print(f"  مقدارهای منفی در value_1400..1404: {neg} → {'✅' if ok else '❌'}")

    # cagr_6y باید همیشه NULL باشد (Issue-008)
    n6 = int(tr_df["cagr_6y"].notna().sum())
    ok = n6 == 0
    if not ok:
        failures.append(f"cagr_6y not-null: {n6}")
    print(
        f"  cagr_6y همیشه NULL (Issue-008): {n6} غیر NULL → "
        f"{'✅' if ok else '❌'}"
    )

    # قواعد NULL برای cagr/pct/mult
    v0 = tr_df["value_1400"]
    bad_cagr = int(
        ((v0 <= 0) & tr_df["cagr_5y"].notna()).sum()
        + ((tr_df["value_1404"] <= 0) & tr_df["cagr_5y"].notna()).sum()
    )
    ok = bad_cagr == 0
    if not ok:
        failures.append(f"cagr computed where v0<=0 or v4<=0: {bad_cagr}")
    print(f"  cagr فقط با v1400>0 و v1404>0: تخلف {bad_cagr} → {'✅' if ok else '❌'}")

    bad_pct = int(((v0 <= 0) & tr_df["pct_change_5y"].notna()).sum())
    ok = bad_pct == 0
    if not ok:
        failures.append(f"pct_change computed where v0<=0: {bad_pct}")
    print(f"  pct/multiplier فقط با v1400>0: تخلف {bad_pct} → {'✅' if ok else '❌'}")

    # دامنه trend_consistency و n_years_with_data
    tc, ny = tr_df["trend_consistency"], tr_df["n_years_with_data"]
    ok = bool(tc.between(0, 4).all() and ny.between(1, 5).all())
    if not ok:
        failures.append("trend_consistency/n_years_with_data out of range")
    print(f"  دامنه trend_consistency (0..4) و n_years (1..5) → {'✅' if ok else '❌'}")

    # mk_p_value در [0,1]
    mk = tr_df["mk_p_value"]
    ok = bool(mk.between(0, 1).all())
    if not ok:
        failures.append("mk_p_value out of [0,1]")
    print(f"  mk_p_value در بازه [0,1] → {'✅' if ok else '❌'}")

    # --- نتیجه ---
    print("\n" + "=" * 72)
    if failures:
        print(f"❌ FAIL — {len(failures)} خرابی:")
        for f in failures:
            print(f"   - {f}")
        return 1
    print("✅ PASS — همه بررسی‌ها موفق (تلورانس < 0.0001٪)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
