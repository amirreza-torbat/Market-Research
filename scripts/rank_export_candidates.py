#!/usr/bin/env python3
"""
task-12 — رتبه‌بندی محصولات کاندید صادرات (هدف نهایی پروژه)

ورودی‌ها (خروجی task-11):
  - 05-Data/processed/trend-classification-by-hs.parquet (۵,۹۹۳ HS × ۲۶ ستون)
  - 05-Data/processed/trend-classification.parquet (۵۰,۱۹۶ جفت × ۲۵ ستون)

خروجی‌ها:
  - 05-Data/processed/export-candidates-ranked.parquet
  - 06-Analysis/export-candidates/_executive-ranking.md (+ charts/top20-scores.png)
  - 06-Analysis/export-candidates/by-target-country.md
  - 06-Analysis/export-candidates/chapter-country-matrix.md (+ charts/chapter-country-heatmap.png)

متدولوژی:
  - فرمول نمره‌دهی: conventions.md §۵.۳ با وزن‌های Decision-009
  - ⚠️ Issue-008: داده ۱۴۰۵ موجود نیست → cagr_5y جایگزین cagr_6y شد
  - فیلتر اولیه: روش membership (نه dominant_trend) طبق یافته task-11 §۱۰/۱۱
  - ریسک‌ها: recipe-09 §۷ (volatile / concentrated / declining_recent)
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# --- نمودارهای فارسی: arabic_reshaper + bidi + DejaVu Sans (مثل task-11) ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from bidi.algorithm import get_display
import arabic_reshaper

fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_HS_PATH = REPO_ROOT / "05-Data/processed/trend-classification-by-hs.parquet"
INPUT_PAIRS_PATH = REPO_ROOT / "05-Data/processed/trend-classification.parquet"
OUTPUT_PATH = REPO_ROOT / "05-Data/processed/export-candidates-ranked.parquet"
OUTPUT_DIR = REPO_ROOT / "06-Analysis/export-candidates"
CHARTS_DIR = OUTPUT_DIR / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))
TODAY = datetime.now(TEHRAN_TZ).strftime("%Y-%m-%d")
TODAY_JALALI = "1405-06-23"
YEARS = [1400, 1401, 1402, 1403, 1404]

# --- وزن‌ها (طبق Decision-009) ---
WEIGHTS = {
    "w1_cagr": 0.30,
    "w2_slope": 0.20,
    "w3_volume": 0.20,
    "w4_diversity": 0.10,
    "w5_consistency": 0.10,
    "w6_volatility": 0.10,
}

# --- آستانه‌های فیلتر و ریسک (طبق Decision-010 و recipe-09 §۶/§۷) ---
MIN_MEAN_RECENT_3Y = 1_000_000          # 1M USD — حداقل حجم کاندید
MIN_N_DESTINATIONS = 3                  # حداقل کشور مقصد فعال در ۱۴۰۴
VOLATILE_CV_THRESHOLD = 0.7             # ریسک نوسان
CONCENTRATED_SHARE_THRESHOLD = 0.70     # ریسک تمرکز بازار

GROWTH_CATEGORIES = ["strong_growth", "moderate_growth", "emerging"]

CATEGORY_FA = {
    "strong_growth": "رشد قوی", "moderate_growth": "رشد متوسط",
    "weak_growth": "رشد ضعیف", "stable": "پایدار",
    "volatile": "نوسانی", "declining": "کاهشی",
    "weak_decline": "کاهش ضعیف", "emerging": "نوظهور",
    "disappearing": "محوشده", "insufficient_data": "داده ناکافی",
}

RISK_FA = {
    "volatile": "نوسان بالا (cv > 0.7)",
    "concentrated": "تمرکز روی یک کشور (سهم > 70٪)",
    "declining_recent": "کاهش در ۱۴۰۴ نسبت به ۱۴۰۳",
    "none": "بدون ریسک شناسایی‌شده",
}


def fa(text: str) -> str:
    """متن فارسی را برای matplotlib شکل‌دهی RTL می‌کند."""
    return get_display(arabic_reshaper.reshape(str(text)))


# ----------------------------------------------------------------------------
# نرمال‌سازی Min-Max (طبق recipe-09 §۶)
# ----------------------------------------------------------------------------
def normalize_minmax(series: pd.Series, penalty: bool = False) -> pd.Series:
    """Min-Max نرمال‌سازی. NULL → ۰. برای جریمه (cv) همان norm مستقیم
    استفاده می‌شود و در فرمول با علامت منفی وارد می‌شود."""
    s = series.copy()
    s_null = s.isna()
    s_clean = s.fillna(0)
    s_min = s_clean.min()
    s_max = s_clean.max()
    if s_max == s_min:
        return pd.Series(0.0, index=s.index)
    norm = (s_clean - s_min) / (s_max - s_min)
    norm[s_null] = 0.0
    return norm


# ----------------------------------------------------------------------------
# فیلتر اولیه — روش membership (نه dominant_trend) طبق یافته task-11
# ----------------------------------------------------------------------------
def filter_candidates(by_hs: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    """
    معیارها (recipe-09 §۶ + توصیه task-11 §۱۱):
    1. membership: حداقل یک جفت در strong_growth/moderate_growth/emerging.
    2. mean_recent_3y_aggregated > 1M USD.
    3. n_destinations_active >= 3.
    """
    print("Filtering candidates with membership approach...")
    has_growth = (
        (by_hs["n_strong_growth"] > 0)
        | (by_hs["n_moderate_growth"] > 0)
        | (by_hs["n_emerging"] > 0)
    )
    has_volume = by_hs["mean_recent_3y_aggregated"] > MIN_MEAN_RECENT_3Y
    has_diversity = by_hs["n_destinations_active"] >= MIN_N_DESTINATIONS

    n0 = len(by_hs)
    n1 = int(has_growth.sum())
    n2 = int((has_growth & has_volume).sum())
    filtered = by_hs[has_growth & has_volume & has_diversity].copy()
    print(f"  membership: {n1:,} HS → +volume>1M: {n2:,} HS → +dest>=3: {len(filtered):,} HS (from {n0:,})")
    return filtered


# ----------------------------------------------------------------------------
# محاسبه export_score (وزن‌های Decision-009)
# ----------------------------------------------------------------------------
def compute_export_score(filtered: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    """محاسبه export_score برای هر HS Code — Min-Max روی کل دیتاست کاندیدها."""
    print("Computing export_score...")

    # trend_consistency_aggregated از task-11 موجود است؛ در صورت نبود محاسبه شود
    if "trend_consistency_aggregated" not in filtered.columns:
        tc_agg = pairs.groupby("hs_code")["trend_consistency"].mean().reset_index()
        tc_agg.columns = ["hs_code", "trend_consistency_aggregated"]
        filtered = filtered.merge(tc_agg, on="hs_code", how="left")

    # نرمال‌سازی شاخص‌ها (⚠️ Issue-008: cagr_5y به‌جای cagr_6y)
    filtered["norm_cagr"] = normalize_minmax(filtered["cagr_5y_aggregated"])
    filtered["norm_slope"] = normalize_minmax(filtered["slope_aggregated"])
    filtered["norm_volume"] = normalize_minmax(filtered["mean_recent_3y_aggregated"])
    filtered["norm_diversity"] = normalize_minmax(filtered["n_destinations_active"].astype(float))
    filtered["norm_consistency"] = normalize_minmax(filtered["trend_consistency_aggregated"])
    filtered["norm_cv_penalty"] = normalize_minmax(filtered["cv_aggregated"], penalty=True)

    # مولفه‌های نمره
    filtered["score_growth"] = WEIGHTS["w1_cagr"] * filtered["norm_cagr"]
    filtered["score_slope"] = WEIGHTS["w2_slope"] * filtered["norm_slope"]
    filtered["score_volume"] = WEIGHTS["w3_volume"] * filtered["norm_volume"]
    filtered["score_diversity"] = WEIGHTS["w4_diversity"] * filtered["norm_diversity"]
    filtered["score_consistency"] = WEIGHTS["w5_consistency"] * filtered["norm_consistency"]
    filtered["score_volatility_penalty"] = WEIGHTS["w6_volatility"] * filtered["norm_cv_penalty"]

    # نمره نهایی (جریمه نوسان با علامت منفی)
    filtered["export_score"] = (
        filtered["score_growth"]
        + filtered["score_slope"]
        + filtered["score_volume"]
        + filtered["score_diversity"]
        + filtered["score_consistency"]
        - filtered["score_volatility_penalty"]
    )

    # رتبه‌بندی نزولی
    filtered = filtered.sort_values("export_score", ascending=False).reset_index(drop=True)
    filtered["rank"] = np.arange(1, len(filtered) + 1, dtype=np.int64)
    print(f"  Scored {len(filtered):,} candidates; "
          f"range [{filtered['export_score'].min():.4f}, {filtered['export_score'].max():.4f}]")
    return filtered


# ----------------------------------------------------------------------------
# ریسک‌ها (recipe-09 §۷) — vectorized با groupby
# ----------------------------------------------------------------------------
def compute_risk_flags(ranked: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    """
    - volatile: cv_aggregated > 0.7
    - concentrated: سهم بزرگ‌ترین کشور از value_1404 > 70٪
    - declining_recent: جمع value_1404 < جمع value_1403 (aggregated)
    - (partial_data اعمال نمی‌شود: ۱۴۰۵ اصلاً موجود نیست — Issue-008)
    """
    print("Computing risk flags...")

    grp = pairs.groupby("hs_code").agg(
        pair_total_1404=("value_1404", "sum"),
        pair_total_1403=("value_1403", "sum"),
        pair_max_1404=("value_1404", "max"),
        n_significant=("is_significant", "sum"),
    ).reset_index()

    ranked = ranked.merge(grp, on="hs_code", how="left")
    ranked["max_country_share"] = np.where(
        ranked["pair_total_1404"] > 0,
        ranked["pair_max_1404"] / ranked["pair_total_1404"],
        0.0,
    )

    def _flags(row) -> str:
        risks = []
        if pd.notna(row["cv_aggregated"]) and row["cv_aggregated"] > VOLATILE_CV_THRESHOLD:
            risks.append("volatile")
        if row["max_country_share"] > CONCENTRATED_SHARE_THRESHOLD:
            risks.append("concentrated")
        if row["pair_total_1403"] > 0 and row["pair_total_1404"] < row["pair_total_1403"]:
            risks.append("declining_recent")
        return ", ".join(risks) if risks else "none"

    ranked["risk_flags"] = ranked.apply(_flags, axis=1)
    ranked["n_significant_pairs"] = ranked["n_significant"].astype("int64")
    ranked = ranked.drop(columns=["pair_total_1404", "pair_total_1403", "pair_max_1404", "n_significant"])
    print(f"  Risk distribution: {ranked['risk_flags'].value_counts().to_dict()}")
    return ranked


# ----------------------------------------------------------------------------
# توصیه استراتژیک (recipe-09 §۷ + پرامپت task-12)
# ----------------------------------------------------------------------------
def compute_recommendation(row) -> str:
    score = row["export_score"]
    has_strong = row.get("n_strong_growth", 0) > 0
    has_moderate = row.get("n_moderate_growth", 0) > 0
    has_emerging = row.get("n_emerging", 0) > 0
    if score > 0.7 and (has_strong or has_moderate or has_emerging):
        return "select"
    elif score >= 0.4:
        return "monitor"
    return "investigate"


# ----------------------------------------------------------------------------
# Top N کشورهای هدف (جفت‌های رشد، fallback: همه جفت‌ها)
# ----------------------------------------------------------------------------
def get_top_countries(hs_code: str, pairs_by_hs: dict, n: int = 5):
    """Top N کشور با رشد مثبت برای یک HS Code → (رشته کشورها، جمع ارزش ۱۴۰۴)."""
    hs_pairs = pairs_by_hs.get(hs_code, pd.DataFrame())
    growth = hs_pairs[
        hs_pairs["trend_category"].isin(GROWTH_CATEGORIES)
    ].nlargest(n, "value_1404")
    if len(growth) == 0:
        growth = hs_pairs.nlargest(n, "value_1404")
    labels = [
        f"{row['destination_country_iso2']} ({row['destination_country_fa']})"
        for _, row in growth.iterrows()
    ]
    total_val = float(growth["value_1404"].sum()) if len(growth) else 0.0
    return labels, total_val


# ----------------------------------------------------------------------------
# جدول نهایی
# ----------------------------------------------------------------------------
def build_ranked_table(ranked: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    print("Building final ranked table...")
    pairs_by_hs = {k: v for k, v in pairs.groupby("hs_code")}

    top_labels, top_values = [], []
    for hs in ranked["hs_code"]:
        labels, val = get_top_countries(hs, pairs_by_hs)
        top_labels.append("; ".join(labels))
        top_values.append(val)
    ranked["top_5_countries"] = top_labels
    ranked["top_5_countries_value_1404"] = top_values

    ranked["recommendation"] = ranked.apply(compute_recommendation, axis=1)
    ranked["hs_chapter"] = ranked["hs_code"].str[:2]
    # trend_category از task-11 (dominant_trend) برای مرجع
    ranked["trend_category"] = ranked["dominant_trend"]

    output_cols = [
        "rank", "hs_code", "hs_description", "hs_chapter",
        "export_score", "recommendation", "risk_flags", "trend_category",
        "cagr_5y_aggregated", "slope_aggregated", "mean_recent_3y_aggregated",
        "n_destinations_active", "trend_consistency_aggregated", "cv_aggregated",
        "total_value_5y", "total_value_1404",
        "n_strong_growth", "n_moderate_growth", "n_emerging",
        "n_declining", "n_disappearing", "n_significant_pairs",
        "top_5_countries", "top_5_countries_value_1404", "max_country_share",
        "score_growth", "score_slope", "score_volume",
        "score_diversity", "score_consistency", "score_volatility_penalty",
    ]
    available_cols = [c for c in output_cols if c in ranked.columns]
    final = ranked[available_cols].copy()

    for c in ["n_destinations_active", "n_strong_growth", "n_moderate_growth",
              "n_emerging", "n_declining", "n_disappearing"]:
        if c in final.columns:
            final[c] = final[c].astype("int32")
    final["rank"] = final["rank"].astype("int32")
    return final


# ----------------------------------------------------------------------------
# اعتبارسنجی (recipe-09 §۹)
# ----------------------------------------------------------------------------
def validate_outputs(final: pd.DataFrame, by_hs: pd.DataFrame, pairs: pd.DataFrame) -> bool:
    print("\nValidation (recipe-09 §9):")
    checks = []

    n = len(final)
    checks.append(("count >= 100 (task acceptance)", n >= 100, f"n={n}"))
    checks.append(("all records have export_score", final["export_score"].notna().all(), ""))
    checks.append(("all records have rank", final["rank"].notna().all(), ""))
    checks.append(("rank unique & no gaps",
                   bool((final["rank"].values == np.arange(1, n + 1)).all()), ""))
    checks.append(("score sorted desc (rank order matches score)",
                   bool(final["export_score"].is_monotonic_decreasing), ""))
    # بازه تئوری: [-w6, w1+w2+w3+w4+w5] = [-0.10, 0.90]
    lo, hi = final["export_score"].min(), final["export_score"].max()
    checks.append(("score range within theoretical [-0.10, 0.90]",
                   bool(lo >= -0.10 - 1e-9 and hi <= 0.90 + 1e-9),
                   f"[{lo:.4f}, {hi:.4f}]"))
    checks.append(("weights sum to 1.0",
                   abs(sum(WEIGHTS.values()) - 1.0) < 1e-12, f"{sum(WEIGHTS.values())}"))
    recomputed = (final["score_growth"] + final["score_slope"] + final["score_volume"]
                  + final["score_diversity"] + final["score_consistency"]
                  - final["score_volatility_penalty"])
    max_err = float((recomputed - final["export_score"]).abs().max())
    checks.append(("score == sum of components", max_err < 1e-9, f"max_err={max_err:.2e}"))
    checks.append(("filter: membership holds for all",
                   bool(((final["n_strong_growth"] > 0) | (final["n_moderate_growth"] > 0)
                         | (final["n_emerging"] > 0)).all()), ""))
    checks.append(("filter: volume > 1M for all",
                   bool((final["mean_recent_3y_aggregated"] > MIN_MEAN_RECENT_3Y).all()), ""))
    checks.append(("filter: n_destinations >= 3 for all",
                   bool((final["n_destinations_active"] >= MIN_N_DESTINATIONS).all()), ""))
    checks.append(("no NULL in key columns",
                   bool(final[["hs_code", "hs_description", "export_score", "rank",
                               "recommendation", "risk_flags", "top_5_countries"]]
                        .notna().all().all()), ""))
    # سازگاری جمع ۱۴۰۴ با pairs (نمونه ۲۰ تایی)
    sample = final.head(20)["hs_code"].tolist()
    grp = pairs[pairs["hs_code"].isin(sample)].groupby("hs_code")["value_1404"].sum()
    merged = final[final["hs_code"].isin(sample)].set_index("hs_code")["total_value_1404"]
    diff = (merged - grp.reindex(merged.index)).abs()
    rel = (diff / grp.reindex(merged.index).clip(lower=1)).max()
    checks.append(("total_value_1404 matches pairs (sample 20, rel)",
                   bool(rel < 1e-9), f"max_rel={rel:.2e}"))
    # هر HS در by_hs دقیقاً یک رکورد
    checks.append(("hs_code unique in output", final["hs_code"].is_unique, ""))

    ok = True
    for name, passed, info in checks:
        status = "PASS" if passed else "FAIL"
        if not passed:
            ok = False
        print(f"  [{status}] {name} {info}")
    return ok


# ----------------------------------------------------------------------------
# نمودار میله‌ای Top 20 (الزام task-file §۷.۲)
# ----------------------------------------------------------------------------
def generate_top20_chart(final: pd.DataFrame) -> None:
    top20 = final.head(20).iloc[::-1]  # رتبه ۱ در بالا
    labels = [
        fa(f"{r['hs_description'][:34]}… ({r['hs_code']})")
        if len(str(r["hs_description"])) > 34
        else fa(f"{r['hs_description']} ({r['hs_code']})")
        for _, r in top20.iterrows()
    ]
    colors = ["#2e7d32" if r["recommendation"] == "select"
              else "#f9a825" if r["recommendation"] == "monitor" else "#8d6e63"
              for _, r in top20.iterrows()]

    fig, ax = plt.subplots(figsize=(11, 10), constrained_layout=True)
    bars = ax.barh(range(len(top20)), top20["export_score"], color=colors, height=0.72)
    ax.set_yticks(range(len(top20)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel(fa("نمره صادرات (export_score)"), fontsize=11)
    ax.set_title(fa("۲۰ کاندید برتر صادرات ایران — نمره ترکیبی (task-12)"), fontsize=13)
    ax.set_xlim(0, max(1.0, float(top20["export_score"].max()) * 1.08))
    for i, (_, r) in enumerate(top20.iterrows()):
        ax.text(float(r["export_score"]) + 0.008, i,
                f"{r['export_score']:.3f}", va="center", fontsize=8)
    ax.grid(True, axis="x", alpha=0.3)
    # راهنما
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#2e7d32", label=fa("select — انتخاب")),
                       Patch(color="#f9a825", label=fa("monitor — پایش")),
                       Patch(color="#8d6e63", label=fa("investigate — بررسی"))],
              loc="lower right", fontsize=9)
    chart_path = CHARTS_DIR / "top20-scores.png"
    fig.savefig(chart_path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {chart_path}")


# ----------------------------------------------------------------------------
# گزارش اجرایی Top 20
# ----------------------------------------------------------------------------
def generate_executive_ranking(final: pd.DataFrame, pairs: pd.DataFrame) -> None:
    print("Generating executive ranking...")
    generate_top20_chart(final)

    top_20 = final.head(20)
    n_total = len(final)
    rec_counts = final["recommendation"].value_counts()

    content = f"""---
