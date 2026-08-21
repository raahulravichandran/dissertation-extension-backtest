"""Reported figures from the dissertation (Tables 1, 2, 3), for validation.

These are the numbers the re-implementation is checked against. Kept in one
place so the validation report is transparent about exactly what it compares to.
Source: 12451ES32033 New.pdf, Tables 1-3.
"""

# Table 1 — FTSE 100 full sample. cagr, sharpe, max_dd, capm_alpha, ff5_alpha, ff5_r2, win, time
TABLE1_FTSE = {
    "market":               dict(cagr=7.2,  sharpe=0.46,  max_dd=-34.3, win=53.1, time=100.0),
    "momentum_sma":         dict(cagr=-4.5, sharpe=-0.30, max_dd=-63.6, capm_alpha=-4.9,  ff5_alpha=-5.8,  ff5_r2=0.047, win=52.0, time=92.6),
    "momentum_ema":         dict(cagr=-11.8,sharpe=-0.76, max_dd=-78.4, capm_alpha=-9.7,  ff5_alpha=-11.9, ff5_r2=0.049, win=48.5, time=99.9),
    "momentum_breakout":    dict(cagr=-0.3, sharpe=-0.09, max_dd=-8.9,  capm_alpha=0.1,   ff5_alpha=-2.1,  ff5_r2=0.033, win=47.2, time=2.0),
    "momentum_lookback":    dict(cagr=-8.3, sharpe=-0.60, max_dd=-67.0, capm_alpha=-6.3,  ff5_alpha=-8.4,  ff5_r2=0.044, win=49.4, time=70.3),
    "contrarian_rsi":       dict(cagr=0.4,  sharpe=0.64,  max_dd=0.0,   capm_alpha=0.4,   ff5_alpha=-1.5,  ff5_r2=0.005, win=100.0,time=0.2),
    "contrarian_bollinger": dict(cagr=7.6,  sharpe=0.69,  max_dd=-30.3, capm_alpha=5.7,   ff5_alpha=4.8,   ff5_r2=0.150, win=52.5, time=44.2),
    "contrarian_reversal":  dict(cagr=-0.1, sharpe=-0.02, max_dd=-22.1, capm_alpha=-0.5,  ff5_alpha=-2.0,  ff5_r2=0.045, win=52.1, time=5.4),
}

# Table 2 — GBP/USD full sample.
TABLE2_GBPUSD = {
    "market":               dict(cagr=-1.3, sharpe=-0.14, max_dd=-32.5, win=49.5, time=100.0),
    "momentum_sma":         dict(cagr=-0.1, sharpe=-0.01, max_dd=-27.1, capm_alpha=0.1,  ff5_alpha=-1.5, ff5_r2=0.006, win=50.3, time=92.8),
    "momentum_ema":         dict(cagr=-2.3, sharpe=-0.25, max_dd=-37.0, capm_alpha=-1.9, ff5_alpha=-3.7, ff5_r2=0.001, win=49.5, time=99.9),
    "momentum_breakout":    dict(cagr=-0.1, sharpe=-0.05, max_dd=-2.9,  capm_alpha=-0.1, ff5_alpha=-1.9, ff5_r2=0.002, win=48.8, time=1.5),
    "momentum_lookback":    dict(cagr=1.0,  sharpe=0.13,  max_dd=-16.5, capm_alpha=1.1,  ff5_alpha=-0.5, ff5_r2=0.005, win=51.3, time=60.8),
    "contrarian_rsi":       dict(cagr=-0.1, sharpe=-0.33, max_dd=-0.9,  capm_alpha=-0.1, ff5_alpha=-1.9, ff5_r2=0.001, win=25.0, time=0.3),
    "contrarian_bollinger": dict(cagr=1.8,  sharpe=0.27,  max_dd=-15.2, capm_alpha=2.0,  ff5_alpha=-0.1, ff5_r2=0.006, win=52.5, time=52.4),
    "contrarian_reversal":  dict(cagr=-0.1, sharpe=-0.06, max_dd=-11.9, capm_alpha=-0.1, ff5_alpha=-2.1, ff5_r2=0.017, win=41.2, time=1.2),
}

# Table 3 — HAC-robust tests, FTSE strategies vs buy-and-hold. ann_diff (%), t, p
TABLE3_HAC_FTSE = {
    "momentum_sma":         dict(ann_diff=-11.6, t=-2.212, p=0.027),
    "momentum_ema":         dict(ann_diff=-19.5, t=-2.591, p=0.010),
    "momentum_breakout":    dict(ann_diff=-8.4,  t=-1.779, p=0.075),
    "momentum_lookback":    dict(ann_diff=-15.9, t=-2.330, p=0.020),
    "contrarian_rsi":       dict(ann_diff=-7.8,  t=-1.655, p=0.098),
    "contrarian_bollinger": dict(ann_diff=-0.2,  t=-0.045, p=0.964),
    "contrarian_reversal":  dict(ann_diff=-8.0,  t=-1.717, p=0.086),
}

# Tolerance for a "match" (Phase 2 plan / CLAUDE.md).
TOL = {"cagr": 1.0, "sharpe": 0.1, "t": 0.3}
