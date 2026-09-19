"""Null-imposed wild cluster bootstrap-t (Rademacher) for the main exposure specification.

Clusters are NCBs. The restricted model (beta = 0) is fitted, residuals are re-signed by cluster,
outcomes are regenerated and beta and its cluster-robust t are re-estimated on each draw.
Reported alongside the permutation p-value as an alternative small-cluster inference.
"""
from __future__ import annotations
import numpy as np, pandas as pd
from code.estimate import panel as pn


def _fit(Zw, yw, k):
    coef, *_ = np.linalg.lstsq(Zw, yw, rcond=None)
    return coef


def wild_cluster_t(df: pd.DataFrame, controls=(), reps=999, seed=7, se="CR3"):
    d = df.dropna(subset=["y", "E"] + list(controls)).reset_index(drop=True)
    govs = sorted(d.gov.unique()); ncbs = sorted(d.ncb.unique())
    gi = d.gov.map({g: i for i, g in enumerate(govs)}).to_numpy()
    ti = d.hy.map({l: i for i, l in enumerate(pn.LABELS)}).to_numpy()
    ni = d.ncb.map({c: i for i, c in enumerate(ncbs)}).to_numpy()
    FE = pn.fe_design(gi, ti, len(govs), len(pn.LABELS),
                      d[list(controls)].to_numpy(float) if controls else None)
    x = d.E.to_numpy(float)[:, None]
    sw = np.sqrt(d.n.to_numpy(float))
    Xw = np.hstack([x, FE]) * sw[:, None]
    Zw = FE * sw[:, None]
    yw = d.y.to_numpy(float) * sw

    def beta_and_t(yvec):
        coef = _fit(Xw, yvec, 1)
        b = coef[0]
        resid = yvec - Xw @ coef
        # leave-one-cluster-out jackknife SE on beta
        ests = []
        for g in range(len(ncbs)):
            m = ni != g
            if m.sum() < Xw.shape[1] + 1:
                continue
            ests.append(_fit(Xw[m], yvec[m], 1)[0])
        ests = np.array(ests); G = len(ests)
        s = np.sqrt((G - 1) / G * ((ests - ests.mean()) ** 2).sum()) if G > 2 else np.nan
        return b, (b / s if s and np.isfinite(s) and s > 0 else np.nan), resid

    b_hat, t_hat, _ = beta_and_t(yw)
    # restricted fit (beta = 0)
    coef0 = _fit(Zw, yw, 0)
    fit0 = Zw @ coef0
    u0 = yw - fit0
    rng = np.random.default_rng(seed)
    t_star = []
    for _ in range(reps):
        signs = rng.choice([-1.0, 1.0], size=len(ncbs))[ni]
        y_b = fit0 + signs * u0
        _, t_b, _ = beta_and_t(y_b)
        t_star.append(t_b)
    t_star = np.array(t_star, float); t_star = t_star[np.isfinite(t_star)]
    p = (1 + np.sum(np.abs(t_star) >= abs(t_hat))) / (1 + len(t_star))
    return dict(beta=float(b_hat), t=float(t_hat), p_wild=float(p), reps=int(len(t_star)),
                clusters=len(ncbs))
