#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task-11 — طبقه‌بندی روند به ۷ دسته + تجمیع به سطح HS Code
============================================================

طبقه‌بندی هر جفت (HS × Country) به یکی از ۷ دسته روند طبق
`conventions.md` §۵.۱ و `recipe-09` §۵، با آستانه‌های Decision-010.

ترتیب شرط‌ها (حیاتی — طبق recipe-09 §۵):
  1. emerging        : v1400 == 0 و v1404 > 100K$
  2. disappearing    : v1400 > 100K$ و v1404 < 10K$ (THRESHOLD/10)
  3. insufficient_data: cagr_5y قابل محاسبه نیست (NULL)
  4. strong_growth   : cagr > 10٪ و mk_p < 0.05 و slope > 0
  5. moderate_growth : 0 < cagr ≤ 10٪ و mk_p < 0.1
  6. declining       : cagr < 0 و mk_p < 0.1
  7. volatile        : cv > 0.5 و r² < 0.3  (قبل از stable)
  8. stable          : |cagr| ≤ 2٪ و r² < 0.3
  9. weak_growth / weak_decline / stable (cagr == 0)

خروجی‌ها:
  - 05-Data/processed/trend-classification.parquet
  - 05-Data/processed/trend-classification-by-hs.parquet
  - 06-Analysis/trend/_classification-summary.md

هشدار آماری (از task-10): با n=5، حداقل p-value ممکن در Mann-Kendall
≈ 0.0275 است؛ شرط mk_p < 0.05 یعنی سری کاملاً یکنواخت. mk_p < 0.01
قابل دستیابی نیست. در گزارش خلاصه مستند می‌شود.

مصرف:
  python scripts/classify_trends.py
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "05-Data/processed/trend-analysis-5y.parquet"
OUTPUT_PAIRS_PATH = REPO_ROOT / "05-Data/processed/trend-classification.parquet"
OUTPUT_HS_PATH = REPO_ROOT / "05-Data/processed/trend-classification-by-hs.parquet"
SUMMARY_PATH = REPO_ROOT / "06-Analysis/trend/_classification-summary.md"

YEARS = [1400, 1401, 1402, 1403, 1404]

# --- آستانه‌ها (طبق Decision-010) ---
THRESHOLD = 100_000.0  # USD — برای emerging/disappearing
CAGR_STRONG = 0.10
CAGR_STABLE = 0.02
CV_VOLATILE = 0.5
R_SQUARED_CLEAR = 0.3
MK_SIGNIFICANT = 0.05
MK_MODERATE = 0.1

# دسته‌ها به ترتیب رسمی (برای گزارش‌ها و tie-breaking در dominant_trend)
CATEGORIES = [
    "strong_growth", "moderate_growth", "weak_growth", "stable",
    "volatile", "declining", "weak_decline", "emerging",
    "disappearing", "insufficient_data",
]

CATEGORY_FA = {
    "strong_growth": "رشد قوی",
    "moderate_growth": "رشد متوسط",
    "weak_growth": "رشد ضعیف",
    "stable": "پایدار",
    "volatile": "نوسانی",
    "declining": "کاهشی",
    "weak_decline": "کاهش ضعیف",
    "emerging": "نوظهور",
    "disappearing": "محوشده",
    "insufficient_data": "داده ناکافی",
}

# پیش‌نمایش task-10 (برای مقایسه خطایابانه؛ ملاحظه: معیار پیش‌نمایش
# محوشده v1404 < 100$ بود اما الگوریتم رسمی v1404 < THRESHOLD/10 = 10K$)
TASK10_PREVIEW = {
    "strong_growth": 340,
    "moderate_growth": 20,
    "stable": 535,
    "volatile": 25_283,
    "declining": 904,
    "emerging": 1_686,
    "disappearing": 1_593,
}