type: analysis
title: 🎯 گزارش اجرایی کاندیدهای صادرات (task-12 — هدف نهایی پروژه)
created: {TODAY}
updated: {TODAY}
status: review
tags:
  - analysis
  - export-candidates
  - ranking
  - final
folder: 06-Analysis/export-candidates
---

# 🎯 گزارش اجرایی کاندیدهای صادرات (task-12)

**تاریخ**: {TODAY} ({TODAY_JALALI}) | **Agent**: Analyst
**Pipeline**: `scripts/rank_export_candidates.py`
**منبع داده**: `trend-classification-by-hs.parquet` + `trend-classification.parquet` (task-11)

## ۱. خلاصه اجرایی

این گزارش **هدف نهایی پروژه** است: شناسایی محصولات با روند رو به رشد برای انتخاب صادرات. از {n_total:,} محصول کاندید (پس از فیلتر membership)، Top 20 با بالاترین `export_score` در این گزارش معرفی می‌شوند. کل زنجیره تحلیل از ۶۲۶,۳۹۵ رکورد صادراتی خام (۵ سال ۱۴۰۰ تا ۱۴۰۴) آغاز شده، به ۵۰,۱۹۶ جفت (HS × کشور) با ۱۳ شاخص روند (task-10)، سپس طبقه‌بندی ۱۰ دسته‌ای آماری (task-11) و اکنون به رتبه‌بندی نهایی رسیده است. نمره هر کاندید ترکیبی از رشد (CAGR)، شدت روند (slope)، حجم اخیر (mean_recent_3y)، تنوع بازار، ثبات روند و جریمه نوسان است تا تصویری چندبُعدی از جذابیت صادراتی هر محصول ارائه شود.

