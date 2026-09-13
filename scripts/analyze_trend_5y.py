#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task-10 — Full 5-Year Trend Analysis (Market-Research Vault)
=============================================================

تحلیل جامع روند برای **تمامی** جفت‌های (HS Code × Country) — حلقه کامل،
بدون هیچ فیلتری. محاسبه تمام شاخص‌های روند ۵ ساله (۱۴۰۰-۱۴۰۴) طبق
recipe-09 و conventions §4.2/§4.2.2/§۵.

این اسکریپت:
  1. exports_1400-1405.parquet را می‌خواند (۶۲۶,۳۹۵ رکورد، سال‌های ۱۴۰۰-۱۴۰۴).
  2. aggregate به سطح (year, hs_code, destination_country_iso2) با
     sum(export_value_usd) — **aggregation در int64 (واحد 1e-4 USD) کاملاً exact**.
  3. pivot به ستون‌های value_1400..value_1404 برای هر جفت.
  4. محاسبه شاخص‌ها برای هر جفت:
     - Decimal (prec 28): cagr_5y, pct_change_5y, growth_multiplier
     - float (vectorized): slope, r_squared (OLS), mk_p_value (Mann-Kendall
       با tie correction), cv, trend_consistency, mean_value, mean_recent_3y
  5. ذخیره trend-analysis-5y.parquet (snappy) + گزارش خلاصه
     trend-analysis-summary.md.
  6. تست دقت داخلی: مجموع value_1400..1404 باید با source برابر باشد
     (تلورانس < 0.0001٪ = 1e-6).

مدیریت Issues:
  - Issue-008: سال 1405 در منبع موجود نیست → تحلیل روی ۵ سال کامل
    (۱۴۰۰-۱۴۰۴)؛ ستون cagr_6y همیشه NULL باقی می‌ماند تا اسکیمای
    تسک‌های بعدی (task-11/12) حفظ شود.
  - Issue-006: 1403/1404 تفکیک ماهانه ندارند → در تحلیل **سالانه** اثری
    ندارند (ماه‌ها ignore می‌شوند).

قواعد sparse (طبق task-10 §۴):
  - سال بدون رکورد برای یک جفت → مقدار 0 (صادرات صفر فرض می‌شود).
  - جفت با مجموع کل صفر در همه سال‌ها → از خروجی حذف می‌شود.
  - n_years_with_data = تعداد سال‌هایی که جفت رکورد دارد (برای
    تشخیص نوظهور/محوشده در task-11).

مصرف:
  python scripts/analyze_trend_5y.py