# ----------------------------------------------------------------------------
# طبقه‌بندی (vectorized با ماسک‌های اولویت‌دار)
# ----------------------------------------------------------------------------
def classify_all_pairs(df: pd.DataFrame) -> pd.DataFrame:
    """اعمال الگوریتم طبقه‌بندی روی همه جفت‌ها (ترتیب شرط‌ها حیاتی)."""
    n = len(df)
    v0 = df["value_1400"].fillna(0.0).to_numpy(dtype=np.float64)
    v4 = df["value_1404"].fillna(0.0).to_numpy(dtype=np.float64)
    cagr = df["cagr_5y"].to_numpy(dtype=np.float64)  # NaN مجاز
    mk_p = df["mk_p_value"].fillna(1.0).to_numpy(dtype=np.float64)
    slope = df["slope"].fillna(0.0).to_numpy(dtype=np.float64)
    r2 = df["r_squared"].fillna(0.0).to_numpy(dtype=np.float64)
    cv = df["cv"].fillna(0.0).to_numpy(dtype=np.float64)

    category = np.empty(n, dtype=object)
    confidence = np.zeros(n, dtype=np.float64)
    is_sig = np.zeros(n, dtype=bool)

    remaining = np.ones(n, dtype=bool)

    def assign(mask: np.ndarray, cat: str, conf: np.ndarray | float,
               sig: bool) -> None:
        nonlocal remaining
        take = mask & remaining
        category[take] = cat
        if isinstance(conf, np.ndarray):
            confidence[take] = conf[take]
        else:
            confidence[take] = conf
        if isinstance(sig, np.ndarray):
            is_sig[take] = sig[take]
        else:
            is_sig[take] = sig
        remaining &= ~take

    # 1. نوظهور
    assign((v0 == 0.0) & (v4 > THRESHOLD), "emerging", 1.0, True)
    # 2. محوشده
    assign((v0 > THRESHOLD) & (v4 < THRESHOLD / 10.0), "disappearing", 1.0, True)
    # 3. داده ناکافی (CAGR = NULL)
    assign(np.isnan(cagr), "insufficient_data", 0.0, False)

    # از اینجا به بعد CAGR عددی است
    conf_rest = np.clip(1.0 - mk_p, 0.0, 1.0)
    sig_rest = mk_p < MK_SIGNIFICANT
    have_cagr = ~np.isnan(cagr)

    # 4. رشد قوی
    assign(have_cagr & (cagr > CAGR_STRONG) & (mk_p < MK_SIGNIFICANT)
           & (slope > 0), "strong_growth", conf_rest, True)
    # 5. رشد متوسط
    assign(have_cagr & (cagr > 0) & (cagr <= CAGR_STRONG) & (mk_p < MK_MODERATE),
           "moderate_growth", conf_rest, sig_rest)
    # 6. کاهشی
    assign(have_cagr & (cagr < 0) & (mk_p < MK_MODERATE),
           "declining", conf_rest, sig_rest)
    # 7. نوسانی (قبل از پایدار)
    assign(have_cagr & (cv > CV_VOLATILE) & (r2 < R_SQUARED_CLEAR),
           "volatile", conf_rest, False)
    # 8. پایدار
    assign(have_cagr & (np.abs(cagr) <= CAGR_STABLE) & (r2 < R_SQUARED_CLEAR),
           "stable", conf_rest, False)
    # 9. باقیمانده: رشد ضعیف / کاهش ضعیف / پایدار (cagr == 0)
    assign(have_cagr & (cagr > 0), "weak_growth", conf_rest, False)
    assign(have_cagr & (cagr < 0), "weak_decline", conf_rest, False)
    assign(np.ones(n, dtype=bool), "stable", conf_rest, False)

    # --- n_signs: کد ۴ کاراکتری [علامت CAGR][علامت slope][MK][CV] ---
    def sign_code(arr: np.ndarray) -> np.ndarray:
        out = np.full(len(arr), "0", dtype=object)
        out[arr > 0] = "+"
        out[arr < 0] = "-"
        return out

    mk_code = np.full(n, "n", dtype=object)
    mk_code[mk_p < MK_SIGNIFICANT] = "s"
    mk_code[(mk_p >= MK_SIGNIFICANT) & (mk_p < MK_MODERATE)] = "m"
    cv_code = np.where(cv > CV_VOLATILE, "v", "d")
    n_signs = np.char.add(
        np.char.add(sign_code(cagr), sign_code(slope)),
        np.char.add(mk_code.astype(str), cv_code.astype(str)),
    )

    # --- recommendation_action ---
    action_map = {
        "strong_growth": "select", "emerging": "select",
        "moderate_growth": "monitor", "weak_growth": "monitor",
        "declining": "avoid", "disappearing": "avoid",
        "volatile": "investigate", "stable": "investigate",
        "weak_decline": "investigate", "insufficient_data": "investigate",
    }

    out = df.copy()
    out["trend_category"] = category
    out["confidence"] = confidence
    out["is_significant"] = is_sig
    out["n_signs"] = n_signs
    out["recommendation_action"] = pd.Series(category).map(action_map).to_numpy()
    print(f"[classify] {n:,} جفت طبقه‌بندی شد")
    return out


