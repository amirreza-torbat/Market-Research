#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task-01 — Customs Export Scraper (Market-Research Vault)
=========================================================
منبع داده (Discovery نتیجه):
  سایت رسمی گمرک (tsd.irica.ir / irica.gov.ir) از خارج ایران قابل دسترسی نیست
  (DNS authoritative در دسترس جهانی پاسخ نمی‌دهد — سه resolver مستقل تأیید کردند).
  منبع جایگزین قابل دسترس: آینه آمار گمرکی اتاق بازرگانی تهران
  https://service.tccim.ir/stats  (داده گمرک: کشور × گمرک × تعرفه × ماه)

Endpoint کشف‌شده برای داده جزئی (سقف ۵۰ رکورد در view نمایش را دور می‌زند):
  stats_TarrifCustomCountryDetail_excel?mode=doit&slcImpExp=Export
      &slcCustom=&slcCountry=&sYear={year}&txtSearchWord={chapter}
  → خروجی: جدول HTML ۱۰ ستونه:
      ردیف | ماه | سال | نام گمرک | نام کشور | شماره تعرفه | توضیحات تعرفه |
      وزن (کیلوگرم) | ارزش (ریال) | ارزش (دلار)

  جستجو substring است؛ کوئری فصل ۲ رقمی (01..99) هر کدی که آن رشته را در خود
  دارد را برمی‌گرداند → پوشش کامل با dedupe کلید رکورد.

Endpoint تجمیعی:
  stats?mode=doit&sYear={year}&slcImpExp=Export&slcCountry=&slcCustom=
  → (سال، گمرک، کشور، ارزش دلاری) + جمع کل ارزش/وزن سال.

مصرف:
  python scripts/scrape_customs.py detail  --years 1400,1401,1402,1403,1404
  python scripts/scrape_customs.py aggregate --years 1400,1401,1402,1403,1404,1405
  python scripts/scrape_customs.py summary
"""
import argparse
import asyncio
import html as html_mod
import json
import re
import sys
import time
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import httpx

# ---------------------------------------------------------------- constants
BASE = "https://service.tccim.ir"
DETAIL_URL = f"{BASE}/stats_TarrifCustomCountryDetail_excel"
AGG_URL = f"{BASE}/stats"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
DELAY_S = 2.0          # تأخیر اخلاقی بین درخواست‌ها (قانون تسک)
RETRIES = 4            # retry با backoff نمایی 2,4,8,16
RATE_LIMIT_SLEEP = 60  # در صورت rate-limit
CHAPTERS = [f"{i:02d}" for i in range(1, 100)]  # 01..99 (77 خالی است ولی بی‌ضرر)
NO_DATA_MARK = "اطلاعاتی موجود نمی باشد"

REPO = Path(__file__).resolve().parent.parent
RAW_DIR = REPO / "05-Data" / "raw"
INTERIM_DIR = REPO / "05-Data" / "interim"
STATE_DIR = REPO / "04-State"
CHECKPOINT_DIR = REPO / "scripts" / ".checkpoints"

FIELDNAMES = [
    "year", "month", "hs_code_raw", "hs_description_raw",
    "destination_country_fa", "customs_office_fa",
    "export_weight_kg", "export_value_rial", "export_value_usd",
    "export_quantity", "source_url", "source_query", "scraped_at",
]

PERSIAN = "۰۱۲۳۴۵۶۷۸۹"
ARABIC = "٠١٢٣٤٥٦٧٨٩"


def normalize_digits(text: str) -> str:
    """تبدیل ارقام فارسی/عربی به لاتین (قانون قراردادهای پروژه)."""
    for i, ch in enumerate(PERSIAN + ARABIC):
        text = text.replace(ch, str(i % 10))
    return text


def to_decimal(text: str) -> Decimal:
    """تبدیل رشته عددی (با کاما) به Decimal — بدون float (Decision-003)."""
    text = normalize_digits(str(text))
    text = re.sub(r"[^\d.\-]", "", text)
    if not text or text in {"-", ".", "-."}:
        return Decimal(0)
    try:
        return Decimal(text)
    except InvalidOperation:
        return Decimal(0)


def log_progress(line: str, milestone: bool = True) -> None:
    """append-only لاگ در 04-State/progress.md — فقط برای مایل‌ستون‌ها."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if milestone:
        with open(STATE_DIR / "progress.md", "a", encoding="utf-8") as f:
            f.write(f"\n## [{stamp}] task-01 — scraper\n- {line}\n")
    print(f"[{stamp}] {line}", flush=True)


