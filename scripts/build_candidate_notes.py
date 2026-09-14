#!/usr/bin/env python3
"""
task-12 — ساخت یادداشت‌های تفصیلی برای Top 50 کاندید صادرات.

ورودی‌ها:
  - 05-Data/processed/export-candidates-ranked.parquet (task-12)
  - 05-Data/processed/trend-classification.parquet (task-11)

خروجی‌ها:
  - 06-Analysis/export-candidates/rank-NN-hs-XX-XXXX-XX-XX.md (۵۰ یادداشت)
  - 06-Analysis/export-candidates/charts/rank-NN-hs-XX-XXXX-XX-XX.png (۵۰ نمودار)

هر یادداشت: خلاصه، شاخص‌ها، روند aggregated، تجزیه نمره، نمودار (روند + سهم
کشورها)، جدول ۵ ساله Top 15 کشور، تحلیل کیفی (۲۰۰+ کلمه)، توصیه‌ها.
متن فارسی نمودارها با arabic_reshaper + bidi + DejaVu Sans شکل‌دهی می‌شود.
⚠️ Issue-008: ۱۴۰۵ موجود نیست → جدول ۵ ساله (۱۴۰۰-۱۴۰۴).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from bidi.algorithm import get_display
import arabic_reshaper

fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_RANKED_PATH = REPO_ROOT / "05-Data/processed/export-candidates-ranked.parquet"
INPUT_PAIRS_PATH = REPO_ROOT / "05-Data/processed/trend-classification.parquet"
OUTPUT_DIR = REPO_ROOT / "06-Analysis/export-candidates"
CHARTS_DIR = OUTPUT_DIR / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))
TODAY = datetime.now(TEHRAN_TZ).strftime("%Y-%m-%d")
YEARS = [1400, 1401, 1402, 1403, 1404]
TOP_N = 50

CATEGORY_FA = {
    "strong_growth": "رشد قوی", "moderate_growth": "رشد متوسط",
    "weak_growth": "رشد ضعیف", "stable": "پایدار",
    "volatile": "نوسانی", "declining": "کاهشی",
    "weak_decline": "کاهش ضعیف", "emerging": "نوظهور",
    "disappearing": "محوشده", "insufficient_data": "داده ناکافی",
}


def fa(text: str) -> str:
    """متن فارسی را برای matplotlib شکل‌دهی RTL می‌کند."""
    return get_display(arabic_reshaper.reshape(str(text)))


def fa_num(x: float) -> str:
    return f"{x:,.0f}"


# ----------------------------------------------------------------------------
# نمودار دو پنلی: روند ۵ ساله + سهم کشورها در ۱۴۰۴
# ----------------------------------------------------------------------------
def make_chart(hs_code: str, hs_description: str,
               country_pairs: pd.DataFrame, output_path: Path) -> None:
    yearly = [float(country_pairs[f"value_{y}"].sum()) for y in YEARS]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), constrained_layout=True)

    # پنل ۱: روند ۵ ساله aggregated
    ax1.plot(YEARS, yearly, marker="o", linewidth=2.2, markersize=8,
             color="#1a6e8e", markerfacecolor="#d4a017")
    ax1.set_title(fa(f"روند صادرات: {str(hs_description)[:48]}") + f"\n({hs_code})", fontsize=11)
    ax1.set_xlabel(fa("سال شمسی"), fontsize=11)
    ax1.set_ylabel(fa("ارزش (میلیون USD)"), fontsize=11)
    ax1.set_xticks(YEARS)
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x/1e6:,.0f}"))

    # پنل ۲: سهم کشورها در ۱۴۰۴ (Top 10)
    top_1404 = country_pairs.nlargest(10, "value_1404")
    ax2.barh(range(len(top_1404)), top_1404["value_1404"] / 1e6,
             color="#ff7f0e", height=0.72)
    ax2.set_yticks(range(len(top_1404)))
    ax2.set_yticklabels(
        [f"{r['destination_country_iso2']} ({str(r['destination_country_fa'])[:12]})"
         for _, r in top_1404.iterrows()], fontsize=9)
    ax2.set_title(fa("سهم کشورهای مقصد در ۱۴۰۴ (Top 10)"), fontsize=11)
    ax2.set_xlabel(fa("ارزش (میلیون USD)"), fontsize=11)
    ax2.invert_yaxis()
    ax2.grid(True, axis="x", alpha=0.3)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------------
# ساخت یک یادداشت تفصیلی
# ----------------------------------------------------------------------------
def build_note(rank_row: pd.Series, pairs: pd.DataFrame, n_total: int) -> Path:
    hs_code = rank_row["hs_code"]
    rank = int(rank_row["rank"])

    hs_pairs = pairs[pairs["hs_code"] == hs_code].copy().sort_values(
        "value_1404", ascending=False)

    safe_code = hs_code.replace(".", "-")
    note_path = OUTPUT_DIR / f"rank-{rank:02d}-hs-{safe_code}.md"
    chart_path = CHARTS_DIR / f"rank-{rank:02d}-hs-{safe_code}.png"

    make_chart(hs_code, rank_row["hs_description"], hs_pairs, chart_path)

    total_5y = float(hs_pairs[[f"value_{y}" for y in YEARS]].sum().sum())
    total_1404 = float(hs_pairs["value_1404"].sum())
    cagr = rank_row.get("cagr_5y_aggregated")
    cagr_str = f"{cagr*100:.2f}%" if pd.notna(cagr) else "N/A"
    n_strong = int(rank_row.get("n_strong_growth", 0))
    n_moderate = int(rank_row.get("n_moderate_growth", 0))
    n_emerging = int(rank_row.get("n_emerging", 0))
    n_declining = int(rank_row.get("n_declining", 0))
    n_disappearing = int(rank_row.get("n_disappearing", 0))
    n_countries = int(rank_row.get("n_destinations_active", 0))
    n_sig = int(rank_row.get("n_significant_pairs", 0))
    cv_val = float(rank_row.get("cv_aggregated", 0) or 0)
    cons_val = float(rank_row.get("trend_consistency_aggregated", 0) or 0)
    share_val = float(rank_row.get("max_country_share", 0) or 0)
    percentile = (1 - rank / n_total) * 100

    cats_txt = " / ".join(filter(None, [
        "رشد قوی" if n_strong else "", "رشد متوسط" if n_moderate else "",
        "نوظهور" if n_emerging else ""]))

    content = f"""---
