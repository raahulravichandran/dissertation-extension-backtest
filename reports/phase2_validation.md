# Phase 2 Validation - Dissertation vs. Re-implementation

Independent re-implementation from the paper's section 3.2. Tolerance: CAGR +/-1.0pp, Sharpe +/-0.1, HAC t +/-0.3 (FF5 alpha directional only).


## FTSE 100

| Strategy | CAGR (mine/rep) | dCAGR | Sharpe (mine/rep) | dSharpe | FF5 a (mine/rep) | HAC t (mine/rep) | Flag |
|---|---|---|---|---|---|---|---|
| Market (buy & hold) | 7.2/7.2 | -0.0 | 0.46/0.46 | -0.00 | -/- | -/- | OK |
| Momentum SMA | -4.5/-4.5 | +0.0 | -0.30/-0.30 | -0.00 | -5.8/-5.8 | -2.22/-2.21 | OK |
| Momentum EMA | -12.0/-11.8 | -0.2 | -0.77/-0.76 | -0.01 | -12.1/-11.9 | -2.62/-2.59 | OK |
| Momentum Breakout | -0.4/-0.3 | -0.1 | -0.12/-0.09 | -0.03 | -2.2/-2.1 | -1.80/-1.78 | OK |
| Momentum Lookback | -8.6/-8.3 | -0.3 | -0.63/-0.60 | -0.03 | -8.7/-8.4 | -2.38/-2.33 | OK |
| Contrarian RSI | 0.4/0.4 | -0.0 | 0.63/0.64 | -0.01 | -1.5/-1.5 | -1.66/-1.66 | OK |
| Contrarian Bollinger | 7.4/7.6 | -0.2 | 0.67/0.69 | -0.02 | 4.6/4.8 | -0.09/-0.04 | OK |
| Contrarian Reversal | -0.2/-0.1 | -0.1 | -0.02/-0.02 | -0.00 | -2.1/-2.0 | -1.73/-1.72 | OK |

## GBP/USD

| Strategy | CAGR (mine/rep) | dCAGR | Sharpe (mine/rep) | dSharpe | FF5 a (mine/rep) | HAC t (mine/rep) | Flag |
|---|---|---|---|---|---|---|---|
| Market (buy & hold) | -1.3/-1.3 | +0.0 | -0.14/-0.14 | +0.00 | -/- | -/- | OK |
| Momentum SMA | -0.1/-0.1 | +0.0 | -0.01/-0.01 | +0.00 | -1.5/-1.5 | 0.28/- | OK |
| Momentum EMA | -2.5/-2.3 | -0.2 | -0.27/-0.25 | -0.02 | -3.9/-3.7 | -0.28/- | OK |
| Momentum Breakout | -0.1/-0.1 | -0.0 | -0.12/-0.05 | -0.07 | -2.0/-1.9 | 0.25/- | OK |
| Momentum Lookback | 0.8/1.0 | -0.2 | 0.10/0.13 | -0.03 | -0.7/-0.5 | 0.47/- | OK |
| Contrarian RSI | -0.1/-0.1 | +0.0 | -0.37/-0.33 | -0.04 | -1.9/-1.9 | 0.29/- | OK |
| Contrarian Bollinger | 1.6/1.8 | -0.2 | 0.24/0.27 | -0.03 | -0.3/-0.1 | 0.86/- | OK |
| Contrarian Reversal | -0.2/-0.1 | -0.1 | -0.06/-0.06 | -0.00 | -2.1/-2.1 | 0.28/- | OK |