def log_issue(title: str, body: str) -> None:
    """ثبت issue در کنسول + فایل لاگ محلی (ادغام دستی در issues.md بعداً)."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"!! ISSUE [{stamp}] {title}: {body}", flush=True)
    with open(REPO / "scripts" / "scraper_issues.log", "a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {title} — {body}\n")


# ---------------------------------------------------------------- parser
TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
TR_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)


def cell_text(raw: str) -> str:
    txt = re.sub(r"<[^>]+>", "", raw)
    txt = html_mod.unescape(txt)
    return normalize_digits(txt).strip()


def parse_detail_html(html_text: str, year: int, source_url: str,
                      source_query: str, scraped_at: str):
    """پارس جدول ۱۰ ستونه خروجی Excel-endpoint.

    ستون‌ها: ردیف | ماه | سال | نام گمرک | نام کشور | شماره تعرفه |
             توضیحات تعرفه | وزن kg | ارزش ریال | ارزش دلار
    برمی‌گرداند: (records, chapter_totals)
    """
    records, totals = [], []
    for row in TR_RE.findall(html_text):
        cells = [cell_text(c) for c in TD_RE.findall(row)]
        if not cells:
            continue
        joined = " ".join(cells)
        if "مجموع" in joined:
            nums = re.findall(r"([\d,]+)", joined)
            if len(nums) >= 2:
                totals.append((to_decimal(nums[0]), to_decimal(nums[1])))
            continue
        if len(cells) != 10 or not cells[0].isdigit():
            continue
        _, month, rec_year, customs, country, code, desc, weight, rial, usd = cells
        records.append({
            "year": year,
            "month": month if month else "",
            "hs_code_raw": code,
            "hs_description_raw": desc,
            "destination_country_fa": country,
            "customs_office_fa": customs,
            "export_weight_kg": to_decimal(weight),
            "export_value_rial": to_decimal(rial),
            "export_value_usd": to_decimal(usd),
            "export_quantity": "",
            "source_url": source_url,
            "source_query": source_query,
            "scraped_at": scraped_at,
        })
    return records, totals


AGG_ROW_RE = re.compile(
    r'<div class="row list-show[^"]*"[^>]*>(.*?)</div>\s*(?:</div>|<div class="col-md-1)', re.S)
AGG_CELL_RE = re.compile(r'<div class="col-md-\d+\s*text-right cell"\s*>(.*?)</div>', re.S)


def parse_agg_html(html_text: str, year: int, source_url: str, scraped_at: str):
    """پارس view تجمیعی (div-based): ردیف | سال | گمرک | کشور | ارزش دلار."""
    records = []
    agg_totals = {}
    m = re.search(r"مجموع ارزش دلاری:\s*([\d,]+)", html_text)
    if m:
        agg_totals["usd"] = to_decimal(m.group(1))
    m = re.search(r"مجموع وزن:\s*([\d,]+)", html_text)
    if m:
        agg_totals["weight"] = to_decimal(m.group(1))
    for row_html in re.findall(
            r'<div class="row list-show(?!" list-show-header)[^"]*"[^>]*>(.*?)(?=<div class="row list-show|$)',
            html_text, flags=re.S):
        cells = [cell_text(c) for c in AGG_CELL_RE.findall(row_html)]
        # ساختار: ردیف، سال، گمرک، کشور، ارزش
        if len(cells) >= 5 and cells[0].isdigit():
            _, rec_year, customs, country, usd = cells[:5]
            if rec_year and not rec_year.isdigit():
                continue
            records.append({
                "year": year,
                "customs_office_fa": customs,
                "destination_country_fa": country,
                "export_value_usd": to_decimal(usd),
                "source_url": source_url,
                "scraped_at": scraped_at,
            })
    return records, agg_totals


# ---------------------------------------------------------------- scraper
class CustomsScraper:
    """استخراج‌کننده آمار صادرات از آینه گمرکی tccim (async، با retry)."""

    def __init__(self, year: int, base_url: str = BASE):
        self.year = year
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(90.0, connect=20.0),
            headers={"User-Agent": UA,
                     "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
                     "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"},
            follow_redirects=True,
        )
        self.raw_dir = RAW_DIR / str(year)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path = CHECKPOINT_DIR / f"{year}.json"

    # ---------- checkpoint helpers
    def load_checkpoint(self) -> dict:
        if self.checkpoint_path.exists():
            return json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
        return {"completed": {}, "records_total": 0, "duplicates": 0}

    def save_checkpoint(self, cp: dict) -> None:
        self.checkpoint_path.write_text(
            json.dumps(cp, ensure_ascii=False, indent=1), encoding="utf-8")

    def rebuild_records_from_raw(self) -> tuple[dict, int]:
        """بازپارس فایل‌های خام موجود (idempotent resume) — raw = source of truth."""
        all_records: dict[tuple, dict] = {}
        dup = 0
        for path in sorted(self.raw_dir.glob(f"export_{self.year}_table-*.html")):
            body = path.read_text(encoding="utf-8")
            if NO_DATA_MARK in body or "ردیف" not in body:
                continue
            ch = path.stem.split("table-")[-1]
            url = (f"{DETAIL_URL}?mode=doit&slcImpExp=Export&slcCustom=&slcCountry="
                   f"&sYear={self.year}&txtSearchWord={ch}")
            records, _ = parse_detail_html(body, self.year, url, ch, "resume-reparse")
            for rec in records:
                key = self.record_key(rec)
                if key in all_records:
                    dup += 1
                else:
                    all_records[key] = rec
        return all_records, dup

    @staticmethod
    def record_key(rec: dict) -> tuple:
        return (rec["year"], rec["month"], rec["hs_code_raw"],
                rec["customs_office_fa"], rec["destination_country_fa"],
                str(rec["export_weight_kg"]), str(rec["export_value_rial"]),
                str(rec["export_value_usd"]))

    # ---------- fetch با retry/backoff (قانون resilience)
    async def fetch(self, url: str, params: dict, save_path: Path) -> str | None:
        for attempt in range(RETRIES):
            try:
                await asyncio.sleep(DELAY_S)
                resp = await self.client.get(url, params=params)
                if resp.status_code in (429, 503):
                    log_issue("rate-limit",
                              f"HTTP {resp.status_code} on {url} — sleep {RATE_LIMIT_SLEEP}s")
                    await asyncio.sleep(RATE_LIMIT_SLEEP)
                    continue
                resp.raise_for_status()
                body = resp.text
                if NO_DATA_MARK in body:
                    save_path.write_text(body, encoding="utf-8")
                    return None
                if len(body) < 500 or "ردیف" not in body:
                    raise ValueError(f"suspicious response ({len(body)} bytes)")
                # ذخیره دقیق پاسخ خام (اصل immutability)
                save_path.write_text(body, encoding="utf-8")
                return body
            except Exception as exc:  # noqa: BLE001
                wait = 2 ** (attempt + 1)
                log_issue("fetch-retry",
                          f"{save_path.name} attempt {attempt + 1}/{RETRIES} failed: {exc} → {wait}s")
                await asyncio.sleep(wait)
        return "FAILED"

    # ---------- حلقه استخراج جزئی یک سال
    async def scrape_year_detail(self, time_budget: float = 0.0, t_start: float = None) -> dict:
        cp = self.load_checkpoint()
        completed = cp["completed"]
        all_records, dup_count = self.rebuild_records_from_raw()
        log_progress(f"شروع/ادامه استخراج سال {self.year} (resume: {len(all_records)} رکورد از "
                     f"فایل‌های خام بازپارس شد | dup={dup_count}).", milestone=False)

        for idx, ch in enumerate(CHAPTERS, start=1):
            if completed.get(ch) == "ok" or completed.get(ch) == "empty":
                continue
            # time-budget: خروج تمیز برای اجرای chunked در sandbox
            if time_budget and t_start and (time.time() - t_start) > time_budget:
                log_progress(f"سال {self.year}: budget تمام شد — فصل‌های باقی‌مانده برای فراخوانی بعدی.")
                csv_path = self.write_csv(all_records, partial=True)
                return {"records": len(all_records), "duplicates": dup_count,
                        "interrupted": True, "csv": str(csv_path)}
            fname = f"export_{self.year}_table-{ch}.html"
            save_path = self.raw_dir / fname
            url = (f"{DETAIL_URL}?mode=doit&slcImpExp=Export&slcCustom=&slcCountry="
                   f"&sYear={self.year}&txtSearchWord={ch}")
            t0 = time.time()
            body = await self.fetch(DETAIL_URL, {
                "mode": "doit", "slcImpExp": "Export", "slcCustom": "",
                "slcCountry": "", "sYear": self.year, "txtSearchWord": ch,
            }, save_path)
            dt = time.time() - t0

            if body == "FAILED":
                completed[ch] = "failed"
                log_issue("chapter-failed",
                          f"سال {self.year} فصل {ch} پس از {RETRIES} تلاش شکست خورد — در issues ثبت شود")
                self._flush(cp, completed, all_records, dup_count)
                continue
            if body is None:
                completed[ch] = "empty"
                log_progress(f"سال {self.year} فصل {ch}: بدون داده ({dt:.0f}s)", milestone=False)
                self._flush(cp, completed, all_records, dup_count)
                continue

            scraped_at = datetime.now().isoformat(timespec="seconds")
            records, totals = parse_detail_html(body, self.year, url, ch, scraped_at)
            new = 0
            for rec in records:
                key = self.record_key(rec)
                if key in all_records:
                    dup_count += 1
                else:
                    all_records[key] = rec
                    new += 1
            completed[ch] = "ok"
            log_progress(f"سال {self.year} فصل {ch}: {len(records)} رکورد fetch | "
                         f"{new} جدید | مجموع {len(all_records)} | dup={dup_count} | {dt:.0f}s",
                         milestone=False)
            self._flush(cp, completed, all_records, dup_count)

        csv_path = self.write_csv(all_records)
        months = sorted({r["month"] for r in all_records.values() if r["month"]})
        log_progress(f"سال {self.year} کامل شد: {len(all_records)} رکورد یکتا | "
                     f"dup={dup_count} | ماه‌ها={months or 'بدون صفت ماه (1403/1404)'} | CSV={csv_path.name}",
                     milestone=True)
        return {"records": len(all_records), "duplicates": dup_count,
                "months": months, "csv": str(csv_path)}

    def _flush(self, cp, completed, all_records, dup_count):
        cp["completed"] = completed
        cp["records_total"] = len(all_records)
        cp["duplicates"] = dup_count
        self.save_checkpoint(cp)

    def write_csv(self, all_records: dict, partial: bool = False) -> Path:
        import csv
        INTERIM_DIR.mkdir(parents=True, exist_ok=True)
        suffix = "_partial" if partial else ""
        csv_path = INTERIM_DIR / f"exports_{self.year}_raw{suffix}.csv"
        rows = list(all_records.values())
        rows.sort(key=lambda r: (r["month"], r["hs_code_raw"],
                                 r["destination_country_fa"], r["customs_office_fa"]))
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDNAMES)
            w.writeheader()
            w.writerows(rows)
        return csv_path

    # ---------- استخراج تجمیعی یک سال
    async def scrape_year_aggregate(self) -> dict:
        save_path = self.raw_dir / f"export_{self.year}_aggregate.html"
        url = (f"{AGG_URL}?mode=doit&slcImpExp=Export&slcCountry=&slcCustom=&sYear={self.year}")
        body = await self.fetch(AGG_URL, {
            "mode": "doit", "slcImpExp": "Export", "slcCountry": "",
            "slcCustom": "", "sYear": self.year,
        }, save_path)
        if body == "FAILED":
            log_issue("aggregate-failed", f"سال {self.year} تجمیعی شکست خورد")
            return {"ok": False}
        if body is None:
            log_progress(f"سال {self.year} (aggregate): بدون داده در منبع")
            return {"ok": True, "empty": True, "records": 0, "months": []}
        scraped_at = datetime.now().isoformat(timespec="seconds")
        records, totals = parse_agg_html(body, self.year, url, scraped_at)
        import csv
        INTERIM_DIR.mkdir(parents=True, exist_ok=True)
        csv_path = INTERIM_DIR / f"exports_{self.year}_aggregate.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["year", "customs_office_fa", "destination_country_fa",
                        "export_value_usd", "source_url", "scraped_at"])
            for r in records:
                w.writerow([r["year"], r["customs_office_fa"],
                            r["destination_country_fa"], r["export_value_usd"],
                            r["source_url"], r["scraped_at"]])
        log_progress(f"سال {self.year} (aggregate): {len(records)} سطر | totals={totals}")
        return {"ok": True, "records": len(records), "totals": totals,
                "csv": str(csv_path), "empty": False}

    async def close(self):
        await self.client.aclose()


# ---------------------------------------------------------------- driver
async def run_detail(years: list[int], time_budget: float = 0.0) -> None:
    t_start = time.time()
    log_progress("شروع task-01 — استخراج جزئیات (chapters 01..99) از آینه tccim")
    for y in years:
        s = CustomsScraper(y)
        res = await s.scrape_year_detail(time_budget=time_budget, t_start=t_start)
        await s.close()
        if res.get("interrupted"):
            log_progress("اجرای chunked: ادامه در فراخوانی بعدی (checkpoint ذخیره شد).")
            return
    log_progress("پایان فاز جزئیات task-01 — همه سال‌ها کامل شد.")


async def run_aggregate(years: list[int]) -> None:
    for y in years:
        s = CustomsScraper(y)
        await s.scrape_year_aggregate()
        await s.close()


def run_summary() -> None:
    """تولید 05-Data/raw/_summary.md از روی CSVهای interim."""
    import csv as csv_mod
    lines = [
        "# خلاصه استخراج داده خام (task-01)",
        "",
        f"**تاریخ تولید**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "**Scraper**: task-01 — `scripts/scrape_customs.py`",
        "**منبع**: آینه آمار گمرکی اتاق بازرگانی تهران `service.tccim.ir`",
        "  (سایت رسمی `tsd.irica.ir` از خارج ایران قابل دسترسی نیست — Issue-005)",
        "**بازه**: ۱۴۰۰ تا ۱۴۰۵",
        "",
        "## آمار به تفکیک سال",
        "",
        "| سال | رکوردها | کشورها | HS Codeها | مجموع ارزش (USD) | مجموع وزن (kg) | months_available |",
        "|-----|---------|--------|-----------|-------------------|-----------------|------------------|",
    ]
    grand = {}
    for y in range(1400, 1406):
        csv_path = INTERIM_DIR / f"exports_{y}_raw.csv"
        if not csv_path.exists():
            lines.append(f"| {y} | ۰ | ۰ | ۰ | ۰ | ۰ | 0 (بدون داده در منبع) |")
            continue
        n = 0
        countries, codes, months = set(), set(), set()
        usd = Decimal(0)
        wgt = Decimal(0)
        with open(csv_path, encoding="utf-8") as f:
            for row in csv_mod.DictReader(f):
                n += 1
                countries.add(row["destination_country_fa"])
                codes.add(row["hs_code_raw"])
                if row["month"]:
                    months.add(row["month"])
                usd += to_decimal(row["export_value_usd"])
                wgt += to_decimal(row["export_weight_kg"])
        ma = len(months) if months else 0
        note = "" if ma else " (بدون صفت ماه در منبع)"
        lines.append(f"| {y} | {n} | {len(countries)} | {len(codes)} | "
                     f"{usd:,.0f} | {wgt:,.0f} | {ma}{note} |")
        grand[y] = (n, usd)
    lines += [
        "",
        "## months_available_1405",
        "",
        "`months_available_1405 = 0`",
        "",
        "منبع جایگزین (tccim) برای سال ۱۴۰۵ **هیچ داده‌ای** ندارد (نه جزئی، نه تجمیعی —",
        "پاسخ سامانه: «اطلاعاتی موجود نمی باشد»). داده ۱۴۰۵ پس از انتشار در منبع،",
        "با همان اسکریپت (`python scripts/scrape_customs.py detail --years 1405`) قابل افزودن است.",
        "",
        "## نکات کیفی داده",
        "",
        "- سال‌های ۱۴۰۰ تا ۱۴۰۲: تفکیک ماهانه کامل (۱۲ ماه).",
        "- سال‌های ۱۴۰۳ و ۱۴۰۴: رکورد جزئی موجود است اما منبع ستون ماه را خالی می‌گذارد",
        "  (تجمیع در سطح سال) — Issue-006.",
        "- جستجوی فصل در منبع substring است؛ رکوردهای تکراری بین کوئری‌های فصل با",
        "  dedupe کلید کامل حذف شدند (شمار duplicates در progress.md).",
        "- `export_quantity` در این منبع ارائه نمی‌شود (ستون خالی).",
        "- رکوردها در سطح تجمیعی (کد تعرفه × ماه × گمرک × کشور) هستند، نه اظهارنامه‌های تکی.",
        "",
        "## فایل‌های تولیدشده",
        "",
        "- `05-Data/raw/YYYY/export_YYYY_table-NN.html` — پاسخ خام هر فصل (immutability)",
        "- `05-Data/raw/YYYY/export_YYYY_aggregate.html` — پاسخ خام view تجمیعی",
        "- `05-Data/interim/exports_YYYY_raw.csv` — رکوردهای جزئی پارس‌شده",
        "- `05-Data/interim/exports_YYYY_aggregate.csv` — سطرهای تجمیعی (گمرک × کشور)",
        "",
        "## مسائل باز",
        "",
        "- Issue-005: دسترسی‌ناپذیری رسمی `tsd.irica.ir` از خارج ایران (DNS block جهانی).",
        "- Issue-006: فقدان صفت ماه در داده جزئی ۱۴۰۳/۱۴۰۴ در منبع.",
        "- Issue-007: فقدان کامل داده ۱۴۰۵ در منبع (months_available_1405 = 0).",
    ]
    out = RAW_DIR / "_summary.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"summary written → {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description="task-01 customs scraper (tccim mirror)")
    ap.add_argument("mode", choices=["detail", "aggregate", "summary", "status"])
    ap.add_argument("--years", default="1400,1401,1402,1403,1404,1405",
                    help="comma separated Jalali years")
    ap.add_argument("--time-budget", type=float, default=0.0,
                    help="max seconds before graceful exit (chunked execution)")
    args = ap.parse_args()
    years = [int(y) for y in args.years.split(",") if y.strip()]
    if args.mode == "detail":
        asyncio.run(run_detail(years, time_budget=args.time_budget))
    elif args.mode == "aggregate":
        asyncio.run(run_aggregate(years))
    elif args.mode == "status":
        show_status(years)
    else:
        run_summary()


def show_status(years: list[int]) -> None:
    for y in years:
        cp_path = CHECKPOINT_DIR / f"{y}.json"
        done = empty = failed = 0
        if cp_path.exists():
            cp = json.loads(cp_path.read_text(encoding="utf-8"))
            vals = list(cp.get("completed", {}).values())
            done = vals.count("ok")
            empty = vals.count("empty")
            failed = vals.count("failed")
        raws = len(list((RAW_DIR / str(y)).glob("export_{}_table-*.html".format(y)))) \
            if (RAW_DIR / str(y)).exists() else 0
        csv_path = INTERIM_DIR / f"exports_{y}_raw.csv"
        nrows = 0
        if csv_path.exists():
            with open(csv_path, encoding="utf-8") as f:
                nrows = sum(1 for _ in f) - 1
        print(f"{y}: chapters ok={done} empty={empty} failed={failed} | raw_files={raws} | csv_rows={nrows}")


if __name__ == "__main__":
    main()