type: analysis
title: کاندید صادرات رتبه {rank} — {str(rank_row['hs_description'])[:60]} ({hs_code})
rank: {rank}
hs_code: {hs_code}
created: {TODAY}
updated: {TODAY}
status: done
tags:
  - analysis
  - export-candidate
  - rank/{rank}
  - tariff/{safe_code}
related:
  - "[[task-12-export-candidates]]"
  - "[[_executive-ranking]]"
  - "[[by-target-country]]"
  - "[[chapter-country-matrix]]"
folder: 06-Analysis/export-candidates
---

# 🎯 کاندید صادرات رتبه {rank} — {rank_row['hs_description']} ({hs_code})

**فصل HS**: {rank_row['hs_chapter']} | **توصیه**: `{rank_row['recommendation']}` | **ریسک‌ها**: `{rank_row['risk_flags']}`

## خلاصه

این محصول با **نمره {rank_row['export_score']:.3f}** در **رتبه {rank} از {n_total:,}** کاندید صادرات (صدک {percentile:.1f}) قرار دارد. کد تعرفه {hs_code} ({rank_row['hs_description']}) به {n_countries} کشور مقصد فعال صادرات داشته و جفت‌های رو به رشد آن در دسته‌های {cats_txt} قرار می‌گیرند. مجموع ارزش ۵ ساله معادل {fa_num(total_5y)} دلار و ارزش سال ۱۴۰۴ معادل {fa_num(total_1404)} دلار بوده است. این یادداشت جزئیات روند، بازارهای هدف، تجزیه نمره و ریسک‌های این کاندید را برای تصمیم‌گیری صادراتی ارائه می‌کند.

