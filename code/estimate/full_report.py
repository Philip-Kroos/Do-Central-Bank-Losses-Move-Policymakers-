"""All pre-specified estimates (PAP v2-v2.3) with ONE joint randomisation scheme.

Every NCB-level treatment (exposure path, loss cohort, attributes) is permuted jointly by the same permutation of NCB
labels. This yields a joint null distribution of studentised statistics across tests, used for (i) per-test RI p-values
and (ii) Romano-Wolf step-down adjustment across the secondary family (PAP v2 §5).
Studentisation: leave-one-NCB-out jackknife SE (PAP v2.3).
"""
from __future__ import annotations
import numpy as np, pandas as pd
from code.estimate import panel as pn
from code.estimate.fast_impute import Panel

LAB = pn.LABELS
TIDX = {l: i for i, l in enumerate(LAB)}


# ----------------------------------------------------------------------------- linear (dose-type) specifications
class Linear:
    """y = FE(unit) + FE(half-year) [+ core x half-year] + controls + b*x ; weights n; jackknife-by-NCB t for x (first col)."""

    def __init__(self, d: pd.DataFrame, controls=(), fe_unit="gov", core_x_hy=False, y="y"):
        self.d = d.dropna(subset=[y] + list(controls)).reset_index(drop=True)
        d = self.d
        units = sorted(d[fe_unit].unique())
        ui = d[fe_unit].map({u: i for i, u in enumerate(units)}).to_numpy(); ti = d.hy.map(TIDX).to_numpy()
        Z = pn.fe_design(ui, ti, len(units), len(LAB), d[list(controls)].to_numpy(float) if controls else None)
        if core_x_hy:
            c = d.ncb.isin(pn.CORE).to_numpy(); CZ = np.zeros((len(d), len(LAB))); CZ[np.arange(len(d))[c], ti[c]] = 1
            Z = np.hstack([Z, CZ[:, 1:]])
        self.sw = np.sqrt(d.n.to_numpy(float)); self.Zw = Z * self.sw[:, None]
        self.yw = d[y].to_numpy(float) * self.sw
        self.ncb = d.ncb.to_numpy(); self.hy = d.hy.to_numpy()

    def stat(self, X):
        """X: (n, k) regressors; returns (b[0], t[0], b vector, jackknife cov diag)."""
        ok = np.all(np.isfinite(X), axis=1)
        Zw, yw, Xw = self.Zw[ok], self.yw[ok], X[ok] * self.sw[ok, None]
        def fit(mask):
            A = np.hstack([Xw[mask], Zw[mask]])
            coef, *_ = np.linalg.lstsq(A, yw[mask], rcond=None)
            return coef[:X.shape[1]]
        b = fit(np.ones(ok.sum(), bool))
        g_ids = np.unique(self.ncb[ok]); jk = np.array([fit(self.ncb[ok] != g) for g in g_ids]); G = len(jk)
        V = (G - 1) / G * ((jk - jk.mean(0)).T @ (jk - jk.mean(0)))
        se = np.sqrt(np.diag(V))
        return b, b / se, V


def exposure_regressor(d, path, perm_map):
    return np.array([path.at[perm_map[c], h] if (perm_map[c] in path.index and h in path.columns) else np.nan
                     for c, h in zip(d.ncb, d.hy)])


# ----------------------------------------------------------------------------- event (imputation) specifications
def event_stat(d: pd.DataFrame, cohort_by_ncb: dict, keep_ncbs):
    dd = d[d.ncb.isin(keep_ncbs)].reset_index(drop=True)
    govs = sorted(dd.gov.unique())
    gi = dd.gov.map({g: i for i, g in enumerate(govs)}).to_numpy(); ti = dd.hy.map(TIDX).to_numpy()
    P = Panel(gi, ti, dd.y.to_numpy(), dd.n.to_numpy(float), len(govs), len(LAB))
    gov_ncb = dd.groupby("gov").ncb.first().reindex(govs).to_numpy()
    coh = np.array([cohort_by_ncb.get(c, np.inf) for c in gov_ncb], float)
    att = P.att(coh)
    ests = [P.att(coh, keep=(dd.ncb.to_numpy() != g)) for g in np.unique(dd.ncb)]
    ests = np.array([e for e in ests if np.isfinite(e)]); G = len(ests)
    se = np.sqrt((G - 1) / G * ((ests - ests.mean()) ** 2).sum()) if G > 2 else np.nan
    return att, att / se if se and np.isfinite(se) and se > 0 else np.nan


