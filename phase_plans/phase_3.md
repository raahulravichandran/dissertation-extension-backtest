# Phase 3 – Extend & Stress-test

Plan agreed before build. Sits under the standing rules and overview in `Extension_Build_Plan.md`.

## Goal
Run the validated strategies on data since the dissertation ended, stress-test the headline result against parameter choices, and redo the Markov regime analysis without look-ahead.
**Done when:** a persistence verdict on the Contrarian Bollinger edge, a robustness table, and a walk-forward regime result exist in `reports/`, all honestly caveated.

## Decisions locked in
- **Extension data:** pull a fresh 2015→today snapshot (needed for 200-day warm-up into the extension), evaluate only the **Sept 2025 → today** slice (~11 months, ~230 trading days). Keep the Phase 2 snapshot frozen as the validated original; report overlap drift between the two as a mini re-validation.
- **Scope:** (1) extension persistence, (2) Bollinger parameter robustness, (3) walk-forward Markov + the one regime split it enables. **Deferred:** event-study replication (FOMC/Trump/BoE CARs) and full sub-period / other-regime tables.
- **Robustness grid:** Contrarian Bollinger window ∈ {10,15,20,30,40} × band k ∈ {1.5,2.0,2.5}, on the original sample.
- **Walk-forward Markov:** expanding window, ≥500-obs minimum, annual refit, filtered probabilities.

## Statistical honesty (committed up front)
- ~230 trading days is far too short for a significant Sharpe. Report **cumulative return + equity curve** as primary; annualised CAGR/Sharpe only with a loud "directional, not significant" caveat; **no HAC significance claims** on the extension window.
- "Inconclusive over 11 months" is a legitimate, expected outcome – not a failure.
- FF5 for the extension is out of scope (Ken French publication lag + focus); extension uses raw performance and comparison to the market buy-and-hold.

## Walk-forward Markov – both look-ahead channels past-only
The dissertation's regime labels used full-sample estimation (look-ahead). This phase removes it on **both** channels:
1. **Parameter channel:** at each annual refit date r, estimate the 2-state (switching-variance) model by MLE on the expanding window up to r only.
2. **Inference channel:** apply those fixed parameters forward and take **filtered** (one-sided) probabilities – P(regime | data up to and including t) – never smoothed (which conditions on the full sample).
Each day d in the forward interval (r, next refit] is labelled using filtered prob with data ≤ d and parameters fit on data ≤ r < d – strictly past-only on both channels. This improves on the original walk-forward helper, which labelled each block using parameters fit at the block's *end* (a bounded parameter-channel leak).
- **Excluded days:** the first ~500 observations (no prior window to fit on) are left unlabelled, not back-filled – back-filling would reintroduce look-ahead.
- Then re-compute the Bollinger high-vol vs low-vol return split under these honest labels and compare to the dissertation's full-sample-label figure (15.8% high-vol). Expectation: the premium likely attenuates.

## What gets built
- `regimes.py` – walk-forward Markov (both channels past-only).
- `run_phase3.py` – orchestrator: extension pull+snapshot, drift check, persistence, robustness grid, walk-forward regime split.
- `reports/phase3_extension.md` – persistence verdict + robustness table + walk-forward regime result.

## Gate
Stop after Phase 3 for review before touching Phase 4.
