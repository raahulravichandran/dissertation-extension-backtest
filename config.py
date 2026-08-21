"""Central configuration for the dissertation-extension system.

All dates, tickers and cost assumptions live here so there are no magic
numbers scattered across the codebase (and so an interviewer can see every
assumption in one place).
"""

from pathlib import Path

# --- Sample window (matches the original dissertation) ---------------------
START_DATE = "2015-01-01"
END_DATE = "2025-08-31"

# --- Instruments -----------------------------------------------------------
# Human-readable name -> Yahoo Finance ticker.
TICKERS = {
    "FTSE100": "VUKE.L",   # Vanguard FTSE 100 UCITS ETF (FTSE 100 proxy)
    "GBPUSD": "GBPUSD=X",  # GBP/USD spot
}

# Price field used throughout. Adjusted close = total return (includes
# dividends); recorded explicitly so validation is apples-to-apples with the
# dissertation and immune to yfinance's auto_adjust default changing.
PRICE_FIELD = "Adj Close"

# --- Transaction costs (per the dissertation) ------------------------------
# 0.02% bid-ask spread + 0.01% commission per one-way trade => 0.04% round-trip.
SPREAD_ONE_WAY = 0.0002
COMMISSION_ONE_WAY = 0.0001
ROUND_TRIP_COST = 2 * (SPREAD_ONE_WAY + COMMISSION_ONE_WAY)  # 0.0004 (unused until Phase 2)

# --- Paths -----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
MANIFEST_PATH = DATA_DIR / "manifest.csv"

# Reference: the dissertation reported ~2,693 trading days over the sample.
DISSERTATION_TRADING_DAYS = 2693
