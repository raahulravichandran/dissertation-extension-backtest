# Phase 3b — Regime-Parameter Sensitivity (closing Phase 3 scope)

Closes the specific gap the markers flagged that the Phase 3 robustness grid did
NOT cover: the grid varied the Bollinger strategy's own parameters (band window,
band k), not the two regime-classification parameters the second marker named.
Strictly two checks — nothing broader.

## The two checks (FTSE 100 Contrarian Bollinger, original sample)
1. **Volatility-state window ∈ {10, 20, 40} days.** Classify days high/low vol by
   whether the N-day annualised rolling std is above/below the full-sample median
   (the dissertation's definition; median kept full-sample to match it — this check
   is about window choice, not the look-ahead, which Phase 3's Markov work handled).
   Show the high-vol vs low-vol Bollinger return spread is stable across N.
2. **Bank Rate threshold ∈ {0.5%, 1%, 2%}.** Split Bollinger returns into
   low-rate (≤ threshold) vs high-rate (> threshold). Show the spread is stable
   across thresholds — i.e. the finding is not an artefact of the exact 1% cut.

Both regime labels lagged one day (past-only) before conditioning returns.
Returns annualised arithmetically (daily mean × 252), matching the dissertation's
Table 5.

## Bank Rate data — fully static, no API, no key
`data/boe_bank_rate.csv`: the Bank of England official Bank Rate step series
(public record), effective date → rate, committed once. The code only ever reads
this CSV — no live fetch, no FRED, no key (not even via env-var). Tail beyond
2025-05 is immaterial to the {0.5,1,2}% thresholds (rate is >2% throughout).

## What gets built
- `data/boe_bank_rate.csv` — static Bank Rate snapshot.
- `run_phase3b.py` — the two sensitivity checks.
- `reports/phase3b_sensitivity.md` — the two tables + verdict vs the dissertation.

## Gate
Stop after Phase 3b for review before Phase 4.