### متدولوژی نمره‌دهی

نمره ترکیبی `export_score` با فرمول زیر محاسبه شده (طبق `conventions.md` §۵.۳ و `decisions.md` Decision-009):

```
export_score = 0.30 × norm(cagr_5y)
             + 0.20 × norm(slope)
             + 0.20 × norm(mean_recent_3y)
             + 0.10 × norm(n_destinations_active)
             + 0.10 × norm(trend_consistency)
             - 0.10 × norm(cv)
```

نرمال‌سازی Min-Max روی کل دیتاست کاندیدها؛ مقادیر NULL → ۰؛ بازه تئوری نمره [-0.10, 0.90] است (جریمه نوسان همیشه ≥ ۰).

### ⚠️ تطابق با Issue-008

سال ۱۴۰۵ در منبع داده موجود نیست. بنابراین `cagr_6y` قابل محاسبه نیست. در این تحلیل، از `cagr_5y` (روی ۵ سال کامل ۱۴۰۰ تا ۱۴۰۴) به‌عنوان جایگزین استفاده شده است. این تطابق در تمام محاسبات و گزارش‌ها مستند شده و نام ستون Parquet نیز `cagr_5y_aggregated` نگه داشته شده است (نه `cagr_6y`) تا ابهامی باقی نماند.

