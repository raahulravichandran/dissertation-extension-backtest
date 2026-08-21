# Phase 1 Report — Data Quality Audit

Persisted output of the Phase 1 data pipeline (`data_pipeline.py`), computed from
the committed CSV snapshots in `data/`. Reproducible: `python data_pipeline.py`.

## Snapshots
| Series | Ticker | File | Price field | Source |
|---|---|---|---|---|
| FTSE 100 | VUKE.L | `data/FTSE100_VUKE.L_20260730.csv` | Adjusted close | Yahoo Finance (yfinance, auto_adjust=False) |
| GBP/USD | GBPUSD=X | `data/GBPUSD_GBPUSD-X_20260730.csv` | Adjusted close | Yahoo Finance (yfinance, auto_adjust=False) |

## Data-quality summary
| Series | Rows | Coverage | Business days in span | Missing business days | NaNs | vs dissertation ~2,693 |
|---|---|---|---|---|---|---|
| FTSE 100 (VUKE.L) | 2,693 | 2015-01-02 → 2025-08-29 | 2,781 | 88 | 0 | +0 (exact) |
| GBP/USD (=X) | 2,776 | 2015-01-01 → 2025-08-29 | 2,782 | 6 | 0 | +83 |

## Notes — explained, not just reported
- **FTSE 100 lands on exactly 2,693 rows**, matching the dissertation's reported
  count — an early sign the trading calendars align.
- **GBP/USD has 83 more rows** because FX trades through most equity-market
  holidays (the LSE closes ~88 business days over the span; FX only ~6). This is
  expected, not an error — the dissertation's 2,693 figure is the FTSE calendar.
  Consequence for later phases: the two series do **not** share an identical index,
  so anything comparing them must align on dates.
- **Missing business days are holidays**, reported and left as gaps — never
  interpolated (interpolating would invent prices on days the market was shut).
- **No NaNs** in either price field.
- **Adjusted close** (total return, incl. dividends) is recorded explicitly in the
  manifest so the price basis is unambiguous and immune to yfinance's `auto_adjust`
  default changing.

## Defensible choices (for interview)
- **Snapshot-then-read:** the pipeline downloads once, writes a timestamped CSV +
  manifest, and all downstream code reads the snapshot — so every result is
  reproducible from a fixed file, not a live API call that can drift.
- Reproducibility over convenience: snapshots are committed to git despite being
  raw vendor data, because that is what makes the numbers defensible a year later.
