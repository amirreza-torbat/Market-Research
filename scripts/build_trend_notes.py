#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task-11 — ساخت یادداشت‌های Obsidian برای Top در هر دسته
========================================================

برای ۴ دسته اصلی (strong-growth, moderate-growth, emerging, declining)،
Top 30 HS Code یادداشت Obsidian + نمودار PNG می‌سازد.

**نکته روش‌شناختی (مستند در _classification-summary.md)**:
  پرامپت اولیه فیلتر `dominant_trend == category` را پیشنهاد می‌کرد، اما
  در داده واقعی ۵,۵۵۸ از ۵,۹۹۳ HS Code دسته غالب insufficient_data دارند
  (اکثر HSها فقط ۱-۲ کشورِ sparse دارند) — با آن فیلتر فقط ۳۷ یادداشت
  ساخته می‌شد. روش اصلاح‌شده: HSهایی که **حداقل یک جفت در دسته** دارند
  (n_<cat> > 0)، رتبه‌بندی با مجموع value_1404 جفت‌های همان دسته.

**متن فارسی در نمودارها**: matplotlib از RTL shaping پشتیبانی نمی‌کند؛
  متن با arabic_reshaper + python-bidi شکل‌دهی و با فونت DejaVu Sans
  (دارای گلیف فارسی) رندر می‌شود.

خروجی‌ها:
  - 06-Analysis/trend/<category>/hs-XX-XXXX-XX-XX.md  (یادداشت‌ها)
  - 06-Analysis/trend/charts/hs-XX-XXXX-XX-XX-trend.png (نمودارها)

مصرف:
  python scripts/build_trend_notes.py
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
from bidi.algorithm import get_display
import arabic_reshaper

# --- فونت: DejaVu Sans پشتیبانی گلیف فارسی دارد ---
fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "05-Data/processed/trend-classification.parquet"
INPUT_HS_PATH = REPO_ROOT / "05-Data/processed/trend-classification-by-hs.parquet"
OUTPUT_DIR = REPO_ROOT / "06-Analysis/trend"
CHARTS_DIR = OUTPUT_DIR / "charts"
YEARS = [1400, 1401, 1402, 1403, 1404]
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# دسته‌های اصلی برای یادداشت‌سازی
CATEGORIES = {
    "strong-growth": "strong_growth",
    "moderate-growth": "moderate_growth",
    "emerging": "emerging",
    "declining": "declining",
}
TOP_N = 30

CATEGORY_FA = {
    "strong_growth": "رشد قوی", "moderate_growth": "رشد متوسط",
    "weak_growth": "رشد ضعیف", "stable": "پایدار",
    "volatile": "نوسانی", "declining": "کاهشی",
    "weak_decline": "کاهش ضعیف", "emerging": "نوظهور",
    "disappearing": "محوشده", "insufficient_data": "داده ناکافی",
}

ALL_CATEGORIES = list(CATEGORY_FA.keys())


def fa(text: str) -> str:
    """متن فارسی را برای matplotlib شکل‌دهی RTL می‌کند."""
    return get_display(arabic_reshaper.reshape(str(text)))


def fa_num(x: float) -> str:
    """عدد با جداکننده هزارگان لاتین (سازگار با بقیه گزارش‌های vault)."""
    return f"{x:,.0f}"


# ----------------------------------------------------------------------------
# نمودار روند aggregated یک HS Code
# ----------------------------------------------------------------------------
def make_chart(hs_code: str, hs_description: str,
               pairs: pd.DataFrame, output_path: Path) -> None:
    yearly = [float(pairs[f"value_{y}"].sum()) for y in YEARS]
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    ax.plot(YEARS, yearly, marker="o", linewidth=2.2, markersize=8,
            color="#1a6e8e", markerfacecolor="#d4a017")
    ax.set_title(fa(f"روند صادرات: {str(hs_description)[:60]}")
                 + f"\n({hs_code})", fontsize=12)
    ax.set_xlabel(fa("سال شمسی"), fontsize=11)
    ax.set_ylabel(fa("ارزش صادرات (USD)"), fontsize=11)
    ax.set_xticks(YEARS)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, _: f"{x:,.0f}"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------------
