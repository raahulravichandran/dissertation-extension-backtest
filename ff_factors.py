"""Pull and snapshot the Fama-French European 5-factor daily series.

Same reproducibility rule as the price data: download once, snapshot to data/,
then read from disk. Returns factors in decimals (not percent). If the download
fails, the caller degrades gracefully and reports FF5 as unavailable.
"""

from __future__ import annotations

import io
import zipfile
from datetime import datetime

import pandas as pd
import requests

import config

FF_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Europe_5_Factors_Daily_CSV.zip"


def _parse_ff_csv(text: str) -> pd.DataFrame:
    """Parse Ken French's daily CSV (skip header preamble, stop at any footer)."""
    rows = []
    for line in text.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) == 7 and parts[0].isdigit() and len(parts[0]) == 8:
            d = pd.Timestamp(parts[0][:4] + "-" + parts[0][4:6] + "-" + parts[0][6:8])
            vals = [float(x) / 100 for x in parts[1:]]  # percent -> decimal
            rows.append([d] + vals)
    df = pd.DataFrame(rows, columns=["Date", "Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF"])
    return df.set_index("Date").replace(-99.99 / 100, pd.NA)


def _latest_snapshot():
    matches = sorted(config.DATA_DIR.glob("FF5_Europe_*.csv"))
    return matches[-1] if matches else None


def get_ff5(refresh: bool = False) -> pd.DataFrame | None:
    """Return FF5 factors over the sample window, downloading/snapshotting if needed."""
    existing = None if refresh else _latest_snapshot()
    if existing is not None:
        print(f"Loading FF5 factors from snapshot: {existing.name}")
        return pd.read_csv(existing, index_col="Date", parse_dates=True)

    print("Downloading FF5 Europe factors from Ken French library...")
    try:
        resp = requests.get(FF_URL, timeout=30)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            name = next(n for n in z.namelist() if "Europe_5_Factors_Daily" in n)
            text = z.read(name).decode("utf-8", "ignore")
        ff = _parse_ff_csv(text)
    except Exception as e:  # noqa: BLE001
        print(f"  WARNING: FF5 download failed ({e}). FF5 alpha will be reported as unavailable.")
        return None

    ff = ff[(ff.index >= config.START_DATE) & (ff.index <= config.END_DATE)]
    date_pulled = datetime.now().strftime("%Y%m%d")
    path = config.DATA_DIR / f"FF5_Europe_{date_pulled}.csv"
    ff.to_csv(path)
    print(f"  Snapshot saved: {path.name} ({len(ff)} rows, {ff.index.min().date()} -> {ff.index.max().date()})")
    return ff