**توصیه استراتژیک**: {rank_row['recommendation']} (طبق آستانه‌های recipe-09 §۷ — برای بحث کالیبراسیون به [[_executive-ranking]] §۵ مراجعه کنید)

## شاخص‌های کلیدی

| شاخص | مقدار |
|------|-------|
| رتبه | {rank} (از {n_total:,}) |
| نمره صادرات (export_score) | {rank_row['export_score']:.3f} |
| توصیه | {rank_row['recommendation']} |
| ریسک‌ها | {rank_row['risk_flags']} |
| CAGR ۵ ساله (aggregated) | {cagr_str} |
| حجم ۳ سال اخیر (USD) | {fa_num(rank_row.get('mean_recent_3y_aggregated', 0))} |
| تعداد کشورهای فعال (۱۴۰۴) | {n_countries} |
| ثبات روند (میانگین جفت‌ها، ۰-۴) | {cons_val:.2f} |
| ضریب تغییرات (میانگین جفت‌ها) | {cv_val:.2f} |
| سهم بزرگ‌ترین کشور (۱۴۰۴) | {share_val*100:.1f}% |
| جفت‌های معنادار آماری | {n_sig} از {len(hs_pairs)} |

## روند ۵ ساله aggregated (⚠️ Issue-008: ۱۴۰۵ در داده نیست)

| سال | ارزش (USD) |
|------|------------|
"""
    for y in YEARS:
        content += f"| {y} | {fa_num(float(hs_pairs[f'value_{y}'].sum()))} |\n"

    content += f"""
## تجزیه نمره (وزن‌های Decision-009)

| مولفه | وزن | مقدار نرمال | سهم نمره |
|-------|-----|-------------|----------|
| رشد (CAGR) | ۰.۳۰ | {rank_row.get('score_growth', 0)/0.30:.3f} | +{rank_row.get('score_growth', 0):.3f} |
| شیب روند | ۰.۲۰ | {rank_row.get('score_slope', 0)/0.20:.3f} | +{rank_row.get('score_slope', 0):.3f} |
| حجم | ۰.۲۰ | {rank_row.get('score_volume', 0)/0.20:.3f} | +{rank_row.get('score_volume', 0):.3f} |
| تنوع بازار | ۰.۱۰ | {rank_row.get('score_diversity', 0)/0.10:.3f} | +{rank_row.get('score_diversity', 0):.3f} |
| ثبات | ۰.۱۰ | {rank_row.get('score_consistency', 0)/0.10:.3f} | +{rank_row.get('score_consistency', 0):.3f} |
| جریمه نوسان | ۰.۱۰ | {rank_row.get('score_volatility_penalty', 0)/0.10:.3f} | -{rank_row.get('score_volatility_penalty', 0):.3f} |
| **جمع** | | | **{rank_row['export_score']:.3f}** |

## نمودار روند و سهم کشورها

![[charts/{chart_path.name}]]

## جدول ۵ ساله به تفکیک کشور (Top 15)

| کشور | ۱۴۰۰ | ۱۴۰۱ | ۱۴۰۲ | ۱۴۰۳ | ۱۴۰۴ | CAGR | دسته |
|------|------|------|------|------|------|------|------|
"""
    top_15 = hs_pairs.head(15)
    for _, row in top_15.iterrows():
        cagr_pair = row.get("cagr_5y")
        cagr_pair_str = f"{cagr_pair*100:.1f}%" if pd.notna(cagr_pair) else "—"
        content += (f"| {row['destination_country_iso2']} ({row['destination_country_fa']}) "
                    f"| {fa_num(row['value_1400'])} | {fa_num(row['value_1401'])} "
                    f"| {fa_num(row['value_1402'])} | {fa_num(row['value_1403'])} "
                    f"| {fa_num(row['value_1404'])} | {cagr_pair_str} "
                    f"| {CATEGORY_FA.get(row['trend_category'], row['trend_category'])} |\n")

    # --- تحلیل کیفی (۲۰۰+ کلمه) ---
    growth_txt = ("رشد قوی" if (pd.notna(cagr) and cagr > 0.1)
                  else "رشد مثبت" if (pd.notna(cagr) and cagr > 0)
                  else "CAGR قابل‌محاسبه ندارد (نوظهور یا داده اولیه صفر)")
    vol_m = float(rank_row.get("mean_recent_3y_aggregated", 0) or 0) / 1e6
    top_countries_txt = str(rank_row.get("top_5_countries", ""))
    share_txt = ("تمرکز شدید بازار" if share_val > 0.7
                 else "تمرکز متوسط" if share_val > 0.4 else "پراکندگی مناسب")
    sig_txt = ("قوی" if n_sig >= 5 else "متوسط" if n_sig >= 2 else "محدود")

    content += f"""