# ----------------------------------------------------------------------------
# تجمیع به سطح HS Code
# ----------------------------------------------------------------------------
def aggregate_by_hs(df: pd.DataFrame) -> pd.DataFrame:
    """تجمیع جفت‌ها به سطح HS Code (یک ردیف به ازای هر HS)."""
    value_cols = [f"value_{y}" for y in YEARS]
    df = df.copy()
    df["total_value_5y"] = df[value_cols].sum(axis=1)

    # شمارش دسته‌ها (crosstab — سریع‌تر و تمیزتر از lambda در agg)
    ct = pd.crosstab(df["hs_code"], df["trend_category"])
    ct.columns = [f"n_{c}" for c in ct.columns]
    for cat in CATEGORIES:
        col = f"n_{cat}"
        if col not in ct.columns:
            ct[col] = 0
    ct = ct[[f"n_{c}" for c in CATEGORIES]].reset_index()

    grouped = df.groupby(["hs_code", "hs_description"]).agg(
        n_countries_total=("destination_country_iso2", "count"),
        total_value_5y=("total_value_5y", "sum"),
        total_value_1404=("value_1404", "sum"),
        agg_value_1400=("value_1400", "sum"),
        agg_value_1404=("value_1404", "sum"),
        mean_recent_3y_aggregated=("mean_recent_3y", "sum"),
        trend_consistency_aggregated=("trend_consistency", "mean"),
        cv_aggregated=("cv", "mean"),
        slope_aggregated=("slope", "sum"),
        n_growth_pairs=("is_significant", "sum"),
    ).reset_index()

    # کشورهای فعال در ۱۴۰۴ (با صادرات مثبت)
    active = (
        df[df["value_1404"] > 0]
        .groupby("hs_code")["destination_country_iso2"]
        .nunique()
        .rename("n_destinations_active")
        .reset_index()
    )

    by_hs = grouped.merge(ct, on="hs_code", how="left").merge(
        active, on="hs_code", how="left"
    )
    by_hs["n_destinations_active"] = by_hs["n_destinations_active"].fillna(0)

    # dominant_trend: دسته با بیشترین کشور (tie → اولین در ترتیب CATEGORIES)
    n_cols = [f"n_{c}" for c in CATEGORIES]
    by_hs["dominant_trend"] = by_hs[n_cols].idxmax(axis=1).str.removeprefix("n_")

    # growth_diversity_score
    by_hs["growth_diversity_score"] = (
        by_hs["n_strong_growth"] + by_hs["n_moderate_growth"]
        + by_hs["n_emerging"]
    ) / by_hs["n_countries_total"].clip(lower=1)

    # cagr_5y_aggregated از مجموع سالانه همه کشورها
    v0 = by_hs["agg_value_1400"].to_numpy(dtype=np.float64)
    v4 = by_hs["agg_value_1404"].to_numpy(dtype=np.float64)
    cagr_agg = np.full(len(by_hs), np.nan)
    ok = (v0 > 0) & (v4 > 0)
    cagr_agg[ok] = (v4[ok] / v0[ok]) ** 0.25 - 1.0
    by_hs["cagr_5y_aggregated"] = cagr_agg

    print(f"[aggregate] {len(by_hs):,} HS Code تجمیع شد")
    return by_hs


