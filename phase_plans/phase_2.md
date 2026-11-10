# Phase 2 – Re-implement & Validate

Plan agreed before build. Sits under the standing rules and overview in `Extension_Build_Plan.md`.

## Goal
Re-implement the 7 strategies independently from the dissertation's written methodology, backtest over the original window (2015-01-01 → 2025-08-31), and validate against the dissertation's reported figures within tolerance.
**Done when:** a validation table shows dissertation vs. re-implemented for every strategy, each figure flagged in/out of tolerance, and any gap investigated – never tuned away.

## Decisions locked in
- **Independence:** build purely from the paper's prose. Where the paper is silent/ambiguous, make a reasonable, documented assumption and flag it. **Do not consult the original dissertation code while implementing** – only open it afterward to *diagnose* an out-of-tolerance result, never to silently match it.
- **Validation gate:** dissertation Tables 1–3 (FTSE full-sample perf, GBP/USD full-sample perf, HAC significance). Regime / sub-period / event-study replication deferred to Phase 3.
- **Tolerance (match = within):** CAGR ±1pp, Sharpe ±0.1, HAC t-stat ±0.3.
- **Must replicate exactly (within tolerance):** Contrarian Bollinger CAGR (~7.6%) and Sharpe (~0.69); and the qualitative ranking (contrarian beats momentum, Bollinger is the standout).
- **Directional-is-fine:** FF5 alpha decay (~10.4% → ~1.9%) – direction and rough scale matter more than exact figures.

## Strategy rules (from §3.2 of the paper)
- Momentum SMA – 50/200-day SMA crossover
- Momentum EMA – 12/26-day EMA crossover
- Momentum Breakout – price vs 20-day high ± 2σ recent vol
- Momentum Lookback – trailing 60-day return, long >+2% / short <−2%
- Contrarian Bollinger – enter at ±2σ bands, exit at 20-day SMA
- Contrarian RSI – 14-day RSI vs dynamic 30+(0.5×vol) threshold, filtered by 200-day SMA
- Contrarian Reversal – prior 5-day return <−5% / >+5%, hold 3 days

## What gets built
- `strategies/` – one documented signal function per strategy.
- `backtest/` – one engine: next-day execution (signal at close t → position t+1), daily P&L = position × return, 0.04% round-trip cost on turnover, reading from the committed snapshot.
- Metrics: CAGR, Sharpe, max drawdown, win rate (active days), time in market; CAPM alpha + HAC (Newey-West, 5-lag) t-stats for strategy-vs-market.
- `reports/` – the dissertation-vs-mine validation table.

## New dependencies / data
- Adds `statsmodels` (HAC regressions).
- Pulls the Fama-French European 5-factor daily series (Ken French library, free), snapshotted like the price data.

## Anticipated discrepancies (honest heads-up, not bugs to hide)
- Thin-sample reported figures (Contrarian RSI: 0.2% time in market, 100% win rate; Breakout: 2% time) are fragile and may not replicate cleanly – a legitimate robustness finding if so.
- Market buy-and-hold (7.2% CAGR / 0.46 Sharpe on FTSE) used as a first sanity anchor before judging any strategy.

## Gate
Stop after Phase 2 for review before touching Phase 3.
