"""Phase 7 orchestrator: portfolio-construction capability demonstration.

Builds an inverse-volatility-weighted portfolio of eight single-name Contrarian
Bollinger sleeves (the Phase 6 universe) and reports it at the PORTFOLIO level:
return, volatility, Sharpe, correlation structure, and max drawdown.

IMPORTANT — this is a *capability demonstration*, not an investment system. The
underlying Contrarian Bollinger signal did NOT persist out-of-sample (Phase 3)
and did NOT generalise to individual stocks (Phase 6, 0/8 HAC-significant). The
portfolio layer therefore demonstrates *portfolio-construction methodology on a
strategy already shown not to work live* — it is never a tradable recommendation.
All in-sample numbers inherit that null result. See reports/phase7_portfolio.md.

Usage: python run_phase7.py [--refresh]
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

import config
from backtest import engine
from data_pipeline import get_series
from strategies.signals import contrarian_bollinger

# Reuse the exact Phase 6 universe (single source of truth): eight FTSE 100
# constituents spanning eight distinct sectors. VUKE.L is deliberately EXCLUDED
# as a sleeve — the index contains these names, so adding it would double-count
# and corrupt the correlation matrix. It appears in Phase 6 as reference only.
from run_phase6 import STOCKS

# Trailing window for the inverse-volatility weights. Reuses the project's
# already-justified 20-day rolling-vol window (no new unjustified lookback).
VOL_WINDOW = 20


def _trim_sample(prices: pd.Series) -> pd.Series:
    return prices.loc[config.START_DATE : config.END_DATE].dropna()


def load_prices(refresh: bool) -> pd.DataFrame:
    """Aligned adjusted-close prices for the eight sleeves (common trading days)."""
    cols = {}
    for name, (ticker, _company, _sector) in STOCKS.items():
        df = get_series(name, ticker, refresh=refresh)
        cols[name] = _trim_sample(df[config.PRICE_FIELD])
    price_df = pd.concat(cols, axis=1).dropna()
    if len(price_df) < 252:
        raise RuntimeError(f"insufficient common history ({len(price_df)} rows)")
    return price_df


def build_sleeves(price_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per-sleeve strategy net returns and active-position flags, aligned."""
    nets, active = {}, {}
    for name in price_df.columns:
        prices = price_df[name]
        bt = engine.backtest(prices, contrarian_bollinger(prices))
        nets[name] = bt["net"]
        active[name] = bt["positions"] != 0
    return pd.DataFrame(nets), pd.DataFrame(active)


def inverse_vol_weights(price_df: pd.DataFrame) -> pd.DataFrame:
    """Inverse-vol weights, normalised to sum to 1, formed WITHOUT look-ahead.

    Weight_i(t) is proportional to 1 / (trailing VOL_WINDOW-day realised vol of
    asset i, using returns through t). The caller applies weights with a one-day
    shift so a weight formed on close of t governs the return realised over t+1.
    """
    asset_ret = price_df.pct_change()
    roll_vol = asset_ret.rolling(VOL_WINDOW).std()
    inv_vol = 1.0 / roll_vol
    weights = inv_vol.div(inv_vol.sum(axis=1), axis=0)
    return weights


def portfolio_metrics(net: pd.Series) -> dict:
    """Reuse engine conventions for CAGR/Sharpe/max-dd; add annualised vol."""
    m = engine.performance_metrics(net)
    m["ann_vol"] = float(net.std() * np.sqrt(252) * 100)
    return m


