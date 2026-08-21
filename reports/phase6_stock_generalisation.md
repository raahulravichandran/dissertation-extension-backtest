# Phase 6 — Stock-level Bollinger generalisation check

**Verdict (read this first):** This is a **mechanism check only**, not evidence of a tradable edge. Phase 3 showed the Contrarian Bollinger strategy **did not persist** on the FTSE 100 index out-of-sample (−1.5% cumulative vs the market's +21.6% over ~11 months after Aug 2025), so any in-sample stock-level numbers below must **not** be read as actionable signals or portfolio inputs. **Even on the index itself (VUKE.L), the strategy was not HAC-significant vs buy-and-hold in Phase 2** (t = -0.09, p = 0.931) — its apparent value was always in the **risk-adjusted return and reduced time-in-market** (Sharpe 0.67 vs 0.46 buy-and-hold; ~44% invested), not in statistically beating passive exposure. On the original sample (2015–Aug 2025), results are **mixed and inconclusive** as a cross-sectional generalisation test: 5/8 stocks show positive strategy CAGR, 3/8 beat their own buy-and-hold, 0/8 are HAC-significant at α=0.05 (raw), and **0/8 survive Bonferroni correction** (α/8 ≈ 0.00625). The index delivered ~7.4% Bollinger CAGR on VUKE.L; the stock range here spans BP (-3.5%) to Unilever (10.3%). Survivorship bias applies (current FTSE 100 members only). **No investment advice is implied.**

## Scope and method

- **Question:** does the Contrarian Bollinger edge validated on VUKE.L (Phase 2) appear on individual FTSE 100 constituents, or was it index-specific?
- **Sample:** 2015-01-01 → 2025-08-31 (original dissertation window; not the Phase 3 extension).
- **Strategy:** Contrarian Bollinger (20-day window, 2σ bands, exit at SMA) — exact Phase 2/3 parameters.
- **Benchmark:** each stock's own buy-and-hold (HAC mean-diff test, Newey-West 5-lag).
- **Multiple testing:** 8 stocks tested; Bonferroni threshold p < 0.00625 (α=0.05/8).
- **Survivorship:** names are current FTSE 100 constituents; delisted or removed constituents are excluded.
- **Phase 3 context:** index-level edge did **not** persist OOS; stock results are in-sample mechanism checks only.



## Results


| Stock                | Sector            | Mkt CAGR | Bollinger CAGR | Sharpe | Time% | HAC t | HAC p | Sig (raw) | Sig (Bonf.) |
| -------------------- | ----------------- | -------- | -------------- | ------ | ----- | ----- | ----- | --------- | ----------- |
| HSBC (HSBA.L)        | Financials        | 4.2%     | -1.7%          | -0.09  | 50.4  | -0.83 | 0.406 | N         | N           |
| AstraZeneca (AZN.L)  | Healthcare        | 9.3%     | 8.0%           | 0.46   | 54.8  | -0.30 | 0.768 | N         | N           |
| Unilever (ULVR.L)    | Consumer staples  | 5.6%     | 10.3%          | 0.73   | 50.0  | 0.47  | 0.640 | N         | N           |
| BP (BP.L)            | Energy            | 0.5%     | -3.5%          | -0.15  | 51.3  | -0.59 | 0.556 | N         | N           |
| Rio Tinto (RIO.L)    | Materials         | 4.3%     | 2.5%           | 0.11   | 53.4  | -0.35 | 0.730 | N         | N           |
| RELX (REL.L)         | Business services | 11.4%    | 3.5%           | 0.25   | 53.5  | -1.27 | 0.203 | N         | N           |
| National Grid (NG.L) | Utilities         | 0.5%     | 3.0%           | 0.20   | 50.1  | 0.19  | 0.846 | N         | N           |
| BT Group (BT-A.L)    | Telecom           | -5.6%    | -0.2%          | -0.01  | 54.4  | 0.31  | 0.760 | N         | N           |


**Index reference (Phase 2, VUKE.L):** Bollinger CAGR 7.4%, Sharpe 0.67, HAC t -0.09 (p=0.931) — not HAC-significant vs buy-and-hold on the index either.

## Limitations

1. **Not tradable evidence** — Phase 3 index non-persistence dominates interpretation.
2. **Multiple testing / selection** — eight parallel tests; Bonferroni is conservative but appropriate for a pre-specified cross-section.
3. **Survivorship bias** — only stocks still in the FTSE 100 as of the pull date.
4. **Single-name vs ETF** — idiosyncratic risk, corporate actions, and spreads differ from the VUKE.L proxy; costs held at dissertation assumptions (0.04% round-trip).
5. **Research only** — findings describe historical simulated performance, not recommendations to buy or sell any security.

