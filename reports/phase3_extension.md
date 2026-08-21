# Phase 3 — Extension, Robustness & Walk-forward Regimes

Extension window: after 2025-08-31 to 2026-07-30 (~11 months). Directional only — too short for statistical significance; no HAC claims are made on this window.


## Verdict (directional)

1. **Persistence:** the FTSE 100 Contrarian Bollinger edge **did NOT persist** in the extension — -1.5% cumulative vs the market's +21.6% over ~11 months. This is consistent with the dissertation's alpha-decay thesis, but the window is far too short to be conclusive.
2. **Robustness:** on the original sample the edge is positive across almost the entire window x k grid (below), so it is **not a knife-edge artefact of the exact (20, 2σ) choice** — support for the original result.
3. **Walk-forward regimes:** with look-ahead removed the high-vol premium **attenuates but survives** — +13.1% vs +6.1% low-vol (dissertation full-sample label: 15.8% high-vol).

## Data drift check (new pull vs frozen Phase 2 snapshot, original window)

- **FTSE100** vs `FTSE100_VUKE.L_20260730.csv` (2693 overlapping days): max |Δ| 0.000%, mean |Δ| 0.0000%.
- **GBPUSD** vs `GBPUSD_GBPUSD-X_20260730.csv` (2776 overlapping days): max |Δ| 0.000%, mean |Δ| 0.0000%.

*(Drift is ~0 because the extension pull happened the same day as the Phase 2 snapshot, so Yahoo returned identical history. A re-pull months later could differ — the check is wired in for that case.)*

## 1. Persistence — strategy performance in the extension window

> **Directional, not significant.** The annualised CAGR and Sharpe below are extrapolations from ~230 trading days (~11 months) and must NOT be read as expected annual performance — **cumulative return is the honest primary figure.** No statistical significance is claimed on this window.


**FTSE100**

| Strategy | Cumulative | CAGR (extrapolated*) | Sharpe (extrapolated*) | Max DD | Time% |
|---|---|---|---|---|---|
| Market (buy & hold) | +21.6% | +23.7% | +2.04 | -8.7% | 100.0 |
| Momentum SMA | +21.6% | +23.7% | +2.04 | -8.7% | 100.0 |
| Momentum EMA | +5.2% | +5.7% | +0.49 | -17.0% | 100.0 |
| Momentum Breakout | -1.2% | -1.3% | -1.50 | -1.2% | 1.7 |
| Momentum Lookback | +10.7% | +11.7% | +1.19 | -12.2% | 80.1 |
| Contrarian RSI | +0.0% | +0.0% | +0.00 | 0.0% | 0.0 |
| Contrarian Bollinger | -1.5% | -1.6% | -0.21 | -11.1% | 47.6 |
| Contrarian Reversal | +0.6% | +0.7% | +0.35 | -0.6% | 1.3 |

**GBPUSD**

| Strategy | Cumulative | CAGR (extrapolated*) | Sharpe (extrapolated*) | Max DD | Time% |
|---|---|---|---|---|---|
| Market (buy & hold) | -1.0% | -1.0% | -0.15 | -4.8% | 100.0 |
| Momentum SMA | -8.0% | -8.4% | -1.25 | -10.8% | 100.0 |
| Momentum EMA | -2.8% | -2.9% | -0.43 | -4.6% | 100.0 |
| Momentum Breakout | -1.2% | -1.3% | -1.98 | -1.2% | 2.5 |
| Momentum Lookback | -6.4% | -6.8% | -2.04 | -6.8% | 21.5 |
| Contrarian RSI | +0.0% | +0.0% | +0.00 | 0.0% | 0.0 |
| Contrarian Bollinger | +5.5% | +5.8% | +1.14 | -3.4% | 64.6 |
| Contrarian Reversal | +0.0% | +0.0% | +0.00 | 0.0% | 0.0 |

## 2. Robustness — Contrarian Bollinger on the original sample (CAGR / Sharpe)

FTSE 100, full original sample. Tests whether the edge depends on the exact (20, 2σ) choice.

| | k 1.5 | k 2.0 | k 2.5 |
|---|---|---|---|
| **win 10** | 2.7% / 0.21 | 2.6% / 0.24 | -0.4% / -0.05 |
| **win 15** | 6.4% / 0.51 | 7.9% / 0.70 | 3.4% / 0.37 |
| **win 20** | 5.3% / 0.42 | 7.4% / 0.67 | 5.0% / 0.54 |
| **win 30** | 5.7% / 0.44 | 6.7% / 0.56 | 4.6% / 0.45 |
| **win 40** | 6.0% / 0.45 | 3.7% / 0.30 | 3.8% / 0.34 |

Original dissertation setting is (win 20, k 2.0).


## 3. Walk-forward Markov regime split — look-ahead removed (FTSE Bollinger)

- Labelled days: 2187 (first 505 unlabelled — no prior window; not back-filled).
- High-vol share of labelled days: **15.5%** (dissertation full-sample labels: 16.5%).
- Bollinger return, **high-vol regime: +13.1%** annualised [n=339] vs **low-vol: +6.1%** [n=1847].
- Dissertation (full-sample labels) reported 15.8% in the high-vol state. Any attenuation here is the effect of removing the look-ahead.

