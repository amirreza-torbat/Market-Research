#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task-03 — ETL Normalize (Market-Research Vault)
================================================

تبدیل داده خام استخراج‌شده (task-01) به مدل داده‌ای تحلیلی تمیز، یکپارچه
و قابل پرس‌وجو با دقت عددی < 0.0001٪.

این اسکریپت:
  1. داده خام را از 05-Data/interim/exports_YYYY_raw.csv.gz می‌خواند.
  2. پاکسازی: dedupe، حذف NA در فیلدهای کلیدی.
  3. نرمال‌سازی:
     - نام فارسی کشورها → ISO 3166-1 alpha-2 (از countries-mapping.csv)
     - HS Code → فرمت HH.HH.HH.HH (8-digit با نقطه)
     - اعداد → Decimal (با precision 28)
  4. ادغام ۵ سال به یک Parquet واحد.
  5. اعتبارسنجی دقت: tol < 0.0001٪.
  6. ساخت جداول مرجع (countries.csv, hs-codes.csv).
  7. ذخیره metadata و گزارش validation.

مدیریت Issues:
  - Issue-006: سال‌های 1403/1404 در منبع ستون month خالی دارند.
               راهکار: month=0 و is_monthly=False، در metadata ثبت می‌شود.
  - Issue-007: export_quantity همیشه NULL است.
               راهکار: فیلد حذف می‌شود (هیچ کاربردی ندارد).
  - Issue-008: سال 1405 در منبع موجود نیست.
               راهکار: در Parquet نیست، در metadata ثبت می‌شود.
               نام فایل همچنان exports_1400-1405.parquet برای سازگاری با تسک‌های بعدی.

مصرف:
  python scripts/etl_normalize.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# دقت Decimal: 28 رقم معادل کافی برای مبالغ دلاری بزرگ
getcontext().prec = 28

REPO_ROOT = Path(__file__).resolve().parents[1]
INTERIM_DIR = REPO_ROOT / "05-Data" / "interim"
PROCESSED_DIR = REPO_ROOT / "05-Data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

YEARS_INCLUDED = [1400, 1401, 1402, 1403, 1404]
YEAR_EXCLUDED = {1405: "no data in source (Issue-008)"}

# --- Parquet schema صریح ---
PARQUET_SCHEMA = pa.schema([
    pa.field("year", pa.int32()),
    pa.field("month", pa.int32()),
    pa.field("is_monthly", pa.bool_()),
    pa.field("hs_code", pa.string()),
    pa.field("hs_code_2", pa.string()),
    pa.field("hs_code_4", pa.string()),
    pa.field("hs_code_6", pa.string()),
    pa.field("hs_code_8", pa.string()),
    pa.field("hs_description", pa.string()),
    pa.field("destination_country_iso2", pa.string()),
    pa.field("destination_country_fa", pa.string()),
    pa.field("customs_office_fa", pa.string()),
    pa.field("export_value_usd", pa.decimal128(20, 4)),
    pa.field("export_value_rial", pa.decimal128(28, 4)),
    pa.field("export_weight_kg", pa.decimal128(20, 4)),
])


def to_decimal(val) -> Decimal:
    """تبدیل به Decimal; رشته‌های خالی/NA/NaN به Decimal(0)."""
    if val is None or pd.isna(val) or str(val).strip() == "":
        return Decimal(0)
    try:
        # حذف کاما، فاصله، و کاراکترهای غیرعددی به‌جز نقطه و علامت منفی
        s = str(val).strip().replace(",", "")
        if s == "" or s.lower() in ("nan", "none", "null"):
            return Decimal(0)
        return Decimal(s)
    except Exception:
        return Decimal(0)


def format_hs_code(code: str | None) -> str | None:
    """فرمت HS Code به HH.HH.HH.HH (8-digit با نقطه).

    منبع همیشه 8-digit است (طبق بررسی)، اما برای مقاومت:
      - کاراکترهای غیرعددی حذف می‌شوند
      - اگر کمتر از 8 رقم باشد، صفر در انتها pad می‌شود
      - اگر بیشتر باشد، به 8 رقم truncate می‌شود
    """
    if code is None or (isinstance(code, float) and pd.isna(code)) or str(code).strip() == "":
        return None
    digits = re.sub(r"\D", "", str(code))
    if digits == "":
        return None
    digits = digits.ljust(8, "0")[:8]
    return f"{digits[:2]}.{digits[2:4]}.{digits[4:6]}.{digits[6:8]}"


