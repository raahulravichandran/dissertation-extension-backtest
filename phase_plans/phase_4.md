# Phase 4 — Minimal Live Signal

Plan agreed before build. Sits under the standing rules in `CLAUDE.md` and the overview in `Extension_Build_Plan.md`.

## Goal
One command that computes the FTSE 100 Contrarian Bollinger signal from the latest
data, prints today's recommended position, and appends one row to a log.
**Done when:** `python live_signal.py` prints the current signal and appends to
`logs/signal_log.csv`. Stop there.

## Hard scope line (do not cross)
One script + one log. **No** hypothetical P&L / performance track record, **no**
backfilled history, **no** additional strategies or assets, **no** dashboard, **no**
scheduling or automation. After this, move to Phase 5.

## No real money — the whole point of the phase
Signal calculator only. No broker connection, no order object, no capital anywhere.
Every printout and the log header carries: "SIMULATED / PAPER SIGNAL — NO REAL
MONEY, NO BROKER, NOT INVESTMENT ADVICE."

## Honest framing built in
Phase 3 showed the Bollinger edge did not persist out-of-sample. The output states
this is a **capability demonstration** (real-time signal pipeline), not a trading
recommendation.

## What gets built
- `live_signal.py` — on each run: fresh yfinance pull (2015→today; a live signal
  needs current data — signal-only, never an order), run the stateful Bollinger
  rule, take the latest state, print a labelled block, append one log row.
- `logs/signal_log.csv` — columns: `run_timestamp, data_as_of, last_price, sma,
  upper, lower, signal, position, vol_regime`. The `vol_regime` column is
  informational only (current 20-day realised vol vs trailing median — a simple
  indicator, not the walk-forward Markov), no gating of the signal.

## Timing convention (stated in output)
Next-day execution: signal as of close of `data_as_of` → position to hold the next
trading day.

## Gate
Stop after Phase 4 for review before Phase 5.
