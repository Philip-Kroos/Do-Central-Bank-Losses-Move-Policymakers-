"""Binary N design if the sample is extended to 2027H2 (3 more half-years). Future counts ASSUMED
equal to each NCB's average per half-year over 2024H1-2026H1. usage: beta reps"""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, ".")
from code.estimate.fast_impute import Panel
beta, reps = float(sys.argv[1]), int(sys.argv[2])
rng = np.random.default_rng(abs(hash(("ext", beta, reps))) % 2**32)
counts = pd.read_pickle("data/derived/y4_counts_heads.pkl")
COH = {"NL": 15, "BE": 15, "SK": 15, "AT": 17, "DE": 19, "FR": 19,
       "ES": np.inf, "FI": np.inf, "GR": np.inf, "IE": np.inf, "IT": np.inf, "PT": np.inf, "LU": np.inf}
units = list(COH)
obs = [f"{y}H{h}" for y in range(2016, 2027) for h in (1, 2)][:21]
C = counts.reindex(pd.MultiIndex.from_product([units, obs]), fill_value=0).to_numpy().reshape(len(units), 21)
fut = np.repeat(np.round(C[:, 16:21].mean(1))[:, None], 3, axis=1)     # 2026H2, 2027H1, 2027H2
C = np.hstack([C, fut]).astype(int)
coh = np.array([COH[u] for u in units]); T = C.shape[1]; ps = []
for _ in range(reps):
    alpha = rng.normal(0, 0.3, len(units)); gamma = np.cumsum(rng.normal(0, 0.08, T))
    N = rng.binomial(C, 0.6); ui, ti = np.nonzero(N); w = N[ui, ti].astype(float)
    y = alpha[ui] + gamma[ti] + beta * (ti >= coh[ui]) + rng.normal(0, 0.2, len(ui)) + rng.normal(0, 0.7, len(ui)) / np.sqrt(w)
    ps.append(Panel(ui, ti, y, w, len(units), T).ri(coh, 99, rng, studentize=False)[1])
out = dict(mode="binary_extended_2027H2", beta=beta, reps=reps, power=float(np.mean(np.array(ps) <= 0.05)))
open("power/power_sensitivity.jsonl", "a").write(json.dumps(out) + "\n"); print(out)