"""
from __future__ import annotations

import sys
import time
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from scipy import stats as sps

# دقت Decimal: 28 رقم معادل — طبق conventions §۴.۲ و Decision-003
getcontext().prec = 28

REPO_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO_ROOT / "05-Data" / "processed"
SOURCE_PARQUET = PROCESSED_DIR / "exports_1400-1405.parquet"
OUT_PARQUET = PROCESSED_DIR / "trend-analysis-5y.parquet"
OUT_SUMMARY = PROCESSED_DIR / "trend-analysis-summary.md"

YEARS = [1400, 1401, 1402, 1403, 1404]
N_YEARS = len(YEARS)
X_CENTERED = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])  # سال‌ها حول 1402
SXX = float((X_CENTERED**2).sum())  # = 10
DEC_10K = Decimal(10000)
TOL = Decimal("1e-6")  # 0.0001٪


# ۱۰۰ هزار دلار در واحدهای int64 (×1e-4 USD) — آستانه Decision-010
MIN_BASE_UNITS = 1_000_000_000  # = 100,000 USD
NEAR_ZERO_UNITS = 1_000_000  # = 100 USD (≈ صفر)


# ----------------------------------------------------------------------------
# ابزار دقیق: decimal128(20,4) → int64 (واحد 1e-4 USD) → Decimal
# ----------------------------------------------------------------------------
def value_col_to_units(series: pd.Series) -> np.ndarray:
    """ستون decimal128(20,4) → آرایه int64 با واحد 1e-4 دلار (تبدیل exact).

    Decimal.scaleb(4) دقیقاً ×10^4 می‌کند (بدون خطای گردکردن، چون حداکثر
    ۲۰ رقم دارد < prec 28)؛ int() هم دقیق است.
    """
    return np.fromiter(
        (int(d.scaleb(4)) for d in series), dtype=np.int64, count=len(series)
    )


def units_to_decimal(units: int) -> Decimal:
    """int64 (واحد 1e-4 USD) → Decimal دلار (exact)."""
    return Decimal(units) / DEC_10K
def mann_kendall_pvalue_matrix(y: np.ndarray) -> np.ndarray:
    """Mann-Kendall p-value برای ماتریس (N, 5) — s و tie correction.

    s و p به‌صورت vectorized؛ tie correction با حلقه سبک روی ردیف‌ها
    (Counter روی ۵ عضو). برگشت p-value دوطرفه (two-sided).
    """
    n = y.shape[1]
    # --- S statistic: جمع sign(y_j - y_i) برای همه (i<j) — vectorized ---
    s = np.zeros(len(y), dtype=np.int64)
    for i in range(n - 1):
        for j in range(i + 1, n):
            s += np.sign(y[:, j] - y[:, i]).astype(np.int64)

    # --- tie correction: Σ t(t-1)(2t+5) روی گروه‌های t>1 ---
    tie = np.zeros(len(y), dtype=np.float64)
    for r in range(len(y)):
        counts = Counter(y[r].tolist()).values()
        tie[r] = sum(t * (t - 1) * (2 * t + 5) for t in counts if t > 1)

    var_s = (n * (n - 1) * (2 * n + 5) - tie) / 18.0

    # --- z و p ---
    z = np.zeros(len(y), dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = s > 0
        neg = s < 0
        z[pos] = (s[pos] - 1) / np.sqrt(var_s[pos])
        z[neg] = (s[neg] + 1) / np.sqrt(var_s[neg])
        # s == 0 یا var_s == 0 (همه برابر) → z = 0 → p = 1
    p = 2.0 * (1.0 - sps.norm.cdf(np.abs(z)))
    p = np.clip(p, 0.0, 1.0)
    p[~np.isfinite(p)] = 1.0
    return p


# ----------------------------------------------------------------------------
# مرحله ۱: بارگذاری داده (بدون هیچ فیلتری)
# ----------------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    tbl = pq.read_table(
        SOURCE_PARQUET,
        columns=[
            "year",
            "hs_code",
            "hs_description",
            "destination_country_iso2",
            "destination_country_fa",
            "export_value_usd",
        ],
    )
    df = tbl.to_pandas()
    df["value_units"] = value_col_to_units(df["export_value_usd"])
    df.drop(columns=["export_value_usd"], inplace=True)
    print(f"[load] {len(df):,} رکورد از {SOURCE_PARQUET.name}")
    return df


# ----------------------------------------------------------------------------
# مرحله ۲: aggregate سالانه (exact در int64)
# ----------------------------------------------------------------------------
def aggregate_to_yearly(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby(["hs_code", "destination_country_iso2", "year"], sort=False)[
            "value_units"
        ]
        .sum()
        .reset_index(name="units")
    )
    print(f"[aggregate] {len(g):,} ردیف (hs × country × year)")
    return g


# ----------------------------------------------------------------------------
# مرحله ۳: pivot + ستون‌های توصیفی
# ----------------------------------------------------------------------------
def build_pairs(df: pd.DataFrame, yearly: pd.DataFrame) -> pd.DataFrame:
    # hs_description: پرتکرارترین شرح برای هر hs_code (deterministic:
    # n نزولی، سپس شرح صعودی — برای ۳,۸۳۳ کد با بیش از یک شرح)
    desc = (
        df.groupby(["hs_code", "hs_description"])
        .size()
        .reset_index(name="n")
        .sort_values(["hs_code", "n", "hs_description"],
                     ascending=[True, False, True])
        .drop_duplicates("hs_code")[["hs_code", "hs_description"]]
    )
    # نام فارسی کشور: یکتا برای هر iso2 (اعتبارسنجی‌شده)
    cname = (
        df.groupby("destination_country_iso2")["destination_country_fa"]
        .first()
        .reset_index()
    )

    piv = yearly.pivot_table(
        index=["hs_code", "destination_country_iso2"],
        columns="year",
        values="units",
        aggfunc="sum",
    ).reindex(columns=YEARS)
    piv.columns = [f"value_{y}" for y in YEARS]
    piv = piv.fillna(0).astype("int64").reset_index()

    # n_years_with_data: تعداد سال‌های دارای رکورد (قبل از zero-fill)
    n_years = (
        yearly.groupby(["hs_code", "destination_country_iso2"])["year"]
        .nunique()
        .rename("n_years_with_data")
    )
    piv = piv.merge(n_years, on=["hs_code", "destination_country_iso2"], how="left")

    piv = piv.merge(desc, on="hs_code", how="left")
    piv = piv.merge(
        cname, on="destination_country_iso2", how="left"
    )

    # حذف جفت‌های تمام-صفر (طبق task-10 §۴) — انتظار: ۰ جفت
    total_units = piv[[f"value_{y}" for y in YEARS]].sum(axis=1)
    n_zero = int((total_units == 0).sum())
    if n_zero:
        piv = piv[total_units > 0].copy()
    print(f"[pairs] {len(piv):,} جفت یکتا (HS × Country) | حذف تمام-صفر: {n_zero}")

    # مرتب‌سازی deterministic
    piv = piv.sort_values(
        ["hs_code", "destination_country_iso2"], kind="mergesort"
    ).reset_index(drop=True)
    return piv


# ----------------------------------------------------------------------------
# مرحله ۴: شاخص‌های float (vectorized) — slope، R²، MK، CV، ...
# ----------------------------------------------------------------------------
def compute_statistical_metrics(pairs: pd.DataFrame) -> pd.DataFrame:
    y = pairs[[f"value_{y}" for y in YEARS]].to_numpy(dtype=np.float64)
    n_rows = len(pairs)

    # --- OLS slope روی ۵ نقطه (vectorized): slope = Σ(x·y)/Σ(x²) ---
    sxy = y @ X_CENTERED
    slope = sxy / SXX

    # --- R² = Sxy² / (Sxx · SS_tot) ؛ سری ثابت → slope=0, R²=0 ---
    ss_tot = ((y - y.mean(axis=1, keepdims=True)) ** 2).sum(axis=1)
    constant = ss_tot <= 0.0
    r_squared = np.zeros(n_rows, dtype=np.float64)
    non_const = ~constant
    r_squared[non_const] = (sxy[non_const] ** 2) / (SXX * ss_tot[non_const])
    slope[constant] = 0.0

    # --- Mann-Kendall p-value (با tie correction) ---
    mk_p = mann_kendall_pvalue_matrix(y)

    # --- CV = std(ddof=1) / mean (mean>0) ---
    mean_v = y.mean(axis=1)
    std_v = np.sqrt(ss_tot / (N_YEARS - 1))
    cv = np.full(n_rows, np.nan)
    has_mean = mean_v > 0
    cv[has_mean] = std_v[has_mean] / mean_v[has_mean]

    # --- trend_consistency: تعداد گذارهای سال‌به‌سال با رشد (۰..۴) ---
    diffs = np.diff(y, axis=1)
    trend_consistency = (diffs > 0).sum(axis=1).astype(np.int32)

    # --- mean_recent_3y: میانگین 1402, 1403, 1404 ---
    mean_recent_3y = y[:, 2:].mean(axis=1)

    # --- تبدیل واحد: محاسبات روی واحدهای int64 (×1e-4 USD) انجام شد؛
    # شاخص‌های وابسته به مقیاس → دلار (÷10,000). cv/r²/MK/consistency
    # مقیاس‌ناوابسته‌اند و نیازی به تبدیل ندارند. ---
    slope = slope / 10_000.0  # USD در سال
    mean_v = mean_v / 10_000.0  # USD
    mean_recent_3y = mean_recent_3y / 10_000.0  # USD

    pairs = pairs.copy()
    pairs["slope"] = slope
    pairs["r_squared"] = r_squared
    pairs["mk_p_value"] = mk_p
    pairs["cv"] = cv
    pairs["trend_consistency"] = trend_consistency
    pairs["mean_value"] = mean_v
    pairs["mean_recent_3y"] = mean_recent_3y
    print("[stats] شاخص‌های آماری (slope/R²/MK/CV/...) محاسبه شد — vectorized")
    return pairs


# ----------------------------------------------------------------------------
# مرحله ۵: شاخص‌های Decimal (cagr_5y, pct_change_5y, growth_multiplier)
# ----------------------------------------------------------------------------
def compute_decimal_metrics(pairs: pd.DataFrame) -> pd.DataFrame:
    """CAGR / pct_change / growth_multiplier با Decimal(prec 28).

    قواعد (task-10 + conventions §۴.۲.۲):
      - v1400 > 0 و v1404 > 0 → cagr_5y = (v4/v0)^(1/4) - 1
      - v1400 > 0              → pct_change_5y، growth_multiplier
      - در غیر این صورت → NULL (NaN در float64)
    """
    n = len(pairs)
    cagr = np.full(n, np.nan)
    pct = np.full(n, np.nan)
    mult = np.full(n, np.nan)

    u0 = pairs["value_1400"].to_numpy()
    u4 = pairs["value_1404"].to_numpy()

    one = Decimal(1)
    quarter = Decimal(1) / Decimal(4)

    n_cagr = 0
    n_pct = 0
    for i in range(n):
        i0 = int(u0[i])
        i4 = int(u4[i])
        if i0 <= 0:
            continue  # v1400 == 0 → هر سه شاخص NULL
        d0 = Decimal(i0) / DEC_10K
        d4 = Decimal(i4) / DEC_10K
        # --- pct_change_5y و growth_multiplier ---
        pct[i] = float((d4 - d0) / d0 * Decimal(100))
        mult[i] = float(d4 / d0)
        n_pct += 1
        # --- cagr_5y ---
        if i4 > 0:
            cagr[i] = float((d4 / d0) ** quarter - one)
            n_cagr += 1

    pairs = pairs.copy()
    pairs["cagr_5y"] = cagr
    pairs["cagr_6y"] = np.nan  # Issue-008: بدون داده 1405 → همیشه NULL
    pairs["pct_change_5y"] = pct
    pairs["growth_multiplier"] = mult
    print(
        f"[decimal] cagr_5y: {n_cagr:,} قابل محاسبه | "
        f"pct_change/multiplier: {n_pct:,} | NULL (v1400=0): {n - n_pct:,}"
    )
    return pairs


# ----------------------------------------------------------------------------
# مرحله ۶: خروجی Parquet
# ----------------------------------------------------------------------------
OUTPUT_COLUMNS = [
    "hs_code",
    "destination_country_iso2",
    "hs_description",
    "destination_country_fa",
    "value_1400",
    "value_1401",
    "value_1402",
    "value_1403",
    "value_1404",
    "cagr_5y",
    "cagr_6y",
    "pct_change_5y",
    "growth_multiplier",
    "slope",
    "r_squared",
    "mk_p_value",
    "cv",
    "trend_consistency",
    "mean_value",
    "mean_recent_3y",
    "n_years_with_data",
]


def write_parquet(pairs: pd.DataFrame) -> None:
    out = pairs[OUTPUT_COLUMNS].copy()
    # واحدها → دلار float64 (ذخیره float64 طبق طرح خروجی؛ دقت جمع
    # در تست مستقل تضمین می‌شود — خطای نسبی float64 ~1e-16)
    for y in YEARS:
        out[f"value_{y}"] = out[f"value_{y}"].to_numpy(dtype=np.float64) / 10_000.0
    out["n_years_with_data"] = out["n_years_with_data"].astype(np.int32)
    out["trend_consistency"] = out["trend_consistency"].astype(np.int32)

    schema = pa.schema(
        [
            pa.field("hs_code", pa.string()),
            pa.field("destination_country_iso2", pa.string()),
            pa.field("hs_description", pa.string()),
            pa.field("destination_country_fa", pa.string()),
            *[pa.field(f"value_{y}", pa.float64()) for y in YEARS],
            pa.field("cagr_5y", pa.float64()),
            pa.field("cagr_6y", pa.float64()),
            pa.field("pct_change_5y", pa.float64()),
            pa.field("growth_multiplier", pa.float64()),
            pa.field("slope", pa.float64()),
            pa.field("r_squared", pa.float64()),
            pa.field("mk_p_value", pa.float64()),
            pa.field("cv", pa.float64()),
            pa.field("trend_consistency", pa.int32()),
            pa.field("mean_value", pa.float64()),
            pa.field("mean_recent_3y", pa.float64()),
            pa.field("n_years_with_data", pa.int32()),
        ]
    )
    table = pa.Table.from_pandas(out, schema=schema, preserve_index=False)
    pq.write_table(table, OUT_PARQUET, compression="snappy")
    size_mb = OUT_PARQUET.stat().st_size / 1024 / 1024
    print(f"[write] {OUT_PARQUET.name} — {len(out):,} ردیف × {len(out.columns)} ستون ({size_mb:.1f} MB, snappy)")


# ----------------------------------------------------------------------------
# مرحله ۷: گزارش خلاصه
# ----------------------------------------------------------------------------
def fmt_fa(x: float, digits: int = 2) -> str:
    return f"{x:,.{digits}f}"


def write_summary(pairs: pd.DataFrame, prec: dict, elapsed: float) -> None:
    n = len(pairs)
    full5 = int((pairs["n_years_with_data"] == 5).sum())
    tot_units = {y: int(pairs[f"value_{y}"].sum()) for y in YEARS}
    grand = sum(tot_units.values())

    lines = []
    a = lines.append
    a("---")
    a("type: data")
    a("title: گزارش تحلیل روند ۵ ساله — task-10")
    a(f"created: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}")
    a("updated: " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"))
    a("status: review")
    a("tags:")
    a("  - data")
    a("  - analysis")
    a("  - task-10")
    a("  - trend")
    a("---")
    a("")
    a("# تحلیل روند ۵ ساله — تمامی جفت‌های (HS Code × Country)")
    a("")
    a("**Agent**: analyst | **اسکریپت**: `scripts/analyze_trend_5y.py`")
    a(f"**تاریخ تولید**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} (UTC)")
    a(f"**زمان اجرا**: {elapsed:.1f} ثانیه | **موتور دقت**: Decimal(prec 28)")
    a("")
    a("> ⚠️ طبق Issue-008، سال ۱۴۰۵ در منبع موجود نیست؛ تحلیل روی **۵ سال کامل")
    a("> (۱۴۰۰-۱۴۰۴)** انجام شد و `cagr_6y` عمداً NULL است (N=4 برای CAGR).")
    a("> طبق Issue-006، سال‌های ۱۴۰۳/۱۴۰۴ تفکیک ماهانه ندارند که در تحلیل")
    a("> سالانه بی‌اثر است.")
    a("")
    a("## ۱. آمار کلی")
    a("")
    a("| شاخص | مقدار |")
    a("|------|-------|")
    a(f"| تعداد کل جفت‌های (HS × Country) | **{n:,}** |")
    a(f"| جفت‌های با داده در هر ۵ سال | {full5:,} ({100.0 * full5 / n:.1f}٪) |")
    a(f"| تعداد HS Code یکتا | {pairs['hs_code'].nunique():,} |")
    a(f"| تعداد کشور مقصد یکتا | {pairs['destination_country_iso2'].nunique():,} |")
    a(f"| مجموع ارزش ۵ ساله (USD) | {units_to_decimal(grand):,} |")
    a("")
    a("### پوشش سال‌های داده")
    a("")
    a("| تعداد سالِ دارای داده | جفت‌ها | درصد |")
    a("|------|-------|-------|")
    vc = pairs["n_years_with_data"].value_counts().sort_index()
    for k, v in vc.items():
        a(f"| {k} | {v:,} | {100.0 * v / n:.1f}٪ |")
    a("")
    a("## ۲. جمع ارزش سالانه و تست دقت")
    a("")
    a("تلورانس < 0.0001٪ (طبق conventions §۴.۲). جمع‌ها exact از واحدهای int64")
    a("(×1e-4 USD) محاسبه شده‌اند.")
    a("")
    a("| سال | جمع خروجی (USD) | تلورانس | نتیجه |")
    a("|-----|-----------------|---------|-------|")
    for y in YEARS:
        r = prec[y]
        a(
            f"| {y} | {r['output']:,} | "
            f"{float(r['tolerance']):.12f} | "
            f"{'✅ PASS' if r['passed'] else '❌ FAIL'} |"
        )
    a(f"| **مجموع** | **{units_to_decimal(grand):,}** | — | — |")
    a("")
    a("## ۳. آمار توصیفی شاخص‌ها")
    a("")
    desc_cols = [
        "cagr_5y", "pct_change_5y", "growth_multiplier", "slope",
        "r_squared", "mk_p_value", "cv", "trend_consistency",
        "mean_value", "mean_recent_3y",
    ]
    a("| شاخص | تعداد | میانگین | میانه | کمینه | بیشینه |")
    a("|------|-------|---------|-------|-------|--------|")
    for c in desc_cols:
        s = pairs[c]
        if c in ("trend_consistency",):
            a(
                f"| {c} | {int(s.notna().sum()):,} | {s.mean():.2f} | "
                f"{s.median():.0f} | {int(s.min())} | {int(s.max())} |"
            )
        else:
            a(
                f"| {c} | {int(s.notna().sum()):,} | {fmt_fa(s.mean(), 4)} | "
                f"{fmt_fa(s.median(), 4)} | {fmt_fa(s.min(), 4)} | "
                f"{fmt_fa(s.max(), 4)} |"
            )
    a("")
    a(f"- جفت‌های با `cagr_5y = NULL`: {int(pairs['cagr_5y'].isna().sum()):,} "
      f"(v1400=0: {int((pairs['value_1400'] == 0).sum()):,} + "
      f"v1400>0 اما v1404=0: "
      f"{int(((pairs['value_1400'] > 0) & (pairs['value_1404'] == 0)).sum()):,})")
    a(f"- جفت‌های با `cv = NULL` (میانگین ≤ 0): {int(pairs['cv'].isna().sum()):,}")
    a("")

    # --- Top 10 CAGR (با فیلتر پایه معقول ≥ 100K دلار — Decision-010) ---
    a("## ۴. Top 10 رشد — CAGR (v1400 ≥ 100,000 دلار)")
    a("")
    a("فیلتر حداقل ارزش پایه برای حذف نویز جفت‌های ریز (`threshold_emerging_disappearing`")
    a("از Decision-010).")
    a("")
    base_ok = pairs[pairs["value_1400"] >= MIN_BASE_UNITS]
    top = base_ok.nlargest(10, "cagr_5y")
    a("| # | HS Code | شرح کالا | کشور | v1400 (USD) | v1404 (USD) | CAGR ۵y | ضریب رشد |")
    a("|---|---------|----------|------|-------------|-------------|---------|-----------|")
    for i, (_, r) in enumerate(top.iterrows(), 1):
        a(
            f"| {i} | {r['hs_code']} | {str(r['hs_description'])[:40]} | "
            f"{r['destination_country_iso2']} | "
            f"{int(r['value_1400']) / 10_000:,.0f} | "
            f"{int(r['value_1404']) / 10_000:,.0f} | "
            f"{r['cagr_5y'] * 100:.1f}٪ | {r['growth_multiplier']:.1f}× |"
        )
    a("")
    # --- Top 10 slope ---
    a("## ۵. Top 10 شدت روند — OLS slope (USD/سال)")
    a("")
    top_s = pairs.nlargest(10, "slope")
    a("| # | HS Code | شرح کالا | کشور | slope | R² | MK p | v1400 → v1404 (USD) |")
    a("|---|---------|----------|------|-------|----|------|---------------------|")
    for i, (_, r) in enumerate(top_s.iterrows(), 1):
        a(
            f"| {i} | {r['hs_code']} | {str(r['hs_description'])[:40]} | "
            f"{r['destination_country_iso2']} | {r['slope']:,.0f} | "
            f"{r['r_squared']:.2f} | {r['mk_p_value']:.3f} | "
            f"{int(r['value_1400']) / 10_000:,.0f} → {int(r['value_1404']) / 10_000:,.0f} |"
        )
    a("")

    # --- پیش‌نمایش طبقه‌بندی (task-11) ---
    a("## ۶. پیش‌نمایش طبقات روند (آماده‌سازی task-11)")
    a("")
    a("شمارش با آستانه‌های Decision-010 (فقط پیش‌نمایش — طبقه‌بندی رسمی و")
    a("اولویت‌بندی دسته‌ها در task-11 انجام می‌شود):")
    a("")
    c = pairs
    strong = (
        (c["cagr_5y"] > 0.10) & (c["mk_p_value"] < 0.05) & (c["slope"] > 0)
    )
    moderate = (
        (c["cagr_5y"] > 0) & (c["cagr_5y"] <= 0.10) & (c["mk_p_value"] < 0.10)
    )
    stable = (c["cagr_5y"].abs() <= 0.02) & (c["r_squared"] < 0.3)
    volatile = (c["cv"] > 0.5) & (c["r_squared"] < 0.3)
    declining = (c["cagr_5y"] < 0) & (c["mk_p_value"] < 0.10)
    emerging = (c["value_1400"] == 0) & (c["value_1404"] >= MIN_BASE_UNITS)
    disappearing = (
        (c["value_1400"] >= MIN_BASE_UNITS) & (c["value_1404"] < NEAR_ZERO_UNITS)
    )
    a("| دسته (پیش‌نمایش) | معیار خلاصه | تعداد |")
    a("|------------------|-------------|-------|")
    a(f"| رشد قوی (strong_growth) | CAGR>10٪ & MK p<0.05 & slope>0 | **{int(strong.sum()):,}** |")
    a(f"| رشد متوسط (moderate_growth) | 0<CAGR≤10٪ & MK p<0.1 | {int(moderate.sum()):,} |")
    a(f"| پایدار (stable) | \\|CAGR\\|≤2٪ & R²<0.3 | {int(stable.sum()):,} |")
    a(f"| نوسانی (volatile) | CV>0.5 & R²<0.3 | {int(volatile.sum()):,} |")
    a(f"| کاهشی (declining) | CAGR<0 & MK p<0.1 | {int(declining.sum()):,} |")
    a(f"| نوظهور (emerging) | v1400=0 & v1404≥100K$ | **{int(emerging.sum()):,}** |")
    a(f"| محوشده (disappearing) | v1400≥100K$ & v1404≈0 | {int(disappearing.sum()):,} |")
    a("")
    a("> ⚠️ دسته‌ها انحصاری متقابل نیستند (طبقه‌بندی با اولویت در task-11).")
    a("")

    a("## ۷. نکات کیفی داده")
    a("")
    a(f"- جفت‌های با فقط ۱ سال داده: {int((pairs['n_years_with_data'] == 1).sum()):,} —")
    a("  CAGR آن‌ها NULL است؛ برای تشخیص نوظهور/محوشده در task-11 استفاده می‌شوند.")
    a(f"- جفت‌های شروع‌شده از صفر (v1400=0): {int((pairs['value_1400'] == 0).sum()):,} —")
    a("  مصادیق بالقوی از دسته «نوظهور».")
    a(f"- جفت‌های ختم‌شده به صفر (v1404=0): {int((pairs['value_1404'] == 0).sum()):,} —")
    a("  مصادیق بالقوی از دسته «محوشده».")
    a("- `hs_description` برای ۳,۸۳۳ کد بیش از یک شرح دارد؛ پرتکرارترین شرح")
    a("  انتخاب شد (deterministic).")
    a("- نام فارسی کشور برای هر iso2 یکتاست (اعتبارسنجی‌شده در pre-flight).")
    a("")
    a("## ۸. فایل‌های خروجی")
    a("")
    a(f"- `05-Data/processed/trend-analysis-5y.parquet` — {n:,} ردیف × {len(OUTPUT_COLUMNS)} ستون (snappy)")
    a("- `05-Data/processed/trend-analysis-summary.md` — همین گزارش")
    a("- تست مستقل: `scripts/test_trend_precision.py` (tol < 1e-6)")
    a("")
    a("## 🔗 تسک‌های وابسته")
    a("")
    a("- [[task-11-trend-classification]] — طبقه‌بندی ۷ دسته + اعتبارسنجی آماری")
    a("- [[task-12-export-candidates]] — رتبه‌بندی کاندیدها با export_score")
    a("- [[task-06-qa-validate]] — QA نهایی")

    OUT_SUMMARY.write_text("\n".join(lines), encoding="utf-8")
    print(f"[summary] {OUT_SUMMARY.name} نوشته شد ({len(lines)} خط)")


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() -> int:
    t0 = time.time()
    print("=" * 72)
    print("task-10 — تحلیل جامع روند ۵ ساله (تمام HS × تمام کشورها)")
    print("=" * 72)

    df = load_data()
    yearly = aggregate_to_yearly(df)
    pairs = build_pairs(df, yearly)
    df_units_per_year = df.groupby("year")["value_units"].sum()

    pairs = compute_statistical_metrics(pairs)
    pairs = compute_decimal_metrics(pairs)

    print("\n[precision] تست دقت داخلی (exact، واحد int64):")
    # بازسازی دقیق source per-year برای مقایسه
    src = {y: int(v) for y, v in df_units_per_year.items()}
    all_pass = True
    prec = {}
    for y in YEARS:
        src_dec = units_to_decimal(src.get(y, 0))
        out_dec = units_to_decimal(int(pairs[f"value_{y}"].sum()))
        tol = (
            abs(out_dec - src_dec) / src_dec if src_dec != 0 else Decimal(0)
        )
        passed = tol < TOL
        prec[y] = {
            "source": src_dec,
            "output": out_dec,
            "tolerance": tol,
            "passed": passed,
        }
        all_pass = all_pass and passed
        print(
            f"  year {y}: src={src_dec:,} out={out_dec:,} "
            f"tol={float(tol):.12f} [{'PASS' if passed else 'FAIL'}]"
        )
    if not all_pass:
        print("\n❌ تست دقت داخلی FAIL — خروجی نوشته نمی‌شود.")
        return 1

    write_parquet(pairs)
    write_summary(pairs, prec, time.time() - t0)

    print(f"\n✅ انجام شد در {time.time() - t0:.1f} ثانیه")
    print(f"   خروجی: {OUT_PARQUET}")
    print(f"   خلاصه:  {OUT_SUMMARY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