# ----------------------------------------------------------------------------
# اعتبارسنجی
# ----------------------------------------------------------------------------
def validate(df_in: pd.DataFrame, pairs: pd.DataFrame, by_hs: pd.DataFrame) -> list[str]:
    """بررسی‌های پذیرش — لیست خرابی‌ها (خالی = همه PASS)."""
    failures: list[str] = []

    # ۱. تعداد ردیف حفظ شده
    if len(pairs) != len(df_in):
        failures.append(f"rows {len(pairs)} != input {len(df_in)}")

    # ۲. هیچ NULL در trend_category
    n_null = int(pairs["trend_category"].isna().sum())
    if n_null:
        failures.append(f"NULL trend_category: {n_null}")

    # ۳. دسته‌ها معتبر
    bad = sorted(set(pairs["trend_category"].dropna()) - set(CATEGORIES))
    if bad:
        failures.append(f"invalid categories: {bad}")

    # ۴. جمع value_1404 حفظ شود
    s_in = float(df_in["value_1404"].sum())
    s_out = float(pairs["value_1404"].sum())
    if s_in > 0 and abs(s_out - s_in) / s_in > 1e-9:
        failures.append(f"value_1404 sum {s_out} != {s_in}")

    # ۵. جمع دسته‌ها == کل جفت‌ها
    total = int(pairs["trend_category"].value_counts().sum())
    if total != len(pairs):
        failures.append(f"category counts sum {total} != {len(pairs)}")

    # ۶. by_hs: تعداد HS یکتا
    if by_hs["hs_code"].nunique() != df_in["hs_code"].nunique():
        failures.append("by_hs hs_code count mismatch")

    # ۷. by_hs: جمع n_countries_total == تعداد جفت‌ها
    if int(by_hs["n_countries_total"].sum()) != len(pairs):
        failures.append("n_countries_total sum mismatch")

    # ۸. recommendation_action فقط مقادیر مجاز
    bad_act = sorted(set(pairs["recommendation_action"]) - {"select", "monitor", "avoid", "investigate"})
    if bad_act:
        failures.append(f"invalid actions: {bad_act}")

    return failures


