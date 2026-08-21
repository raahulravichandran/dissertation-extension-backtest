"""Phase 6 orchestrator: Contrarian Bollinger on individual FTSE 100 constituents.

Tests whether the index-level edge generalises to single names (mechanism check only — not
evidence of a tradable edge; see Phase 3 index non-persistence). Writes
reports/phase6_stock_generalisation.md.

Usage: python run_phase6.py [--refresh]
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd

import config
from backtest import engine
from data_pipeline import get_series
from strategies.signals import contrarian_bollinger

# Phase 6 stock universe — agreed before build (see phase_plans/phase_6.md).
STOCKS: dict[str, tuple[str, str, str]] = {
    "HSBA": ("HSBA.L", "HSBC", "Financials"),
    "AZN": ("AZN.L", "AstraZeneca", "Healthcare"),
    "ULVR": ("ULVR.L", "Unilever", "Consumer staples"),
    "BP": ("BP.L", "BP", "Energy"),
    "RIO": ("RIO.L", "Rio Tinto", "Materials"),
    "REL": ("REL.L", "RELX", "Business services"),
    "NG": ("NG.L", "National Grid", "Utilities"),
    "BT": ("BT-A.L", "BT Group", "Telecom"),
}

BONFERRONI_ALPHA = 0.05
N_TESTS = len(STOCKS)
BONFERRONI_P = BONFERRONI_ALPHA / N_TESTS


def _trim_sample(prices: pd.Series) -> pd.Series:
    return prices.loc[config.START_DATE : config.END_DATE].dropna()


def run_stock(name: str, ticker: str, company: str, sector: str, refresh: bool) -> dict:
    df = get_series(name, ticker, refresh=refresh)
    prices = _trim_sample(df[config.PRICE_FIELD])
    if len(prices) < 252:
        raise RuntimeError(f"{name}: insufficient data ({len(prices)} rows) after trimming")

    market_ret = prices.pct_change()
    signals = contrarian_bollinger(prices)
    bt = engine.backtest(prices, signals)
    m = engine.performance_metrics(bt["net"], bt["positions"])
    hac = engine.hac_mean_diff(bt["net"], market_ret)
    mkt = engine.performance_metrics(market_ret.dropna())

    sig_raw = hac["p"] < 0.05 if pd.notna(hac["p"]) else False
    sig_bonf = hac["p"] < BONFERRONI_P if pd.notna(hac["p"]) else False

    return {
        "name": name,
        "ticker": ticker,
        "company": company,
        "sector": sector,
        "n_obs": m["n_obs"],
        "mkt_cagr": mkt["cagr"],
        "cagr": m["cagr"],
        "sharpe": m["sharpe"],
        "time_pct": m["time_in_market"],
        "hac_t": hac["t"],
        "hac_p": hac["p"],
        "hac_ann_diff": hac["ann_diff"],
        "sig_raw": sig_raw,
        "sig_bonf": sig_bonf,
    }


def _verdict(rows: list[dict], index_row: dict) -> str:
    n_pos_cagr = sum(1 for r in rows if r["cagr"] > 0)
    n_beat_mkt = sum(1 for r in rows if r["cagr"] > r["mkt_cagr"])
    n_sig_raw = sum(1 for r in rows if r["sig_raw"])
    n_sig_bonf = sum(1 for r in rows if r["sig_bonf"])
    best = max(rows, key=lambda r: r["cagr"])
    worst = min(rows, key=lambda r: r["cagr"])

    if n_sig_bonf == 0 and n_pos_cagr <= n_beat_mkt:
        pattern = (
            "the Bollinger edge **does not generalise reliably** to individual FTSE 100 names"
        )
    elif n_sig_bonf >= 2 or n_beat_mkt >= 5:
        pattern = (
            "the Bollinger pattern **partially generalises** to some individual names "
            "(mixed in-sample results across sectors)"
        )
    elif n_pos_cagr >= 6:
        pattern = (
            "positive in-sample CAGRs are **widespread but mostly insignificant** after "
            "multiple-testing adjustment — weak/partial generalisation at best"
        )
    else:
        pattern = "results are **mixed and inconclusive** as a cross-sectional generalisation test"

    hp = index_row["hac_p"]
    hp_s = f"{hp:.3f}" if pd.notna(hp) else "n/a"
    ht = index_row["hac_t"]
    ht_s = f"{ht:.2f}" if pd.notna(ht) else "n/a"

    return (
        "**Verdict (read this first):** This is a **mechanism check only**, not evidence of a "
        "tradable edge. Phase 3 showed the Contrarian Bollinger strategy **did not persist** on "
        "the FTSE 100 index out-of-sample (−1.5% cumulative vs the market's +21.6% over ~11 "
        "months after Aug 2025), so any in-sample stock-level numbers below must **not** be read "
        "as actionable signals or portfolio inputs. **Even on the index itself (VUKE.L), the "
        f"strategy was not HAC-significant vs buy-and-hold in Phase 2** (t = {ht_s}, p = {hp_s}) "
        "— its apparent value was always in the **risk-adjusted return and reduced "
        f"time-in-market** (Sharpe {index_row['sharpe']:.2f} vs {index_row['mkt_sharpe']:.2f} "
        f"buy-and-hold; ~{index_row['time_pct']:.0f}% invested), not in statistically beating "
        "passive exposure. On the original sample (2015–Aug 2025), "
        f"{pattern}: {n_pos_cagr}/8 stocks show positive strategy CAGR, {n_beat_mkt}/8 beat "
        f"their own buy-and-hold, {n_sig_raw}/8 are HAC-significant at α=0.05 (raw), and "
        f"**{n_sig_bonf}/8 survive Bonferroni correction** (α/8 ≈ {BONFERRONI_P:.5f}). "
        f"The index delivered ~{index_row['cagr']:.1f}% Bollinger CAGR on VUKE.L; the stock "
        f"range here spans {worst['company']} ({worst['cagr']:.1f}%) to "
        f"{best['company']} ({best['cagr']:.1f}%). Survivorship bias applies (current FTSE 100 "
        "members only). **No investment advice is implied.**"
    )


def format_report(rows: list[dict], index_row: dict) -> str:
    lines = [
        "# Phase 6 — Stock-level Bollinger generalisation check\n",
        _verdict(rows, index_row),
        "\n",
        "## Scope and method\n",
        "- **Question:** does the Contrarian Bollinger edge validated on VUKE.L (Phase 2) appear "
        "on individual FTSE 100 constituents, or was it index-specific?",
        f"- **Sample:** {config.START_DATE} → {config.END_DATE} (original dissertation window; "
        "not the Phase 3 extension).",
        "- **Strategy:** Contrarian Bollinger (20-day window, 2σ bands, exit at SMA) — exact "
        "Phase 2/3 parameters.",
        "- **Benchmark:** each stock's own buy-and-hold (HAC mean-diff test, Newey-West 5-lag).",
        f"- **Multiple testing:** {N_TESTS} stocks tested; Bonferroni threshold "
        f"p < {BONFERRONI_P:.5f} (α={BONFERRONI_ALPHA}/{N_TESTS}).",
        "- **Survivorship:** names are current FTSE 100 constituents; delisted or removed "
        "constituents are excluded.",
        "- **Phase 3 context:** index-level edge did **not** persist OOS; stock results are "
        "in-sample mechanism checks only.\n",
        "## Results\n",
        "| Stock | Sector | Mkt CAGR | Bollinger CAGR | Sharpe | Time% | HAC t | HAC p | "
        "Sig (raw) | Sig (Bonf.) |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]

    for r in rows:
        raw = "Y" if r["sig_raw"] else "N"
        bonf = "Y" if r["sig_bonf"] else "N"
        hp = f"{r['hac_p']:.3f}" if pd.notna(r["hac_p"]) else "-"
        ht = f"{r['hac_t']:.2f}" if pd.notna(r["hac_t"]) else "-"
        lines.append(
            f"| {r['company']} ({r['ticker']}) | {r['sector']} | {r['mkt_cagr']:.1f}% | "
            f"{r['cagr']:.1f}% | {r['sharpe']:.2f} | {r['time_pct']:.1f} | {ht} | {hp} | "
            f"{raw} | {bonf} |"
        )

    lines.extend([
        f"\n**Index reference (Phase 2, VUKE.L):** Bollinger CAGR "
        f"{index_row['cagr']:.1f}%, Sharpe {index_row['sharpe']:.2f}, HAC t "
        f"{index_row['hac_t']:.2f} (p={index_row['hac_p']:.3f}) — not HAC-significant vs "
        "buy-and-hold on the index either.\n",
        "## Limitations\n",
        "1. **Not tradable evidence** — Phase 3 index non-persistence dominates interpretation.",
        "2. **Multiple testing / selection** — eight parallel tests; Bonferroni is conservative "
        "but appropriate for a pre-specified cross-section.",
        "3. **Survivorship bias** — only stocks still in the FTSE 100 as of the pull date.",
        "4. **Single-name vs ETF** — idiosyncratic risk, corporate actions, and spreads differ "
        "from the VUKE.L proxy; costs held at dissertation assumptions (0.04% round-trip).",
        "5. **Research only** — findings describe historical simulated performance, not "
        "recommendations to buy or sell any security.\n",
    ])
    return "\n".join(lines) + "\n"


def run_index_reference(refresh: bool) -> dict:
    """Recompute FTSE Bollinger on the original window for the context row."""
    df = get_series("FTSE100", config.TICKERS["FTSE100"], refresh=refresh)
    prices = _trim_sample(df[config.PRICE_FIELD])
    market_ret = prices.pct_change()
    bt = engine.backtest(prices, contrarian_bollinger(prices))
    mkt = engine.performance_metrics(market_ret.dropna())
    m = engine.performance_metrics(bt["net"], bt["positions"])
    hac = engine.hac_mean_diff(bt["net"], market_ret)
    return {
        "cagr": m["cagr"],
        "sharpe": m["sharpe"],
        "time_pct": m["time_in_market"],
        "mkt_sharpe": mkt["sharpe"],
        "hac_t": hac["t"],
        "hac_p": hac["p"],
    }


def main(refresh: bool = False) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    print("=" * 60)
    print("PHASE 6: STOCK-LEVEL BOLLINGER GENERALISATION")
    print("=" * 60)

    rows = []
    for name, (ticker, company, sector) in STOCKS.items():
        print(f"\nRunning {company} ({ticker})...")
        rows.append(run_stock(name, ticker, company, sector, refresh))

    index_row = run_index_reference(refresh)
    report = format_report(rows, index_row)
    out = config.PROJECT_ROOT / "reports" / "phase6_stock_generalisation.md"
    out.write_text(report, encoding="utf-8")

    print("\n" + report)
    print(f"Report written to {out.relative_to(config.PROJECT_ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 6 stock-level Bollinger check")
    parser.add_argument("--refresh", action="store_true", help="Force fresh Yahoo downloads")
    args = parser.parse_args()
    main(refresh=args.refresh)