### فیلتر اولیه (روش membership)

طبق یافته task-11، فیلتر `dominant_trend` کار نمی‌کرد (۵,۵۵۸ از ۵,۹۹۳ HS Code غالب insufficient_data داشتند). به‌جای آن، روش membership استفاده شد:
- HS Codeهایی که **حداقل یک جفت** در `strong_growth`، `moderate_growth`، یا `emerging` دارند.
- `mean_recent_3y_aggregated > 1,000,000 USD` (حداقل ۱ میلیون دلار سالانه).
- `n_destinations_active >= 3` (حداقل ۳ کشور مقصد در ۱۴۰۴).

**نتیجه فیلتر**: از ۵,۹۹۳ HS Code → ۱,۰۴۶ با membership → ۶۱۴ با حجم کافی → **{n_total} کاندید نهایی** در {final['hs_chapter'].nunique()} فصل HS.

## ۲. نمودار Top 20

![[charts/top20-scores.png]]

## ۳. Top 20 کاندید صادرات

| رتبه | HS Code | شرح کالا | نمره | توصیه | CAGR 5y | حجم ۳ سال اخیر (USD) | کشورهای هدف |
|------|---------|----------|------|-------|---------|----------------------|-------------|
"""
    for _, row in top_20.iterrows():
        cagr = row.get("cagr_5y_aggregated")
        cagr_str = f"{cagr*100:.1f}%" if pd.notna(cagr) else "N/A"
        vol = row.get("mean_recent_3y_aggregated", 0)
        vol_str = f"{vol/1e6:.0f}M" if pd.notna(vol) and vol > 0 else "N/A"
        desc = str(row["hs_description"])[:40]
        countries = str(row.get("top_5_countries", ""))[:60]
        content += (f"| {row['rank']} | {row['hs_code']} | {desc} | {row['export_score']:.3f} "
                    f"| {row['recommendation']} | {cagr_str} | {vol_str} | {countries} |\n")

    content += "\n## ۴. تحلیل کیفی Top 5\n"

    for _, row in top_20.head(5).iterrows():
        cagr = row.get("cagr_5y_aggregated")
        cagr_str = f"{cagr*100:.1f}%" if pd.notna(cagr) else "N/A"
        growth_txt = ("رشد قوی" if (pd.notna(cagr) and cagr > 0.1)
                      else "رشد مثبت" if (pd.notna(cagr) and cagr > 0) else "بدون CAGR قابل محاسبه")
        n_growth_pairs = int(row["n_strong_growth"] + row["n_moderate_growth"] + row["n_emerging"])
        content += f"""### رتبه {row['rank']}: {row['hs_description']} ({row['hs_code']})

