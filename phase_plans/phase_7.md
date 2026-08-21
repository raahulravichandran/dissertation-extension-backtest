# Phase 7 — Portfolio-construction capability demonstration (bounded)

Plan agreed before build. Standing rules in `CLAUDE.md` apply in full.

## Goal

Demonstrate multi-asset portfolio-construction capability — position sizing, portfolio-level
risk, correlation, drawdown — applied to the Contrarian Bollinger strategy. This is a
**capability demonstration, NOT an investment system.** The signal already failed out-of-sample
(Phase 3) and failed to generalise to single names (Phase 6), so the portfolio layer demonstrates
*methodology on a strategy shown not to work live* and is never a tradable recommendation. The
null result is inherited and foregrounded throughout.

**Done when:** `reports/phase7_portfolio.md` leads with the capability framing + null-result caveat,
then reports one justified sizing rule and portfolio-level return, vol, Sharpe, correlation matrix,
and max drawdown, then an honest limitations section (correlation instability, inherited null,
single-rule simplification). Plus `run_phase7.py` reproduces it from committed snapshots.

## Decisions locked in

- **Universe:** the 8 Phase-6 single-name Bollinger sleeves (HSBA, AZN, ULVR, BP, RIO, REL, NG, BT),
  one per sector. **VUKE.L excluded as a sleeve** — the index contains these names, so including it
  would double-count and corrupt the correlation matrix; it stays reference-only (Phase 6).
- **Sample:** original window `2015-01-01` → `2025-08-31`; **in-sample**, Phase 3 OOS caveat inherited.
- **Sizing rule (one):** **inverse-volatility** — weight ∝ 1 / (trailing 20-day realised vol of the
  underlying asset), normalised to sum to 1. Chosen because it demonstrates risk-based sizing;
  equal-weight is the named alternative not used (simpler, but lets volatile names dominate risk).
- **No look-ahead:** weights from trailing vol only, applied one day forward (weight set at close of
  *t* governs return over *t+1*). Reuses the project's justified 20-day rolling-vol window.
- **Benchmark:** equal-weight buy-and-hold of the same 8 names (1/8 each at start, left to drift).
- **Metrics:** cumulative return, CAGR, annualised vol, Sharpe, max drawdown, portfolio time-in-market
  (avg capital deployed), correlation matrix of the 8 sleeves + empirical instability check
  (first-half vs second-half mean pairwise correlation), HAC mean-diff vs benchmark.
- **Costs:** each sleeve bears the 0.04% round-trip on its own signal turnover; extra turnover from
  daily re-weighting is NOT charged — noted as a limitation, not modelled.
- **Framing:** research only; the Sharpe/drawdown improvement is mechanical (cash + sizing down vol),
  not alpha; no claim anywhere that this portfolio should be traded.

## Explicitly out of scope

Mean-variance / Markowitz optimisation, efficient frontier, any sizing "menu", rebalancing-frequency
study, rebalancing-cost modelling beyond the flat 0.04%, leverage, shorting beyond the base strategy,
new data sources or infrastructure, any live/tradable recommendation.

## Guardrail

If the build starts needing an optimiser, a new data pipeline, or rebalancing machinery — STOP and
flag it as sprawl beyond a bounded capability demo.

## What gets built

- `run_phase7.py` — reuse committed snapshots, `engine`, `contrarian_bollinger`, and the Phase-6
  `STOCKS` universe; build inverse-vol portfolio; write report.
- `reports/phase7_portfolio.md` — verdict-first report with framing, metrics table, correlation
  matrix, and limitations.
- `INTERVIEW_NOTES.md` — add a Stage 7 section (incl. the "Would you trade this?" Q + honest "no").