# ----------------------------------------------------------------------------
# گزارش خلاصه
# ----------------------------------------------------------------------------
def generate_summary(pairs: pd.DataFrame, by_hs: pd.DataFrame,
                     failures: list[str], elapsed: float) -> None:
    n_total = len(pairs)
    cat_counts = pairs["trend_category"].value_counts().to_dict()
    n_is_sig = int(pairs["is_significant"].sum())
    n_mk_sig = int((pairs["mk_p_value"] < MK_SIGNIFICANT).sum())
    n_hs = len(by_hs)
    hs_dominant_counts = by_hs["dominant_trend"].value_counts().to_dict()
    n_hs_strong_any = int((by_hs["n_strong_growth"] > 0).sum())
    n_hs_strong_dom = int(hs_dominant_counts.get("strong_growth", 0))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    top_strong = pairs[pairs["trend_category"] == "strong_growth"].nlargest(10, "value_1404")
    top_emerging = pairs[pairs["trend_category"] == "emerging"].nlargest(10, "value_1404")
    top_declining = pairs[pairs["trend_category"] == "declining"].nlargest(10, "value_1404")
    top_hs_strong = by_hs[by_hs["dominant_trend"] == "strong_growth"].nlargest(10, "total_value_1404")

    L = []
    a = L.append
    a("---")
    a("type: analysis")
    a("title: خلاصه طبقه‌بندی روند (task-11)")
    a(f"created: {now.split(' ')[0]}")
    a(f"updated: {now}")
    a("status: review")
    a("tags:")
    a("  - analysis")
    a("  - trend")
    a("  - classification")
    a("  - task-11")
    a("folder: 06-Analysis/trend")
    a("---")
    a("")
    a("# خلاصه طبقه‌بندی روند (task-11)")
    a("")
    a(f"**تاریخ**: {now} (UTC) | **Agent**: Analyst")
    a("**Pipeline**: `scripts/classify_trends.py`")
    a("**منبع داده**: `trend-analysis-5y.parquet` (task-10)")
    a(f"**زمان اجرا**: {elapsed:.1f} ثانیه | آستانه‌ها: Decision-010")
    a("")
    a("## ۱. آمار کلی")
    a("")
    a("| شاخص | مقدار |")
    a("|------|-------|")
    a(f"| تعداد کل جفت‌های طبقه‌بندی‌شده | **{n_total:,}** |")
    a(f"| جفت‌های با پرچم `is_significant` (MK p<0.05 **یا** نوظهور/محوشده) | {n_is_sig:,} |")
    a(f"| جفت‌های با `mk_p_value < 0.05` (کاملاً یکنواخت) | {n_mk_sig:,} |")
    a(f"| تعداد HS Codeهای یکتا | {n_hs:,} |")
    a(f"| HS Code با حداقل یک کشور strong_growth | {n_hs_strong_any:,} |")
    a(f"| HS Code با `dominant_trend = strong_growth` | **{n_hs_strong_dom:,}** |")
    a("")
    a("## ۲. توزیع دسته‌های روند (جفت‌ها)")
    a("")
    a("| دسته | نام فارسی | تعداد | درصد |")
    a("|------|-----------|-------|-------|")
    for cat in CATEGORIES:
        c = cat_counts.get(cat, 0)
        a(f"| `{cat}` | {CATEGORY_FA[cat]} | {c:,} | {100.0 * c / n_total:.1f}٪ |")
    a("")
    a("### توصیه اقدام (recommendation_action)")
    a("")
    act_counts = pairs["recommendation_action"].value_counts().to_dict()
    a("| اقدام | معنی | جفت‌ها |")
    a("|-------|------|--------|")
    act_fa = {"select": "انتخاب برای task-12", "monitor": "پایش دوره‌ای",
              "avoid": "اجتناب/خروج", "investigate": "بررسی بیشتر"}
    for act in ["select", "monitor", "investigate", "avoid"]:
        a(f"| `{act}` | {act_fa[act]} | {act_counts.get(act, 0):,} |")
    a("")
    a("## ۳. توزیع دسته‌های غالب (HS Codeها)")
    a("")
    a("| دسته غالب | تعداد HS Code | درصد |")
    a("|-----------|----------------|-------|")
    for cat in CATEGORIES:
        c = hs_dominant_counts.get(cat, 0)
        a(f"| `{cat}` | {c:,} | {100.0 * c / n_hs:.1f}٪ |")
    a("")
    a("## ۴. ⚠️ هشدار آماری مهم (Mann-Kendall با n=5)")
    a("")
    a("با n=5 (۵ نقطه زمانی)، حداقل p-value ممکن در تست Mann-Kendall")
    a("**≈ ۰.۰۲۷۵** است (سری کاملاً یکنواخت). این یعنی:")
    a("- شرط `mk_p < 0.05` قابل رسیدن است (۰.۰۲۷۵ < ۰.۰۵) ✅")
    a("- اما شرط `mk_p < 0.01` قابل رسیدن نیست ❌")
    a(f"- تعداد جفت‌های با `mk_p < 0.05`: **{n_mk_sig:,}**")
    a("")
    a("**توصیه**: در task-12 (رتبه‌بندی)، شاخص `is_significant` را به‌عنوان")
    a("فیلتر یا وزن در نظر بگیر. power آزمون برای n=5 پایین است؛ معناداری")
    a("را در کنار CAGR/R²/ثبات تفسیر کن.")
    a("")
    a("## ۵. Top 10 جفت‌های با رشد قوی (strong_growth)")
    a("")
    a("| HS Code | کشور | شرح کالا | value_1404 (USD) | CAGR 5y | MK p |")
    a("|---------|------|----------|------------------|---------|------|")
    for _, r in top_strong.iterrows():
        a(f"| {r['hs_code']} | {r['destination_country_iso2']} | "
          f"{str(r['hs_description'])[:38]} | {r['value_1404']:,.0f} | "
          f"{r['cagr_5y']*100:.1f}٪ | {r['mk_p_value']:.4f} |")
    a("")
    a("## ۶. Top 10 جفت‌های نوظهور (emerging)")
    a("")
    a("| HS Code | کشور | شرح کالا | value_1400 | value_1404 (USD) |")
    a("|---------|------|----------|------------|------------------|")
    for _, r in top_emerging.iterrows():
        a(f"| {r['hs_code']} | {r['destination_country_iso2']} | "
          f"{str(r['hs_description'])[:38]} | {r['value_1400']:,.0f} | {r['value_1404']:,.0f} |")
    a("")
    a("## ۷. Top 10 جفت‌های کاهشی (declining)")
    a("")
    a("| HS Code | کشور | شرح کالا | value_1404 (USD) | CAGR 5y |")
    a("|---------|------|----------|------------------|---------|")
    for _, r in top_declining.iterrows():
        a(f"| {r['hs_code']} | {r['destination_country_iso2']} | "
          f"{str(r['hs_description'])[:38]} | {r['value_1404']:,.0f} | "
          f"{r['cagr_5y']*100:.1f}٪ |")
    a("")
    a("## ۸. Top 10 HS Code با دسته غالب strong_growth")
    a("")
    a("| HS Code | شرح | کشورها | total_value_1404 | CAGR agg | تنوع رشد |")
    a("|---------|------|--------|------------------|----------|-----------|")
    for _, r in top_hs_strong.iterrows():
        cagr = r.get("cagr_5y_aggregated")
        cagr_str = f"{cagr*100:.1f}٪" if pd.notna(cagr) else "N/A"
        a(f"| {r['hs_code']} | {str(r['hs_description'])[:38]} | "
          f"{int(r['n_countries_total'])} | {r['total_value_1404']:,.0f} | "
          f"{cagr_str} | {r['growth_diversity_score']:.2f} |")
    a("")
    a("## ۹. مقایسه با پیش‌نمایش task-10 (خطایابانه)")
    a("")
    a("| دسته | پیش‌نمایش task-10 | الگوریتم کامل | توضیح |")
    a("|------|-------------------|----------------|-------|")
    explain = {
        "strong_growth": "نوظهورها اول چک می‌شوند (v1400=0 → emerging)",
        "moderate_growth": "هم‌ارز",
        "declining": "هم‌ارز (کاهش جزئی به‌دلیل اولویت نوظهور/محوشده)",
        "emerging": "هم‌ارز",
        "disappearing": "پیش‌نمایش v1404<100$ بود؛ الگوریتم رسمی v1404<10K$ → بیشتر",
        "stable": "نوسانی قبل از پایدار چک می‌شود → کمتر",
        "volatile": "هم‌ارز",
    }
    for cat in ["strong_growth", "moderate_growth", "declining", "emerging",
                "disappearing", "stable", "volatile"]:
        prev = TASK10_PREVIEW.get(cat, "—")
        cur = cat_counts.get(cat, 0)
        a(f"| `{cat}` | {prev:,} | {cur:,} | {explain.get(cat, '')} |")
    a("")
    a("> مابه‌التفاوت‌ها ناشی از **ترتیب اولویت** الگوریتم رسمی (recipe-09 §۵)")
    a("> و **تعریف آستانه محوشده** (THRESHOLD/10) است، نه خطا.")
    a("")
    a("## ۱۰. یادداشت‌های Obsidian (ساخته‌شده با build_trend_notes.py)")
    a("")
    a("- `strong-growth/` — Top 30 HS Code با دسته غالب رشد قوی")
    a("- `moderate-growth/` — Top HS Codeهای رشد متوسط (تعداد محدود به داده)")
    a("- `emerging/` — Top 30 HS Code نوظهور")
    a("- `declining/` — Top 30 HS Code کاهشی")
    a("- `charts/` — نمودار PNG روند aggregated هر یادداشت")
    a("")
    a("## ۱۱. مبنای task-12 (رتبه‌بندی کاندیدهای صادرات)")
    a("")
    a("- فیلتر اولیه: فقط HS Codeهایی با `dominant_trend` در")
    a("  [strong_growth, moderate_growth, emerging]")
    a("- نمره‌دهی: `cagr_5y_aggregated`, `slope_aggregated`,")
    a("  `mean_recent_3y_aggregated`, `n_destinations_active`,")
    a("  `trend_consistency_aggregated`, `cv_aggregated` (وزن‌های Decision-009)")
    a("- فیلترهای اضافی recipe-09 §۶: `mean_recent_3y > 1M$` و `n_destinations_active ≥ 3`")
    a("- خروجی نهایی: Top 100 کاندید صادرات با `export_score`")
    a("")
    a("## ۱۲. اعتبارسنجی")
    a("")
    if failures:
        a(f"❌ {len(failures)} خرابی:")
        for f in failures:
            a(f"- {f}")
    else:
        a("✅ همه بررسی‌ها PASS:")
        a(f"- {n_total:,} جفت طبقه‌بندی‌شده، بدون NULL، دسته‌ها معتبر")
        a(f"- جمع `value_1404` با ورودی برابر (تلورانس < 1e-9 نسبی)")
        a(f"- جمع `n_countries_total` در by-hs == {n_total:,}")
        a(f"- {n_hs:,} HS Code یکتا در by-hs (بدون کاهش)")
    a("")
    a("## مراجع")
    a("- [[task-10-trend-analysis]]")
    a("- [[task-12-export-candidates]]")
    a("- [[conventions]] — بخش ۵")
    a("- [[recipe-09-trend-classification]]")

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text("\n".join(L), encoding="utf-8")
    print(f"[summary] {SUMMARY_PATH.name} نوشته شد ({len(L)} خط)")


