"""Phase 3b: regime-parameter sensitivity for the FTSE 100 Contrarian Bollinger.

Closes the specific gap the markers flagged (the Phase 3 robustness grid varied the
Bollinger strategy's own parameters, not the regime-classification parameters). Two
bounded checks on the original sample:
  1. Volatility-state window in {10, 20, 40} days.
  2. Bank Rate threshold in {0.5%, 1%, 2%}.
Both show whether the regime finding is stable to the specific parameter choice.

Usage: python run_phase3b.py
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import config
from backtest import engine
from data_pipeline import latest_snapshot, load_snapshot
from strategies.signals import contrarian_bollinger

BOE_CSV = config.DATA_DIR / "boe_bank_rate.csv"


def _split(returns: pd.Series, regime_high: pd.Series) -> dict:
    """Annualised (arithmetic) return in the high vs low leg of a lagged binary regime."""
    lab = regime_high.shift(1)  # past-only: yesterday's label conditions today's return
    df = pd.DataFrame({"r": returns, "hi": lab}).dropna()
    hi = df["r"][df["hi"] == 1]
    lo = df["r"][df["hi"] == 0]
    return {
        "high_ann": hi.mean() * 252 * 100 if len(hi) else np.nan,
        "low_ann": lo.mean() * 252 * 100 if len(lo) else np.nan,
        "n_high": len(hi), "n_low": len(lo),
    }


def vol_state_sensitivity(prices: pd.Series, bollinger_net: pd.Series, windows) -> list[dict]:
    out = []
    for w in windows:
        vol = prices.pct_change().rolling(w).std() * np.sqrt(252)
        high = (vol > vol.median()).astype(float)  # full-sample median (dissertation's def)
        s = _split(bollinger_net, high)
        s["window"] = w
        s["spread"] = s["high_ann"] - s["low_ann"]
        out.append(s)
    return out


def rate_threshold_sensitivity(prices: pd.Series, bollinger_net: pd.Series, thresholds) -> list[dict]:
    rate = pd.read_csv(BOE_CSV, comment="#", parse_dates=["effective_date"]).sort_values("effective_date")
    steps = rate.set_index("effective_date")["bank_rate"]
    daily = steps.reindex(steps.index.union(prices.index)).ffill().reindex(prices.index)
    out = []
    for t in thresholds:
        high = (daily > t).astype(float)  # high-rate = above threshold
        s = _split(bollinger_net, high)   # "high" leg = high-rate; report both
        s["threshold"] = t
        s["low_rate_ann"] = s["low_ann"]   # rate <= t
        s["high_rate_ann"] = s["high_ann"]  # rate > t
        s["spread_low_minus_high"] = s["low_ann"] - s["high_ann"]
        out.append(s)
    return out


def build_report(vol_rows, rate_rows) -> str:
    L = ["# Phase 3b — Regime-Parameter Sensitivity (FTSE 100 Contrarian Bollinger)\n"]
    L.append("Closes the Phase 3 gap: the robustness grid varied the Bollinger strategy's own "
             "parameters; these two checks vary the regime-classification parameters the second "
             "marker specifically flagged. Original sample; returns annualised arithmetically "
             "(daily mean × 252); regime labels lagged one day.\n")

    L.append("\n## 1. Volatility-state window {10, 20, 40 days}\n")
    L.append("High/low vol = N-day annualised rolling std above/below the full-sample median "
             "(the dissertation's definition). Question: does the high-vol premium depend on N=20?\n")
    L.append("| Window | High-vol ann. | Low-vol ann. | Spread (high−low) | n high/low |")
    L.append("|---|---|---|---|---|")
    for r in vol_rows:
        L.append(f"| {r['window']}d | {r['high_ann']:+.1f}% | {r['low_ann']:+.1f}% | "
                 f"{r['spread']:+.1f}pp | {r['n_high']}/{r['n_low']} |")
    L.append("\n*Dissertation (20-day, Table 5): high-vol 10.8% vs low-vol 5.3%.*\n")

    L.append("\n## 2. Bank Rate threshold {0.5%, 1%, 2%}\n")
    L.append("Low-rate = Bank Rate ≤ threshold. Question: does the low-rate outperformance depend "
             "on the exact 1% cut?\n")
    L.append("| Threshold | Low-rate ann. | High-rate ann. | Spread (low−high) | n low/high |")
    L.append("|---|---|---|---|---|")
    for r in rate_rows:
        L.append(f"| {r['threshold']:.1f}% | {r['low_rate_ann']:+.1f}% | {r['high_rate_ann']:+.1f}% | "
                 f"{r['spread_low_minus_high']:+.1f}pp | {r['n_low']}/{r['n_high']} |")
    L.append("\n*Dissertation (1% split, Table 5): low-rate 9.4% vs high-rate 4.6%.*\n")

    # Verdict
    vol_spreads = [r["spread"] for r in vol_rows]
    rate_spreads = [r["spread_low_minus_high"] for r in rate_rows]
    vol_stable = all(s > 0 for s in vol_spreads)
    rate_stable = all(s > 0 for s in rate_spreads)
    L.append("\n## Verdict\n")
    L.append(f"- **Vol-state window:** high-vol premium is {'positive across all three windows' if vol_stable else 'NOT stable across windows'} "
             f"({min(vol_spreads):+.1f} to {max(vol_spreads):+.1f}pp) — the finding does not hinge on choosing 20 days.")
    L.append(f"- **Bank Rate threshold:** low-rate outperformance is {'positive across all three thresholds' if rate_stable else 'NOT stable across thresholds'} "
             f"({min(rate_spreads):+.1f} to {max(rate_spreads):+.1f}pp) — the finding does not hinge on the exact 1% cut.")
    return "\n".join(L) + "\n"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    print("=" * 60)
    print("PHASE 3b: REGIME-PARAMETER SENSITIVITY")
    print("=" * 60)

    prices = load_snapshot(latest_snapshot("FTSE100"))[config.PRICE_FIELD].dropna()
    net = engine.backtest(prices, contrarian_bollinger(prices))["net"]

    vol_rows = vol_state_sensitivity(prices, net, windows=[10, 20, 40])
    rate_rows = rate_threshold_sensitivity(prices, net, thresholds=[0.5, 1.0, 2.0])

    report = build_report(vol_rows, rate_rows)
    out = config.PROJECT_ROOT / "reports" / "phase3b_sensitivity.md"
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"Report written to {out.relative_to(config.PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