## تحلیل کیفی

{rank_row['hs_description']} با کد تعرفه {hs_code} و فصل HS {rank_row['hs_chapter']}، یکی از کاندیدهای صادرات ایران با رتبه {rank} از {n_total:,} است (صدک {percentile:.1f}). این محصول با نمره {rank_row['export_score']:.3f} به {n_countries} کشور مقصد فعال صادرات دارد و تحلیل ۵ ساله نشان می‌دهد که {n_strong} جفت با رشد قوی، {n_moderate} جفت با رشد متوسط و {n_emerging} جفت نوظهور دارد. در مقابل، {n_declining} جفت کاهشی و {n_disappearing} جفت محوشده نیز دیده می‌شود که ضرورت پایش بازارهای در حال افول را یادآوری می‌کند.

روند کلی aggregated با CAGR {cagr_str} نشان‌دهنده **{growth_txt}** است. حجم ۳ سال اخیر معادل {vol_m:,.0f} میلیون دلار در سال است که اهمیت اقتصادی این محصول را نشان می‌دهد و ارزش سال ۱۴۰۴ آن به {fa_num(total_1404)} دلار رسیده است. ضریب تغییرات {cv_val:.2f} {"نوسان قابل توجهی" if cv_val > 1.0 else "نوسان نسبتاً بالایی" if cv_val > 0.7 else "نوسان متعادلی"} را نشان می‌دهد — یادآوری: این شاخص میانگین cv جفت‌هاست و با صفر-پرکردن سال‌های خالی متورم می‌شود؛ نمودار روند بالا تصویر واقعی‌تری از الگوی نوسان می‌دهد. ثبات روند {cons_val:.2f} از ۴ یعنی {"بیشترِ سال‌ها روند هم‌جهت بوده" if cons_val >= 2 else "جهت روند بین سال‌ها جابه‌جا شده" if cons_val >= 1 else "روند پراکنده و کم‌ثباتی"} است.

از منظر بازار هدف، مهم‌ترین جفت‌های رشد عبارت‌اند از: {top_countries_txt}. سهم بزرگ‌ترین کشور مقصد از ارزش ۱۴۰۴ برابر {share_val*100:.1f} درصد است ({share_txt}) — {"تنوع‌بخشی به بازارهای مقصد، اولویت ریسک این کاندید است" if share_val > 0.7 else "سبد بازار نسبتاً متعادل است و ریسک تمرکز کنترل‌شده به نظر می‌رسد"}. این ترکیب بازار تعیین می‌کند که توسعه صادرات بیشتر مبتنی بر تعمیق بازارهای فعلی باشد یا گسترش به مقاصد جدید.

از منظر اعتبار آماری، {n_sig} جفت از جفت‌های این HS پرچم `is_significant` دارند (Mann-Kendall p<0.05 یا نوظهور/محوشده) — پشتوانه آماری {sig_txt}. با توجه به محدودیت توان آزمون MK در n=5 (حداقل p ممکن ≈ ۰.۰۲۷۵)، این سیگنال را باید در کنار CAGR، R² و ثبات روند تفسیر کرد، نه به‌تنهایی. {"⚠️ **ریسک‌های شناسایی‌شده**: " + str(rank_row['risk_flags']) + " — پیش از تصمیم‌گیری، سیر ۱۴۰۳→۱۴۰۴ و تمرکز بازار را بررسی کنید." if str(rank_row['risk_flags']) != 'none' else "ریسک تمایزبخش خاصی غیر از نوسان عمومی شناسایی نشد."}

