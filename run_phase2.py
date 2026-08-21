"""Phase 2 orchestrator: run the 7 strategies on both assets, compute metrics,
and validate against the dissertation (Tables 1-3). Writes reports/phase2_validation.md.

Usage: python run_phase2.py
"""

from __future__ import annotations

import sys

import pandas as pd

import config
import ff_factors
from backtest import engine
from data_pipeline import get_series
from dissertation_reference import TABLE1_FTSE, TABLE2_GBPUSD, TABLE3_HAC_FTSE, TOL
from strategies.signals import STRATEGIES


def _flag(diff, tol):
    return "OK" if (pd.notna(diff) and abs(diff) <= tol) else "DISCREPANCY"


def run_asset(name: str, ticker: str, reported: dict, hac_reported: dict | None, ff):
    """Backtest all strategies on one asset; return a list of result rows."""
    df = get_series(name, ticker)
    prices = df[config.PRICE_FIELD].dropna()
    market_ret = prices.pct_change()

    rows = []
    # Market buy-and-hold as a sanity anchor.
    mkt = engine.performance_metrics(market_ret.dropna())
    rows.append({
        "strategy": "market", "label": "Market (buy & hold)",
        "cagr": mkt["cagr"], "sharpe": mkt["sharpe"], "max_dd": mkt["max_dd"],
        "time": 100.0, "hac_t": None,
        "rep_cagr": reported["market"]["cagr"], "rep_sharpe": reported["market"]["sharpe"],
        "rep_hac_t": None,
    })

    for key, (label, fn) in STRATEGIES.items():
        signals = fn(prices)
        bt = engine.backtest(prices, signals)
        m = engine.performance_metrics(bt["net"], bt["positions"])
        hac = engine.hac_mean_diff(bt["net"], market_ret)
        ff5 = engine.ff5_alpha(bt["net"], ff) if ff is not None else {"ff5_alpha": None}

        rep = reported[key]
        rows.append({
            "strategy": key, "label": label,
            "cagr": m["cagr"], "sharpe": m["sharpe"], "max_dd": m["max_dd"],
            "time": m["time_in_market"], "n_trades": m["n_trades"],
            "ff5_alpha": ff5.get("ff5_alpha"),
            "hac_t": hac["t"], "hac_ann_diff": hac["ann_diff"], "hac_p": hac["p"],
            "rep_cagr": rep["cagr"], "rep_sharpe": rep["sharpe"], "rep_ff5": rep.get("ff5_alpha"),
            "rep_hac_t": hac_reported[key]["t"] if hac_reported else None,
        })
    return rows


def format_report(ftse_rows, gbp_rows) -> str:
    lines = ["# Phase 2 Validation - Dissertation vs. Re-implementation\n"]
    lines.append("Independent re-implementation from the paper's section 3.2. Tolerance: "
                 f"CAGR +/-{TOL['cagr']}pp, Sharpe +/-{TOL['sharpe']}, HAC t +/-{TOL['t']} "
                 "(FF5 alpha directional only).\n")

    for asset, rows in [("FTSE 100", ftse_rows), ("GBP/USD", gbp_rows)]:
        lines.append(f"\n## {asset}\n")
        lines.append("| Strategy | CAGR (mine/rep) | dCAGR | Sharpe (mine/rep) | dSharpe | "
                     "FF5 a (mine/rep) | HAC t (mine/rep) | Flag |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for r in rows:
            reasons = []
            dc = r["cagr"] - r["rep_cagr"] if r["rep_cagr"] is not None else None
            ds = r["sharpe"] - r["rep_sharpe"] if r["rep_sharpe"] is not None else None
            if dc is not None and abs(dc) > TOL["cagr"]:
                reasons.append("CAGR")
            if ds is not None and abs(ds) > TOL["sharpe"]:
                reasons.append("Sharpe")
            if r.get("hac_t") is not None and r.get("rep_hac_t") is not None:
                if abs(r["hac_t"] - r["rep_hac_t"]) > TOL["t"]:
                    reasons.append("HAC")
            flag = "OK" if not reasons else "DISCREPANCY: " + ",".join(reasons)

            dc_s = f"{dc:+.1f}" if dc is not None else "-"
            ds_s = f"{ds:+.2f}" if ds is not None else "-"
            rep_c = f"{r['rep_cagr']:.1f}" if r["rep_cagr"] is not None else "-"
            rep_s = f"{r['rep_sharpe']:.2f}" if r["rep_sharpe"] is not None else "-"
            ff5_mine = f"{r['ff5_alpha']:.1f}" if r.get("ff5_alpha") is not None else "-"
            ff5_rep = f"{r['rep_ff5']:.1f}" if r.get("rep_ff5") is not None else "-"
            hac_mine = f"{r['hac_t']:.2f}" if r.get("hac_t") is not None else "-"
            hac_rep = f"{r['rep_hac_t']:.2f}" if r.get("rep_hac_t") is not None else "-"
            lines.append(
                f"| {r['label']} | {r['cagr']:.1f}/{rep_c} | {dc_s} | "
                f"{r['sharpe']:.2f}/{rep_s} | {ds_s} | {ff5_mine}/{ff5_rep} | {hac_mine}/{hac_rep} | {flag} |"
            )
    return "\n".join(lines) + "\n"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows console is cp1252 by default
    except Exception:  # noqa: BLE001
        pass
    print("=" * 60)
    print("PHASE 2: RE-IMPLEMENT & VALIDATE")
    print("=" * 60)
    ff = ff_factors.get_ff5()

    ftse_rows = run_asset("FTSE100", config.TICKERS["FTSE100"], TABLE1_FTSE, TABLE3_HAC_FTSE, ff)
    gbp_rows = run_asset("GBPUSD", config.TICKERS["GBPUSD"], TABLE2_GBPUSD, None, ff)

    report = format_report(ftse_rows, gbp_rows)
    out = config.PROJECT_ROOT / "reports" / "phase2_validation.md"
    out.write_text(report, encoding="utf-8")

    print(report)
    print(f"Report written to {out.relative_to(config.PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