- **نمره**: {row['export_score']:.3f} | **توصیه**: {row['recommendation']} | **ریسک‌ها**: {row.get('risk_flags', 'none')}
- **CAGR ۵ ساله**: {cagr_str} | **حجم ۳ سال اخیر**: {row.get('mean_recent_3y_aggregated', 0)/1e6:.0f} میلیون دلار
- **کشورهای فعال**: {int(row.get('n_destinations_active', 0))} | **جفت‌های رشد**: {n_growth_pairs} (قوی {int(row['n_strong_growth'])} / متوسط {int(row['n_moderate_growth'])} / نوظهور {int(row['n_emerging'])})

این محصول با نمره {row['export_score']:.3f} در رتبه {row['rank']} کاندیدهای صادرات قرار دارد. روند ۵ ساله aggregated نشان‌دهنده **{growth_txt}** است و محصول به {int(row.get('n_destinations_active', 0))} کشور مقصد فعال صادرات داشته است. مجموع ارزش ۵ ساله آن {row.get('total_value_5y', 0)/1e6:,.0f} میلیون دلار و ارزش سال ۱۴۰۴ معادل {row.get('total_value_1404', 0)/1e6:,.0f} میلیون دلار بوده است. ضریب تغییرات {row.get('cv_aggregated', 0):.2f} {"نوسان قابل توجهی" if row.get('cv_aggregated', 0) > 0.5 else "نوسان کنترل‌شده‌ای"} را نشان می‌دهد و سهم بزرگ‌ترین کشور مقصد {row.get('max_country_share', 0)*100:.1f} درصد است.{"⚠️ ریسک‌های شناسایی‌شده: " + str(row.get('risk_flags', '')) + "." if str(row.get('risk_flags', 'none')) != 'none' else "بدون ریسک شناسایی‌شده."} توصیه استراتژیک نهایی: **{row['recommendation']}**.

"""

    # بررسی کوتاه رتبه‌های ۶ تا ۲۰
    content += "\n### بررسی کوتاه رتبه‌های ۶ تا ۲۰\n\n"
    for _, row in top_20.iloc[5:20].iterrows():
        cagr = row.get("cagr_5y_aggregated")
        cagr_str = f"{cagr*100:.1f}%" if pd.notna(cagr) else "N/A"
        desc = str(row["hs_description"])[:45]
        risks = str(row.get("risk_flags", "none"))
        risk_note = f" ریسک‌ها: {risks}." if risks != "none" else ""
        content += (f"- **رتبه {row['rank']}** — {desc} ({row['hs_code']}): نمره {row['export_score']:.3f}، "
                    f"CAGR {cagr_str}، {int(row['n_destinations_active'])} کشور فعال، "
                    f"حجم اخیر {row['mean_recent_3y_aggregated']/1e6:.0f}M$. توصیه: {row['recommendation']}.{risk_note}\n")

    rec_lines = "".join(
        f"| {rec} | {count} | {count/n_total*100:.1f}% |\n"
        for rec, count in rec_counts.items()
    )
    s = final["export_score"]
    content += f"""
## ۵. توزیع توصیه‌ها و نمره‌ها

| توصیه | تعداد | درصد |
|-------|-------|-------|
{rec_lines}

### آمار توزیع نمره

| شاخص | مقدار |
|------|-------|
| بیشینه نمره | {s.max():.4f} |
| صدک ۹۰ | {s.quantile(0.9):.4f} |
| میانه | {s.median():.4f} |
| کمینه | {s.min():.4f} |

> ⚠️ **یافته مهم — کالیبراسیون آستانه توصیه‌ها**: با نرمال‌سازی Min-Max، هیچ کاندیدی همزمان در همه ۶ بُعد پیشتاز نیست (محصولِ پرحجم معمولاً CAGR پایین‌تر یا NULL دارد و محصولِ پررشد حجم کوچک‌تری دارد)؛ در نتیجه نمره‌های ترکیبی در بازه [-۰.۰۳, ۰.۳۵] فشرده می‌شوند و آستانه‌های ثابت پرامپت (select>0.7، monitor≥0.4) به هیچ کاندیدی تعلق نمی‌گیرد — همه «investigate» می‌شوند. این خروجیِ صادقانه همان فرمول و آستانه‌های مصوب (recipe-09 §۷) است؛ **سیگنال قابل‌اقدام، خودِ رتبه‌بندی (رتبه ۱ تا ۵۷۴) و یادداشت‌های Top 50 است**. اگر مایل باشید آستانه‌ها بر اساس توزیع واقعی (مثلاً select ≥ ۰.۲۵ و monitor ≥ ۰.۱۰) یا وزن‌های جدید (Decision-009 / Pending-003) بازکالیبره شود، این تسک با یک re-run به‌روز می‌شود.
"""

    risk_counts = {"volatile": 0, "concentrated": 0, "declining_recent": 0, "none": 0}
    for risks in final["risk_flags"]:
        if risks == "none":
            risk_counts["none"] += 1
        else:
            for r in str(risks).split(", "):
                if r in risk_counts:
                    risk_counts[r] += 1
    risk_lines = "".join(
        f"| {risk} | {count} | {RISK_FA[risk]} |\n"
        for risk, count in risk_counts.items()
    )
    content += f"""
