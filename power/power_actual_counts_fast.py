"""Chunked power simulation for PAP v2 (actual counts, observed cohorts). Usage: python3 ... f beta reps studentize(0/1)
Appends one JSON line per call to power/power_actual_counts.jsonl. Assumptions as in power_sim_actual_counts.py."""
import json, re, sys, time
import numpy as np, pandas as pd
sys.path.insert(0, ".")
from code.estimate.fast_impute import Panel
from code.corpus import go_nogo

f, beta, reps, stud = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), bool(int(sys.argv[4]))
seed = abs(hash((f, beta, reps, stud))) % 2**32
rng = np.random.default_rng(seed)
cache = "data/derived/y4_counts_heads.pkl"
try:
    counts = pd.read_pickle(cache)
except FileNotFoundError:
    P = pd.read_pickle("data/derived/bis_ea_passages_prefilter.pkl")
    y4 = re.compile(r"\b(?:policy rates?|key interest rates?|deposit facility rate|interest rate (?:hikes?|increases?|cuts?|decisions?)|rate (?:hikes?|cuts?)|raise (?:interest )?rates|cut (?:interest )?rates|monetary (?:policy )?tightening|tighten\w*|monetary policy stance|restrictive (?:territory|monetary)|accommodative|easing cycle)\b", re.I)
    H = P[(P.role == "ncb_head") & P.text.str.contains(y4)].copy()
    H["hy"] = go_nogo.half_year_label(H.date)
    counts = H.groupby(["ncb", "hy"]).size()
    counts.to_pickle(cache)
COH = {"NL": 15, "BE": 15, "SK": 15, "AT": 17, "DE": 19, "FR": 19,
       "ES": np.inf, "FI": np.inf, "GR": np.inf, "IE": np.inf, "IT": np.inf, "PT": np.inf, "LU": np.inf}
units = list(COH); labels = [f"{y}H{h}" for y in range(2016, 2027) for h in (1, 2)][:21]
C = counts.reindex(pd.MultiIndex.from_product([units, labels]), fill_value=0).to_numpy().reshape(len(units), len(labels))
coh = np.array([COH[u] for u in units])
t0 = time.time(); res = []
for _ in range(reps):
    alpha = rng.normal(0, 0.3, len(units)); gamma = np.cumsum(rng.normal(0, 0.08, len(labels)))
    N = rng.binomial(C, f)
    ui, ti = np.nonzero(N)
    D = ti >= coh[ui]
    y = alpha[ui] + gamma[ti] + beta * D + rng.normal(0, 0.2, len(ui)) + rng.normal(0, 0.7, len(ui)) / np.sqrt(N[ui, ti])
    p = Panel(ui, ti, y, N[ui, ti], len(units), len(labels))
    res.append(p.ri(coh, 99, rng, studentize=stud))
r = np.array(res, float)
out = dict(f=f, beta=beta, reps=reps, studentized=stud, power=float(np.mean(r[:, 1] <= 0.05)),
           mean_att_or_t=float(np.nanmean(r[:, 0])), seconds=round(time.time() - t0, 1))
open("power/power_actual_counts.jsonl", "a").write(json.dumps(out) + "\n"); print(out)
