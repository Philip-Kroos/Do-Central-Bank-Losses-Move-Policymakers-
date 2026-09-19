"""Build the governor x half-year analysis panel (PAP v2/v2.1) from classification results.

Joins happen only here, after classification is frozen. Units: NCB heads (+ ECB board as placebo group).
"""
from __future__ import annotations
import unicodedata
import numpy as np, pandas as pd

LABELS = [f"{y}H{h}" for y in range(2016, 2027) for h in (1, 2)][:21]          # 2016H1..2026H1
CORE = {"AT", "BE", "DE", "FI", "FR", "LU", "NL"}


def hy(dates: pd.Series) -> pd.Series:
    d = pd.to_datetime(dates)
    return d.dt.year.astype(str) + "H" + ((d.dt.month > 6) + 1).astype(str)


def gov_id(author: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFKD", str(author)) if not unicodedata.combining(c))
    return " ".join(s.lower().replace(".", " ").split())


def outcome_panel(results: pd.DataFrame, key: pd.DataFrame, exclude_retrospective: bool = False) -> pd.DataFrame:
    r = results[(results.valid == True) & (results.topic == True)]
    if exclude_retrospective and "retrospective" in r.columns:                      # robustness R11
        r = r[r.retrospective.astype(str).str.lower() != "true"]
    r = r.merge(key, on="id", how="inner")
    r["hy"] = hy(r.date); r["gov"] = r.author.map(gov_id)
    r = r[r.hy.isin(LABELS)]
    g = r.groupby(["role_group", "ncb", "gov", "hy"])
    out = g.agg(y=("position", "mean"), n=("position", "size"),
                share_hawk=("position", lambda x: (x == 1).mean()), share_dove=("position", lambda x: (x == -1).mean())).reset_index()
    out["y_share"] = out.share_hawk - out.share_dove          # identical to y by construction (kept for transparency)
    nd = out.share_hawk + out.share_dove
    out["y_directional"] = np.where(nd > 0, (out.share_hawk - out.share_dove) / nd.where(nd > 0, 1), np.nan)   # R5 (PAP deviation 2026-09-11)
    return out


def treatment_cohorts(treat: pd.DataFrame) -> dict:
    """First half-year of treatment (index into LABELS) for net (N) and covered-gross-only (G)."""
    idx = {l: i for i, l in enumerate(LABELS)}
    N, G = {}, {}
    for r in treat.itertuples():
        N[r.ncb] = idx.get(r.net_on, np.inf) if isinstance(r.net_on, str) else np.inf
        G[r.ncb] = idx.get(r.gross_on, np.inf) if isinstance(r.gross_on, str) else np.inf
    return dict(N=N, G=G)


def exposure_panel(exp_hy: pd.DataFrame) -> pd.DataFrame:
    e = exp_hy[exp_hy.hy.isin(LABELS)][["ncb", "hy", "carry_per_keypp_demeaned"]].copy()
    sd = e.carry_per_keypp_demeaned.std()
    e["E"] = (e.carry_per_keypp_demeaned - e.carry_per_keypp_demeaned.mean()) / sd
    return e[["ncb", "hy", "E"]]


def spread_panel(yields: pd.DataFrame) -> pd.DataFrame:
    y = yields.copy(); y["hy"] = hy(y.month)
    de = y[y.country == "DE"].groupby("hy").yield_pct.mean()
    s = y.groupby(["country", "hy"]).yield_pct.mean().reset_index()
    s["spread_de"] = s.yield_pct - s.hy.map(de)
    return s.rename(columns={"country": "ncb"})[["ncb", "hy", "spread_de"]]


def pre_period_x_rate(level_panel: pd.DataFrame, value: str, rates: pd.DataFrame,
                      pre=("2019H1", "2019H2", "2020H1", "2020H2", "2021H1", "2021H2")) -> pd.DataFrame:
    """PAP v2.2 control: NCB mean of `value` over 2019-2021 times the half-year deposit facility rate."""
    lvl = level_panel[level_panel.hy.isin(pre)].groupby("ncb")[value].mean().rename("pre")
    r = rates.copy(); r["hy"] = hy(r.month); dfr = r.groupby("hy").dfr_pct.mean()
    out = pd.MultiIndex.from_product([lvl.index, LABELS], names=["ncb", "hy"]).to_frame(index=False)
    out[f"pre_{value}_x_dfr"] = out.ncb.map(lvl) * out.hy.map(dfr)
    return out


def residual_variance_share(df: pd.DataFrame, controls=(), extra_fe=None) -> float:
    """Share of passage-weighted exposure variance left after governor + half-year FE (+ controls). Outcome-blind."""
    d = df.dropna(subset=["E"] + list(controls)).reset_index(drop=True)
    govs = sorted(d.gov.unique())
    gi = d.gov.map({g: i for i, g in enumerate(govs)}).to_numpy(); ti = d.hy.map({l: i for i, l in enumerate(LABELS)}).to_numpy()
    Z = fe_design(gi, ti, len(govs), len(LABELS), d[list(controls)].to_numpy(float) if controls else None)
    if extra_fe == "core_x_hy":
        c = d.ncb.isin(CORE).to_numpy(); CZ = np.zeros((len(d), len(LABELS))); CZ[np.arange(len(d))[c], ti[c]] = 1; Z = np.hstack([Z, CZ[:, 1:]])
    w = np.sqrt(d.n.to_numpy(float)); x = d.E.to_numpy()
    coef, *_ = np.linalg.lstsq(Z * w[:, None], x * w, rcond=None)
    r = x * w - (Z * w[:, None]) @ coef
    xc = (x - np.average(x, weights=w ** 2)) * w
    return float((r ** 2).sum() / (xc ** 2).sum())


def fe_design(g_idx, t_idx, n_g, n_t, X=None):
    n = len(g_idx); Z = np.zeros((n, n_g + n_t - 1))
    Z[np.arange(n), g_idx] = 1; m = t_idx > 0; Z[np.arange(n)[m], n_g + t_idx[m] - 1] = 1
    return Z if X is None else np.hstack([Z, X])


def dose_estimate(df: pd.DataFrame, controls=(), extra_fe=None, n_perm=999, rng=None):
    """H3: y = a_gov + g_hy (+ core x hy) + beta*E + X'd, weights n; studentised RI permuting NCB exposure paths."""
    rng = rng or np.random.default_rng(0)
    d = df.dropna(subset=["y", "E"] + list(controls)).reset_index(drop=True)
    govs = sorted(d.gov.unique()); ncbs = sorted(d.ncb.unique())
    gi = d.gov.map({g: i for i, g in enumerate(govs)}).to_numpy(); ti = d.hy.map({l: i for i, l in enumerate(LABELS)}).to_numpy()
    X = d[list(controls)].to_numpy(float) if controls else None
    Z = fe_design(gi, ti, len(govs), len(LABELS), X)
    if extra_fe == "core_x_hy":
        core = d.ncb.isin(CORE).to_numpy()
        CZ = np.zeros((len(d), len(LABELS))); CZ[np.arange(len(d))[core], ti[core]] = 1
        Z = np.hstack([Z, CZ[:, 1:]])
    w = d.n.to_numpy(float); sw = np.sqrt(w)
    path = d.pivot_table(index="ncb", columns="hy", values="E", aggfunc="first").reindex(columns=LABELS)
    ni = d.ncb.map({c: i for i, c in enumerate(ncbs)}).to_numpy()
    def stat(perm):
        pmap = dict(zip(ncbs, [ncbs[k] for k in perm]))
        x = np.array([path.at[pmap[c], h] if pmap[c] in path.index else np.nan for c, h in zip(d.ncb, d.hy)])
        ok = np.isfinite(x)
        Zw = Z[ok] * sw[ok, None]
        B = np.column_stack([d.y.to_numpy()[ok] * sw[ok], x[ok] * sw[ok]])
        coef, *_ = np.linalg.lstsq(Zw, B, rcond=None); R = B - Zw @ coef
        b = (R[:, 1] * R[:, 0]).sum() / (R[:, 1] ** 2).sum()
        # PAP v2.3: CR3 jackknife SE (leave one NCB out); CR0 was oversized with controls in simulation
        ests = []
        for g in np.unique(ni[ok]):
            keep = ni[ok] != g
            ck, *_ = np.linalg.lstsq(Zw[keep], B[keep], rcond=None); Rk = B[keep] - Zw[keep] @ ck
            ests.append((Rk[:, 1] * Rk[:, 0]).sum() / (Rk[:, 1] ** 2).sum())
        ests = np.array(ests); G_ = len(ests)
        se = np.sqrt((G_ - 1) / G_ * ((ests - ests.mean()) ** 2).sum())
        return b, b / se, se
    b0, t0, se0 = stat(np.arange(len(ncbs)))
    null = np.array([stat(rng.permutation(len(ncbs)))[1] for _ in range(n_perm)])
    p = (1 + (np.abs(null) >= abs(t0)).sum()) / (1 + len(null))
    return dict(beta=float(b0), se_jackknife=float(se0), t=float(t0), p_ri=float(p), n_cells=int(len(d)), n_gov=len(govs), n_ncb=len(ncbs),
                n_passages=int(w.sum()))


def event_estimate(df: pd.DataFrame, cohorts: dict, n_perm=999, rng=None):
    """H1: imputation DiD with governor FE; cohorts assigned at NCB level; transition half-year dropped; RI over NCB cohorts."""
    from code.estimate.fast_impute import Panel
    rng = rng or np.random.default_rng(0)
    d = df[df.ncb.isin(cohorts)].dropna(subset=["y"]).reset_index(drop=True)
    govs = sorted(d.gov.unique()); ncbs = sorted(d.ncb.unique())
    gi = d.gov.map({g: i for i, g in enumerate(govs)}).to_numpy(); ti = d.hy.map({l: i for i, l in enumerate(LABELS)}).to_numpy()
    gov_ncb = d.groupby("gov").ncb.first().reindex(govs).to_numpy()
    p = Panel(gi, ti, d.y.to_numpy(), d.n.to_numpy(float), len(govs), len(LABELS))
    base_coh = np.array([cohorts[c] for c in ncbs], float)
    def by_gov(coh_ncb):
        m = dict(zip(ncbs, coh_ncb)); return np.array([m[c] for c in gov_ncb], float)
    att = p.att(by_gov(base_coh))
    null = np.array([p.att(by_gov(rng.permutation(base_coh))) for _ in range(n_perm)])
    null = null[np.isfinite(null)]
    pv = (1 + (np.abs(null) >= abs(att)).sum()) / (1 + len(null))
    return dict(att=float(att), p_ri=float(pv), n_cells=int(len(d)), n_gov=len(govs), n_ncb=len(ncbs))
