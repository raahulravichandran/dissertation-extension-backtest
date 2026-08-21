"""Phase 4 — minimal live signal for the FTSE 100 Contrarian Bollinger strategy.

SIMULATED / PAPER SIGNAL — NO REAL MONEY, NO BROKER, NOT INVESTMENT ADVICE.

One command: pull the latest VUKE.L prices, compute the Bollinger signal, print
today's recommended position, and append one row to logs/signal_log.csv. This is a
signal calculator only — there is no broker connection, no order, and no capital
anywhere in this project. It is a capability demonstration: Phase 3 found the
Bollinger edge did NOT persist out-of-sample, so this is not a recommendation to trade.

Usage: python live_signal.py
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf

import config
from strategies.signals import contrarian_bollinger

BANNER = ("SIMULATED / PAPER SIGNAL — NO REAL MONEY, NO BROKER, NOT INVESTMENT ADVICE. "
          "Capability demo only; Phase 3 found this edge did not persist out-of-sample.")
LOG_PATH = config.PROJECT_ROOT / "logs" / "signal_log.csv"
POSITION = {1: "LONG", 0: "CASH", -1: "SHORT"}


def pull_latest() -> pd.Series:
    """Fresh pull of VUKE.L adjusted close, 2015 -> today (a live signal needs current data)."""
    end = (date.today() + timedelta(days=1)).isoformat()
    df = yf.download(config.TICKERS["FTSE100"], start=config.START_DATE, end=end,
                     auto_adjust=False, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index)
    return df[config.PRICE_FIELD].dropna()


def compute_signal(prices: pd.Series, window: int = 20, k: float = 2.0) -> dict:
    """Latest Bollinger state plus band context and a simple current vol regime."""
    sig = contrarian_bollinger(prices, window=window, k=k)
    sma = prices.rolling(window).mean()
    std = prices.rolling(window).std()

    # Informational only: current 20-day annualised realised vol vs its trailing median.
    rvol = prices.pct_change().rolling(window).std() * np.sqrt(252)
    vol_regime = "HIGH" if rvol.iloc[-1] > rvol.median() else "LOW"

    return {
        "data_as_of": prices.index[-1].date().isoformat(),
        "last_price": round(float(prices.iloc[-1]), 4),
        "sma": round(float(sma.iloc[-1]), 4),
        "upper": round(float(sma.iloc[-1] + k * std.iloc[-1]), 4),
        "lower": round(float(sma.iloc[-1] - k * std.iloc[-1]), 4),
        "signal": int(sig.iloc[-1]),
        "position": POSITION[int(sig.iloc[-1])],
        "vol_regime": vol_regime,
    }


def print_block(s: dict) -> None:
    line = "=" * 72
    print(line)
    print("  " + BANNER)
    print(line)
    print(f"  Strategy:        FTSE 100 Contrarian Bollinger (20-day, 2σ) via VUKE.L")
    print(f"  Data as of:      {s['data_as_of']} (close)")
    print(f"  Last price:      {s['last_price']}")
    print(f"  Bands:           lower {s['lower']}  |  SMA {s['sma']}  |  upper {s['upper']}")
    print(f"  Signal:          {s['signal']:+d}  ->  POSITION: {s['position']}")
    print(f"  Vol regime:      {s['vol_regime']} (informational; no gating)")
    print(f"  Execution:       signal as of close {s['data_as_of']} -> hold from next trading day")
    print(line)


def append_log(s: dict) -> None:
    LOG_PATH.parent.mkdir(exist_ok=True)
    row = {"run_timestamp": datetime.now().isoformat(timespec="seconds"), **s}
    cols = ["run_timestamp", "data_as_of", "last_price", "sma", "upper", "lower",
            "signal", "position", "vol_regime"]
    new_file = not LOG_PATH.exists()
    with open(LOG_PATH, "a", encoding="utf-8", newline="") as f:
        if new_file:
            f.write(f"# {BANNER}\n")
            f.write(",".join(cols) + "\n")
        f.write(",".join(str(row[c]) for c in cols) + "\n")
    print(f"  Logged to {LOG_PATH.relative_to(config.PROJECT_ROOT)}")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    prices = pull_latest()
    s = compute_signal(prices)
    print_block(s)
    append_log(s)


if __name__ == "__main__":
    main()
