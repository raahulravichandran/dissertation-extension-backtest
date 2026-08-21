# Phase 7 — Portfolio-construction capability demonstration

**Verdict (read this first):** This is a **portfolio-construction capability demonstration, not an investment system and not a tradable portfolio.** It applies standard portfolio methodology (inverse-volatility sizing, portfolio-level risk reporting) to the Contrarian Bollinger strategy — a signal this project has **already shown does not work live**: it did **not** persist out-of-sample on the FTSE 100 index (Phase 3: −1.5% vs the market's +21.6% in the ~11 months after Aug 2025) and did **not** generalise to individual stocks (Phase 6: 0/8 HAC-significant, raw or Bonferroni). Every number below is therefore **in-sample and inherits that null result** — the point is to show I can *build and risk-assess a multi-asset portfolio*, not that this portfolio should be traded. On the 2015–Aug 2025 window the inverse-vol portfolio returned 62.9% cumulative (4.7% CAGR, 8.7% vol, Sharpe 0.54, max drawdown -18.8%, ~52% average capital deployed) versus the equal-weight buy-and-hold of the same eight names at 60.5% cumulative (4.6% CAGR, 15.0% vol, Sharpe 0.30, max drawdown -27.5%). The portfolio's mean daily return is **not** statistically distinguishable from that benchmark (HAC t = -0.13, p = 0.894). **No investment advice is implied; do not trade this.**


## What this phase is (and is not)

- **Is:** a demonstration that I can construct a multi-asset portfolio (position sizing, portfolio-level risk, correlation, drawdown) — a core asset-management / quant skill.
- **Is not:** a claim that this portfolio is tradable. The underlying signal failed out-of-sample (Phase 3) and failed to generalise (Phase 6). The construction *methodology* is the deliverable; the strategy is a vehicle for demonstrating it, chosen because it is already validated as *not working live* — so no reader can mistake it for a recommendation.

## Scope and method

- **Universe:** eight FTSE 100 single-name Contrarian Bollinger sleeves (the Phase 6 set), one per sector. VUKE.L is **excluded** as a sleeve — the index contains these names, so including it would double-count and corrupt the correlation matrix; it appears in Phase 6 as reference only.
- **Sample:** 2015-01-01 → 2025-08-31 (original dissertation window; **in-sample** — the Phase 3 out-of-sample non-persistence caveat is inherited in full).
- **Sizing rule (one, deliberately):** **inverse-volatility weighting** — each sleeve weighted ∝ 1 / (trailing 20-day realised volatility of the underlying asset), normalised to sum to 1. Chosen because it *demonstrates risk-based sizing* (size to risk), the transferable skill this phase is about; equal-weight — the alternative **not** used — is simpler but ignores that the jumpier names (energy, telecom) then silently dominate portfolio risk.
- **No look-ahead:** weights are formed from *trailing* volatility only and applied one day forward (a weight set on the close of day *t* governs the return over *t+1*). This directly answers the markers' full-sample look-ahead critique — the weights never see future data.
- **Benchmark:** equal-weight **buy-and-hold** of the same eight names (1/8 each at the start, left to drift; no rebalancing).
- **Costs:** each sleeve already bears the dissertation's 0.04% round-trip cost on its own signal turnover; the *additional* turnover from daily weight rebalancing is **not** charged (noted as a limitation).

## Portfolio-level results

| Metric | Inverse-vol portfolio | Equal-weight buy & hold |
|---|---|---|
| Cumulative return | 62.9% | 60.5% |
| CAGR | 4.7% | 4.6% |
| Annualised volatility | 8.7% | 15.0% |
| Sharpe | 0.54 | 0.30 |
| Max drawdown | -18.8% | -27.5% |
| Avg. capital deployed (time in market) | 52.2% | 100% |

**Portfolio vs benchmark (HAC mean-diff, Newey–West 5-lag):** annualised difference -0.6%, t = -0.13, p = 0.894 — **not statistically distinguishable** from equal-weight buy-and-hold.

> **Read the Sharpe honestly.** The portfolio's higher Sharpe and shallower drawdown versus buy-and-hold are **mechanical, not alpha**: it sits in cash ~48% of the time and inverse-vol deliberately shrinks the most volatile sleeves, so of course realised volatility and drawdown fall. The *return* itself is statistically indistinguishable from the benchmark (above), and the underlying signal failed out-of-sample. Lower risk from holding cash and sizing down is a property of the construction, **not** evidence the strategy works.

### Average realised sleeve weights

Inverse-vol tilts capital toward the lower-volatility names, as intended:

| Sleeve | Sector | Avg. weight |
|---|---|---|
| Unilever | Consumer staples | 15.4% |
| RELX | Business services | 15.1% |
| National Grid | Utilities | 14.7% |
| HSBC | Financials | 12.4% |
| AstraZeneca | Healthcare | 12.0% |
| BP | Energy | 10.5% |
| BT Group | Telecom | 10.2% |
| Rio Tinto | Materials | 9.6% |

### Correlation matrix of the eight sleeve return streams

| | HSBA | AZN | ULVR | BP | RIO | REL | NG | BT |
|---|---|---|---|---|---|---|---|---|
| **HSBA** | 1.00 | 0.10 | 0.10 | 0.24 | 0.14 | 0.08 | 0.06 | 0.13 |
| **AZN** | 0.10 | 1.00 | 0.16 | 0.09 | 0.04 | 0.13 | 0.09 | 0.01 |
| **ULVR** | 0.10 | 0.16 | 1.00 | 0.15 | 0.07 | 0.17 | 0.18 | 0.13 |
| **BP** | 0.24 | 0.09 | 0.15 | 1.00 | 0.21 | 0.19 | 0.09 | 0.16 |
| **RIO** | 0.14 | 0.04 | 0.07 | 0.21 | 1.00 | 0.15 | 0.08 | 0.14 |
| **REL** | 0.08 | 0.13 | 0.17 | 0.19 | 0.15 | 1.00 | 0.19 | 0.13 |
| **NG** | 0.06 | 0.09 | 0.18 | 0.09 | 0.08 | 0.19 | 1.00 | 0.16 |
| **BT** | 0.13 | 0.01 | 0.13 | 0.16 | 0.14 | 0.13 | 0.16 | 1.00 |

**Correlation instability (evidence, not assertion):** mean pairwise sleeve correlation is 0.13 over the full window, but 0.21 in the first half versus 0.04 in the second — the correlation structure *shifts within the very sample it is estimated on*. Any diversification benefit read off the matrix above is therefore not something to rely on out-of-sample.

## Limitations

1. **Inherited null result (dominant).** The underlying Contrarian Bollinger signal did not persist out-of-sample (Phase 3) and did not generalise across stocks (Phase 6). No portfolio wrapper can rescue a signal that does not work live; every figure here is in-sample and must not be read as a tradable result.
2. **Correlation instability.** As shown above, the correlations that drive any diversification claim are not stable even within the sample, let alone out of it. In-sample correlation (and covariance) is a weak guide to future co-movement — the classic reason naive optimisation disappoints live.
3. **Weight instability / estimation risk.** The inverse-vol weights are themselves estimated from trailing realised volatility, which is noisy and regime-dependent; the average weights shown are not stable targets.
4. **Single sizing rule by design.** One rule (inverse-vol) is shown, not a menu. Mean-variance / Markowitz optimisation and an efficient frontier are deliberately out of scope — a much larger undertaking, and one that would over-fit in-sample covariance here to little end.
5. **Rebalancing costs not modelled.** Only each sleeve's own signal turnover bears the 0.04% cost; the daily turnover from re-weighting is uncosted, so the portfolio return is modestly optimistic.
6. **Survivorship bias.** The eight names are current FTSE 100 constituents; delisted/removed names are excluded.
7. **Research only.** Simulated historical performance on a strategy shown not to work live — not advice to buy or sell any security, and not a portfolio to trade.

