# Dissertation Extension — Lean Build Plan

**Purpose:** a defensible, honestly-reported system I can show (code + report) to a working analyst/PM. Defensible beats impressive. One differentiator among many — keep it clean and finished, not sprawling.

**Standing rules:** Python + mainstream libs (pandas, numpy, statsmodels). No live trading / no broker / no real capital, ever, labelled as simulated. Confirm with me at each phase gate before proceeding. If a result looks too good, hunt for a bug (esp. look-ahead) before reporting it.

---

### Phase 1 — Scaffold & data pipeline
Clean project (`data/`, `strategies/`, `backtest/`, `reports/`), dependency file. Pull FTSE 100 (VUKE.L) + GBP/USD via yfinance.
- **Snapshot raw data to CSV** so every result is reproducible from a fixed file, not a live re-pull.
- Flag data gaps honestly; do not silently interpolate.
- **Done when:** pipeline runs from saved snapshots and prints an honest data-quality summary (rows, gaps, date coverage).

### Phase 2 — Re-implement & validate
Re-implement the 7 strategies **cleanly from the rules described in the dissertation** — *not* by reusing `Diss final v3.txt` (reusing it would only prove the code reproduces itself).
- Run over the original window; compare CAGR / Sharpe / HAC significance to the dissertation.
- **Match tolerance:** CAGR within ±1pp, Sharpe within ±0.1, HAC t-stats within ±0.3 of the dissertation. Report anything outside as a discrepancy; do **not** tune code to hit the numbers — a genuine mismatch is a finding (likely a data revision or an original bug), and chasing it down is the point.
- **Done when:** independent numbers sit within tolerance of the dissertation, or the gap is explained.

### Phase 3 — Extend + stress-test
Re-run validated strategies from Aug 2025 → today. Same metrics as the dissertation. Headline question: has the Contrarian Bollinger edge **persisted, decayed further, or reversed?**
- **Frame the ~11-month window as directional only — not statistically significant.** State this up front; never quote a Sharpe off it as if it were.
- **Add a parameter-robustness check** (a few reasonable alternatives for the key choices markers flagged: lookbacks, the 1% Bank-Rate split, 20-day vol window). Answers "did you just pick parameters that worked?"
- Fix the Markov look-ahead from the paper: **rolling/walk-forward regime estimation**, not full-sample labels. (Converts a stated limitation into a demonstrated fix.)
- **Done when:** persistence verdict + robustness table + walk-forward regimes are in hand, honestly caveated.

### Phase 4 — Live signal (minimal)
Generate **today's signal** for the best strategy + a simple local logging harness. **Not** a performance track record — too short to mean anything. No waiting weeks to populate.
- **Done when:** one command prints the current signal and appends to a log. Stop there.

### Phase 5 — Report (the deliverable)
Concise write-up: original vs extension results, with charts. Plain-English **why** performance changed (regime shift, crowding, structural change).
- The **honest limitations section is a headline feature, not a footnote** — "what decayed, why, what I'd test next."
- **Done when:** a report I could excerpt in an equity-research pitch or walk an interviewer through, every number defensible.

---

**Stop line:** if any phase starts sprawling beyond its "Done when," stop and check in rather than expanding scope. A focused finished system beats an ambitious half-built one.