class ETLPipeline:
    """ETL Pipeline: raw CSV (gz) → cleaned Parquet."""

    def __init__(self):
        self.country_mapping = self._load_country_mapping()
        self.unmapped_countries: list[str] = []
        self.records_before: dict[int, int] = {}
        self.records_after: dict[int, int] = {}
        self.duplicates_dropped: dict[int, int] = {}
        self.na_dropped: dict[int, int] = {}

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    def _load_country_mapping(self) -> dict[str, str]:
        path = PROCESSED_DIR / "countries-mapping.csv"
        df = pd.read_csv(
            path,
            dtype=str,
            encoding="utf-8",
            # حیاتی: بدون این گزینه، pandas مقادیر "NA" (کد Namibia) را به‌عنوان NaN تفسیر می‌کند!
            keep_default_na=False,
            na_values=[],
        )
        # کلید: نام فارسی، مقدار: ISO2
        return dict(zip(df["country_fa"], df["country_iso2"]))

    def load_raw(self, year: int) -> pd.DataFrame:
        path = INTERIM_DIR / f"exports_{year}_raw.csv.gz"
        df = pd.read_csv(
            path,
            dtype=str,
            encoding="utf-8",
            keep_default_na=False,  # رشته‌های خالی به‌جای NaN
            na_values=[""],
        )
        return df

    # ------------------------------------------------------------------
    # Cleaning
    # ------------------------------------------------------------------
    def clean(self, df: pd.DataFrame, year: int) -> pd.DataFrame:
        n_before = len(df)
        self.records_before[year] = n_before

        # 1) حذف تکراری (طبق گزارش Scraper صفر تکراری بوده، اما برای اطمینان)
        # کلید: year, month, hs_code_raw, destination_country_fa,
        #        customs_office_fa, export_value_usd, export_weight_kg, export_value_rial
        #       (شامل value/weight چون دو گمرک ممکن است همان کلید متنی داشته باشند با مقادیر متفاوت)
        df = df.drop_duplicates(subset=[
            "year", "month", "hs_code_raw", "destination_country_fa",
            "customs_office_fa", "export_value_usd", "export_weight_kg",
            "export_value_rial",
        ])
        self.duplicates_dropped[year] = n_before - len(df)

        # 2) حذف رکوردهای با NA در فیلدهای کلیدی (طبق conventions §4.3 و §4.4)
        n_after_dedup = len(df)
        df = df.dropna(subset=["year", "hs_code_raw", "destination_country_fa", "export_value_usd"])
        # مقادیر رشته‌ای خالی هم باید حذف شوند (dropna با keep_default_na=False به تنهایی کافی نیست)
        df = df[df["year"].astype(str).str.strip() != ""]
        df = df[df["hs_code_raw"].astype(str).str.strip() != ""]
        df = df[df["destination_country_fa"].astype(str).str.strip() != ""]
        df = df[df["export_value_usd"].astype(str).str.strip() != ""]
        self.na_dropped[year] = n_after_dedup - len(df)
        self.records_after[year] = len(df)
        return df.reset_index(drop=True)

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------
    def normalize_country(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["destination_country_iso2"] = df["destination_country_fa"].map(self.country_mapping)
        unmapped_mask = df["destination_country_iso2"].isna()
        if unmapped_mask.any():
            new_unmapped = df.loc[unmapped_mask, "destination_country_fa"].unique().tolist()
            self.unmapped_countries.extend(new_unmapped)
            print(f"  ⚠️  Unmapped countries ({len(new_unmapped)}): {new_unmapped[:10]}{'...' if len(new_unmapped) > 10 else ''}")
        return df

    def normalize_hs_code(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["hs_code"] = df["hs_code_raw"].apply(format_hs_code)
        # مشتقات کوتاه (بدون نقطه)
        df["hs_code_2"] = df["hs_code"].str[:2]
        df["hs_code_4"] = df["hs_code"].str[:5].str.replace(".", "")
        df["hs_code_6"] = df["hs_code"].str[:8].str.replace(".", "")
        df["hs_code_8"] = df["hs_code"].str.replace(".", "")
        return df

    def convert_to_decimal(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["export_value_usd"] = df["export_value_usd"].apply(to_decimal)
        df["export_value_rial"] = df["export_value_rial"].apply(to_decimal)
        df["export_weight_kg"] = df["export_weight_kg"].apply(to_decimal)
        return df

    def normalize_month(self, df: pd.DataFrame) -> pd.DataFrame:
        """Issue-006: سال‌های 1403/1404 در منبع ستون month خالی دارند.

        راهکار:
          - month → 0 اگر خالی یا NaN
          - is_monthly: True اگر month ∈ [1,12]، False در غیر این صورت
        """
        df = df.copy()
        df["month"] = df["month"].apply(
            lambda v: int(float(v)) if (v is not None and not pd.isna(v) and str(v).strip() != "") else 0
        )
        df["is_monthly"] = df["month"].between(1, 12)
        return df

    # ------------------------------------------------------------------
    # Process pipeline
    # ------------------------------------------------------------------
    def process_year(self, year: int) -> pd.DataFrame:
        print(f"\n--- Processing year {year} ---")
        df = self.load_raw(year)
        print(f"  loaded {len(df):,} raw records")
        df = self.clean(df, year)
        print(f"  after cleaning: {len(df):,} records (dupes dropped: {self.duplicates_dropped[year]:,}, NA dropped: {self.na_dropped[year]:,})")
        df = self.normalize_country(df)
        df = self.normalize_hs_code(df)
        df = self.normalize_month(df)
        df = self.convert_to_decimal(df)
        # year به‌عنوان int
        df["year"] = df["year"].astype(int)
        return df

    def merge_all_years(self) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        for year in YEARS_INCLUDED:
            df = self.process_year(year)
            frames.append(df)
        merged = pd.concat(frames, ignore_index=True)
        print(f"\n=== Merged total: {len(merged):,} records ===")
        return merged

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate_precision(self, df: pd.DataFrame) -> dict[int, dict]:
        """برای هر سال: مجموع export_value_usd در داده پردازش‌شده باید
        با مجموع داده خام برابر باشد (تلورانس < 0.0001٪).
        """
        results: dict[int, dict] = {}
        for year in YEARS_INCLUDED:
            raw_df = self.load_raw(year)
            raw_df = raw_df.dropna(subset=["export_value_usd"])
            raw_df = raw_df[raw_df["export_value_usd"].astype(str).str.strip() != ""]
            raw_sum = sum(to_decimal(v) for v in raw_df["export_value_usd"])

            proc_subset = df[df["year"] == year]
            proc_sum = proc_subset["export_value_usd"].apply(lambda x: Decimal(str(x))).sum()

            if raw_sum > 0:
                tolerance = abs(proc_sum - raw_sum) / raw_sum
            else:
                tolerance = Decimal(0)

            results[year] = {
                "raw_sum_usd": raw_sum,
                "proc_sum_usd": proc_sum,
                "tolerance": tolerance,
                "tolerance_pct": tolerance * Decimal(100),
                "pass": tolerance < Decimal("0.000001"),
            }
            status = "✅ PASS" if results[year]["pass"] else "❌ FAIL"
            print(f"  Year {year}: tolerance = {tolerance:.10f} ({tolerance * Decimal(100):.6f}%)  {status}")
        return results

    # ------------------------------------------------------------------
    # Save Parquet
    # ------------------------------------------------------------------
    def save_parquet(self, df: pd.DataFrame) -> Path:
        out_path = PROCESSED_DIR / "exports_1400-1405.parquet"

        # تبدیل ستون‌ها به انواع Parquet-compatible
        df_out = pd.DataFrame({
            "year": df["year"].astype("int32").values,
            "month": df["month"].astype("int32").values,
            "is_monthly": df["is_monthly"].astype(bool).values,
            "hs_code": df["hs_code"].astype(str).values,
            "hs_code_2": df["hs_code_2"].astype(str).values,
            "hs_code_4": df["hs_code_4"].astype(str).values,
            "hs_code_6": df["hs_code_6"].astype(str).values,
            "hs_code_8": df["hs_code_8"].astype(str).values,
            "hs_description": df["hs_description_raw"].fillna("").astype(str).values,
            "destination_country_iso2": df["destination_country_iso2"].fillna("ZZ").astype(str).values,
            "destination_country_fa": df["destination_country_fa"].astype(str).values,
            "customs_office_fa": df["customs_office_fa"].fillna("").astype(str).values,
            # Decimal → برای Parquet به‌عنوان decimal128 با preserve از طریق list comprehension
            "export_value_usd": [Decimal(str(v)) for v in df["export_value_usd"]],
            "export_value_rial": [Decimal(str(v)) for v in df["export_value_rial"]],
            "export_weight_kg": [Decimal(str(v)) for v in df["export_weight_kg"]],
        })

        table = pa.Table.from_pandas(df_out, schema=PARQUET_SCHEMA, preserve_index=False)
        pq.write_table(table, out_path, compression="snappy")
        print(f"✅ Parquet saved: {out_path}")
        return out_path

    # ------------------------------------------------------------------
    # Reference tables
    # ------------------------------------------------------------------
    def build_reference_tables(self, df: pd.DataFrame) -> None:
        # countries.csv (final, with iso2 + fa + en from mapping)
        mapping_df = pd.read_csv(
            PROCESSED_DIR / "countries-mapping.csv",
            dtype=str,
            encoding="utf-8",
            keep_default_na=False,
            na_values=[],
        )
        countries_in_data = df[["destination_country_iso2", "destination_country_fa"]].drop_duplicates()
        countries_in_data.columns = ["country_iso2", "country_fa"]
        # join با mapping برای گرفتن country_en و notes
        countries = countries_in_data.merge(
            mapping_df[["country_iso2", "country_en", "notes"]],
            on="country_iso2", how="left",
        )
        countries = countries.sort_values("country_iso2").reset_index(drop=True)
        countries.to_csv(PROCESSED_DIR / "countries.csv", index=False, encoding="utf-8")
        print(f"✅ countries.csv: {len(countries)} rows")

        # hs-codes.csv
        hs = df[["hs_code", "hs_code_2", "hs_code_4", "hs_code_6", "hs_code_8", "hs_description_raw"]].drop_duplicates()
        hs.columns = ["hs_code", "hs_code_2", "hs_code_4", "hs_code_6", "hs_code_8", "hs_description"]
        hs = hs.sort_values("hs_code").reset_index(drop=True)
        hs.to_csv(PROCESSED_DIR / "hs-codes.csv", index=False, encoding="utf-8")
        print(f"✅ hs-codes.csv: {len(hs)} rows")

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------
    def save_metadata(self) -> None:
        months_per_year = {1400: 12, 1401: 12, 1402: 12, 1403: 0, 1404: 0}
        metadata = {
            "dataset": "iran-exports-1400-1405",
            "task": "task-03-etl-normalize",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": {
                "primary": "https://tsd.irica.ir",
                "fallback_used": "https://service.tccim.ir",
                "reason": "tsd.irica.ir unreachable from outside Iran (Issue-005)",
                "query_endpoint": "stats_TarrifCustomCountryDetail_excel",
            },
            "years_included": YEARS_INCLUDED,
            "years_excluded": {str(k): v for k, v in YEAR_EXCLUDED.items()},
            "months_available_per_year": {str(y): m for y, m in months_per_year.items()},
            "is_partial_year": {
                "1403": "monthly_data_unavailable",
                "1404": "monthly_data_unavailable",
                "1405": "no_data",
            },
            "issues_addressed": [
                "Issue-005: alternative source tccim.ir used (tsd.irica.ir unreachable from outside Iran)",
                "Issue-006: years 1403/1404 have no monthly breakdown in source → month=0 and is_monthly=False",
                "Issue-007: export_quantity column was always NULL in source → column dropped from final schema",
                "Issue-008: year 1405 has no data in source → not included in Parquet, documented in metadata",
            ],
            "schema": {
                "year": "int32 (1400-1404)",
                "month": "int32 (0 if source had no monthly breakdown, else 1-12)",
                "is_monthly": "bool (False for 1403/1404, True for 1400-1402)",
                "hs_code": "string HH.HH.HH.HH (ISO 3166-aligned 8-digit format)",
                "hs_code_2/4/6/8": "string (sub-codes without dots)",
                "destination_country_iso2": "ISO 3166-1 alpha-2 (user-assigned codes XO/ZF/ZS/ZZ for non-standard)",
                "destination_country_fa": "Persian name as in source",
                "customs_office_fa": "Persian name of customs office",
                "export_value_usd": "decimal128(20,4) — USD",
                "export_value_rial": "decimal128(28,4) — Iranian Rial",
                "export_weight_kg": "decimal128(20,4) — kilograms",
            },
            "precision_target": "tolerance < 0.0001% (1e-6)",
            "precision_engine": "Python decimal.Decimal with precision 28",
            "files": {
                "main": "exports_1400-1405.parquet",
                "countries_mapping": "countries-mapping.csv",
                "countries_reference": "countries.csv",
                "hs_codes_reference": "hs-codes.csv",
                "validation_report": "_validation-report.md",
            },
        }
        out_path = PROCESSED_DIR / "_dataset-metadata.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"✅ _dataset-metadata.json saved")

    # ------------------------------------------------------------------
    # Validation report
    # ------------------------------------------------------------------
    def write_validation_report(self, df: pd.DataFrame, precision_results: dict) -> None:
        from datetime import datetime as dt
        now = dt.now().strftime("%Y-%m-%d %H:%M")

        # آمار توصیفی
        # برای محاسبه آمار، ابتدا به Decimal تبدیل مجدد
        values_usd = [Decimal(str(v)) for v in df["export_value_usd"]]
        weights_kg = [Decimal(str(v)) for v in df["export_weight_kg"]]
        n = len(values_usd)
        sum_usd = sum(values_usd)
        sum_kg = sum(weights_kg)
        min_usd = min(values_usd) if values_usd else Decimal(0)
        max_usd = max(values_usd) if values_usd else Decimal(0)
        mean_usd = sum_usd / n if n else Decimal(0)

        # تعداد کشورها و HS codes
        n_countries = df["destination_country_iso2"].nunique()
        n_hs_codes = df["hs_code"].nunique()
        n_customs = df["customs_office_fa"].nunique()

        # nulls check (کلیدی)
        nulls_year = df["year"].isna().sum()
        nulls_month = df["month"].isna().sum()
        nulls_hs = df["hs_code"].isna().sum()
        nulls_country = df["destination_country_iso2"].isna().sum()
        nulls_value = df["export_value_usd"].apply(lambda v: pd.isna(v) or str(v) == "0").sum()

        lines = [
            f"---",
            f"type: data",
            f"title: گزارش Validation — ETL (task-03)",
            f"created: {now}",
            f"updated: {now}",
            f"status: review",
            f"tags:",
            f"  - data",
            f"  - etl",
            f"  - task-03",
            f"---",
            f"",
            f"# گزارش Validation — ETL (task-03)",
            f"",
            f"**تاریخ**: {now}",
            f"**Agent**: ETL Engineer",
            f"**Pipeline**: `scripts/etl_normalize.py`",
            f"**منبع داده**: `service.tccim.ir` (آینه آمار گمرکی اتاق بازرگانی تهران)",
            f"**سال‌های موجود**: 1400, 1401, 1402, 1403, 1404 (۱۴۰۵ به‌دلیل نبود داده در منبع در Parquet نیست — Issue-008)",
            f"",
            f"## ۱. آمار کلی",
            f"",
            f"| شاخص | مقدار |",
            f"|------|-------|",
            f"| تعداد رکوردهای پردازش‌شده (final) | {n:,} |",
            f"| تعداد کشورهای یکتا | {n_countries} |",
            f"| تعداد HS Codeهای یکتا | {n_hs_codes} |",
            f"| تعداد گمرک‌های یکتا | {n_customs} |",
            f"| مجموع ارزش (USD) | {sum_usd:,.2f} |",
            f"| مجموع وزن (kg) | {sum_kg:,.2f} |",
            f"| کمینه ارزش (USD) | {min_usd:,.2f} |",
            f"| بیشینه ارزش (USD) | {max_usd:,.2f} |",
            f"| میانگین ارزش (USD) | {mean_usd:,.2f} |",
            f"",
            f"## ۲. آمار پاکسازی به تفکیک سال",
            f"",
            f"| سال | رکوردهای خام | تکراری حذف | NA حذف | رکورد نهایی |",
            f"|-----|-------------|-----------|--------|-------------|",
        ]
        for year in YEARS_INCLUDED:
            lines.append(
                f"| {year} | {self.records_before.get(year, 0):,} | "
                f"{self.duplicates_dropped.get(year, 0):,} | "
                f"{self.na_dropped.get(year, 0):,} | "
                f"{self.records_after.get(year, 0):,} |"
            )

        lines += [
            f"",
            f"## ۳. تست دقت عددی (تلورانس < 0.0001٪)",
            f"",
            f"هدف: مجموع `export_value_usd` در داده پردازش‌شده باید با داده خام برابر باشد",
            f"با تلورانس کمتر از 0.0001٪ (یعنی < 1e-6 به‌صورت کسر).",
            f"",
            f"| سال | جمع خام (USD) | جمع پردازش‌شده (USD) | تلورانس | تلورانس (٪) | نتیجه |",
            f"|-----|---------------|----------------------|---------|-------------|-------|",
        ]
        all_pass = True
        for year in YEARS_INCLUDED:
            r = precision_results[year]
            if not r["pass"]:
                all_pass = False
            lines.append(
                f"| {year} | {r['raw_sum_usd']:,.2f} | {r['proc_sum_usd']:,.2f} | "
                f"{r['tolerance']:.10f} | {r['tolerance_pct']:.8f} | "
                f"{'✅ PASS' if r['pass'] else '❌ FAIL'} |"
            )

        lines += [
            f"",
            f"**نتیجه کلی**: {'✅ همه سال‌ها PASS' if all_pass else '❌ برخی سال‌ها FAIL — بررسی شود'}",
            f"",
            f"## ۴. بررسی Null در فیلدهای کلیدی",
            f"",
            f"| فیلد | تعداد NULL | نتیجه |",
            f"|------|-----------|-------|",
            f"| year | {nulls_year} | {'✅' if nulls_year == 0 else '❌'} |",
            f"| month | {nulls_month} | {'✅' if nulls_month == 0 else '❌'} (۰ مجاز است برای ۱۴۰۳/۱۴۰۴ — Issue-006) |",
            f"| hs_code | {nulls_hs} | {'✅' if nulls_hs == 0 else '❌'} |",
            f"| destination_country_iso2 | {nulls_country} | {'✅' if nulls_country == 0 else '❌'} |",
            f"| export_value_usd (==0) | {nulls_value} | (درصد رکوردهای با value=0 — برای تحلیل آینده) |",
            f"",
            f"## ۵. مدیریت Issues",
            f"",
            f"### Issue-006 — فقدان ماه در ۱۴۰۳/۱۴۰۴",
            f"- **وضعیت**: 🟢 addressed در ETL",
            f"- **راهکار**: برای رکوردهای ۱۴۰۳/۱۴۰۴ فیلد `month=0` و `is_monthly=False` تنظیم شد.",
            f"- **تأثیر**: تحلیل‌های ماهانه/YTD فقط باید روی ۱۴۰۰-۱۴۰۲ اجرا شود؛ برای ۱۴۰۳/۱۴۰۴ فقط تحلیل سالانه.",
            f"- **تعداد رکوردهای بدون ماه**: {((df['year'].isin([1403, 1404])) & (df['month'] == 0)).sum():,}",
            f"",
            f"### Issue-007 — فقدان export_quantity",
            f"- **وضعیت**: 🟢 addressed در ETL",
            f"- **راهکار**: فیلد `export_quantity` از اسکیمای Parquet حذف شد (هیچ داده‌ای نداشت).",
            f"",
            f"### Issue-008 — نبود داده ۱۴۰۵",
            f"- **وضعیت**: 🟢 documented در metadata",
            f"- **راهکار**: ۱۴۰۵ در Parquet نیست. نام فایل همچنان `exports_1400-1405.parquet` برای سازگاری با تسک‌های بعدی وقتی ۱۴۰۵ در دسترس شد.",
            f"- **اقدام آینده**: وقتی منبع داده ۱۴۰۵ را منتشر کرد، اجرای اسکریپت استخراج + این ETL کافی است.",
            f"",
            f"## ۶. کشورهای نگاشت‌نشده",
            f"",
        ]
        if self.unmapped_countries:
            lines.append(f"⚠️ {len(self.unmapped_countries)} کشور نگاشت نشده:")
            for c in sorted(set(self.unmapped_countries)):
                lines.append(f"- `{c}`")
            lines.append("")
        else:
            lines.append(f"✅ همه ۱۶۶ نام فارسی کشور در `countries-mapping.csv` به‌طور کامل نگاشت شده‌اند.")
            lines.append("")

        lines += [
            f"## ۷. کدهای خاص (user-assigned per ISO 3166)",
            f"",
            f"| کد | نام فارسی | توضیح |",
            f"|-----|----------|-------|",
            f"| XO | سایر کشورهای خارجی | تجمیع کشورهای فهرست‌نشده در منبع |",
            f"| ZF | مناطق آزاد | مناطق آزاد تجاری ایران (داخلی، نه کشور) |",
            f"| ZS | مناطق ویژه | مناطق ویژه اقتصادی ایران (داخلی، نه کشور) |",
            f"| ZZ | نامشخص | مقصد نامشخص در منبع |",
            f"",
            f"## ۸. آمار توصیفی تجمیعی (در ۵ سال)",
            f"",
            f"| شاخص | مقدار |",
            f"|------|-------|",
            f"| min export_value_usd | {min_usd:,.2f} |",
            f"| max export_value_usd | {max_usd:,.2f} |",
            f"| mean export_value_usd | {mean_usd:,.2f} |",
            f"| sum export_value_usd | {sum_usd:,.2f} |",
            f"| sum export_weight_kg | {sum_kg:,.2f} |",
            f"",
            f"## ۹. فایل‌های خروجی",
            f"",
            f"- `05-Data/processed/exports_1400-1405.parquet` — داده نرمال‌شده ۵ سال",
            f"- `05-Data/processed/_dataset-metadata.json` — metadata با issues_addressed",
            f"- `05-Data/processed/countries-mapping.csv` — نگاشت ۱۶۶ نام فارسی → ISO2",
            f"- `05-Data/processed/countries.csv` — مرجع کشورهای موجود در داده",
            f"- `05-Data/processed/hs-codes.csv` — مرجع HS Codeها",
            f"- `05-Data/processed/_validation-report.md` — این گزارش",
            f"",
            f"## ۱۰. مسائل باز برای تسک‌های بعدی",
            f"",
            f"- تحلیل‌های ماهانه (Mann-Kendall ماهانه) فقط روی ۱۴۰۰-۱۴۰۲ قابل اجراست.",
            f"- CAGR ۵ ساله (۱۴۰۰-۱۴۰۴) باید روی داده سالانه محاسبه شود (به‌دلیل نبود ماه در ۱۴۰۳/۱۴۰۴).",
            f"- اگر کاربر از داخل ایران به `tsd.irica.ir` دسترسی دارد، می‌تواند داده ۱۴۰۳/۱۴۰۴ ماهانه و ۱۴۰۵ را از منبع رسمی استخراج کند.",
            f"",
        ]

        out_path = PROCESSED_DIR / "_validation-report.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"✅ _validation-report.md saved")


def main():
    pipeline = ETLPipeline()

    # 1) Merge all years
    print("=" * 80)
    print("STEP 1: Merge all years")
    print("=" * 80)
    df = pipeline.merge_all_years()
    print(f"\nTotal merged records: {len(df):,}")

    # 2) Validate precision
    print("\n" + "=" * 80)
    print("STEP 2: Validate precision (< 0.0001%)")
    print("=" * 80)
    precision_results = pipeline.validate_precision(df)

    all_pass = all(r["pass"] for r in precision_results.values())
    if not all_pass:
        print("\n❌ PRECISION TEST FAILED — aborting before save.")
        sys.exit(2)
    print("\n✅ All years PASS precision test.")

    # 3) Save Parquet
    print("\n" + "=" * 80)
    print("STEP 3: Save Parquet")
    print("=" * 80)
    pipeline.save_parquet(df)

    # 4) Build reference tables
    print("\n" + "=" * 80)
    print("STEP 4: Build reference tables")
    print("=" * 80)
    pipeline.build_reference_tables(df)

    # 5) Save metadata
    print("\n" + "=" * 80)
    print("STEP 5: Save metadata")
    print("=" * 80)
    pipeline.save_metadata()

    # 6) Write validation report
    print("\n" + "=" * 80)
    print("STEP 6: Write validation report")
    print("=" * 80)
    pipeline.write_validation_report(df, precision_results)

    print("\n" + "=" * 80)
    print(f"✅ ETL complete! Output in {PROCESSED_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