# ساخت یک یادداشت Obsidian
# ----------------------------------------------------------------------------
def build_note(hs_code: str, hs_row: pd.Series, cat_code: str,
               cat_pairs: pd.DataFrame, all_pairs: pd.DataFrame,
               category_dir: Path) -> Path:
    pairs = all_pairs[all_pairs["hs_code"] == hs_code].copy()
    pairs = pairs.sort_values("value_1404", ascending=False)
    safe_code = hs_code.replace(".", "-")
    note_path = category_dir / f"hs-{safe_code}.md"
    chart_path = CHARTS_DIR / f"hs-{safe_code}-trend.png"
    make_chart(hs_code, hs_row["hs_description"], pairs, chart_path)

    desc = str(hs_row["hs_description"])
    total_value_5y = float(pairs[[f"value_{y}" for y in YEARS]].sum().sum())
    total_value_1404 = float(pairs["value_1404"].sum())
    cagr_agg = hs_row.get("cagr_5y_aggregated")
    cagr_str = f"{cagr_agg*100:.1f}٪" if pd.notna(cagr_agg) else "—"
    n_total = int(hs_row["n_countries_total"])
    n_cat = int(hs_row[f"n_{cat_code}"])
    gds = float(hs_row["growth_diversity_score"])
    cat_fa = CATEGORY_FA[cat_code]

    # سهم بزرگ‌ترین کشور (1404)
    top_country_row = pairs.iloc[0] if len(pairs) else None
    top_share = (float(top_country_row["value_1404"]) / total_value_1404 * 100
                 if top_country_row is not None and total_value_1404 > 0 else 0.0)

    # ---- محتوای یادداشت ----
    c = []
    a = c.append
    a("---")
    a("type: analysis")
    a(f"title: روند صادرات {desc} ({hs_code})")
    a(f"hs_code: {hs_code}")
    a(f"created: {TODAY}")
    a(f"updated: {TODAY}")
    a("status: done")
    a("tags:")
    a("  - analysis")
    a("  - trend")
    a(f"  - tariff/{safe_code}")
    a(f"  - trend-category/{cat_code}")
    a("related:")
    a('  - "[[task-11-trend-classification]]"')
    a('  - "[[_classification-summary]]"')
    a(f"folder: 06-Analysis/trend/{category_dir.name}")
    a("---")
    a("")
    a(f"# روند صادرات {desc} ({hs_code})")
    a("")
    cat_action = {"strong_growth": "select", "moderate_growth": "monitor",
                  "emerging": "select", "declining": "avoid"}[cat_code]
    a(f"**دسته یادداشت**: {cat_fa} (`{cat_code}`) | "
      f"**توصیه دسته**: `{cat_action}` | "
      f"**دسته غالب HS**: `{hs_row['dominant_trend']}`")
    a("")
    a("## خلاصه")
    a("")
    a(f"این یادداشت روند ۵ ساله (۱۴۰۰ تا ۱۴۰۴) صادرات «{desc}» را به تفکیک"
      f" کشور مقصد بررسی می‌کند. این HS Code به {n_total} کشور صادرات داشته"
      f" که {n_cat} مورد از آن‌ها در دسته **{cat_fa}** طبقه‌بندی شده‌اند."
      f" مجموع ارزش ۵ ساله معادل {fa_num(total_value_5y)} دلار و ارزش سال"
      f" ۱۴۰۴ معادل {fa_num(total_value_1404)} دلار بوده است. CAGR تجمیعی"
      f" ۵ ساله این کد {cagr_str} است و ضریب تنوع رشد آن {gds:.2f} محاسبه"
      f" شد. تحلیل دقیق‌تر رتبه‌بندی در task-12 انجام خواهد شد.")
    a("")
    a("## شاخص‌های کلی (aggregated)")
    a("")
    a("| شاخص | مقدار |")
    a("|------|-------|")
    a(f"| تعداد کشورهای مقصد | {n_total} |")
    a(f"| کشورهای فعال در ۱۴۰۴ | {int(hs_row['n_destinations_active'])} |")
    a(f"| جفت‌های دسته {cat_fa} | {n_cat} |")
    a(f"| مجموع ارزش ۵ ساله (USD) | {fa_num(total_value_5y)} |")
    a(f"| مجموع ارزش ۱۴۰۴ (USD) | {fa_num(total_value_1404)} |")
    a(f"| CAGR ۵ ساله (aggregated) | {cagr_str} |")
    a(f"| دسته غالب (dominant_trend) | `{hs_row['dominant_trend']}` |")
    a(f"| تنوع رشد (growth_diversity_score) | {gds:.2f} |")
    a(f"| ثبات روند میانگین (trend_consistency) | {float(hs_row['trend_consistency_aggregated']):.2f} |")
    a(f"| CV میانگین | {float(hs_row['cv_aggregated']):.2f} |")
    a("")
    a("## نمودار روند aggregated (مجموع همه کشورها)")
    a("")
    a(f"![[{chart_path.name}]]")
    a("")
    a("## توزیع دسته‌های جفت‌های این HS Code")
    a("")
    a("| دسته | تعداد کشور |")
    a("|------|-----------|")
    for cat in ALL_CATEGORIES:
        n = int(hs_row[f"n_{cat}"])
        if n > 0:
            a(f"| {CATEGORY_FA[cat]} (`{cat}`) | {n} |")
    a("")
    a("## کشورهای با بیشترین صادرات (Top 10)")
    a("")
    a("| کشور | ۱۴۰۰ | ۱۴۰۱ | ۱۴۰۲ | ۱۴۰۳ | ۱۴۰۴ | CAGR | دسته |")
    a("|------|------|------|------|------|------|------|------|")
    for _, row in pairs.head(10).iterrows():
        cagr = row.get("cagr_5y")
        cagr_s = f"{cagr*100:.1f}٪" if pd.notna(cagr) else "—"
        a(f"| {row['destination_country_iso2']} "
          f"({row['destination_country_fa']}) | "
          f"{fa_num(row['value_1400'])} | {fa_num(row['value_1401'])} | "
          f"{fa_num(row['value_1402'])} | {fa_num(row['value_1403'])} | "
          f"{fa_num(row['value_1404'])} | {cagr_s} | "
          f"{CATEGORY_FA[row['trend_category']]} |")
    a("")
    if cat_code in ("emerging", "strong_growth", "moderate_growth"):
        a("## جفت‌های همین دسته (رانش اصلی رشد)")
    else:
        a("## جفت‌های همین دسته (رانش اصلی افت)")
    a("")
    a("| کشور | ۱۴۰۰ | ۱۴۰۴ | MK p | توصیه |")
    a("|------|------|------|------|-------|")
    for _, row in cat_pairs.sort_values(
            "value_1404", ascending=False).head(10).iterrows():
        a(f"| {row['destination_country_iso2']} "
          f"({row['destination_country_fa']}) | "
          f"{fa_num(row['value_1400'])} | {fa_num(row['value_1404'])} | "
          f"{row['mk_p_value']:.3f} | `{row['recommendation_action']}` |")
    a("")
    a("## تحلیل کیفی")
    a("")
    # بند پویا (۱۵۰+ کلمه)
    top_iso = (top_country_row["destination_country_iso2"]
               if top_country_row is not None else "—")
    qualitative = (
        f"کد تعرفه {hs_code} («{desc}») در میان {n_total} بازار مقصد خود، "
        f"در {n_cat} بازار دسته {cat_fa} را تجربه کرده است؛ این یعنی "
        f"جریان رشد/افت این کد محدود به یک بازار نیست و سیگنال آن در چند "
        f"مقصد هم‌زمان دیده می‌شود. بزرگ‌ترین مقصد در سال ۱۴۰۴، "
        f"{top_iso} با سهم {top_share:.1f}٪ از ارزش صادرات این کد است که "
        f"نشانه {'تمرکز بالا' if top_share > 70 else 'پراکندگی متعادل'} "
        f"بازار است. CAGR تجمیعی {cagr_str} در کنار ضریب تنوع رشد "
        f"{gds:.2f} نشان می‌دهد سهم کشورهای دارای رشد مثبت (قوی، متوسط "
        f"یا نوظهور) از کل بازارهای این کد چقدر است. ثبات روند میانگین "
        f"{float(hs_row['trend_consistency_aggregated']):.2f} (از ۴) و ضریب "
        f"تغییرات {float(hs_row['cv_aggregated']):.2f} نیز کیفیت مسیر را "
        f"توصیف می‌کنند: مقادیر پایین‌تر پایداری بیشتر را نشان می‌دهد. "
        f"برای تصمیم‌گیری صادراتی، این کد در task-12 با شاخص ترکیبی "
        f"export_score (وزن‌های Decision-009) در کنار فیلترهای حداقل "
        f"حجم ۱ میلیون دلار و حداقل ۳ مقصد فعال ارزیابی خواهد شد؛ "
        f"توصیه فعلی سطح جفت، `{pairs['recommendation_action'].mode().iloc[0]}` است."
    )
    a(qualitative)
    a("")
    a("## یادداشت آماری")
    a("")
    a("> ⚠️ با ۵ نقطه زمانی، حداقل p-value ممکن در Mann-Kendall ≈ ۰.۰۲۷۵")
    a("> است؛ `mk_p < 0.05` عملاً یعنی سری کاملاً یکنواخت. معناداری را در")
    a("> کنار CAGR و R² تفسیر کنید (طبق `_classification-summary.md` §۴).")
    a("")
    a("## مراجع")
    a("")
    a("- [[task-11-trend-classification]]")
    a("- [[_classification-summary]]")
    a("- [[task-10-trend-analysis]]")
    a("- [[task-12-export-candidates]]")
    a("")

    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text("\n".join(c), encoding="utf-8")
    return note_path


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main() -> int:
    t0 = time.time()
    print("=" * 72)
    print("task-11 — ساخت یادداشت‌های Top در هر دسته")
    print("=" * 72)

    print("\n[1/3] بارگذاری داده...")
    pairs = pd.read_parquet(INPUT_PATH)
    by_hs = pd.read_parquet(INPUT_HS_PATH)
    print(f"  جفت‌ها: {len(pairs):,} | HS Codeها: {len(by_hs):,}")

    print("\n[2/3] ساخت یادداشت‌ها (روش: membership، رتبه‌بندی با ارزش دسته)...")
    total_notes = 0
    for folder_name, cat_code in CATEGORIES.items():
        category_dir = OUTPUT_DIR / folder_name
        category_dir.mkdir(parents=True, exist_ok=True)

        # HSهایی که حداقل یک جفت در این دسته دارند
        candidates = by_hs[by_hs[f"n_{cat_code}"] > 0].copy()
        # رتبه‌بندی با مجموع value_1404 جفت‌های همین دسته
        cat_pairs = pairs[pairs["trend_category"] == cat_code]
        cat_val = (cat_pairs.groupby("hs_code")["value_1404"].sum()
                   .rename("cat_value_1404"))
        candidates = candidates.merge(cat_val, on="hs_code", how="left")
        candidates["cat_value_1404"] = candidates["cat_value_1404"].fillna(0.0)
        top_hs = candidates.nlargest(TOP_N, "cat_value_1404")

        # نگاشت جفت‌های هر HS در این دسته
        cat_pairs_by_hs = {
            hs: grp for hs, grp in cat_pairs.groupby("hs_code")
        }

        print(f"\n  {cat_code}: {len(candidates)} HS کاندید → "
              f"{len(top_hs)} یادداشت")
        for i, (_, hs_row) in enumerate(top_hs.iterrows(), 1):
            build_note(hs_row["hs_code"], hs_row, cat_code,
                       cat_pairs_by_hs.get(hs_row["hs_code"],
                                           cat_pairs.iloc[0:0]),
                       pairs, category_dir)
            total_notes += 1
            if i % 10 == 0:
                print(f"    {i}/{len(top_hs)}")

    print(f"\n[3/3] کامل شد — {total_notes} یادداشت، "
          f"{total_notes} نمودار در {time.time() - t0:.1f} ثانیه")
    return 0


if __name__ == "__main__":
    sys.exit(main())