def callaway_santanna(d: pd.DataFrame, cohort_by_ncb: dict, keep_ncbs):
    """R8: CS ATT with not-yet-treated controls on the NCB x half-year mean panel, base period g-2 (skips transition g-1)."""
    m = d[d.ncb.isin(keep_ncbs)].groupby(["ncb", "hy"]).apply(lambda x: np.average(x.y, weights=x.n), include_groups=False).unstack().reindex(columns=LAB)
    Y = m.to_numpy(); ncbs = list(m.index); coh = np.array([cohort_by_ncb.get(c, np.inf) for c in ncbs])
    atts, wts = [], []
    for g in sorted(set(coh[np.isfinite(coh)])):
        g = int(g); base = g - 2
        if base < 0: continue
        tr = coh == g
        for t in range(g, len(LAB)):
            ctrl = (coh > t) & np.isfinite(Y[:, base]) & np.isfinite(Y[:, t])
            trv = tr & np.isfinite(Y[:, base]) & np.isfinite(Y[:, t])
            if trv.sum() == 0 or ctrl.sum() == 0: continue
            atts.append((Y[trv, t] - Y[trv, base]).mean() - (Y[ctrl, t] - Y[ctrl, base]).mean()); wts.append(trv.sum())
    return float(np.average(atts, weights=wts)) if atts else np.nan


# ----------------------------------------------------------------------------- Romano-Wolf step-down
def romano_wolf(t_obs: np.ndarray, t_null: np.ndarray) -> np.ndarray:
    a_obs = np.abs(t_obs); a_null = np.abs(t_null)
    order = np.argsort(-a_obs); p = np.empty(len(t_obs)); prev = 0.0
    for j, k in enumerate(order):
        rem = order[j:]
        mx = np.nanmax(a_null[:, rem], axis=1)
        pj = (1 + np.sum(mx >= a_obs[k])) / (1 + len(mx))
        prev = max(prev, pj); p[k] = prev
    return p


