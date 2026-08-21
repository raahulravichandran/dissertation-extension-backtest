"""Phase 1 data pipeline: pull, snapshot, and audit the two price series.

Design principle (see CLAUDE.md): every downstream result must be reproducible
from a fixed file, not a live re-pull. So this module downloads once, writes a
timestamped CSV snapshot plus a manifest, and thereafter reads from the
snapshot. Gaps are reported honestly, never interpolated.

Usage:
    python data_pipeline.py            # download if no snapshot exists, then audit
    python data_pipeline.py --refresh  # force a fresh download + new snapshot
"""

from __future__ import annotations

import argparse
from datetime import datetime

import pandas as pd
import yfinance as yf

import config


def _safe_ticker(ticker: str) -> str:
    """Make a ticker safe for use in a filename (e.g. 'GBPUSD=X' -> 'GBPUSD-X')."""
    return ticker.replace("=", "-").replace("/", "-")


def download_series(ticker: str) -> pd.DataFrame:
    """Download one series from Yahoo Finance over the configured window.

    auto_adjust=False keeps both raw 'Close' and 'Adj Close' so the price field
    used downstream is explicit and recorded, rather than silently baked in.
    """
    df = yf.download(
        ticker,
        start=config.START_DATE,
        end=config.END_DATE,
        auto_adjust=False,
        progress=False,
    )
    if df is None or df.empty:
        raise RuntimeError(f"No data returned for {ticker}")

    # Recent yfinance can return MultiIndex columns even for a single ticker.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.index = pd.to_datetime(df.index)
    df.index.name = "Date"
    return df


def snapshot_path(name: str, ticker: str, date_pulled: str) -> "config.Path":
    return config.DATA_DIR / f"{name}_{_safe_ticker(ticker)}_{date_pulled}.csv"


def latest_snapshot(name: str):
    """Return the most recent snapshot CSV for a series name, or None."""
    matches = sorted(config.DATA_DIR.glob(f"{name}_*.csv"))
    return matches[-1] if matches else None


def save_snapshot(df: pd.DataFrame, name: str, ticker: str) -> "config.Path":
    """Write a timestamped CSV snapshot and append a row to the manifest."""
    config.DATA_DIR.mkdir(exist_ok=True)
    date_pulled = datetime.now().strftime("%Y%m%d")
    path = snapshot_path(name, ticker, date_pulled)
    df.to_csv(path)

    manifest_row = {
        "name": name,
        "ticker": ticker,
        "file": path.name,
        "date_pulled": date_pulled,
        "rows": len(df),
        "start_date": df.index.min().date().isoformat(),
        "end_date": df.index.max().date().isoformat(),
        "price_field": config.PRICE_FIELD,
        "source": "Yahoo Finance (yfinance, auto_adjust=False)",
    }
    manifest = pd.DataFrame([manifest_row])
    if config.MANIFEST_PATH.exists():
        existing = pd.read_csv(config.MANIFEST_PATH)
        manifest = pd.concat([existing, manifest], ignore_index=True)
    manifest.to_csv(config.MANIFEST_PATH, index=False)
    return path


def load_snapshot(path) -> pd.DataFrame:
    df = pd.read_csv(path, index_col="Date", parse_dates=True)
    return df


def data_quality_summary(df: pd.DataFrame, name: str, ticker: str) -> None:
    """Print an honest audit of one series. Flags gaps; does not fix them."""
    price = df[config.PRICE_FIELD]
    expected_bdays = pd.bdate_range(df.index.min(), df.index.max())
    missing_bdays = expected_bdays.difference(df.index)

    print(f"\n{name} ({ticker})")
    print("-" * 60)
    print(f"  Rows (trading days):     {len(df)}")
    print(f"  Coverage:                {df.index.min().date()} -> {df.index.max().date()}")
    print(f"  Price field:             {config.PRICE_FIELD}")
    print(f"  Business days in span:   {len(expected_bdays)}")
    print(f"  Missing business days:   {len(missing_bdays)}  (holidays/non-trading; NOT interpolated)")
    print(f"  NaNs in price field:     {int(price.isna().sum())}")
    diff = len(df) - config.DISSERTATION_TRADING_DAYS
    print(f"  vs dissertation ~{config.DISSERTATION_TRADING_DAYS} days: {diff:+d}  (small differences expected, reported not reconciled)")


def get_series(name: str, ticker: str, refresh: bool = False) -> pd.DataFrame:
    """Return a series, downloading + snapshotting only if needed."""
    existing = None if refresh else latest_snapshot(name)
    if existing is not None:
        print(f"Loading {name} from snapshot: {existing.name}")
        return load_snapshot(existing)

    print(f"Downloading {name} ({ticker})...")
    df = download_series(ticker)
    path = save_snapshot(df, name, ticker)
    print(f"  Snapshot saved: {path.name}")
    # Read back from disk so the audited data is exactly what was persisted.
    return load_snapshot(path)


def main(refresh: bool = False) -> None:
    print("=" * 60)
    print("PHASE 1 DATA PIPELINE")
    print("=" * 60)

    for name, ticker in config.TICKERS.items():
        df = get_series(name, ticker, refresh=refresh)
        data_quality_summary(df, name, ticker)

    print("\nDone. All summaries computed from on-disk snapshots.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 1 data pipeline")
    parser.add_argument("--refresh", action="store_true", help="Force a fresh download + new snapshot")
    args = parser.parse_args()
    main(refresh=args.refresh)