## توصیه‌های استراتژیک

- **اولویت نسبی**: رتبه {rank} از {n_total:,} (صدک {percentile:.1f}) در میان کاندیدهای واجد شرایط
- **انتخاب برای صادرات**: {"✅ در اولویت نخست قرار دارد" if rank <= 10 else "⏳ در میان Top 50 قرار دارد — نیاز به بررسی بیشتر" if rank <= 50 else "نیاز به بررسی بیشتر"}
- **کشورهای هدف**: {top_countries_txt}
- {"**هشدار تمرکز**: سهم بزرگ‌ترین کشور " + f"{share_val*100:.1f}%" + " است — تنوع‌بخشی توصیه می‌شود." if share_val > 0.7 else "**تنوع بازار**: مناسب یا قابل‌قبول."}
- **اقدام پیشنهادی**: {"توسعه بازار در کشورهای هدف فعلی + ورود به بازارهای جدید" if rank_row['recommendation'] == 'select' else "حفظ بازار فعلی + بررسی فرصت‌های جدید" if rank_row['recommendation'] == 'monitor' else "بررسی عمیق‌تر قبل از سرمایه‌گذاری"} (رتبه {rank} از {n_total:,})
- **نکته آماری**: روندها بر پایه ۵ سال کامل (۱۴۰۰-۱۴۰۴) است؛ داده ۱۴۰۵ هنوز منتشر نشده (Issue-008) و پس از انتشار، به‌روزرسانی re-run توصیه می‌شود.

## مراجع
- [[task-12-export-candidates]]
- [[_executive-ranking]]
- [[by-target-country]]
- [[chapter-country-matrix]]
- [[task-11-trend-classification]]
"""
    with open(note_path, "w", encoding="utf-8") as f:
        f.write(content)
    return note_path


def main() -> int:
    print("=" * 60)
    print(f"task-12: ساخت یادداشت‌های تفصیلی Top {TOP_N}")
    print("=" * 60)

    print("\n[1/2] Loading data...")
    ranked = pd.read_parquet(INPUT_RANKED_PATH)
    pairs = pd.read_parquet(INPUT_PAIRS_PATH)
    n_total = len(ranked)
    print(f"  Ranked: {n_total:,}, Pairs: {len(pairs):,}")

    print(f"\n[2/2] Building notes for Top {TOP_N}...")
    note_paths = []
    for idx, (_, row) in enumerate(ranked.head(TOP_N).iterrows(), 1):
        note_paths.append(build_note(row, pairs, n_total))
        if idx % 10 == 0:
            print(f"  {idx}/{TOP_N}")

    # اعتبارسنجی
    charts = sorted(CHARTS_DIR.glob("rank-*.png"))
    missing_sections = []
    for p in note_paths:
        txt = p.read_text(encoding="utf-8")
        for sec in ["## خلاصه", "## شاخص‌های کلیدی", "## تجزیه نمره",
                    "## نمودار روند", "## جدول ۵ ساله", "## تحلیل کیفی",
                    "## توصیه‌های استراتژیک"]:
            if sec not in txt:
                missing_sections.append(f"{p.name}:{sec}")
        # تحلیل کیفی ۲۰۰+ کلمه
        qual = txt.split("## تحلیل کیفی")[1].split("## توصیه‌های")[0]
        n_words = len(qual.split())
        if n_words < 200:
            missing_sections.append(f"{p.name}:qualitative<{n_words}w")

    print(f"\n✅ Done! {len(note_paths)} notes + {len(charts)} charts built.")
    if missing_sections:
        print("⚠️ Issues:", missing_sections[:10])
        return 1
    print("  All notes contain required sections; qualitative analysis ≥200 words each.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