# ----------------------------------------------------------------------------- main driver
def run_all(heads: pd.DataFrame, exp_paths: dict, cohorts: dict, documented: set, attrs: pd.DataFrame,
            main_controls: tuple, n_perm=999, rng=None, retro_heads: pd.DataFrame | None = None,
            successors_after_2022: set = frozenset()):
    rng = rng or np.random.default_rng(20260911)
    ncbs = sorted(heads.ncb.unique())
    base_path = exp_paths["net_flow_pepp0.889_mm1"]
    lead = base_path.shift(-2, axis=1)                            # exposure two half-years ahead (F1)

    specs = {}                                                    # name -> callable(perm_map) -> (estimate, t)
    L_main = Linear(heads, main_controls)
    specs["H3_main"] = lambda pm: L_main.stat(exposure_regressor(L_main.d, base_path, pm)[:, None])
    L_r1 = Linear(heads, main_controls, fe_unit="ncb")
    specs["R1_ncb_fe"] = lambda pm: L_r1.stat(exposure_regressor(L_r1.d, base_path, pm)[:, None])
    h3 = heads[~heads.gov.isin(successors_after_2022)]
    L_r3 = Linear(h3, main_controls)
    specs["R3_no_late_successors"] = lambda pm: L_r3.stat(exposure_regressor(L_r3.d, base_path, pm)[:, None])
    L_r4 = Linear(heads, ())
    specs["R4_no_controls"] = lambda pm: L_r4.stat(exposure_regressor(L_r4.d, base_path, pm)[:, None])
    L_r5 = Linear(heads.dropna(subset=["y_directional"]), main_controls, y="y_directional")
    specs["R5_share_outcome"] = lambda pm: L_r5.stat(exposure_regressor(L_r5.d, base_path, pm)[:, None])
    L_r9 = Linear(heads, main_controls, core_x_hy=True)
    specs["R9_core_x_hy"] = lambda pm: L_r9.stat(exposure_regressor(L_r9.d, base_path, pm)[:, None])
    if "spread_de" in heads:
        L_r10 = Linear(heads, tuple(c for c in ("spread_de", "debt_ratio_now") if c in heads))
        specs["R10_contemporaneous_controls"] = lambda pm: L_r10.stat(exposure_regressor(L_r10.d, base_path, pm)[:, None])
    if retro_heads is not None:
        L_r11 = Linear(retro_heads, main_controls)
        specs["R11_no_retrospective"] = lambda pm: L_r11.stat(exposure_regressor(L_r11.d, base_path, pm)[:, None])
    def f1(pm):
        X = np.column_stack([exposure_regressor(L_main.d, base_path, pm), exposure_regressor(L_main.d, lead, pm)])
        b, t, V = L_main.stat(X)
        return b[1:], t[1:], V
    specs["F1_lead_exposure"] = f1
    if "pre_debt_ratio_x_dfr" in main_controls:
        ctrl_wo = tuple(c for c in main_controls if c != "pre_debt_ratio_x_dfr")
        L_f6 = Linear(heads, ctrl_wo)
        def f6(pm):                                            # coefficient on the debt term when exposure is included
            X = np.column_stack([L_f6.d.pre_debt_ratio_x_dfr.to_numpy(float), exposure_regressor(L_f6.d, base_path, pm)])
            return L_f6.stat(X)
        specs["F6_debt_term_given_exposure"] = f6
    # event designs (H1, R6 gross, H2 = N minus G not studentised jointly -> reported separately)
    specs["H1_net_loss"] = lambda pm: event_stat(heads, {c: cohorts["N"].get(pm[c], np.inf) for c in ncbs}, documented)
    specs["R6_gross_loss"] = lambda pm: event_stat(heads, {c: cohorts["G"].get(pm[c], np.inf) for c in ncbs}, documented)
    # H4 heterogeneity: exposure x attribute (attribute moves with NCB permutation only for NCB-level attributes)
    if attrs is not None and len(attrs):
        a = heads.merge(attrs, on="gov", how="left")
        for col in [c for c in attrs.columns if c != "gov"]:
            if a[col].notna().sum() < 20: continue
            Lh = Linear(a.dropna(subset=[col]), main_controls)
            def h4(pm, Lh=Lh, col=col):
                x = exposure_regressor(Lh.d, base_path, pm)
                return Lh.stat(np.column_stack([x * Lh.d[col].to_numpy(float), x]))
            specs[f"H4_exposure_x_{col}"] = h4

    # R12 (PAP v2.4): leave-one-NCB-out estimates of H3, because identifying variation is concentrated
    loo = {}
    for c in ncbs:
        sub = heads[heads.ncb != c]
        if sub.ncb.nunique() < 5:
            continue
        Lc = Linear(sub, main_controls)
        b, t, _ = Lc.stat(exposure_regressor(Lc.d, base_path, {x: x for x in ncbs})[:, None])
        loo[c] = dict(beta=float(b[0]), t=float(t[0]), n_cells=int(len(Lc.d)))

    identity = {c: c for c in ncbs}
    obs = {}
    for k, f in specs.items():
        r = f(identity); obs[k] = (np.atleast_1d(r[0])[0], np.atleast_1d(r[1])[0])
    null = {k: [] for k in specs}
    for _ in range(n_perm):
        pm = dict(zip(ncbs, rng.permutation(ncbs)))
        for k, f in specs.items():
            try:
                null[k].append(np.atleast_1d(f(pm)[1])[0])
            except Exception:
                null[k].append(np.nan)
    out = {}
    for k in specs:
        nk = np.array(null[k], float); nk = nk[np.isfinite(nk)]
        p = (1 + np.sum(np.abs(nk) >= abs(obs[k][1]))) / (1 + len(nk)) if np.isfinite(obs[k][1]) else np.nan
        out[k] = dict(estimate=float(obs[k][0]), t=float(obs[k][1]), p_ri=float(p), n_perm_valid=int(len(nk)))
    for k in out:
        if k.startswith("F6"):
            out[k]["note"] = "p_ri permutes exposure only and is not a test of the debt term; interpret t (jackknife)"
    fam = [k for k in out if k.startswith(("H1_", "H4_"))]
    if len(fam) >= 2:
        T = np.column_stack([np.array(null[k], float) for k in fam])
        pr = romano_wolf(np.array([out[k]["t"] for k in fam]), T)
        for k, p in zip(fam, pr): out[k]["p_romano_wolf"] = float(p)
    out["R12_leave_one_ncb_out"] = dict(estimates=loo, note="H3 re-estimated dropping each NCB; no RI (point estimates and jackknife t)")
    out["R8_callaway_santanna_H1"] = dict(estimate=callaway_santanna(heads, cohorts["N"], documented), note="point estimate; inference via RI in run with --perm")
    return out