## ۶. ریسک‌های شناسایی‌شده

| نوع ریسک | تعداد کاندید | توضیح |
|----------|---------------|-------|
{risk_lines}
> پرچم `partial_data` اعمال نشده چون سال ۱۴۰۵ اصلاً در داده موجود نیست (Issue-008) و برای همه کاندیدها یکسان است.
"""

    chapter_stats = final.groupby("hs_chapter").agg(
        n_candidates=("hs_code", "count"),
        total_score=("export_score", "sum"),
        avg_score=("export_score", "mean"),
    ).sort_values("total_score", ascending=False).head(10)
    chapter_lines = "".join(
        f"| {chapter} | {stats['n_candidates']} | {stats['total_score']:.2f} (میانگین: {stats['avg_score']:.3f}) |\n"
        for chapter, stats in chapter_stats.iterrows()
    )
    content += f"""
## ۷. فصل‌های پرپتانسیل (HS Chapter)

| فصل | تعداد کاندید | مجموع نمره |
|------|---------------|------------|
{chapter_lines}
"""

    content += f"""
## ۸. مراجع و فایل‌های خروجی

- **داده**: `05-Data/processed/export-candidates-ranked.parquet` ({n_total} کاندید × {len(final.columns)} ستون)
- **یادداشت‌های تفصیلی**: `06-Analysis/export-candidates/rank-NN-*.md` (Top 50)
- **گزارش کشور-محور**: [[by-target-country]]
- **ماتریس فصل × کشور**: [[chapter-country-matrix]]
- **منابع تحلیلی**: [[task-10-trend-analysis]]، [[task-11-trend-classification]]، [[_classification-summary]]
- **متدولوژی**: [[conventions]] §۵.۳، [[recipe-09-trend-classification]] §۶/§۷، Decision-009/010

## ۹. محدودیت‌ها و نکات

1. **سال ۱۴۰۵**: داده در منبع موجود نیست (Issue-008). تحلیل روی ۵ سال کامل (۱۴۰۰ تا ۱۴۰۴) انجام شد و `cagr_5y` جایگزین `cagr_6y` شد.
2. **تفکیک ماهانه ۱۴۰۳/۱۴۰۴**: موجود نیست (Issue-006). اما در تحلیل سالانه مشکلی ایجاد نمی‌کند.
3. **هشدار آماری Mann-Kendall**: با n=5، حداقل p-value ممکن ≈ ۰.۰۲۷۵ است. شاخص `is_significant` (جفت‌های با MK p<0.05 یا نوظهور/محوشده) به‌صورت ستون اطلاعاتی `n_significant_pairs` در خروجی Parquet ثبت شد و در گزارش کشور-محور لحاظ گردید؛ ساختار وزن‌ها طبق قانون سخت «فقط Decision-009» دست‌نخورده ماند.
4. **وزن‌های نمره‌دهی**: قابل تنظیم در `decisions.md` Decision-009. اگر وزن‌های متفاوتی خواسته شود، این تحلیل re-run شود.
5. **نوسان و پرچم volatile**: `cv_aggregated` میانگین cv جفت‌هاست و cv جفت‌ها با صفر-پرکردن سال‌های بدون صادرات متورم می‌شود؛ در نتیجه cv_aggregated همه کاندیدها > ۰.۷ است و پرچم «volatile» برای همه فعال می‌شود (غایت‌گیری‌کننده). پرچم‌های «concentrated» و «declining_recent» همچنان تمایزبخش‌اند. در تفسیر نوسان، به نمودار روند یادداشت تفصیلی هر کاندید رجوع کنید.
6. **مبنای نرمال‌سازی**: Min-Max روی ست کاندیدهای فیلترشده (نه کل ۵,۹۹۳ HS) — طبق پیاده‌سازی مرجع پرامپت task-12؛ نمره یعنی جاذابیت نسبی در میان کاندیدهای واجد شرایط.

---

**این گزارش هدف نهایی پروژه است.** برای سؤالات یا تغییر وزن‌ها/آستانه‌ها، با کاربر هماهنگ کنید.
"""
    output_path = OUTPUT_DIR / "_executive-ranking.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Saved: {output_path}")


# ----------------------------------------------------------------------------
# گزارش کشور-محور
# ----------------------------------------------------------------------------
def generate_by_target_country(final: pd.DataFrame, pairs: pd.DataFrame) -> None:
    """برای هر کشور مقصد، HS Codeهایی با روند رشد قوی/متوسط/نوظهور."""
    print("Generating by-target-country report...")

    growth_pairs = pairs[pairs["trend_category"].isin(GROWTH_CATEGORIES)].copy()

    country_stats = growth_pairs.groupby(
        ["destination_country_iso2", "destination_country_fa"]
    ).agg(
        n_hs_growth=("hs_code", "count"),
        total_value_1404=("value_1404", "sum"),
        n_strong=("trend_category", lambda x: (x == "strong_growth").sum()),
        n_moderate=("trend_category", lambda x: (x == "moderate_growth").sum()),
        n_emerging=("trend_category", lambda x: (x == "emerging").sum()),
        n_significant_pairs=("is_significant", "sum"),
    ).reset_index().sort_values("total_value_1404", ascending=False)

    n_countries = len(country_stats)
    top_30_countries = country_stats.head(30)

    content = f"""---
type: analysis
title: گزارش کشور-محور کاندیدهای صادرات (task-12)
created: {TODAY}
updated: {TODAY}
status: review
tags:
  - analysis
  - export-candidates
  - by-country
folder: 06-Analysis/export-candidates
---

# گزارش کشور-محور کاندیدهای صادرات (task-12)