def correlation_stability(sleeve_net: pd.DataFrame) -> dict:
    """Mean pairwise correlation over the full window vs each half.

    A compact, empirical demonstration that in-sample correlations are not
    stable — supporting the instability caveat with evidence, not assertion.
    """

    def mean_pairwise(df: pd.DataFrame) -> float:
        c = df.corr().values
        iu = np.triu_indices_from(c, k=1)
        return float(np.nanmean(c[iu]))

    n = len(sleeve_net)
    first, second = sleeve_net.iloc[: n // 2], sleeve_net.iloc[n // 2 :]
    return {
        "full": mean_pairwise(sleeve_net),
        "first_half": mean_pairwise(first),
        "second_half": mean_pairwise(second),
    }


def run_portfolio(refresh: bool) -> dict:
    price_df = load_prices(refresh)
    sleeve_net, sleeve_active = build_sleeves(price_df)
    weights = inverse_vol_weights(price_df)

    # Apply weights one day forward (no look-ahead); evaluate only where the
    # trailing-vol weights are fully defined.
    weights_applied = weights.shift(1)
    valid = weights_applied.dropna().index.intersection(sleeve_net.index)

    w = weights_applied.loc[valid]
    port_net = (w * sleeve_net.loc[valid]).sum(axis=1)

    # Equal-weight buy-and-hold of the same eight names, evaluated on the same
    # window. True buy-and-hold (1/8 each at the start, left to drift) — no
    # implicit daily rebalancing.
    bh_value = (price_df / price_df.iloc[0]).mean(axis=1)
    bh_net = bh_value.pct_change().loc[valid]

    # Portfolio time-in-market = average fraction of capital actually deployed
    # (weight-weighted sleeve activity), not a simple day count.
    exposure = (w * sleeve_active.loc[valid]).sum(axis=1)

    port_m = portfolio_metrics(port_net)
    bh_m = portfolio_metrics(bh_net)
    hac = engine.hac_mean_diff(port_net, bh_net)

    corr = sleeve_net.loc[valid].corr()
    stab = correlation_stability(sleeve_net.loc[valid])

    # Average realised weight per sleeve over the evaluated window (for context).
    avg_w = w.mean().sort_values(ascending=False)

    return {
        "price_df": price_df,
        "valid": valid,
        "port_net": port_net,
        "bh_net": bh_net,
        "port_m": port_m,
        "bh_m": bh_m,
        "hac": hac,
        "corr": corr,
        "stab": stab,
        "avg_w": avg_w,
        "time_pct": float(exposure.mean() * 100),
        "port_cum": float((1 + port_net).prod() - 1) * 100,
        "bh_cum": float((1 + bh_net).prod() - 1) * 100,
    }


def _verdict(res: dict) -> str:
    port, bh, hac = res["port_m"], res["bh_m"], res["hac"]
    p_s = f"{hac['p']:.3f}" if pd.notna(hac["p"]) else "n/a"
    t_s = f"{hac['t']:.2f}" if pd.notna(hac["t"]) else "n/a"
    return (
        "**Verdict (read this first):** This is a **portfolio-construction "
        "capability demonstration, not an investment system and not a tradable "
        "portfolio.** It applies standard portfolio methodology (inverse-volatility "
        "sizing, portfolio-level risk reporting) to the Contrarian Bollinger "
        "strategy — a signal this project has **already shown does not work live**: "
        "it did **not** persist out-of-sample on the FTSE 100 index (Phase 3: −1.5% "
        "vs the market's +21.6% in the ~11 months after Aug 2025) and did **not** "
        "generalise to individual stocks (Phase 6: 0/8 HAC-significant, raw or "
        "Bonferroni). Every number below is therefore **in-sample and inherits that "
        "null result** — the point is to show I can *build and risk-assess a "
        "multi-asset portfolio*, not that this portfolio should be traded. On the "
        f"2015–Aug 2025 window the inverse-vol portfolio returned "
        f"{res['port_cum']:.1f}% cumulative ({port['cagr']:.1f}% CAGR, "
        f"{port['ann_vol']:.1f}% vol, Sharpe {port['sharpe']:.2f}, max drawdown "
        f"{port['max_dd']:.1f}%, ~{res['time_pct']:.0f}% average capital deployed) "
        f"versus the equal-weight buy-and-hold of the same eight names at "
        f"{res['bh_cum']:.1f}% cumulative ({bh['cagr']:.1f}% CAGR, "
        f"{bh['ann_vol']:.1f}% vol, Sharpe {bh['sharpe']:.2f}, max drawdown "
        f"{bh['max_dd']:.1f}%). The portfolio's mean daily return is **not** "
        f"statistically distinguishable from that benchmark (HAC t = {t_s}, "
        f"p = {p_s}). **No investment advice is implied; do not trade this.**"
    )


def format_report(res: dict) -> str:
    port, bh = res["port_m"], res["bh_m"]
    stab = res["stab"]
    lines = [
        "# Phase 7 — Portfolio-construction capability demonstration\n",
        _verdict(res),
        "\n",
        "## What this phase is (and is not)\n",
        "- **Is:** a demonstration that I can construct a multi-asset portfolio "
        "(position sizing, portfolio-level risk, correlation, drawdown) — a core "
        "asset-management / quant skill.",
        "- **Is not:** a claim that this portfolio is tradable. The underlying "
        "signal failed out-of-sample (Phase 3) and failed to generalise (Phase 6). "
        "The construction *methodology* is the deliverable; the strategy is a "
        "vehicle for demonstrating it, chosen because it is already validated as "
        "*not working live* — so no reader can mistake it for a recommendation.\n",
        "## Scope and method\n",
        "- **Universe:** eight FTSE 100 single-name Contrarian Bollinger sleeves "
        "(the Phase 6 set), one per sector. VUKE.L is **excluded** as a sleeve — "
        "the index contains these names, so including it would double-count and "
        "corrupt the correlation matrix; it appears in Phase 6 as reference only.",
        f"- **Sample:** {config.START_DATE} → {config.END_DATE} (original "
        "dissertation window; **in-sample** — the Phase 3 out-of-sample "
        "non-persistence caveat is inherited in full).",
        "- **Sizing rule (one, deliberately):** **inverse-volatility weighting** — "
        f"each sleeve weighted ∝ 1 / (trailing {VOL_WINDOW}-day realised "
        "volatility of the underlying asset), normalised to sum to 1. Chosen "
        "because it *demonstrates risk-based sizing* (size to risk), the "
        "transferable skill this phase is about; equal-weight — the alternative "
        "**not** used — is simpler but ignores that the jumpier names (energy, "
        "telecom) then silently dominate portfolio risk.",
        "- **No look-ahead:** weights are formed from *trailing* volatility only "
        "and applied one day forward (a weight set on the close of day *t* governs "
        "the return over *t+1*). This directly answers the markers' full-sample "
        "look-ahead critique — the weights never see future data.",
        "- **Benchmark:** equal-weight **buy-and-hold** of the same eight names "
        "(1/8 each at the start, left to drift; no rebalancing).",
        "- **Costs:** each sleeve already bears the dissertation's 0.04% "
        "round-trip cost on its own signal turnover; the *additional* turnover "
        "from daily weight rebalancing is **not** charged (noted as a limitation).\n",
        "## Portfolio-level results\n",
        "| Metric | Inverse-vol portfolio | Equal-weight buy & hold |",
        "|---|---|---|",
        f"| Cumulative return | {res['port_cum']:.1f}% | {res['bh_cum']:.1f}% |",
        f"| CAGR | {port['cagr']:.1f}% | {bh['cagr']:.1f}% |",
        f"| Annualised volatility | {port['ann_vol']:.1f}% | {bh['ann_vol']:.1f}% |",
        f"| Sharpe | {port['sharpe']:.2f} | {bh['sharpe']:.2f} |",
        f"| Max drawdown | {port['max_dd']:.1f}% | {bh['max_dd']:.1f}% |",
        f"| Avg. capital deployed (time in market) | {res['time_pct']:.1f}% | 100% |",
        f"\n**Portfolio vs benchmark (HAC mean-diff, Newey–West 5-lag):** "
        f"annualised difference {res['hac']['ann_diff']:.1f}%, t = "
        f"{res['hac']['t']:.2f}, p = {res['hac']['p']:.3f} — "
        "**not statistically distinguishable** from equal-weight buy-and-hold.\n",
        "> **Read the Sharpe honestly.** The portfolio's higher Sharpe and shallower "
        "drawdown versus buy-and-hold are **mechanical, not alpha**: it sits in cash "
        f"~{100 - res['time_pct']:.0f}% of the time and inverse-vol deliberately "
        "shrinks the most volatile sleeves, so of course realised volatility and "
        "drawdown fall. The *return* itself is statistically indistinguishable from "
        "the benchmark (above), and the underlying signal failed out-of-sample. Lower "
        "risk from holding cash and sizing down is a property of the construction, "
        "**not** evidence the strategy works.\n",
        "### Average realised sleeve weights\n",
        "Inverse-vol tilts capital toward the lower-volatility names, as intended:\n",
        "| Sleeve | Sector | Avg. weight |",
        "|---|---|---|",
    ]
    for name, w in res["avg_w"].items():
        _ticker, company, sector = STOCKS[name]
        lines.append(f"| {company} | {sector} | {w * 100:.1f}% |")

    # Correlation matrix of the eight sleeve return streams.
    corr = res["corr"]
    lines.append("\n### Correlation matrix of the eight sleeve return streams\n")
    header = "| | " + " | ".join(corr.columns) + " |"
    sep = "|---" * (len(corr.columns) + 1) + "|"
    lines.append(header)
    lines.append(sep)
    for row in corr.index:
        cells = " | ".join(f"{corr.loc[row, c]:.2f}" for c in corr.columns)
        lines.append(f"| **{row}** | {cells} |")

    lines.extend([
        "\n**Correlation instability (evidence, not assertion):** mean pairwise "
        f"sleeve correlation is {stab['full']:.2f} over the full window, but "
        f"{stab['first_half']:.2f} in the first half versus "
        f"{stab['second_half']:.2f} in the second — the correlation structure "
        "*shifts within the very sample it is estimated on*. Any diversification "
        "benefit read off the matrix above is therefore not something to rely on "
        "out-of-sample.\n",
        "## Limitations\n",
        "1. **Inherited null result (dominant).** The underlying Contrarian "
        "Bollinger signal did not persist out-of-sample (Phase 3) and did not "
        "generalise across stocks (Phase 6). No portfolio wrapper can rescue a "
        "signal that does not work live; every figure here is in-sample and must "
        "not be read as a tradable result.",
        "2. **Correlation instability.** As shown above, the correlations that "
        "drive any diversification claim are not stable even within the sample, "
        "let alone out of it. In-sample correlation (and covariance) is a weak "
        "guide to future co-movement — the classic reason naive optimisation "
        "disappoints live.",
        "3. **Weight instability / estimation risk.** The inverse-vol weights are "
        "themselves estimated from trailing realised volatility, which is noisy "
        "and regime-dependent; the average weights shown are not stable targets.",
        "4. **Single sizing rule by design.** One rule (inverse-vol) is shown, "
        "not a menu. Mean-variance / Markowitz optimisation and an efficient "
        "frontier are deliberately out of scope — a much larger undertaking, and "
        "one that would over-fit in-sample covariance here to little end.",
        "5. **Rebalancing costs not modelled.** Only each sleeve's own signal "
        "turnover bears the 0.04% cost; the daily turnover from re-weighting is "
        "uncosted, so the portfolio return is modestly optimistic.",
        "6. **Survivorship bias.** The eight names are current FTSE 100 "
        "constituents; delisted/removed names are excluded.",
        "7. **Research only.** Simulated historical performance on a strategy "
        "shown not to work live — not advice to buy or sell any security, and not "
        "a portfolio to trade.\n",
    ])
    return "\n".join(lines) + "\n"


def main(refresh: bool = False) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    print("=" * 60)
    print("PHASE 7: PORTFOLIO-CONSTRUCTION CAPABILITY DEMONSTRATION")
    print("=" * 60)
    print("\nBuilding inverse-vol portfolio of eight Bollinger sleeves...")

    res = run_portfolio(refresh)
    report = format_report(res)
    out = config.PROJECT_ROOT / "reports" / "phase7_portfolio.md"
    out.write_text(report, encoding="utf-8")

    print("\n" + report)
    print(f"Report written to {out.relative_to(config.PROJECT_ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 7 portfolio construction demo")
    parser.add_argument("--refresh", action="store_true", help="Force fresh Yahoo downloads")
    args = parser.parse_args()
    main(refresh=args.refresh)
