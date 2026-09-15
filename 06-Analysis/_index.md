---
type: index
title: ایندکس تحلیل‌ها
created: 2026-09-14
folder: 06-Analysis
---

# 📑 ایندکس تحلیل‌ها

> ایندکس درختی همه یادداشت‌های تحلیلی پروژه. اگر این اولین بازدید شماست، از «گزارش‌های اصلی» شروع کنید. برای وضعیت اجرایی پروژه، [[../04-State/STATUS]] را ببینید.

## گزارش‌های اصلی (task-08)

- [[executive-summary]] — خلاصه اجرایی: آمار کلی، یافته‌ها، توصیه‌ها
- [[methodology]] — روش‌شناسی: منبع داده، شاخص‌ها، آستانه‌ها، دقت
- [[key-findings]] — پنج یافته کلیدی با تحلیل عمیق

## تحلیل روند (task-10/11) — ۱۰۸ یادداشت + ۱۰۲ نمودار

- [[trend/_MOC]] — فهرست کامل یادداشت‌های روند
- [[trend/_classification-summary]] — خلاصه طبقه‌بندی ۵۰,۱۹۶ جفت
- `trend/strong-growth/` — ۳۰ یادداشت رشد قوی (نمونه: [[trend/strong-growth/hs-26-08-00-40]]، [[trend/strong-growth/hs-72-14-20-00]])
- `trend/moderate-growth/` — ۱۸ یادداشت رشد متوسط
- `trend/emerging/` — ۳۰ یادداشت نوظهور (نمونه: [[trend/emerging/hs-27-11-21-90]]، [[trend/emerging/hs-31-02-10-90]])
- `trend/declining/` — ۳۰ یادداشت کاهشی
- `trend/charts/` — ۱۰۲ نمودار PNG روند aggregated

## کاندیدهای صادرات (task-12) — هدف نهایی

- [[export-candidates/_MOC]] — فهرست کامل ۵۰ یادداشت تفصیلی
- [[export-candidates/_executive-ranking]] — گزارش اجرایی Top 50 (بازکالیبره‌شده: select ۵۸ / monitor ۱۷۲ / investigate ۳۴۴)
- [[export-candidates/by-target-country]] — گزارش کشور-محور (Top 30 کشور + Top 10 HS هر کشور)
- [[export-candidates/chapter-country-matrix]] — ماتریس فصل × کشور + heatmap
- یادداشت‌های برتر: [[export-candidates/rank-01-hs-27-11-21-90]] (گاز طبیعی) | [[export-candidates/rank-02-hs-72-14-99-00]] (میله فولادی) | [[export-candidates/rank-03-hs-26-01-11-90]] (سنگ آهن) | [[export-candidates/rank-04-hs-27-13-20-00]] (قیر) | [[export-candidates/rank-05-hs-27-11-12-90]] (پروپان)
- `export-candidates/charts/` — ۵۲ نمودار PNG (شامل top20-scores و chapter-country-heatmap)

## تحلیل به تفکیک کشور

- [[by-country/_MOC]] — MOC تحلیل کشور-محور (task-04 هنوز pending؛ تحلیل کشور-محور عملی در [[export-candidates/by-target-country]] انجام شده است)

## تحلیل به تفکیک تعرفه

- [[by-tariff/_MOC]] — MOC تحلیل تعرفه-محور (task-05 هنوز pending؛ تحلیل تعرفه-محور عملی در trend/ و [[export-candidates/_MOC]] انجام شده است)

## داده‌ها

- [[../05-Data/_MOC]] — MOC کل داده‌ها
- [[../05-Data/processed/_validation-report]] — گزارش validation ETL (task-03)
- [[../05-Data/processed/trend-analysis-summary]] — خلاصه تحلیل روند (task-10)
- `05-Data/processed/exports_1400-1405.parquet` — ۶۲۶,۳۹۵ رکورد نرمال
- `05-Data/processed/trend-analysis-5y.parquet` — ۵۰,۱۹۶ جفت × ۲۱ ستون
- `05-Data/processed/trend-classification.parquet` — طبقه‌بندی ۷+۳ دسته
- `05-Data/processed/export-candidates-ranked-recalibrated.parquet` — ۵۷۴ کاندید بازکالیبره

## خروجی‌های Excel

- `07-Exports/iran-exports-1400-1405-20260914.xlsx` — Excel نهایی ۱۸ شیت (task-07)
- `07-Exports/iran-export-candidates-500.xlsx` — Excel کامل ۵۷۴ کاندید (۷ شیت)
- [[../07-Exports/_MOC]] — فهرست خروجی‌ها

## گزارش‌های پروژه (State)

- [[../04-State/STATUS]] — وضعیت پروژه و تسک‌ها
- [[../04-State/progress]] — لاگ پیشرفت
- [[../04-State/qa-report]] — گزارش QA نهایی (۴۹/۴۹ PASS)
- [[../04-State/decisions]] — تصمیم‌های پروژه (Decision-001 تا 011)
- [[../04-State/issues]] — مسائل باز و مستند (Issues 001 تا 009)

## مستندات پایه

- [[../00-Overview/project-overview]] — معرفی و محدوده پروژه
- [[../00-Overview/conventions]] — قراردادها و تاکسونومی روند (بخش ۵)
- [[../00-Overview/glossary]] — واژه‌نامه
- [[../00-Overview/data-sources]] — منابع داده
- [[../01-Tasks/_MOC]] — فهرست و وابستگی تسک‌ها
- [[../03-Recipes/recipe-06-write-obsidian-notes]] — SOP نوشتن یادداشت
- [[../03-Recipes/recipe-09-trend-classification]] — SOP طبقه‌بندی و رتبه‌بندی

## مراجع

- [[../04-State/STATUS]]
- [[../01-Tasks/_MOC]]
- [[_MOC]] — MOC این پوشه
