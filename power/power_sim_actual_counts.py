"""Power for PAP v2 using ACTUAL counts of rate-stance prefilter passages (NCB heads, BIS) per
NCB x half-year and the OBSERVED net-loss cohorts. No stance positions are used.

Assumptions (flagged): passage position noise sd = 0.7 on the -1..+1 scale; governor-half-year
shock sd = 0.2; share of prefilter passages that are truly stance passages f in {0.6, 1.0}.
Units: NCBs with documented treatment status (13). Estimator: imputation DiD with unit and time
FE, weights = passages; transition half-year excluded; RI over cohort labels (99 draws for power).
"""
import json, re, sys
import numpy as np, pandas as pd
sys.path.insert(0, ".")
from code.estimate.imputation import ri_pvalue
from code.corpus import go_nogo

rng = np.random.default_rng(20260911)
P = pd.read_pickle("data/derived/bis_ea_passages_prefilter.pkl")
meta = pd.read_pickle("data/derived/bis_ea_meta.pkl")
y4 = re.compile(r"\b(?:policy rates?|key interest rates?|deposit facility rate|interest rate (?:hikes?|increases?|cuts?|decisions?)|rate (?:hikes?|cuts?)|raise (?:interest )?rates|cut (?:interest )?rates|monetary (?:policy )?tightening|tighten\w*|monetary policy stance|restrictive (?:territory|monetary)|accommodative|easing cycle)\b", re.I)
H = P[(P.role == "ncb_head") & P.text.str.contains(y4)].copy()
H["hy"] = go_nogo.half_year_label(H.date)
COH = {"NL": 15, "BE": 15, "SK": 15, "AT": 17, "DE": 19, "FR": 19,
       "ES": np.inf, "FI": np.inf, "GR": np.inf, "IE": np.inf, "IT": np.inf, "PT": np.inf, "LU": np.inf}
labels = [f"{y}H{h}" for y in range(2016, 2027) for h in (1, 2)][:21]
tidx = {l: i for i, l in enumerate(labels)}
counts = (H[H.ncb.isin(COH) & H.hy.isin(labels)].groupby(["ncb", "hy"]).size()
            .reindex(pd.MultiIndex.from_product([list(COH), labels]), fill_value=0))
print("passages by NCB (2016H1-2026H1):", counts.groupby(level=0).sum().to_dict())
alpha = {u: rng.normal(0, 0.3) for u in COH}

def one(beta, f):
    gamma = dict(zip(labels, np.cumsum(rng.normal(0, 0.08, len(labels)))))
    rows = []
    for (u, hy), n in counts.items():
        n_eff = rng.binomial(n, f)
        if n_eff == 0:
            continue
        D = int(tidx[hy] >= COH[u])
        mean = alpha[u] + gamma[hy] + beta * D + rng.normal(0, 0.2)
        y = mean + rng.normal(0, 0.7 / np.sqrt(n_eff))
        rows.append(dict(unit=u, t=hy, y=y, w=n_eff))
    df = pd.DataFrame(rows)
    base, p, _ = ri_pvalue(df, COH, tidx, n_perm=99, rng=rng)
    return base, p

out = []
for f, reps in ((0.6, 150), (1.0, 100)):
    for beta in (0.0, -0.1, -0.2, -0.3, -0.4):
        r = np.array([one(beta, f) for _ in range(reps)])
        rec = dict(f=f, beta=beta, reps=reps, power=float((r[:, 1] <= 0.05).mean()),
                   mean_est=float(np.nanmean(r[:, 0])), sd_est=float(np.nanstd(r[:, 0])))
        out.append(rec); print(rec, flush=True)
pd.DataFrame(out).to_csv("power/power_actual_counts.csv", index=False)
