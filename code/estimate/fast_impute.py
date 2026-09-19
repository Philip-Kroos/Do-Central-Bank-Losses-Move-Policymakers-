"""Array-based imputation DiD for simulation and randomisation inference (same estimator as
imputation.att). Adds a leave-one-unit-out jackknife SE and a studentised RI statistic, because
plain RI on the ATT can be oversized when units differ strongly in precision (e.g. DE vs SK)."""
from __future__ import annotations
import numpy as np


class Panel:
    def __init__(self, unit_idx, time_idx, y, w, n_units, n_times):
        self.u = np.asarray(unit_idx); self.t = np.asarray(time_idx)
        self.y = np.asarray(y, float); self.w = np.asarray(w, float)
        self.nu, self.nt = n_units, n_times
        n = len(self.y)
        Z = np.zeros((n, n_units + n_times - 1))
        Z[np.arange(n), self.u] = 1
        m = self.t > 0
        Z[np.arange(n)[m], n_units + self.t[m] - 1] = 1
        self.Z = Z
        self.sw = np.sqrt(self.w)

    def att(self, cohort_by_unit, keep=None):
        coh = np.asarray(cohort_by_unit, float)[self.u]
        D = self.t >= coh
        keep_mask = self.t != (coh - 1)                      # drop transition half-year
        if keep is not None:
            keep_mask &= keep
        ctrl = keep_mask & ~D
        tr = keep_mask & D
        if tr.sum() == 0 or ctrl.sum() == 0:
            return np.nan
        # treated obs need their unit and time among controls
        uc = np.zeros(self.nu, bool); uc[self.u[ctrl]] = True
        tc = np.zeros(self.nt, bool); tc[self.t[ctrl]] = True
        ok = tr & uc[self.u] & tc[self.t]
        if not ok.any():
            return np.nan
        coef, *_ = np.linalg.lstsq(self.Z[ctrl] * self.sw[ctrl, None], self.y[ctrl] * self.sw[ctrl], rcond=None)
        r = self.y[ok] - self.Z[ok] @ coef
        return float((r * self.w[ok]).sum() / self.w[ok].sum())

    def jackknife_se(self, cohort_by_unit):
        units = np.unique(self.u)
        ests = []
        for g in units:
            e = self.att(cohort_by_unit, keep=self.u != g)
            if np.isfinite(e):
                ests.append(e)
        ests = np.array(ests)
        k = len(ests)
        return float(np.sqrt((k - 1) / k * ((ests - ests.mean()) ** 2).sum())) if k > 2 else np.nan

    def ri(self, cohort_by_unit, n_perm, rng, studentize=True):
        coh = np.asarray(cohort_by_unit, float)
        def stat(c):
            a = self.att(c)
            if not studentize:
                return a
            s = self.jackknife_se(c)
            return a / s if s and np.isfinite(s) and s > 0 else np.nan
        base = stat(coh)
        null = np.array([stat(rng.permutation(coh)) for _ in range(n_perm)])
        null = null[np.isfinite(null)]
        p = (1 + (np.abs(null) >= abs(base)).sum()) / (1 + len(null))
        return base, p
