# Phase 1 — Scaffold & Data Pipeline

Plan agreed before build. Sits under the standing rules and overview in `Extension_Build_Plan.md`.

## Goal
A clean project skeleton plus a data pipeline that pulls the two price series, snapshots them to disk, and prints an honest data-quality summary. Deliverable is a reproducible, inspectable foundation — not analysis.
**Done when:** the pipeline runs *from the saved snapshot* (not a live re-pull) and reports rows / coverage / gaps.

## Decisions locked in
- **Environment:** plain `venv` + pinned `requirements.txt` (not conda).
- **Libraries (Phase 1):** pandas, numpy, yfinance. (statsmodels added in Phase 2.)
- **Adjusted close:** use adjusted (total-return) close explicitly and record which, so Phase 2 validation is apples-to-apples with the dissertation.
- **Snapshots committed to git** (~150–250 KB per series; negligible), so reproducibility is real.

## Structure
```
data/        # raw snapshots (CSV) + manifest
strategies/  # empty (Phase 2)
backtest/    # empty (Phase 2)
reports/     # empty (Phase 5)
config.py    # dates, tickers, cost params in one place
data_pipeline.py
requirements.txt
README.md
```

## Steps
1. Scaffold folders + `config.py` (sample window 2015-01-01 → 2025-08-31, tickers, 0.04% round-trip cost).
2. Pull `VUKE.L` (FTSE 100 proxy) and `GBPUSD=X` (spot) via yfinance, adjusted close.
3. Snapshot each raw pull to `data/` as timestamped CSV + a manifest (ticker, date pulled, rows, date range, source, adjusted-close flag). All downstream code reads the snapshot, never the live API.
4. Print an honest data-quality summary per series: rows, date coverage, missing business days, NaNs. Flag gaps — do **not** interpolate. Note row count vs. dissertation's ~2,693 days (small differences expected, reported not reconciled).

## Deliberately out of scope for Phase 1
- FF5 factors / CAPM benchmark (Phase 2/3).
- Any strategy or backtest code.
- Any cleaning/adjustment beyond what's declared in the manifest.

## Gate
Stop after Phase 1 for review before touching Phase 2.