**تاریخ**: {TODAY} ({TODAY_JALALI}) | **Agent**: Analyst
**منبع داده**: `trend-classification.parquet` (task-11)

## خلاصه

این گزارش برای هر کشور مقصد، HS Codeهایی که روند رشد قوی/متوسط/نوظهور به آن کشور دارند را فهرست می‌کند. این اطلاعات برای توسعه بازار هدفمند مفید است — کاربر می‌تواند ببیند هر بازار مقصد چه فرصت‌های محصولی در حال رشد دارد و اولویت‌بندی بازار بر اساس ارزش و تعداد فرصت‌ها انجام شود. ستون «معنادار» تعداد جفت‌هایی است که پرچم `is_significant` دارند (MK p<0.05 یا نوظهور/محوشده) — با توجه به محدودیت توان آماری Mann-Kendall در n=5 (حداقل p≈۰.۰۲۷۵)، این ستون به‌عنوان سیگنال اعتبار آماری در کنار CAGR تفسیر شود.

## آمار کلی

| شاخص | مقدار |
|------|-------|
| تعداد کشورهای با حداقل یک جفت رشد | {n_countries} |
| مجموع جفت‌های با رشد | {int(country_stats['n_hs_growth'].sum()):,} |
| تعداد strong_growth | {int(country_stats['n_strong'].sum()):,} |
| تعداد moderate_growth | {int(country_stats['n_moderate'].sum()):,} |
| تعداد emerging | {int(country_stats['n_emerging'].sum()):,} |

## Top 30 کشور مقصد (بر اساس ارزش ۱۴۰۴ جفت‌های رشد)

| رتبه | کشور | تعداد HS رشد | strong | moderate | emerging | معنادار | ارزش ۱۴۰۴ (USD) |
|------|------|--------------|--------|----------|----------|---------|-----------------|
"""
    for idx, (_, row) in enumerate(top_30_countries.iterrows(), 1):
        content += (f"| {idx} | {row['destination_country_iso2']} ({row['destination_country_fa']}) "
                    f"| {int(row['n_hs_growth'])} | {int(row['n_strong'])} | {int(row['n_moderate'])} "
                    f"| {int(row['n_emerging'])} | {int(row['n_significant_pairs'])} "
                    f"| {row['total_value_1404']:,.0f} |\n")

    content += "\n## Top 10 HS Code برای هر کشور (Top 10 کشور)\n"

    for _, country_row in top_30_countries.head(10).iterrows():
        country_iso = country_row["destination_country_iso2"]
        country_fa_name = country_row["destination_country_fa"]
        country_hs = growth_pairs[
            growth_pairs["destination_country_iso2"] == country_iso
        ].nlargest(10, "value_1404")

        content += f"""### {country_fa_name} ({country_iso})

| HS Code | شرح | ۱۴۰۴ (USD) | CAGR | دسته | معنادار |
|---------|------|------------|------|------|---------|
"""
        for _, hs in country_hs.iterrows():
            cagr = hs.get("cagr_5y")
            cagr_str = f"{cagr*100:.1f}%" if pd.notna(cagr) else "—"
            sig = "✓" if bool(hs.get("is_significant", False)) else "—"
            content += (f"| {hs['hs_code']} | {str(hs['hs_description'])[:40]} "
                        f"| {hs['value_1404']:,.0f} | {cagr_str} "
                        f"| {CATEGORY_FA.get(hs['trend_category'], hs['trend_category'])} | {sig} |\n")
        content += "\n"

    content += """## مراجع
- [[_executive-ranking]]
- [[chapter-country-matrix]]
- [[task-11-trend-classification]]
"""
    output_path = OUTPUT_DIR / "by-target-country.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Saved: {output_path}")


# ----------------------------------------------------------------------------
# ماتریس فصل × کشور با heatmap
# ----------------------------------------------------------------------------
def generate_chapter_country_matrix(final: pd.DataFrame, pairs: pd.DataFrame) -> None:
    print("Generating chapter-country matrix...")

    import seaborn as sns

    strong_pairs = pairs[pairs["trend_category"] == "strong_growth"].copy()
    strong_pairs["hs_chapter"] = strong_pairs["hs_code"].str[:2]

    top_countries = strong_pairs["destination_country_iso2"].value_counts().head(30).index.tolist()

    matrix_data = strong_pairs[
        strong_pairs["destination_country_iso2"].isin(top_countries)
    ].groupby(["hs_chapter", "destination_country_iso2"]).size().unstack(fill_value=0)

    for country in top_countries:
        if country not in matrix_data.columns:
            matrix_data[country] = 0
    matrix_data = matrix_data[top_countries].sort_index()

    # --- heatmap (متن فارسی با fa() شکل‌دهی می‌شود) ---
    fig, ax = plt.subplots(figsize=(16, 11), constrained_layout=True)
    sns.heatmap(
        matrix_data,
        annot=True,
        fmt="d",
        cmap="YlOrRd",
        ax=ax,
        linewidths=0.3,
        linecolor="#f0f0f0",
        cbar_kws={"label": fa("تعداد HS Code با رشد قوی")},
    )
    ax.set_title(fa("ماتریس فصل HS × کشور مقصد — تعداد جفت‌های با رشد قوی (task-12)"), fontsize=14)
    ax.set_xlabel(fa("کشور مقصد (ISO2)"), fontsize=12)
    ax.set_ylabel(fa("فصل HS (۲-رقمی)"), fontsize=12)
    ax.tick_params(axis="x", rotation=90, labelsize=8)
    ax.tick_params(axis="y", rotation=0, labelsize=8)

    chart_path = CHARTS_DIR / "chapter-country-heatmap.png"
    fig.savefig(chart_path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {chart_path}")

    n_chapters_matrix = len(matrix_data)
    content = f"""---
type: analysis
title: ماتریس فصل × کشور کاندیدهای صادرات (task-12)
created: {TODAY}
updated: {TODAY}
status: review
tags:
  - analysis
  - export-candidates
  - matrix
folder: 06-Analysis/export-candidates
---

# ماتریس فصل × کشور کاندیدهای صادرات (task-12)

