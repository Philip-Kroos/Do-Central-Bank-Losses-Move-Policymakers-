"""Imputation DiD estimator (Borusyak, Jaravel & Spiess) for a governor x half-year panel.

Fit y = a_unit + g_time + X'd on untreated observations (weighted), impute Y(0) for treated
observations, ATT = weighted mean of (y - yhat). Randomisation inference permutes cohort labels
across units. Designed for small panels (tens of units); dense least squares.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def _design(units, times, X, unit_levels, time_levels):
    n = len(units)
    ui = pd.Categorical(units, categories=unit_levels).codes
    ti = pd.Categorical(times, categories=time_levels).codes
    D = np.zeros((n, len(unit_levels) + len(time_levels) - 1))
    D[np.arange(n), ui] = 1.0
    mask = ti > 0
    D[np.arange(n)[mask], len(unit_levels) + ti[mask] - 1] = 1.0
    return np.hstack([D, X]) if X is not None and X.shape[1] else D


def att(df: pd.DataFrame, y="y", unit="unit", time="t", treat="D", w="w", controls=(), return_event=False):
    d = df.dropna(subset=[y]).copy()
    X = d[list(controls)].to_numpy(float) if controls else None
    unit_levels = sorted(d[unit].unique()); time_levels = sorted(d[time].unique())
    Z = _design(d[unit].to_numpy(), d[time].to_numpy(), X, unit_levels, time_levels)
    ctrl = d[treat].to_numpy() == 0
    tr = ~ctrl
    if tr.sum() == 0:
        return np.nan
    # imputation requires each treated unit and time to appear among controls
    units_ctrl = set(d.loc[ctrl, unit]); times_ctrl = set(d.loc[ctrl, time])
    ok = tr & d[unit].isin(units_ctrl).to_numpy() & d[time].isin(times_ctrl).to_numpy()
    sw = np.sqrt(d[w].to_numpy(float))
    coef, *_ = np.linalg.lstsq(Z[ctrl] * sw[ctrl, None], d[y].to_numpy(float)[ctrl] * sw[ctrl], rcond=None)
    resid = d[y].to_numpy(float) - Z @ coef
    ww = d[w].to_numpy(float)
    est = float((resid[ok] * ww[ok]).sum() / ww[ok].sum()) if ok.any() else np.nan
    if not return_event:
        return est
    d["tau"] = resid
    return est, d


def ri_pvalue(df: pd.DataFrame, cohort_of_unit: dict, time_index: dict, n_perm=999, rng=None, **kw):
    """Permute cohort labels (including never = inf) across units; recompute D and ATT."""
    rng = rng or np.random.default_rng(0)
    units = list(cohort_of_unit)
    labels = np.array([cohort_of_unit[u] for u in units], dtype=float)

    def build(lbl):
        m = dict(zip(units, lbl))
        tnum = df["t"].map(time_index).to_numpy()
        coh = df["unit"].map(m).to_numpy(float)
        D = (tnum >= coh).astype(int)
        trans = (tnum == coh - 1)             # transition half-year (publication inside) excluded
        return D, trans

    D0, tr0 = build(labels)
    base = att(df.assign(D=D0)[~tr0], **kw)
    null = []
    for _ in range(n_perm):
        D, tr = build(rng.permutation(labels))
        null.append(att(df.assign(D=D)[~tr], **kw))
    null = np.array(null)
    null = null[np.isfinite(null)]
    p = (1 + (np.abs(null) >= abs(base)).sum()) / (1 + len(null))
    return base, p, null