# ----------------------------------------------------------------------------
# خروجی Parquet
# ----------------------------------------------------------------------------
PAIRS_SCHEMA = pa.schema([
    ("hs_code", pa.string()),
    ("destination_country_iso2", pa.string()),
    ("hs_description", pa.string()),
    ("destination_country_fa", pa.string()),
    ("value_1400", pa.float64()),
    ("value_1401", pa.float64()),
    ("value_1402", pa.float64()),
    ("value_1403", pa.float64()),
    ("value_1404", pa.float64()),
    ("cagr_5y", pa.float64()),
    ("pct_change_5y", pa.float64()),
    ("growth_multiplier", pa.float64()),
    ("slope", pa.float64()),
    ("r_squared", pa.float64()),
    ("mk_p_value", pa.float64()),
    ("cv", pa.float64()),
    ("trend_consistency", pa.int32()),
    ("mean_value", pa.float64()),
    ("mean_recent_3y", pa.float64()),
    ("n_years_with_data", pa.int32()),
    ("trend_category", pa.string()),
    ("confidence", pa.float64()),
    ("is_significant", pa.bool_()),
    ("n_signs", pa.string()),
    ("recommendation_action", pa.string()),
])

BY_HS_SCHEMA = pa.schema([
    ("hs_code", pa.string()),
    ("hs_description", pa.string()),
    ("n_countries_total", pa.int32()),
    *[pa.field(f"n_{c}", pa.int32()) for c in CATEGORIES],
    ("total_value_5y", pa.float64()),
    ("total_value_1404", pa.float64()),
    ("agg_value_1400", pa.float64()),
    ("agg_value_1404", pa.float64()),
    ("mean_recent_3y_aggregated", pa.float64()),
    ("trend_consistency_aggregated", pa.float64()),
    ("cv_aggregated", pa.float64()),
    ("slope_aggregated", pa.float64()),
    ("n_growth_pairs", pa.int32()),
    ("n_destinations_active", pa.int32()),
    ("dominant_trend", pa.string()),
    ("growth_diversity_score", pa.float64()),
    ("cagr_5y_aggregated", pa.float64()),
])