**تاریخ**: {TODAY} ({TODAY_JALALI}) | **Agent**: Analyst
**منبع داده**: `trend-classification.parquet` (task-11)

## خلاصه

این ماتریس نشان می‌دهد هر فصل HS (۲-رقمی) به کدام کشورها بیشترین رشد قوی صادرات داشته است. مقدار هر سلول = تعداد جفت‌های (HS Code × کشور) با `trend_category = strong_growth` در آن فصل به آن کشور. ماتریس روی {n_chapters_matrix} فصل × Top 30 کشور مقصد (بر اساس تعداد جفت رشد قوی) ساخته شده و مجموع کل سلول‌ها {int(matrix_data.values.sum())} جفت رشد قوی را پوشش می‌دهد.

## نمودار Heatmap

![[charts/chapter-country-heatmap.png]]

## ماتریس عددی (Top 15 کشور × همه فصول)

"""
    content += "| فصل | " + " | ".join(top_countries[:15]) + " |\n"
    content += "|------|" + "|".join(["---"] * 15) + "|\n"
    for chapter in matrix_data.index:
        row_data = [str(chapter)]
        for country in top_countries[:15]:
            val = matrix_data.loc[chapter, country]
            row_data.append(str(int(val)) if val > 0 else "·")
        content += "| " + " | ".join(row_data) + " |\n"

    top_chapter = matrix_data.sum(axis=1).idxmax()
    top_chapter_count = int(matrix_data.sum(axis=1).max())
    top_country = matrix_data.sum(axis=0).idxmax()
    top_country_count = int(matrix_data.sum(axis=0).max())
    hot_cells = int((matrix_data.values >= 5).sum())

    content += f"""
## یافته‌های کلیدی

1. **فصل پرپتانسیل**: فصل {top_chapter} با {top_chapter_count} جفت رشد قوی، بیشترین پتانسیل را دارد.
2. **کشور پرتنوع**: کشور {top_country} با {top_country_count} جفت رشد قوی، بیشترین تنوع محصولی رشد را دارد.
3. **نقاط داغ**: {hot_cells} سلول با مقدار ≥ ۵ وجود دارد که نشان‌دهنده فرصت‌های متمرکز فصل-به-کشور است.
4. سلول‌های خالی (·) یعنی آن فصل به آن کشور جفت رشد قوی ندارد — لزوماً صادرات صفر، بلکه فقدان رشد معنادار است.

## مراجع
- [[_executive-ranking]]
- [[by-target-country]]
- [[task-11-trend-classification]]
"""
    output_path = OUTPUT_DIR / "chapter-country-matrix.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Saved: {output_path}")


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() -> int:
    print("=" * 60)
    print("task-12: رتبه‌بندی کاندیدهای صادرات (هدف نهایی پروژه)")
    print("=" * 60)

    print("\n[1/6] Loading data...")
    by_hs = pd.read_parquet(INPUT_HS_PATH)
    pairs = pd.read_parquet(INPUT_PAIRS_PATH)
    print(f"  HS codes: {len(by_hs):,}, Pairs: {len(pairs):,}")

    print("\n[2/6] Filtering candidates (membership approach)...")
    filtered = filter_candidates(by_hs, pairs)

    print("\n[3/6] Computing export_score...")
    ranked = compute_export_score(filtered, pairs)

    print("\n[4/6] Computing risk flags...")
    ranked = compute_risk_flags(ranked, pairs)

    print("\n[5/6] Building final ranked table...")
    final = build_ranked_table(ranked, pairs)

    # اعتبارسنجی قبل از ذخیره
    ok = validate_outputs(final, by_hs, pairs)

    print("\n[6/6] Saving outputs...")
    schema = pa.schema([
        ("rank", pa.int32()),
        ("hs_code", pa.string()),
        ("hs_description", pa.string()),
        ("hs_chapter", pa.string()),
        ("export_score", pa.float64()),
        ("recommendation", pa.string()),
        ("risk_flags", pa.string()),
        ("trend_category", pa.string()),
        ("cagr_5y_aggregated", pa.float64()),
        ("slope_aggregated", pa.float64()),
        ("mean_recent_3y_aggregated", pa.float64()),
        ("n_destinations_active", pa.int32()),
        ("trend_consistency_aggregated", pa.float64()),
        ("cv_aggregated", pa.float64()),
        ("total_value_5y", pa.float64()),
        ("total_value_1404", pa.float64()),
        ("n_strong_growth", pa.int32()),
        ("n_moderate_growth", pa.int32()),
        ("n_emerging", pa.int32()),
        ("n_declining", pa.int32()),
        ("n_disappearing", pa.int32()),
        ("n_significant_pairs", pa.int32()),
        ("top_5_countries", pa.string()),
        ("top_5_countries_value_1404", pa.float64()),
        ("max_country_share", pa.float64()),
        ("score_growth", pa.float64()),
        ("score_slope", pa.float64()),
        ("score_volume", pa.float64()),
        ("score_diversity", pa.float64()),
        ("score_consistency", pa.float64()),
        ("score_volatility_penalty", pa.float64()),
    ])
    table = pa.Table.from_pandas(final, schema=schema, preserve_index=False)
    pq.write_table(table, OUTPUT_PATH, compression="snappy")
    size_mb = OUTPUT_PATH.stat().st_size / 1e6
    print(f"  Saved: {OUTPUT_PATH} ({len(final):,} × {final.shape[1]}, {size_mb:.1f}MB snappy)")

    # گزارش‌ها
    generate_executive_ranking(final, pairs)
    generate_by_target_country(final, pairs)
    generate_chapter_country_matrix(final, pairs)

    print(f"\n{'✅' if ok else '⚠️'} task-12 complete! {len(final):,} candidates ranked "
          f"(validation {'all PASS' if ok else 'FAILED'}).")
    top1 = final.iloc[0]
    print(f"   Top recommendation: rank 1 = {top1['hs_description']} ({top1['hs_code']})")
    print(f"   Score: {top1['export_score']:.3f} | {top1['recommendation']} | risks: {top1['risk_flags']}")
    print(f"   Recommendations: {final['recommendation'].value_counts().to_dict()}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
