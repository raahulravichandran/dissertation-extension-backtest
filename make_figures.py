"""Phase 5 figure: Contrarian Bollinger vs. market cumulative return, 2015 -> today,
with the Aug-2025 in/out-of-sample split marked. Reads the committed extension snapshot.

Usage: python make_figures.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import config
from backtest import engine
from run_phase3 import get_full_history
from strategies.signals import contrarian_bollinger

FIG_DIR = config.PROJECT_ROOT / "reports" / "figures"


def main() -> None:
    full = get_full_history("FTSE100", config.TICKERS["FTSE100"])  # loads existing snapshot
    prices = full[config.PRICE_FIELD].dropna()

    market = prices.pct_change().fillna(0.0)
    boll = engine.backtest(prices, contrarian_bollinger(prices))["net"]

    mkt_cum = (1 + market).cumprod()
    boll_cum = (1 + boll).cumprod()
    split = pd.Timestamp(config.END_DATE)

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(boll_cum.index, boll_cum, label="Contrarian Bollinger (net)", color="#1f77b4", lw=1.6)
    ax.plot(mkt_cum.index, mkt_cum, label="Market (VUKE.L buy & hold)", color="#888888", lw=1.4, ls="--")
    ax.axvline(split, color="#d62728", lw=1.0, ls=":")
    ax.text(split, ax.get_ylim()[1], "  in-sample | extension", color="#d62728",
            va="top", ha="left", fontsize=8)

    ax.set_title("FTSE 100 Contrarian Bollinger vs. Market — cumulative return (£1 invested)")
    ax.set_ylabel("Growth of £1 (net of costs)")
    ax.set_xlabel("")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.margins(x=0.01)
    fig.tight_layout()

    out = FIG_DIR / "bollinger_vs_market.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved {out.relative_to(config.PROJECT_ROOT)}  "
          f"(Bollinger x{boll_cum.iloc[-1]:.2f}, Market x{mkt_cum.iloc[-1]:.2f}, split {split.date()})")


if __name__ == "__main__":
    main()