def write_outputs(pairs: pd.DataFrame, by_hs: pd.DataFrame) -> None:
    out_pairs = pairs[[f.name for f in PAIRS_SCHEMA]].copy()
    for col in ("trend_consistency", "n_years_with_data"):
        out_pairs[col] = out_pairs[col].astype(np.int32)
    table = pa.Table.from_pandas(out_pairs, schema=PAIRS_SCHEMA,
                                 preserve_index=False)
    pq.write_table(table, OUTPUT_PAIRS_PATH, compression="snappy")
    print(f"[write] {OUTPUT_PAIRS_PATH.name} — {table.num_rows:,} × {table.num_columns} "
          f"({OUTPUT_PAIRS_PATH.stat().st_size/1024/1024:.1f} MB)")

    out_hs = by_hs[[f.name for f in BY_HS_SCHEMA]].copy()
    int_cols = ["n_countries_total", "n_growth_pairs", "n_destinations_active"] + \
               [f"n_{c}" for c in CATEGORIES]
    for col in int_cols:
        out_hs[col] = out_hs[col].astype(np.int32)
    table_hs = pa.Table.from_pandas(out_hs, schema=BY_HS_SCHEMA,
                                    preserve_index=False)
    pq.write_table(table_hs, OUTPUT_HS_PATH, compression="snappy")
    print(f"[write] {OUTPUT_HS_PATH.name} — {table_hs.num_rows:,} × {table_hs.num_columns} "
          f"({OUTPUT_HS_PATH.stat().st_size/1024/1024:.1f} MB)")


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() -> int:
    t0 = time.time()
    print("=" * 72)
    print("task-11 — طبقه‌بندی روند به ۷ دسته + تجمیع به سطح HS Code")
    print("=" * 72)

    print("\n[1/4] بارگذاری trend-analysis-5y.parquet...")
    df = pd.read_parquet(INPUT_PATH)
    print(f"  {len(df):,} جفت × {df.shape[1]} ستون")

    print("\n[2/4] طبقه‌بندی همه جفت‌ها...")
    classified = classify_all_pairs(df)
    cat_counts = classified["trend_category"].value_counts()
    print("\n  توزیع:")
    for cat in CATEGORIES:
        print(f"    {cat}: {cat_counts.get(cat, 0):,}")

    print("\n[3/4] تجمیع به سطح HS Code...")
    by_hs = aggregate_by_hs(classified)

    print("\n[4/4] اعتبارسنجی و ذخیره...")
    failures = validate(df, classified, by_hs)
    if failures:
        print("\n❌ FAIL:")
        for f in failures:
            print(f"   - {f}")
        return 1
    print("  همه بررسی‌ها PASS ✅")

    write_outputs(classified, by_hs)
    generate_summary(classified, by_hs, failures, time.time() - t0)

    print(f"\n✅ task-11 کامل شد در {time.time() - t0:.1f} ثانیه")
    return 0


if __name__ == "__main__":
    sys.exit(main())
