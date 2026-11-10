# Phase 6 – Stock-level generalisation check (optional, bounded)

Plan agreed before build. The standing rules in `Extension_Build_Plan.md` apply in full.

## Goal

Test whether the validated Contrarian Bollinger Band edge (20-day, 2σ, exit at SMA) generalises
from the FTSE 100 index (VUKE.L) to individual FTSE 100 constituents – a mechanism check, not
evidence of a tradable edge (Phase 3 found the index edge did not persist out-of-sample).

**Done when:** `reports/phase6_stock_generalisation.md` contains a verdict paragraph (leading with
the mechanism-check framing), a results table, Bonferroni-adjusted significance, and explicit
cross-reference to Phase 3 non-persistence.

## Decisions locked in

- **Stocks (8):** HSBA.L, AZN.L, ULVR.L, BP.L, RIO.L, REL.L, NG.L, BT-A.L – diverse sectors and
  cap tiers; SHEL.L excluded (RDS/RDSB → SHEL restructuring complicates 2015–2025 history).
- **Sample:** original dissertation window only (`2015-01-01` → `2025-08-31`); same costs and
  next-day execution as Phases 2–3.
- **Strategy:** `contrarian_bollinger(window=20, k=2.0)` only – no parameter search.
- **Metrics:** CAGR, Sharpe, HAC mean-diff vs each stock's own buy-and-hold (Newey-West, 5-lag).
- **Multiple testing:** 8 stocks ⇒ Bonferroni threshold α/8 ≈ 0.00625; report raw and adjusted.
- **Survivorship:** current FTSE 100 members only; delisted names excluded – flagged honestly.
- **Framing:** research results only; not investment advice or trade recommendations.

## Explicitly out of scope

Portfolio weighting, additional strategies, other asset classes, live trading, OOS extension on
stocks, new backtest infrastructure.

## What gets built

- `run_phase6.py` – download/snapshot stocks via existing pipeline; backtest Bollinger; write report.
- `reports/phase6_stock_generalisation.md` – verdict-first report with table and caveats.
