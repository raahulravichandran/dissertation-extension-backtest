"""Backtest execution, performance metrics, and factor regressions.

One engine, shared by every strategy. Execution convention: a signal formed on
the close of day t takes effect on day t+1 (positions = signals.shift(1)), so
there is no look-ahead. Costs are charged on turnover (change in position).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

import config

# Cost per unit of turnover. A 0→1 open is one-way (half the round trip); a
# -1→+1 flip is turnover 2 and so costs the full round trip.
COST_PER_TURN = config.ROUND_TRIP_COST / 2  # 0.0002


def backtest(prices: pd.Series, signals: pd.Series) -> dict:
    """Run one strategy. Returns net daily returns, positions, and gross returns."""
    prices = prices.astype(float)
    signals = signals.reindex(prices.index).fillna(0.0)

    daily_ret = prices.pct_change().fillna(0.0)
    positions = signals.shift(1).fillna(0.0).astype(float)  # execute next day

    gross = positions * daily_ret
    turnover = positions.diff().abs().fillna(0.0)
    costs = turnover * COST_PER_TURN
    net = gross - costs
    return {"net": net, "gross": gross, "positions": positions, "turnover": turnover}


def performance_metrics(net: pd.Series, positions: pd.Series | None = None) -> dict:
    """CAGR, Sharpe, max drawdown, win rate (active days), time in market."""
    r = net.dropna()
    if len(r) == 0:
        return {}

    total_return = (1 + r).prod() - 1
    cagr = (1 + total_return) ** (252 / len(r)) - 1
    ann_vol = r.std() * np.sqrt(252)
    sharpe = cagr / ann_vol if ann_vol > 0 else 0.0

    cum = (1 + r).cumprod()
    drawdown = (cum - cum.expanding().max()) / cum.expanding().max()
    max_dd = drawdown.min()

    if positions is not None:
        pos = positions.reindex(r.index).fillna(0.0)
        active = pos != 0
        active_ret = r[active]
        time_in_market = float(active.mean() * 100)
    else:
        active_ret = r
        time_in_market = np.nan
    win_rate = float((active_ret > 0).mean() * 100) if len(active_ret) else 0.0

    return {
        "cagr": cagr * 100,
        "sharpe": sharpe,
        "max_dd": max_dd * 100,
        "win_rate": win_rate,
        "time_in_market": time_in_market,
        "n_obs": len(r),
        "n_trades": int((positions.diff().abs() != 0).sum()) if positions is not None else np.nan,
    }


def capm_alpha(strategy_ret: pd.Series, market_ret: pd.Series) -> dict:
    """CAPM alpha/beta vs the market (rf = 0), HAC (Newey-West, 5-lag) errors."""
    df = pd.DataFrame({"s": strategy_ret, "m": market_ret}).dropna()
    if len(df) < 60:
        return {"alpha": np.nan, "beta": np.nan, "alpha_p": np.nan}
    X = sm.add_constant(df["m"])
    model = sm.OLS(df["s"], X).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    return {
        "alpha": model.params["const"] * 252 * 100,
        "beta": model.params["m"],
        "alpha_p": model.pvalues["const"],
    }


def hac_mean_diff(strategy_ret: pd.Series, market_ret: pd.Series) -> dict:
    """Table 3 test: is the strategy's mean daily return different from the market's?

    Regress (strategy - market) on a constant with HAC errors; report the annualised
    difference, t-stat and p-value.
    """
    diff = (strategy_ret - market_ret).dropna()
    if len(diff) < 120:
        return {"ann_diff": np.nan, "t": np.nan, "p": np.nan}
    X = np.ones((len(diff), 1))
    model = sm.OLS(diff.values, X).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    return {
        "ann_diff": float(model.params[0]) * 252 * 100,
        "t": float(model.tvalues[0]),
        "p": float(model.pvalues[0]),
    }


def ff5_alpha(strategy_ret: pd.Series, ff: pd.DataFrame) -> dict:
    """Fama-French 5-factor alpha (HAC). ff columns: Mkt-RF, SMB, HML, RMW, CMA, RF (decimals)."""
    df = pd.DataFrame({"s": strategy_ret}).join(ff, how="inner").dropna()
    if len(df) < 60:
        return {"ff5_alpha": np.nan, "ff5_r2": np.nan, "ff5_alpha_p": np.nan}
    excess = df["s"] - df["RF"]
    X = sm.add_constant(df[["Mkt-RF", "SMB", "HML", "RMW", "CMA"]])
    model = sm.OLS(excess, X).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    return {
        "ff5_alpha": model.params["const"] * 252 * 100,
        "ff5_r2": model.rsquared,
        "ff5_alpha_p": model.pvalues["const"],
    }
