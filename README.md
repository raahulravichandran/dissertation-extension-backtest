# Dissertation Extension — Momentum & Contrarian Strategies on UK Assets

A reproducible Python system that independently rebuilds and extends my undergraduate dissertation (First Class, 70%) — *"Profitability of Momentum and Contrarian Trading Strategies Under Macroeconomic Conditions"* — testing seven momentum and contrarian strategies on the FTSE 100 (via VUKE.L) and GBP/USD, 2015–2025, extended ~11 months out-of-sample to July 2026, and taken to stock level and portfolio construction.

**The headline is a negative result, reported honestly:** the one strategy that beat the market in-sample did not survive out-of-sample, and the report is explicit about what that does and does not establish. Built defensible-over-impressive: no live trading, ever — any signal is simulated and labelled as such; no broker, no capital, no orders anywhere in this project.

## Headline findings

- **Reproduction:** every headline figure reproduced within pre-registered tolerances (CAGR ±1pp, Sharpe ±0.1, HAC t ±0.3) on a fresh data pull; market anchor matched exactly (7.2% CAGR, 0.46 Sharpe). Re-implementation deltas ran uniformly slightly *worse* than the original — consistent with vendor data revisions, and the opposite direction to what look-ahead bias would cause.
- **Momentum failed structurally** on the FTSE 100: all four momentum strategies negative; three significantly underperformed buy-and-hold (HAC-robust).
- **The in-sample edge:** Contrarian Bollinger Band — 7.4% CAGR, 0.67 Sharpe re-implemented, invested ~44% of the time — robust across the full parameter grid.
- **Out-of-sample (Sept 2025 → Jul 2026):** −1.5% cumulative vs the market's +21.6%. Directional only (~100 active days; no significance claimed). The edge did not persist — though this window cannot distinguish genuine decay from an unfavourable bull-market regime for a mean-reversion rule; the report's leading limitation.
- **Look-ahead bias eliminated:** the original volatility-regime labels used full-sample information; walk-forward Markov re-estimation (expanding window, one-sided filtered probabilities) attenuates the high-vol premium from 15.8% to 13.1% — the honest number, which survives.
- **Stock-level generalisation (8 FTSE 100 names, one per sector):** an honest null — nothing HAC-significant at α=0.05; nothing survives Bonferroni (α/8).
- **Portfolio construction demo:** inverse-volatility-weighted 8-sleeve portfolio with Sharpe, drawdown and correlation-stability analysis. In-sample Sharpe 0.54 vs 0.30 equal-weight — mechanical, not alpha (HAC p = 0.89), and labelled as such; pairwise correlations unstable across sample halves (0.21 → 0.04).

## Start here — the deliverables

- `reports/final_report.pdf` — the interview-facing write-up. Read this first.
- Per-phase detail: `reports/phase1_data_quality.md`, `phase2_validation.md`, `phase2_review.md`, `phase3_extension.md`, `phase3b_sensitivity.md`, plus the stock-level and portfolio addenda.
- `phase_plans/` — the plan committed **before** each phase was built (the pre-registration track record).

## Setup

Python 3.13, mainstream libraries only.

```
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Reproduce each phase

Price snapshots are **not** committed to this public repo (vendor licensing); rebuild them first with `python data_pipeline.py --refresh`, then run the phases. Because pulls are fresh, expect small deltas vs the report's figures from vendor data revisions — the same effect the report documents in its own reproduction section. `data/boe_bank_rate.csv` (open data) is committed.

| Phase | Command | Produces |
|---|---|---|
| 1 — data pipeline | `python data_pipeline.py` | audits the price snapshots |
| 2 — validate | `python run_phase2.py` | `reports/phase2_validation.md` |
| 3 — extend + regimes | `python run_phase3.py` | `reports/phase3_extension.md` |
| 3b — regime sensitivity | `python run_phase3b.py` | `reports/phase3b_sensitivity.md` |
| 4 — live signal (simulated) | `python live_signal.py` | prints signal; appends log |
| 5 — report | `python make_figures.py` then `python make_pdf.py` | chart + `reports/final_report.pdf` |
| 6 — stock-level generalisation | `python run_phase6.py` | 8-stock FTSE 100 test (Bonferroni-corrected) |
| 7 — portfolio construction | `python run_phase7.py` | inverse-volatility portfolio + risk analysis |

Phase 4 is the only script that pulls live data; it is a capability demonstration only — given the non-persistence finding, explicitly not a system I would trade.

## Layout

```
config.py                  # dates, tickers, cost params (single source of truth)
data_pipeline.py           # Phase 1: pull / snapshot / audit
strategies/                # the 7 strategy signal functions (re-implemented from the paper)
backtest/                  # execution engine + performance metrics + factor regressions
regimes.py                 # walk-forward Markov regimes (look-ahead-free)
run_phase2.py              # re-implement & validate vs the dissertation
run_phase3.py              # extension, robustness grid, walk-forward regime split
run_phase3b.py             # regime-parameter sensitivity
live_signal.py             # minimal simulated live signal
make_figures.py, make_pdf.py  # report build
ff_factors.py              # Fama-French 5-factor pull + snapshot
dissertation_reference.py  # the paper's reported figures, for validation
data/                      # snapshot manifest + open BoE data (price CSVs local-only)
extension/                 # fresh 2015→today snapshot layer
reports/                   # per-phase reports, final report, figures
phase_plans/               # pre-registered phase plans (track record)
```

## Limitations (deliberately the most developed part of the report)

The extension window cannot separate edge decay from regime; the in-sample selection is subject to multiple-testing bias (seven strategies × two assets × regime cuts; Harvey, Liu & Zhu 2016); the cost model is a lower bound. The next tests that would resolve these are specified in the report: a regime-matched out-of-sample comparison and a deflated Sharpe ratio.

## Tooling

Built with AI-assisted development (Claude Code) to accelerate the engineering; the methodology, strategy re-implementation, pre-registered validation, and every result review are my own.

---

*Raahul Ravichandran — BSc Economics (Bath), MSc Investment & Wealth Management (Imperial, 2026–27).*
