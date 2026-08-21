"""The seven trading strategies, re-implemented from the dissertation's §3.2.

Each function takes a price series (adjusted close) and returns a signal series
of {-1 short, 0 cash, +1 long}. Signals use only information available up to and
including the close of day t; the backtest engine applies the one-day execution
lag (position on t+1), so there is no look-ahead here.

Where the paper under-specifies a rule, the assumption is marked ASSUMPTION and
listed in reports/phase2_validation.md. Per the Phase 2 plan, these were chosen
from the prose without consulting the original code.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# --- shared helper ---------------------------------------------------------
def compute_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """Wilder's RSI (EMA smoothing, alpha = 1/window)."""
    delta = prices.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    return 100 - (100 / (1 + rs))


# --- momentum --------------------------------------------------------------
def momentum_sma(prices: pd.Series, fast: int = 50, slow: int = 200) -> pd.Series:
    """Long when 50-day SMA > 200-day SMA, short when below (cash during warm-up)."""
    sma_fast = prices.rolling(fast).mean()
    sma_slow = prices.rolling(slow).mean()
    sig = pd.Series(0, index=prices.index, dtype=int)
    sig[sma_fast > sma_slow] = 1
    sig[sma_fast < sma_slow] = -1
    return sig


def momentum_ema(prices: pd.Series, fast: int = 12, slow: int = 26) -> pd.Series:
    """Long when 12-day EMA > 26-day EMA, short when below (MACD spans)."""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    sig = pd.Series(0, index=prices.index, dtype=int)
    sig[ema_fast > ema_slow] = 1
    sig[ema_fast < ema_slow] = -1
    return sig


def momentum_breakout(prices: pd.Series, lookback: int = 20, k: float = 2.0) -> pd.Series:
    """Long when price breaks above the prior 20-day high + 2σ; short below the low - 2σ.

    ASSUMPTION: the paper gives no explicit exit/hold, so the position is held only
    on days the breakout condition holds (sparse, matching the ~2% time-in-market the
    paper reports). Bands use the prior window (shift 1) so today's price is compared
    to a level known before today.
    """
    rolling_high = prices.rolling(lookback).max().shift(1)
    rolling_low = prices.rolling(lookback).min().shift(1)
    vol = prices.pct_change().rolling(lookback).std().shift(1) * prices  # σ in price terms
    resistance = rolling_high + k * vol
    support = rolling_low - k * vol
    sig = pd.Series(0, index=prices.index, dtype=int)
    sig[prices > resistance] = 1
    sig[prices < support] = -1
    return sig


def momentum_lookback(prices: pd.Series, lookback: int = 60, threshold: float = 0.02) -> pd.Series:
    """Long when trailing 60-day return > +2%, short when < -2%, else cash."""
    past = prices.pct_change(lookback)
    sig = pd.Series(0, index=prices.index, dtype=int)
    sig[past > threshold] = 1
    sig[past < -threshold] = -1
    return sig


# --- contrarian ------------------------------------------------------------
def contrarian_bollinger(prices: pd.Series, window: int = 20, k: float = 2.0) -> pd.Series:
    """Enter long below the lower 2σ band, short above the upper band; exit at the SMA.

    Stateful: once entered, hold until price reverts to the 20-day SMA (the paper's
    'exits at the 20-day SMA'). This is the standout strategy, so the rule is coded
    exactly as described.
    """
    sma = prices.rolling(window).mean()
    std = prices.rolling(window).std()
    upper = sma + k * std
    lower = sma - k * std

    sig = pd.Series(0, index=prices.index, dtype=int)
    position = 0
    for i in range(len(prices)):
        px, s, u, l = prices.iloc[i], sma.iloc[i], upper.iloc[i], lower.iloc[i]
        if pd.isna(s) or pd.isna(u) or pd.isna(l):
            sig.iloc[i] = 0
            continue
        if position == 0:
            if px <= l:
                position = 1
            elif px >= u:
                position = -1
        elif position == 1 and px >= s:
            position = 0
        elif position == -1 and px <= s:
            position = 0
        sig.iloc[i] = position
    return sig


def contrarian_rsi(prices: pd.Series, rsi_window: int = 14, sma_window: int = 200) -> pd.Series:
    """Long when 14-day RSI < dynamic oversold and price > 200-day SMA; symmetric short.

    Dynamic thresholds: oversold = 30 + 0.5·vol, overbought = 70 - 0.5·vol, clipped and
    gap-enforced to prevent crossing (per the paper).
    ASSUMPTION: 'rolling volatility' read as the 20-day daily-return std in percentage
    points (×100), keeping the adjustment small relative to the 0-100 RSI scale.
    """
    rsi = compute_rsi(prices, rsi_window)
    sma = prices.rolling(sma_window).mean()
    vol = prices.pct_change().rolling(20).std() * 100

    oversold = (30 + 0.5 * vol).clip(lower=5, upper=45)
    overbought = (70 - 0.5 * vol).clip(lower=55, upper=95)
    overbought = np.maximum(overbought, oversold + 10)  # min gap 10

    sig = pd.Series(0, index=prices.index, dtype=int)
    sig[(rsi < oversold) & (prices > sma)] = 1
    sig[(rsi > overbought) & (prices < sma)] = -1
    return sig


def contrarian_reversal(prices: pd.Series, lookback: int = 5, threshold: float = 0.05,
                        hold_days: int = 3) -> pd.Series:
    """Long when prior 5-day return < -5%, short when > +5%; hold for 3 days."""
    past = prices.pct_change(lookback)
    entry = pd.Series(np.nan, index=prices.index)
    entry[past < -threshold] = 1
    entry[past > threshold] = -1
    sig = entry.ffill(limit=max(0, hold_days - 1)).fillna(0).astype(int)
    return sig


# Registry: key -> (label, function). Order matches the dissertation tables.
STRATEGIES = {
    "momentum_sma": ("Momentum SMA", momentum_sma),
    "momentum_ema": ("Momentum EMA", momentum_ema),
    "momentum_breakout": ("Momentum Breakout", momentum_breakout),
    "momentum_lookback": ("Momentum Lookback", momentum_lookback),
    "contrarian_rsi": ("Contrarian RSI", contrarian_rsi),
    "contrarian_bollinger": ("Contrarian Bollinger", contrarian_bollinger),
    "contrarian_reversal": ("Contrarian Reversal", contrarian_reversal),
}
