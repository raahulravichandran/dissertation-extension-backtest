"""Walk-forward Markov regime labelling, free of look-ahead on both channels.

The dissertation labelled high/low-volatility regimes using full-sample
estimation — a look-ahead a real-time trader could not have used. This module
removes it on both channels (see phase_plans/phase_3.md):

  1. Parameter channel: at each annual refit date r, the 2-state switching-
     variance model is estimated by MLE on the expanding window up to r only.
  2. Inference channel: those fixed parameters are applied forward and the
     FILTERED (one-sided) probabilities are taken - P(regime | data up to and
     including t) - never smoothed (which conditions on the whole sample).

Each day d in the forward interval (r, next_refit] is labelled using a filtered
probability from data <= d with parameters fit on data <= r < d: strictly
past-only on both channels. The first ~min_obs days have no prior window and are
left unlabelled (NaN) rather than back-filled, which would reintroduce look-ahead.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

warnings.filterwarnings("ignore")


def _highvol_regime(params: pd.Series) -> int:
    """Index of the higher-variance regime from a fitted params vector."""
    sigmas = {}
    for k in params.index:
        if "sigma2" in str(k):
            i = int(str(k).split("[")[1].split("]")[0])
            sigmas[i] = params[k]
    return max(sigmas, key=sigmas.get)


def walkforward_highvol_labels(returns: pd.Series, min_obs: int = 500,
                               refit_freq: str = "YS") -> pd.Series:
    """Return a {0 low-vol, 1 high-vol, NaN unlabelled} series, past-only on both channels."""
    r = pd.to_numeric(returns, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    labels = pd.Series(np.nan, index=r.index, dtype=float)
    if len(r) < min_obs:
        return labels

    idx = r.index
    first_refit = idx[min_obs - 1]
    # Annual refit cut-off trading days (as-of each annual boundary).
    cutoffs = []
    for d in pd.date_range(first_refit, idx[-1], freq=refit_freq):
        pos = idx.searchsorted(d, side="right") - 1
        if pos >= 0:
            cutoffs.append(idx[pos])
    cutoffs = sorted(set(cutoffs))
    if not cutoffs:
        cutoffs = [first_refit]

    for i, cut in enumerate(cutoffs):
        train = r.loc[:cut]
        if len(train) < min_obs:
            continue
        try:
            res = MarkovRegression(train, k_regimes=2, trend="c",
                                   switching_variance=True).fit(disp=False)
        except Exception:  # noqa: BLE001
            continue
        highvol = _highvol_regime(res.params)

        # Forward interval (cut, fwd_end]; fixed params applied forward, filtered probs.
        fwd_end = cutoffs[i + 1] if i + 1 < len(cutoffs) else idx[-1]
        ext = r.loc[:fwd_end]
        try:
            res_ext = MarkovRegression(ext, k_regimes=2, trend="c",
                                       switching_variance=True).filter(res.params)
            filt = res_ext.filtered_marginal_probabilities[highvol]
        except Exception:  # noqa: BLE001
            continue

        mask = (filt.index > cut) & (filt.index <= fwd_end)
        labels.loc[filt.index[mask]] = (filt[mask] > 0.5).astype(float)

    return labels
