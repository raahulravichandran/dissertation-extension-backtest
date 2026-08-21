# Phase 3b — Regime-Parameter Sensitivity (FTSE 100 Contrarian Bollinger)

Closes the Phase 3 gap: the robustness grid varied the Bollinger strategy's own parameters; these two checks vary the regime-classification parameters the second marker specifically flagged. Original sample; returns annualised arithmetically (daily mean × 252); regime labels lagged one day.


## 1. Volatility-state window {10, 20, 40 days}

High/low vol = N-day annualised rolling std above/below the full-sample median (the dissertation's definition). Question: does the high-vol premium depend on N=20?

| Window | High-vol ann. | Low-vol ann. | Spread (high−low) | n high/low |
|---|---|---|---|---|
| 10d | +11.7% | +3.9% | +7.8pp | 1341/1351 |
| 20d | +10.6% | +5.0% | +5.6pp | 1336/1356 |
| 40d | +10.2% | +5.4% | +4.8pp | 1326/1366 |

*Dissertation (20-day, Table 5): high-vol 10.8% vs low-vol 5.3%.*


## 2. Bank Rate threshold {0.5%, 1%, 2%}

Low-rate = Bank Rate ≤ threshold. Question: does the low-rate outperformance depend on the exact 1% cut?

| Threshold | Low-rate ann. | High-rate ann. | Spread (low−high) | n low/high |
|---|---|---|---|---|
| 0.5% | +11.1% | +4.1% | +7.0pp | 1416/1276 |
| 1.0% | +9.2% | +4.4% | +4.8pp | 1883/809 |
| 2.0% | +9.8% | +2.5% | +7.2pp | 1951/741 |

*Dissertation (1% split, Table 5): low-rate 9.4% vs high-rate 4.6%.*


## Verdict

- **Vol-state window:** high-vol premium is positive across all three windows (+4.8 to +7.8pp) — the finding does not hinge on choosing 20 days.
- **Bank Rate threshold:** low-rate outperformance is positive across all three thresholds (+4.8 to +7.2pp) — the finding does not hinge on the exact 1% cut.
